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


async def _prepare_convo_active(client: AsyncClient) -> str:
    create_resp = await client.post("/games", json={})
    assert create_resp.status_code == 200
    game_id = create_resp.json()["game_id"]
    rc_resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}},
    )
    assert rc_resp.status_code == 200
    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    assert r1_ready.status_code == 200
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        step_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_1_STEP", "payload": {}},
        )
        assert step_resp.status_code == 200
    # into round2 setup
    ready_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
    assert ready_resp.status_code == 200
    # select partner
    select_resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    assert select_resp.status_code == 200
    assert select_resp.json()["state"]["status"] == "ROUND_2_CONVERSATION_ACTIVE"
    return game_id


@pytest.mark.asyncio(scope="session")
async def test_conversation_progression_and_checkpoints():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_convo_active(client)

        t_before, c_before = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        # 5 exchanges -> 10 messages + 1 interrupt = +11 transcripts
        for i in range(5):
            resp = await client.post(
                f"/games/{game_id}/advance",
                json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
            )
            assert resp.status_code == 200

        t_after, c_after = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 11
        # 5 exchanges *2 + interrupt checkpoint = 11 checkpoints deltas (one per message including interrupt)
        assert c_after - c_before == 11


@pytest.mark.asyncio(scope="session")
async def test_interrupt_and_final_closure():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_convo_active(client)

        # run 5 exchanges to trigger interrupt
        for i in range(5):
            resp = await client.post(
                f"/games/{game_id}/advance",
                json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
            )
            assert resp.status_code == 200
        transcript_resp = await client.get(f"/games/{game_id}/transcript")
        entries = transcript_resp.json()
        assert any(e.get("metadata", {}).get("interrupt") for e in entries if isinstance(e.get("metadata"), dict))

        t_before, c_before = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        # Final human message after interrupt
        final_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
        )
        assert final_resp.status_code == 200
        state = final_resp.json()["state"]
        assert state["status"] == "ROUND_2_SELECT_CONVO_2"
        assert state["round2"]["convo1"]["status"] == "CLOSED"

        t_after, c_after = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 2
        assert c_after - c_before == 2

        # No further messages allowed
        blocked = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": "extra"}},
        )
        assert blocked.status_code == 400
