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
```

Run the API:
```bash
uvicorn backend.main:app --reload
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
