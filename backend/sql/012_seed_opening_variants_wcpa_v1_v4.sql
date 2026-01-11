BEGIN;

-- WCPA opening variants (v1–v4), idempotent upserts
INSERT INTO opening_variants (id, role_id, opening_text, initial_stances, conversation_interests)
VALUES
(
  'c1d2e3f4-5a6b-7c8d-9e0f-1a2b3c4d5e61',
  'WCPA',
  'The World Coal Power Association participates in this process to contribute a practical perspective on mercury management in the power sector. Coal-fired electricity remains a major source of reliable and affordable energy in many regions, particularly where alternatives are limited or still developing.\n\nThe International Mercury Assessment identifies coal combustion as a source of mercury emissions. It also shows that emission levels vary widely depending on plant design, fuel characteristics, and control technologies. This variability matters. It means outcomes are shaped by how facilities operate, not simply by their existence.\n\nFrom our perspective, the most effective path forward is to focus on performance improvements. Modern pollution control technologies can substantially reduce mercury emissions when they are properly implemented and maintained. Encouraging their deployment delivers real reductions without compromising energy security.\n\nWCAP recognizes the importance of protecting human health and the environment. At the same time, abrupt policy shifts that ignore economic and infrastructure realities risk unintended consequences, including reduced electricity access and higher costs for consumers.\n\nA balanced approach emphasizes achievable standards, technology transfer, and continuous improvement. Such approaches allow countries to reduce emissions while maintaining stable power systems and supporting economic development.\n\nWCAP does not oppose progress. We support policies that are grounded in technical feasibility and that recognize different starting points across regions. Flexibility in how reductions are achieved encourages innovation and avoids locking countries into unworkable commitments.\n\nWe encourage delegates to consider solutions that deliver measurable reductions through realistic pathways. By aligning environmental goals with operational realities, this process can advance both public health and energy reliability.',
  '{
    "summary":{
      "top_priorities":["cost-effective emission controls","energy reliability and affordability"],
      "red_lines":["mandatory phase-out of coal power","policies that undermine grid stability"],
      "flexibilities":["technology-based standards","incremental emission reductions","differentiated implementation timelines"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.3","firmness":0.85},
      "ISSUE_2":{"preferred":"2.2","firmness":0.80},
      "ISSUE_3":{"preferred":"3.3","firmness":0.75},
      "ISSUE_4":{"preferred":"4.2","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["USA","CHN","EU","CAN"],
    "topics":[
      {"topic":"control technologies","intent":"offer","details":"Share evidence on achievable mercury reductions from existing technologies."},
      {"topic":"energy system impacts","intent":"probe","details":"Examine risks of rapid transitions for electricity reliability."},
      {"topic":"implementation flexibility","intent":"ask","details":"Advocate for standards that allow multiple compliance pathways."}
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
  'd2e3f4a5-6b7c-8d9e-0f1a-2b3c4d5e6f72',
  'WCPA',
  'The World Coal Power Association participates in this negotiation to raise a practical concern. Policies that address mercury must be judged not only by intent, but by proportionality and real-world impact.\n\nCoal-fired power continues to supply electricity to millions of households and industries. In many regions, it underpins hospitals, water systems, and economic activity. Any approach that treats coal generation as easily replaceable risks overlooking these dependencies.\n\nThe International Mercury Assessment identifies coal combustion as a contributor to mercury emissions. It also shows that control costs and effectiveness vary widely. Beyond a certain point, additional controls yield smaller reductions at significantly higher cost. This reality matters when resources are limited and competing health priorities exist.\n\nFrom our perspective, cost effectiveness is not an obstacle to environmental protection. It is a requirement for sustainable policy. Measures that impose high costs for modest gains can divert resources from interventions that would deliver greater overall benefit.\n\nWCAP supports emission reductions where they can be achieved efficiently. Performance-based standards and best-available technologies have already demonstrated meaningful progress in many facilities. Expanding these approaches delivers results without destabilizing power systems or imposing unnecessary burdens on consumers.\n\nWe caution against frameworks that mandate uniform outcomes without regard to national circumstances or system constraints. Flexibility in compliance pathways allows countries to balance environmental objectives with development and energy needs.\n\nWCAP urges delegates to assess proposals through a lens of realism. Effective mercury reduction should improve health outcomes while preserving affordable and reliable electricity. Policies that fail this balance risk losing both public support and long-term viability.',
  '{
    "summary":{
      "top_priorities":["cost-effective mercury controls","protection of energy affordability"],
      "red_lines":["high-cost mandates with limited benefit","policies that jeopardize electricity access"],
      "flexibilities":["performance-based standards","technology-driven compliance","nationally tailored implementation"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.3","firmness":0.90},
      "ISSUE_2":{"preferred":"2.2","firmness":0.85},
      "ISSUE_3":{"preferred":"3.3","firmness":0.80},
      "ISSUE_4":{"preferred":"4.2","firmness":0.95}
    }
  }'::jsonb,
  '{
    "targets":["USA","CHN","EU","CAN"],
    "topics":[
      {"topic":"cost-benefit tradeoffs","intent":"probe","details":"Question proportionality of proposed mercury controls."},
      {"topic":"energy affordability","intent":"ask","details":"Press delegates to account for consumer and system impacts."},
      {"topic":"efficient technologies","intent":"offer","details":"Highlight controls that deliver reductions at lower cost."}
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
  'e3f4a5b6-7c8d-9e0f-1a2b-3c4d5e6f7a83',
  'WCPA',
  'The World Coal Power Association participates in this discussion to emphasize a constructive opportunity. Mercury reductions in the power sector are increasingly a question of technology deployment rather than structural prohibition.\n\nCoal-fired facilities today are not uniform. Modern plants equipped with advanced air pollution controls operate very differently from older installations. Integrated systems designed to address sulfur dioxide, particulates, and other pollutants can also deliver significant mercury reductions as a co-benefit.\n\nThe International Mercury Assessment documents this interaction. Where plants invest in modern controls and optimized operations, mercury emissions decline alongside other pollutants. This experience suggests that progress does not require abandoning existing infrastructure overnight.\n\nFrom our perspective, innovation changes the policy landscape. As technologies improve and costs fall, higher performance becomes more achievable. Policies that encourage modernization accelerate this process, while rigid mandates can slow adoption by creating uncertainty and resistance.\n\nWCAP supports approaches that reward improvement and diffusion of best practices. Technology transfer, financing mechanisms, and operational standards can raise performance across regions with very different starting points.\n\nWe recognize concerns about long-term environmental and health impacts. Addressing those concerns effectively requires pathways that operators can implement and maintain. Solutions that align environmental goals with engineering realities are more likely to endure.\n\nWCAP encourages delegates to focus on how innovation can deliver shared gains. By treating mercury reduction as part of a broader modernization effort, this process can achieve measurable progress while supporting energy systems that remain reliable and affordable.',
  '{
    "summary":{
      "top_priorities":["technology-driven mercury reductions","modernization of existing power infrastructure"],
      "red_lines":["blanket bans on coal power","policies that discourage investment in upgrades"],
      "flexibilities":["technology incentives","performance benchmarking","international technology transfer"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.3","firmness":0.85},
      "ISSUE_2":{"preferred":"2.2","firmness":0.80},
      "ISSUE_3":{"preferred":"3.3","firmness":0.75},
      "ISSUE_4":{"preferred":"4.2","firmness":0.90}
    }
  }'::jsonb,
  '{
    "targets":["USA","CHN","EU","CAN"],
    "topics":[
      {"topic":"technology modernization","intent":"offer","details":"Highlight co-benefits of advanced pollution controls."},
      {"topic":"innovation incentives","intent":"ask","details":"Promote policies that reward investment in upgrades."},
      {"topic":"technology transfer","intent":"probe","details":"Discuss mechanisms to scale modern controls globally."}
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
  'f4a5b6c7-8d9e-0f1a-2b3c-4d5e6f7a8b94',
  'WCPA',
  'The World Coal Power Association participates in this negotiation to underscore a broader consideration. Energy systems are foundational to public welfare, and decisions that affect them carry consequences beyond any single pollutant.\n\nCoal-fired power continues to play a stabilizing role in electricity systems around the world. In many regions, it provides dependable baseload generation that supports hospitals, industry, water treatment, and daily life. These functions are not easily substituted in the near term.\n\nThe International Mercury Assessment identifies coal combustion as a source of mercury emissions. It also reflects the reality that emission reduction strategies intersect with infrastructure, fuel supply, and grid reliability. Addressing mercury in isolation from these factors risks creating new vulnerabilities.\n\nFrom our perspective, energy security is inseparable from public health. Power disruptions and unaffordable electricity impose real costs on communities, often affecting the most vulnerable first. Policies that underestimate these risks can undermine the very protections they seek to advance.\n\nWCAP supports emission reductions that strengthen, rather than weaken, energy systems. Incremental improvements, operational optimization, and realistic timelines allow progress while preserving stability. Abrupt mandates that force premature shutdowns or constrain dispatch options threaten reliability.\n\nWe recognize the long-term need to evolve energy systems. That evolution must be managed in a way that avoids shocks and maintains essential services. A measured transition protects both environmental and social outcomes.\n\nWCAP urges delegates to evaluate proposals through a system-wide lens. Effective mercury policy should reduce harm without introducing new risks to energy security and economic resilience.',
  '{
    "summary":{
      "top_priorities":["energy system stability","managed and predictable transition"],
      "red_lines":["policies that trigger power instability","forced plant closures without viable alternatives"],
      "flexibilities":["gradual compliance timelines","system-aware standards","integration with broader energy planning"]
    },
    "by_issue_id":{
      "ISSUE_1":{"preferred":"1.3","firmness":0.85},
      "ISSUE_2":{"preferred":"2.2","firmness":0.85},
      "ISSUE_3":{"preferred":"3.3","firmness":0.80},
      "ISSUE_4":{"preferred":"4.2","firmness":0.95}
    }
  }'::jsonb,
  '{
    "targets":["USA","CHN","EU","CAN"],
    "topics":[
      {"topic":"grid stability risks","intent":"probe","details":"Examine how proposed measures affect power system reliability."},
      {"topic":"transition planning","intent":"ask","details":"Press for coordinated timelines aligned with infrastructure readiness."},
      {"topic":"system-wide impacts","intent":"offer","details":"Share analysis on energy security implications of rapid change."}
    ]
  }'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  role_id = EXCLUDED.role_id,
  opening_text = EXCLUDED.opening_text,
  initial_stances = EXCLUDED.initial_stances,
  conversation_interests = EXCLUDED.conversation_interests;

COMMIT;
