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
                # ROUND_1_STEP should fail on human turn
                resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
                assert resp.status_code == 400
                assert "HUMAN_OPENING_STATEMENT" in resp.text

                # Send human opening text
                opening_text = "Hello from human opening"
                ok = await client.post(
                    f"/games/{game_id}/advance",
                    json={"event": "HUMAN_OPENING_STATEMENT", "payload": {"text": opening_text}},
                )
                ok.raise_for_status()
                new_state = ok.json()["state"]
                assert new_state.get("round1", {}).get("cursor", 0) == cursor + 1

                # Verify transcript contains the human opening text
                async for session in get_session():
                    assert isinstance(session, AsyncSession)
                    t_count = await _count(session, "transcript_entries", game_id)
                    break
                transcript = (await client.get(f"/games/{game_id}/transcript")).json()
                human_rows = [r for r in transcript if r.get("role_id") == "USA"]
                assert any(opening_text in (r.get("content") or "") for r in human_rows)
                return
            else:
                step = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
                step.raise_for_status()
