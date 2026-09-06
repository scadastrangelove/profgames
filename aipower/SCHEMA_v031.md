# Schema notes — v0.31

v0.31 extends the v0.30 cyber classification without replacing its axes. `artifact_kind`, `normative_force`, `implementation_stage`, `cyber_role_ids`, `delegated_authority` and `editorial_priority` keep their previous meanings.

## Domain 5 subdomains

`CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY` now has two explicit analytical scales:

| ID | Scope |
|---|---|
| `CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION` | Task boundaries, memory, provenance, coordination, monitorability, interruption and influence over a decision. |
| `CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY` | Agent identity, revocation, logs, keys, portability, investigation and exit from a provider stack. |

An event may belong to both. The subdomains are not maturity levels and 5B is not evidence that a system is sovereign or autonomous.

## Behavioural fields

| Field | Shape | Meaning |
|---|---|---|
| `cyber_subdomain_ids` | array | Applicable 5A/5B scale. |
| `behavioral_mechanism_ids` | array | One or more of the eleven mechanisms in `cyberFramework.behavioral_mechanisms`. |
| `behavioral_status` | array | What the evidence establishes: incident, demonstrated or assessed capability, estimated propensity, tested mitigation, measured exposure/effect, reported pattern, risk assessment or policy response. |
| `evidence_context` | array | Production, internal deployment, training, evaluation with external effect, controlled simulation, benchmark, ecosystem measurement or governance document. |
| `evidence_method` | string | Narrow method label retained separately from the broader context vocabulary. |
| `agent_population_scope` | string | Single agent, repeated runs, a shared-state population, explicit multi-agent system, human-agent workflow or not applicable. |
| `shared_writable_state` | string | None, local memory, shared internal artifact, public external artifact or unknown. |
| `oversight_target` | array | User, reviewer, grader, monitor, security control, peer agent or institutional process affected by the behaviour/control. |
| `motivation_basis` | string | Evidential basis for any motive language; `no_motivation_claim` is explicit, not missing data. |

Vocabulary IDs and bilingual labels live in `cyberFramework`. Renderers must not infer these fields from titles, keywords or relation names.

## Five mechanism groups

`cyberFramework.behavior_groups` organises the eleven mechanisms into a readable dependency order:

1. task framing;
2. memory and provenance;
3. coordination;
4. control and interruption;
5. decision and exit.

This order is an authored control model, not a causal DAG. Counts in the interface report classified records under the current filters; they do not measure risk, prevalence or control strength.

## Evidence boundaries

`behavioral_status` is deliberately multi-valued. A controlled experiment may both demonstrate a capability and test a mitigation. A product incident followed by a rollback may be both `incident_observed` and `policy_response`.

The following must remain distinct:

- capability demonstrated in a selected configuration;
- propensity estimated for a stated population and setup;
- an externally consequential incident;
- a provider's operational synthesis;
- a forward-looking risk assessment;
- an organisational or legal response.

The calibrated claim `CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE` is `partially_verified`. Its supporting and qualifying evidence are separate reference arrays. Neither a rare incident nor a null provider-monitoring result is generalised to all deployed agents.

## Time and provenance

`date` is the event or first-observation date used on the timeline. Source publication and revision dates remain in each source object. In particular:

- `SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE` uses `2026-05-24`, the first verified successful wiki write;
- `SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS` uses `2025-09-13`, arXiv v1; the 2026 revision is not backdated into the event point.

The unmodified candidate package is retained under `review/v031-agent-behavior/`. Migration copy and normalised production fields are explicit so that candidate wording is not silently treated as canonical data.

## References and parity

`referenceIntegrity` covers typed endpoints, arc keys, `supporting_evidence`, `qualifying_evidence`, node `arcIds`, `arcFamilyIds`, `edgeIds` and source `used_by` links. Every URL referenced by a node must occur exactly once in `sourceIndex`.

RU and EN packages share IDs, dates, edge signatures and all classification fields. Visible editorial prose may differ. JSON remains authoritative; generated HTML embeds it exactly.
