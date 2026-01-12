from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, TypedDict

from .ai import AIResponder, FakeLLM


class LLMRequest(TypedDict, total=False):
    game_id: str
    role_id: str
    status: str
    prompt: str
    prompt_version: str
    conversation_context: Any
    game_state_excerpt: Dict[str, Any]
    request_payload: Dict[str, Any]


class LLMResponse(TypedDict, total=False):
    assistant_text: str
    metadata: Optional[Dict[str, Any]]


class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse:  # pragma: no cover - interface
        ...


class FakeLLMProvider:
    def __init__(self, responder: Optional[AIResponder] = None) -> None:
        self._responder = responder or FakeLLM()

    async def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.get("prompt") or ""
        assistant_text = await self._responder.respond(prompt)
        return {"assistant_text": assistant_text, "metadata": None}


def get_llm_provider(app_state: Any) -> LLMProvider:
    existing = getattr(app_state, "llm_provider", None)
    if existing:
        return existing
    responder = getattr(app_state, "ai_responder", None) or FakeLLM()
    provider = FakeLLMProvider(responder)
    setattr(app_state, "llm_provider", provider)
    return provider


__all__ = ["LLMProvider", "LLMRequest", "LLMResponse", "FakeLLMProvider", "get_llm_provider"]
