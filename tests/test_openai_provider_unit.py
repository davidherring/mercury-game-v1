import pytest
import asyncio

from backend.llm_provider import OpenAIProvider, ValidationError, DEFAULT_OPENAI_MODEL


@pytest.mark.asyncio
async def test_openai_provider_success_stub():
    async def stub_caller(prompt: str) -> str:
        return f"stubbed:{prompt}"

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller)
    resp = await provider.generate({"prompt": "hello"})
    assert resp["assistant_text"] == "stubbed:hello"
    assert resp["metadata"]["provider"] == "openai"
    assert resp["metadata"]["model"] == DEFAULT_OPENAI_MODEL


@pytest.mark.asyncio
async def test_openai_provider_empty_content_raises():
    async def stub_caller(prompt: str) -> str:
        return "   "

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller)
    with pytest.raises(ValidationError):
        await provider.generate({"prompt": "hello"})


@pytest.mark.asyncio
async def test_openai_provider_bubbles_errors():
    async def stub_caller(prompt: str) -> str:
        raise RuntimeError("boom")

    provider = OpenAIProvider(api_key="dummy", model="stub-model", client=stub_caller, max_retries=0)
    with pytest.raises(RuntimeError):
        await provider.generate({"prompt": "hello"})
