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
