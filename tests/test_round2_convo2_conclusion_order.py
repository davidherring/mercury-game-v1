import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


async def _advance(client: AsyncClient, game_id: str, event: str, payload: dict):
    resp = await client.post(f"/games/{game_id}/advance", json={"event": event, "payload": payload})
    resp.raise_for_status()
    return resp


async def _fast_forward_round1(client: AsyncClient, game_id: str):
    while True:
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        if state.get("status") != "ROUND_1_OPENING_STATEMENTS":
            break
        # If human turn requires text, send it; otherwise step.
        r1 = state.get("round1", {})
        order = r1.get("speaker_order", [])
        cursor = r1.get("cursor", 0)
        if cursor < len(order) and order[cursor] == state.get("human_role_id"):
            await _advance(client, game_id, "HUMAN_OPENING_STATEMENT", {"text": "human opening"})
        else:
            await _advance(client, game_id, "ROUND_1_STEP", {})


async def _complete_convo(client: AsyncClient, game_id: str, event_name: str):
    # send 5 turns to trigger interrupt, then final turn
    for i in range(5):
        await _advance(client, game_id, event_name, {"content": f"m{i+1}"})
    # final exchange after interrupt
    await _advance(client, game_id, event_name, {"content": "m6"})


@pytest.mark.asyncio
async def test_convo2_conclusion_happens_after_final_exchange():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]

        await _advance(client, game_id, "ROLE_CONFIRMED", {"human_role_id": "USA"})
        await _advance(client, game_id, "ROUND_1_READY", {})
        await _fast_forward_round1(client, game_id)
        await _advance(client, game_id, "ROUND_2_READY", {})
        await _advance(client, game_id, "CONVO_1_SELECTED", {"partner_role_id": "BRA"})
        await _complete_convo(client, game_id, "CONVO_1_MESSAGE")
        # select convo2
        await _advance(client, game_id, "CONVO_2_SELECTED", {"partner_role_id": "MFF"})
        await _complete_convo(client, game_id, "CONVO_2_MESSAGE")

        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        contents = [row.get("content") or "" for row in transcript]

        try:
            idx_concluded = max(i for i, c in enumerate(contents) if "Private negotiations concluded" in c)
        except ValueError:
            pytest.fail("Concluded line not found in transcript")
        try:
            idx_final_human = max(i for i, c in enumerate(contents) if c.strip() == "m6")
            idx_final_ai = max(i for i, c in enumerate(contents) if "[FAKE_RESPONSE]m6" in c)
        except ValueError:
            pytest.fail("Final exchange rows not found")

        assert idx_final_human < idx_concluded
        assert idx_final_ai < idx_concluded
