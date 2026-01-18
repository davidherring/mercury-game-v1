import json
from typing import Any, Dict, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.main import app


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


def _normalize_issue_id(issue_key: str) -> str:
    if issue_key.startswith("ISSUE_"):
        return issue_key.split("_", 1)[1]
    return issue_key


@pytest.mark.asyncio
async def test_opening_initial_stances_applied_to_state():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_resp = await client.post("/games", json={})
        assert create_resp.status_code == 200
        game_id = create_resp.json()["game_id"]

        agen = get_session()
        session = await agen.__anext__()
        try:
            state = await _load_state(session, game_id)
            state.setdefault("stances", {}).setdefault("USA", {}).setdefault("1", {}).setdefault("acceptance", {})
            state["stances"]["USA"]["1"]["acceptance"]["1.1"] = 0.2
            state["stances"]["USA"]["1"]["acceptance"]["1.2"] = None
            await _save_state(session, game_id, state)
        finally:
            await agen.aclose()

        rc_resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}},
        )
        assert rc_resp.status_code == 200

        r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
        assert r1_ready.status_code == 200
        state_after = r1_ready.json()["state"]

        opening = state_after["round1"]["openings"]["USA"]["initial_stances"]
        by_issue = opening.get("by_issue_id", opening)
        issue1 = by_issue.get("ISSUE_1")
        assert isinstance(issue1, dict)
        preferred = issue1.get("preferred")
        assert isinstance(preferred, str)

        usa_stance = state_after["stances"]["USA"]["1"]
        assert usa_stance.get("preferred") == preferred
        assert usa_stance["acceptance"]["1.1"] == 0.2
        assert usa_stance["acceptance"]["1.2"] is None

        other_issue = None
        for issue_key, issue_data in by_issue.items():
            if issue_key == "ISSUE_1":
                continue
            if isinstance(issue_data, dict) and isinstance(issue_data.get("preferred"), str):
                other_issue = issue_key
                break
        assert other_issue is not None
        issue_id = _normalize_issue_id(other_issue)
        pref_opt = by_issue[other_issue]["preferred"]
        assert usa_stance == state_after["stances"]["USA"]["1"]
        assert state_after["stances"]["USA"][issue_id]["acceptance"][pref_opt] == 0.7
