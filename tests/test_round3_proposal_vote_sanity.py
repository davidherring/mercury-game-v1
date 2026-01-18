import json
from typing import Any, Dict, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app
from backend.state import CHAIR, COUNTRIES, VOTE_ORDER
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _load_state(session: AsyncSession, game_id: str) -> Dict[str, Any]:
    row = await session.execute(
        text("SELECT state FROM game_state WHERE game_id = :gid"),
        {"gid": game_id},
    )
    state = row.scalar_one()
    return state if isinstance(state, dict) else cast(Dict[str, Any], json.loads(state))


async def _save_state(session: AsyncSession, game_id: str, state: Dict[str, Any]) -> None:
    await session.execute(
        text("UPDATE game_state SET state = :state, updated_at = now() WHERE game_id = :gid"),
        {"state": json.dumps(state), "gid": game_id},
    )
    await session.commit()


async def _set_acceptance(
    session: AsyncSession,
    game_id: str,
    role_id: str,
    issue_id: str,
    updates: Dict[str, Any],
) -> None:
    state = await _load_state(session, game_id)
    stances = state.setdefault("stances", {})
    stances.setdefault(role_id, {}).setdefault(issue_id, {}).setdefault("acceptance", {})
    acceptance = stances[role_id][issue_id]["acceptance"]
    acceptance.update(updates)
    await _save_state(session, game_id, state)


async def _advance_issue_to_debate_end(client: AsyncClient, game_id: str, issue_id: str) -> None:
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": issue_id, "human_placement": "skip"}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue1 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue1)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue2 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue2)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})


async def _proposal_step(client: AsyncClient, game_id: str) -> Dict[str, Any]:
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    resp.raise_for_status()
    return resp.json()["state"]


async def _vote_steps(client: AsyncClient, game_id: str, count: int) -> Dict[str, Any]:
    state: Dict[str, Any] = {}
    for _ in range(count):
        resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        resp.raise_for_status()
        state = resp.json()["state"]
    return state


async def _fetch_votes_row(session: AsyncSession, game_id: str, issue_id: str) -> Dict[str, Any]:
    row = await session.execute(
        text(
            """
            SELECT votes_by_country, passed, proposal_option_id
            FROM votes
            WHERE game_id = :gid AND issue_id = :iid
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """
        ),
        {"gid": game_id, "iid": issue_id},
    )
    res = row.mappings().first()
    if res is None:
        return {}
    votes_by_country = res["votes_by_country"]
    if isinstance(votes_by_country, str):
        votes_by_country = json.loads(votes_by_country)
    return {
        "votes_by_country": votes_by_country,
        "passed": res["passed"],
        "proposal_option_id": res["proposal_option_id"],
    }


@pytest.mark.asyncio
async def test_proposal_tie_break_determinism():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    issue_id = "3"

    async def _run_once(seed: int) -> str:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=seed)
            await _advance_issue_to_debate_end(client, game_id, issue_id)

            agen = get_session()
            session = await agen.__anext__()
            try:
                for country in COUNTRIES:
                    await _set_acceptance(
                        session,
                        game_id,
                        country,
                        issue_id,
                        {"3.1": 0.5, "3.2": 0.5, "3.3": 0.1},
                    )
            finally:
                await agen.aclose()

            state = await _proposal_step(client, game_id)
            assert state["status"] == "ISSUE_VOTE"
            return state["round3"]["active_issue"]["proposed_option_id"]

    chosen_1 = await _run_once(44401)
    chosen_2 = await _run_once(44401)
    assert chosen_1 == "3.1"
    assert chosen_2 == "3.1"


@pytest.mark.asyncio
async def test_vote_unanimity_false_records_failed_vote():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    issue_id = "1"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=50501)
        await _advance_issue_to_debate_end(client, game_id, issue_id)
        state = await _proposal_step(client, game_id)
        proposed_option = state["round3"]["active_issue"]["proposed_option_id"]

        agen = get_session()
        session = await agen.__anext__()
        try:
            for country in COUNTRIES:
                await _set_acceptance(
                    session,
                    game_id,
                    country,
                    issue_id,
                    {proposed_option: 0.8},
                )
            await _set_acceptance(session, game_id, "BRA", issue_id, {proposed_option: 0.6})
        finally:
            await agen.aclose()

        await _vote_steps(client, game_id, len(VOTE_ORDER))

        agen = get_session()
        session = await agen.__anext__()
        try:
            vote_row = await _fetch_votes_row(session, game_id, issue_id)
        finally:
            await agen.aclose()

        assert vote_row["passed"] is False
        votes_by_country = vote_row["votes_by_country"]
        assert set(votes_by_country.keys()) == set(COUNTRIES)
        assert votes_by_country["BRA"] == "NO"


@pytest.mark.asyncio
async def test_vote_unanimity_true_records_passed_vote():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    issue_id = "1"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=50502)
        await _advance_issue_to_debate_end(client, game_id, issue_id)
        state = await _proposal_step(client, game_id)
        proposed_option = state["round3"]["active_issue"]["proposed_option_id"]

        agen = get_session()
        session = await agen.__anext__()
        try:
            for country in COUNTRIES:
                await _set_acceptance(
                    session,
                    game_id,
                    country,
                    issue_id,
                    {proposed_option: 0.8},
                )
        finally:
            await agen.aclose()

        await _vote_steps(client, game_id, len(VOTE_ORDER))

        agen = get_session()
        session = await agen.__anext__()
        try:
            vote_row = await _fetch_votes_row(session, game_id, issue_id)
        finally:
            await agen.aclose()

        assert vote_row["passed"] is True
        votes_by_country = vote_row["votes_by_country"]
        assert set(votes_by_country.keys()) == set(COUNTRIES)
        assert all(val == "YES" for val in votes_by_country.values())


@pytest.mark.asyncio
async def test_vote_order_excludes_chair_and_ngos():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    issue_id = "1"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=50503)
        await _advance_issue_to_debate_end(client, game_id, issue_id)
        state = await _proposal_step(client, game_id)
        active = state["round3"]["active_issue"]

        vote_order = active.get("vote_order", [])
        assert vote_order == list(VOTE_ORDER)
        assert CHAIR not in vote_order

        roles = state.get("roles", {})
        ngo_roles = [rid for rid, info in roles.items() if isinstance(info, dict) and info.get("type") == "ngo"]
        assert set(ngo_roles).isdisjoint(set(vote_order))
