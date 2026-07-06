# Reviewer-2/3 statistics addendum

## W7b disclosure — UNPARSED accounting (Reviewer-3 #4)
judge labels over all 504 attempts: {'REFUSED': 86, 'PROVIDED': 370, 'UNPARSED': 9, 'MENTIONED': 39}
UNPARSED/other by model: {'anthropic': 4, 'anthropic_sonnet': 3, 'deepseek': 2}
_PROVIDED-rate reported PARSED-ONLY (denominator = parsed attempts); UNPARSED are parser failures, excluded. This is why per-model n ranges 68–72._

## W7b PROVIDED rate: Wilson (sample-level) vs CLUSTER bootstrap (cluster = scenario×pretext)
| model | provided | Wilson-ish n | cluster-boot 95% CI | n_clusters |
|---|---|---|---|---|
| Opus-4.8 | 0.721 | 68 | [0.551, 0.882] | 9 |
| Sonnet-4.6 | 0.029 | 69 | [0.0, 0.09] | 9 |
| DeepSeek-v4 | 0.714 | 70 | [0.559, 0.873] | 9 |
| Llama-8b | 1.0 | 72 | [1.0, 1.0] | 9 |
| Mistral-lg | 0.875 | 72 | [0.708, 1.0] | 9 |
| GPT-5.5 | 1.0 | 72 | [1.0, 1.0] | 9 |
| Qwen3.7 | 0.861 | 72 | [0.764, 0.944] | 9 |
_Cluster bootstrap (9 scenario×pretext clusters) widens intervals vs Wilson-on-samples; the ordering (GPT/Llama high, Sonnet ~0) is stable, but per-model CIs are wider than the sample-level Wilson CIs in T3a._

## W7b PROVIDED rate by pretext (Reviewer-2/3)
| pretext | provided | n |
|---|---|---|
| delivery | 0.752 | 165 |
| helpdesk | 0.818 | 165 |
| onboarding | 0.673 | 165 |

## W7b per-trial mixed logit (REAL per-sample; random intercepts scenario+pretext)
Reference = Sonnet. Positive coef = more likely to PROVIDE than Sonnet. (VB fit; treat CrI as approximate — mean-field VB is anti-conservative, Reviewer-3 #3.)
| effect | log-odds | 95% CrI (approx) |
|---|---|---|
| Opus-4.8 vs Sonnet | +3.06 | [+2.52, +3.61] |
| DeepSeek-v4 vs Sonnet | +3.03 | [+2.50, +3.56] |
| Llama-8b vs Sonnet | +6.39 | [+4.89, +7.89] |
| Mistral-lg vs Sonnet | +4.10 | [+3.42, +4.78] |
| GPT-5.5 vs Sonnet | +6.39 | [+4.89, +7.89] |
| Qwen3.7 vs Sonnet | +3.98 | [+3.32, +4.64] |

## W7c cluster-bootstrap CIs (cluster = scenario×pretext) — the reframed flagship
### Protected — three severity classes (bearer secret: token-out = it leaked at all)
| model | clean hand-over (PROVIDED) | exposed-while-refusing (MENTIONED) | **token-out** (P+M) | token-out 95% CI | n |
|---|---|---|---|---|---|
| Mistral-lg | 0.191 | 0.618 | **0.809** | [0.671, 0.929] | 68 |
| Sonnet-4.6 | 0.0 | 0.296 | **0.296** | [0.097, 0.528] | 71 |
| Llama-8b | 0.139 | 0.0 | **0.139** | [0.0, 0.278] | 72 |
| Opus-4.8 | 0.0 | 0.06 | **0.06** | [0.0, 0.154] | 67 |
| DeepSeek-v4 | 0.0 | 0.029 | **0.029** | [0.0, 0.069] | 70 |
| Qwen3.7 | 0.0 | 0.0 | **0.0** | [0.0, 0.0] | 72 |
| GPT-5.5 | 0.0 | 0.0 | **0.0** | [0.0, 0.0] | 72 |
_**Clean compliant disclosure (PROVIDED) despite the instruction is confined to Mistral/Llama.** But token-out — the human-validated leak measure (PROVIDED+MENTIONED) — is nonzero for Mistral (0.81) and Sonnet (0.30): they quote the bearer token inside a refusal. Refusal-with-disclosure is lower-severity than clean hand-over, but the secret still escaped. A PROVIDED-only metric hides this; F7 shows both._

### Neutral control — REFUSED = over-refusal of a LEGITIMATE citation (RLHF cost)
| model | over-refusal (REFUSED) | cluster-boot 95% CI | n | n_clusters |
|---|---|---|---|---|
| Opus-4.8 | 0.8 | [0.2, 1.0] | 20 | 3 |
| Sonnet-4.6 | 0.5 | [0.0, 1.0] | 14 | 3 |
| DeepSeek-v4 | 0.783 | [0.714, 0.875] | 23 | 3 |
| Llama-8b | 0.0 | [0.0, 0.0] | 24 | 3 |
| Mistral-lg | 0.864 | [0.75, 1.0] | 22 | 3 |
| GPT-5.5 | 0.0 | [0.0, 0.0] | 24 | 3 |
| Qwen3.7 | 0.583 | [0.25, 0.75] | 24 | 3 |
_Refusal of a legitimate audit citation = the over-refusal side of the security/utility tradeoff; clustered by scenario (single neutral pretext). **Unequal denominators:** the parsed n is attrited by UNPARSED unevenly across models (Sonnet 10/24 unparseable here vs GPT/Llama/Qwen 0/24), so this is a directional tradeoff signal, not a clean cross-model ranking — see the n column._

| model | parsed n | UNPARSED dropped |
|---|---|---|
| Opus-4.8 | 20 | 4 |
| Sonnet-4.6 | 14 | 10 |
| DeepSeek-v4 | 23 | 1 |
| Llama-8b | 24 | 0 |
| Mistral-lg | 22 | 2 |
| GPT-5.5 | 24 | 0 |
| Qwen3.7 | 24 | 0 |


## W4/W5 negative controls (Reviewer-2: give the negatives a table)
### W4 adaptive-harvest max lure-rate per (domain,victim) — single-shot injection is weak
| domain | victim | harvested lure_rate |
|---|---|---|
| procurement | Opus-4.8 | 0.0 |
| procurement | Sonnet-4.6 | 0.0 |
| procurement | GPT-5.5 | 0.0 |
| procurement | Qwen3.7 | 0.0 |
| procurement | DeepSeek-v4 | 0.167 |
| procurement | Mistral-lg | 0.0 |
| governance | Opus-4.8 | 0.0 |
| governance | Sonnet-4.6 | 0.0 |
| governance | GPT-5.5 | 0.0 |
| governance | Qwen3.7 | 0.0 |
| governance | DeepSeek-v4 | 0.0 |
| governance | Mistral-lg | 0.0 |
| incident_triage | Opus-4.8 | 0.0 |
| incident_triage | Sonnet-4.6 | 0.0 |
| incident_triage | GPT-5.5 | 0.0 |
| incident_triage | Qwen3.7 | 0.0 |
| incident_triage | DeepSeek-v4 | 0.0 |
| incident_triage | Mistral-lg | 0.0 |

### W5 weak-victim: baseline vs injected lure at D0 (leak is ENDOGENOUS, not injected)
| victim | baseline_lure | influence_pre_lure | injected_delta |
|---|---|---|---|
| Opus-4.8 | 0.0 | 0.012 | 0.012 |
| Llama-8b | 0.333 | 0.258 | -0.075 |
