# AI Power Atlas

English publication package for **AI Stack as Structural Power**.

Site URL after GitHub Pages deploy:

<https://scadastrangelove.github.io/profgames/aipower/>

## Artifacts

| File | Description |
| --- | --- |
| [`index.html`](index.html) | Small entry page for the AI Power package. |
| [`ai-power-atlas.html`](ai-power-atlas.html) | Self-contained interactive atlas: overview, story map, stack heatmap, fact catalog, claim checks and source index. |
| [`ai_power_storygraph_v0_11_en.json`](ai_power_storygraph_v0_11_en.json) | Machine-readable English storygraph used by the atlas. |

## Current Counts

- `122` facts
- `70` claims
- `26` claim checks
- `18` story arcs
- `230` story edges
- `183` sources
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

This English package was generated from the v0.11 master storygraph built during the AIgeopol research pass.
The v0.11 update merged a targeted heatmap backfill: 22 additional evidence signals, 2 new story arcs and explicit edges so previously sparse 2024-2025 model/data/cloud/cyber cells are represented.

## Reuse

The JSON is intended for agents and researchers. Keep stable ids when extending it, and preserve source URLs, confidence levels, statuses and caveats.
