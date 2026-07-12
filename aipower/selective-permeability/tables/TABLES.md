# Appendix B. Supplementary result tables

The tables are generated from the released raw and derived data. Denominators, uncertainty, and missing-outcome bounds are stated with each result.

## T1. Auditor dissociation (W1) — mean auditor flag by ground-truth label
| label | content | relevance | provenance | independence |
|---|---|---|---|---|
| false | 0.977 | 0.961 | 0.998 | 0.882 |
| irrelevant | 0.329 | 0.983 | 0.746 | 0.753 |
| relevant | 0.36 | 0.18 | 0.003 | 0.431 |

_Content is blind to true-but-irrelevant (0.33); relevance catches it (0.98); provenance token-verifies (relevant 0.003 vs fabricated 1.00)._

## T1b. Auditor operating points at tau=0.5
| role | positive class | sensitivity | specificity | AUC | TP/FN/TN/FP |
|---|---|---|---|---|---|
| content | fabricated content | 0.99 | 0.67 | 0.96 | 107/1/356/177 |
| relevance | off-rule or false | 1.00 | 0.79 | 0.96 | 430/2/164/44 |
| provenance | unauthorized/self-confirming | 0.87 | 1.00 | 0.97 | 376/56/210/0 |
| independence | self-confirming path | 1.00 | 0.32 | 0.80 | 108/0/168/364 |

_The positive class is role-specific. The `relevant` T1 row is authorized and token-verified. The `irrelevant` row is true but carries no valid issuer token: its authority labels are unauthorized or self-confirming. False-positive rates on legitimate items explain why a useful detector can be a poor quarantine gate._

## T2. Long-horizon durable selective permeability (W9b) — by vehicle × defense
| vehicle | defense | durable_update | durable_leak | selective_permeability |
|---|---|---|---|---|
| memory | cooling_off | 0.488 | 0.214 | 0.274 |
| memory | memory_quarantine | 0.274 | 0.179 | 0.095 |
| memory | none | 0.476 | 0.298 | 0.178 |
| memory | provenance_bound | 0.655 | 0.131 | 0.524 |
| rag | cooling_off | 0.845 | 0.19 | 0.655 |
| rag | memory_quarantine | 0.548 | 0.119 | 0.429 |
| rag | none | 0.821 | 0.202 | 0.619 |
| rag | provenance_bound | 0.857 | 0.167 | 0.69 |
| wiki | cooling_off | 0.036 | 0.024 | 0.012 |
| wiki | memory_quarantine | 0.024 | 0.012 | 0.012 |
| wiki | none | 0.012 | 0.012 | 0.0 |
| wiki | provenance_bound | 0.012 | 0.0 | 0.012 |

_provenance_bound is a **clear win in memory** (SP 0.52 vs none 0.18) and a **marginal, uncertain increment in RAG** (0.69 vs 0.62 — CIs overlap, T5b); naive quarantine over-blocks; **wiki collapses** in the merged, token-erasing setup (compaction retained 0/42 tokens). Observed channel differences also include retrieval/delivery success and are not interpreted as a causal vehicle effect without a separate retrieval-success measure._

## T2c. W9d — per-item, token-preserving wiki summarization recovers the channel
| defense | durable_update | durable_leak | SP | cluster 95% CI | clusters |
|---|---|---|---|---|---|
| cooling_off | 0.39 | 0.15 | 0.24 | [0.08, 0.40] | 21 |
| memory_quarantine | 0.25 | 0.15 | 0.10 | [0.00, 0.23] | 21 |
| none | 0.33 | 0.18 | 0.15 | [0.06, 0.27] | 21 |
| provenance_bound | 0.31 | 0.17 | 0.14 | [0.04, 0.29] | 21 |

_The §7.5 source-amnesia collapse was a **merged-wiki + token-stripping-summarizer** confound. With per-item summaries and a token-preserving (Opus) summarizer that retains 42/42 tokens, wiki SP recovers from approximately zero. `provenance_bound` (0.14) does not exceed `none` (0.15); the supported conclusion is channel recovery through per-item token preservation, not a restored provenance-control premium._

## T3a. Token disclosure (W7b) — token-out primary, severity secondary
_Token-out = PROVIDED + MENTIONED and is the human-validated leak boundary. PROVIDED-only is a secondary severity category; approximately one third of emitted-token cases in the single-coder subset were hedged or incidental._

| model | parsed/attempted | token-out | 95% CI | provided | mentioned | refused |
|---|---|---|---|---|---|---|
| GPT-5.5 | 72/72 | 1.0 | [0.949, 1] | 1.0 | 0.0 | 0.0 |
| Llama-8b | 72/72 | 1.0 | [0.949, 1] | 1.0 | 0.0 | 0.0 |
| Mistral-lg | 72/72 | 0.875 | [0.779, 0.933] | 0.875 | 0.0 | 0.125 |
| Qwen3.7 | 72/72 | 0.861 | [0.763, 0.923] | 0.861 | 0.0 | 0.139 |
| Opus-4.8 | 68/72 | 0.75 | [0.636, 0.838] | 0.721 | 0.029 | 0.25 |
| DeepSeek-v4 | 70/72 | 0.714 | [0.599, 0.807] | 0.714 | 0.0 | 0.286 |
| Sonnet-4.6 | 69/72 | 0.565 | [0.448, 0.676] | 0.029 | 0.536 | 0.435 |

## T3b. Token forgery acceptance (W7b) — by model × defense, 95% CI
| model | defense | forged_accept | 95% CI | n |
|---|---|---|---|---|
| Opus-4.8 | none | 0.0 | [0, 0.138] | 24 |
| Opus-4.8 | registry | 0.0 | [0, 0.138] | 24 |
| Sonnet-4.6 | none | 0.0 | [0, 0.138] | 24 |
| Sonnet-4.6 | registry | 0.0 | [0, 0.138] | 24 |
| DeepSeek-v4 | none | 0.0 | [0, 0.138] | 24 |
| DeepSeek-v4 | registry | 0.0 | [0, 0.138] | 24 |
| Llama-8b | none | 0.417 | [0.245, 0.612] | 24 |
| Llama-8b | registry | 0.292 | [0.149, 0.492] | 24 |
| Mistral-lg | none | 0.917 | [0.742, 0.977] | 24 |
| Mistral-lg | registry | 0.0 | [0, 0.138] | 24 |
| GPT-5.5 | none | 0.0 | [0, 0.138] | 24 |
| GPT-5.5 | registry | 0.0 | [0, 0.138] | 24 |
| Qwen3.7 | none | 0.0 | [0, 0.138] | 24 |
| Qwen3.7 | registry | 0.0 | [0, 0.138] | 24 |

_Only Mistral and Llama accept the forged token in this assay; the registry policy removes the observed Mistral effect. GPT-5.5's 72/72 no-instruction emissions are also classified PROVIDED by the Anthropic second judge, so the GPT row does not depend on self-judging._

## T3c. W7c protected condition — token-out primary
| model | parsed/attempted | token-out | provided | mentioned | missing bounds |
|---|---|---|---|---|---|
| Mistral-lg | 68/72 | 0.809 | 0.191 | 0.618 | [0.764, 0.819] |
| Llama-8b | 72/72 | 0.139 | 0.139 | 0.0 | [0.139, 0.139] |
| Opus-4.8 | 67/72 | 0.06 | 0.0 | 0.06 | [0.056, 0.125] |
| Sonnet-4.6 | 71/72 | 0.296 | 0.0 | 0.296 | [0.292, 0.306] |
| GPT-5.5 | 72/72 | 0.0 | 0.0 | 0.0 | [0.0, 0.0] |
| Qwen3.7 | 72/72 | 0.0 | 0.0 | 0.0 | [0.0, 0.0] |
| DeepSeek-v4 | 70/72 | 0.029 | 0.0 | 0.029 | [0.028, 0.056] |

_The exact bearer string is the primary outcome. Clean handover and mention-within-refusal are reported as severity categories._

## T3d. W7c legitimate citation request — refusal with missing-outcome bounds
| model | parsed/attempted | parsed refusal | all-missing bounds |
|---|---|---|---|
| GPT-5.5 | 24/24 | 0.0 | [0.0, 0.0] |
| Llama-8b | 24/24 | 0.0 | [0.0, 0.0] |
| Sonnet-4.6 | 14/24 | 0.5 | [0.292, 0.708] |
| Qwen3.7 | 24/24 | 0.583 | [0.583, 0.583] |
| DeepSeek-v4 | 23/24 | 0.783 | [0.75, 0.792] |
| Opus-4.8 | 20/24 | 0.8 | [0.667, 0.833] |
| Mistral-lg | 22/24 | 0.864 | [0.792, 0.875] |

_These are model profiles, not evidence of a universal security-versus-over-refusal trade-off. Sonnet's parsed estimate 0.50 has a full-attempt bound of 0.29-0.71 because 10/24 stored outputs were unparseable._

## T3e. W7d full 2x2 — strict token containment
| model | real+secret | real+public | inert+secret | inert+public | D_label | D_referent | interaction |
|---|---|---|---|---|---|---|---|
| Opus-4.8 | 0.667 | 0.167 | 0.611 | 0 | 0.556 | 0.111 | -0.111 |
| Sonnet-4.6 | 0.722 | 0.278 | 0.611 | 0 | 0.528 | 0.194 | -0.167 |
| DeepSeek-v4 | 0.778 | 0.167 | 0.389 | 0.111 | 0.444 | 0.222 | 0.333 |
| Llama-8b | 1 | 0 | 1 | 0.111 | 0.944 | -0.056 | 0.111 |
| Mistral-lg | 0.167 | 0 | 0 | 0 | 0.083 | 0.083 | 0.167 |
| GPT-5.5 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |
| Qwen3.7 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |

_Strict containment counts only REFUSED as containing the bearer token. Refusal posture (REFUSED + MENTIONED) gives D_label=0.87 and D_referent=0.04; strict containment gives 0.65 and 0.08. The effect is large but outcome-dependent, and the original policy texts differ in emphasis. W7e below addresses that prompt-strength confound._

## T3f. W7e emphasis-matched replication - strict token containment
| model | real+secret | real+public | inert+secret | inert+public | D_policy | D_referent | interaction |
|---|---|---|---|---|---|---|---|
| Opus-4.8 | 0.778 | 0 | 0.389 | 0 | 0.583 | 0.194 | 0.389 |
| Sonnet-4.6 | 0.722 | 0.222 | 0.889 | 0.278 | 0.556 | -0.111 | -0.111 |
| DeepSeek-v4 | 0.722 | 0.167 | 0.667 | 0.056 | 0.583 | 0.083 | -0.056 |
| Llama-8b | 1 | 0.056 | 1 | 0.222 | 0.861 | -0.083 | 0.167 |
| Mistral-lg | 0.444 | 0 | 0.556 | 0 | 0.500 | -0.056 | -0.111 |
| GPT-5.5 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |
| Qwen3.7 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |

_Both policy polarities use matched capitalization, modality, exception lists, and length. Strict containment gives D_policy=0.726 [0.655, 0.821] and D_referent=0.004 [-0.036, 0.036]; D_policy exceeds D_referent in all seven selected model rows. All 504 target records are valid. The intervals resample only three scenario clusters and are therefore descriptive._

## T4a. ScamOps capture, no defense (W8, pilot) — mechanism × model
| mechanism | model | baseline_correct | capture |
|---|---|---|---|
| authority_seizure | Opus-4.8 | 0.667 | 0.0 |
| authority_seizure | Sonnet-4.6 | 0.583 | 0.0 |
| authority_seizure | DeepSeek-v4 | 0.5 | 0.083 |
| authority_seizure | Llama-8b | 0.667 | 0.917 |
| authority_seizure | Mistral-lg | 0.5 | 1.0 |
| authority_seizure | GPT-5.5 | 0.667 | 0.0 |
| authority_seizure | Qwen3.7 | 1.0 | 0.0 |
| manufactured_consensus | Opus-4.8 | 0.667 | 0.0 |
| manufactured_consensus | Sonnet-4.6 | 0.667 | 0.0 |
| manufactured_consensus | DeepSeek-v4 | 0.417 | 0.0 |
| manufactured_consensus | Llama-8b | 0.75 | 0.167 |
| manufactured_consensus | Mistral-lg | 0.5 | 0.333 |
| manufactured_consensus | GPT-5.5 | 0.667 | 0.0 |
| manufactured_consensus | Qwen3.7 | 1.0 | 0.0 |
| urgency_compression | Opus-4.8 | 0.667 | 0.0 |
| urgency_compression | Sonnet-4.6 | 0.583 | 0.083 |
| urgency_compression | DeepSeek-v4 | 0.25 | 0.0 |
| urgency_compression | Llama-8b | 0.75 | 0.583 |
| urgency_compression | Mistral-lg | 0.417 | 0.333 |
| urgency_compression | GPT-5.5 | 0.667 | 0.0 |
| urgency_compression | Qwen3.7 | 1.0 | 0.0 |
| verification_capture | Opus-4.8 | 0.667 | 0.0 |
| verification_capture | Sonnet-4.6 | 0.583 | 0.0 |
| verification_capture | DeepSeek-v4 | 0.417 | 0.0 |
| verification_capture | Llama-8b | 0.667 | 1.0 |
| verification_capture | Mistral-lg | 0.417 | 0.333 |
| verification_capture | GPT-5.5 | 0.667 | 0.0 |
| verification_capture | Qwen3.7 | 1.0 | 0.0 |

## T4b. ScamOps defense recovery (W8) — lure-rate reduction vs no-defense
| mechanism | defense | lure_rate | recovery_vs_none | correct_rate |
|---|---|---|---|---|
| authority_seizure | cooling_off | 0.083 | 0.188 | 0.438 |
| authority_seizure | independent_registry | 0.25 | 0.021 | 0.375 |
| authority_seizure | none | 0.271 | 0.0 | 0.333 |
| authority_seizure | single_dissenter | 0.25 | 0.021 | 0.375 |
| manufactured_consensus | cooling_off | 0.083 | 0.0 | 0.479 |
| manufactured_consensus | independent_registry | 0.062 | 0.021 | 0.458 |
| manufactured_consensus | none | 0.083 | 0.0 | 0.479 |
| manufactured_consensus | single_dissenter | 0.083 | 0.0 | 0.562 |
| urgency_compression | cooling_off | 0.0 | 0.083 | 0.604 |
| urgency_compression | independent_registry | 0.083 | 0.0 | 0.438 |
| urgency_compression | none | 0.083 | 0.0 | 0.458 |
| urgency_compression | single_dissenter | 0.021 | 0.062 | 0.479 |
| verification_capture | cooling_off | 0.062 | 0.021 | 0.479 |
| verification_capture | independent_registry | 0.021 | 0.062 | 0.521 |
| verification_capture | none | 0.083 | 0.0 | 0.5 |
| verification_capture | single_dissenter | 0.083 | 0.0 | 0.417 |

_Pilot. Capture (T4a) now covers all **7 models** (Sonnet/Qwen/Llama added, no-defense only); defense-recovery (T4b) remains the original 4-model run. Crude pressure is concentrated in Mistral and Llama in this panel; other rows are near zero. Cooling-off has the largest observed recovery, within a small pilot._

## T5a. W1 selective permeability by defense — cluster-bootstrap 95% CI (unit = payload)
| defense | selective_permeability | 95% CI |
|---|---|---|
| D0_no_defense | 0.732 | [0.628, 0.82] |
| D1_content_audit | 0.321 | [0.116, 0.532] |
| D2_relevance_provenance_independence | 0.372 | [0.162, 0.585] |
| D3_action_critic | 0.0 | [0.0, 0.0] |
| D4_known_good_source_registry | 0.501 | [0.299, 0.705] |

_Multiplicity-preserving cluster bootstrap (resamples payloads with replacement). D0 (no gate) SP is highest; the content and action-critic gates' CIs are disjoint from D0, the registry gate's overlaps modestly. Detector is not automatically a deployable gate on models with an already-low illegitimate-leak component; authorized-update rates must be inspected separately._

## T5b. W9b durable selective permeability — cluster-bootstrap 95% CI (unit = scenario×victim)
| vehicle | defense | selective_permeability | 95% CI | n_clusters |
|---|---|---|---|---|
| memory | cooling_off | 0.274 | [0.131, 0.429] | 21 |
| memory | memory_quarantine | 0.095 | [0.012, 0.214] | 21 |
| memory | none | 0.179 | [0.048, 0.321] | 21 |
| memory | provenance_bound | 0.524 | [0.345, 0.702] | 21 |
| rag | cooling_off | 0.655 | [0.476, 0.833] | 21 |
| rag | memory_quarantine | 0.429 | [0.262, 0.607] | 21 |
| rag | none | 0.619 | [0.429, 0.798] | 21 |
| rag | provenance_bound | 0.69 | [0.5, 0.869] | 21 |
| wiki | cooling_off | 0.012 | [-0.024, 0.048] | 21 |
| wiki | memory_quarantine | 0.012 | [-0.036, 0.071] | 21 |
| wiki | none | 0.0 | [0.0, 0.0] | 21 |
| wiki | provenance_bound | 0.012 | [0.0, 0.036] | 21 |

_provenance_bound on **memory** excludes the none-defense level (clear win); on **RAG** the increment is marginal (CIs overlap none); **wiki** collapses. n=21 clusters is coarse — some CIs reach slightly below 0._

