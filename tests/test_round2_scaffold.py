import json

import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.db import get_session


async def _prepare_to_round2_setup(client: AsyncClient) -> str:
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
    # step through all speakers
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        step_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_1_STEP", "payload": {}},
        )
        assert step_resp.status_code == 200
    # now status should be ROUND_2_SETUP
    get_resp = await client.get(f"/games/{game_id}")
    assert get_resp.json()["state"]["status"] == "ROUND_2_SETUP"
    return game_id


async def _count_transcripts(session: AsyncSession, game_id: str) -> int:
    res = await session.execute(text("SELECT COUNT(*) FROM transcript_entries WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _count_checkpoints(session: AsyncSession, game_id: str) -> int:
    res = await session.execute(text("SELECT COUNT(*) FROM checkpoints WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


@pytest.mark.asyncio(scope="session")
async def test_round2_ready_writes_transcript_and_checkpoint():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_to_round2_setup(client)

        t_before, c_before = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count_transcripts(session, game_id)
            c_before = await _count_checkpoints(session, game_id)
            break

        resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
        assert resp.status_code == 200
        state = resp.json()["state"]
        assert state["status"] == "ROUND_2_SELECT_CONVO_1"

        t_after, c_after = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count_transcripts(session, game_id)
            c_after = await _count_checkpoints(session, game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1

        # ensure transcript entry is visible and round 2
        resp_transcript = await client.get(f"/games/{game_id}/transcript")
        entries = resp_transcript.json()
        last = entries[-1]
        assert last["phase"] == "ROUND_2"
        assert last["visible_to_human"] is True


@pytest.mark.asyncio(scope="session")
async def test_convo1_selection_writes_transcript_and_checkpoint():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_to_round2_setup(client)

        # enter selection state
        ready_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
        assert ready_resp.status_code == 200

        t_before, c_before = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count_transcripts(session, game_id)
            c_before = await _count_checkpoints(session, game_id)
            break

        select_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
        )
        assert select_resp.status_code == 200
        state = select_resp.json()["state"]
        assert state["status"] == "ROUND_2_CONVERSATION_ACTIVE"
        assert state["round2"]["convo1"]["partner_role"] == "BRA"

        t_after, c_after = 0, 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count_transcripts(session, game_id)
            c_after = await _count_checkpoints(session, game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1

        resp_transcript = await client.get(f"/games/{game_id}/transcript", params={"visible_to_human": "true"})
        entries = resp_transcript.json()
        last = entries[-1]
        assert last["phase"] == "ROUND_2"
        assert last["content"].startswith("Private negotiation started with")
