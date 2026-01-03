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
