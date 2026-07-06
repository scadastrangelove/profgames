# Runbook v2 (gated architecture)

v2 makes defenses **real gates** and the auditor panel **load-bearing**. See
`docs/METHOD_CRITIQUE_AND_V2.md` for the why. v1 files stay runnable; v2 uses new scenarios/config.

Build scenarios (once, no API):
```bash
python3 scenarios/build_v2.py
python3 code/validate_scenarios.py --scenarios scenarios/mvp_v2.jsonl
```

Everything runs in Docker on Tamm, detached (survives SSH drop). Prereq: funded key in
`~/aigeopol-labs/.secrets/openrouter.env` (v1 key is exhausted). Sync + build:
```bash
rsync -az --delete --exclude artifacts --exclude .secrets src/ gordey@85.142.100.8:/home/gordey/aigeopol-labs/src/
ssh gordey@85.142.100.8 'cd ~/aigeopol-labs/src && sudo docker build -t aigeopol-labs:latest .'
```

Detached wave (pattern):
```bash
ssh gordey@85.142.100.8 'cd ~/aigeopol-labs/src && sudo docker run -d --name W --network host \
  --env-file ~/aigeopol-labs/.secrets/openrouter.env \
  -v ~/aigeopol-labs/artifacts:/work/artifacts aigeopol-labs:latest <cmd>'
# progress: sudo docker logs -f W
```

## Waves

- **W0 smoke** — 1 victim family, 1 domain, tiny:
  `code/run_labs_gated.py --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out /work/artifacts/raw/w0.jsonl --k 2 --victim-family openai --defense-level D0_no_defense --defense-level D2_relevance_provenance_independence --workers 4 --preflight all`

- **W1 gated selective-permeability matrix** (the signature; ~5.9k calls):
  `code/run_labs_gated.py --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out /work/artifacts/raw/w1_gated.jsonl --k 6 --workers 12 --preflight all`

- **W2 ladder** (multi-turn micro-commitment + sustain; ~150 calls):
  `code/run_labs_ladder.py --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out /work/artifacts/raw/w2_ladder.jsonl --workers 6 --preflight first`

- **W3 remediation** (purge/quarantine/snapshot/taint; ~150 calls):
  `code/run_labs_remediation.py --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out /work/artifacts/raw/w3_remediation.jsonl --workers 6 --preflight first`

- **W4 calibrated lures** (optional, adaptive; ~700 calls) — then re-run W1 on the merged bank:
  `code/harvest_lures.py --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out /work/artifacts/raw/w4_lures.jsonl --iters 5 --k 6 --workers 6`

- **W5 analyze** (no API):
  `code/analyze_v2.py --gated-jsonl /work/artifacts/raw/w1_gated.jsonl --out-dir /work/artifacts/derived --prefix mvp_v2`

Outputs: `mvp_v2_selective_permeability.csv` (two-sided SP per defense×victim), `mvp_v2_gate_effect.csv`
(quarantine rate + leak reduction vs D0), `mvp_v2_auditor_dissociation.csv` (content vs relevance/
provenance/independence by ground-truth label), `mvp_v2_summary.json`.

Read (UPDATED — the pre-registered hypothesis did NOT hold): we expected D2 (relevance/provenance gate)
to give the highest selective permeability. The actual result is the opposite and more honest: on frontier
models illegitimate leakage is already ≈0, so **every gate over-blocks legitimate updates and D0 (no gate)
has the highest SP** (D0 0.73 [0.63,0.82] vs all gates lower; T5a, F6). The audit panel is a strong
*detector* but a poor *deployable gate* on already-robust models (§7.1). Report SP with the multiplicity-
preserving cluster bootstrap (`bootstrap_ci.py`).

## W7b/W7c/W7d — token disclosure, protected/neutral, label-vs-referent
- **W7b** disclosure+forgery: `run_labs_token.py` (or judged raw already in `artifacts/raw/w7b_token_judged.jsonl`);
  rebuild derived CSVs with `python3 code/analyze_w7b.py` → `w7b_disclosure.csv`, `w7b_forgery.csv`.
- **W7c** protected (in-context nondisclosure policy) + neutral (legit citation): `run_labs_token3.py
  --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json --out artifacts/raw/w7c_token.jsonl --k 8`;
  judge → `w7c_token_judged.jsonl`; `analyze_token3.py`. Report by severity: token-out = PROVIDED+MENTIONED (F7).
- **W7d** label-vs-referent 2×2: `run_labs_labelref.py --scenarios ... --models config/models_v2.json
  --out artifacts/raw/w7d_labelref.jsonl --k 6` (inline gpt-5.5 judge, needs env key); `analyze_labelref.py`.
- Extra stats (cluster-boot, per-trial logit, W7c token-out, W4/W5): `reviewer23_stats.py`.

## W9 — Long-horizon memory (token-laundering + wiki-drift / source amnesia)
GENUINE cross-run persistence: the store lives on the mounted volume; seed/compact/read are SEPARATE
docker runs sharing /work/artifacts/mem/store.json (the write is NOT in the reader's prompt).

  # seed (NO API): deterministic control items (authorized_true real-token / laundered_forged
  #   forged-token / benign) to the store. Add --advisor-write to probe self-laundering (API).
  docker run --rm -v ~/aigeopol-labs/artifacts:/work/artifacts aigeopol-labs:latest \
    code/run_labs_mem.py --phase seed --scenarios scenarios/mvp_v2.jsonl \
    --models config/models_v2.json --store /work/artifacts/mem/store.json

  # compact (API): summarize stored notes into wiki pages; records issuer tokens retained (source amnesia)
  docker run --rm --env-file .../openrouter.env -v ...:/work/artifacts aigeopol-labs:latest \
    code/run_labs_mem.py --phase compact --scenarios scenarios/mvp_v2.jsonl \
    --models config/models_v2.json --store /work/artifacts/mem/store.json --summarizer google/gemini-2.5-pro

  # read (API, Phase 2, attacker ABSENT): decide across vehicle{memory,rag,wiki} x defense{none,
  #   provenance_bound,cooling_off,memory_quarantine} x item_kind{authorized_true,laundered_forged}
  docker run -d --name w9 --env-file .../openrouter.env -v ...:/work/artifacts aigeopol-labs:latest \
    code/run_labs_mem.py --phase read --scenarios scenarios/mvp_v2.jsonl --models config/models_v2.json \
    --store /work/artifacts/mem/store.json --out /work/artifacts/raw/w9_mem_read.jsonl --k 4 --workers 12

  # analyze: durable_update vs durable_leak per vehicle x defense; provenance_retention after compaction
  docker run --rm -v ...:/work/artifacts aigeopol-labs:latest code/analyze_mem.py \
    --read-jsonl /work/artifacts/raw/w9_mem_read.jsonl --store /work/artifacts/mem/store.json \
    --out-dir /work/artifacts/derived --prefix w9

Scale: read ~504 units x K4 = ~2016 calls (~$10) + ~21 compact. Needs credit top-up.
Read: provenance_bound should admit the real-token update (durable_update high) and block the forged
one (durable_leak low); the wiki vehicle should COLLAPSE both if compaction stripped the token
(source amnesia) -- that contrast is the finding.
