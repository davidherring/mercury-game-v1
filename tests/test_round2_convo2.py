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


async def _reach_convo2_select(client: AsyncClient) -> str:
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
    # 5 exchanges + final to close convo1
    for i in range(5):
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
        )
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
    )
    return game_id


@pytest.mark.asyncio
async def test_skip_convo2():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_convo2_select(client)
        # counts before skip
        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        skip_resp = await client.post(f"/games/{game_id}/advance", json={"event": "CONVO_2_SKIPPED", "payload": {}})
        assert skip_resp.status_code == 200
        state = skip_resp.json()["state"]
        assert state["status"] == "ROUND_2_WRAP_UP"

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1

        transcript = await client.get(f"/games/{game_id}/transcript")
        last = transcript.json()[-1]
        assert "skipped" in last["content"].lower()


@pytest.mark.asyncio
async def test_select_convo2_and_progression():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_convo2_select(client)

        select_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_2_SELECTED", "payload": {"partner_role_id": "CAN"}},
        )
        assert select_resp.status_code == 200
        state = select_resp.json()["state"]
        assert state["status"] == "ROUND_2_CONVERSATION_ACTIVE"
        assert state["round2"]["active_convo_index"] == 2
        assert state["round2"]["convo2"]["partner_role"] == "CAN"

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        # 5 exchanges -> 10 messages + interrupt = +11
        for i in range(5):
            resp = await client.post(
                f"/games/{game_id}/advance",
                json={"event": "CONVO_2_MESSAGE", "payload": {"content": f"c2-{i}"}},
            )
            assert resp.status_code == 200

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 11
        assert c_after - c_before == 11

        # Final exchange -> +3 transcripts (human, ai, wrap) and +3 checkpoints; state moves to wrap
        t_before_final = t_after
        c_before_final = c_after
        final_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_2_MESSAGE", "payload": {"content": "final2"}},
        )
        assert final_resp.status_code == 200
        state = final_resp.json()["state"]
        assert state["status"] == "ROUND_2_WRAP_UP"
        assert state["round2"]["convo2"]["status"] == "CLOSED"

        t_after_final = c_after_final = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after_final = await _count(session, "transcript_entries", game_id)
            c_after_final = await _count(session, "checkpoints", game_id)
            break

        assert t_after_final - t_before_final == 3
        assert c_after_final - c_before_final == 3

        # No further messages allowed
        blocked = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_2_MESSAGE", "payload": {"content": "extra2"}},
        )
        assert blocked.status_code == 400


@pytest.mark.asyncio
async def test_wrap_up_to_round3_setup():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_convo2_select(client)
        # skip convo2 to reach wrap quickly
        await client.post(f"/games/{game_id}/advance", json={"event": "CONVO_2_SKIPPED", "payload": {}})

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        wrap_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})
        assert wrap_resp.status_code == 200
        state = wrap_resp.json()["state"]
        assert state["status"] == "ROUND_3_SETUP"

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1


@pytest.mark.asyncio
async def test_convo2_partner_validation():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_convo2_select(client)

        # same as convo1 partner should fail
        t_before, c_before = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        bad_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_2_SELECTED", "payload": {"partner_role_id": "BRA"}},
        )
        assert bad_resp.status_code == 400

        good_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_2_SELECTED", "payload": {"partner_role_id": "CAN"}},
        )
        assert good_resp.status_code == 200

        t_after, c_after = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1
