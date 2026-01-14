import json

import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.db import get_session
from backend.main import app
from test_round2_conversation import _prepare_convo_active


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


def _reset_provider_cache() -> None:
    if hasattr(app.state, "llm_provider"):
        delattr(app.state, "llm_provider")
    get_settings.cache_clear()


@pytest.mark.asyncio(scope="session")
async def test_round2_openai_failure_semantics(monkeypatch: pytest.MonkeyPatch):
    _reset_provider_cache()
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    class StubOpenAIProvider:
        provider_name = "openai"
        model_name = "stub-model"

        async def generate(self, request):
            raise Exception("boom")

    def _stub_get_llm_provider(_app_state):
        return StubOpenAIProvider()

    monkeypatch.setattr("backend.main.get_llm_provider", _stub_get_llm_provider)

    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _prepare_convo_active(client)

        before_transcript = await client.get(f"/games/{game_id}/transcript")
        before_entries = before_transcript.json()
        before_ai = [
            entry
            for entry in before_entries
            if entry.get("phase") == "ROUND_2"
            and entry.get("role_id") == "BRA"
            and isinstance(entry.get("metadata"), dict)
            and entry.get("metadata", {}).get("sender") == "ai"
            and entry.get("metadata", {}).get("convo") == "convo1"
        ]

        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": "hello"}},
        )
        assert resp.status_code == 502

        after_transcript = await client.get(f"/games/{game_id}/transcript")
        after_entries = after_transcript.json()
        after_ai = [
            entry
            for entry in after_entries
            if entry.get("phase") == "ROUND_2"
            and entry.get("role_id") == "BRA"
            and isinstance(entry.get("metadata"), dict)
            and entry.get("metadata", {}).get("sender") == "ai"
            and entry.get("metadata", {}).get("convo") == "convo1"
        ]
        assert len(after_ai) == len(before_ai)

        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            traces = await _fetch_llm_traces(session, game_id)
        finally:
            await agen.aclose()

        assert traces, "No llm_traces rows found"
        trace = traces[-1]
        assert trace["provider"] == "openai"
        resp_payload = trace.get("response_payload") or {}
        if isinstance(resp_payload, str):
            resp_payload = json.loads(resp_payload)
        assert resp_payload.get("error_type") == "Exception"
        assert resp_payload.get("error_message") == "boom"
