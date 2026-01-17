import pytest
import asyncio

from backend.llm_provider import OpenAIProvider, ValidationError, DEFAULT_OPENAI_MODEL


@pytest.mark.asyncio
async def test_openai_provider_success_stub():
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
