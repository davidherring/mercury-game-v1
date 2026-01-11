Sprint 11 Working Note — Content Persistence Gaps

## Current Content Sources
- Seed SQL: `backend/sql/002_seed_minimal.sql`
- Tables with narrative/game content: `roles`, `issue_definitions`, `opening_variants`, `japan_scripts`, `ima_excerpts`

## Placeholder Content Audit
- `roles`: ids and display_name present; no rich public/private descriptions.
- `issue_definitions`: option text present but long/short descriptions may be terse; agent_notes exist but may need authoritative language.
- `opening_variants`: opening_text uses placeholders; initial_stances minimal/null-heavy.
- `japan_scripts`: small starter set of generic templates only.
- `ima_excerpts`: seeded keys exist; content likely minimal and not curated per issue/round tags.

## Persistence Readiness for Rich Content
- Roles/issues/openings/scripts/IMA are fully DB-driven via seed SQL; openings are snapshotted into `game_state.round1.openings` at `ROUND_1_READY`.
- Updating seeds does not retroactively change existing games; snapshots and running games keep prior values.
- Round 2/3 runtime content (messages, votes) persists to `transcript_entries` / `votes`; state cursors live in `game_state`.

## Recommendations (Smallest Next Steps)
- Enrich seed SQL rows in place; use `INSERT ... ON CONFLICT DO UPDATE` patterns already present to allow reseeding.
- Populate `opening_variants.opening_text` with real statements and fuller `initial_stances`.
- Expand `japan_scripts` with complete Round 1/2/3 procedural lines.
- Curate `ima_excerpts` with tagged, approved passages and ensure keys match prompt usage.
- For issues/options, review `agent_notes`/descriptions against source PDFs to replace placeholder phrasing.
- When adding new content, prefer a new seed file or clearly versioned block if large edits are needed.

## No-Change Findings
- Current tests confirm seed → state snapshot → transcript → review persistence; no schema changes required.
