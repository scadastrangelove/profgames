# Schema notes — v0.37

## Scope

This additive release extends the frontier-pacing and continuity layer beyond the United States. All v0.36 IDs, dates and source URLs remain. It adds three events and 31 explicit edges; the number of claims, claim checks and story arcs does not change.

## Comparative mechanisms

The records and reused events deliberately preserve five different forms of control:

- `SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS` — voluntary developer thresholds for development and deployment;
- `SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS` — observed pre-deployment evaluator access without a general veto power;
- `SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE` — official implementation counts for a binding public-service filing regime;
- the existing EU record — statutory evaluation and public-availability powers under the AI Act;
- the existing South Korean records — provenance, supplier-control and domestic-capability programmes.

These are connected by a checkpoint mechanism, not by identical law, scope or effect. `artifact_kind`, `normative_force`, `implementation_stage`, `delegated_authority`, `status`, `confidence` and bilingual caveats remain separate fields.

## Pacing claim

`CLM_031_FRONTIER_PACING_AUTHORITY` remains `partially_verified`. Its scope now includes development tempo, deployment thresholds, pre-release observability, market or service access and continuity. It does not establish one global pacing regime or a measured reduction in worldwide training cadence.

`CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK` is updated to place these checkpoints within the five-part cyber-resilience frame without treating their existence as proof of effective implementation.

## Story arc and chronology

`ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL` keeps its ID and family. Its authored `key_nodes` now run from China's July 2023 Interim Measures through Seoul and UK AISI in 2024, then the 2026 Chinese, Korean, EU and U.S. events. The order is event chronology, not insertion order, and does not assert causation.

## Links

The release adds 31 edges:

- 16 `part_of_arc` thematic memberships, including five reused non-U.S. events;
- eight scoped evidence links into `CLM_031_FRONTIER_PACING_AUTHORITY`;
- seven editorial links that identify institutionalisation, prior art, parallels or context without asserting causation.

## Audit

`review/global-pacing-access-regimes/candidates.json` contains the bilingual source ledger, accepted records and deferred interpretations. `scripts/migrate_global_pacing_regimes.py` accepts only the pinned v0.36 bilingual checksums and validates reference, date and source preservation before writing either output.
