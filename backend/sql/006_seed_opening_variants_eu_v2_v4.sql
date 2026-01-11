BEGIN;

-- Additional EU opening variants (v2–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'e1c2d3f4-5a6b-4c7d-8e9f-0a1b2c3d4e55',
  'EU',
  'The European Union welcomes the opportunity to continue this work on mercury with a shared commitment to seriousness and clarity. The International Mercury Assessment provides a necessary foundation, and it also underscores the importance of designing responses that are coherent, enforceable, and capable of lasting beyond political cycles.\n\nMercury poses a distinct challenge because of its persistence and its ability to move across borders. These characteristics mean that isolated national measures, while valuable, cannot fully address the problem. At the same time, experience shows that international agreements succeed only when they align with existing regulatory systems and legal obligations.\n\nFor the European Union, precaution is closely linked to governance. Acting in the face of uncertainty does not mean acting without structure. It means ensuring that decisions are embedded in clear rules, transparent reporting, and mechanisms that allow for review and adjustment as evidence evolves.\n\nThe EU therefore supports moving toward a coordinated international framework that establishes common expectations for reducing anthropogenic mercury releases, particularly from sources with global reach. Such a framework should be designed to integrate with domestic regulatory systems rather than operate in isolation from them.\n\nWe also recognize that implementation capacity varies. Differentiated pathways, phased obligations, and targeted support can ensure that participation is broad and that commitments are meaningful. Flexibility strengthens agreements when it is paired with clarity about objectives and responsibilities.\n\nThe European Union sees particular value in addressing mercury use in products and industrial processes where alternatives are already available. These measures can be incorporated into regulatory systems with relative certainty and can deliver measurable benefits over shorter timeframes.\n\nThe EU looks forward to working with partners to identify options that combine ambition with legal and institutional soundness. A credible response to mercury must be both forward-looking and firmly grounded in governance that works.',
  '{
    "summary":{
      "top_priorities":["legally coherent international action","reduction of anthropogenic mercury releases"],
      "red_lines":["approaches lacking regulatory clarity","exclusion of major global sources from scope"],
      "flexibilities":["phased implementation","differentiated pathways","implementation support"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.70}
    }
  }'::jsonb,
  '{
    "targets":["USA","CAN","CHN"],
    "topics":[
      {"topic":"regulatory alignment","intent":"probe","details":"Discuss how international commitments could integrate with domestic legal systems."},
      {"topic":"framework architecture","intent":"offer","details":"Explore design options that balance ambition with enforceability."},
      {"topic":"products and processes","intent":"ask","details":"Identify areas where regulatory action can deliver near-term benefits."}
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
  'f2a3b4c5-6d7e-4f8a-9b0c-1d2e3f4a5b66',
  'EU',
  'The European Union approaches this discussion with a clear concern for the human and environmental consequences of mercury pollution. Mercury is not simply a technical issue. It is a substance that accumulates silently, travels far from its sources, and imposes risks that are borne disproportionately by vulnerable communities and future generations.\n\nThe International Mercury Assessment documents pathways of exposure that are well understood, particularly through food systems. It also shows that mercury persists for decades, meaning that decisions to delay action today shape the risks of tomorrow. Uncertainty about precise magnitudes does not negate these realities. In many cases, it strengthens the case for prevention.\n\nFor the European Union, precaution is a matter of responsibility. Experience with other persistent pollutants has shown that waiting for complete certainty often leads to avoidable harm and higher costs. When credible evidence points to widespread risk, early action is the safer course.\n\nThe EU therefore supports moving beyond voluntary efforts toward a shared international response that addresses major sources of anthropogenic mercury. Atmospheric emissions, in particular, contribute to a global burden that no country can manage alone. Addressing these sources is essential if collective efforts are to be meaningful.\n\nAt the same time, the European Union recognizes that action must be fair. Countries differ in capacity, and pathways toward reduction must reflect those differences. Equity and ambition are not in tension when assistance, technology sharing, and phased approaches are part of the solution.\n\nThe EU also places strong emphasis on reducing mercury use in products and industrial processes where alternatives exist. These measures protect consumers directly and demonstrate that prevention is both feasible and effective.\n\nThe European Union invites partners to consider not only what is easiest in the short term, but what is responsible in the long term. Protecting health and ecosystems requires foresight, cooperation, and the willingness to act before harm becomes irreversible.',
  '{
    "summary":{
      "top_priorities":["prevention of health and ecological harm","reduction of global mercury burden"],
      "red_lines":["continued reliance on voluntary action alone","postponement of action despite credible risk"],
      "flexibilities":["phased obligations","capacity-based differentiation","assistance and technology transfer"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.2","firmness":0.80},
      "ISSUE_4":{"preferred":"4.1","firmness":0.75}
    }
  }'::jsonb,
  '{
    "targets":["USA","CAN","CHN","AMAP","WCAP"],
    "topics":[
      {"topic":"health and ecosystem risk","intent":"probe","details":"Center discussion on exposure pathways and long-term impacts."},
      {"topic":"precautionary action","intent":"offer","details":"Frame early action as responsible risk management."},
      {"topic":"support for equitable action","intent":"offer","details":"Discuss assistance mechanisms that enable ambitious participation."}
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
  '0a1b2c3d-4e5f-4a6b-8c9d-1e2f3a4b5c77',
  'EU',
  'The European Union approaches this working group with the aim of strengthening cooperation and maintaining a shared focus on progress that is achievable for all parties. Mercury presents a global challenge, but the effectiveness of any response will depend on whether it brings countries together rather than divides them.\n\nThe International Mercury Assessment shows that mercury moves across borders and persists in the environment, linking national actions through a shared global cycle. At the same time, it also reflects uneven data quality and different national circumstances. These realities suggest that progress will require patience, trust, and a willingness to advance step by step.\n\nFor the European Union, international cooperation succeeds when it balances ambition with inclusion. A framework that is supported by many countries, even if it advances incrementally, can ultimately deliver greater impact than one that moves quickly but leaves key actors behind.\n\nThe EU therefore supports a phased approach to addressing mercury, beginning with areas where consensus is strongest and benefits are most immediate. Improving emissions monitoring, strengthening information exchange, and reducing mercury use in products and processes where alternatives exist are practical starting points.\n\nAt the same time, the European Union believes it is important to keep longer-term objectives in view. Atmospheric emissions contribute to a global burden that cannot be ignored indefinitely. Discussions today should lay the groundwork for deeper cooperation in the future, even if not all elements are addressed at once.\n\nThe EU recognizes that countries differ in capacity and priorities. Differentiated pathways, voluntary commitments that can evolve over time, and targeted support can help build confidence and participation without foreclosing future ambition.\n\nThe European Union invites all parties to approach this process in a spirit of pragmatism and mutual respect. By focusing on shared interests and workable steps, this group can move forward together while keeping the door open to stronger action as understanding and trust deepen.',
  '{
    "summary":{
      "top_priorities":["inclusive international cooperation","incremental progress toward long-term reductions"],
      "red_lines":["approaches that fragment participation","frameworks that exclude key emitters"],
      "flexibilities":["phased commitments","voluntary measures that can strengthen over time","capacity-based differentiation"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.75},
      "ISSUE_2":{"preferred":"2.1","firmness":0.70},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["USA","CAN","CHN","BRA","TZA"],
    "topics":[
      {"topic":"phased cooperation","intent":"offer","details":"Explore stepwise approaches that maintain broad participation."},
      {"topic":"confidence building","intent":"probe","details":"Identify actions that can build trust across differing positions."},
      {"topic":"future ambition","intent":"ask","details":"Discuss how voluntary measures could evolve into stronger commitments."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
