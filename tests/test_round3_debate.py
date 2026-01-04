import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.ai import FakeLLM
from backend.db import get_session


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _reach_issue_debate(client: AsyncClient, human_placement: str = "skip") -> str:
    create_resp = await client.post("/games", json={})
    game_id = create_resp.json()["game_id"]
    await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
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
    await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": human_placement}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
    return game_id


@pytest.mark.asyncio(scope="session")
async def test_full_debate_progression_all_ai():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_issue_debate(client, human_placement="skip")

        # Round 1 queue length
        state_resp = await client.get(f"/games/{game_id}")
        queue1 = state_resp.json()["state"]["round3"]["active_issue"]["debate_queue"]

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        for _ in range(len(queue1)):
            resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            assert resp.status_code == 200
            assert resp.json()["state"]["status"] in ("ISSUE_DEBATE_ROUND_1", "ISSUE_DEBATE_ROUND_2")

        state_mid = (await client.get(f"/games/{game_id}")).json()["state"]
        assert state_mid["status"] == "ISSUE_DEBATE_ROUND_2"
        queue2 = state_mid["round3"]["active_issue"]["debate_queue"]

        for _ in range(len(queue2)):
            resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            assert resp.status_code == 200

        final_state = (await client.get(f"/games/{game_id}")).json()["state"]
        assert final_state["status"] == "ISSUE_POSITION_FINALIZATION"

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        # One transcript/checkpoint per AI speech; total = len(queue1)+len(queue2)
        assert t_after - t_before == len(queue1) + len(queue2)
        assert c_after - c_before == len(queue1) + len(queue2)


@pytest.mark.asyncio(scope="session")
async def test_human_turn_requires_explicit_message():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_issue_debate(client, human_placement="first")
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        queue = state["round3"]["active_issue"]["debate_queue"]
        assert queue[0] == state["human_role_id"]

        # Step without human message should fail
        bad = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert bad.status_code == 400

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        ok = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "HUMAN_DEBATE_MESSAGE", "payload": {"text": "human opens"}},
        )
        assert ok.status_code == 200
        state_after = ok.json()["state"]
        assert state_after["round3"]["active_issue"]["debate_cursor"] == 1

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1
