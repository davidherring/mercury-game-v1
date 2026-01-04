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

COMMIT;
