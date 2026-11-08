# Knowledge Outcomes Extension, v0.52

This additive extension retains the v0.38 graph and classification contracts. It adds no mandatory fields to unrelated events and makes no changes to cyber domain selection.

## Research Records

- `research_track`: `science`, `medicine`, `work`, or `education`.
- `research_candidate_id`: stable ID in the reviewed input package.
- `research_evidence_kind`, `research_outcome_stage`: authored method and outcome descriptors, not a universal quality ranking.
- `research_review_status`: input review scope. Values containing `pending` or `discrepancy` are displayed with a limited-review notice and `partially_verified` / C.
- `research_provenance`: full original bilingual candidate, including source access and review limits. This is an audit record, not a second graph node.
- `geo_roles`: optional developer organizations and countries, validation countries, data inputs, upstream models, bilingual access notes and interpretation limits. Fifteen records are profiled. Empty country arrays mean unassigned or multinational, not absence of activity. Developer affiliation does not establish ownership, sovereignty or deployment location.
- `mechanism_ru/en`: explicitly labelled interpretation, distinct from factual summary and caveats.

## Dates and Study Families

`date` remains the timeline anchor. `date_precision` retains day or month precision. Study periods, revision dates and announcement dates are independent fields.

`source_observation_not_publication` is used for Faros: the anchor is the documented page observation; `publication_date` is null and `date_status` is `publication_date_unknown`. This date must not be presented as the report's first release.

The QJE revision updates `SIG_2023_NBER_GENAI_TACIT_KNOWLEDGE`. Its original 2023 anchor remains. `research_revision_date` and `historical_versions` preserve the revised date and earlier source account/numbers. It is one study family, not two independent experiments.

## Story Structure

- `ARC_KNOWLEDGE_PRODUCTION_VALIDATION`: core mechanism.
- `ARC_MEDICAL_AI_TRANSLATION`: nested sector case under knowledge production.
- `ARC_EDUCATION_COMPETENCE`: nested sector case under knowledge production.
- `ARC_WORK_COMPETENCE_DISTRIBUTION`: nested sector case under corporate decision support.

Event-to-arc memberships use `part_of_arc` with `relationship_class: thematic`. Research comparisons and arc-to-thesis connections use `context_for` and explicitly editorial wording. None of the 76 added edges automatically confirms a thesis. Existing claims and claim checks are unchanged.

## Provenance and Reproduction

`researchAudit.knowledge_outcomes.candidate_mapping` covers all 53 inputs: 52 added events and one merged revision. `migrationAudit.v052_*` records additions, updates and pinned baseline hashes. The migration rejects a repeated run or an unreviewed input file.

Use `python3 tests/knowledge_outcomes_test.py` to replay against the pinned Git baseline and compare the exact current output. Use `python3 scripts/build.py` to regenerate the two standalone HTML files from current JSON. Source verification is not replaced by structural validation.
