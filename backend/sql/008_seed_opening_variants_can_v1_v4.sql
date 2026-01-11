BEGIN;

-- Canada opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  '5a6b7c8d-9e0f-4a1b-b2c3-d4e5f6a7b801',
  'CAN',
  'Canada approaches this working group with a strong respect for scientific evidence and a practical interest in outcomes that can be implemented. Mercury pollution is a well-documented risk to human health and ecosystems, including in regions far from major sources.\n\nThe International Mercury Assessment shows how mercury travels long distances through the atmosphere and accumulates in food webs. These processes help explain why northern and Indigenous communities, despite contributing little to global emissions, face disproportionate exposure. This reality underscores the shared responsibility that connects national actions to global consequences.\n\nCanada supports international cooperation that is grounded in credible assessment and transparent reporting. Decisions should be informed by the best available evidence, while acknowledging areas of uncertainty. Where risks are clear and impacts are significant, action should follow.\n\nFrom Canada’s perspective, effective policy depends on practicality. Measures that are clear, monitorable, and adaptable over time are more likely to deliver lasting reductions than approaches that are overly rigid or disconnected from implementation capacity. Phased commitments and review mechanisms can help align ambition with feasibility.\n\nCanada also recognizes that countries face different circumstances. Support for capacity building, technology sharing, and information exchange can strengthen participation and improve outcomes without weakening collective goals.\n\nAt the same time, Canada believes that voluntary efforts alone are unlikely to address a problem with global pathways. Where evidence supports it, coordinated international measures are appropriate, particularly for sources that contribute to long-range transport.\n\nCanada invites partners to engage in a constructive, evidence-driven dialogue. By combining scientific clarity with practical cooperation, this working group can make meaningful progress on reducing mercury risks.',
  '{
    "summary":{
      "top_priorities":["evidence-based international action","reduction of long-range mercury transport"],
      "red_lines":["approaches that ignore scientific assessment","exclusive reliance on voluntary measures"],
      "flexibilities":["phased commitments","review and adjustment mechanisms","capacity and information support"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.70}
    }
  }'::jsonb,
  '{
    "targets":["USA","EU","BRA","TZA","AMAP"],
    "topics":[
      {"topic":"scientific assessment and monitoring","intent":"offer","details":"Promote shared data, reporting standards, and review processes."},
      {"topic":"long-range transport","intent":"probe","details":"Discuss sources contributing to cross-border mercury exposure."},
      {"topic":"capacity building","intent":"ask","details":"Explore support mechanisms that strengthen participation."}
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
  '6b7c8d9e-0f1a-4b2c-c3d4-e5f6a7b8c902',
  'CAN',
  'Canada approaches this working group with a focus on the lived consequences of mercury pollution. For many communities in the North, mercury exposure is not theoretical. It affects food security, health, and cultural practices that depend on aquatic ecosystems.\n\nThe International Mercury Assessment documents how mercury travels long distances and accumulates in food webs. These pathways explain why northern and Indigenous communities experience elevated exposure despite contributing little to global emissions. This imbalance highlights a fairness concern that must be taken seriously.\n\nFrom Canada’s perspective, international cooperation on mercury is a matter of shared responsibility. When pollutants cross borders and persist for decades, national actions are inseparable from global outcomes. Addressing these impacts requires collective measures that reflect this interdependence.\n\nCanada supports evidence-based action that reduces major sources of long-range transport. Atmospheric emissions are a particular concern, given their role in exposing distant regions. Where science indicates clear links between sources and impacts, coordinated international measures are justified.\n\nAt the same time, Canada recognizes that effective cooperation depends on trust and inclusion. Countries face different capacities and priorities, and progress will require support, transparency, and phased approaches that allow commitments to strengthen over time.\n\nCanada also sees value in improved monitoring and information sharing, particularly in regions that experience high exposure. Better data can inform policy choices, support communities, and strengthen confidence in collective action.\n\nCanada invites partners to consider mercury not only as an environmental issue, but as a question of equity. By reducing emissions that affect distant and vulnerable populations, this working group can deliver benefits that are both scientifically sound and socially just.',
  '{
    "summary":{
      "top_priorities":["protection of northern and Indigenous communities","reduction of long-range mercury transport"],
      "red_lines":["dismissal of cross-border impacts","approaches that externalize harm to vulnerable regions"],
      "flexibilities":["phased commitments","capacity and monitoring support","adaptive implementation timelines"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["USA","EU","CHN","AMAP"],
    "topics":[
      {"topic":"cross-border exposure","intent":"probe","details":"Link emission sources to impacts in distant regions."},
      {"topic":"equity and responsibility","intent":"ask","details":"Discuss how global action can address unequal burdens."},
      {"topic":"monitoring in high-exposure regions","intent":"offer","details":"Support data collection and community-informed assessment."}
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
  '7c8d9e0f-1a2b-4c3d-d4e5-f6a7b8c9d013',
  'CAN',
  'Canada approaches this working group with an interest in building common ground. Mercury presents a global challenge with shared pathways, but also with differing national perspectives on how best to respond. Progress will depend on whether those perspectives can be brought into constructive dialogue.\n\nThe International Mercury Assessment shows that mercury moves through the environment in complex ways. It also highlights uncertainty in the contribution of specific sources and variability in national circumstances. These findings suggest the value of cooperation that is deliberate and informed, rather than rushed or polarized.\n\nCanada believes that strong outcomes are most likely when parties have confidence in the process. Transparency, shared evidence, and opportunities to test options can help bridge differences and reduce mistrust. This is especially important when considering measures that may carry economic or political implications.\n\nFrom Canada’s perspective, international cooperation should begin with areas of overlap. Improving monitoring, sharing data, and strengthening reporting practices can build a common factual foundation. These steps can support more substantive decisions over time.\n\nCanada recognizes that some parties seek rapid movement toward binding commitments, while others emphasize caution. A durable agreement will need to respect both impulses. Phased approaches and review mechanisms offer one way to reconcile ambition with prudence.\n\nCanada does not see facilitation as neutrality. Where evidence points clearly to harm, action is warranted. At the same time, maintaining engagement among all major actors is essential if global pathways are to be addressed effectively.\n\nCanada invites partners to use this working group as a space for constructive exploration. By focusing on shared understanding and workable steps, participants can move closer to outcomes that command broad support.',
  '{
    "summary":{
      "top_priorities":["maintaining broad participation","building shared factual foundations"],
      "red_lines":["processes that entrench polarization","outcomes that exclude major emitters"],
      "flexibilities":["phased commitments","review-based escalation","procedural experimentation"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.80},
      "ISSUE_2":{"preferred":"2.1","firmness":0.75},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.60}
    }
  }'::jsonb,
  '{
    "targets":["USA","EU","CHN","BRA"],
    "topics":[
      {"topic":"process design","intent":"offer","details":"Explore sequencing and review mechanisms to bridge positions."},
      {"topic":"areas of overlap","intent":"probe","details":"Identify measures with broad preliminary support."},
      {"topic":"confidence building","intent":"ask","details":"Discuss steps that could maintain engagement among major actors."}
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
  '8d9e0f1a-2b3c-4d4e-e5f6-a7b8c9d0e124',
  'CAN',
  'Canada approaches this working group with an emphasis on implementation. International commitments matter most when they can be translated into clear policies, measurable outcomes, and sustained compliance.\n\nThe International Mercury Assessment underscores the value of inventories, monitoring, and transparent reporting in understanding mercury pathways and evaluating progress. Without these foundations, it is difficult to know whether policies are working or where adjustments are needed.\n\nCanada’s experience suggests that effective mercury controls rely on clarity. Measures that define expectations, support data collection, and allow for regular review are more likely to deliver real reductions than approaches that depend on broad principles alone. This is especially important for pollutants that persist and move across borders.\n\nCanada supports international cooperation that strengthens national implementation capacity. Shared methodologies, comparable reporting, and technical assistance can reduce uncertainty and build confidence among parties. These tools also make it easier to scale ambition over time.\n\nAt the same time, Canada recognizes that not all countries start from the same position. Implementation pathways must reflect differences in capacity and institutional readiness. Phased obligations and pilot approaches can help ensure that commitments remain credible and achievable.\n\nCanada does not view practicality as a constraint on ambition. Rather, it is the means by which ambition becomes durable. Where evidence supports stronger measures, implementation tools should be designed to support them.\n\nCanada invites partners to focus on how agreements will operate in practice. By grounding discussions in monitoring, reporting, and review, this working group can lay the groundwork for cooperation that delivers lasting results.',
  '{
    "summary":{
      "top_priorities":["credible implementation and compliance","monitoring and reporting frameworks"],
      "red_lines":["commitments without monitoring or review","ambition detached from implementation capacity"],
      "flexibilities":["phased obligations","pilot and review-based escalation","technical assistance and shared methods"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.80},
      "ISSUE_4":{"preferred":"4.1","firmness":0.75}
    }
  }'::jsonb,
  '{
    "targets":["USA","EU","BRA","AMAP"],
    "topics":[
      {"topic":"monitoring and reporting design","intent":"offer","details":"Share approaches for inventories, metrics, and review cycles."},
      {"topic":"implementation pathways","intent":"probe","details":"Assess what tools are needed to translate commitments into action."},
      {"topic":"technical assistance","intent":"ask","details":"Discuss how support can strengthen compliance and confidence."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
