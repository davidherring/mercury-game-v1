# GAME_STATE.md

**Purpose:** This document defines a **concrete, implementation-ready example** of the `game_state` object. It exists to:

* Prevent architectural drift
* Make backend routes and frontend state usage obvious
* Ensure save/resume correctness
* Enable coding to begin immediately after this doc

This is **not a proposal** or a flexible sketch. It is a **reference shape** that code should conform to.

---

## High-level principles

* `game_state` is the **authoritative snapshot** of gameplay
* Everything needed to resume the game lives here
* It is safe to store this as JSONB in Postgres
* Transcript content lives elsewhere; `game_state` stores **pointers and cursors**, not full text

---

## Example: Mid–Round 3 game state

```json
{
  "game_id": "game_7f3a92",
  "version": "v1",
  "created_at": "2026-01-14T18:42:11Z",
  "updated_at": "2026-01-14T19:07:44Z",

  "status": "ISSUE_DEBATE_ROUND_1",

  "human_role_id": "USA",

  "roles": {
    "USA": { "type": "country" },
    "BRA": { "type": "country" },
    "CAN": { "type": "country" },
    "CHN": { "type": "country" },
    "EU":  { "type": "country" },
    "TZA": { "type": "country" },

    "AMAP": { "type": "ngo" },
    "MFF":  { "type": "ngo" },
    "WCPA": { "type": "ngo" },

    "JPN":  { "type": "chair" }
  },

  "round1": {
    "speaker_order": ["CAN", "CHN", "USA", "BRA", "EU", "TZA", "AMAP", "MFF", "WCPA"],
    "opening_variants": {
      "USA": "usa_opening_v2",
      "BRA": "bra_opening_v1",
      "CHN": "chn_opening_v3",
      "EU":  "eu_opening_v1",
      "CAN": "can_opening_v2",
      "TZA": "tza_opening_v1",
      "AMAP": "amap_opening_v1",
      "MFF":  "mff_opening_v2",
      "WCPA": "wcpa_opening_v1"
    },
    "cursor": 9
  },

  "round2": {
    "human_conversations": [
      {
        "conversation_id": "r2c1",
        "participants": ["USA", "EU"],
        "human_turns_used": 5,
        "ai_turns_used": 5,
        "phase": "FINAL_TURNS",
        "closed": true
      }
    ],
    "second_conversation_available": true
  },

  "round3": {
    "issues": ["1", "2", "3", "4"],
    "active_issue_index": 0,

    "active_issue": {
      "issue_id": "1",
      "debate_round": 1,
      "debate_order": ["USA", "BRA", "EU", "CAN", "CHN", "TZA", "AMAP", "MFF", "WCPA"],
      "cursor": 2
    }
  },

  "stances": {
    "USA": {
      "1": {
        "acceptance": {
          "1.1": 0.85,
          "1.2": null
        },
        "firmness": 0.7
      },
      "2": {
        "acceptance": {
          "2.1": 0.4,
          "2.2": 0.75
        },
        "firmness": 0.6
      },
      "3": {
        "acceptance": {
          "3.1": 0.3,
          "3.2": 0.65,
          "3.3": null
        },
        "firmness": 0.7
      },
      "4": {
        "acceptance": {
          "4.1": 0.5,
          "4.2": 0.8
        },
        "firmness": 0.5
      }
    },
    "EU": {
      "1": {
        "acceptance": {
          "1.1": 0.9,
          "1.2": 0.2
        },
        "firmness": 0.85
      },
      "2": {
        "acceptance": {
          "2.1": 0.9,
          "2.2": 0.4
        },
        "firmness": 0.8
      },
      "3": {
        "acceptance": {
          "3.1": 0.85,
          "3.2": 0.3,
          "3.3": null
        },
        "firmness": 0.9
      },
      "4": {
        "acceptance": {
          "4.1": 0.75,
          "4.2": 0.4
        },
        "firmness": 0.6
      }
    }
  },

  "votes": {
    "1": {
      "proposal": null,
      "country_votes": {},
      "resolved": false
    }
  },

  "checkpoints": [
    {
      "checkpoint_id": "cp_018",
      "created_at": "2026-01-14T19:07:44Z",
      "status": "ISSUE_DEBATE_ROUND_1",
      "transcript_upto": 143
    }
  ]
}
```

---

## Field-by-field explanation (what matters for coding)

### `status`

* Drives backend routing and frontend rendering
* No UI should infer phase indirectly

---

### `roles`

* Minimal role metadata only
* Display names, flags, and full role info live elsewhere

---

### `round1`

* All randomness resolved and persisted
* `cursor` indicates how many speakers have completed

---

### `round2`

* Conversations are tracked structurally, not textually
* Turn counts enforce Japan’s interruption rules

---

### `round3.active_issue`

* Cursor-based debate progression
* No role can speak twice in the same debate round

---

### `stances`

* Each role tracks **per-option acceptance scores** for each issue
* Acceptance values:

  * `null` → structurally unacceptable (immutable red line)
  * `0.0–1.0` → persuadable to varying degrees
* `firmness` represents resistance to change, not mathematical decay
* There are **no formulas** governing updates
* Agents may adjust acceptance values qualitatively, but must:

  * respect `null` as immutable
  * keep values within bounds

Voting rule:

* A country votes **YES** if `acceptance[proposed_option] ≥ 0.7`
* `null` always results in a NO vote

---

### `votes`

* Populated only after Japan proposes an option
* Votes recorded incrementally

---

### `checkpoints`

* Store *where* to resume, not *what happened*
* `transcript_upto` links to transcript_entries table

---

## What this enables immediately

With this shape, you can now:

* Implement `POST /games` (new game)
* Implement `POST /games/{id}/advance` (state transitions)
* Implement save/resume logic
* Build frontend components directly from `status`
* Log transcript entries independently

---

## What is intentionally *not* here

* Transcript text
* UI presentation details
* Instructor/admin roles
* Authentication data

Those come later and do **not** require changing this shape.
