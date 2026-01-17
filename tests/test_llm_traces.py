import json
import pytest
from typing import Any, cast
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from types import SimpleNamespace

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app
from backend.config import get_settings
from backend.llm_provider import get_llm_provider, OpenAIProvider, FakeLLMProvider


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


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return cast(dict[str, Any], json.loads(payload))
        except json.JSONDecodeError:
            return {}
    return {}


def _reset_provider_cache() -> None:
    if hasattr(app.state, "llm_provider"):
        delattr(app.state, "llm_provider")
    get_settings.cache_clear()


# @pytest.mark.asyncio
@pytest.mark.asyncio
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
        assert trace["prompt_version"] == "r2_convo_v3"
        req_payload = _normalize_payload(trace.get("request_payload"))
        assert test_msg in (req_payload.get("prompt") or "")
        assert "Role: You are" in (req_payload.get("prompt") or "")
        context = _normalize_payload(req_payload.get("context"))
        openings = _normalize_payload(context.get("openings"))
        partner_opening = _normalize_payload(openings.get("partner_opening"))
        assert partner_opening.get("initial_stances") is not None
        assert partner_opening.get("conversation_interests") is not None
        human_opening = openings.get("human_opening_text")
        assert isinstance(human_opening, str)
        assert human_opening.strip()
        transcript_tail = context.get("transcript_tail") or []
        assert isinstance(transcript_tail, list)
        assert len(transcript_tail) <= 10
        assert isinstance(transcript_tail[-1], dict)
        # Request-time snapshot: tail ends with the human message before AI generation.
        assert transcript_tail[-1].get("content") == test_msg
        assert transcript_tail[-1].get("role_id") == "USA"
        issues = context.get("issues") or []
        assert isinstance(issues, list)
        assert issues
        issue = issues[0]
        assert isinstance(issue, dict)
        assert issue.get("issue_id")
        assert issue.get("title")
        assert isinstance(issue.get("options"), list)
        if issue.get("options"):
            option = issue["options"][0]
            assert "short_description" not in option
        resp_payload = trace.get("response_payload") or {}
        assert resp_payload.get("assistant_text") == ai_content


@pytest.mark.skip(reason="OpenAI provider selection is disabled in Sprint 14 (FakeLLM-only)")
def test_provider_selection_openai(monkeypatch: pytest.MonkeyPatch):
    _reset_provider_cache()
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setenv("OPENAI_MODEL", "stub-model")
    provider = get_llm_provider(SimpleNamespace())
    assert isinstance(provider, OpenAIProvider)
    assert provider.provider_name == "openai"
    assert provider.model_name == "stub-model"
    _reset_provider_cache()
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    provider2 = get_llm_provider(SimpleNamespace())
    assert isinstance(provider2, FakeLLMProvider)


@pytest.mark.skip(reason="OpenAI provider selection is disabled in Sprint 14 (FakeLLM-only)")
# @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_round2_llm_trace_openai_stub(monkeypatch: pytest.MonkeyPatch):
    _reset_provider_cache()
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setenv("OPENAI_MODEL", "stub-model")

    async def _stub_generate(self, request):
        prompt = request.get("prompt") or ""
        return {"assistant_text": f"[OPENAI_STUB]{prompt}", "metadata": {"provider": "openai", "model": self.model_name}}

    monkeypatch.setattr(OpenAIProvider, "generate", _stub_generate)

    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]

        await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        order_len = len(state["round1"]["speaker_order"])
        for _ in range(order_len):
            await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
        )
        msg = "openai-trace"
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": msg}},
        )

        transcript = (await client.get(f"/games/{game_id}/transcript")).json()
        ai_rows = [r for r in transcript if r.get("role_id") == "BRA" and "[OPENAI_STUB]" in (r.get("content") or "")]
        assert ai_rows, "No AI response rows found for OpenAI stub"
        ai_content = ai_rows[-1]["content"]

        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            traces = await _fetch_llm_traces(session, game_id)
        finally:
            await agen.aclose()

        assert traces, "No llm_traces rows found for OpenAI stub"
        trace = traces[-1]
        assert trace["provider"] == "openai"
        assert trace["model"] == "stub-model"
        assert trace["prompt_version"] == "r2_convo_v3"
        resp_payload = trace.get("response_payload") or {}
        assert resp_payload.get("assistant_text") == ai_content

    _reset_provider_cache()
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
