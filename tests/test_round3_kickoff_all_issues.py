import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.db import get_session
from tests.test_round3_issue_intro import _reach_round3_setup


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "issue_id,expected_option_ids",
    [
        ("1", ["1.1", "1.2"]),
        ("2", ["2.1", "2.2"]),
        ("3", ["3.1", "3.2", "3.3"]),
        ("4", ["4.1", "4.2"]),
    ],
)
async def test_round3_intro_all_issues(issue_id: str, expected_option_ids: list[str]):
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup(client)

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": issue_id, "human_placement": "first"}},
        )
        assert resp.status_code == 200
        state = resp.json()["state"]
        assert state["status"] == "ISSUE_INTRO"
        active = state["round3"]["active_issue"]
        assert active["issue_id"] == issue_id
        option_ids = [o["option_id"] for o in active["options"]]
        for oid in expected_option_ids:
            assert oid in option_ids

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        assert t_after - t_before == 1
        assert c_after - c_before == 1

        transcript = await client.get(f"/games/{game_id}/transcript")
        entries = transcript.json()
        last = entries[-1]
        assert last["phase"] == "ISSUE_INTRO"
        assert last["visible_to_human"] is True
        assert last.get("metadata", {}).get("issue_id") == issue_id
        new_tid = last["id"]

        # Checkpoint tied to this transcript
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            cp = await session.execute(
                text(
                    "SELECT id, created_at FROM checkpoints WHERE game_id = :gid AND transcript_entry_id = :tid LIMIT 1"
                ),
                {"gid": game_id, "tid": new_tid},
            )
            row = cp.first()
            assert row is not None
            break
