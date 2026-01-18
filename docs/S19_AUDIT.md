# Sprint 19 Audit — Proposal/Votes/Stances (current behavior)

## 1) Proposal selection
- **Observed behavior**
  - In `ISSUE_PROPOSAL_SELECTION`, Japan proposes the option with the highest computed support among countries.
  - Support is the sum of `acceptance` values across `COUNTRIES` for each option; `null`/missing acceptance is treated as `0.0`.
  - Tie-break is by lowest `option_id` (stable sort on `(-support, option_id)`).
  - If no support data is present, it picks the first option in the issue options list.
  - A Chair transcript entry is written with the `PROPOSAL` Japan script.
- **Where implemented**
  - Support calculation: `_proposal_support` in `backend/main.py` (sums `state["stances"][country][issue_id].acceptance[option_id]`).
  - Proposal selection and transcript write: `advance_game` in `backend/main.py`, `current_status == "ISSUE_PROPOSAL_SELECTION"`.
  - Option list ordering: `ROUND_3_START_ISSUE` sorts options by `option_id` in `backend/main.py`.
  - Chair script: `fetch_japan_script(session, "PROPOSAL")` in `backend/main.py`.
- **Determinism / tie-break notes**
  - Deterministic: support uses stable country list (`COUNTRIES`) and options are sorted by `option_id`.
  - Tie-break matches ISSUE_OPTION_SPEC guidance (lowest `option_id` wins).
- **Gaps vs Sprint 19 requirements**
  - None found relative to the documented deterministic rule; behavior matches spec in `docs/STATE_MACHINE.md` (highest support among countries, tie-break by option id).

## 2) Vote capture + counting
- **Observed behavior**
  - Vote order is `VOTE_ORDER`, which equals `COUNTRIES` (6 countries only).
  - If the current voter is the human role, the API requires `HUMAN_VOTE` with `"YES"` or `"NO"`.
  - AI country votes are derived from stance: `YES` if `acceptance[proposed_option] >= 0.7`, else `NO` (missing/`null` treated as `0.0`).
  - Each vote is appended to transcript entries and stored in `state["round3"]["active_issue"]["votes"]`.
  - When all 6 country votes are recorded, a row is inserted into the `votes` table with `votes_by_country` and `passed`.
  - Unanimity is enforced when computing `passed`: all 6 votes must be `"YES"`.
- **Where implemented**
  - Vote sequence and capture: `advance_game` in `backend/main.py`, `current_status == "ISSUE_VOTE"`.
  - Unanimity check and vote record insert: `backend/main.py` (`passed = len(votes) == len(COUNTRIES) and all(v == "YES" ...)`).
  - Vote order source: `VOTE_ORDER` in `backend/state.py` (equal to `COUNTRIES`).
  - Votes table schema: `docs/DATABASE_SCHEMA.md` (table `votes`).
- **Determinism / tie-break notes**
  - Deterministic: vote order is fixed (`COUNTRIES`), vote threshold is fixed (`>= 0.7`).
  - NGOs and Japan are excluded in code by not appearing in `VOTE_ORDER`.
- **Gaps vs Sprint 19 requirements**
  - No explicit additional guard beyond `VOTE_ORDER` to prevent NGO/Chair voting (but they are not in `VOTE_ORDER`).

## 3) Stance data model
- **Observed behavior**
  - Stances live in `game_state.state["stances"]` (JSONB).
  - Base stances are initialized with empty `acceptance` maps and default `firmness` via `ensure_default_stances`.
  - Opening variants include `initial_stances` in `opening_variants` (seeded), and these are stored in `game_state.round1.openings` but not applied to `state["stances"]` in the current code path.
  - Vote logic reads stances from `state["stances"][role][issue_id].acceptance`.
- **Where implemented**
  - Stance initialization: `ensure_default_stances` in `backend/state.py` (called in `advance_game` ROLE_CONFIRMED and game creation).
  - Stance usage in proposal support: `_proposal_support` in `backend/main.py`.
  - Stance usage in votes: `advance_game` `ISSUE_VOTE` branch in `backend/main.py`.
  - Stance shape reference: `docs/GAME_STATE.md` (`stances` section).
  - Opening variants stance bundles: `opening_variants.initial_stances` in `docs/DATABASE_SCHEMA.md`.
- **Determinism / tie-break notes**
  - Deterministic usage: stances are read only; vote thresholds are fixed.
- **Gaps vs Sprint 19 requirements**
  - No enforcement found in code for “null acceptance is immutable”; `null` is treated as `0.0` in support/vote calculations.
  - No code found that applies `opening_variants.initial_stances` into `state["stances"]`; only stored in `round1.openings`.

---

Searches run (high-signal):
- `backend/main.py`: `ISSUE_PROPOSAL_SELECTION`, `ISSUE_VOTE`, `_proposal_support`, `VOTE_ORDER`, `acceptance`.
- `backend/state.py`: `COUNTRIES`, `VOTE_ORDER`, `ensure_default_stances`.
- `docs/STATE_MACHINE.md`: proposal/vote spec (`ISSUE_PROPOSAL_SELECTION`, `ISSUE_VOTE`).
- `docs/GAME_STATE.md`: `stances` shape and voting rule.
- `docs/DATABASE_SCHEMA.md`: `votes` table and `opening_variants.initial_stances`.
