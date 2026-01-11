BEGIN;

-- Additional USA opening variants (v2–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  '7f2c1f2e-0c45-4f35-9b2e-31c1f0a0e021',
  'USA',
  'The United States welcomes the opportunity to participate in this working group and values the seriousness with which parties have approached the scientific assessment. The International Mercury Assessment provides a shared factual basis for discussion, and it is an appropriate place to begin.\n\nThe report makes two points clear. First, mercury is globally mobile and persistent, meaning that national actions alone cannot fully address its impacts. Second, while uncertainty remains, the overall body of evidence supports concern about continued anthropogenic emissions and their long-term effects on human health and ecosystems. The question before us is how to translate that evidence into effective cooperation.\n\nFor the United States, effectiveness depends on credibility. International commitments must be clear, measurable, and capable of implementation within domestic legal and institutional systems. Agreements that are ambitious on paper but vague in practice risk undermining confidence and compliance.\n\nThe United States therefore supports moving toward a structured international approach, while recognizing that flexibility will be essential. Countries differ in capacity, and responsibilities should reflect those differences. Phased implementation, technical cooperation, and transparency mechanisms can help bridge these gaps without weakening the overall framework.\n\nAt the same time, the United States does not believe that voluntary measures alone are sufficient. Experience with other persistent pollutants suggests that voluntary efforts, while useful, tend to produce uneven results. A credible international response requires shared expectations and accountability, even if those expectations are implemented in different ways.\n\nWe also see practical opportunities to make progress now. Reducing mercury use in products and industrial processes where alternatives exist can deliver tangible benefits and build trust. Improved emissions monitoring can strengthen future decision-making and reduce uncertainty over time.\n\nThe United States looks forward to working with partners to identify next steps that are realistic, science-based, and institutionally sound. Our goal should be an approach that countries can implement, sustain, and stand behind.',
  '{
    "summary":{
      "top_priorities":["credible and implementable international action","accountability and transparency"],
      "red_lines":["exclusive reliance on voluntary measures","agreements without measurable commitments"],
      "flexibilities":["phased implementation","capacity-based differentiation","technical cooperation"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.80},
      "ISSUE_2":{"preferred":"2.1","firmness":0.75},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","CHN","CHAIR"],
    "topics":[
      {"topic":"implementation and compliance","intent":"probe","details":"Discuss how commitments could be operationalized across different national systems."},
      {"topic":"phased commitments","intent":"offer","details":"Explore sequencing and differentiation to improve feasibility."},
      {"topic":"monitoring and reporting","intent":"ask","details":"Promote transparency as a foundation for trust."}
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
  '8f4d3b6c-6a1a-4c89-8b9b-4f6e2c1d5e32',
  'USA',
  'The United States approaches this working group with a strong interest in practical cooperation and lasting outcomes. Mercury presents a shared challenge, but the value of any international response will depend on whether it can be sustained over time.\n\nThe International Mercury Assessment shows that mercury persists in the environment, moves across borders, and accumulates in ways that raise legitimate concern. At the same time, it highlights uneven data quality and long timelines between action and observable results. These realities shape how policy must be designed if it is to endure.\n\nFor the United States, durability matters. International commitments that cannot be implemented consistently within domestic legal and political systems risk weakening, rather than strengthening, global cooperation. This is not a question of ambition versus caution. It is a question of building agreements that countries can maintain even as circumstances change.\n\nThe United States supports coordinated international action on mercury, particularly where evidence points to significant sources with global impact. However, we are cautious about approaches that rely on rigid obligations without clear pathways for implementation. Voluntary measures alone are unlikely to deliver consistent results, but binding commitments that outpace domestic capacity can also fail.\n\nWe see value in approaches that combine shared expectations with national discretion in how those expectations are met. Phased commitments, transparency, and support for implementation can create space for participation while preserving accountability.\n\nThere are also areas where progress is immediately achievable. Reducing mercury use in products and industrial processes where alternatives are available can yield concrete benefits and demonstrate momentum. Strengthening emissions monitoring can improve confidence in future decisions and help align policy with evidence.\n\nThe United States looks to this working group to identify options that balance responsibility with feasibility. Agreements that last are built not only on sound science, but on the ability of governments to stand behind them over time.',
  '{
    "summary":{
      "top_priorities":["durable international commitments","balance between accountability and feasibility"],
      "red_lines":["commitments that cannot be implemented domestically","purely voluntary approaches with no accountability"],
      "flexibilities":["phased commitments","national discretion in implementation","monitoring and transparency mechanisms"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.75},
      "ISSUE_2":{"preferred":"2.1","firmness":0.70},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.1","firmness":0.60}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","CHN"],
    "topics":[
      {"topic":"durability of commitments","intent":"probe","details":"Discuss how different frameworks hold up under domestic political constraints."},
      {"topic":"implementation pathways","intent":"ask","details":"Explore how commitments could be met flexibly while remaining credible."},
      {"topic":"near-term achievable actions","intent":"offer","details":"Identify steps that can deliver early results without overcommitting."}
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
  '9e5f4a7d-8b2c-4d9e-9c4f-5f7e3c2b6d43',
  'USA',
  'The United States approaches this working group with the view that progress is both possible and necessary. Mercury is not an abstract concern. Its persistence and global movement mean that decisions taken here will shape environmental and health outcomes well into the future.\n\nThe International Mercury Assessment outlines a problem that is technically complex but increasingly well understood. Mercury accumulates over time, crosses national boundaries, and imposes costs that are not evenly distributed. These characteristics point toward the need for shared solutions, even if those solutions take different forms across countries.\n\nThe United States believes that international cooperation works best when it is organized around clear goals and practical tools. Action on mercury should focus on sources that contribute most to global exposure and on measures that can be implemented, tracked, and improved over time. Progress does not require uniformity, but it does require direction.\n\nWe support moving toward an international framework that sets common expectations while allowing flexibility in how countries meet them. This approach can create momentum without forcing premature convergence. It can also encourage investment, innovation, and cooperation across borders.\n\nAt the same time, we recognize that leadership carries responsibility. Developed countries should be prepared to contribute expertise, technology, and support to ensure that action is achievable for all participants. Shared goals are more effective when matched with shared effort.\n\nThere are also immediate opportunities to demonstrate progress. Phasing down mercury use in products and industrial processes where alternatives are available can deliver visible results and reinforce confidence in collective action. Strengthening monitoring and reporting can further anchor future decisions in evidence rather than speculation.\n\nThe United States invites partners to focus on building a forward-looking pathway. The challenge before us is not only to assess the problem accurately, but to organize ourselves to address it effectively. We are ready to work with others to define that path.',
  '{
    "summary":{
      "top_priorities":["organized international cooperation","measurable reductions in global mercury exposure"],
      "red_lines":["fragmented approaches with no shared direction","commitments lacking follow-through mechanisms"],
      "flexibilities":["flexible implementation pathways","support for capacity building","iterative strengthening over time"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["EU","CAN","BRA","CHN"],
    "topics":[
      {"topic":"framework design","intent":"offer","details":"Discuss how shared expectations can coexist with national flexibility."},
      {"topic":"leadership contributions","intent":"offer","details":"Explore technology transfer and expertise-sharing from developed countries."},
      {"topic":"early action opportunities","intent":"probe","details":"Identify steps that can demonstrate momentum and credibility."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
