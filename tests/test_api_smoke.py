import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from typing import cast, Any

from backend.main import app


@pytest.mark.asyncio
async def test_health_and_create_game():
    # async with AsyncClient(app=app, base_url="http://testserver") as client:
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        health_resp = await client.get("/health")
        assert health_resp.status_code == 200
        health_json = health_resp.json()
        assert health_json.get("status") == "ok"

        game_resp = await client.post("/games", json={})
        assert game_resp.status_code == 200
        game_json = game_resp.json()
        assert "game_id" in game_json
        assert "state" in game_json
        assert game_json["state"].get("status") == "ROLE_SELECTION"
