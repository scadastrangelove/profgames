# ProfGames — English Starter Layer

This folder contains the first English-facing artifacts for the **ProfGames** cycle and the parallel **AI-Mind / psAIcho** psychological layer.

The canonical project is still the Russian version in the repository root. The files here are a publication and onboarding layer for English-speaking readers: they preserve stable ids, source URLs and evidence levels, while providing concise English summaries.

## Artifacts

| Artifact | Description |
| --- | --- |
| [`aimind.html`](aimind.html) | English reader layer for AI-Mind / psAIcho: 85 signals, PH/HB/AB taxonomy, Atlas routing map, boundary patterns and links to canonical machine-readable artifacts. |
| [`a-events.html`](a-events.html) | English-facing A1 event explorer: 177 signals from 2020-2026, filters by year, region, evidence level and framework dimension. |
| [`factcheck.html`](factcheck.html) | English-facing fact-check audit view: 65 claims, 20 evidence gaps, filters by verification status. |
| [`factcheck.json`](factcheck.json) | Machine-readable English audit layer. Original Russian canonical wording is preserved in `original_ru`. |
| [`presentations/profgames-cycle-talk-en.pptx`](presentations/profgames-cycle-talk-en.pptx) | 30-slide English talk deck about the cycle, with emphasis on the Russian fork from article C. |
| [`presentations/profgames-cycle-talk-en-contact-sheet.png`](presentations/profgames-cycle-talk-en-contact-sheet.png) | Contact sheet for quickly reviewing the deck. |

## Translation Status

`factcheck.json` is not a blind full-text translation of the root `factcheck.json`.
It is an English audit layer:

- stable claim ids are unchanged;
- statuses and A/B/C/D evidence levels are unchanged;
- source URLs are preserved;
- each claim receives a concise English title and claim summary;
- the original Russian topic, claim, caveats, corrections and recommended wording remain in `original_ru`.

This makes the pack usable for English review without losing the canonical wording.

## Links

- Main site: <https://scadastrangelove.github.io/profgames/>
- English AI-Mind reader: [`aimind.html`](aimind.html)
- English A1 event explorer: [`a-events.html`](a-events.html)
- Canonical AI-Mind dataset: [`../aimind/aimind_signals.jsonl`](../aimind/aimind_signals.jsonl)
- Canonical fact-check pack: [`../factcheck.json`](../factcheck.json)
- Canonical A1 event dataset: [`../profgames_ai_signals.jsonl`](../profgames_ai_signals.jsonl)
- Telegram: <https://t.me/aiakyn>
- Teletype: <https://teletype.in/@sergey_gordey>
