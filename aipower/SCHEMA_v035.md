# Schema notes — v0.35

## Scope

This additive release maps Anthropic's September 2026 threat-intelligence report into both the cyber framework and the wider structural-power graph. All v0.34 node IDs, event dates and source URLs remain. No top-level domain or story arc is added.

## New evidence boundary

Seven records separate mechanisms that the source report combines:

- provider observability and account enforcement;
- adaptive malware rebuilding after detection;
- persistent multi-agent vulnerability research;
- credential collection across downstream customers;
- state-surveillance workflows;
- influence operations with persistent doctrine and attribution laundering;
- the U.S.-China dispute over model distillation.

The records share a report but are not independent observations. `status`, `confidence`, `evidence_method`, source lists and caveats preserve provider attribution, partial external corroboration and the selected-case limitation.

## Provider observability claim

`CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE` is a `claimCheck`, not a new thesis node. It links three arcs and two thesis nodes while remaining `partially_verified`.

The claim has two separate parts:

1. hosted-model telemetry can provide privileged but incomplete visibility into user and agent workflows;
2. control of accounts, requests and configurations can enable selective access revocation.

The claim does not imply complete surveillance, neutral decision-making or public authority. Customer-side telemetry and open-weight deployment are explicit qualifications. The Habr article supplies the panopticon/chokepoint analytical frame and is labelled `primary_or_secondary=analytical_frame`; it does not corroborate Anthropic telemetry.

## Dated state update

The existing `SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE` retains:

- `date=2026-02-23`;
- `numbers.attributed_accounts_approx=24000`;
- `numbers.interactions_more_than=16000000`.

New September figures are stored under `current_state` with `observed_at=2026-09-10` and `event_date=null`. The windows and populations differ, so the values are not automatically additive. Sources are also attached at the event level so the global source index remains complete.

## Official positions

`SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE` stores both the 8 September U.S. joint advisory and the 9 September Chinese response. `verified_official_positions_disputed_attribution` means that publication of both positions is verified; it does not adjudicate consent, legality, data provenance or technical attribution.

## Behaviour fields

Three records join `BEH_TRACK_CONCEALMENT_PERSISTENCE`:

- GTG-20006 through strategic concealment and external artifacts;
- GTG-10007 through persistent campaign memory and agent coordination;
- influence operations through persistent doctrine files and externalized state.

`behavior_origin=externally_injected` and `goal_source=external_instruction` preserve the human-supplied objective. They must not be read as evidence of independent model intent.

## Links

The release adds 39 edges. Of these, 21 are `part_of_arc` thematic memberships and do not support an entire arc. Evidential links target scoped claim checks; `updated_by` links provide chronology without asserting causality.

## Audit

`review/anthropic-threat-intel-september-2026/candidates.json` contains the bilingual source ledger, accepted records, the scoped claim check, the dated update and deferred topics. `scripts/migrate_anthropic_threat_intel.py` accepts only the pinned v0.34 bilingual checksums and validates references, dates and source preservation before writing either output.
