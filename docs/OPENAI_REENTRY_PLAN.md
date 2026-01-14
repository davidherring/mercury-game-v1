OpenAI Re-entry Plan — 2026-01-13

## Re-entry insertion point (single swap location)
- **File/function:** `backend/llm_provider.py:get_llm_provider`
- Provider selection must stay centralized here; no other file may branch on env/settings for LLM choice. Round 2 call sites in `backend/main.py` continue to call `get_llm_provider`.

## Contracts that must hold
- **Request schema (LLMRequest)**: dict containing `game_id` (str), `role_id` (str), `status` (str), `prompt` (str), `prompt_version` (str), `request_payload` (dict), optional `conversation_context`, `game_state_excerpt`.
- **Response schema (LLMResponse)**: dict with required `assistant_text: str`, optional `metadata: dict|None`.
- **Error handling**: provider failures return HTTP 502 from `/advance`; no AI transcript is written on failure; a trace row is still written capturing error details; human message + state already committed before LLM call remain unchanged.
- **Trace expectations**: every provider call writes `llm_traces` with `provider`, `model`, `prompt_version`, `request_payload`, `response_payload`, `game_id`, `role_id`, `status`.

## Configuration rules (strict)
- Default behavior: system must boot and tests must pass with FakeLLM even if OpenAI-related env vars exist.
- OpenAI enablement: OpenAI is enabled only via a single, centralized switch (choose one: LLM_PROVIDER=openai or explicit injection), evaluated only in backend/llm_provider.py:get_llm_provider.
- Settings parsing: Settings must not hard-fail on “extra” env keys. If strict validation is kept, OpenAI-related keys must be explicitly modeled as optional fields so they don’t crash the app when present.
- Required keys: OPENAI_API_KEY is required only when OpenAI is enabled; otherwise ignored.
- Caching discipline: tests that modify env must clear get_settings() cache (e.g., reset_settings_cache() if present) and clear any provider cache on app.state to prevent cross-test contamination.

## First success criteria
- Target: one Round 2 exchange using OpenAI behind a single env flag (`LLM_PROVIDER=openai` at startup) in `get_llm_provider`.
- Tests remain deterministic: default provider remains FakeLLM; tests never call network. Add one stubbed provider test in `tests/test_llm_traces.py::test_openai_wiring_stub` that injects a deterministic StubOpenAIProvider (implements the LLMProvider protocol) and asserts request shape + llm_traces provider/model/prompt_version fields. No network calls.

## Rollback strategy
- Disable OpenAI by unsetting `LLM_PROVIDER` (defaults to FakeLLM). If any 502s appear in canary tests, trace write missing on error, or transcript ordering regressions occur, revert to FakeLLM-only selection in `get_llm_provider`.

## Checklist
- [ ] Gate OpenAI-specific tests behind an explicit opt-in flag so FakeLLM-only CI remains green.
- [ ] Centralize provider selection in `get_llm_provider` with `LLM_PROVIDER` flag.
- [ ] Enforce request/response validation (`assistant_text` required).
- [ ] Ensure llm_traces written on success and error.
- [ ] Add stubbed OpenAI wiring test (no network).
- [ ] Confirm tests default to FakeLLM (CI env).
- [ ] Document required env vars and defaults in README.
- [ ] Verify Round 2 transcript/trace ordering unchanged.
- [ ] Provide rollback toggle (unset `LLM_PROVIDER`).
