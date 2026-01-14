import json
from typing import Any, Dict, List, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app
from backend.state import VOTE_ORDER
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _vote_sequence_for_issue(session: AsyncSession, game_id: str, issue_id: str) -> List[str]:
    rows = await session.execute(
        text(
            """
            SELECT role_id
            FROM transcript_entries
            WHERE game_id = :gid
              AND phase = 'ISSUE_VOTE'
              AND (metadata ->> 'issue_id') = :iid
              AND metadata ? 'vote'
            ORDER BY created_at ASC, id ASC
            """
        ),
        {"gid": game_id, "iid": issue_id},
    )
    return [r[0] for r in rows.fetchall()]


@pytest.mark.asyncio
async def test_vote_order_and_resolution_semantics():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    issue_id = "3"  # 3-option issue with tie-break semantics
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=202601)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": issue_id, "human_placement": "skip"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

        # consume debate rounds
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        q1 = state["round3"]["active_issue"]["debate_queue"]
        for _ in range(len(q1)):
            await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        q2 = state["round3"]["active_issue"]["debate_queue"]
        for _ in range(len(q2)):
            await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

        # proposal
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

        # votes
        for _ in range(6):
            await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

        # resolution
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        final_state = (await client.get(f"/games/{game_id}")).json()["state"]
        active = final_state["round3"]["active_issue"]
        votes = active.get("votes", {})

        # Canary assertions
        assert set(votes.keys()) == set(VOTE_ORDER)
        assert active.get("proposed_option_id") in ("3.1", "3.2", "3.3")

        agen = get_session()
        session = await agen.__anext__()
        try:
            vote_sequence = await _vote_sequence_for_issue(session, game_id, issue_id)
        finally:
            await agen.aclose()

        assert vote_sequence == list(VOTE_ORDER)


@pytest.mark.asyncio
async def test_checkpoints_follow_transcripts():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=303002)

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
        finally:
            await agen.aclose()

        # advance a couple of transcripted actions (round3 start + intro continue)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "skip"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
        finally:
            await agen.aclose()

        assert t_after > t_before
        assert c_after > c_before
