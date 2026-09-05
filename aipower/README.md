# AI Power Atlas

Publication package for **AI stack: four structures of power at one checkpoint**.

A fact map of how compute, clouds, models, data, cyber and capital become the default environment: access is metered, dependency is locked in, and rent is collected.

Site URL after GitHub Pages deploy:

<https://scadastrangelove.github.io/profgames/aipower/>

## Artifacts

| File | Description |
| --- | --- |
| [`index.html`](index.html) | Small entry page for the AI Power package. |
| [`ai-power-atlas.html`](ai-power-atlas.html) | Self-contained English interactive atlas: overview, story map, linked 2025–2026 cyber map, timeline, stack heatmap, fact catalog, claim checks and source index. |
| [`ai-power-atlas-ru.html`](ai-power-atlas-ru.html) | Russian atlas generated from the same v0.27 storygraph line, including the same cyber capability, incident, assurance and governance view. |
| [`ai_power_storygraph_en.json`](ai_power_storygraph_en.json) | Machine-readable English storygraph used by the atlas. |
| [`ai_power_storygraph_ru.json`](ai_power_storygraph_ru.json) | Russian v0.27 master storygraph with facts, claims, edges, sources and graph diagnostics. |
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

- `280` facts
- `71` claims
- `30` claim checks
- `25` exact story arcs in `6` analytical families
- `557` story edges
- `435` sources
- `0` hanging arcs after connectivity checks
- `4554` cross-references checked, `0` unresolved and `0` endpoint-kind mismatches

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

## Classifier Model

The release keeps legacy labels for auditability while separating fields used by the interface:

- `geography_raw` preserves every source label; `jurisdictions`, `regions`, `locations`, `institutional_scopes`, `geo_context` and `geographic_scopes` drive distinct filters;
- `actor_raw`, `actors_raw` and `actor_facets_legacy` preserve the old representation; `actor_entities`, `actor_types` and `actor_jurisdictions` remove joined labels and role/country collisions;
- every exact arc id is retained; `family_id` groups the 25 arcs into 6 analytical families, while `arc_kind=phase` marks chronology-first arcs.

The embedded `classifierAudit` records before/after counts and SHA-256 checks over fact ids, claim ids, exact arc ids, complete edge signatures and source URLs.

The safe wording rule is simple: present contested or partial evidence as contested or partial. Do not turn model releases, cloud contracts or vendor claims into stronger geopolitical claims than the source can support.

## Provenance

This package was generated from the v0.27 master storygraph built during the AIgeopol research pass.
Added a primary-source pass on state regulation and public assurance of AI cyber resilience: 30 facts across China, the United States, South Korea, Singapore, Russia, Five Eyes, the UK, Japan, Canada, the EU, Australia and the FSB; one cross-jurisdiction assurance-stack arc; one claim check; and explicit distinctions among binding, supervisory, voluntary, draft and future-effective measures. A second sweep added the AISI evaluation incident, NCSC interim runtime controls and the EU GPAI enforcement checkpoint with agent-scope guidance.

Public JSON filenames are intentionally versionless. The current version remains inside `meta.version` and the changelog, while the URLs stay stable across rebuilds.

## Reuse

The JSON files are intended for agents and researchers. Keep stable ids when extending them, and preserve source URLs, confidence levels, statuses and caveats.
