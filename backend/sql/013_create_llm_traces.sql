BEGIN;

CREATE TABLE IF NOT EXISTS llm_traces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  role_id TEXT,
  status TEXT,
  provider TEXT NOT NULL,
  model TEXT,
  prompt_version TEXT,
  request_payload JSONB,
  response_payload JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;
