# Issue & Option JSON Spec (V1)

**Purpose:** Define the canonical, implementation-ready representation of issues and options for Round 3 voting. This spec is **agent-facing** (for gameplay logic and prompting), not player-facing pedagogy.

**Scope (V1):**

* Fixed issues and fixed options (no freeform text)
* Deterministic option IDs
* Agent-facing notes to anchor behavior and reduce hallucination
* Neutral short descriptions suitable for UI display

---

## Global Rules

* Each issue is voted on **independently**.
* **Unanimous approval by the six countries** is required for adoption.
* NGOs and Japan **do not vote**.
* After a vote (pass or fail), the issue is **closed permanently**.
* Japan proposes **one option per issue** for the vote.
* If multiple options have equal country support, **lowest optionId wins**.

---

## Canonical Data Shape

Each issue conforms to the following shape:

```json
{
  "issue_id": "<number>",
  "title": "<string>",
  "ui_prompt": "<string>",
  "options": [
    {
      "option_id": "<issue>.<index>",
      "label": "<short label>",
      "short_description": "<neutral description>",
      "long_description": "<authoritative text sourced verbatim from HgGame_GeneralInstructions.pdf>",
      "agent_notes": [
        "<bullet>",
        "<bullet>"
      ]
    }
  ]
}
```

* `option_id` values are **stable and deterministic**.
* `agent_notes` are **not shown to players**; they are injected into prompts.

---

## Issue 1 — **Institutional Form for Action**

```json
{
  "issue_id": "1",
  "title": "If and how to regulate mercury emissions",
  "ui_prompt": "Is global action necessary to address mercury, and what form should action take?",
  "options": [
    {
      "option_id": "1.1",
      "label": "Binding emissions limits",
      "short_description": "Countries adopt legally binding limits on mercury emissions from major sources.",
      "long_description": "There is sufficient evidence that mercury is a global problem with significant risks. Initiate formal negotiations for a new legally binding mercury convention.",
      "agent_notes": [
  "Supported by parties arguing mercury is a global pollutant requiring a global response under the precautionary principle",
  "Often prioritized by NGOs and Arctic-impacted actors who emphasize long-range transport and vulnerable populations",
  "Seen as the clearest path to coordinated action (binding commitments, reporting, and accountability), but with higher compliance costs",
  "Opposed by actors emphasizing scientific uncertainty, national sovereignty, and the economic burden of mandatory controls"
]
    },
    {
      "option_id": "1.2",
      "label": "Voluntary reduction targets",
      "short_description": "Countries commit to non-binding targets to reduce mercury emissions.",
      "long_description": "There is a need for more evidence that mercury is a global problem with significant risks. Enhance voluntary measures.",
"agent_notes": [
  "Supported by parties emphasizing flexibility, sovereignty, and lower near-term costs through non-binding cooperation",
  "Often framed as “evidence first”: expand monitoring and inventories before committing to a treaty",
  "Politically attractive to countries with limited capacity or high dependence on emitting sectors, since targets are voluntary",
  "Criticized by NGOs and Arctic-focused actors as too weak to prevent ongoing harm and delays meaningful reductions"
]


    }
  ]
}
```

---

## Issue 2 — Atmospheric Emissions

```json
{
  "issue_id": "2",
  "title": "Inclusion of atmospheric mercury emissions",
  "ui_prompt": "Should atmospheric emissions of mercury be within the scope of a potential agreement?",
  "options": [
    {
      "option_id": "2.1",
      "label": "Include atmospheric emissions with binding requirements",
      "short_description": "Atmospheric mercury emissions are included with mandatory inventories, targets, and timetables.",
      "long_description": "There is sufficient information that atmospheric emissions are a large source of mercury. This issue should be included in the scope. Future negotiations should include requiring national emissions inventories and proposed timetables and targets for all major emitters.",
"agent_notes": [
  "Supported by parties emphasizing long-range transport and disproportionate impacts on downwind and Arctic regions",
  "Frames atmospheric emissions as the core global pathway, warranting inventories plus targets and timetables for major emitters",
  "Often paired with calls for financing and technical support so countries can build inventories and implement controls",
  "Opposed by actors citing high control costs, enforcement challenges, and uncertainty about how much reduces real-world risk"
]
    },
    {
      "option_id": "2.2",
      "label": "Exclude atmospheric emissions pending further evidence",
      "short_description": "Atmospheric emissions are excluded until scientific uncertainties are reduced.",
      "long_description": "There is insufficient evidence that atmospheric mercury emissions are a large source of mercury. This issue should be excluded from the scope. Future negotiations could gather information on inventories to all media before taking action.",
"agent_notes": [
  "Supported by parties emphasizing uncertainty, the large role of natural sources and re-emissions, and the cost of controls",
  "Often framed as “study first”: expand inventories and monitoring across media before committing to atmospheric obligations",
  "Appeals to countries prioritizing economic development or energy security and wary of expensive power-sector requirements",
  "Strongly opposed by Arctic-focused actors and NGOs who argue delay allows continued global deposition and harm"
]
    }
  ]
}
```

---

## Issue 3 — Products and Processes

```json
{
  "issue_id": "3",
  "title": "Inclusion of mercury demand in products and processes",
  "ui_prompt": "Should global demand for products and processes be included within the scope of a potential agreement?",
  "options": [
    {
      "option_id": "3.1",
      "label": "Include products and processes within the scope",
      "short_description": "Global demand for mercury in products and processes is included within the scope of future action.",
      "long_description": "There is sufficient evidence that demand for mercury used in products and processes significantly contributes to the global mercury problem. All products and processes should be included within the scope of future negotiations.",
"agent_notes": [
  "Supported by parties emphasizing intentional mercury use, trade, and preventable releases from disposal and waste",
  "Often viewed as a relatively tractable first step where substitutes exist, compared to controlling diffuse emissions",
  "Raises equity and feasibility concerns for countries relying on certain products/processes where alternatives are costly or limited",
  "Opposed by actors wary of broad mandates, compliance burdens, and the need for financing and technology transfer"
]

    },
{
      "option_id": "3.2",
      "label": "Include some pre-identified products and processes in the scope",
      "short_description": "Mercury use in some pre-identified products and processes is included from the scope of a potential agreement.",
      "long_description": "Demand for mercury used in some products and processes contributes significantly to emissions and mercury releases, while other mercury uses do not. The parties should draft a list for inclusion in the scope of future negotiations",
"agent_notes": [
  "Often framed as a pragmatic compromise: include demand, but limit scope to an agreed list of priority uses",
  "Appeals to parties prioritizing feasibility, national flexibility, and differentiated timelines based on capacity",
  "Centers negotiations on substitutes, costs, and exemptions for uses where alternatives are not yet viable",
  "Criticized by NGOs as too weak if the list becomes narrow, slow, or leaves major uses untouched"
]

    },
    {
      "option_id": "3.3",
      "label": "Exclude products and processes from the scope",
      "short_description": "Mercury use in products and processes is excluded from the scope of a potential agreement.",
      "long_description": "There is insufficient evidence that demand for mercury used in products and processes significantly contributes to the global mercury problem. All products and processes should be excluded from the scope of future negotiations.",
"agent_notes": [
  "Supported by parties emphasizing sovereignty, development priorities, and uncertainty about costs and substitutes",
  "Often framed as “domestic action first”: allow national regulation while gathering more information",
  "Appeals to countries with ongoing reliance on mercury-containing products or industrial processes",
  "Strongly opposed by NGOs and many countries arguing exclusion leaves preventable demand and waste pathways unaddressed"
]
    }
  ]
}
```

---

## Issue 4 — Artisanal and Small-Scale Gold Mining (ASGM)

```json
{
  "issue_id": "4",
  "title": "Inclusion of mercury emissions from artisanal and small-scale gold mining (ASGM)",
  "ui_prompt": "Should mercury emissions from artisanal and small-scale gold mining (ASGM) be included within the scope of a potential agreement?",
  "options": [
    {
      "option_id": "4.1",
      "label": "Include ASGM within the scope",
      "short_description": "Mercury use in ASGM is included within the scope of future action.",
      "long_description": "There is sufficient evidence that mercury use in ASGM is a significant part of the global mercury problem. ASGM should be included within the scope of future negotiations, with potential actions including requiring countries to submit national action plans on ASGM with timetables to phase out the usage.",
      "agent_notes": [
        "Supported by parties emphasizing ASGM as a major, preventable exposure pathway with serious local health risks",
        "Often prioritized by developing-country blocs that see ASGM as central, but condition progress on financing and technology transfer",
        "Seen as a pathway to formalize the sector and reduce harms without collapsing livelihoods in poor rural communities",
        "Opposed by parties arguing ASGM is hard to regulate in the informal sector and should not trigger strict international obligations"
      ]
    },
    {
      "option_id": "4.2",
      "label": "Exclude ASGM pending further assessments",
      "short_description": "ASGM is excluded from the scope while further information is gathered with support.",
      "long_description": "There is insufficient evidence that mercury use in ASGM is a significant part of the global mercury problem or that ASGM is a tractable problem. ASGM should be excluded from the scope of future negotiations while financial and technical support are provided to conduct further assessments on ASGM.",
      "agent_notes": [
        "Supported by parties emphasizing tractability, sovereignty, and enforcement limits in informal mining sectors",
        "Often framed as “study first”: build better data on scale, emissions, and workable interventions before prescribing obligations",
        "Politically attractive to actors worried about poverty/development impacts and the feasibility of phase-out timetables",
        "Strongly opposed by NGOs and affected regions arguing delay prolongs harm to vulnerable communities and workers"
      ]
    }
  ]
}

```

---

## Implementation Notes (Non-Functional)

* Option IDs must be treated as **opaque identifiers**; do not infer meaning from ordering beyond deterministic tie-breaking.
* `agent_notes` should be injected into prompts alongside role-specific instructions.
* UI should display only `title`, `ui_prompt`, `label`, and `short_description`.
* Future versions may add weights or metadata, but V1 logic must work without them.

---

**Status:** Ready for backend wiring and prompt integration.
