class AIResponder:
    async def respond(self, prompt: str) -> str:  # pragma: no cover - interface only
        raise NotImplementedError


class FakeLLM(AIResponder):
    async def respond(self, prompt: str) -> str:
        return f"[FAKE_RESPONSE]{prompt}"


__all__ = ["AIResponder", "FakeLLM"]
