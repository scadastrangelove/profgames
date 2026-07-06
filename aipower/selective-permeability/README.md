# Selective Permeability
### A Behavioral-Security Metric for LLM Advisors, with Two Failure Modes of In-Context Provenance Workflows

**Sergey Gordeychik** · CyberOK Research · [gordey@cyberok.ru](mailto:gordey@cyberok.ru)
Text: [CC BY 4.0](LICENSE) · Code: MIT (`aigeopol-labs/`)

A behavioral-security study of seven frontier / near-frontier LLM advisors. Instead of asking "did the
agent get fooled?", we measure a two-sided **selective permeability** — how well an agent *updates* on
legitimate, authorized evidence while *resisting* illegitimate influence — and use experimental-psychology
procedures (not claims about machine minds) as adversarial assays, including a benign synthetic version of
the social-engineering / phone-scam playbook.

**Headline (Fig. F9):** crude social pressure, forged tokens, and factual opinion-flip crack only the
weaker-aligned models. The **subtle** credential attacks — a polite request for the authority token, and
handing over the *real* authorization lever when it is merely labeled "routine" — crack even the frontier.
The behavioral cause (Fig. F8, W7d): a model's refusal posture tracks the **secrecy label**, not whether
the token actually authorizes anything.

## Read it

| File | What |
| --- | --- |
| [`preprint.md`](preprint.md) | The preprint (structured; evidence tiers explicit). |
| [`figures/`](figures/) | F1–F9. **F9** = the model × attack panorama; **F8** = label-vs-referent. |
| [`tables/TABLES.md`](tables/TABLES.md) | T1–T5 (+T2c), generated from the data. |
| [`blog/medium_EN.md`](blog/medium_EN.md) · [`blog/teletype_RU.md`](blog/teletype_RU.md) | Plain-language write-ups (EN / RU). |

## Supplementary

- [`HUMAN_VALIDATION.md`](HUMAN_VALIDATION.md) — human coding of the disclosure judge (leak-detection κ=1.0).
- [`W7d_LABEL_VS_REFERENT.md`](W7d_LABEL_VS_REFERENT.md) — the label-vs-referent dissociation.
- [`STATS_reviewer23.md`](STATS_reviewer23.md) — cluster-bootstrap CIs, per-trial mixed logit, W7c severity, negatives.
- [`GLMM.md`](GLMM.md) — hierarchical binomial logit (random intercepts + slopes).
- [`docs/`](docs/) — positioning, the psychology-as-assays framing, provenance manifest, verbatim attack dialogues.

## Reproduce

Everything regenerates from committed data with a stdlib-only harness (plus matplotlib/statsmodels for
figures/GLMM). See [`aigeopol-labs/REPRODUCE.md`](aigeopol-labs/REPRODUCE.md). Model calls go through
OpenRouter; provide your own key in `.secrets/openrouter.env` (**not included** — only `.env.example`).

```bash
python3 aigeopol-labs/src/code/make_tables.py     # -> tables/TABLES.md
python3 aigeopol-labs/src/code/make_figures.py    # -> figures/  (needs matplotlib)
python3 aigeopol-labs/src/code/analyze_w7b.py     # rebuilds w7b CSVs from judged raw (byte-identical)
```

## Prior work

This paper extends the earlier preprint from which the opinion-flip data in F9 is drawn:

> Gordeychik, S. (2026). *Machine-Speed Cyber and Poisoned Cognition: A Layer-Dependent Game-Theoretic
> Framework, with Empirical Probes.* PREPRINTS.RU. [doi:10.24108/preprints-3115766](https://doi.org/10.24108/preprints-3115766)
> — published in this repo under [`../preprint_release/`](../preprint_release/).

## Scope and caveats

Seven models, synthetic benign tasks, a single researcher. The numbers describe behavior under these
conditions; they are a behavioral map, not a security benchmark or a model leaderboard. The paper states
what is strong (audit dissociation; provenance-bound memory; label-vs-referent) and what is a pilot
(multi-turn ScamOps pressure) or a negative control.
