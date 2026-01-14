import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.db import get_session


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _reach_round3_setup(client: AsyncClient) -> str:
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
    wrap_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})
    assert wrap_resp.json()["state"]["status"] == "ROUND_3_SETUP"
    return game_id


@pytest.mark.asyncio
async def test_round3_issue_intro_sets_active_issue_and_transcript():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup(client)

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        start_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "first"}},
        )
        assert start_resp.status_code == 200
        state = start_resp.json()["state"]
        assert state["status"] == "ISSUE_INTRO"
        active = state["round3"]["active_issue"]
        assert active["issue_id"] == "1"
        option_ids = [o["option_id"] for o in active["options"]]
        assert "1.1" in option_ids and "1.2" in option_ids

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before >= 1

        transcript = await client.get(f"/games/{game_id}/transcript")
        last = transcript.json()[-1]
        assert last["visible_to_human"] is True
        assert last["phase"] == "ISSUE_INTRO"


@pytest.mark.asyncio
async def test_issue_intro_continue_moves_to_debate_queue():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup(client)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "first"}},
        )

        resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
        assert resp.status_code == 200
        state = resp.json()["state"]
        assert state["status"] == "ISSUE_DEBATE_ROUND_1"
        queue = state["round3"]["active_issue"]["debate_queue"]
        # Countries first (human USA first in group), then NGOs
        assert queue[:6] == ["USA", "BRA", "CAN", "CHN", "EU", "TZA"]
        assert queue[6:] == ["AMAP", "MFF", "WCPA"]
