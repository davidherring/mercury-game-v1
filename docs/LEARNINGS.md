# Learnings Log

Purpose: capture short, factual lessons learned during implementation and testing. This is a memo log, not a spec. Use it to record decisions, pitfalls, and stable patterns with concrete file references.

Template for new entries:

## Sprint XX — <short title>
- What changed:
- What worked:
- What failed:
- Where to look (files/functions):

---

## Sprint 17 — Prompt Grounding from DB (Round 2)
- Round 2 grounding needs state enrichment or rehydration; state enrichment was used.
- `game_state.round1.openings` should persist the full opening packet fields used in Round 2 (`initial_stances`, `conversation_interests`).
- Round 2 context should be structured and bounded (compact issues/options; transcript tail limit). See `backend/prompt_builder.py` and `backend/main.py`.
- Behavior instructions work best as an editable text file loaded by the prompt builder and injected before the Context JSON. See `backend/prompts/round2_behavior_instructions_v1.txt` and `backend/prompt_builder.py`.

- SQLAlchemy autobegin gotcha: read queries can trigger autobegin; starting a new `session.begin()` later can raise "A transaction is already begun". Fix by running grounding reads inside a bounded `async with session.begin()` before later begin blocks. See `backend/main.py`.

- `request_payload.context.transcript_tail` is a request-time snapshot; it typically ends with the human message, not the AI response. Tests should assert semantics accordingly. See `tests/test_llm_traces.py`.

- Avoid asserting FakeLLM response exact strings in ordering tests; prefer ordering/metadata assertions (phase, `metadata.convo`, `role_id` sequencing). See `tests/test_round2_convo2_conclusion_order.py`.

- Pytest async "event loop is closed" pattern: `async for session in get_session(): ... break` can leak generator cleanup. Fix by always `aclose()` the async generator via a helper (local `_with_session`). See `tests/test_round3_kickoff_all_issues.py` and `tests/test_round3_issue1_full_run.py`.
- Avoid global `engine.dispose()` teardown during tests when it re-triggers loop/pool issues (Sprint 16B context).

- Pytest config warning: remove unsupported `asyncio_default_fixture_loop_scope` when the installed pytest-asyncio does not recognize it. See `pytest.ini`.

---

## Sprint 18 — Round 3 Speech-1 OpenAI Gating + Tracing
- Round 3 debate Speech 1 (`ISSUE_DEBATE_ROUND_1`) for non-chair scheduled speakers can use OpenAI when enabled; Speech 2 stays FakeLLM. See `backend/main.py`.
- Japan/Chair remains scripted/deterministic and never uses OpenAI.
- Gating/vars: `LLM_PROVIDER=openai`, `OPENAI_API_KEY=...`, and `OPENAI_ROUND3_DEBATE_SPEECHES=1` are required for real OpenAI calls. Default behavior remains FakeLLM/offline.
- Failure behavior (Speech 1 OpenAI): write `llm_traces` with error metadata, return 502, no transcript write, no state advance. See `backend/main.py`.
- Tracing: both FakeLLM and OpenAI debate speeches write `llm_traces` with structured `request_payload.context` (active issue/options, speech slot, speaker, bounded debate transcript tail, opening summary, stance snapshot). See `backend/prompt_builder.py`.
- Tests: offline-only stubs cover Speech‑1 OpenAI success and failure in `tests/test_round3_openai_speech1_tracing.py` (no network calls).

### Typing/Interfaces (Round 3 OpenAI integration)
- Use typed request objects (LLMRequest) rather than ad-hoc dicts when calling providers to keep `status`, `prompt_version`, and `request_payload` consistent. See `backend/main.py` and `backend/llm_provider.py`.
- Error payloads should be JSON-shaped types (`Dict[str, Any]` or a narrow TypedDict), not `Dict[str, Dict[str, str]]`, because we attach string fields like `error_type`/`error_message`.
- Prefer attribute/required-field access over `.get()` for required fields (e.g., `status`) to keep trace insertion type-safe.
- Keep `request_payload` structured and JSON-serializable; annotate with `Dict[str, Any]` (or `Mapping[str, Any]`) to reflect real usage.

### Test Hygiene: AsyncSession cleanup (Pytest warnings)
- Symptom: `PytestUnraisableExceptionWarning` with `AsyncSession.close` and “Event loop is closed”.
- Common trigger: `async for session in get_session(): ... break` (single-use generator, cleanup deferred to GC).
- Preferred: use `async with` session fixtures or sessionmaker directly when available.
- If consuming `get_session()` directly, explicitly close the generator:
  - `agen = get_session(); session = await agen.__anext__(); ... finally: await agen.aclose()`
- Rationale: guarantees session close while the event loop is still alive.
- Checklist: avoid breaking out of async generators without `agen.aclose()`.
- Quick scan: `grep -R "async for session in get_session" -n tests`.
- If warnings appear, reproduce with a small DB-heavy subset before running the full suite.
- Sprint 18: updated targeted tests to close the generator; warnings stopped in the subset run.

---

## Sprint 19 — Stance Updates & Proposal/Vote Sanity
- **Stance defaults must be merge-only.** Normalizing or initializing `state["stances"]` must preserve existing acceptance maps and `None` values; destructive re-init breaks negotiation semantics and downstream proposal/vote logic.
- **Apply stance shifts once per logical message, not per transcript row.** In Round 2, shifting once per human message avoids double-counting when AI replies are generated in the same event.
- **Bounded, deterministic stance deltas are sufficient to make negotiation consequential.** Small, clamped, auditable shifts (without NLP or helper agents) were enough to drive meaningful proposal selection and unanimous-vote outcomes.
- **Seed authoritative stances at Round 1.** Applying `opening_variants.initial_stances` into `state["stances"]` ensures proposals and votes are meaningful from the first issue onward.

---

## Sprint 21 — Environment Mode Contract (LLM Provider)
- Added `MERCURY_ENV` (`test | dev | prod`) as the authoritative environment mode in `backend/config.py`.
- Provider resolution forces `FakeLLM` when `MERCURY_ENV=test`, regardless of other provider env vars. See `backend/llm_provider.py`.
- `MERCURY_ENV` is read once from settings and stored on `app.state` for reuse.
- OpenAI network calls are hard-blocked in test mode with a fast-fail guard in `OpenAIProvider.generate`. See `backend/llm_provider.py`.
- Pytest runs set `MERCURY_ENV=test` and skip loading runtime dotenv files; settings ignore env_file when in test mode. See `tests/conftest.py` and `backend/config.py`.
- Test DB config is explicit: export `SUPABASE_DATABASE_URL` or provide a dedicated test env file via `MERCURY_ENV_FILE`/`ENV_FILE` (e.g., `apps/api/.env.test`). Runtime dotenv files are never auto-loaded in tests.
- OpenAI integration tests are opt-in via `RUN_OPENAI_INTEGRATION_TESTS=1` and require `MERCURY_ENV=dev` (or prod) plus a valid `OPENAI_API_KEY`.


## Sprint 22 - Test Hygiene: AsyncSession teardown warnings (intermittent)
- Symptom: Occasional `PytestUnraisableExceptionWarning` referencing `AsyncSession.close` and “Event loop is closed” when running the full pytest suite.
- Observation: The warning is intermittent and does not reproduce reliably when running individual tests.
- Attempted fix: Replacing `async for session in get_session()` with explicit `agen.__anext__()` / `agen.aclose()` patterns in select tests.
- Outcome: While the warning disappeared, this change destabilized other end-to-end tests (connection closed mid-operation).
- Decision: Prefer a consistently green test suite over eliminating this intermittent warning.
- Guidance: Avoid manually closing `get_session()` generators in tests unless the session lifecycle is fully isolated; premature teardown can interfere with pooled asyncpg connections.
