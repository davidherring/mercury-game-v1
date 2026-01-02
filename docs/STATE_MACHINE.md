# State Machine Spec (V1)

**Purpose:** Define a deterministic, save/resume-safe state machine for the Mercury negotiation simulation (web version). This document is the canonical source of game flow rules.

**V1 Goals**

* Deterministic progression through Round 1 → Round 2 → Round 3 → Review
* Fixed issue options (no freeform policy text)
* Unanimous voting by 6 countries; NGOs and Japan do not vote
* Persistent, append-only transcript logging
* Save/resume at end of last completed interaction (turn boundary)
* No live AI calls required for Round 1

**Non-goals (V1)**

* Full AI–AI private negotiation simulation coverage
* Instructor/admin class management
* OAuth requirement (can be added later)
* Perfect realism of real-world negotiation timing/structure

---

## 1) Entities and Roles

### Voting Countries (6)

* Brazil, Canada, China, European Union, Tanzania, United States
* Each has **one equal vote**

### Non-voting Roles

* NGOs (3): AMAP, MFF, WCPA
* Japan: Chair/Moderator

### Human Player

* Selects one of the 9 non-chair roles (country or NGO)
* All other roles are AI-controlled

---

## 2) Canonical Game Timeline

### Top-level phases

1. **BOOT** (new game or resume)
2. **ROLE_SELECTION**
3. **ROUND_1_OPENING_STATEMENTS**
4. **ROUND_2_PRIVATE_NEGOTIATIONS**
5. **ROUND_3_PUBLIC_DEBATE_AND_VOTING** (issues processed sequentially)
6. **REVIEW**

Each phase is a deterministic state with allowed events and side effects.

---

## 3) Core State Shape (Conceptual)

> Implementation can use Postgres+JSONB or Mongo; this spec assumes a single authoritative `game_state` object persisted and checkpointed.

### Required state fields

* `game_id`
* `created_at`, `updated_at`
* `status`: one of the phase/state ids defined below
* `human_role_id`
* `roles[]`: all roles in the session (10 total including chair)

  * includes: id, type (country|ngo|chair), displayName
* `round1`

  * `speaker_order`: ordered list (countries first group, NGOs after), randomized with constraints
  * `openings`: map roleId → openingVariantId + openingText
* `round2`

  * `human_conversations`: ordered list of conversations (1 required, 2nd optional)
  * `ai_ai_background_outcomes`: optional list of stance updates applied (v1 may be rules-only)
* `round3`

  * `issues[]`: 4 issues, each with options
  * `active_issue_index`
  * `active_issue_state` (debate round, speaker cursor, etc.)
* `stances`

  * per-role stance for each issue (preferred option, acceptability, conditions)
  * updated incrementally
* `votes[]`

  * per issue: proposalOptionId, per-country votes, result
* `checkpoints[]`

  * list of checkpoint ids with pointers to transcript_entry_id and game_state snapshot metadata

### Determinism requirements

* All randomness derived from stored `seed` or stored results at decision time.
* Speaker orders, opening variants, and any random selections must be persisted immediately.

---

## 4) Save / Resume Rules

### Save boundary

* The system saves at the **end of each completed interaction** (turn boundary).
* If a message is being generated (e.g., AI response streaming) and the session ends, resume returns to the **last completed message**.

### Checkpoint policy

* Create a checkpoint after:

  * role selection finalized
  * Round 1 speaker order + openings assigned
  * each Round 2 message (human or AI) committed
  * each Round 3 message (human or AI) committed
  * each Issue vote recorded

### Resume policy

* On resume, the UI loads:

  * current `status`
  * transcript entries up to `checkpoints.transcript_entry_id` (or by created_at <= checkpoint time)
  * current cursors (speaker cursor, debate round, conversation cursor)
* The next action is the next expected event for the current state.

---

## 5) State Machine: States, Events, and Transitions

### Legend

* **State**: a node in the machine
* **Event**: user/system action that triggers transition
* **Guards**: conditions that must be true
* **Side effects**: writes to DB/transcript, stance updates, scheduling AI calls

---

## 5.1 BOOT

**State:** `BOOT`

**Entry actions**

* If `game_id` provided: load game; go to `RESUME`
* Else: create new game shell; go to `ROLE_SELECTION`

**Transitions**

* `BOOT → ROLE_SELECTION` on `NEW_GAME_CREATED`
* `BOOT → RESUME` on `LOAD_EXISTING_GAME`

---

## 5.2 RESUME

**State:** `RESUME`

**Entry actions**

* Validate stored state consistency (schema version, required fields)
* Load last checkpoint
* Transition to stored `status`

**Transitions**

* `RESUME → <stored_status>` on `RESUME_READY`

---

## 5.3 ROLE_SELECTION

**State:** `ROLE_SELECTION`

**User actions**

* User selects a role from available roles (excluding chair)

**System actions (on confirm)**

* Persist `human_role_id`
* Initialize `seed` (if not present)
* Initialize base `stances` from Top Secret docs + selected opening variant bundle
* Precompute Round 1 constraints and generate `speaker_order`
* Assign Round 1 opening statement variants for all roles (no AI calls)

**Guards**

* Selected role must be valid

**Transitions**

* `ROLE_SELECTION → ROUND_1_SETUP` on `ROLE_CONFIRMED`

---

## 5.4 ROUND_1_SETUP

**State:** `ROUND_1_SETUP`

**Entry actions**

* Persist:

  * `round1.speaker_order`
  * `round1.openings` (variant id + text per role)
* Append transcript entries for Japan’s introductory framing (scripted)

**Transitions**

* `ROUND_1_SETUP → ROUND_1_OPENING_STATEMENTS` on `ROUND_1_READY`

---

## 5.5 ROUND_1_OPENING_STATEMENTS

**State:** `ROUND_1_OPENING_STATEMENTS`

**Mechanics**

* Japan announces each speaker in order
* Each speaker’s opening statement is displayed/recorded
* No live AI calls

**Cursor**

* `round1.cursor_index` over `speaker_order`

**On each step**

* Append transcript entry: Japan intro for the speaker
* Append transcript entry: speaker opening statement
* Update cursor

**Completion**

* When cursor reaches end:

  * set `status = ROUND_2_SETUP`

**Transitions**

* `ROUND_1_OPENING_STATEMENTS → ROUND_2_SETUP` on `ROUND_1_COMPLETE`

---

## 5.6 ROUND_2_SETUP

**State:** `ROUND_2_SETUP`

**Entry actions**

* Determine which roles “request to speak” with the human (from role config bundle)
* Display selectable list
* Initialize Round 2 counters

**Transitions**

* `ROUND_2_SETUP → ROUND_2_SELECT_CONVO_1` on `ROUND_2_READY`

---

## 5.7 ROUND_2_SELECT_CONVO_1

**State:** `ROUND_2_SELECT_CONVO_1`

**User actions**

* Choose first conversation partner (required)

**System actions**

* Create `round2.human_conversations[0]` with participants = {humanRoleId, partnerRoleId}
* Decide who starts (user chooses: start vs let AI start)

**Transitions**

* `ROUND_2_SELECT_CONVO_1 → ROUND_2_CONVERSATION_ACTIVE` on `CONVO_1_STARTED`

---

## 5.8 ROUND_2_CONVERSATION_ACTIVE

**State:** `ROUND_2_CONVERSATION_ACTIVE`

**Conversation constraints**

* Japan interrupts after **5 messages each** (human and partner)
* Then each gets **1 final message**

**Counters**

* `human_turns_used`, `partner_turns_used`
* `phase` within convo: `OPEN` | `INTERRUPT` | `FINAL_TURNS` | `CLOSED`

**Events**

* `HUMAN_MESSAGE_SUBMITTED`
* `AI_MESSAGE_COMMITTED`

**Side effects on each committed message**

* Append transcript entry (private; visible to human, not to other roles)
* Update stance state based on message content (rule-based or helper agent)
* Create checkpoint

**Interrupt trigger**

* When `human_turns_used == 5` and `partner_turns_used == 5`:

  * append Japan interrupt (scripted)
  * set phase `FINAL_TURNS`

**Close trigger**

* After each has produced one final message:

  * append Japan close (optional)
  * mark convo closed

**Transitions**

* `ROUND_2_CONVERSATION_ACTIVE → ROUND_2_SELECT_CONVO_2` on `CONVO_1_CLOSED`

---

## 5.9 ROUND_2_SELECT_CONVO_2

**State:** `ROUND_2_SELECT_CONVO_2`

**User actions**

* Choose second partner OR pass

**Transitions**

* `ROUND_2_SELECT_CONVO_2 → ROUND_2_CONVERSATION_ACTIVE` on `CONVO_2_STARTED`
* `ROUND_2_SELECT_CONVO_2 → ROUND_2_WRAP_UP` on `CONVO_2_SKIPPED`

---

## 5.10 ROUND_2_WRAP_UP

**State:** `ROUND_2_WRAP_UP`

**Entry actions**

* Apply any queued stance updates (e.g., helper summarizer results)
* Optionally apply AI–AI “background outcomes” (v1 may be none)
* Create checkpoint

**Transitions**

* `ROUND_2_WRAP_UP → ROUND_3_SETUP` on `ROUND_2_COMPLETE`

---

## 5.11 ROUND_3_SETUP

**State:** `ROUND_3_SETUP`

**Entry actions**

* Load the 4 issues + options (from GeneralInstructions)
* Initialize `active_issue_index = 0`
* Initialize issue state for debate
* Create checkpoint

**Transitions**

* `ROUND_3_SETUP → ISSUE_INTRO` on `ROUND_3_READY`

---

## 5.12 ISSUE_INTRO

**State:** `ISSUE_INTRO`

**Entry actions**

* Japan announces the issue and lists all fixed options
* UI enables “Issue modal” (pre-vote: shows issue + options)
* Determine discussion order for Debate Round 1

  * countries first, then NGOs
  * human placement options: first | random | skip
* Persist debate order and human choice

**Transitions**

* `ISSUE_INTRO → ISSUE_DEBATE_ROUND_1` on `ISSUE_INTRO_COMPLETE`

---

## 5.13 ISSUE_DEBATE_ROUND_1

**State:** `ISSUE_DEBATE_ROUND_1`

**Mechanics**

* Each role in order may speak once or skip
* NGOs only after countries

**Cursor**

* `issue.cursor_index` over `debate_order_round1`

**Events**

* `HUMAN_TURN_SPEAK`
* `HUMAN_TURN_SKIP`
* `AI_TURN_COMMITTED`

**Side effects**

* Append transcript entry (public)
* Update stance state incrementally
* Optionally update “explicit intent” fields for the speaker
* Create checkpoint

**Transitions**

* `ISSUE_DEBATE_ROUND_1 → ISSUE_DEBATE_ROUND_2` on `DEBATE_ROUND_1_COMPLETE`

---

## 5.14 ISSUE_DEBATE_ROUND_2

**State:** `ISSUE_DEBATE_ROUND_2`

Same as Round 1, with a separate stored order `debate_order_round2`.

**Transitions**

* `ISSUE_DEBATE_ROUND_2 → ISSUE_POSITION_FINALIZATION` on `DEBATE_ROUND_2_COMPLETE`

---

## 5.15 ISSUE_POSITION_FINALIZATION

**State:** `ISSUE_POSITION_FINALIZATION`

**Goal**

* Avoid expensive “query everyone at end” by maintaining continuously updated stance.

**Entry actions**

* Ensure each role has a current `issue_preference` selected (option id)

  * If a role did not speak, retain previous preference unless a rule update changed it
  * If the last speaker’s stance update is pending, apply it now

**Optional acceleration**

* If using helper agent: run/await a fast stance-delta computation for any roles marked `dirty`.

**Transitions**

* `ISSUE_POSITION_FINALIZATION → ISSUE_PROPOSAL_SELECTION` on `POSITIONS_FINALIZED`

---

## 5.16 ISSUE_PROPOSAL_SELECTION

**State:** `ISSUE_PROPOSAL_SELECTION`

**Mechanics**

* Each role has a selected `most_supported_option`.
* Japan selects one option to propose.

**V1 deterministic rule (to be implemented)**

* Select the option with the highest support among **countries**.
* Tie-breakers: stable deterministic ordering by option id

**Side effects**

* Append transcript entry: Japan proposes option X
* Persist `current_proposal_option_id`

**Transitions**

* `ISSUE_PROPOSAL_SELECTION → ISSUE_VOTE` on `PROPOSAL_MADE`

---

## 5.17 ISSUE_VOTE

**State:** `ISSUE_VOTE`

**Mechanics**

* Countries vote YES/NO on proposed option.
* NGOs and Japan do not vote.
* Unanimity required for adoption.

**Events**

* `HUMAN_VOTE_CAST` (if human is a voting country)
* `AI_VOTE_COMMITTED` (for each AI country)

**Side effects**

* Persist votes as they come in
* Append transcript entries (public): vote announcements
* When all 6 votes recorded:

  * compute result
  * append Japan result announcement
  * persist vote record for the issue
  * update issue modal content to include vote breakdown
  * create checkpoint

**Transitions**

* `ISSUE_VOTE → ISSUE_RESOLUTION` on `VOTE_COMPLETE`

---

## 5.18 ISSUE_RESOLUTION

**State:** `ISSUE_RESOLUTION`

**Rules**

* The issue is resolved permanently after the vote.
* No revotes and no alternate-option votes for that issue.

**Post-issue updates**

* Apply any conditional commitments affecting future issues (stance updates)
* Mark next issue as active

**Transitions**

* If `active_issue_index < 3`:

  * `ISSUE_RESOLUTION → ISSUE_INTRO` on `NEXT_ISSUE`
* Else:

  * `ISSUE_RESOLUTION → ROUND_3_COMPLETE` on `ALL_ISSUES_RESOLVED`

---

## 5.19 ROUND_3_COMPLETE

**State:** `ROUND_3_COMPLETE`

**Entry actions**

* Final checkpoint
* Transition to Review

**Transitions**

* `ROUND_3_COMPLETE → REVIEW` on `ROUND_3_ENDED`

---

## 5.20 REVIEW

**State:** `REVIEW`

**Displayed content**

* Full Round 1 transcript
* Full Round 2 transcripts (human conversations only)
* Full Round 3 transcript
* Vote records per issue (modal UI also available during Round 3)
* AI-generated summary of the game and human performance

**Events**

* `REQUEST_AI_SUMMARY`
* `AI_SUMMARY_READY`

**Side effects**

* Store summary in game record

**Terminal**

* `REVIEW` is terminal for the session; user may start a new game.

---

## 6) Transcript Visibility Rules

* Round 1 and Round 3 entries are **public**.
* Round 2 human conversations are **private**:

  * visible to the human in Review
  * visible to the human during later rounds via modal
  * NOT visible to other roles

---

## 7) AI Call Placement (V1 Guidance)

### Round 1

* No model calls (prewritten variants)

### Round 2

* Model calls only for the active private conversation partner
* Optional helper summarizer runs asynchronously after each committed message

### Round 3

* Model calls only for the next speaker in order
* Maintain stance incrementally to avoid end-of-issue latency
