import json
from typing import Any, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.config import get_settings
from backend.db import get_session
from backend.main import app
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _fetch_llm_traces(session: AsyncSession, game_id: str) -> list[dict[str, Any]]:
    rows = await session.execute(
        text(
            """
            SELECT game_id, role_id, status, provider, model, prompt_version, request_payload, response_payload
            FROM llm_traces
            WHERE game_id = :gid
            ORDER BY created_at DESC, id DESC
            """
        ),
        {"gid": game_id},
    )
    return [dict(row._mapping) for row in rows]


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return cast(dict[str, Any], json.loads(payload))
        except json.JSONDecodeError:
            return {}
    return {}


@pytest.mark.asyncio
async def test_round3_openai_speech1_success(monkeypatch: pytest.MonkeyPatch):
    app.state.ai_responder = FakeLLM()
    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_ROUND3_DEBATE_SPEECHES", "1")
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    class StubOpenAIProvider:
        provider_name = "openai"
        model_name = "stub-model"

        async def generate(self, request):
            return {
                "assistant_text": "[OPENAI_STUB]debate",
                "metadata": {"provider": "openai", "model": self.model_name},
            }

    monkeypatch.setattr("backend.main.get_llm_provider", lambda _app_state: StubOpenAIProvider())

    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=90101)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "skip"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

        state = (await client.get(f"/games/{game_id}")).json()["state"]
        queue = state["round3"]["active_issue"]["debate_queue"]
        speaker = queue[0]

        resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert resp.status_code == 200

        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        speech_rows = [
            row
            for row in transcript
            if row.get("phase") == "ISSUE_DEBATE_ROUND_1" and row.get("role_id") == speaker
        ]
        assert speech_rows, "No debate speech transcript row found"
        speech_text = speech_rows[-1]["content"]
        assert speech_text == "[OPENAI_STUB]debate"

        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            traces = await _fetch_llm_traces(session, game_id)
        finally:
            await agen.aclose()

        assert traces, "No llm_traces rows found"
        trace = traces[0]
        assert trace["provider"] == "openai"
        assert trace["prompt_version"] == "r3_debate_speech_v1"
        req_payload = _normalize_payload(trace.get("request_payload"))
        assert req_payload.get("speech_number") == 1
        assert req_payload.get("debate_round") == 1
        assert req_payload.get("issue_id") == "1"
        assert req_payload.get("speaker_role") == speaker
        context = req_payload.get("context")
        assert isinstance(context, dict)
        assert "active_issue" in context
        assert "speech_slot" in context
        resp_payload = _normalize_payload(trace.get("response_payload"))
        assert resp_payload.get("assistant_text") == speech_text


@pytest.mark.asyncio
async def test_round3_openai_speech1_failure(monkeypatch: pytest.MonkeyPatch):
    app.state.ai_responder = FakeLLM()
    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_ROUND3_DEBATE_SPEECHES", "1")
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    class StubOpenAIProvider:
        provider_name = "openai"
        model_name = "stub-model"

        async def generate(self, request):
            if request.get("prompt_version") == "r3_debate_speech_v1":
                raise RuntimeError("boom")
            return {
                "assistant_text": "[OPENAI_STUB]setup",
                "metadata": {"provider": "openai", "model": self.model_name},
            }

    monkeypatch.setattr("backend.main.get_llm_provider", lambda _app_state: StubOpenAIProvider())

    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_round3_setup_generic(client, human_role="AMAP", seed=90102)
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": "skip"}},
        )
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

        state = (await client.get(f"/games/{game_id}")).json()["state"]
        queue = state["round3"]["active_issue"]["debate_queue"]
        speaker = queue[0]

        transcript_before = (await client.get(f"/games/{game_id}/transcript")).json()
        before_count = len(
            [row for row in transcript_before if row.get("phase") == "ISSUE_DEBATE_ROUND_1" and row.get("role_id") == speaker]
        )

        resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert resp.status_code == 502

        transcript_after = (await client.get(f"/games/{game_id}/transcript")).json()
        after_count = len(
            [row for row in transcript_after if row.get("phase") == "ISSUE_DEBATE_ROUND_1" and row.get("role_id") == speaker]
        )
        assert after_count == before_count

        state_after = (await client.get(f"/games/{game_id}")).json()["state"]
        active_after = state_after["round3"]["active_issue"]
        assert active_after.get("debate_cursor") == 0
        assert state_after.get("status") == "ISSUE_DEBATE_ROUND_1"

        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            traces = await _fetch_llm_traces(session, game_id)
        finally:
            await agen.aclose()

        assert traces, "No llm_traces rows found"
        trace = traces[0]
        assert trace["provider"] == "openai"
        assert trace["prompt_version"] == "r3_debate_speech_v1"
        req_payload = _normalize_payload(trace.get("request_payload"))
        assert req_payload.get("speech_number") == 1
        assert req_payload.get("issue_id") == "1"
        assert req_payload.get("speaker_role") == speaker
        context = req_payload.get("context")
        assert isinstance(context, dict)
        assert "active_issue" in context
        assert "speech_slot" in context
        resp_payload = _normalize_payload(trace.get("response_payload"))
        assert resp_payload.get("error_type") == "RuntimeError"
        assert resp_payload.get("error_message") == "boom"
