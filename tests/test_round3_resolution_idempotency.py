import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Tuple, cast

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _reach_issue_resolution(client: AsyncClient) -> Tuple[str, dict]:
    create_resp = await client.post("/games", json={})
    create_resp.raise_for_status()
    game_id = create_resp.json()["game_id"]

    await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "AMAP"}})
    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
    await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    for i in range(5):
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
        )
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "CONVO_2_SKIPPED", "payload": {}})
    await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})

    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "skip"}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue1 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue1)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue2 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue2)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    prop = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    prop_state = prop.json()["state"]
    assert prop_state["status"] == "ISSUE_VOTE"

    for _ in range(6):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    res = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    res_state = res.json()["state"]
    assert res_state["status"] == "ISSUE_RESOLUTION"
    return game_id, res_state


@pytest.mark.asyncio
async def test_resolution_transcript_idempotent_and_continue_transition():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id, _ = await _reach_issue_resolution(client)

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_before = await _count(session, "transcript_entries", game_id)
        finally:
            await agen.aclose()

        resp1 = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert resp1.status_code == 200
        state = resp1.json()["state"]
        assert state["status"] == "ISSUE_RESOLUTION"

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_after_first = await _count(session, "transcript_entries", game_id)
        finally:
            await agen.aclose()

        resp2 = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert resp2.status_code == 200
        state = resp2.json()["state"]
        assert state["status"] == "ISSUE_RESOLUTION"

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_after_second = await _count(session, "transcript_entries", game_id)
        finally:
            await agen.aclose()

        delta1 = t_after_first - t_before
        assert delta1 in (0, 1)
        assert t_after_second == t_after_first

        resp3 = await client.post(
            f"/games/{game_id}/advance", json={"event": "ISSUE_RESOLUTION_CONTINUE", "payload": {}}
        )
        assert resp3.status_code == 200
        state = resp3.json()["state"]
        assert state["status"] == "ROUND_3_SETUP"

        agen = get_session()
        session = await agen.__anext__()
        try:
            t_after_continue = await _count(session, "transcript_entries", game_id)
        finally:
            await agen.aclose()

        assert t_after_continue - t_after_second == 0
