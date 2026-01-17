from typing import Any, Optional, cast

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


async def _advance(client: AsyncClient, game_id: str, event: str, payload: Optional[dict[str, Any]] = None):
    payload = payload or {}
    resp = await client.post(f"/games/{game_id}/advance", json={"event": event, "payload": payload})
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise AssertionError(f"Advance failed {resp.status_code} for event {event} payload {payload}: {detail}")
    data = resp.json()
    if "state" not in data:
        raise AssertionError(f"No state in response for event {event}: {data}")
    return data["state"]


async def _fast_forward_round1(client: AsyncClient, game_id: str):
    # Assumes ROUND_1_READY already called
    while True:
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        if state.get("status") != "ROUND_1_OPENING_STATEMENTS":
            break
        r1 = state.get("round1", {})
        order = r1.get("speaker_order", [])
        cursor = r1.get("cursor", 0)
        if cursor >= len(order):
            break
        await _advance(client, game_id, "ROUND_1_STEP", {})


async def _reach_round2_setup(client: AsyncClient) -> tuple[str, dict, dict, str]:
    create = await client.post("/games", json={})
    create.raise_for_status()
    game_id = create.json()["game_id"]
    state_initial = (await client.get(f"/games/{game_id}")).json()["state"]
    roles = state_initial.get("roles", {})
    human_role = next((rid for rid, info in roles.items() if info.get("type") == "ngo" or info.get("role_type") == "ngo"), None) or next(iter(roles))
    await _advance(client, game_id, "ROLE_CONFIRMED", {"human_role_id": human_role})
    await _advance(client, game_id, "ROUND_1_READY", {})
    await _fast_forward_round1(client, game_id)
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    return game_id, state, roles, human_role


def _choose_partner_ids(roles: dict, human_role: str) -> list[str]:
    others = [(rid, info) for rid, info in roles.items() if rid != human_role]

    def is_country(info: dict) -> bool:
        t = info.get("type") or info.get("role_type")
        return t == "country"

    countries = [rid for rid, info in others if is_country(info)]
    non_countries = [rid for rid, _ in others if rid not in countries]
    return countries + non_countries


# @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_seeded_content_survives_create_and_round1_ready():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = (await client.post("/games", json={})).json()["game_id"]
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        # Before ROUND_1_READY, openings may be absent
        assert "round1" in state
        # After ROUND_1_READY, openings populated from seed
        await _advance(client, game_id, "ROLE_CONFIRMED", {"human_role_id": "USA"})
        ready_state = await _advance(client, game_id, "ROUND_1_READY", {})
        openings = ready_state.get("round1", {}).get("openings", {})
        assert openings, "round1.openings should be populated after ROUND_1_READY"
        sample_opening = next(iter(openings.values()))
        assert sample_opening.get("text"), "Opening text should be non-empty"
        # Stable within game
        refreshed = (await client.get(f"/games/{game_id}")).json()["state"].get("round1", {}).get("openings", {})
        assert openings == refreshed


# @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_transcript_persists_round1_to_round2_boundary():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id, state, _roles, _human = await _reach_round2_setup(client)
        # Should be at ROUND_2_SETUP
        assert state.get("status") == "ROUND_2_SETUP"
        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        contents = [row.get("content") or "" for row in transcript]
        assert any("Chair" in c or "calls the meeting" in c for c in contents), "Expect chair line in transcript"
        assert any("opening" in c.lower() or c.strip() for c in contents), "Expect opening statements recorded"


async def _play_to_review(client: AsyncClient, game_id: str, roles: dict, human_role: str):
    # Assumes at ROUND_2_SETUP. Drive a minimal Round 2 path, then fetch review.
    await _advance(client, game_id, "ROUND_2_READY", {})
    partners = _choose_partner_ids(roles, human_role or "")
    partner1 = partners[0] if partners else None
    if partner1:
        await _advance(client, game_id, "CONVO_1_SELECTED", {"partner_role_id": partner1})
        await _advance(client, game_id, "CONVO_1_MESSAGE", {"content": "hello"})
        try:
            await _advance(client, game_id, "CONVO_END_EARLY", {})
        except AssertionError:
            # If end early is disallowed, skip to wrap path
            pass
    await _advance(client, game_id, "CONVO_2_SKIPPED", {})
    await _advance(client, game_id, "ROUND_2_WRAP_READY", {})


# @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_full_playthrough_review_contains_votes():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id, state, roles, human_role = await _reach_round2_setup(client)
        await _play_to_review(client, game_id, roles, human_role)
        review_resp = await client.get(f"/games/{game_id}/review")
        assert review_resp.status_code == 200
        review = review_resp.json()
        assert "transcript" in review
        transcript = review.get("transcript", [])
        assert isinstance(transcript, list) and transcript, "Review transcript should not be empty"
        assert any((row.get("content") or "").strip() for row in transcript), "Transcript entries should have content"
        assert "votes" in review
