# Schema notes — v0.36

## Scope

This additive release maps frontier-model pacing and continuity of access into the structural-power graph. All v0.35 node IDs, event dates and source URLs remain. It adds five events, one claim check, one story arc and 35 explicit edges.

## Evidence classes

The five records deliberately preserve different forms of authority:

- `SIG_2026_DOW_AI_STRATEGY_SPEED_WINS` — binding internal military strategy;
- `SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL` — binding presidential memorandum for the national-security enterprise;
- `SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL` — first-party policy proposal;
- `SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS` — public commitments of unequal specificity;
- `SIG_2026_TRUMP_REJECTS_FRONTIER_PACING` — reported political position, not a new legal instrument.

`artifact_kind`, `normative_force`, `implementation_stage`, `status`, `confidence` and bilingual caveats must not be collapsed into a single governance status. The 30-day update target and NSPM-11 contract controls are directions whose implementation still needs evidence.

## Pacing claim

`CLM_031_FRONTIER_PACING_AUTHORITY` is a `partially_verified` claim check. It distinguishes two opposing forms of authority: a laboratory's ability to pause training or condition release, and a state's ability to demand speed, supplier replaceability and continuity of access. It does not establish a common industry schedule, a global pacing regime or complete state control.

The existing `export-14` claim qualifies the result with judicial limits on executive authority. `CLM_026_DECISION_SOVEREIGNTY_MITIGATION` and `CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK` are updated without changing their IDs.

## Story arc and chronology

`ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL` orders its authored `key_nodes` by event time: January strategy, June memorandum and model-control action, August training pause and court ruling, then the September proposal, endorsements and presidential response. The order is not insertion order and does not by itself assert causation.

The arc belongs to `ARC_FAMILY_ACCESS_CONTROL` and reaches `THESIS_ACCESS_AS_POWER`, `THESIS_DECISION_SOVEREIGNTY` and `THESIS_CORE` through the scoped claim check.

## Links

The release adds 35 edges:

- 17 `part_of_arc` thematic memberships;
- six scoped or claim-only evidence links into the new claim check;
- one judicial qualification;
- four links from the claim to its arc and thesis nodes;
- one update to decision sovereignty;
- six editorial chronology or opposition links.

Thematic and editorial links are not factual corroboration. `precedes_and_qualifies`, `context_for`, `develops_into` and `countermove` describe the authored reading path within their summaries.

## Audit

`review/frontier-pacing-september-2026/candidates.json` contains the bilingual source ledger, accepted records and deferred interpretations. `scripts/migrate_frontier_pacing.py` accepts only the pinned v0.35 bilingual checksums and validates reference, date and source preservation before writing either output.
