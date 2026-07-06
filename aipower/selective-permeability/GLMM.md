# Hierarchical binomial logit (random intercepts: victim + scenario)

Per-sample outcomes reconstructed exactly from stored cell rates (rate×K = integer successes). Variational-Bayes fit (statsmodels BinomialBayesMixedGLM). Log-odds; OR = exp(coef).

### W1 (D0): lure outcome by condition — positive-update vs influence-leak
`y ~ C(condition, Treatment('influence'))` + (1|victim) + (1|scenario);  n=3852 samples

| fixed effect | log-odds | 95% CrI | odds ratio |
|---|---|---|---|
| Intercept | -4.26 | [-4.42, -4.11] | 0.01 |
| C(condition, Treatment('influence'))[T.authorized_relevant] | +0.44 | [+0.01, +0.88] | 1.55 |
| C(condition, Treatment('influence'))[T.positive_relevant] | +6.33 | [+6.13, +6.54] | 562.75 |

_Reference = influence (leak). A positive `positive_relevant` coefficient = the update side sits above the leak side at baseline (two-sided permeability)._

### W9b (memory+rag): durable outcome by item_kind × defense — random intercepts
`y ~ C(item_kind, Treatment('laundered_forged')) * C(defense, Treatment('none'))` + (1|victim) + (1|scenario);  n=1344 samples

| fixed effect | log-odds | 95% CrI | odds ratio |
|---|---|---|---|
| Intercept | -1.72 | [-1.88, -1.55] | 0.18 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true] | +3.37 | [+3.17, +3.58] | 29.21 |
| C(defense, Treatment('none'))[T.cooling_off] | -0.55 | [-0.86, -0.24] | 0.58 |
| C(defense, Treatment('none'))[T.memory_quarantine] | -1.24 | [-1.58, -0.90] | 0.29 |
| C(defense, Treatment('none'))[T.provenance_bound] | -1.19 | [-1.52, -0.87] | 0.30 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.cooling_off] | +0.68 | [+0.29, +1.07] | 1.97 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.memory_quarantine] | -0.48 | [-0.92, -0.04] | 0.62 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.provenance_bound] | +1.94 | [+1.53, +2.34] | 6.94 |

_Reference = laundered_forged × none. `item_kind[authorized_true]` > 0 ⇒ real-token updates are adopted more than forged ones are leaked (two-sidedness). The `authorized_true:provenance_bound` interaction captures whether the token gate widens that gap (selective permeability)._

### W9b random-SLOPES robustness — `(item_kind | victim)` (Barr 2013 maximal RE)
`y ~ C(item_kind, Treatment('laundered_forged')) * C(defense, Treatment('none'))` + (item_kind|victim) + (1|scenario);  n=1344 samples

| fixed effect | log-odds | 95% CrI | odds ratio |
|---|---|---|---|
| Intercept | -1.97 | [-2.14, -1.80] | 0.14 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true] | +3.48 | [+3.27, +3.68] | 32.31 |
| C(defense, Treatment('none'))[T.cooling_off] | -0.68 | [-1.00, -0.35] | 0.51 |
| C(defense, Treatment('none'))[T.memory_quarantine] | -1.50 | [-1.84, -1.15] | 0.22 |
| C(defense, Treatment('none'))[T.provenance_bound] | -1.44 | [-1.78, -1.10] | 0.24 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.cooling_off] | +0.80 | [+0.40, +1.19] | 2.22 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.memory_quarantine] | -0.18 | [-0.60, +0.23] | 0.83 |
| C(item_kind, Treatment('laundered_forged'))[T.authorized_true]:C(defense, Treatment('none'))[T.provenance_bound] | +2.20 | [+1.79, +2.61] | 9.02 |

_Adding the maximal by-victim random slope leaves the `authorized_true:provenance_bound` interaction in the same direction and significant; the intercepts-only model is the more conservative report. Exact coefficients regenerate from this script (VB fit)._

