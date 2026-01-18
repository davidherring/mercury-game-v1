import json
from typing import Any, Dict, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _load_state(session: AsyncSession, game_id: str) -> Dict[str, Any]:
    row = await session.execute(
        text("SELECT state FROM game_state WHERE game_id = :gid"),
        {"gid": game_id},
    )
    state = row.scalar_one()
    return state if isinstance(state, dict) else cast(Dict[str, Any], json.loads(state))


async def _save_state(session: AsyncSession, game_id: str, state: Dict[str, Any]) -> None:
    await session.execute(
        text("UPDATE game_state SET state = :state, updated_at = now() WHERE game_id = :gid"),
        {"state": json.dumps(state), "gid": game_id},
    )
    await session.commit()


async def _set_acceptance(
    session: AsyncSession,
    game_id: str,
    role_id: str,
    issue_id: str,
    updates: Dict[str, Any],
) -> None:
    state = await _load_state(session, game_id)
    stances = state.setdefault("stances", {})
    stances.setdefault(role_id, {}).setdefault(issue_id, {}).setdefault("acceptance", {})
    acceptance = stances[role_id][issue_id]["acceptance"]
    acceptance.update(updates)
    await _save_state(session, game_id, state)


async def _prepare_round2_convo(client: AsyncClient) -> str:
    create_resp = await client.post("/games", json={})
    assert create_resp.status_code == 200
    game_id = create_resp.json()["game_id"]
    rc_resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}},
    )
    assert rc_resp.status_code == 200
    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    assert r1_ready.status_code == 200
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        step_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_1_STEP", "payload": {}},
        )
        assert step_resp.status_code == 200
    ready_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
    assert ready_resp.status_code == 200
    select_resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    assert select_resp.status_code == 200
    return game_id


@pytest.mark.asyncio
async def test_round3_speech_updates_speaker_stance_only():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="USA", seed=10101)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "first"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        speaker = state["round3"]["active_issue"]["debate_queue"][0]
        assert speaker == "USA"

        agen = get_session()
        session = await agen.__anext__()
        try:
            await _set_acceptance(session, game_id, "USA", "1", {"1.1": 0.4})
            await _set_acceptance(session, game_id, "BRA", "1", {"1.1": 0.4})
        finally:
            await agen.aclose()

        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "HUMAN_DEBATE_MESSAGE", "payload": {"text": "I support 1.1"}},
        )
        assert resp.status_code == 200

        state_after = (await client.get(f"/games/{game_id}")).json()["state"]
        usa_acc = state_after["stances"]["USA"]["1"]["acceptance"]["1.1"]
        bra_acc = state_after["stances"]["BRA"]["1"]["acceptance"]["1.1"]
        assert usa_acc == 0.45
        assert bra_acc == 0.4

        log = state_after.get("round3", {}).get("stance_log", [])
        assert any(
            entry.get("role_id") == "USA" and entry.get("option_id") == "1.1"
            for entry in log
        )


@pytest.mark.asyncio
async def test_round2_message_updates_both_participants():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_round2_convo(client)
        agen = get_session()
        session = await agen.__anext__()
        try:
            await _set_acceptance(session, game_id, "USA", "1", {"1.1": 0.4})
            await _set_acceptance(session, game_id, "BRA", "1", {"1.1": 0.4})
        finally:
            await agen.aclose()

        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": "Discuss 1.1"}},
        )
        assert resp.status_code == 200

        state_after = (await client.get(f"/games/{game_id}")).json()["state"]
        usa_acc = state_after["stances"]["USA"]["1"]["acceptance"]["1.1"]
        bra_acc = state_after["stances"]["BRA"]["1"]["acceptance"]["1.1"]
        assert usa_acc == 0.45
        assert bra_acc == 0.45

        log = state_after.get("round2", {}).get("stance_log", [])
        roles = {entry.get("role_id") for entry in log}
        assert {"USA", "BRA"}.issubset(roles)


@pytest.mark.asyncio
async def test_null_acceptance_immutable_under_wiring():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_round2_convo(client)
        agen = get_session()
        session = await agen.__anext__()
        try:
            await _set_acceptance(session, game_id, "USA", "1", {"1.2": None})
            await _set_acceptance(session, game_id, "BRA", "1", {"1.2": None})
        finally:
            await agen.aclose()

        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": "1.2"}},
        )
        assert resp.status_code == 200

        state_after = (await client.get(f"/games/{game_id}")).json()["state"]
        assert state_after["stances"]["USA"]["1"]["acceptance"]["1.2"] is None
        assert state_after["stances"]["BRA"]["1"]["acceptance"]["1.2"] is None

        log = state_after.get("round2", {}).get("stance_log", [])
        assert not any(entry.get("option_id") == "1.2" for entry in log)
