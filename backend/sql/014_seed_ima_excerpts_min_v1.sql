BEGIN;

-- Sprint 20 Phase 3: minimal, auditable IMA evidence excerpts (8–12)
-- Notes:
-- - Data-only: no schema, prompt, or gameplay changes.
-- - Tags encode issue association (issue1–issue4) + usage (round3, evidence).
-- - We try to deactivate an existing placeholder row without knowing its key.

UPDATE ima_excerpts
SET is_active = false
WHERE excerpt_key ILIKE '%PLACEHOLDER%'
   OR content ILIKE '%placeholder%';

INSERT INTO ima_excerpts (excerpt_key, content, source_ref, tags, is_active)
VALUES
  (
    'IMA_MOBILIZED_FACTOR_3_5',
    'Although mercury is a naturally occurring heavy metal element, and has always been present in the environment, human activity has increased mobilized mercury by a factor of three to five. Once mobilized, mercury persists, cycling for centuries to millennia until it is sequestered in deep ocean sediments (1).',
    'IMA — Introduction, Reasons for concern',
    ARRAY['issue1','round3','evidence','persistence','global'],
    true
  ),
  (
    'IMA_ATMOS_LIFETIME_6_18_MONTHS',
    'In its gaseous elemental form, mercury has a long atmospheric lifetime of 6 to 18 months, allowing the element to be transported globally. Global transport is a key reason prompting international cooperation.',
    'IMA — Introduction, Reasons for concern',
    ARRAY['issue2','round3','evidence','transport','global'],
    true
  ),
  (
    'IMA_MEHG_BIOACCUM_1M',
    'Once mercury is converted to methylmercury, it is highly toxic and can bioaccumulate up the food chain, particularly in fish. MeHg can be present in predatory fish at 1,000,000 times the background level (3).',
    'IMA — Issue 1.1 What are mercury’s main human exposure pathways?',
    ARRAY['issue1','round3','evidence','health','bioaccumulation'],
    true
  ),
  (
    'IMA_EXPOSURE_FISH_PRIMARY',
    'Most human populations are exposed to methylmercury primarily through eating fish, with heightened exposure from eating fish at higher trophic levels.',
    'IMA — Issue 1.1 What are mercury’s main human exposure pathways?',
    ARRAY['issue1','round3','evidence','health','exposure'],
    true
  ),
  (
    'IMA_PLACENTA_BLOOD_BRAIN',
    'All mercury-containing compounds are readily passable through the placental and the blood-brain barrier. Mercury’s toxicity depends on its chemical form; the same exposure to elemental mercury and organic mercury compounds can produce different symptoms in the same patient.',
    'IMA — Issue 1.2 What are mercury’s health impacts and toxicity?',
    ARRAY['issue1','round3','evidence','health','toxicity'],
    true
  ),
  (
    'IMA_EMISSIONS_1930T_ONE_THIRD',
    'In 2005, global anthropogenic emissions to the atmosphere were estimated to be 1930 tonnes (range 1230–2890 tonnes). In summary, anthropogenic emissions, natural emissions and re-emissions each contribute approximately one-third of total annual emissions (22-25; Figure 4).',
    'IMA — Issue 2.1 What is the scale of atmospheric emissions?',
    ARRAY['issue2','round3','evidence','emissions','inventory'],
    true
  ),
  (
    'IMA_COAL_POWER_45_PERCENT',
    'Coal-fired power production, an unintentional release, is the single largest global source of atmospheric mercury emissions, accounting for approximately 45% of the total quantified atmospheric emissions from anthropogenic sources (23, 25).',
    'IMA — Issue 2.3 What are the sources of atmospheric emissions?',
    ARRAY['issue2','round3','evidence','coal','power'],
    true
  ),
  (
    'IMA_PRODUCTS_EXAMPLES',
    'Additional exposure occurs through mercury-containing skin-lightening creams, use in medicines and rituals and in dental products.',
    'IMA — Issue 1.1 What are mercury’s main human exposure pathways?',
    ARRAY['issue3','round3','evidence','products','demand','exposure'],
    true
  ),
  (
    'IMA_CHLOR_ALKALI_WORKERS',
    'Workers may be at an elevated risk of exposure to mercury in chlor-alkali plants, mercury mines, dental clinics and small-scale gold mines.',
    'IMA — Issue 1.1 What are mercury’s main human exposure pathways?',
    ARRAY['issue3','round3','evidence','processes','demand','workers'],
    true
  ),
  (
    'IMA_HG0_HGII_LIFETIMES',
    'In contrast to Hg(0), Hg(II) and Hg(P) have much shorter lifetimes in the atmosphere, on the order of days to weeks. As a result they do not tend to be transported long distances, and instead contribute to local and regional pollution.',
    'IMA — Issue 2.4 How is mercury transported in the atmosphere?',
    ARRAY['issue2','round3','evidence','transport','regional'],
    true
  )
ON CONFLICT (excerpt_key) DO UPDATE
SET content    = EXCLUDED.content,
    source_ref = EXCLUDED.source_ref,
    tags       = EXCLUDED.tags,
    is_active  = EXCLUDED.is_active;

COMMIT;
