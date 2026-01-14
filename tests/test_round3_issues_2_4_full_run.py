import json
from typing import Any, List, Tuple, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _reach_round3_setup_generic(
    client: AsyncClient, *, human_role: str = "AMAP", seed: int = 12345
) -> str:
    create_resp = await client.post("/games", json={})
    create_resp.raise_for_status()
    game_id = create_resp.json()["game_id"]
    # deterministic seed for stable queues/openings
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        async with session.begin():
            await session.execute(text("UPDATE games SET seed = :seed WHERE id = :gid"), {"seed": seed, "gid": game_id})
        break

    await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": human_role}})
    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
    await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    for i in range(5):
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
        )
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "CONVO_2_SKIPPED", "payload": {}})
    wrap_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})
    assert wrap_resp.json()["state"]["status"] == "ROUND_3_SETUP"
    return game_id


async def _run_issue_to_resolution(
    client: AsyncClient, *, issue_id: str, human_role: str = "AMAP"
) -> Tuple[str, dict, int, int]:
    game_id = await _reach_round3_setup_generic(client, human_role=human_role)
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

    prop = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    prop.raise_for_status()
    state = prop.json()["state"]
    assert state["status"] == "ISSUE_VOTE"

    for _ in range(6):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    res = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    res.raise_for_status()
    final_state = res.json()["state"]
    assert final_state["status"] == "ISSUE_RESOLUTION"
    return game_id, final_state, len(queue1), len(queue2)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "issue_id,expected_options",
    [
        ("2", ["2.1", "2.2"]),
        ("3", ["3.1", "3.2", "3.3"]),
        ("4", ["4.1", "4.2"]),
    ],
)
async def test_issues_2_4_full_run(issue_id: str, expected_options: List[str]):
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id, final_state, q1_len, q2_len = await _run_issue_to_resolution(
            client, issue_id=issue_id, human_role="AMAP"
        )
        active = final_state["round3"]["active_issue"]
        assert active["issue_id"] == issue_id
        opt_ids = [o["option_id"] for o in active["options"]]
        for oid in expected_options:
            assert oid in opt_ids

        votes = active["votes"]
        assert list(votes.keys()) == ["BRA", "CAN", "CHN", "EU", "TZA", "USA"]

        # transcript/checkpoint monotonicity
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_total = await _count(session, "transcript_entries", game_id)
            c_total = await _count(session, "checkpoints", game_id)
            break
        assert t_total >= (q1_len + q2_len + 8)  # debate + proposal + votes + resolution
        assert c_total <= t_total


@pytest.mark.asyncio
async def test_proposal_tie_break_lowest_option_id():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP")
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "3", "human_placement": "skip"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

        async for session in get_session():
            assert isinstance(session, AsyncSession)
            async with session.begin():
                state_row = await session.execute(
                    text("SELECT state FROM game_state WHERE game_id = :gid FOR UPDATE"), {"gid": game_id}
                )
                state = state_row.scalar_one()
                if isinstance(state, str):
                    state = json.loads(state)
                for role in state.get("stances", {}):
                    state["stances"][role]["3"] = {
                        "acceptance": {"3.1": 0.0, "3.2": 0.0, "3.3": 0.0},
                        "firmness": 0.5,
                    }
                await session.execute(
                    text("UPDATE game_state SET state = CAST(:state AS jsonb) WHERE game_id = :gid"),
                    {"state": json.dumps(state), "gid": game_id},
                )
            break

        # advance until proposal is selected
        proposal_id = None
        max_steps = 50
        for _ in range(max_steps):
            resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            resp.raise_for_status()
            state = resp.json()["state"]
            ai = state.get("round3", {}).get("active_issue", {})
            proposal_id = ai.get("proposed_option_id")
            if proposal_id:
                break
            if state.get("status") == "ISSUE_VOTE":
                proposal_id = ai.get("proposed_option_id")
                break
        assert proposal_id is not None
        assert proposal_id == "3.1"
