from __future__ import annotations

import logging
import os
import inspect
from typing import Any, Dict, Optional, Protocol, TypedDict

from .ai import AIResponder, FakeLLM
from .config import get_settings

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when an LLM response fails basic structure validation."""


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
    @property
    def provider_name(self) -> str:
        ...

    @property
    def model_name(self) -> Optional[str]:
        ...

    async def generate(self, request: LLMRequest) -> LLMResponse:  # pragma: no cover - interface
        ...


def validate_llm_response(resp: Any) -> LLMResponse:
    if not isinstance(resp, dict):
        raise ValidationError("LLM response must be a dict")
    text = resp.get("assistant_text")
    if not isinstance(text, str):
        raise ValidationError("assistant_text must be a string")
    meta = resp.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        raise ValidationError("metadata must be a dict or None")
    return {"assistant_text": text, "metadata": meta}


class FakeLLMProvider:
    def __init__(self, responder: Optional[AIResponder] = None) -> None:
        self._responder = responder or FakeLLM()
        self._provider_name = "fake"
        self._model_name: Optional[str] = "fake"

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> Optional[str]:
        return self._model_name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.get("prompt") or ""
        assistant_text = await self._responder.respond(prompt)
        return {"assistant_text": assistant_text, "metadata": None}


def get_llm_provider(app_state: Any) -> LLMProvider:
    existing = getattr(app_state, "llm_provider", None)
    if existing:
        return existing

    settings = get_settings()
    env_mode = getattr(app_state, "mercury_env", None)
    if not env_mode:
        env_mode = settings.mercury_env
        setattr(app_state, "mercury_env", env_mode)

    if env_mode == "test":
        responder = getattr(app_state, "ai_responder", None) or FakeLLM()
        provider = FakeLLMProvider(responder)
    else:
        provider_choice = (settings.llm_provider or "").lower()
        if provider_choice == "openai" and settings.openai_api_key:
            model_name = settings.openai_model or DEFAULT_OPENAI_MODEL
            provider = OpenAIProvider(api_key=settings.openai_api_key, model=model_name)
        else:
            responder = getattr(app_state, "ai_responder", None) or FakeLLM()
            provider = FakeLLMProvider(responder)

    if settings.app_env == "local":
        logger.info(
            "LLM provider selected",
            extra={
                "mercury_env": env_mode,
                "llm_provider_env": os.getenv("LLM_PROVIDER"),
                "provider_name": getattr(provider, "provider_name", None),
                "model_name": getattr(provider, "model_name", None),
            },
        )

    setattr(app_state, "llm_provider", provider)
    return provider


DEFAULT_OPENAI_MODEL = "gpt-5-nano"


class OpenAIProvider:
    def __init__(self, api_key: str, model: str, timeout: float = 30.0, max_retries: int = 2, client: Any = None) -> None:
        self.api_key = api_key
        self._model_name: str = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = client
        self._provider_name = "openai"

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> Optional[str]:
        return self._model_name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        settings = get_settings()
        if settings.mercury_env == "test":
            raise RuntimeError("OpenAI is disabled in test mode (MERCURY_ENV=test).")

        # Lazy import to avoid hard dependency when not used
        try:
            from openai import AsyncOpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("OpenAI client not available") from exc

        prompt = request.get("prompt") or ""
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                if callable(self._client):
                    maybe_result = self._client(prompt)
                    content = await maybe_result if inspect.isawaitable(maybe_result) else maybe_result
                else:
                    client = self._client or AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
                    # Use Responses API if available; fall back to chat completions if not.
                    if hasattr(client, "responses"):
                        resp = await client.responses.create(  # type: ignore[attr-defined]
                            model=self._model_name,
                            input=prompt,
                        )
                        content = getattr(resp, "output_text", None) or ""
                    else:
                        chat = await client.chat.completions.create(  # type: ignore[attr-defined]
                            model=self._model_name,
                            messages=[{"role": "user", "content": prompt}],
                        )
                        content = chat.choices[0].message.content if chat.choices else ""
                if not isinstance(content, str) or not content.strip():
                    raise ValidationError("OpenAI response was empty")
                return {"assistant_text": content or "", "metadata": {"provider": "openai", "model": self.model_name}}
            except ValidationError:
                raise
            except Exception as exc:  # pragma: no cover - best effort retry
                last_error = exc
                if attempt >= self.max_retries:
                    break
                if isinstance(exc, (TimeoutError,)):
                    continue
                if "rate" in str(exc).lower() or "timeout" in str(exc).lower():
                    continue
                break
        raise RuntimeError(f"OpenAI call failed: {last_error}") if last_error else RuntimeError("OpenAI call failed")


__all__ = [
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "FakeLLMProvider",
    "DEFAULT_OPENAI_MODEL",
    "OpenAIProvider",
    "get_llm_provider",
    "validate_llm_response",
]
