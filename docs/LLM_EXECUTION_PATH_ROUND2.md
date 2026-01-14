Sprint 13 Working Note — Round 2 LLM Execution Path

## Overview
Round 2 private conversation LLM calls are driven entirely from the POST `/games/{game_id}/advance` handler in `backend/main.py`. Provider selection is centralized in `backend/llm_provider.py` (defaults to FakeLLM; can be OpenAI via env/settings). Prompts are built by `backend/prompt_builder.py` with a version tag (`r2_convo_v1`). Responses are validated, written to `transcript_entries`, and every call is logged to `llm_traces`.

## End-to-end flow (Round 2 human message → AI reply)
1) **Entry point / routing**: FastAPI route POST `/games/{game_id}/advance` in `backend/main.py` dispatches on `req.event`. For Round 2 active conversation (`status == ROUND_2_CONVERSATION_ACTIVE`), events include:
   - `CONVO_1_MESSAGE` / `CONVO_2_MESSAGE`: human sends a message in convo1/2.
   - `CONVO_END_EARLY`: optional human end (handled elsewhere in same status block).
2) **Human message commit**: In the Round 2 handler (main.py, convo block), the human message content (`payload["content"]`) is inserted into `transcript_entries` via `insert_transcript_entry`, and `game_state.round2` counters (turns_used, post_interrupt flags) are updated and persisted via `persist_state`.
3) **Provider selection**: `get_llm_provider(app.state)` in `backend/llm_provider.py`:
   - Reads `Settings` (env) for `LLM_PROVIDER` / `OPENAI_*`.
   - If `LLM_PROVIDER == "openai"` and API key present → `OpenAIProvider`; otherwise `FakeLLMProvider`.
   - Caches provider on `app.state.llm_provider` until cleared.
   - Note: In practice, provider switching is currently fragile because Settings validation can fail when env contains keys the active Settings model doesn’t accept, and because provider instances may be cached on app.state
4) **Prompt build**: `build_round2_conversation_prompt` in `backend/prompt_builder.py` constructs:
   - `prompt_version = "r2_convo_v1"`
   - `prompt` (current human content)
   - `request_payload` (includes prompt, game_id, role_id, partner_role, convo key, turn counters).
   The handler assembles an `LLMRequest` with game_id, role_id (partner), status, prompt_version, prompt, request_payload, conversation_context.
5) **Provider call**: `provider.generate(request)` is awaited. `FakeLLMProvider` uses `FakeLLM.respond(prompt)`; `OpenAIProvider` would call OpenAI (lazy import; optional dependency). Response is validated via `validate_llm_response` (must be dict with `assistant_text: str`, optional `metadata`).
6) **Trace write (success or error)**: `insert_llm_trace` inserts into `llm_traces` with game_id, role_id, status, provider, model, prompt_version, request_payload, response_payload. On exceptions/validation failure, an error payload is logged and HTTP 502 is raised (state not advanced for AI turn).
7) **Transcript write (AI reply)**: On success, AI text (`assistant_text`) is inserted into `transcript_entries` with metadata (partner, sender="ai", index, convo key). Round 2 counters advance; interrupts/final flags may trigger chair interrupt after 5 exchanges and concluding lines after final exchange.
8) **State/transition**: Status remains `ROUND_2_CONVERSATION_ACTIVE` until convo completion; after final exchange/interrupt logic, transitions to `ROUND_2_SELECT_CONVO_2` (after convo1) or `ROUND_2_WRAP_UP` (after convo2).

## Key decision points / invariants
- Provider selection strictly gated by `LLM_PROVIDER=openai`; presence of `OPENAI_API_KEY` alone should not flip provider.
- Prompt version for Round 2 is fixed: `r2_convo_v1`.
- Validation failure or provider exception returns HTTP 502 and logs a trace; AI transcript row is NOT written on failure.
- Trace timing: llm_traces is written before returning an HTTP 502 on provider/validation errors (so failures still produce a trace row even when no AI transcript row is written).
- Human message is always committed before LLM call; AI turn only on successful provider response.
- Trace linkage: `llm_traces.game_id` stores the game UUID (as string in insert params).

## Trace schema snapshot
Table `llm_traces` columns (see `backend/sql/001_init.sql`): `id uuid pk`, `game_id uuid`, `role_id text`, `status text`, `provider text`, `model text`, `prompt_version text`, `request_payload jsonb`, `response_payload jsonb`, `created_at timestamptz default now()`.

## Notes on caching / tests
- `Settings` uses `lru_cache` (get_settings); tests must clear via `reset_settings_cache` when monkeypatching env.
- `get_llm_provider` caches provider on `app.state.llm_provider`; tests clear it to switch providers.
- Sharp edge: app.state.llm_provider caching can cause cross-test contamination unless explicitly cleared; this is a key coupling point we will remove in Sprint 14 Task 3.
