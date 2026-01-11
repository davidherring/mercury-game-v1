BEGIN;

-- Tanzania opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  '9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c41',
  'TZA',
  'Tanzania approaches this working group with a clear view of how mercury affects communities on the ground. In our country, mercury use is closely linked to artisanal and small-scale gold mining, which provides income for many families but also creates serious risks to health and the environment.\n\nThe International Mercury Assessment shows that exposure in mining communities can be severe, particularly where mercury is handled informally and without adequate safeguards. These risks are real and immediate. They affect miners, families, and nearby ecosystems, and they deserve careful attention.\n\nTanzania supports international cooperation on mercury where it helps reduce these harms in practical ways. Education, safer mining practices, and access to appropriate technologies can make a meaningful difference. Progress in these areas depends on sustained support and partnership, not on measures that overlook local realities.\n\nFrom Tanzania’s perspective, effective action must recognize development challenges. Many mercury-related activities are driven by poverty and limited economic alternatives. Addressing mercury without addressing livelihoods risks pushing harmful practices further out of sight rather than eliminating them.\n\nTanzania is open to participating in broader discussions on mercury transport and global impacts, while noting that our priority remains reducing direct exposure in affected communities. International measures should reflect different national circumstances and allow countries to move forward at a pace that matches their capacity.\n\nTanzania also sees value in regional cooperation. Shared experiences across East Africa provide opportunities for learning and coordinated action, particularly in monitoring, training, and technology exchange.\n\nTanzania invites partners to focus on cooperation that delivers tangible improvements for people and environments most affected by mercury. By aligning international efforts with local needs, this working group can support progress that is both effective and equitable.',
  '{
    "summary":{
      "top_priorities":["reduction of mercury exposure in ASGM communities","development-aligned risk mitigation"],
      "red_lines":["measures that undermine livelihoods without alternatives","binding commitments without implementation support"],
      "flexibilities":["phased commitments","capacity building and training","technology transfer and education"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.60},
      "ISSUE_2":{"preferred":"2.2","firmness":0.55},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.1","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["BRA","AMAP","WCAP","EU","CAN"],
    "topics":[
      {"topic":"ASGM safety and transition","intent":"ask","details":"Seek support for safer practices, training, and alternatives."},
      {"topic":"capacity building","intent":"offer","details":"Share experiences from East African contexts."},
      {"topic":"regional cooperation","intent":"probe","details":"Explore coordinated approaches across neighboring countries."}
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
  '0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d52',
  'TZA',
  'Across East Africa, countries are confronting similar challenges linked to mercury use in artisanal and small-scale gold mining. Tanzania enters this discussion with the view that these shared conditions create an opportunity for coordinated solutions.\n\nThe International Mercury Assessment shows that mercury exposure in mining communities remains high where practices are informal and resources are limited. These conditions are not unique to any one country. They reflect regional patterns that call for cooperation rather than isolated responses.\n\nTanzania believes that regional coordination can strengthen national efforts. Training programs, technology pilots, and monitoring systems can be more effective when they are developed collaboratively and adapted to local contexts. Sharing experience across borders reduces duplication and builds confidence.\n\nInternational cooperation is most helpful when it reinforces these regional efforts. Support that flows through partnerships, regional centers, and peer networks can reach communities more effectively than one-size-fits-all mandates. This approach also respects national sovereignty while promoting shared progress.\n\nTanzania remains focused on reducing direct exposure in mining communities. Safer practices, education, and access to alternatives are immediate priorities. These goals are best served through practical assistance and sustained engagement rather than rapid regulatory escalation.\n\nAt the same time, Tanzania recognizes that mercury has broader environmental pathways. Regional coordination can also contribute to improved data and understanding of these impacts, creating a stronger foundation for future discussions at the global level.\n\nTanzania invites partners to support regionally grounded cooperation. By strengthening coordination across East Africa, this working group can help reduce mercury risks in ways that are realistic, durable, and aligned with development needs.',
  '{
    "summary":{
      "top_priorities":["regional coordination on ASGM risk reduction","strengthening shared capacity and learning"],
      "red_lines":["isolated national mandates without regional support","binding obligations that bypass regional institutions"],
      "flexibilities":["regionally coordinated measures","phased implementation","peer-based training and support"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.65},
      "ISSUE_2":{"preferred":"2.2","firmness":0.60},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.85}
    }
  }'::jsonb,
  '{
    "targets":["BRA","AMAP","WCAP","CAN","EU"],
    "topics":[
      {"topic":"regional training networks","intent":"offer","details":"Coordinate ASGM safety and technology programs across East Africa."},
      {"topic":"shared monitoring","intent":"ask","details":"Seek support for regional data collection and analysis."},
      {"topic":"peer learning","intent":"probe","details":"Exchange lessons learned among countries with similar conditions."}
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
  '1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e63',
  'TZA',
  'For Tanzania, mercury is first and foremost a health issue. Exposure affects miners who handle mercury directly, families who live near processing sites, and children whose development is put at risk by contaminated environments.\n\nThe International Mercury Assessment documents how informal mercury use leads to direct inhalation and contact, often without protective measures. These exposures are immediate and severe. They do not wait for long-range transport or global accumulation to cause harm.\n\nTanzania’s priority is to reduce these risks where they are most acute. Safer handling practices, education, and access to alternatives can prevent illness and injury today. These measures are practical, proven, and urgently needed.\n\nInternational cooperation plays an important role when it supports these goals. Training programs, medical awareness, and appropriate technologies can reduce exposure quickly when they are delivered in ways that communities can adopt. Support that remains abstract or distant from affected populations is less effective.\n\nTanzania recognizes that mercury also has broader environmental pathways. However, policies that focus primarily on distant impacts while neglecting direct exposure miss the most pressing problem facing many communities. Health protection must remain central.\n\nTanzania is prepared to engage in broader discussions as understanding improves and capacity grows. For now, the measure of success should be whether fewer people are exposed and fewer families face preventable harm.\n\nTanzania invites partners to treat mercury reduction as a public health intervention. By focusing on immediate exposure and practical prevention, this working group can deliver results that are visible, credible, and life-changing.',
  '{
    "summary":{
      "top_priorities":["reduction of direct human exposure","protection of vulnerable populations"],
      "red_lines":["policies that ignore immediate health risks","abstract commitments without on-the-ground impact"],
      "flexibilities":["health-focused interventions","education and awareness programs","phased engagement on broader measures"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.55},
      "ISSUE_2":{"preferred":"2.2","firmness":0.50},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.1","firmness":0.95}
    }
  }'::jsonb,
  '{
    "targets":["AMAP","WCAP","CAN","EU"],
    "topics":[
      {"topic":"health interventions","intent":"ask","details":"Seek support for exposure reduction and medical awareness."},
      {"topic":"community education","intent":"offer","details":"Share experiences from health-focused ASGM programs."},
      {"topic":"measuring health outcomes","intent":"probe","details":"Discuss indicators that reflect real reductions in exposure."}
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
  '2d3e4f5a-6b7c-8d9e-0f1a-2b3c4d5e6f74',
  'TZA',
  'Tanzania joins this discussion with an emphasis on fairness and shared responsibility. Mercury pollution is a global problem, but its causes and consequences are not evenly distributed.\n\nIn countries like Tanzania, mercury use is closely tied to informal economic activity and limited alternatives. Communities facing the greatest exposure often contribute the least to global emissions and have the fewest resources to manage the risks. Any effective response must begin from this reality.\n\nThe International Mercury Assessment shows that while mercury travels globally, its impacts are shaped by local conditions. Policies that ignore these differences risk placing disproportionate burdens on those least able to absorb them.\n\nTanzania supports international cooperation that reflects differentiated responsibility. Developing countries should not be asked to shoulder obligations without commensurate support. Capacity building, technology access, and financial assistance are essential components of any credible framework.\n\nTanzania is prepared to work alongside other countries that share these constraints to advance practical solutions. Collective voices can help ensure that global measures remain grounded, equitable, and focused on real risk reduction rather than symbolic commitments.\n\nAt the same time, Tanzania does not reject ambition. We recognize the need to reduce mercury risks over time, including through improved practices and gradual transitions. Ambition must, however, be matched to capacity and delivered through partnership.\n\nTanzania invites partners to engage with developing countries as collaborators rather than recipients. By aligning expectations with support and respecting different starting points, this working group can build solutions that endure.',
  '{
    "summary":{
      "top_priorities":["equitable burden sharing","capacity-supported mercury reduction"],
      "red_lines":["uniform obligations without support","frameworks that shift costs onto low-capacity countries"],
      "flexibilities":["coalition-based approaches","phased commitments tied to assistance","voluntary measures that strengthen over time"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.2","firmness":0.60},
      "ISSUE_2":{"preferred":"2.2","firmness":0.55},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.1","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["BRA","AMAP","WCAP","EU","CAN"],
    "topics":[
      {"topic":"differentiated responsibility","intent":"ask","details":"Clarify how support will match expected commitments."},
      {"topic":"coalition coordination","intent":"offer","details":"Align positions among countries with similar constraints."},
      {"topic":"support mechanisms","intent":"probe","details":"Assess reliability and accessibility of assistance channels."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
