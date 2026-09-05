# Schema notes — v0.30

## Separate axes

For each of the 97 classified cyber records:

| Field | Meaning | Important boundary |
|---|---|---|
| `artifact_kind` | Law, recommendation, incident, evaluation, research, product, access programme, etc. | Kind is not legal force. |
| `normative_force` | `binding`, `advisory`, `contractual`, `conditional`, `not_applicable`, `undetermined` | Always read with stage and scope. `binding` + `future_effective` is not currently applicable. |
| `implementation_stage` | Effective, partly effective, transition period, draft, future-effective, observed, published, remediation or deployment state | A publication date does not establish operation at full scale. |
| `scope_ru`, `scope_en` | Applicability, affected system/population and evidence limits | No universal applicability inferred from one jurisdiction or programme. |
| `primary_domain_id` | Explicit primary analytical domain | Does not depend on array order. Stable domain-03 ID retains `NATIONAL_DEFENSE` for compatibility; its current label is broader. |
| `cyber_domain_ids` | All applicable domains | Multiple domains are allowed, not steps in a maturity ladder. |
| `cyber_role_ids` | Protected system / defensive tool / attack enabler | May be empty for context. A tool used to attack is distinct from an AI system being attacked. |
| `delegated_authority` | Observed, evaluated, control requirement, not established, not applicable | A policy discussing permissions is not evidence of actual agency. |
| `editorial_priority` | 1: core; 2: context; 3: peripheral | Not a model score, confidence score or graph-centrality measure. |
| `editorial_rationale_ru/en` | Editorial selection note | Does not certify the underlying claim. |

Vocabulary IDs and bilingual labels live in `cyberFramework`. Renderers must not independently infer these fields from keyword substrings. Proposed instruments may carry `intended_normative_force`, explicitly distinct from actual force. Legacy `cyber_access_principal` is retained as a compatibility flag, but the interface does not treat it as proof of exercised access.

## Links and countervailing effects

`part_of_arc` is thematic membership; `relationship_class=thematic`. It must not be counted as evidentiary support. Previous labels are retained in `relation_legacy_v029`.

`mechanism_effects` describes a narrower editorial interpretation: actor, controlled mechanism, direction and scope. The four annotations concern Microsoft cloud exclusivity, Google publisher-content control, provider-centralised telemetry and institutional AI outcomes. They are not estimates of causal effect. Older event-to-event relation names remain stable; definitions warn where the name is stronger than independently established evidence.

## Time

`date` remains the original event date. `current_state.observed_at` is the date a state was observed, **not** necessarily the date it first became true. `current_state.event_date=null` for Kimi means that the first weight-release date is not established in this package. The July announcement and September observation must not be collapsed.

## Entities

`actor_raw`, `actors_raw`, `geography_raw` preserve prior labels. Named entities are not limited to a preapproved list. Canonical `actor_entities` collapse known aliases (including `Nvidia` → `NVIDIA` and `US DOJ` → `US Department of Justice`) without rewriting raw or legacy evidence. `actor_unclassified` and `classificationReviewQueue` expose unresolved labels. The catalogue includes singleton actors; the `__unresolved__` UI option is a filter token, not an actor entity.

## Claims and counts

`summary.claim_status_counts` refers to 71 claims, not 321 events. `verified=49`, `partially_verified=20`, `disputed=2` are dataset labels, not a new external scoring exercise. Source URL count is not a count of independent confirmations.

## Reproducibility

The two language packages share IDs, edge signatures, entity lists and classifications. Their presentation strings may differ. JSON is canonical; HTML embeds it exactly. `classification_legacy_v029`, migration patches and pinned baselines preserve audit history. `referenceIntegrity` is regenerated from declared reference fields; browser tests exercise actual rendering separately.
