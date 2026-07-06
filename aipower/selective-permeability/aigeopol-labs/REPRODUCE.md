# Reproducibility index — Human–Agent Influence Resilience lab

Self-contained harness + raw/derived data for the selective-permeability experiments (2026-07-04/05).
Models reached as raw completions over OpenRouter; put your own key in `.secrets/openrouter.env`
(NOT included). Runs in Docker; see `src/docs/RUNBOOK_DOCKER.md` and `src/docs/RUNBOOK_V2.md`.

## Layout
```
src/code/        harness (stdlib only): labs_lib, run_labs_*, analyze_*, mem_store, harvest_lures, ...
src/scenarios/   mvp_v2.jsonl (+ build_v2.py generator); mvp_3x3x3.jsonl (v1)
src/config/      models_v2.json (7 victims + 3 auditor families), models.json (v1)
src/docs/        RUNBOOK_DOCKER, RUNBOOK_V2, METHOD_CRITIQUE_AND_V2, RESULTS_v2
artifacts/raw/   per-wave raw records (jsonl)
artifacts/derived/  per-wave analysis (csv/json)
artifacts/mem/   long-horizon memory store (store.json)
```

## Models under test (victims)
`anthropic/claude-opus-4.8`, `anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`, `qwen/qwen3.7-max`,
`deepseek/deepseek-v4-pro`, `mistralai/mistral-large-2512`, and `meta-llama/llama-3.1-8b-instruct`
(weak-model control). Auditor/critic/summarizer families: google/gemini-2.5-pro, anthropic, openai.
Runs dated 2026-07-04..05; pin checkpoints + API dates before citing.

## Wave → data → what it shows
| wave | raw | derived | shows |
|------|-----|---------|-------|
| W1 gated matrix | `raw/w1_gated.jsonl` | `derived/mvp_v2_*` | auditor dissociation; gates over-block; opus sticky |
| W4 adaptive harvest | `raw/w4_lures.jsonl` | — | frontier resist adaptive single-shot lures (max 0.167) |
| W5 weak-victim gate | `raw/w5_gated_weak.jsonl` | `derived/w5_*` | weak-model leak is endogenous, not injected |
| W6/W8 ScamOps | `raw/w6_scamops.jsonl`,`w8_scamops.jsonl` | `derived/w6_*`,`w8_*` | authority-seizure flips mistral; consensus weak; cooling-off best |
| W7b/W7c token flagship | `raw/w7b_token_judged.jsonl`,`w7c_token_judged.jsonl` | `derived/w7b_*` (rebuild: `python3 code/analyze_w7b.py`, verified byte-identical) | no-instruction: most models emit the token (compliance, not breach); protected (nondisclosure instruction): leak confined to Mistral/Llama; neutral control: over-refusal of a legit citation. Forgery accepted by Mistral/Llama; registry fixes Mistral. Judge human-validated as a leak detector (κ=1.0), not a clean-vs-hedged classifier — see `../review_pack/HUMAN_VALIDATION.md`. |
| W9/W9b memory | `raw/w9b_mem_read.jsonl` | `derived/w9b_*` | provenance-bound: clear win in memory, marginal (CI-overlapping) in RAG; wiki compaction=source amnesia (mitigable per-item, W9d) |
| W8 ScamOps capture (7-model) | `raw/w8_scamops.jsonl` (4) + `raw/w8_scamops_extra.jsonl` (Sonnet/Qwen/Llama, no-defense) | `derived/w8_capture.csv` | crude pressure flips only weak models (Mistral/Llama 1.0; frontier ≈0). Rebuild: `analyze_scamops.py --jsonl <cat of both>`. |
| F9 panorama (opinion-flip cols) | prior paper EXP-29 (`~/…/exp29_keying/raw/analysis_summary_full.json`) → `derived/exp29_flip.csv` | — | 2 columns (keyed opinion-flip mean/worst per model) imported into F9. **Source: Gordeychik 2026, PREPRINTS.RU, doi:10.24108/preprints-3115766** (CC BY 4.0). |
| W7d label-vs-referent | `raw/w7d_labelref.jsonl` | `derived/w7d_labelref.csv` | guard behavior tracks the secrecy LABEL (Δ0.87), not the token's actual authority/REFERENT (Δ0.04); models guard an inert public string and hand over the real lever — security theater, not a threat model. Runner `run_labs_labelref.py`, analyze `analyze_labelref.py`. |

## Reproduce a wave (example, gated matrix)
```bash
cd src
docker build -t aigeopol-labs:latest .
docker run --rm --env-file ../.secrets/openrouter.env -v $PWD/../artifacts:/work/artifacts \
  aigeopol-labs:latest code/run_labs_gated.py --scenarios scenarios/mvp_v2.jsonl \
  --models config/models_v2.json --out /work/artifacts/raw/w1_gated.jsonl --k 6 --workers 12 --preflight all
docker run --rm -v $PWD/../artifacts:/work/artifacts aigeopol-labs:latest code/analyze_v2.py \
  --gated-jsonl /work/artifacts/raw/w1_gated.jsonl --out-dir /work/artifacts/derived --prefix mvp_v2
```
Full command set per wave: `src/docs/RUNBOOK_V2.md`. Narrative results: `src/docs/RESULTS_v2.md`.
Related-work positioning: `../docs/POSITIONING.md`; example attack dialogues: `../docs/DIALOGUES_token_extraction.md`.
