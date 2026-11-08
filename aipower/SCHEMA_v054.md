# v0.54: audit repair contract

This additive contract extends v0.52 without deleting records, source URLs or original edge endpoints. `auditRepair` describes the migration. Its reversible field journal is stored in `review/audit-repair-2026-11-08/migration-audit.json`.

## Aliases and counts

- `canonical_event_id` identifies the event used for presentation. `exclude_from_presentation: true` hides a duplicate from listings and counts, not from the data or old links.
- The canonical record lists `alias_event_ids`, `canonical_provenance_event_ids` and `canonical_edge_ids`. Presentation merges sources, caveats and associations from the retained alias.
- Edges retain `source` and `target`. Optional `canonical_source` / `canonical_target` identify presentation endpoints. They do not create new independent evidence.
- Legacy counts describe stored records. `auditRepair.presentation_counts` distinguishes 566 presented events from 567 retained records.

## Membership and evidence

Authored primary/secondary routes and direct membership edges determine reading routes. A contextual `arc_id` alone does not imply membership. `context_arc_ids` records associations outside the reading route. Historical prerequisites can live in an arc's `context_nodes`, with separate context dates, without extending its period.

`edgeIds` is the exact list of incident original edges. Every edge carries typed endpoints. `supporting_evidence` remains a legacy reference field; its name is not a polarity guarantee. `evidence_relations` records available manual polarity. The interface labels it neutrally and shows `qualifying_evidence` separately.

## Sources and actors

Repeated exact URLs within one record are displayed once; `citation_variants` retains the original citation objects. Original source IDs and URLs are retained; the completion adds identity-review sources to the index and groups.

Actor types use reviewed exact registry identities and the existing taxonomy. `audit_actor_types` retains unresolved identities for later review. No organisation or role is inferred from a title substring or a co-actor.

`auditCompletion` records the 13 reviewed actor records, 52 editorial corrections and added URLs. `actor_identity_review.actors` records canonical names, types, jurisdictions, identity basis and primary sources. It is a scoped review of named leads or programme participants, not an exhaustive affiliation inventory or a fresh assessment of study results. Raw input fields are unchanged. The additive `public_official` type means a named politician or public official, not a government body. The completion is independently replayable from `completion-audit.json`; the earlier repair journal is unchanged.

## Chronology

Event dates are unchanged. Object-shaped `current_state.observed_at` and string-shaped `current_state` with `current_state_as_of` normalize to separate updates; they never move the original event. Latest events and later updates have independent descending chronology.

The timeline is piecewise-linear: compressed early history, intervening annual segments and four expanded quarters of the latest year. Dates are linear inside each labelled segment. Collision packing changes only vertical position, not time. Dense groups receive additional rows rather than overlapping targets.
