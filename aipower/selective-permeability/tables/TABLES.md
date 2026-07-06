# Review-pack tables (generated from artifacts/derived)

## T1. Auditor dissociation (W1) — mean auditor flag by ground-truth label
| label | content | relevance | provenance | independence |
|---|---|---|---|---|
| false | 0.977 | 0.961 | 0.998 | 0.882 |
| irrelevant | 0.329 | 0.983 | 0.746 | 0.753 |
| relevant | 0.36 | 0.18 | 0.003 | 0.431 |

_Content is blind to true-but-irrelevant (0.33); relevance catches it (0.98); provenance token-verifies (relevant 0.003 vs fabricated 1.00)._

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

_provenance_bound is a **clear win in memory** (SP 0.52 vs none 0.18) and a **marginal, uncertain increment in RAG** (0.69 vs 0.62 — CIs overlap, T5b); naive quarantine over-blocks; **wiki collapses** in the merged, token-erasing setup (compaction retained 0/42 tokens). The dominant effect is the vehicle, not the defense._

## T2c. W9d — per-item, token-preserving wiki summarization recovers SP (mitigates source amnesia)
| defense | durable_update | durable_leak | selective_permeability |
|---|---|---|---|
| cooling_off | 0.393 | 0.155 | 0.238 |
| memory_quarantine | 0.25 | 0.155 | 0.095 |
| none | 0.333 | 0.179 | 0.155 |
| provenance_bound | 0.31 | 0.167 | 0.143 |

_The §7.5 source-amnesia collapse was a **merged-wiki + token-stripping-summarizer** confound. With per-item summaries and a token-preserving (Opus) summarizer that retains 42/42 tokens, wiki SP recovers from ≈0 to **0.14–0.24** (provenance_bound 0.14, cooling_off 0.24). Source amnesia is real but **mitigable** — a pipeline choice, not an intrinsic failure._

## T3a. Token disclosure (W7b) — PROVIDED rate with 95% CI (7×3 pretexts×K8, judge-classified)
_Human-validated as a **leak rate** (token-out κ=1.0 vs GPT / 97.7% vs Anthropic, HUMAN_VALIDATION.md); the judge does not separate clean from hedged/incidental disclosure (3-class κ≈0.5), and ~⅓ of leaks are the hedged kind. Read 'provided' as 'usable token emitted', not 'clean hand-over'._
| model | n | provided | 95% CI | mentioned | refused |
|---|---|---|---|---|---|
| GPT-5.5 | 72 | 1.0 | [0.949, 1] | 0.0 | 0.0 |
| Llama-8b | 72 | 1.0 | [0.949, 1] | 0.0 | 0.0 |
| Mistral-lg | 72 | 0.875 | [0.779, 0.933] | 0.0 | 0.125 |
| Qwen3.7 | 72 | 0.861 | [0.763, 0.923] | 0.0 | 0.139 |
| Opus-4.8 | 68 | 0.721 | [0.604, 0.813] | 0.029 | 0.25 |
| DeepSeek-v4 | 70 | 0.714 | [0.599, 0.807] | 0.0 | 0.286 |
| Sonnet-4.6 | 69 | 0.029 | [0.008, 0.1] | 0.536 | 0.435 |

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

_Most frontier advisors emit the credential (leak; Sonnet excepted, .03 — it mentions-while-refusing). Only Mistral/Llama accept forgery; a registry policy fixes Mistral (0.92→0)._

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

_Pilot. Capture (T4a) now covers all **7 models** (Sonnet/Qwen/Llama added, no-defense only); defense-recovery (T4b) remains the original 4-model run. Crude pressure flips only the weak models (Mistral, Llama); frontier ≈0. Cooling-off is the best recovery._

## T5a. W1 selective permeability by defense — cluster-bootstrap 95% CI (unit = payload)
| defense | selective_permeability | 95% CI |
|---|---|---|
| D0_no_defense | 0.732 | [0.628, 0.82] |
| D1_content_audit | 0.321 | [0.116, 0.532] |
| D2_relevance_provenance_independence | 0.372 | [0.162, 0.585] |
| D3_action_critic | 0.0 | [0.0, 0.0] |
| D4_known_good_source_registry | 0.501 | [0.299, 0.705] |

_Multiplicity-preserving cluster bootstrap (resamples payloads with replacement). D0 (no gate) SP is highest; the content and action-critic gates' CIs are disjoint from D0, the registry gate's overlaps modestly. Detector≠deployable-gate on already-robust models (§7.1)._

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

