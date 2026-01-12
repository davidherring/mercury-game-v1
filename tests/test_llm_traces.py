import pytest
from typing import Any, cast
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app


async def _fetch_llm_traces(session: AsyncSession, game_id: str) -> list[dict[str, Any]]:
    rows = await session.execute(
        text(
            """
            SELECT game_id, role_id, status, provider, model, prompt_version, request_payload, response_payload
            FROM llm_traces
            WHERE game_id = :gid
            """
        ),
        {"gid": game_id},
    )
    return [dict(row._mapping) for row in rows]


@pytest.mark.asyncio(scope="session")
async def test_round2_llm_writes_trace_row():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]

        # Role select and round 1 ready
        await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
        # consume all openings
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        order_len = len(state["round1"]["speaker_order"])
        for _ in range(order_len):
            await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})

        # Round 2 select and message
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
        )
        test_msg = "hello-trace-test"
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": test_msg}},
        )

        # Fetch transcript to get AI response text
        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        ai_rows = [r for r in transcript if r.get("role_id") == "BRA" and "[FAKE_RESPONSE]" in (r.get("content") or "")]
        assert ai_rows, "No AI response rows found"
        ai_content = ai_rows[-1]["content"]

        # Check llm_traces
        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            traces = await _fetch_llm_traces(session, game_id)
        finally:
            await agen.aclose()

        assert traces, "No llm_traces rows found"
        trace = traces[-1]
        assert trace["provider"] == "fake"
        assert trace["model"] == "fake"
        assert trace["prompt_version"] == "r2_convo_v1"
        req_payload = trace.get("request_payload") or {}
        assert test_msg in (req_payload.get("prompt") or "")
        resp_payload = trace.get("response_payload") or {}
        assert resp_payload.get("assistant_text") == ai_content
