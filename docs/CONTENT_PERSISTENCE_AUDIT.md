Sprint 11 Working Audit — This document exists to support testing and content seeding and may be removed after Sprint 11.

## Purpose
Brief audit of where core game content and state live, how/when they are persisted, and which APIs read them. This guides testing and content updates without redefining the data model.

## Source of Truth Map

- Roles / representatives  
  - Origin: Seeded static content  
  - Stored in: DB table `roles`  
  - When persisted: Migration/seed (backend/sql/002_seed_minimal.sql)  
  - Read via: Opening/stance setup in code; not exposed directly via a dedicated API

- Issues & options  
  - Origin: Seeded static content from docs/ISSUE_OPTION_SPEC.md  
  - Stored in: DB table `issue_definitions`  
  - When persisted: Migration/seed (backend/sql/002_seed_minimal.sql)  
  - Read via: /advance Round 3 issue start (ROUND_3_START_ISSUE)

- Opening statements  
  - Origin: Seeded static content (prewritten variants)  
  - Stored in: DB table `opening_variants`; snapshotted into `game_state.round1.openings` at ROUND_1_READY  
  - When persisted: Seed SQL; snapshot into game_state during /advance ROUND_1_READY  
  - Read via: /advance ROUND_1_STEP uses game_state.round1.openings

- Round 2 private conversations  
  - Origin: Generated at runtime (human + FakeLLM)  
  - Stored in: game_state.round2 (active convo, partner, counters); transcript rows in `transcript_entries`  
  - When persisted: /advance ROUND_2_READY, CONVO_1_SELECTED, CONVO_1_MESSAGE/CONVO_2_MESSAGE, CONVO_2_SELECTED/SKIPPED, CONVO_END_EARLY, ROUND_2_WRAP_READY  
  - Read via: /games/{id} (state), /games/{id}/transcript

- Round 3 debate, voting, and resolution  
  - Origin: Hybrid (issue definitions seeded; debate/vote content generated at runtime)  
  - Stored in: game_state.round3 (active_issue, queues, votes); votes table `votes` for final per-issue records; transcript rows in `transcript_entries`  
  - When persisted: /advance ROUND_3_START_ISSUE, ISSUE_INTRO_CONTINUE, ISSUE_DEBATE_STEP/HUMAN_DEBATE_MESSAGE, CONTINUE in POSITION/PROPOSAL, HUMAN_VOTE/AI votes, ISSUE_RESOLUTION_CONTINUE  
  - Read via: /games/{id} (state), /games/{id}/transcript, /games/{id}/review (votes + filtered transcript)

- Transcript entries  
  - Origin: Generated at runtime (chair/human/AI lines)  
  - Stored in: DB table `transcript_entries` (append-only)  
  - When persisted: Throughout /advance routes (Round 1, 2, 3, wrap-up) via insert_transcript_entry  
  - Read via: GET /games/{id}/transcript; GET /games/{id}/review (filtered)

- Review payload  
  - Origin: Aggregated from persisted data  
  - Stored in: N/A (assembled at request time)  
  - When persisted: Votes already in `votes`; transcript already in `transcript_entries`  
  - Read via: GET /games/{id}/review (reads votes + filtered transcript)

## Persistence Invariants
- game_state is the authoritative snapshot for in-progress gameplay (cursors, queues, stances, active issues).
- transcript_entries is append-only; never updated/deleted.
- checkpoints log state snapshots at safe boundaries.
- Seeded content (roles, issue_definitions, opening_variants, japan_scripts, ima_excerpts) is loaded at migration/seed time; openings are snapshotted into game_state at ROUND_1_READY.
- Votes table records final per-issue votes; vote ordering is canonicalized before persistence.

## Open Questions / To Be Proven by Tests
- Confirm round-trip ordering of transcript entries remains stable under tie timestamps (created_at + metadata.index + id).
- Confirm game_state snapshots reflect all cursor/queue updates needed to resume mid-round without divergence.
- Confirm review endpoint always returns four vote rows after complete playthrough.
