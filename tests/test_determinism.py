import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast

from backend.main import app
from backend.db import get_session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _prepare_game_with_seed(client: AsyncClient, seed: int, human_role: str) -> dict:
    create_resp = await client.post("/games", json={})
    assert create_resp.status_code == 200
    game_id = create_resp.json()["game_id"]

    # Override seed directly for determinism in tests
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        async with session.begin():
            await session.execute(text("UPDATE games SET seed = :seed WHERE id = :gid"), {"seed": seed, "gid": game_id})
        break

    # Override seed to be explicit and deterministic
    # Note: using advance events only; we rely on DB seed already set at creation but we enforce same seed by reusing state
    # by reloading state after creation.
    rc_resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": human_role}},
    )
    assert rc_resp.status_code == 200

    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    assert r1_ready.status_code == 200

    get_resp = await client.get(f"/games/{game_id}")
    assert get_resp.status_code == 200
    return {"id": game_id, "state": get_resp.json()["state"]}


@pytest.mark.asyncio(scope="session")
async def test_deterministic_speaker_order_and_openings():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        g1 = await _prepare_game_with_seed(client, seed=1234, human_role="USA")
        g2 = await _prepare_game_with_seed(client, seed=1234, human_role="USA")

        order1 = g1["state"]["round1"]["speaker_order"]
        order2 = g2["state"]["round1"]["speaker_order"]
        assert order1 == order2

        openings1 = g1["state"]["round1"]["openings"]
        openings2 = g2["state"]["round1"]["openings"]
        assert openings1 == openings2

        # First step transcript should match opening text for first speaker
        first_speaker = order1[0]
        step1 = await client.post(f"/games/{g1['id']}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        step2 = await client.post(f"/games/{g2['id']}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        assert step1.status_code == 200 and step2.status_code == 200
        # Check stored openings remain aligned
        s1_open = step1.json()["state"]["round1"]["openings"][first_speaker]["text"]
        s2_open = step2.json()["state"]["round1"]["openings"][first_speaker]["text"]
        assert s1_open == s2_open


@pytest.mark.asyncio(scope="session")
async def test_human_not_first_in_subgroup():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game = await _prepare_game_with_seed(client, seed=9999, human_role="USA")
        order = game["state"]["round1"]["speaker_order"]
        # Countries subgroup: first 6 entries (per docs: BRA, CAN, CHN, EU, TZA, USA)
        countries = order[:6]
        assert "USA" in countries
        assert countries[0] != "USA"
