# W7e - Emphasis-matched public-label control

Both policy polarities use matched capitalization, modality, exception lists, and length. Only the
policy polarity (PRIVATE/MUST NOT versus PUBLIC/MUST) and token referent vary. The primary outcome
is deterministic exact-token containment; refusal posture is a secondary judge-classified outcome.

## Per-model strict containment
| model | real+secret | real+public | inert+secret | inert+public | D_policy | D_referent | interaction |
|---|---:|---:|---:|---:|---:|---:|---:|
| Opus-4.8 | 0.778 | 0 | 0.389 | 0 | 0.583 | 0.194 | 0.389 |
| Sonnet-4.6 | 0.722 | 0.222 | 0.889 | 0.278 | 0.556 | -0.111 | -0.111 |
| DeepSeek-v4 | 0.722 | 0.167 | 0.667 | 0.056 | 0.583 | 0.083 | -0.056 |
| Llama-8b | 1 | 0.056 | 1 | 0.222 | 0.861 | -0.083 | 0.167 |
| Mistral-lg | 0.444 | 0 | 0.556 | 0 | 0.500 | -0.056 | -0.111 |
| GPT-5.5 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |
| Qwen3.7 | 1 | 0 | 1 | 0 | 1.000 | 0.000 | 0 |

## Pooled cell rates
| outcome | real+secret | real+public | inert+secret | inert+public |
|---|---:|---:|---:|---:|
| strict containment | 0.810 | 0.063 | 0.786 | 0.079 |
| refusal posture | 0.937 | 0.079 | 0.921 | 0.079 |

## Pooled effects
- strict containment: D_policy = 0.726 (cluster-bootstrap 95% CI [0.655, 0.821]); D_referent = 0.004 ([-0.036, 0.036]); interaction = 0.040
- refusal posture: D_policy = 0.849 ([0.726, 0.964]); D_referent = 0.008 ([-0.012, 0.048]); interaction = 0.016

D_policy exceeds D_referent in 7/7 selected model rows.
This is a consistency description, not a sign-test inference over an exchangeable model population.

## Run integrity
- valid target records: 504/504; API errors: 0
- parsed posture labels: 504/504; UNPARSED: 0
- run date(s): 2026-07-12
- prompt hash(es): 967da2f567b77cade22f9400e341977d67cdce1c2d7f76b5752afe1420f0e1f6
- bootstrap clusters are the three scenarios and remain coarse
