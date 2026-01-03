import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, cast

from backend.main import app
from backend.db import get_session


async def _count_rows(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _prepare_round1_openings(client: AsyncClient) -> str:
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
    return game_id


@pytest.mark.asyncio(scope="session")
async def test_round1_step_adds_two_transcripts_and_checkpoint():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_round1_openings(client)

        transcripts_before: int | None = None
        checkpoints_before: int | None = None
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            transcripts_before = await _count_rows(session, "transcript_entries", game_id)
            checkpoints_before = await _count_rows(session, "checkpoints", game_id)
            break
        assert transcripts_before is not None
        assert checkpoints_before is not None

        step_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        assert step_resp.status_code == 200
        state = step_resp.json()["state"]
        assert state["round1"]["cursor"] == 1

        transcripts_after: int | None = None
        checkpoints_after: int | None = None
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            transcripts_after = await _count_rows(session, "transcript_entries", game_id)
            checkpoints_after = await _count_rows(session, "checkpoints", game_id)
            break
        assert transcripts_after is not None
        assert checkpoints_after is not None

        assert transcripts_after - transcripts_before == 2
        assert checkpoints_after - checkpoints_before == 1


@pytest.mark.asyncio(scope="session")
async def test_round1_full_progression_reaches_round2_setup():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_round1_openings(client)

        # Fetch speaker order length
        get_resp = await client.get(f"/games/{game_id}")
        assert get_resp.status_code == 200
        state = get_resp.json()["state"]
        order_len = len(state["round1"]["speaker_order"])

        # Step through all speakers
        for _ in range(order_len):
            resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
            assert resp.status_code == 200
            state = resp.json()["state"]

        assert state["status"] == "ROUND_2_SETUP"

        transcript_count: int | None = None
        checkpoint_count: int | None = None
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            transcript_count = await _count_rows(session, "transcript_entries", game_id)
            checkpoint_count = await _count_rows(session, "checkpoints", game_id)
            break
        assert transcript_count is not None
        assert checkpoint_count is not None

        # One Japan open + two per speaker
        expected_transcripts = 1 + 2 * order_len
        assert transcript_count == expected_transcripts
        # Checkpoints: role_confirmed, round1_ready, one per step (order_len), plus create-game checkpoint exists but not counted via state; count at least matches order_len+2
        assert checkpoint_count >= order_len + 2
