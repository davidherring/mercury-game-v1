# AGENTS.md — Mercury Game Rebuild (V1)

This file defines **non‑negotiable rules** for all AI coding agents (Codex, ChatGPT, local agents) working on this repository.

Its purpose is to:
* Preserve the integrity of the game design
* Prevent silent rule drift or “helpful” simplifications
* Keep AI assistance aligned with a deterministic, debuggable system

If instructions here conflict with comments, tests, or ad‑hoc prompts, **this file wins**.

---

## 1. Global invariants (do not violate)

* **Game rules are fixed** unless explicitly changed by the human author.
* **No agent may invent new issues, options, voting rules, or roles.**
* **Unanimous voting by the six countries is required** for adoption.
* **NGOs and Japan never vote.**
* **Issues are independent**; a failed issue is never revisited.
* **Round structure is fixed**: Round 1 → Round 2 → Round 3 → Review.


Any change to these requires an explicit instruction from the human.

---

## 2. Architectural principles

### 2.1 State machine–driven system

* All gameplay must follow the **State Machine Spec (V1)** exactly.
* Frontend components **reflect state**; they do not decide logic.
* Backend transitions must be deterministic and auditable.

Do not introduce hidden transitions, implicit shortcuts, or UI‑driven logic.

---

### 2.2 Persistence rules

* `game_state` is the **single authoritative snapshot**.
* `transcript_entries` is **append‑only** and immutable.
* `checkpoints` are created **only at safe turn boundaries**.
* Resume must always return to the **last completed interaction**, never mid‑turn.

Never:
* mutate or delete transcript rows
* resume inside an incomplete AI or human message

---
### 2.2.1 Partial AI generation / failure handling (V1)

If an AI message is streaming and fails mid-generation:
  * Do not write partial text to transcript_entries.
  * Resume returns to the last completed checkpoint.
  * The next action is to re-attempt generation for the same turn using the same stored prompt inputs (role_id, state snapshot, transcript pointer).
  * Emit an error log event using the standard logging protocol (see 7.2).

---

## 3. AI behavior constraints (gameplay)

### 3.1 Role behavior

AI representatives:
* May **withhold private information**
* May **bluff or misrepresent strategically**
* May offer **conditional support or cross‑issue trades**
* Must **defend their interests** and red lines
* Must **not automatically agree** for the sake of consensus
* Private role instructions must never be revealed:
  * No direct quotes.
  * No paraphrases that expose specific hidden facts, red lines, or confidential rationale as “instructions.”
  * Roles may express positions and motivations naturally, but must not attribute them to secret documents or disclose hidden constraints explicitly.

---

### 3.2 Information boundaries

* Round 2 private conversations are **private forever**:
  * visible to the human player
  * not visible to other AI roles except the agents who were directly involved in the conversations
* AI roles must not reference private conversations they were not part of.
* The IMA Assessment may be referenced **only through approved excerpts** listed in the ima_excerpts DB table.

---

### 3.3 Japan (Chair) behavior

Japan:
* Moderates only
* Does not persuade substantively
* Does not reveal preferences
* Enforces turn order, limits, interruptions, and voting

Japan’s language should be:
* procedural
* neutral
* consistent

Japan intervenes only to enforce structure:
* Announces state transitions (round changes, issue intro, proposal, vote, result).
* Enforces speaking order and “speak or skip” limits.
* Does not intervene for rhetoric quality, persuasion, or substance.
* Round 3: Japan does not “timeout” speakers; the UI enforces turn completion.
* If an AI response fails/returns empty, Japan emits the appropriate procedural line from the Japan script library and the system treats the turn as SKIPPED.
  * Japan’s procedural lines live in the DB table. AGENTS.md only defines *when* Japan speaks, not the full text.
  * A skipped turn advances the cursor and counts as that role’s opportunity to speak for that slot.


---

## 4. AI call placement & performance rules

### 4.1 Round 1

* **No live model calls**
* Use prewritten opening variants only

---

### 4.1.1 Opening variant selection (deterministic)

Round 1 openings are selected deterministically from the DB:
* Source of truth: `opening_variants` rows filtered by `role_id`.
* Selection: use a seeded RNG derived from `game.seed` to pick one row per role.
* To make the selection stable across DB ordering changes, sort candidates by a stable key (e.g., `opening_variants.id ASC`) before indexing.
* Persist both `variant_id` and `opening_text` into `game_state.round1.openings` at `ROUND_1_SETUP`.
* No live model calls for Round 1.

---

### 4.2 Round 2

* Only the **active conversation partner** may trigger a model call.
* Maximum conversation length:
  * up to **5 messages each**
  * Japan interrupts
  * **1 final message each**
* The human may end the conversation early.

Optional:
* A helper agent may run **asynchronously** to update stance deltas.
* The UI must **never wait** on helper agents.

---

### 4.3 Round 3

* Only the next scheduled speaker triggers a model call.
* No bulk “query all agents” calls at the end of debate.
* Stances should be updated incrementally.
* Tie-breaking for proposals uses ISSUE_OPTION_SPEC: if support ties, lowest option_id wins.

---

### 4.4 Helper agent contract (optional)

* If a helper agent is used for stance deltas, it must follow this contract:

* Input:
  * role_id (speaker)
  * round (2 or 3)
  * issue_id (if round 3)
  * last_committed_message (text)
  * current_stance_snapshot (for that role + relevant issue(s))

* Output (JSON):
  * changed: boolean
  * deltas: { issue_id: { acceptance: { option_id: deltaFloat }, firmness: deltaFloat } }
  * reasons: [short strings]

* Rules:
  * Must never propose changes to null acceptances.
  * If helper output is missing/late/invalid, ignore it; gameplay must proceed without waiting.
  * Helper results must be applied only at safe boundaries (after a message is committed), and logged.


---

## 5. Stance management rules

* Each role has a structured stance per issue:
  * preferred option
  * firmness
  * acceptable fallbacks
  * conditions

* Stances may update:
  * after Round 2 conversations
  * after concessions in Round 3
  * after issue votes (affecting future issues)

* Stance updates may be:
  * rule‑based (v1 default)
  * helper‑agent assisted (optional)

* Unless a helper-agent result is explicitly applied, stance updates are rule-based and bounded:
  * Hard rule: `acceptance[option] = null` is immutable and must never change.
  * Soft bounds: non-null acceptance stays within [0.0, 1.0].
  * Default behavior:
    * Round 2 (private): after each committed message, only the two participants may have stance changes, and only for issues explicitly discussed in that message.
    * Round 3 (public): after each committed speech, only the speaker’s stance may shift, and only for the active issue.
  * Allowed shifts:
    * Small adjustments only (recommended max delta per message: ±0.10 per option; firmness ±0.05).
  * No formulas required; prefer explicit, logged “reason” strings when stances change.

Do **not** require stance logic to be perfect for v1.

---

## 6. Frontend rules

* Frontend components must be **purely state‑driven**.
* UI may:
  * display speaker order
  * allow turn skipping
  * show issue and vote modals
* UI must **not**:
  * determine vote outcomes
  * alter stance logic
  * bypass backend state transitions

---

## 7. Coding style & safety

* Prefer explicit over clever.
* Prefer readability over abstraction.
* Avoid premature optimization.
* Log state transitions clearly.

If unsure, choose the approach that:

1. preserves determinism
2. is easier to debug
3. aligns with the state machine

---

### 7.1 Required transition logging (V1)

Every state transition must log:
  * game_id
  * from_status → to_status
  * event_name
  * actor_role_id (or SYSTEM)
  * checkpoint_id created (if any)

Prefer structured JSON logs.

Destination: backend application logs (stdout) as structured JSON. (Persisting logs to DB is optional and out of scope for V1 unless explicitly added.)
  * Example: { "type":"transition", "game_id":"...", "from":"ROUND_2_SETUP", "to":"ROUND_2_SELECT_CONVO_1", "event":"ROUND_2_READY", "actor":"SYSTEM", "checkpoint_id":"cp_..." }


---
### 7.2 Required error logging (V1)

Required fields:
  * type: "error"
  * game_id
  * status
  * actor_role_id (or SYSTEM)
  * error_code (e.g., AI_EMPTY, AI_STREAM_FAIL, AI_TIMEOUT)
  * attempt (int)
  * checkpoint_id (the last safe checkpoint you rolled back to)
  * optional: round, issue_id

---

## 8. What not to build (V1)

* Full AI–AI negotiation simulation
* Instructor/admin dashboards
* OAuth enforcement
* Real‑time collaboration
* Complex analytics

These are explicitly **out of scope** until the core game works.

---

## 9. Final rule

If an AI agent is uncertain about how to proceed:

* **Stop and ask the human.**
* Do not invent mechanics, rules, or shortcuts.

This project values correctness and clarity over speed.
