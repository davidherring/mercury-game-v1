import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast

from backend.main import app


@pytest.mark.asyncio(scope="session")
async def test_get_game_returns_state_and_game():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_resp = await client.post("/games", json={})
        assert create_resp.status_code == 200
        created = create_resp.json()
        game_id = created["game_id"]
        initial_status = created["state"]["status"]

        get_resp = await client.get(f"/games/{game_id}")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert "game" in body and "state" in body
        assert str(body["game"]["id"]) == str(game_id)
        assert body["state"]["status"] == initial_status
