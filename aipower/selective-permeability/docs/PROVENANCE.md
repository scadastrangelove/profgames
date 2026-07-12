# Provenance manifest (camera-ready checklist)

**Run dates (OpenRouter):** 2026-07-04 (W0–W6), 2026-07-05 (W7b, W9/W9b, W8), and 2026-07-12
(W7e emphasis-matched control). Pin the exact per-wave
timestamps from `run_id` fields in `artifacts/raw/*.jsonl` (each is `labs-<phase>-<unixtime>`).

**Access:** raw chat-completions over OpenRouter; stdlib-only harness; role separation
(victim / auditor panel / attacker / critic / summarizer are distinct model families).

## Model roster (exact OpenRouter slugs) — TWO configs, pinned per wave
Two victim configs were used; **provenance is pinned by the hash stored in each raw record, not the
current on-disk file** (on-disk configs have since been edited/split and no longer byte-match).
- **6-victim config (W1 / gated waves):** opus-4.8 · sonnet-4.6 · gpt-5.5 · qwen3.7-max · deepseek-v4-pro ·
  mistral-large-2512 (**no llama**). W1 raw records embed `model_config_hash =
  4c345f11b2e60acd8fd8f52816a88a0c49406c1abcf02a1dbe26cec483472b13` (the config *as run* — trust this, not
  the current `src/models_v2.json`, which has changed).
- **7-victim config (token W7b/W7c/W7d/W7e, memory):** the six above **+ meta-llama/llama-3.1-8b-instruct
  (weak control)**, file `src/config/models_v2.json` (current on-disk sha256 `6767ccc…`). ⚠️ These raw
  records do **not** embed a config hash — a provenance gap to close at camera-ready.
Auditors/critic/summarizer: google/gemini-2.5-pro · anthropic/claude-opus-4.8 · openai/gpt-5.5. Disclosure
judge: openai/gpt-5.5 (non-Anthropic ⇒ Sonnet family-clean); 2nd judge anthropic/claude-opus-4.8 (κ only).

## Sampling parameters (per wave)
| wave | K | victim config | victim temp | notes |
|---|---|---|---|---|
| W1 gated | 6 | 6-victim (no llama) | 0.7 | 5 defense gates; auditor temp 0.0 |
| W6/W8 ScamOps | 4 | 6-victim (+llama for W8) | 0.7 | multi-turn; consensus 3-of-5 |
| W7b/W7c token | 8 | 7-victim | 0.7 | W7b 3 pretexts; W7c protected/neutral; judge temp 0.0 |
| W7d label-vs-referent | 6 | 7-victim | 0.7 | 2×2 referent×label; inline gpt-5.5 judge (max_tokens 2000) |
| W7e emphasis-matched | 6 | 7-victim | 0.7 | 2×2 referent×policy; 504 target calls; cross-family secondary judge; full replies |
| W9/W9b memory | 4 | 7-victim | 0.7 (read) | seed deterministic; compact summarizer temp 0.3 |

## Prompt templates and hash coverage (honest)
Frozen in `src/code/labs_lib.py` and per-runner files. **Hash coverage is partial:** only the **W1/gated**
raw records embed `model_config_hash`, `scenario_hash`, `payload_hash` (sha256; example payload_hash
`1bc44e40aed78bce…`). The **token (W7b/W7c/W7d) and memory (W9b)** raw records store the full victim
`reply` + condition metadata (model, scenario, pretext/cell, sample, judge_label) but **not** prompt/
payload/scenario hashes — reconstruct the prompt from the frozen runner + `scenarios/mvp_v2.jsonl`. Adding
hash-stamping to the token/memory runners is a camera-ready item. Scenarios frozen: `scenarios/mvp_v2.jsonl`
(generator `scenarios/build_v2.py`).

**W7e improves this prospectively:** every raw record stores the prompt-template hash
`967da2f567b77cade22f9400e341977d67cdce1c2d7f76b5752afe1420f0e1f6`, full response, requested model,
returned model, provider/usage metadata when supplied, and run start time. The shipped run artifact sha256
is `b2f009e0645be3e6016963eae1382a15c78e4d696a26c184920d11663826c840`; the shipped scenario and model
config hashes are `3d069b5697f8…` and `6767cccb8fc5…`, respectively. These latter two hashes are recorded in
this manifest rather than embedded in each W7e row.

## Parsers (version = git state of labs_lib.py at run)
- victim answer: regex `ANSWER=(Yes|No);CONFIDENCE=<int>` / decision JSON {answer,confidence,brief_reason}.
- auditor score: `SCORE=<int 0-100>`.
- token-disclosure judge (W7b/W7c): provision-vs-mention classifier + deterministic pre-classifier, run
  upstream on the compute host (script `rejudge_token2.py`, **not shipped** — the *judged* raw
  `w7b_token_judged.jsonl` / `w7c_token_judged.jsonl` is what ships). Aggregation judged-raw → CSVs is
  `analyze_w7b.py` / `analyze_token3.py` (shipped; `analyze_w7b.py` verified to reproduce the derived CSVs
  byte-for-byte). For **W7d** the judge is inline in `run_labs_labelref.py` (shipped). For **W7e**, exact
  token containment is deterministic; the secondary PROVIDED/MENTIONED/REFUSED classifier uses Anthropic
  for GPT victims and GPT for every other family. Runner and analyzer are shipped as
  `run_labs_labelref_matched.py` and `analyze_labelref_matched.py`.

## To finalize at camera-ready
Freeze exact checkpoint dates per model (OpenRouter may roll slugs); archive raw prompts + parser
regex snapshot; record OpenRouter model `created`/version fields if exposed.
