import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


async def _advance(client: AsyncClient, game_id: str, event: str, payload: dict):
    resp = await client.post(f"/games/{game_id}/advance", json={"event": event, "payload": payload})
    resp.raise_for_status()
    return resp.json()["state"]


async def _fast_forward_round1(client: AsyncClient, game_id: str):
    while True:
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        if state.get("status") != "ROUND_1_OPENING_STATEMENTS":
            break
        r1 = state.get("round1", {})
        order = r1.get("speaker_order", [])
        cursor = r1.get("cursor", 0)
        if cursor < len(order) and order[cursor] == state.get("human_role_id"):
            await _advance(client, game_id, "HUMAN_OPENING_STATEMENT", {"text": "human opening"})
        else:
            await _advance(client, game_id, "ROUND_1_STEP", {})


@pytest.mark.asyncio(scope="session")
async def test_end_convo1_early_transitions_to_convo2_select():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = (await client.post("/games", json={})).json()["game_id"]
        await _advance(client, game_id, "ROLE_CONFIRMED", {"human_role_id": "USA"})
        await _advance(client, game_id, "ROUND_1_READY", {})
        await _fast_forward_round1(client, game_id)
        await _advance(client, game_id, "ROUND_2_READY", {})
        await _advance(client, game_id, "CONVO_1_SELECTED", {"partner_role_id": "BRA"})
        # one human message
        await _advance(client, game_id, "CONVO_1_MESSAGE", {"content": "hi"})
        state = await _advance(client, game_id, "CONVO_END_EARLY", {})
        assert state.get("status") == "ROUND_2_SELECT_CONVO_2"
        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        contents = [row.get("content") or "" for row in transcript]
        assert not any("The Chair interrupts" in c for c in contents)
        assert not any("Private negotiations concluded" in c for c in contents)


@pytest.mark.asyncio(scope="session")
async def test_end_convo2_early_transitions_to_wrap_up():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = (await client.post("/games", json={})).json()["game_id"]
        await _advance(client, game_id, "ROLE_CONFIRMED", {"human_role_id": "USA"})
        await _advance(client, game_id, "ROUND_1_READY", {})
        await _fast_forward_round1(client, game_id)
        await _advance(client, game_id, "ROUND_2_READY", {})
        await _advance(client, game_id, "CONVO_1_SELECTED", {"partner_role_id": "BRA"})
        await _advance(client, game_id, "CONVO_1_MESSAGE", {"content": "hi"})
        await _advance(client, game_id, "CONVO_END_EARLY", {})
        await _advance(client, game_id, "CONVO_2_SELECTED", {"partner_role_id": "MFF"})
        await _advance(client, game_id, "CONVO_2_MESSAGE", {"content": "hello"})
        state = await _advance(client, game_id, "CONVO_END_EARLY", {})
        assert state.get("status") == "ROUND_2_WRAP_UP"
        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        contents = [row.get("content") or "" for row in transcript]
        assert not any("The Chair interrupts" in c for c in contents)
        assert not any("Private negotiations concluded" in c for c in contents)
