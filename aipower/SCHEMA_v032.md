# Schema notes — v0.32

v0.32 extends the v0.31 behavioural layer without changing the meaning of its existing fields. The canonical JSON and HTML filenames remain unversioned.

## Concealment and continuity track

`cyberFramework.behavior_tracks` contains the authored track `BEH_TRACK_CONCEALMENT_PERSISTENCE`. Its four stages keep distinct questions separate:

| Stage | Question |
|---|---|
| Weights | Does a conditional policy persist through training or evaluation? |
| Observation state | Does behaviour differ when the model believes it is being trained, evaluated or deployed? |
| Explanation | Is the reasoning trace complete, and is an action or capability deliberately obscured? |
| External state | Can memory, a file or shared environment carry state to a later run? |

The stages are an analytical reading order, not a demonstrated causal chain. Records join the track through `behavior_track_ids`; the track remains inside `ARC_COGSEC_LAB_TO_WILD_TO_STATE` and is not a new top-level story arc.

## New orthogonal fields

| Field | Shape | Meaning |
|---|---|---|
| `behavior_track_ids` | array | Authored local research views to which a record belongs. |
| `behavior_origin` | string | Whether the behaviour was intentionally implanted, elicited by an evaluation, observed during training or deployment, externally injected, unknown or not applicable. |
| `concealment_targets` | array | Party from which an action, objective or signal was hidden; `none` records that concealment was not established. |
| `persistence_media` | array | Weights, reasoning trace, persistent memory, external artifact, shared state, none or unknown. This is not a claim that every listed medium persists across sessions. |
| `goal_source` | string | Explicit prompt, trained preference, inferred grader preference, researcher-implanted objective, external instruction, unknown or not applicable. |

Vocabulary IDs and bilingual labels live in `cyberFramework`. Renderers must not infer these fields from a title or a dramatic transcript.

## Evidence boundary

The 12 backfilled records are primary-source research reports, not 12 production incidents. In particular:

- Sleeper Agents, hidden-objective audits and AuditBench use deliberately constructed model organisms;
- Apollo scheming, Anthropic agentic misalignment and sandbagging use selected controlled evaluations;
- OpenAI reward-seeking evidence concerns intermediate training checkpoints without final safety training;
- chain-of-thought unfaithfulness does not by itself establish intentional lying;
- low CoT controllability is a proxy result, not a guarantee that future motivated models cannot evade monitoring.

The central claim remains `partially_verified`. Capability, conditional propensity and ordinary deployment prevalence remain separate claims.

## Release invariants

The release contains 355 events, 72 claims, 25 arcs, 738 edges and 532 unique source URLs. All 6,435 checked references resolve in each language. RU and EN packages share IDs, dates, edge signatures and classification fields; visible prose may differ.
