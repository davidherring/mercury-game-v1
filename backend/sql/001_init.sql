-- Initial schema for Mercury Game (Supabase Postgres)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

BEGIN;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  display_name TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roles (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  role_type TEXT NOT NULL CHECK (role_type IN ('country','ngo','chair')),
  voting_power INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE issue_definitions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  options JSONB NOT NULL
);

CREATE TABLE opening_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id TEXT REFERENCES roles(id),
  opening_text TEXT NOT NULL,
  initial_stances JSONB NOT NULL,
  conversation_interests JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE games (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  human_role_id TEXT REFERENCES roles(id),
  status TEXT NOT NULL,
  seed BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE game_state (
  game_id UUID PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
  state JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE transcript_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  role_id TEXT REFERENCES roles(id),
  phase TEXT NOT NULL,
  round INTEGER,
  issue_id TEXT,
  visible_to_human BOOLEAN NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_transcript_game ON transcript_entries(game_id);
CREATE INDEX idx_transcript_game_phase ON transcript_entries(game_id, phase);

CREATE TABLE checkpoints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  transcript_entry_id UUID REFERENCES transcript_entries(id),
  status TEXT NOT NULL,
  state_snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  issue_id TEXT NOT NULL,
  proposal_option_id TEXT NOT NULL,
  votes_by_country JSONB NOT NULL,
  passed BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE japan_scripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  script_key TEXT NOT NULL UNIQUE,
  state TEXT,
  template TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ima_excerpts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  excerpt_key TEXT NOT NULL UNIQUE,
  content TEXT NOT NULL,
  source_ref TEXT,
  tags TEXT[],
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;
