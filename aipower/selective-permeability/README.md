# Selective Permeability
### A Behavioral-Security Metric for LLM Advisors, with Two Failure Modes of In-Context Provenance Workflows

**Sergey Gordeychik** · CyberOK Research · [gordey@cyberok.ru](mailto:gordey@cyberok.ru)
Text: [CC BY 4.0](LICENSE) · Code: MIT (`aigeopol-labs/`)

A behavioral-security study of seven selected LLM advisors, including a deliberately weak control.
Selective permeability reports the operating point between updating on authorized evidence and leaking
under illegitimate influence. Its scalar form is Youden's J (`update - leak`), so the release also reports
both components and does not treat the difference as a deployment utility function.

The main result is narrower than a model ranking. Bearer-style in-context provenance can fail when the
authority token leaves the model or when compaction erases its origin metadata. W7e removes W7d's unequal
instruction-emphasis confound: under exact-token containment, explicit in-context policy polarity has a
pooled effect of 0.726 [0.655, 0.821], while the token's functional referent has an effect of 0.004
[-0.036, 0.036]. The policy effect is larger in all seven selected model rows. W9d shows that
token-preserving summarization restores the compacted-wiki channel, but not a provenance-control premium
over the no-defense condition.

## Read it

| File | What |
| --- | --- |
| [`preprint.md`](preprint.md) | Main manuscript source (structured; evidence tiers explicit). |
| [`preprint.html`](preprint.html) | Self-contained publication HTML with all figures inlined. |
| [`preprint.pdf`](preprint.pdf) | Publication PDF with figures, appendices, result tables, and references. |
| [`references.md`](references.md) | Verified bibliography used by the publication build. |
| [`figures/`](figures/) | F1–F9. **F9** = the model × attack panorama; **F8** = emphasis-matched policy-vs-referent. |
| [`tables/TABLES.md`](tables/TABLES.md) | Generated operating points, full W7 cells, missingness bounds, and bootstrap intervals. |
| [`blog/medium_EN.md`](blog/medium_EN.md) · [`blog/teletype_RU.md`](blog/teletype_RU.md) | Plain-language write-ups (EN / RU). |

## Supplementary

- [`HUMAN_VALIDATION.md`](HUMAN_VALIDATION.md) — human coding of the disclosure judge (leak-detection κ=1.0).
- [`W7d_LABEL_VS_REFERENT.md`](W7d_LABEL_VS_REFERENT.md) — original policy-vs-referent assay and its prompt-strength caveat.
- [`W7e_EMPHASIS_MATCHED.md`](W7e_EMPHASIS_MATCHED.md) — completed emphasis-matched replication and run-integrity record.
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
python3 aigeopol-labs/src/code/analyze_w7b.py     # rebuilds token-out + severity CSVs
python3 aigeopol-labs/src/code/analyze_labelref.py # rebuilds W7d full 2x2 analysis
python3 aigeopol-labs/src/code/analyze_labelref_matched.py # rebuilds W7e analysis
```

## Build the publication files

The publication build combines the manuscript, result tables, references, and nine figures into one
self-contained HTML file and an A4 PDF. Images are embedded in the HTML, so the published document has
no runtime dependencies.

```bash
python3 -m pip install -r requirements-publication.txt
python3 build_preprint.py
```

Chrome or Chromium is required for PDF rendering. Use `python3 build_preprint.py --html-only` when only
the self-contained HTML is needed.

## Prior work

This paper extends the earlier preprint from which the opinion-flip data in F9 is drawn:

> Gordeychik, S. (2026). *Machine-Speed Cyber and Poisoned Cognition: A Layer-Dependent Game-Theoretic
> Framework, with Empirical Probes.* PREPRINTS.RU. [doi:10.24108/preprints-3115766](https://doi.org/10.24108/preprints-3115766)
> — published in this repo under [`../preprint_release/`](../preprint_release/).

## Scope and caveats

Seven selected model aliases, three synthetic decision domains, and one researcher. W7b/W7c store only
400-character response excerpts; W7d and W7e each have only three scenario clusters; and the severity
subset has one human coder. W7e tests policy polarity in user context, not system/developer-policy
placement. The numbers describe these conditions; they are a behavioral map, not a security benchmark,
provider comparison, or alignment ordering.
