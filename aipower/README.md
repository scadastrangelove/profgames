# AI Power Atlas

Publication package for **AI Stack as Structural Power**.

Site URL after GitHub Pages deploy:

<https://scadastrangelove.github.io/profgames/aipower/>

## Artifacts

| File | Description |
| --- | --- |
| [`index.html`](index.html) | Small entry page for the AI Power package. |
| [`ai-power-atlas.html`](ai-power-atlas.html) | Self-contained English interactive atlas: overview, story map, stack heatmap, fact catalog, claim checks and source index. |
| [`ai-power-atlas-ru.html`](ai-power-atlas-ru.html) | Self-contained Russian interactive atlas generated from the same v0.12 storygraph line. |
| [`ai_power_storygraph_v0_12_en.json`](ai_power_storygraph_v0_12_en.json) | Machine-readable English storygraph used by the atlas. |
| [`ai_power_storygraph_v0_12_ru.json`](ai_power_storygraph_v0_12_ru.json) | Russian v0.12 master storygraph with facts, claims, edges, sources and graph diagnostics. |

## Current Counts

- `135` facts
- `70` claims
- `26` claim checks
- `20` story arcs
- `251` story edges
- `196` sources
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

This package was generated from the v0.12 master storygraph built during the AIgeopol research pass.
The v0.12 update adds capital-mix framing, cyber weaponization caveats, corporate decision-support backfill, explicit story-arc-to-thesis rendering, and multi-lane timeline normalization so multi-layer facts appear on every relevant stack layer.

## Reuse

The JSON files are intended for agents and researchers. Keep stable ids when extending them, and preserve source URLs, confidence levels, statuses and caveats.
