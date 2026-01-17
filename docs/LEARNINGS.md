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
