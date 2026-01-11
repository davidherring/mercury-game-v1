BEGIN;

-- AMAP opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'aa1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c81',
  'AMAP',
  'The Arctic Monitoring and Assessment Programme participates in this discussion to share scientific findings on how mercury affects Arctic environments and communities. Our role is not to advocate for particular national positions, but to ensure that decisions are informed by the best available evidence.\n\nThe International Mercury Assessment and related Arctic research show that mercury released far from the Arctic is transported through the atmosphere and oceans, accumulating in cold regions. These processes lead to elevated concentrations in marine food webs and create exposure risks for Indigenous and northern communities that rely on traditional diets.\n\nThese impacts are well documented and persistent. Mercury deposited in the Arctic remains in circulation for long periods, compounding past emissions with current ones. This means that choices made today will influence exposure for decades to come.\n\nFrom a scientific perspective, the Arctic illustrates the global nature of mercury pollution. Local controls alone cannot protect regions that receive contaminants from distant sources. Reductions in major emitting activities therefore have direct relevance for Arctic health and ecosystems, even when those activities occur elsewhere.\n\nAMAP recognizes that countries differ in capacity and responsibility. Our contribution is to clarify where evidence is strong, where uncertainties remain, and how different sources contribute to observed impacts. This information can support balanced decisions that take both effectiveness and feasibility into account.\n\nWe encourage participants to consider the Arctic as an early warning system. Changes observed there often signal broader global risks. Addressing mercury at its sources can reduce harm not only in the Arctic, but across interconnected ecosystems worldwide.\n\nAMAP stands ready to provide further assessment and technical input to support informed and constructive dialogue throughout this process.',
  '{
    "summary":{
      "top_priorities":["use of scientific evidence in decision making","reduction of long-range mercury transport"],
      "red_lines":["dismissal of well-established Arctic impacts","policy decisions that ignore long-range transport"],
      "flexibilities":["phased emission reductions","science-informed differentiation","adaptive policy design"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["CAN","EU","USA","CHN"],
    "topics":[
      {"topic":"long-range transport evidence","intent":"offer","details":"Share findings linking distant emissions to Arctic exposure."},
      {"topic":"Arctic impacts","intent":"probe","details":"Encourage recognition of disproportionate northern effects."},
      {"topic":"science-policy integration","intent":"ask","details":"Discuss how assessment results can inform policy choices."}
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
  'bb2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d92',
  'AMAP',
  'The Arctic Monitoring and Assessment Programme participates in this process to convey a clear message from the scientific record. Mercury pollution is already producing measurable harm in the Arctic, and those impacts are not hypothetical or distant.\n\nAssessments summarized in the International Mercury Assessment show that mercury emitted far from the Arctic is transported efficiently through the atmosphere and oceans. Once deposited in cold regions, mercury accumulates in food webs and persists over long timeframes. These processes have resulted in elevated exposure for Arctic wildlife and for Indigenous communities that depend on marine resources.\n\nFrom a scientific standpoint, the Arctic functions as an early indicator. Changes observed there often precede or magnify trends that later appear elsewhere. The presence of mercury in Arctic ecosystems therefore signals broader global risks, not a localized concern.\n\nThe evidence indicates that continued emissions will compound existing burdens. Past releases have not dissipated. They remain in circulation, interacting with new inputs. Decisions to delay action increase the scale and duration of future exposure.\n\nAMAP recognizes that policy decisions must account for feasibility and national circumstances. However, the scientific findings also make clear that incremental or voluntary measures alone are unlikely to reverse observed trends in remote regions. Meaningful reductions in major emission sources are necessary to prevent further accumulation.\n\nThe Arctic experience underscores a central point. Regions with little influence over global emissions can nonetheless bear disproportionate consequences. This imbalance should inform discussions of responsibility and urgency.\n\nAMAP encourages participants to treat Arctic findings as a warning grounded in evidence. Acting earlier, rather than later, reduces long-term risk and limits irreversible harm. We remain available to provide further data and analysis as deliberations continue.',
  '{
    "summary":{
      "top_priorities":["recognition of Arctic early-warning signals","reduction of major emission sources"],
      "red_lines":["minimization of documented Arctic harm","reliance on voluntary action despite clear evidence"],
      "flexibilities":["phased but meaningful emission reductions","science-guided differentiation","adaptive policy mechanisms"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.90},
      "ISSUE_2":{"preferred":"2.1","firmness":0.85},
      "ISSUE_3":{"preferred":"3.2","firmness":0.70},
      "ISSUE_4":{"preferred":"4.1","firmness":0.65}
    }
  }'::jsonb,
  '{
    "targets":["CAN","EU","USA","CHN"],
    "topics":[
      {"topic":"early warning evidence","intent":"offer","details":"Present Arctic trends as indicators of broader global risk."},
      {"topic":"urgency of action","intent":"probe","details":"Challenge assumptions that delay carries low cost."},
      {"topic":"responsibility for remote impacts","intent":"ask","details":"Encourage acknowledgment of disproportionate Arctic burdens."}
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
  'cc3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6ea3',
  'AMAP',
  'The Arctic Monitoring and Assessment Programme contributes to this discussion by clarifying what the scientific evidence shows and where its limits remain. Sound decisions depend not only on recognizing risks, but also on understanding uncertainty.\n\nThe International Mercury Assessment documents long-range transport of mercury to the Arctic and its accumulation in food webs. These findings are well supported. At the same time, the assessment also notes variability in deposition patterns and uncertainty in attributing observed concentrations to specific sources or sectors.\n\nFrom a scientific perspective, distinguishing strong conclusions from areas of uncertainty strengthens, rather than weakens, policy. Overstating precision can undermine credibility and erode trust, particularly when measures carry economic or social implications.\n\nAMAP’s role is to provide a clear account of evidence quality. In some cases, trends are robust across datasets. In others, gaps in monitoring or limited historical data make causal claims more tentative. Recognizing these distinctions allows policymakers to match responses to confidence levels.\n\nThe Arctic experience still demonstrates the global reach of mercury pollution. However, uncertainty remains regarding the relative effectiveness of different control pathways and timelines. Continued monitoring and targeted research are therefore essential components of any long-term strategy.\n\nAMAP encourages approaches that remain adaptable. Policies that include review mechanisms, updated assessments, and learning over time can respond to new evidence without locking in assumptions prematurely.\n\nBy grounding discussions in both what is known and what remains uncertain, participants can design responses that are credible, proportionate, and resilient. AMAP stands ready to support this process through ongoing assessment and technical input.',
  '{
    "summary":{
      "top_priorities":["accurate interpretation of scientific evidence","policy designs that account for uncertainty"],
      "red_lines":["overstated scientific certainty","irreversible commitments unsupported by evidence"],
      "flexibilities":["adaptive management approaches","review-based escalation","expanded monitoring and research"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.80},
      "ISSUE_2":{"preferred":"2.1","firmness":0.75},
      "ISSUE_3":{"preferred":"3.2","firmness":0.65},
      "ISSUE_4":{"preferred":"4.1","firmness":0.60}
    }
  }'::jsonb,
  '{
    "targets":["CAN","EU","USA","CHN"],
    "topics":[
      {"topic":"evidence boundaries","intent":"offer","details":"Clarify which findings are robust and which remain uncertain."},
      {"topic":"adaptive policy design","intent":"ask","details":"Discuss mechanisms that allow adjustment as evidence evolves."},
      {"topic":"monitoring gaps","intent":"probe","details":"Identify areas where additional data would improve confidence."}
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
  'dd4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7fb4',
  'AMAP',
  'The Arctic Monitoring and Assessment Programme engages in this discussion with a focus on what comes after commitments are made. Evidence matters not only for setting direction, but for determining whether actions taken are producing real change.\n\nMonitoring in the Arctic provides one of the clearest signals of whether global mercury controls are effective. Because the region integrates emissions from many sources, changes observed there can indicate whether policies are reducing overall loading rather than shifting it geographically.\n\nThe International Mercury Assessment highlights the importance of sustained observation. Reductions in emissions do not immediately translate into lower concentrations in ecosystems. Without consistent monitoring, it becomes difficult to distinguish between delayed responses, ineffective measures, and incomplete implementation.\n\nFrom a scientific standpoint, credibility depends on follow-through. Ambitious decisions that cannot be evaluated risk weakening confidence in the process. Clear indicators, transparent reporting, and regular assessment allow parties to learn what is working and what requires adjustment.\n\nAMAP does not prescribe specific policy choices. Our role is to help ensure that whatever options are selected can be assessed against observable outcomes. This includes identifying indicators that are sensitive to change, comparable across time, and meaningful for human and ecological health.\n\nThe Arctic experience demonstrates that long-range pollution problems require patience as well as persistence. Progress should be judged through evidence collected over time, not solely through initial commitments.\n\nAMAP invites participants to consider how monitoring and review can be integrated into their decisions from the outset. Doing so strengthens accountability and supports durable cooperation grounded in measurable results.',
  '{
    "summary":{
      "top_priorities":["measurable policy effectiveness","integration of monitoring and review"],
      "red_lines":["commitments without evaluation mechanisms","decisions that preclude learning or adjustment"],
      "flexibilities":["review-based escalation","indicator-driven assessment","iterative policy refinement"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.1","firmness":0.85},
      "ISSUE_2":{"preferred":"2.1","firmness":0.80},
      "ISSUE_3":{"preferred":"3.2","firmness":0.75},
      "ISSUE_4":{"preferred":"4.1","firmness":0.70}
    }
  }'::jsonb,
  '{
    "targets":["CAN","EU","USA","CHN"],
    "topics":[
      {"topic":"monitoring indicators","intent":"offer","details":"Propose Arctic-linked indicators to track global effectiveness."},
      {"topic":"review cycles","intent":"ask","details":"Discuss how assessment and reporting can be embedded in decisions."},
      {"topic":"implementation learning","intent":"probe","details":"Explore how monitoring results could inform future adjustments."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
