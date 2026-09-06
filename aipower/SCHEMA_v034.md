# Schema notes — v0.34

## Scope

An additive layer for domains 03 and 04; all v0.33 node IDs, original event dates and source URLs remain. There are no new top-level domains or story arcs. JSON remains canonical; both HTML versions embed it exactly.

## New fields

| Field | Meaning | Boundary |
|---|---|---|
| `resilience_track_ids` | Membership in six authored reading tracks | Thematic, not proof of every claim in a track. |
| `cyberFramework.resilience_tracks[].event_ids` | Explicit event IDs for each track | Rebuilt and checked against event membership in both languages. |
| `cyberFramework.resilience_claim_id` | Scoped throughput/capacity claim | Remains `partially_verified`; not an industry-wide incidence estimate. |
| `defense_evidence_kind` | Maintainer report, provider report, released fix, upstream artifact, announcement, draft, pilot, risk assessment, product preview or historical context | Evidence type is separate from normative force and implementation stage. |
| `defense_stage_ids` | Stages addressed by the evidence: discovery, validation, ownership, coordination, patch, release, deployment, revalidation, recovery | Stage relevance does NOT assert that the stage has been completed. Consult scope and the source. |
| `pipeline_metrics[]` | Metric ID, value, unit, population RU/EN, as-of date and source URL | Units and populations must not be pooled without justification. |
| `pipeline_semantics` | Explicit denominator/route limitations for CVD | Not a sequential funnel; direct disclosure can contain unreviewed findings. |
| `cooperative_program` artifact kind | Industry/community cooperative initiative | Not a government program or binding regulation by default. |

## Observation versus event date

`current_state.observed_at` is a state-observation date, not the original event date. The rust-in-peace record retains the 6 August statement and its 33 fixes; a separate 6 September observation records the ledger summary dated 18 August and the two individually checked upstream PRs. The author-reported 37 resolved findings are not a full independent recount.

For Defense Factory the source is undated. `date_basis=observation_date_publication_unknown`, `event_date=null` and `observed_at=2026-09-06` prevent the observation from being mistaken for the sprint date or initial publication. `source_date` remains empty. This is not a future event.

## Numeric safeguards

CVD: 5,008 reviewed; 4,576 validated in that subset; 91.4% is not full-corpus precision. Two reporting routes sum to 2,300; `acknowledged` means a reply, not validation. Upstream fixes do not establish fleet-wide deployment. Duplicate and won't-fix cases can be included in validated findings.

Linux networking: 632 and 648 count patches. A maintainer's approximate AI attribution is not a counted population of unique vulnerabilities. curl 8.22.0 has nine curl/libcurl security fixes; the adjacent wcurl CVE is separate. Daybreak's $1B is a commitment to subsidized access/support, not cash already disbursed. Watershed's launch is not a measured pilot outcome.

## Links and UI

The new 45 edges include 15 `part_of_arc` thematic memberships. Support edges are restricted to the scoped claim; program announcements do not establish effective mitigation. Reading tracks respect the existing global cyber filters and have their own `r.track` / `r.open` URL state. These parameters do not change the established behavior-layer `b.*` state.

## Audit

`review/resilience-throughput/candidates.json` is the accepted bilingual source layer and deferred-candidate queue. `source-ledger.json` records checked sources, dates, verification paths and upstream merge SHAs. `baseline-manifest.json` preserves v0.33 IDs, dates, URLs and selected historical metrics. `changes_ru.json` and `changes_en.json` report added and changed nodes by ID. The migration accepts only pinned v0.33 checksums and validates both inputs before writing either language.
