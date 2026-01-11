BEGIN;

-- Mercury Free Future opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'ee1f2a3b-4c5d-6e7f-8a9b-0c1d2e3f4a81',
  'MFF',
  'Mercury Free Future participates in this negotiation to represent a simple principle. Mercury is a toxic substance, and continued exposure is neither necessary nor acceptable when safer alternatives exist.\n\nThe International Mercury Assessment documents extensive harm to human health and ecosystems from mercury pollution. Neurological damage, developmental risks, and long-term environmental contamination are not abstract concerns. They are documented outcomes of continued mercury use and release.\n\nFrom our perspective, the central question is not whether mercury poses a risk, but why its use continues despite available solutions. In many sectors, substitutes already exist that reduce or eliminate mercury without sacrificing performance or economic viability. Where alternatives are not yet widely adopted, targeted support can accelerate transition.\n\nMercury Free Future recognizes that countries face different circumstances and capacities. However, acknowledging these differences should not be used to justify indefinite delay. Each year of continued mercury release adds to a burden that future generations must bear.\n\nWe encourage participants to approach this negotiation with a prevention mindset. Managing emissions without addressing sources locks in long-term harm. Phasing out mercury where feasible delivers lasting benefits and reduces the need for costly remediation later.\n\nAmbition and practicality are not in conflict. Clear timelines, strong signals, and coordinated support can drive change while respecting national contexts. What matters is direction. Policies that move decisively away from mercury create certainty for communities, industries, and governments alike.\n\nMercury Free Future urges delegates to choose outcomes that protect health, ecosystems, and future generations. The tools exist. The evidence is clear. What remains is the willingness to act.',
  '{
    "summary":{
      "top_priorities":["elimination of mercury use","protection of human health and ecosystems"],
      "red_lines":["policies that normalize ongoing mercury use","open-ended timelines without phase-out intent"],
      "flexibilities":["phased transitions with clear endpoints","support for alternative technologies","assistance for affected communities"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.1","firmness":0.80},
      "ISSUE_4":{"preferred":"4.1","firmness":0.75}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","USA","AMAP","WCAP"],
    "topics":[
      {"topic":"mercury phase-out","intent":"ask","details":"Press for clear commitments to eliminate mercury use."},
      {"topic":"alternatives and substitutes","intent":"offer","details":"Share evidence that safer alternatives are feasible."},
      {"topic":"intergenerational risk","intent":"probe","details":"Challenge positions that delay action despite known harm."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'ff2a3b4c-5d6e-7f8a-9b0c-1d2e3f4a5b92',
  'MFF',
  'Mercury Free Future joins this discussion to speak for communities that rarely have a seat at negotiations, yet live with the consequences of mercury exposure every day.\n\nThe International Mercury Assessment makes clear that mercury does not affect all populations equally. Children, pregnant women, and workers in informal or poorly regulated sectors face higher risks and fewer protections. These disparities are not accidental. They reflect policy choices that tolerate harm where political influence is weakest.\n\nFrom our perspective, mercury pollution is a question of justice as much as science. When exposure is well documented and alternatives exist, continued use represents a decision to shift costs onto those least able to bear them.\n\nMercury Free Future recognizes that transitions require planning and support. However, justice demands that protection for vulnerable communities not be postponed indefinitely. Each delay extends exposure that is preventable.\n\nEquity also requires honesty about who benefits from inaction. Convenience, short-term savings, or institutional inertia cannot outweigh documented harm to human health. Where mercury use persists, it is often because its true costs are borne elsewhere.\n\nWe urge participants to evaluate proposals not only by technical feasibility, but by who is protected and who remains at risk. Policies that fail to reduce exposure for the most affected populations should be viewed as incomplete.\n\nMercury Free Future calls on delegates to commit to outcomes that prioritize people over pollutants. Eliminating mercury where possible is a matter of fairness, dignity, and responsibility. The measure of success should be whether those most exposed today are safer tomorrow.',
  '{
    "summary":{
      "top_priorities":["protection of vulnerable populations","elimination of unjust exposure"],
      "red_lines":["policies that externalize harm onto marginalized communities","delays that perpetuate known exposure"],
      "flexibilities":["equity-focused transition support","targeted protections for high-risk groups","phased elimination with justice benchmarks"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.1","firmness":0.80},
      "ISSUE_4":{"preferred":"4.1","firmness":0.80}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","USA","TZA","WCAP"],
    "topics":[
      {"topic":"environmental justice","intent":"ask","details":"Press delegates to address unequal exposure and protection."},
      {"topic":"vulnerable populations","intent":"offer","details":"Share evidence on disproportionate health impacts."},
      {"topic":"accountability for harm","intent":"probe","details":"Challenge who benefits from delayed action."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'a3b4c5d6-7e8f-9a0b-1c2d-3e4f5a6b7c03',
  'MFF',
  'Mercury Free Future engages in this process to help establish what responsible conduct looks like in the face of known harm. International agreements do more than coordinate action. They define norms that guide behavior across borders, markets, and institutions.\n\nThe International Mercury Assessment leaves little doubt that mercury poses serious and lasting risks to human health and ecosystems. When such risks are well documented, continued routine use becomes increasingly difficult to justify. Over time, what was once accepted practice should no longer be treated as normal.\n\nFrom our perspective, the purpose of this negotiation is to set clear expectations. Strong standards signal that mercury use is an exception to be managed down, not a baseline to be accommodated indefinitely. This clarity influences investment decisions, technology development, and public trust.\n\nMercury Free Future recognizes that countries move at different speeds. Norms do not require identical timelines, but they do require a shared direction. Ambiguous outcomes weaken incentives for change and reward delay.\n\nClear commitments also protect those who act first. When expectations are explicit, early movers are not placed at a disadvantage, and markets can shift toward safer alternatives with greater confidence.\n\nWe encourage delegates to consider how their decisions will be interpreted beyond this room. The absence of a strong signal can be read as acceptance. The presence of one can accelerate transition far beyond formal compliance.\n\nMercury Free Future urges participants to use this process to establish mercury elimination as the global standard. Doing so does not resolve every challenge immediately, but it sets a course that aligns policy, innovation, and responsibility over time.',
  '{
    "summary":{
      "top_priorities":["establishing mercury elimination as a global norm","clear and credible international standards"],
      "red_lines":["outcomes that normalize ongoing mercury use","ambiguous commitments without directional clarity"],
      "flexibilities":["differentiated timelines","phased compliance with clear endpoints","support for early adopters"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.1","firmness":0.85},
      "ISSUE_4":{"preferred":"4.1","firmness":0.75}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","USA","AMAP","WCAP"],
    "topics":[
      {"topic":"global standards","intent":"ask","details":"Encourage clear signals that mercury use is no longer acceptable."},
      {"topic":"market certainty","intent":"offer","details":"Explain how strong norms accelerate adoption of alternatives."},
      {"topic":"early mover protection","intent":"probe","details":"Discuss how commitments can avoid penalizing proactive actors."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'b4c5d6e7-8f9a-0b1c-2d3e-4f5a6b7c8d14',
  'MFF',
  'Mercury Free Future enters this discussion with a concern shared by many communities affected by mercury pollution. Too often, commitments are made without a clear path to delivery, leaving exposure unchanged and trust diminished.\n\nThe International Mercury Assessment documents ongoing harm despite years of awareness and partial controls. This gap between knowledge and outcomes is not a scientific failure. It is a failure of accountability.\n\nFrom our perspective, the credibility of this process depends on whether its decisions lead to measurable change. Statements of intent that lack enforcement, timelines, or consequences risk repeating past patterns where mercury reduction remains aspirational rather than real.\n\nMercury Free Future recognizes that negotiation requires compromise. However, compromise should not come at the expense of effectiveness. Outcomes that postpone responsibility or rely on voluntary goodwill place the burden of inaction on communities already facing exposure.\n\nAccountability is not about punishment. It is about alignment between commitments and consequences. Clear expectations, transparent reporting, and mechanisms to address non-performance protect both people and the integrity of the agreement itself.\n\nWe urge participants to consider how their positions will be judged not only by peers, but by those living with mercury contamination. Credibility is earned when commitments translate into reduced exposure, not when language is carefully balanced.\n\nMercury Free Future calls for outcomes that can be tracked, evaluated, and enforced. Without accountability, ambition is rhetorical. With it, meaningful change becomes possible.',
  '{
    "summary":{
      "top_priorities":["accountable and enforceable commitments","measurable reductions in mercury exposure"],
      "red_lines":["non-binding outcomes without follow-through","commitments lacking timelines or evaluation"],
      "flexibilities":["graduated enforcement mechanisms","review-linked escalation","support paired with accountability"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.90},
      "ISSUE_3":{"preferred":"3.1","firmness":0.85},
      "ISSUE_4":{"preferred":"4.1","firmness":0.80}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","USA","AMAP"],
    "topics":[
      {"topic":"commitment credibility","intent":"probe","details":"Examine how proposed outcomes will be enforced or evaluated."},
      {"topic":"implementation gaps","intent":"ask","details":"Press delegates to explain how commitments avoid past failures."},
      {"topic":"accountability mechanisms","intent":"offer","details":"Propose approaches that link ambition to delivery."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
