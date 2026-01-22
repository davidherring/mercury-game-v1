import pytest
import asyncio

from backend.config import get_settings
from backend.llm_provider import OpenAIProvider, ValidationError, DEFAULT_OPENAI_MODEL, FakeLLMProvider, get_llm_provider


@pytest.mark.asyncio
async def test_openai_provider_success_stub(monkeypatch: pytest.MonkeyPatch):
    get_settings.cache_clear()
    monkeypatch.setenv("MERCURY_ENV", "dev")
    get_settings.cache_clear()
    async def stub_caller(prompt: str) -> str:
        return f"stubbed:{prompt}"

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller)
    resp = await provider.generate({"prompt": "hello"})
    assistant_text = resp.get("assistant_text")
    assert assistant_text is not None
    assert assistant_text == "stubbed:hello"
    metadata = resp.get("metadata")
    assert metadata is not None
    assert metadata.get("provider") == "openai"
    assert metadata.get("model") == DEFAULT_OPENAI_MODEL


@pytest.mark.asyncio
async def test_openai_provider_empty_content_raises(monkeypatch: pytest.MonkeyPatch):
    get_settings.cache_clear()
    monkeypatch.setenv("MERCURY_ENV", "dev")
    get_settings.cache_clear()
    async def stub_caller(prompt: str) -> str:
        return "   "

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller)
    with pytest.raises(ValidationError):
        await provider.generate({"prompt": "hello"})


@pytest.mark.asyncio
async def test_openai_provider_bubbles_errors(monkeypatch: pytest.MonkeyPatch):
    get_settings.cache_clear()
    monkeypatch.setenv("MERCURY_ENV", "dev")
    get_settings.cache_clear()
    async def stub_caller(prompt: str) -> str:
        raise RuntimeError("boom")

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller, max_retries=0)
    with pytest.raises(RuntimeError):
        await provider.generate({"prompt": "hello"})


def test_provider_forces_fake_llm_in_test_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("MERCURY_ENV", "test")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("SUPABASE_DATABASE_URL", "postgresql://test@localhost/testdb")
    get_settings.cache_clear()

    class _AppState:
        pass

    provider = get_llm_provider(_AppState())
    assert isinstance(provider, FakeLLMProvider)
    assert provider.provider_name == "fake"
