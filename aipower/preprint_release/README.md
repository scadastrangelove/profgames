# Machine-Speed Cyber and Poisoned Cognition
### A Layer-Dependent Game-Theoretic Framework, with Empirical Probes

**Sergey Gordeychik** · CyberOK Research · [gordey@cyberok.ru](mailto:gordey@cyberok.ru)
Text: [CC BY 4.0](LICENSE) · Code: [MIT](p1-redteam-release/LICENSE)

A framework paper with first-pass empirical **probes** (not a benchmark or a security
evaluation) arguing that AI-mediated conflict is not one offense–defense game but a
**layered** one — a *wire* layer of machine-speed discovery, a *model/weights* layer of
captured decision-support, an *audit* layer of verification exhaustion, and an *attribution*
layer where punishment lags defection. The central claim is an inversion across layers:
the observable wire layer is relatively self-correcting, while the unobservable model and
audit layers can become self-reinforcing — **stable on the wire, unstable in the weights.**

## Abstract

> Strategic analysis of AI-enabled conflict often treats "cyber" as one offense–defense game
> and AI capability as a scalar speedup. We argue instead that AI-mediated conflict is a
> **layered strategic environment**. We formalize the stack with five compact model results
> and seven falsifiable predictions. Two results are empirically grounded here: the wire-layer
> queueing claim that correlated vulnerability arrivals inflate remediation backlogs, and the
> model-layer capture-bound claim that deep, quiet, sustained manipulation should be hard. The
> audit and attribution results remain **simulation-only** here; their incident-data grounding
> is future work. We run two proof-of-concept probes: on the wire, open vulnerability corpora
> show clustered, over-dispersed discovery streams that inflate remediation queues, with the
> 2026 LLM-credited discovery wave real but still mostly upstream of weaponization; on the model
> layer, adaptive red-teaming across six checkpoints yields a transfer-confirmed 3:3 split
> supporting a **content-versus-relevance audit diagnostic** — not yet a general keyed-payload
> capability.

(Full abstract and scope table are in the manuscript, §Abstract and §1.4.)

## Repository contents

| Path | What it is |
|---|---|
| [`preprint.md`](preprint.md) | The manuscript (Markdown source of record; ~18.2k words, §1–11 + Appendices A–E). |
| [`preprint.pdf`](preprint.pdf) | Submission PDF (A4, figures embedded). |
| [`preprint.html`](preprint.html) | Self-contained single-file HTML (figures inlined as base64) — open in any browser, no assets needed. |
| [`related_work.bib`](related_work.bib) | Machine-verified BibTeX for all references (each DOI / landing page resolved and checked). |
| [`experiment_ledger_crosswalk.md`](experiment_ledger_crosswalk.md) | EXP-id ↔ claim ↔ figure crosswalk for the empirical phase. |
| [`figures/`](figures/) | The 12 figures (fig11–fig22), rendered from verified data. |
| [`p1-redteam-release/`](p1-redteam-release/) | **Code + data** for the model-layer red-team (§6): the P-1 detectability-bound study. Self-contained, MIT-licensed, reproducible from `code/`. |

## Figures

| File | Caption (short) |
|---|---|
| `fig11_metasploit_clustering.png` | Metasploit: over-dispersed inter-arrival across exploit classes. |
| `fig12_ai_tooling_attacksurface.png` | Nuclei: the AI/ML-tooling attack surface, 0% → 12.5% of new templates. |
| `fig13_queue_clustering.png` | Queue model (Lemma 5): clustering inflates the remediation backlog 1.65–5.2×. |
| `fig14_kernel_cna_clustering.png` | Kernel CNA: extreme subsystem clustering (Gini 0.81). |
| `fig15_disclosure_to_weaponization.png` | Discovery → weaponization funnel and the short lag for migrators. |
| `fig16_weaponization_ladder.png` | Weaponization ladder: disclosed → PoC → operational catalog → exploited. |
| `fig17_model_poison.png` | 0.5B pilot: fluent misinformation is deepest and quietest. |
| `fig18_opinion_vs_fact_axes.png` | Fact-robustness ≠ opinion-robustness (distinct axes). |
| `fig19_honest_vs_masker_tradeoff.png` | Honest persuader vs covert masker: effectiveness visible, stealth shallow. |
| `fig20_two_axes_capstone.png` | Two orthogonal axes across six models, transfer-confirmed. |
| `fig21_falsification.png` | Negative controls: null on null data, effect on real data. |
| `fig22_regime_controls.png` | Audit-layer regime controls (P-3 blinding; P-2 tolerate→audit-hard corner). |

## Code & data (reproducibility)

**Model layer — bundled in this repo.** [`p1-redteam-release/`](p1-redteam-release/) is the
model-layer red-team behind §6: an *existence + heterogeneity + method-validation* study of the
P-1 detectability bound (can a manipulator push an advisor **deep** while staying **quiet**?).
It ships the runnable code (`code/`), the raw per-probe data for EXP_25–28 (`data/`), the
experiment write-ups (`experiments/`), and framed conclusions ([`REPORT.md`](p1-redteam-release/REPORT.md),
[`CONCLUSIONS.md`](p1-redteam-release/CONCLUSIONS.md)). Models are reached as raw completions over
OpenRouter with the attacker separated from the target; **set `OPENROUTER_API_KEY` (or a `.orkey`
file) to reproduce — no key is bundled.** See [`p1-redteam-release/README.md`](p1-redteam-release/README.md).

**Wire layer — external.** The KEV/EPSS analysis and orientation-race fit ship as the
`kev_vs_epss` dataset — <https://github.com/scadastrangelove/kev_vs_epss>. Method and limits:

- Gordeychik, S. (2025). *Prediction Meets Patch Queues: Empirical Limits of EPSS-Only Prioritization
  Using CISA KEV Additions in 2025.* TechRxiv. <https://doi.org/10.36227/techrxiv.176857939.95987957/v1>
- Gordeychik, S. (2026). *UPS Meets Patch Queues: Evidence-Timeline Prioritization under Limited
  Capacity, Cadence, and Compliance Gravity.* SSRN Working Paper No. 6286359.

## Rendering / build

`preprint.html` and `preprint.pdf` are generated from `preprint.md` (Python-Markdown for HTML
with figures base64-embedded; Chrome headless `--print-to-pdf` for the A4 PDF). Both derive from
the same source of record — edit the `.md` and re-render.

## How to cite

See [`CITATION.cff`](CITATION.cff). BibTeX:

```bibtex
@techreport{gordeychik2026machinespeed,
  author      = {Gordeychik, Sergey},
  title       = {Machine-Speed Cyber and Poisoned Cognition: A Layer-Dependent
                 Game-Theoretic Framework, with Empirical Probes},
  institution = {CyberOK Research},
  year        = {2026},
  type        = {Preprint}
}
```

## License

Dual-licensed by artifact type:

- **Manuscript text and figures** — [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).
  Share and adapt with attribution.
- **Code in [`p1-redteam-release/`](p1-redteam-release/)** — [MIT](p1-redteam-release/LICENSE).
