# AI Power Atlas

Publication package for **AI stack: four structures of power at one checkpoint**.

A fact map of how compute, clouds, models, data, cyber and capital become the default environment: access is metered, dependency is locked in, and rent is collected.

Site URL after GitHub Pages deploy:

<https://scadastrangelove.github.io/profgames/aipower/>

## Artifacts

| File | Description |
| --- | --- |
| [`index.html`](index.html) | Small entry page for the AI Power package. |
| [`ai-power-atlas.html`](ai-power-atlas.html) | Self-contained English interactive atlas: overview, story map, timeline, stack heatmap, fact catalog, claim checks and source index. |
| [`ai-power-atlas-ru.html`](ai-power-atlas-ru.html) | Self-contained Russian interactive atlas generated from the same v0.16 storygraph line. |
| [`ai_power_storygraph_en.json`](ai_power_storygraph_en.json) | Machine-readable English storygraph used by the atlas. |
| [`ai_power_storygraph_ru.json`](ai_power_storygraph_ru.json) | Russian v0.16 master storygraph with facts, claims, edges, sources and graph diagnostics. |
| [`preprint_release/`](preprint_release/) | **Machine-Speed Cyber and Poisoned Cognition: A Layer-Dependent Game-Theoretic Framework, with Empirical Probes** — HTML, PDF, Markdown source, figures, bibliography and the P1 red-team evidence bundle. |
| [`selective-permeability/`](selective-permeability/) | **Selective Permeability: A Behavioral-Security Metric for LLM Advisors, with Two Failure Modes of In-Context Provenance Workflows** — preprint (HTML/PDF/Markdown), figures F1–F9 (F9 = model × attack panorama), reproducible harness, and EN/RU write-ups. |

## Preprints

Two preprints are published alongside the atlas:

**P1 — *Machine-Speed Cyber and Poisoned Cognition*** (framework + probes):
- [`preprint_release/preprint.html`](preprint_release/preprint.html) — browser-readable self-contained version;
- [`preprint_release/preprint.pdf`](preprint_release/preprint.pdf) — paginated PDF;
- [`preprint_release/preprint.md`](preprint_release/preprint.md) — Markdown source;
- [`preprint_release/p1-redteam-release/`](preprint_release/p1-redteam-release/) — reproducibility bundle for the P1 red-team experiments.

**P2 — *Selective Permeability*** (behavioral-security metric + credential/provenance attacks):
- [`selective-permeability/preprint.md`](selective-permeability/preprint.md) — the preprint;
- [`selective-permeability/figures/F9_susceptibility_matrix.png`](selective-permeability/figures/F9_susceptibility_matrix.png) — the model × attack panorama;
- [`selective-permeability/blog/`](selective-permeability/blog/) — plain-language EN/RU write-ups;
- [`selective-permeability/aigeopol-labs/`](selective-permeability/aigeopol-labs/) — reproducible harness + data.

## Current Counts

- `203` facts
- `71` claims
- `28` claim checks
- `23` story arcs
- `379` story edges
- `307` sources
- `0` hanging arcs after connectivity checks

## Frame

The atlas does **not** argue that any single actor has total control over AI.
It maps structural power across the stack:

- energy, compute and chips;
- cloud and inference capacity;
- frontier models, open weights and vetted access;
- data licensing and telemetry;
- cyber vulnerability discovery and patching;
- decision-support and cognitive-security layers;
- governance, law, finance and rent.

The safe wording rule is simple: present contested or partial evidence as contested or partial. Do not turn model releases, cloud contracts or vendor claims into stronger geopolitical claims than the source can support.

## Provenance

This package was generated from the v0.16 master storygraph built during the AIgeopol research pass.
Chronology audit and pre-2022 backfill. Corrected the GPT-2 and Cloud TPU milestone sequence, added 15 primary-sourced facts including ten events in 2021, revised the formation claim, and added two connected story arcs that distinguish development, disclosure, availability, law, authorization, proposal, report and complaint.

Public JSON filenames are intentionally versionless. The current version remains inside `meta.version` and the changelog, while the URLs stay stable across rebuilds.

## Reuse

The JSON files are intended for agents and researchers. Keep stable ids when extending them, and preserve source URLs, confidence levels, statuses and caveats.
