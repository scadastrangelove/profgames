# Schema notes — v0.38

## Scope

This release restructures story-arc presentation without adding or removing facts, claims, claim checks, arcs, edges or source URLs. All v0.37 identifiers remain valid. The hierarchy is an editorial reading route, not an evidentiary or causal score.

## Arc hierarchy

Each record in `arcs` now has four presentation fields:

- `display_role` — `mechanism`, `submechanism`, `qualifier`, `case`, `sector_case`, `timeline_lens` or `timeline_marker`;
- `display_order` — stable order inside its family;
- `default_visible` — whether the record appears in the mechanism-first view;
- `parent_arc_id` — another legacy arc ID when the record is nested.

The top-level `arcHierarchy` object defines the six-family order, bilingual role labels, role counts and the interpretive boundary. The `summary.arc_hierarchy` object exposes compact counts for the interface.

## Display membership

Events that belong to at least one real story arc receive:

- `story_primary_arc_id` — one placement route selected deterministically from existing memberships;
- `story_secondary_arc_ids` — the remaining display routes.

These fields do not replace `arcIds`, `arcFamilyIds`, `edgeIds`, authored `key_nodes` or `part_of_arc` edges. A primary route does not make a fact stronger evidence for that arc.

## Structural decisions

`ARC_EXPORT_CHIPS_TO_MODELS` contains the licensed-access submechanism, the enforcement/leakage qualifier and the A800/H800 case. `ARC_CORPORATE_DECISION_SUPPORT_ADOPTION` contains the Palantir, finance and war-data sector cases. The war-data record moves to the decisions-and-data family; its ID and every existing edge remain unchanged.

The three formation arcs and the 2023 governance marker are timeline records. They remain directly selectable and preserve their dated facts, but do not compete with mechanisms in the default view.

## Audit

`scripts/migrate_arc_hierarchy.py` accepts only the pinned v0.37 bilingual checksums. `migrationAudit.v038_arc_hierarchy` records role counts, the single family reassignment, 14 matching edge-family metadata updates, 12 recomputed node-family memberships, zero semantic edge changes and zero removed IDs. Validation checks all new references, bilingual hierarchy parity, embedded-data parity and preservation of the complete legacy corpus.
