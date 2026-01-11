BEGIN;

-- Brazil opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  '1a2b3c4d-5e6f-4789-9abc-def012345671',
  'BRA',
  'Brazil approaches this working group with a strong awareness of how mercury pollution affects real communities and environments. In our country, mercury is not an abstract global issue. It is present in river systems, forests, and livelihoods that sustain millions of people.\n\nThe International Mercury Assessment highlights the particular vulnerability of regions where artisanal and small-scale gold mining remains an important economic activity. These activities are often informal, closely tied to poverty, and concentrated in ecologically sensitive areas. Addressing mercury in these contexts requires solutions that are socially grounded as well as environmentally sound.\n\nBrazil supports international cooperation on mercury, especially where it can help reduce clear and well-documented harms. At the same time, we emphasize that effective action must reflect national circumstances. Policies that do not account for development challenges, enforcement capacity, and local realities risk displacing problems rather than solving them.\n\nOur priority is practical progress. This includes strengthening support for cleaner technologies, improving monitoring and data collection, and addressing mercury use in activities where alternatives can realistically be adopted. In the case of ASGM, progress depends on education, economic alternatives, and sustained engagement with affected communities.\n\nBrazil does not oppose ambition, but ambition must be matched with feasibility. Binding commitments that cannot be implemented on the ground will undermine trust and cooperation. A phased approach that builds capacity and confidence is more likely to deliver lasting results.\n\nWe also recognize that mercury pollution has regional and global dimensions. Brazil is prepared to engage constructively in discussions on atmospheric transport and shared impacts, provided these discussions respect national sovereignty and differentiated responsibilities.\n\nBrazil invites partners to focus on cooperation that delivers tangible benefits. By combining international support with locally appropriate solutions, this working group can reduce mercury risks while supporting sustainable development.',
  '{
    "summary":{
      "top_priorities":["reduction of mercury harms in vulnerable ecosystems and communities","capacity-sensitive international cooperation"],
      "red_lines":["binding commitments without implementation support","approaches that ignore development realities"],
      "flexibilities":["phased commitments","technology and capacity support","cooperation on monitoring and data"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.70},
      "ISSUE_2":{"preferred":"2.2","firmness":0.65},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.85}
    }
  }'::jsonb,
  '{
    "targets":["EU","USA","CAN","TZA","AMAP"],
    "topics":[
      {"topic":"ASGM support strategies","intent":"ask","details":"Discuss assistance, technology transfer, and community-based approaches."},
      {"topic":"capacity building","intent":"offer","details":"Frame phased action as a path to durable reductions."},
      {"topic":"regional impacts","intent":"probe","details":"Explore how regional ecosystems are affected by mercury deposition."}
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
  '2b3c4d5e-6f70-4819-abcd-ef0123456782',
  'BRA',
  'Brazil approaches this working group with a deep concern for the integrity of ecosystems that are vital not only to our country, but to the global environment. Mercury pollution threatens rivers, forests, and food systems that sustain biodiversity and human life alike.\n\nThe International Mercury Assessment shows that mercury accumulates in aquatic ecosystems and moves through food webs in ways that are difficult to reverse. In tropical regions, these impacts are amplified by ecological sensitivity and by close connections between communities and natural systems. Damage in these areas carries long-term consequences.\n\nFor Brazil, protecting ecosystems is inseparable from sustainable development. Environmental degradation erodes livelihoods, increases vulnerability, and imposes costs that far exceed the investments required for prevention. Addressing mercury is therefore a matter of stewardship as well as responsibility.\n\nBrazil supports international cooperation that reduces mercury releases and prevents further accumulation in sensitive environments. Measures that address mercury use in products and processes where alternatives exist can deliver meaningful gains. Efforts to reduce releases associated with artisanal and small-scale gold mining are also essential, provided they are paired with education, technical support, and viable economic options.\n\nAt the same time, Brazil emphasizes that environmental ambition must be matched with practical pathways. Policies that overlook enforcement realities or community needs risk driving harmful practices underground. Progress depends on engagement, trust, and sustained support.\n\nBrazil is open to discussions on atmospheric mercury and shared impacts, particularly where scientific evidence indicates risks to vulnerable ecosystems. Such discussions should advance cooperation rather than impose uniform obligations that ignore national context.\n\nBrazil invites partners to view mercury reduction as an investment in environmental resilience. By acting now to protect ecosystems, this working group can safeguard resources that future generations depend upon.',
  '{
    "summary":{
      "top_priorities":["protection of sensitive ecosystems","long-term environmental resilience"],
      "red_lines":["environmental measures detached from local realities","obligations without enforcement capacity"],
      "flexibilities":["phased environmental action","support for community-based solutions","cooperation on ecosystem monitoring"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.75},
      "ISSUE_2":{"preferred":"2.2","firmness":0.70},
      "ISSUE_3":{"preferred":"3.2","firmness":0.80},
      "ISSUE_4":{"preferred":"4.1","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","TZA","AMAP","WCAP"],
    "topics":[
      {"topic":"ecosystem protection","intent":"offer","details":"Frame mercury reduction as environmental stewardship."},
      {"topic":"ASGM transition support","intent":"ask","details":"Discuss sustainable alternatives and community engagement."},
      {"topic":"regional ecological risk","intent":"probe","details":"Highlight vulnerability of tropical ecosystems."}
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
  '3c4d5e6f-7081-492a-bcde-f01234567893',
  'BRA',
  'Brazil approaches this discussion with a focus on how mercury policy intersects with development realities. In many regions, the activities linked to mercury use are not peripheral. They are connected to income, employment, and the survival of communities with limited alternatives.\n\nThe International Mercury Assessment makes clear that artisanal and small-scale gold mining remains a significant source of mercury releases. It also shows that these activities are deeply embedded in local economies and often operate beyond the reach of formal regulation. Addressing mercury in this context requires more than restrictions. It requires pathways that people can realistically follow.\n\nBrazil supports international cooperation that recognizes these constraints. Policies that move too quickly toward prohibition risk pushing vulnerable populations further into informality, reducing oversight and increasing harm. Progress depends on building trust, providing alternatives, and strengthening institutions over time.\n\nOur priority is to reduce mercury risks while preserving social stability. This means investing in cleaner technologies, supporting education and training, and creating economic options that allow communities to transition away from mercury-dependent practices. These measures take time, but they are essential for durable outcomes.\n\nBrazil is open to cooperation on products and industrial processes where change can be achieved without threatening livelihoods. We also recognize the broader dimensions of mercury transport and are prepared to engage in dialogue on shared impacts, provided responsibilities remain differentiated and implementation remains feasible.\n\nBrazil cautions against approaches that rely heavily on binding obligations without sufficient support. Commitments that cannot be met on the ground weaken cooperation and credibility. A phased approach that links ambition to capacity is more likely to succeed.\n\nBrazil invites partners to focus on solutions that integrate environmental goals with development needs. By aligning mercury reduction with economic inclusion, this working group can make progress that is both effective and equitable.',
  '{
    "summary":{
      "top_priorities":["protection of livelihoods during mercury transition","development-aligned risk reduction"],
      "red_lines":["abrupt prohibitions affecting informal economies","binding obligations without economic alternatives"],
      "flexibilities":["phased transitions","capacity and livelihood support","voluntary measures that can strengthen over time"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.65},
      "ISSUE_2":{"preferred":"2.2","firmness":0.60},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["TZA","AMAP","WCAP","EU"],
    "topics":[
      {"topic":"livelihood transitions","intent":"ask","details":"Discuss economic alternatives tied to mercury reduction."},
      {"topic":"phased commitments","intent":"offer","details":"Promote gradual approaches linked to capacity growth."},
      {"topic":"implementation feasibility","intent":"probe","details":"Assess what commitments are realistic in informal sectors."}
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
  '4d5e6f70-8192-4a3b-cdef-0123456789a4',
  'BRA',
  'Brazil approaches this working group with a regional perspective. Mercury does not respect national borders. In South America, shared river systems, ecosystems, and trade link the consequences of mercury use across countries.\n\nThe International Mercury Assessment shows that mercury travels through air and water, contributing to regional deposition patterns. These dynamics mean that isolated national efforts are often insufficient. Progress depends on coordination, shared information, and trust among neighbors.\n\nBrazil believes that regional cooperation can play a central role in reducing mercury risks. Countries facing similar development challenges and environmental conditions can learn from one another and build solutions that are realistic and effective. South–South collaboration has the potential to deliver results that externally imposed models often fail to achieve.\n\nBrazil supports international action on mercury, particularly where it strengthens regional capacity. Improving monitoring networks, sharing technical expertise, and coordinating approaches to artisanal and small-scale gold mining can reduce risks while respecting national sovereignty.\n\nAt the same time, Brazil stresses that regional leadership must remain inclusive. Differences in capacity across countries require flexible arrangements and sustained support. Cooperative frameworks should enable participation rather than create new barriers.\n\nBrazil is prepared to engage constructively with partners on atmospheric mercury and global transport, provided these discussions recognize the value of regional approaches as building blocks for broader action.\n\nBrazil invites all parties to consider how regional cooperation can complement global frameworks. By strengthening collaboration among neighboring countries, this working group can advance mercury reduction in a way that is both effective and equitable.',
  '{
    "summary":{
      "top_priorities":["regional cooperation and coordination","capacity building through South–South collaboration"],
      "red_lines":["approaches that bypass regional institutions","uniform obligations that undermine regional solutions"],
      "flexibilities":["regionally coordinated measures","phased regional commitments","shared monitoring and data exchange"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.70},
      "ISSUE_2":{"preferred":"2.2","firmness":0.65},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.85}
    }
  }'::jsonb,
  '{
    "targets":["TZA","AMAP","WCAP","EU","CAN"],
    "topics":[
      {"topic":"regional coordination","intent":"offer","details":"Promote South–South cooperation as a foundation for action."},
      {"topic":"shared monitoring","intent":"ask","details":"Discuss regional data-sharing and joint monitoring efforts."},
      {"topic":"capacity partnerships","intent":"probe","details":"Explore how international support can strengthen regional institutions."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
