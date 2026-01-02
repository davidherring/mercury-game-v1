# Mercury Negotiation Game (AI‑Integrated Web Version)

## 1. Purpose & Learning Goals

**Core purpose**
Rebuild the Mercury Negotiation Simulation as a single‑player, AI‑mediated web game that preserves:

* Multi‑party negotiation dynamics
* Asymmetric information (private role instructions)
* The tension between science, uncertainty, economics, and politics

**Learning outcomes (inferred)**

* Understand science‑policy negotiation tradeoffs
* Practice coalition‑building and deal‑making
* Experience how incentives shape negotiation behavior
* Reflect on how information access influences outcomes

This version replaces human counterparts with AI agents while keeping one human learner fully embedded in the negotiation.

---

## 2. High‑Level Game Structure

**Actors (10 total)**

* 1 Human player (selects a role)
* 9 AI agents

  * Countries: Brazil (GRULAC), Canada, China, EU, Tanzania (Africa Group), USA
  * NGOs: AMAP, MFF, WCPA
  * Chair/Moderator: Japan

**Rounds**

1. **Round 1 – Opening Statements**

   * Each representative presents an opening position
   * Public, sequential
   * AI statements drawn from curated variants (reduces API calls)

2. **Round 2 – Private Negotiations**

   * One‑on‑one or small‑group discussions
   * Private, role‑specific
   * AI agents negotiate based on goals, constraints, and prior interactions

3. **Round 3 – Formal Debate & Voting**

   * Four issues debated
   * Voting / consensus logic applied

4. **Post‑Game Review**

   * Replay conversation history
   * Outcome summary
   * Optional instructor‑guided reflection

---

## 2A. V1 Mechanics Clarifications

### Voting

* **Each country has exactly one vote** (Brazil and Tanzania may *represent blocs* rhetorically but do not get extra votes).
* NGOs do **not** vote.
* **Unanimous YES** across the voting countries is required for an issue to pass.

### Round 1 – Speaker order

* Japan introduces each speaker.
* Speaker order is randomized after role selection, with constraint: the human does **not** speak first among countries or NGOs.
* The order is shown on screen and reinforced by Japan’s introductions.

### Round 2 – Human private negotiations

* The human chooses **1 mandatory** private conversation partner; a **2nd is optional**.
* Some representatives indicate they want to speak with the human (shown as a list), but the human chooses.
* In a private conversation, the human can go first or let the counterpart start.
* Japan enforces a basic cap: interrupt after **5 comments each** (human + agent), then allow **1 final comment each** to finalize plans.
* AI–AI private negotiations occur separately; prebuilt/snippet-based conversations may be used to reduce API calls.

  * If the human selects a given AI representative, that AI conducts only **one** additional AI–AI conversation.

### Round 3 – Debate & voting loop

* Four issues are handled **sequentially**.
* Each issue has **two discussion rounds**.

  * In each discussion round, each representative may speak at most once (or skip).
  * Therefore any representative may speak at most **twice** per issue.
* NGOs follow the same speaking limits and may speak **only after countries**.
* For Round 3 speaker order:

  * The order for the first discussion round is shown on screen.
  * The human may choose: go first, be inserted randomly, or skip their turn.
  * The process repeats for the second discussion round, then the vote.

## 3. Core Issues Under Negotiation

There are **four issues**, each debated and voted **independently** in **Round 3**, in **sequential order**:

1. **Institutional Form for Action**

   * Legally binding treaty vs voluntary measures

2. **Atmospheric Emissions**

   * Inclusion/exclusions, inventories, targets, timelines

3. **Products & Processes**

   * Phase-outs, exemptions, timelines

4. **Artisanal & Small-Scale Gold Mining (ASGM)**

   * Inclusion, financing, national action plans

**Decision rule (v1):**

* **Only countries/blocks vote**; NGOs do **not** vote.
* Voting power is **equal** across voting representatives.
* An issue passes only with a **unanimous YES** vote.
* Most propositions may fail; failure is expected.

**Round 3 speaking constraint (v1):**

* For each issue, each participant may speak **up to two times** during the debate before the vote.

## 4. Role Architecture

### Role Definition Components

Each role includes:

* Public stance summary
* Private objectives
* Red lines / non‑negotiables
* Flexibility levers (what concessions are possible, under what conditions)
* Rhetorical style / tone

### Role Data Sources

* Converted from existing PDFs (MIT Mercury Game)
* Normalized into structured JSON for agent prompts

---

## 5. Pages & User Flow

### Required Pages

* **Login** (Google OAuth)
* **Role Selection**
* **Round 1 Interface** (public statements)
* **Round 2 Interface** (private negotiation UI)
* **Round 3 Interface** (formal debate + voting)
* **Review Page** (timeline + outcomes)

### Optional / Phase‑2 Pages

* Instructor Admin (class creation, analytics)
* User Profile (past games)
* Site Admin

---

## 6. Data Model (Draft)

### users

* id
* name
* email
* role (student | instructor | admin)
* classes[]

### roles

* id
* country_or_org
* public_summary
* private_instructions
* personality_traits

### opening_statements

* role_id
* text
* tone

### negotiation_snippets (optional optimization)

* participants[]
* scenario_tags
* dialogue

### game_records

* id
* user_id
* selected_role
* state (round, issue)
* conversation_log
* decisions
* outcome_summary

---

## 7. AI Architecture (Initial, Non-MCP)

### Key behavioral requirements

* Agents may **withhold** private information; private notes should never be openly disclosed.
* Agents may **bluff / misrepresent** strategically when appropriate.
* Agents must **not automatically agree**; they should defend interests and red lines.
* Agents may trade support across issues (e.g., side deals) and make financial promises where plausible.
* Scientific arguments may reference the **shared IMA Assessment**.

### Agent strategy (v1)

To reduce timeouts and complexity:

* Use **one primary LLM “role actor”** that is re-prompted per speaking turn with:

  * The role’s private instructions
  * Shared game rules and constraints
  * The current round + issue
  * The current public transcript + relevant private negotiation context
* Optionally use **one secondary summarizer** behind the scenes to maintain a compact running summary.

  * Summaries should be structured (e.g., positions, concessions, threats, promises, and open questions).

### Performance / reliability constraints

* Round 1 should run **without live model calls** (use curated opening statements) to allow background warm-up and reduce early latency.
* Japan (Chair) can be **largely automated** via templated moderation actions and timing gates.
* Prevent timeouts by:

  * Early initialization / warm-up
  * Bounded prompt sizes
  * Streaming responses to the UI

## 8. Tooling & Workflow

**Stack**

* Frontend: React + TypeScript
* Backend: Python + FastAPI
* DB: MongoDB (open to Postgres if relational needs increase)
* AI: OpenAI API

**AI‑Assisted Development**

* Codex for implementation
* AGENTS.md for repo‑level constraints
* GitHub + VS Code

---

## 9. Explicit Non‑Goals (for v1)

* Real‑time multiplayer
* MCP server
* Goose / autonomous long‑running agents
* Full instructor analytics

These are *deliberate exclusions* to protect completion.
