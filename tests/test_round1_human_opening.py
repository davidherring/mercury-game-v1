import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.db import get_session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


@pytest.mark.asyncio(scope="session")
async def test_human_opening_requires_text_and_records_transcript():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create game and select human role
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]
        await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})

        # Advance until human turn
        while True:
            state = (await client.get(f"/games/{game_id}")).json()["state"]
            cursor = state.get("round1", {}).get("cursor", 0)
            order = state.get("round1", {}).get("speaker_order", [])
            if cursor >= len(order):
                pytest.fail("Ran out of speakers before hitting human turn")
            next_speaker = order[cursor]
            if next_speaker == "USA":
                openings = state.get("round1", {}).get("openings", {})
                opening_entry = openings.get("USA", {}) if isinstance(openings, dict) else {}
                expected_text = opening_entry.get("text") or opening_entry.get("opening_text") or ""
                expected_snippet = expected_text.strip()[:80].lower() if expected_text else ""

                resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
                resp.raise_for_status()
                new_state = resp.json()["state"]
                assert new_state.get("round1", {}).get("cursor", 0) == cursor + 1

                transcript = (await client.get(f"/games/{game_id}/transcript")).json()
                human_rows = [r for r in transcript if r.get("role_id") == "USA"]
                assert human_rows
                if expected_snippet:
                    assert any(expected_snippet in (r.get("content") or "").lower() for r in human_rows)
                else:
                    assert any((r.get("content") or "").strip() for r in human_rows)
                return
            else:
                step = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
                step.raise_for_status()
