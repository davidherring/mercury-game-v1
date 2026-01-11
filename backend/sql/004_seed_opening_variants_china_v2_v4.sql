BEGIN;

-- Additional CHN opening variants (v2–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'a0f3b1f8-3d25-4e4f-9c5f-6d6a5e0c2b11',
  'CHN',
  'China welcomes the opportunity to participate in this working group and appreciates the effort that has gone into compiling the International Mercury Assessment. The report provides a valuable overview of current knowledge and, just as importantly, makes clear where significant gaps remain.\n\nMercury is a complex substance. It is naturally occurring, globally mobile, and persistent over long time scales. Human activity has altered this cycle, but the assessment also shows that attribution is difficult and that uncertainty remains high at multiple stages, from emissions inventories to ecosystem response. These facts should encourage caution and rigor in how we interpret the evidence.\n\nChina’s position is guided by two principles. The first is responsibility. Policies adopted here must be grounded in what the science can clearly support, not in assumptions about future benefits that may or may not materialize. The second is fairness. Countries differ widely in development stage, industrial structure, and capacity to act. Any international approach that ignores these differences risks being ineffective and unjust.\n\nAt this stage, China does not believe the evidence supports mandatory global controls on atmospheric mercury emissions. While long-range transport is real, the relationship between diffuse emissions and specific health outcomes remains uncertain, particularly when compared with well-documented cases of localized exposure. For this reason, China cannot support binding targets or timetables at this time.\n\nThat said, China does not advocate inaction. We support strengthening voluntary cooperation, improving emissions inventories, and expanding scientific research, especially in regions where data gaps are largest. Better information will benefit all parties and allow future decisions to be made on a more solid foundation.\n\nChina is also prepared to engage in practical discussions on mercury use in products and processes, where alternatives are technically and economically feasible. Progress in these areas can reduce intentional releases without imposing disproportionate burdens on development.\n\nChina encourages this working group to focus on achievable steps that build trust and knowledge. A measured, evidence-driven approach will create better outcomes than rushing toward commitments that the science does not yet justify.',
  '{
    "summary":{
      "top_priorities":["evidence-based decision making","protection of development flexibility"],
      "red_lines":["binding atmospheric emissions targets","premature legal obligations"],
      "flexibilities":["enhanced voluntary cooperation","scientific research and inventory development","targeted action on products and processes"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.75},
      "ISSUE_2":{"preferred":"2.2","firmness":0.85},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.2","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["EU","USA","CAN"],
    "topics":[
      {"topic":"scientific uncertainty","intent":"probe","details":"Highlight data gaps and limits of current causal evidence."},
      {"topic":"voluntary cooperation","intent":"offer","details":"Support enhanced information sharing and research collaboration."},
      {"topic":"products and processes","intent":"offer","details":"Explore phased reductions where alternatives are feasible."}
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
  'b6c4e8fd-6bd0-48f1-9f4b-7b8f7a0e5c22',
  'CHN',
  'China thanks the Chair and the Secretariat for convening this working group and for the extensive preparation reflected in the International Mercury Assessment. The document provides a shared foundation for discussion, and it also makes clear that mercury policy is not a simple question with a single answer.\n\nThe assessment shows that mercury is present throughout the environment and that human activity has altered its global cycle. It also shows that uncertainty remains significant. Emissions inventories vary widely in quality, the contribution of different sources is difficult to separate, and ecosystem responses unfold over long time periods. These realities should guide both our expectations and our decisions.\n\nChina believes that progress on mercury requires cooperation, but cooperation must be based on trust and balance. Many countries represented here are still developing. Their energy systems, industrial bases, and public health priorities differ fundamentally from those of countries that industrialized earlier. Any global approach that ignores this context risks placing disproportionate burdens on those least able to bear them.\n\nFor this reason, China cannot support binding international controls on atmospheric mercury emissions at this stage. Long-range transport exists, but the evidence does not yet justify mandatory targets that would constrain national development choices without clear and predictable benefits.\n\nAt the same time, China recognizes the concerns raised by other parties and does not seek to delay progress. We support strengthening voluntary action, expanding emissions monitoring, and improving scientific understanding, particularly in regions where data gaps remain largest. These steps can build confidence and prepare the ground for future decisions.\n\nChina also sees practical opportunities to reduce mercury use in products and processes where alternatives are already available. Cooperation in these areas can deliver tangible results and demonstrate good faith, especially if technology transfer and capacity building are part of the discussion.\n\nChina encourages this working group to focus on what can realistically be achieved now. Incremental progress, built on evidence and mutual respect, will bring us closer to effective global solutions than forcing premature commitments that divide the group.',
  '{
    "summary":{
      "top_priorities":["balanced cooperation across development levels","incremental progress grounded in evidence"],
      "red_lines":["binding atmospheric emissions limits","uniform obligations across countries"],
      "flexibilities":["voluntary cooperation","monitoring and data improvement","products and processes with viable alternatives"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.80},
      "ISSUE_2":{"preferred":"2.2","firmness":0.85},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.2","firmness":0.70}
    }
  }'::jsonb,
  '{
    "targets":["TZA","BRA","EU"],
    "topics":[
      {"topic":"differentiated responsibilities","intent":"probe","details":"Build alignment with developing country blocs on equity concerns."},
      {"topic":"voluntary cooperation","intent":"offer","details":"Frame voluntary measures as credible near-term progress."},
      {"topic":"technology transfer","intent":"ask","details":"Encourage support for capacity building tied to feasible actions."}
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
  'c4c2d6b1-7c31-4f49-bf3c-0e6b8e1f7d33',
  'CHN',
  'China participates in this working group as a country with both significant development needs and substantial experience managing environmental risk. We take mercury seriously, and we approach this discussion with a clear understanding of the tradeoffs involved.\n\nThe International Mercury Assessment confirms that mercury is persistent and globally mobile. It also confirms that emissions originate from a wide range of sources and that the benefits of reductions may take many years to materialize. These findings are important. They mean that policy decisions made here will carry real economic consequences while delivering uncertain and delayed returns.\n\nChina has already undertaken major domestic efforts to modernize its industrial base and improve environmental performance. These efforts require sustained investment and careful sequencing. International commitments that restrict energy choices or impose rigid controls would interfere with this process and risk undermining broader development goals.\n\nFor China, the central question is not whether mercury matters, but how action can be aligned with economic reality. Binding global limits on atmospheric emissions are not justified at this stage. The science does not yet support clear thresholds for action, and the costs of compliance would fall unevenly across countries.\n\nChina favors a practical approach. Improving emissions inventories, sharing technology, and addressing specific high-risk uses of mercury can produce progress without destabilizing development pathways. These steps also allow countries to act in ways that reflect their national circumstances.\n\nChina is prepared to engage constructively with partners who recognize these constraints. We are open to cooperation on products and processes where alternatives are viable and where transitions can be managed responsibly. We are also willing to participate in expanded monitoring efforts that improve the quality of future decisions.\n\nChina urges this working group to remain focused on realism. Effective international cooperation is built on policies that countries can implement, not on commitments that look strong on paper but fail in practice.',
  '{
    "summary":{
      "top_priorities":["economic feasibility of mercury controls","alignment of action with national development plans"],
      "red_lines":["binding atmospheric emissions caps","rigid international mandates affecting energy policy"],
      "flexibilities":["monitoring and inventory improvement","technology cooperation","targeted reductions in products and processes"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.85},
      "ISSUE_2":{"preferred":"2.2","firmness":0.90},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.2","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["USA","EU"],
    "topics":[
      {"topic":"economic costs of controls","intent":"warn","details":"Emphasize feasibility and long timelines for benefits."},
      {"topic":"domestic action recognition","intent":"probe","details":"Seek acknowledgment of national efforts outside binding frameworks."},
      {"topic":"technology cooperation","intent":"offer","details":"Explore non-binding collaboration that supports gradual transition."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
