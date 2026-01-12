## Mercury Game Backend (Sprint 0)

This sprint scaffolds a FastAPI backend wired to Supabase Postgres with deterministic game setup for Round 1.

### Prerequisites
- Python 3.10+
- Postgres database (Supabase connection string recommended)

### Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set environment variables (create a `.env`):
```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
APP_ENV=local
```

Apply the SQL:
```bash
psql "$DATABASE_URL" -f backend/sql/001_init.sql
psql "$DATABASE_URL" -f backend/sql/002_seed_minimal.sql
psql "$DATABASE_URL" -f backend/sql/003_seed_opening_variants_v1.sql
```
Alternatively, you can paste the contents of `backend/sql/003_seed_opening_variants_v1.sql` into the Supabase SQL editor. Openings are snapshotted into `game_state` at `ROUND_1_READY`, so start a new game after reseeding to see updated text.

Run the API:
```bash
uvicorn backend.main:app --reload
```

### Database seeding and updates (Supabase)
- The app uses an async SQLAlchemy DSN like `postgresql+asyncpg://...`, but `psql` expects a standard Postgres URL like `postgresql://USER:PASSWORD@HOST:5432/postgres`.
- Apply seed/update files from terminal (idempotent upserts; safe to rerun). Run in numeric order: 001_init, 002_seed_minimal, 003_seed_opening_variants_v1, 004+, etc.
```bash
psql "postgresql://USER:PASSWORD@HOST:5432/postgres" -f backend/sql/<file>.sql
```
- Opening variants are snapshotted into `game_state` at `ROUND_1_READY`; start a new game after reseeding to see updated openings.

Env files:
- Default backend env is loaded from `apps/api/.env` (or `ENV_FILE`/`MERCURY_ENV_FILE` if set). Ensure `SUPABASE_DATABASE_URL` is present there.
- Example from repo root:
```bash
ENV_FILE=apps/api/.env uvicorn backend.main:app --reload
```

### API quickstart
Create a game:
```bash
curl -X POST http://localhost:8000/games \
  -H "Content-Type: application/json" \
  -d '{}'
```

Confirm a role:
```bash
curl -X POST http://localhost:8000/games/<game_id>/advance \
  -H "Content-Type: application/json" \
  -d '{ "event": "ROLE_CONFIRMED", "payload": { "human_role_id": "USA" } }'
```

Move to Round 1 setup and openings:
```bash
# Generate Round 1 speaker order and openings
curl -X POST http://localhost:8000/games/<game_id>/advance \
  -H "Content-Type: application/json" \
  -d '{ "event": "ROUND_1_READY", "payload": {} }'

# Step through each opening statement (call repeatedly until cursor completes)
curl -X POST http://localhost:8000/games/<game_id>/advance \
  -H "Content-Type: application/json" \
  -d '{ "event": "ROUND_1_STEP", "payload": {} }'
```

Health check:
```bash
curl http://localhost:8000/health
```

## Testing
Most tests are **DB-backed integration tests** (FastAPI + async Postgres). Run them locally with a working `SUPABASE_DATABASE_URL` (or equivalent Postgres DSN) in your environment.

**Full suite**
```bash
python -m pytest -q
Single file

python -m pytest -q tests/test_canaries_round3.py
Single test (fast iteration)

python -m pytest -q -x tests/test_full_game_playthrough.py::test_full_game_playthrough
Handy flags

Stop on first failure:
python -m pytest -q -x
Show print output (debugging):

python -m pytest -q -s -x tests/test_full_game_playthrough.py::test_full_game_playthrough
Re-run only the last failures:

python -m pytest -q --lf
Deterministic full playthrough (backend-only)
Uses FakeLLM to run a deterministic end-to-end playthrough:

python -m pytest -q -x tests/test_full_game_playthrough.py::test_full_game_playthrough
Canary tests (quick regression tripwires)
Fast tests intended to fail if key invariants drift (vote sequencing/resolution semantics, checkpoints tracking transcripted actions):

python -m pytest -q -x tests/test_canaries_round3.py
Note on AI code generation environments
Some AI code generation environments cannot reach your database and therefore cannot run DB-backed tests. Treat any “tests failed due to DB connectivity” notes as non-authoritative unless the exact pytest command output is included. The source of truth for test status is the local pytest output shown above.

### LLM Providers (Round 2)
- Default: FakeLLM (deterministic, no network). This is always used unless explicitly enabled.
- Enable OpenAI locally (Round 2 private conversations only):
  - `LLM_PROVIDER=openai`
  - `OPENAI_API_KEY=...`
  - `OPENAI_MODEL=...` (optional; current default is `gpt-5-nano`)
- Tracing: every Round 2 LLM call writes `llm_traces` with `provider`, `model`, `prompt_version` (`r2_convo_v1`), and request/response payloads. Example query:
  - `SELECT provider, model, prompt_version, request_payload, response_payload FROM llm_traces WHERE game_id = '<id>';`
- CI/tests: run with FakeLLM only. Do not set `OPENAI_API_KEY` or `LLM_PROVIDER=openai` in CI. OpenAI behavior is covered via stubs/monkeypatch; no network calls occur in tests.

### Review (end-of-game payload)
- Endpoint: `GET /games/{game_id}/review`
- Returns:
  - `transcript`: chronological transcript entries for the whole game; Round 2 entries are included only when `visible_to_human=true`.
  - `votes`: one row per Round 3 issue from the `votes` table, including `proposal_option_id`, `votes_by_country`, and `passed`.
- Example:
```bash
curl http://localhost:8000/games/<GAME_ID>/review
```
- Round 3 resolution events (UI/testing note):
  - When `status == ISSUE_RESOLUTION`:
    - `ISSUE_DEBATE_STEP` is allowed and idempotent (ensures the resolution transcript exists; does not advance).
    - `ISSUE_RESOLUTION_CONTINUE` advances to `ROUND_3_SETUP` (if issues remain) or `REVIEW` (when all issues are closed).

### LLM providers (current: FakeLLM; future: OpenAI)
- Current behavior: all LLM calls use FakeLLM via the provider boundary (`backend/llm_provider.py:get_llm_provider`); prompts are built in `backend/prompt_builder.py`; traces are written to `llm_traces` with provider/model/prompt_version (currently “fake”/“fake”/“r2_convo_v1”).
- Sprint 13 plan: add a feature flag/env selector (e.g., `LLM_PROVIDER=fake|openai`) and OpenAI credentials (e.g., `OPENAI_API_KEY`) to opt into OpenAI in dev; CI remains on FakeLLM for determinism.
- Traces will continue to capture provider/model/prompt_version; OpenAI calls will record provider=`openai`, model=<chosen model>, with the same prompt_version and request/response payload shape.
