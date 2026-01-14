import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, List, Dict, cast

from backend.ai import FakeLLM
from backend.main import app
from backend.state import VOTE_ORDER
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _advance_issue_in_place(client: AsyncClient, game_id: str, issue_id: str):
    # Start issue
    resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": issue_id, "human_placement": "random"}},
    )
    assert resp.status_code == 200, f"start issue {issue_id} failed: {resp.text}"
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
    assert resp.status_code == 200, f"intro continue failed: {resp.text}"

    state = resp.json()["state"]
    max_steps = 200
    for _ in range(max_steps):
        status = state.get("status")
        if status == "ISSUE_RESOLUTION":
            break
        # If we are on a human debate turn, send the required event
        ai = state.get("round3", {}).get("active_issue", {})
        queue = ai.get("debate_queue", [])
        cursor = int(ai.get("debate_cursor", 0))
        human_role = state.get("human_role_id")
        speaker = queue[cursor] if cursor < len(queue) else None

        if status == "ISSUE_VOTE":
            vote_payload = {"event": "HUMAN_VOTE", "payload": {"vote": "YES"}}
            resp = await client.post(f"/games/{game_id}/advance", json=vote_payload)
            assert resp.status_code == 200, f"human vote failed: {resp.text} state={status}"
            state = resp.json()["state"]
            continue
        if speaker == human_role:
            resp = await client.post(
                f"/games/{game_id}/advance",
                json={"event": "HUMAN_DEBATE_MESSAGE", "payload": {"text": "Test human message."}},
            )
            assert resp.status_code == 200, f"human debate message failed: {resp.text} state={status}"
        else:
            resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            assert resp.status_code == 200, f"advance failed: {resp.text} state={status}"
        state = resp.json()["state"]
    else:
        assert False, "Exceeded max steps without reaching ISSUE_RESOLUTION"

    # After resolution, explicit continue to next issue or review
    resp = await client.post(
        f"/games/{game_id}/advance", json={"event": "ISSUE_RESOLUTION_CONTINUE", "payload": {}}
    )
    assert resp.status_code == 200, f"resolution continue failed: {resp.text} state={state.get('status')}"
    state = resp.json()["state"]
    expected = "REVIEW" if issue_id == "4" else "ROUND_3_SETUP"
    if state.get("status") != expected:
        debug_info = {
            "issue_id": issue_id,
            "status": state.get("status"),
            "round3": state.get("round3", {}),
        }
        assert False, f"Unexpected status after resolution continue: {debug_info}"
    return state


@pytest.mark.asyncio
async def test_game_reaches_review_and_review_payload():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=50001)
        state: Dict[str, Any] | None = None
        for issue_id in ["1", "2", "3", "4"]:
            state = await _advance_issue_in_place(client, game_id, issue_id)

        # Ensure final status is REVIEW
        assert state is not None
        state = cast(Dict[str, Any], state)
        if state.get("status") != "REVIEW":
            resp = await client.post(
                f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}}
            )
            assert resp.status_code == 200, f"advance to review failed: {resp.text}"
            state = cast(Dict[str, Any], resp.json()["state"])
        assert state["status"] == "REVIEW"

        review_resp = await client.get(f"/games/{game_id}/review")
        assert review_resp.status_code == 200
        review = review_resp.json()
        transcript = review.get("transcript", [])
        votes = review.get("votes", [])

        # Transcript sanity
        assert isinstance(transcript, list)
        assert len(transcript) > 0
        # Visibility filter: no hidden Round 2 entries
        for entry in transcript:
            if entry.get("round") == 2:
                assert entry.get("visible_to_human") is True

        # Votes sanity
        assert len(votes) == 4
        issue_ids = {str(v["issue_id"]) for v in votes}
        assert issue_ids == {"1", "2", "3", "4"}
        for v in votes:
            assert set(v["votes_by_country"].keys()) == set(VOTE_ORDER)

        # Optional: ensure transcript ordering is stable (created_at monotonic non-strict)
        created = [t.get("created_at") for t in transcript if "created_at" in t]
        assert created == sorted(created)
