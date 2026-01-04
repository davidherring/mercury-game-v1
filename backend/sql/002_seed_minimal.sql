BEGIN;

-- Roles
INSERT INTO roles (id, display_name, role_type, voting_power) VALUES
('BRA', 'Brazil', 'country', 1),
('CAN', 'Canada', 'country', 1),
('CHN', 'China', 'country', 1),
('EU', 'European Union', 'country', 1),
('TZA', 'Tanzania', 'country', 1),
('USA', 'United States', 'country', 1),
('AMAP', 'AMAP', 'ngo', 0),
('MFF', 'Mercury Free Future', 'ngo', 0),
('WCPA', 'World Conservation Policy Alliance', 'ngo', 0),
('JPN', 'Japan (Chair)', 'chair', 0);

-- Opening variants (placeholder text; initial stances are simple defaults)
INSERT INTO opening_variants (role_id, opening_text, initial_stances) VALUES
('BRA', 'Brazil opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('CAN', 'Canada opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('CHN', 'China opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('EU', 'EU opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('TZA', 'Tanzania opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('USA', 'United States opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('AMAP', 'AMAP opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('MFF', 'MFF opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}'),
('WCPA', 'WCPA opening placeholder.', '{"1":{"firmness":0.5,"acceptance":{}}, "2":{"firmness":0.5,"acceptance":{}}, "3":{"firmness":0.5,"acceptance":{}}, "4":{"firmness":0.5,"acceptance":{}}}');

-- Japan scripts (minimal starter set)
INSERT INTO japan_scripts (script_key, state, template) VALUES
('R1_OPEN', 'ROUND_1_OPENING_STATEMENTS', 'The Chair calls the meeting to order. We will begin opening statements.'),
('R1_CALL_SPEAKER', 'ROUND_1_OPENING_STATEMENTS', 'I recognize {speaker}.'),
('R2_INTERRUPT', 'ROUND_2_CONVERSATION_ACTIVE', 'The Chair interrupts. Please move to final statements.'),
('ISSUE_INTRO', 'ISSUE_INTRO', 'We now consider Issue {issue_id}: {issue_title}. The options are: {options_list}.'),
('PROPOSAL', 'ISSUE_PROPOSAL_SELECTION', 'The Chair proposes option {option_id} for adoption.'),
('VOTE_RESULT_PASS', 'ISSUE_VOTE', 'The proposal is adopted by unanimous consent.'),
('VOTE_RESULT_FAIL', 'ISSUE_VOTE', 'The proposal is not adopted (unanimity was not achieved).');

-- Approved IMA excerpts (placeholder)
INSERT INTO ima_excerpts (excerpt_key, content, source_ref, tags) VALUES
('IMA_SAMPLE', 'Approved excerpt placeholder from IMA.', 'IMA p.1', ARRAY['round2','round3']);

-- Issue definitions (canonical, Issue 1)
INSERT INTO issue_definitions (id, title, description, options) VALUES
('1',
 'If and how to regulate mercury emissions',
 'Is global action necessary to address mercury, and what form should action take?',
 '[
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
        "Often framed as \u201cevidence first\u201d: expand monitoring and inventories before committing to a treaty",
        "Politically attractive to countries with limited capacity or high dependence on emitting sectors, since targets are voluntary",
        "Criticized by NGOs and Arctic-focused actors as too weak to prevent ongoing harm and delays meaningful reductions"
      ]
    }
 ]'
)
ON CONFLICT (id) DO UPDATE SET
 title = EXCLUDED.title,
 description = EXCLUDED.description,
 options = EXCLUDED.options;

 INSERT INTO issue_definitions (id, title, description, options) VALUES
('2',
 'Inclusion of atmospheric mercury emissions',
 'Should atmospheric emissions of mercury be within the scope of a potential agreement?',
 '[
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
 ]'
)
ON CONFLICT (id) DO UPDATE SET
 title = EXCLUDED.title,
 description = EXCLUDED.description,
 options = EXCLUDED.options;

-- Issue definitions (canonical, Issue 3)
INSERT INTO issue_definitions (id, title, description, options) VALUES
('3',
 'Inclusion of mercury demand in products and processes',
 'Should global demand for products and processes be included within the scope of a potential agreement?',
 '[
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
 ]'
)
ON CONFLICT (id) DO UPDATE SET
 title = EXCLUDED.title,
 description = EXCLUDED.description,
 options = EXCLUDED.options;

-- Issue definitions (canonical, Issue 4)
INSERT INTO issue_definitions (id, title, description, options) VALUES
('4',
 'Inclusion of mercury emissions from artisanal and small-scale gold mining (ASGM)',
 'Should mercury emissions from artisanal and small-scale gold mining (ASGM) be included within the scope of a potential agreement?',
 '[
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
 ]'
)
ON CONFLICT (id) DO UPDATE SET
 title = EXCLUDED.title,
 description = EXCLUDED.description,
 options = EXCLUDED.options;

COMMIT;
