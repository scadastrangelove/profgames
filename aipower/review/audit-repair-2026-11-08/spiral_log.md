# Audit repair log

## 2026-11-08

Repaired the v0.53 audit and recent-year chronology in both language packages. Original audit and source evidence are retained. Tests cover data migration, release reproducibility, navigation, complete evidence display and real browser geometry.

Completion: resolved the 13-record actor-type queue using primary institutional and author sources; added 13 URLs with identity-only provenance. Removed the mismatched governance preamble from 52 research cards without altering scientific results. English cards now display normalized actor entities. Separate reversible journals and replay tests cover both passes.

## Debt

1. Closed: the 13-record actor-type review queue is empty. The older 16 unresolved raw classifier labels remain separately tracked; resolving ambiguous raw input is still outstanding.
2. Closed: known governance boilerplate removed from all 52 affected research cards. Original study outcomes and limitations remain unchanged.
3. Legacy `evidence_relations.event_id` can reference a claim, such as `export-14`. It is validated as a typed existing node; a future schema revision can rename it to `node_id` with compatibility support.
4. Full independent source re-verification remains outside this repair. Identity-source review is explicitly scoped and does not upgrade study outcomes. Release publication is authorized; deployment must be checked against the pushed commit.

## Anti-overfit

Use explicit identities and relations. Preserve ambiguous evidence, reject conflicting manual relations, and test synthetic dates, duplicate citations and same-date collisions independently of the news fixture set.
