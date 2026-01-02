# DATABASE_SCHEMA.md

**Target:** Supabase-hosted PostgreSQL

**Design goals**

* Support deterministic save/resume at turn boundaries
* Append-only transcripts (auditability)
* Fast reads for active game state
* JSONB for flexible, evolving structures (stances, cursors)
* Clean separation between *configuration*, *runtime state*, and *logs*

This schema is intentionally **conservative** for v1 and leaves clean extension points for future features (admin tools, analytics, instructor dashboards).

---

## 1. High-level table overview

### Core tables

1. `users` – human players (auth-light for v1)
2. `games` – one row per game session (high-level metadata)
3. `game_state` – authoritative mutable state snapshot (JSONB)
4. `transcript_entries` – append-only conversation log
5. `checkpoints` – save/resume anchors
6. `votes` – per-issue voting records

### Reference / config tables

7. `roles` – static role definitions (countries, NGOs, Japan)
8. `issue_definitions` – static issues and options (from PDFs)
9. `opening_variants` – prewritten opening statements + stance bundles

---

## 2. users

Represents a human player. OAuth fields can be added later.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  display_name TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Notes:

* Email is optional in v1
* No auth constraints enforced yet

---

## 3. roles

Static catalog of all roles in the game.

```sql
CREATE TABLE roles (
  id TEXT PRIMARY KEY,          -- e.g. 'BRA', 'CHN', 'AMAP', 'JPN'
  display_name TEXT NOT NULL,
  role_type TEXT NOT NULL CHECK (role_type IN ('country','ngo','chair')),
  voting_power INTEGER NOT NULL DEFAULT 0  -- 1 for countries, 0 otherwise
);
```

This table is seeded once and rarely changes.

---

## 4. issue_definitions

Canonical issue + option definitions extracted from `HgGame_GeneralInstructions.pdf`.

```sql
CREATE TABLE issue_definitions (
  id TEXT PRIMARY KEY,          -- e.g. 'ISSUE_1'
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  options JSONB NOT NULL        -- [{ optionId, label, description }]
);
```

Notes:

* Options are fixed-menu; no freeform text
* JSONB keeps structure compact and flexible

---

## 5. opening_variants

Prewritten Round 1 opening statements bundled with initial stance data.

```sql
CREATE TABLE opening_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id TEXT REFERENCES roles(id),
  opening_text TEXT NOT NULL,
  initial_stances JSONB NOT NULL,
  conversation_interests JSONB,   -- optional hints for Round 2
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

`initial_stances` example shape:

```json
{
  "ISSUE_1": { "preferred": "1.2", "firmness": 0.8 },
  "ISSUE_2": { "preferred": "2.1", "firmness": 0.6 }
}
```

---

## 6. games

One row per game session. Lightweight and query-friendly.

```sql
CREATE TABLE games (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  human_role_id TEXT REFERENCES roles(id),
  status TEXT NOT NULL,
  seed BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Notes:

* `status` mirrors the state machine (e.g. ROUND_2_CONVERSATION_ACTIVE)
* `seed` guarantees deterministic randomness

---

## 7. game_state

Authoritative mutable snapshot of the game.

```sql
CREATE TABLE game_state (
  game_id UUID PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
  state JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Contents of `state` include:

* round cursors
* speaker orders
* stance objects per role per issue
* active issue index
* debate round info

This is the **single source of truth** for resume.

---

## 8. transcript_entries

Append-only log of all messages (public and private).

```sql
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
```

Notes:

* **Never update or delete** rows in this table
* `metadata` may include:

  * turn counters
  * interruption flags
  * explicit intent markers

Indexes recommended:

```sql
CREATE INDEX idx_transcript_game ON transcript_entries(game_id);
CREATE INDEX idx_transcript_game_phase ON transcript_entries(game_id, phase);
```

---

## 9. checkpoints

Anchors for save/resume.

```sql
CREATE TABLE checkpoints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  transcript_entry_id UUID REFERENCES transcript_entries(id),
  status TEXT NOT NULL,
  state_snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Notes:

* `state_snapshot` allows fast rollback
* Checkpoints are created only at safe boundaries

---

## 10. votes

Stores final vote records per issue.

```sql
CREATE TABLE votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  issue_id TEXT NOT NULL,
  proposal_option_id TEXT NOT NULL,
  votes_by_country JSONB NOT NULL,
  passed BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

`votes_by_country` example:

```json
{
  "BRA": "YES",
  "CHN": "NO",
  "USA": "YES",
  "EU": "YES",
  "CAN": "YES",
  "TZA": "YES"
}
```

---

## 11. Japan procedural script lines (templated, keyed)

```sql
CREATE TABLE japan_scripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  script_key TEXT NOT NULL UNIQUE,              -- e.g. 'R2_INTERRUPT', 'ISSUE_INTRO', 'VOTE_RESULT_PASS'
  state TEXT,                                   -- optional: STATE_MACHINE status where used
  template TEXT NOT NULL,                        -- the actual line (can include {placeholders})
  metadata JSONB,                                -- optional: { "placeholders": ["speaker","issue_id"] }
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Sample starter set:
```sql
INSERT INTO japan_scripts (script_key, state, template) VALUES
('R1_OPEN', 'ROUND_1_OPENING_STATEMENTS', 'The Chair calls the meeting to order. We will begin opening statements.'),
('R1_CALL_SPEAKER', 'ROUND_1_OPENING_STATEMENTS', 'I recognize {speaker}.'),
('R2_INTERRUPT', 'ROUND_2_CONVERSATION_ACTIVE', 'The Chair interrupts. Please move to final statements.'),
('ISSUE_INTRO', 'ISSUE_INTRO', 'We now consider Issue {issue_id}: {issue_title}. The options are: {options_list}.'),
('PROPOSAL', 'ISSUE_PROPOSAL_SELECTION', 'The Chair proposes option {option_id} for adoption.'),
('VOTE_RESULT_PASS', 'ISSUE_VOTE', 'The proposal is adopted by unanimous consent.'),
('VOTE_RESULT_FAIL', 'ISSUE_VOTE', 'The proposal is not adopted (unanimity was not achieved).');
```

---

## 12. Approved IMA excerpts (the ONLY allowed IMA text source)

```sql
CREATE TABLE ima_excerpts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  excerpt_key TEXT NOT NULL UNIQUE,              -- e.g. 'IMA_ATMOS_TRANSPORT', 'IMA_HEALTH_IMPACTS'
  content TEXT NOT NULL,                         -- the approved excerpt text
  source_ref TEXT,                               -- optional: "IMA p.12", section name, etc.
  tags TEXT[],                                   -- optional: ARRAY['round2','round3','atmospheric']
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```


---

## 11. Performance & cost considerations (Supabase free tier)

* Game state reads: **1 row per resume**
* Transcript writes: append-only, cheap
* JSONB keeps schema migrations minimal
* All heavy AI data stays **out of DB** (only outputs stored)

This comfortably fits free-tier limits for:

* development
* testing
* demos

---

## 12. Intentional omissions (V1)

* Instructor/admin tables
* Analytics tables
* Full audit/version history of `game_state`
* Role-based access controls

These can be layered later without breaking compatibility.

##
