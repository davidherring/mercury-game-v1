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

## 3. AI behavior constraints (gameplay)

### 3.1 Role behavior

AI representatives:

* May **withhold private information**
* May **bluff or misrepresent strategically**
* May offer **conditional support or cross‑issue trades**
* Must **defend their interests** and red lines
* Must **not automatically agree** for the sake of consensus

Private role instructions are **never** to be revealed or paraphrased verbatim.

---

### 3.2 Information boundaries

* Round 2 private conversations are **private forever**:

  * visible to the human player
  * not visible to other AI roles
* AI roles must not reference private conversations they were not part of.
* The IMA Assessment may be referenced **only through approved excerpts**.

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

---

## 4. AI call placement & performance rules

### 4.1 Round 1

* **No live model calls**
* Use prewritten opening variants only

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
