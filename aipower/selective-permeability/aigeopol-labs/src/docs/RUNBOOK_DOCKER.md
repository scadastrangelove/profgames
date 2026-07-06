# Docker/SSH Runbook

Remote host: `gordey@85.142.100.8`

Remote layout:

```bash
/home/gordey/aigeopol-labs/src
/home/gordey/aigeopol-labs/artifacts
/home/gordey/aigeopol-labs/.secrets/openrouter.env
```

The OpenRouter key stays server-side in `.secrets/openrouter.env`, mode `600`. It is never copied into the image and never synced back.

## 0. Local Checks

From `purple_labs/`:

```bash
python3 -m py_compile code/*.py
python3 code/validate_scenarios.py --scenarios scenarios/mvp_3x3x3.jsonl
python3 code/run_labs_matrix.py \
  --scenarios scenarios/mvp_3x3x3.jsonl \
  --models config/models.json \
  --out artifacts/dryrun_victims.jsonl \
  --k 6 \
  --dry-run
python3 code/run_labs_auditors.py \
  --scenarios scenarios/mvp_3x3x3.jsonl \
  --models config/models.json \
  --out artifacts/dryrun_auditors.jsonl \
  --dry-run
python3 code/analyze_labs.py \
  --victim-jsonl /dev/null \
  --audit-jsonl /dev/null \
  --out-dir artifacts/analysis_empty \
  --prefix empty
OPENROUTER_PREFIX="$(printf 'sk-%s' or)"
rg -n "$OPENROUTER_PREFIX" .
```

Expected dry-run scale for E1:

- victim cells: `66 payloads x 3 defenses x 6 victims = 1188`
- victim calls with `K=6`: `7128`
- auditor cells, no baseline: `63 payloads x 8 auditors = 504`

Real API runs use a fail-fast OpenRouter preflight. Use `--preflight all` before long waves to test every selected model ID; use `--preflight first` for quick smoke; use `--preflight none` only when resuming known-good infrastructure.

## 1. Remote Setup

```bash
ssh gordey@85.142.100.8 \
  'mkdir -p /home/gordey/aigeopol-labs/{src,artifacts/raw,artifacts/derived,.secrets} && chmod 700 /home/gordey/aigeopol-labs/.secrets'
```

Create the remote secret file interactively:

```bash
ssh gordey@85.142.100.8 \
  'umask 077; cat > /home/gordey/aigeopol-labs/.secrets/openrouter.env'
```

Paste one line, then press `Ctrl-D`:

```bash
OPENROUTER_API_KEY=...
```

Verify permissions:

```bash
ssh gordey@85.142.100.8 \
  'chmod 600 /home/gordey/aigeopol-labs/.secrets/openrouter.env && ls -l /home/gordey/aigeopol-labs/.secrets/openrouter.env'
```

Before long Docker runs, refresh sudo once:

```bash
ssh -t gordey@85.142.100.8 'sudo -v'
```

## 2. Sync And Build

From the parent directory that contains `purple_labs/`:

```bash
rsync -az --delete \
  --exclude artifacts \
  --exclude .secrets \
  purple_labs/ \
  gordey@85.142.100.8:/home/gordey/aigeopol-labs/src/
```

Build on remote:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker build -t aigeopol-labs:latest .'
```

Container validation without secrets:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts aigeopol-labs:latest code/validate_scenarios.py --scenarios scenarios/mvp_3x3x3.jsonl'
```

## 3. E0 Docker/SSH Smoke

Victim smoke: one scenario slice, two victims, `K=2`.

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_matrix.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e0_victim_smoke.jsonl \
      --domain-id procurement \
      --condition baseline \
      --condition influence \
      --vehicle direct_context \
      --mechanism relevance_misbinding \
      --defense-level D0_no_defense \
      --victim-family anthropic_opus \
      --victim-family openai \
      --k 2 \
      --workers 2 \
      --preflight all'
```

Auditor smoke: one auditor family and the same slice.

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_auditors.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e0_auditor_smoke.jsonl \
      --domain-id procurement \
      --condition influence \
      --vehicle direct_context \
      --mechanism relevance_misbinding \
      --auditor-family google \
      --workers 2 \
      --preflight all'
```

Analyze E0:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/analyze_labs.py \
      --victim-jsonl /work/artifacts/raw/e0_victim_smoke.jsonl \
      --audit-jsonl /work/artifacts/raw/e0_auditor_smoke.jsonl \
      --out-dir /work/artifacts/derived/e0 \
      --prefix e0'
```

Secret scan after E0:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs && OPENROUTER_PREFIX="$(printf '"'"'sk-%s'"'"' or)" && if command -v rg >/dev/null; then ! rg -n "$OPENROUTER_PREFIX" src artifacts; else ! grep -RIn "$OPENROUTER_PREFIX" src artifacts; fi'
```

Acceptance: records parse, artifacts are written, and the secret scan is clean.

## 4. E1 MVP 3x3x3 Medium Run

Victim run:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_matrix.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e1_victim_mvp_3x3x3.jsonl \
      --k 6 \
      --workers 6 \
      --shuffle \
      --preflight all'
```

Auditor run:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_auditors.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e1_auditor_mvp_3x3x3.jsonl \
      --workers 6 \
      --shuffle \
      --preflight all'
```

Analyze E1:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/analyze_labs.py \
      --victim-jsonl /work/artifacts/raw/e1_victim_mvp_3x3x3.jsonl \
      --audit-jsonl /work/artifacts/raw/e1_auditor_mvp_3x3x3.jsonl \
      --out-dir /work/artifacts/derived/e1 \
      --prefix e1_mvp_3x3x3'
```

Primary outputs:

- `e1_mvp_3x3x3_summary.json`
- `e1_mvp_3x3x3_selective_permeability.csv`
- `e1_mvp_3x3x3_mechanism_victim_matrix.csv`
- `e1_mvp_3x3x3_origin_victim_matrix.csv`
- `e1_mvp_3x3x3_keying_index.csv`
- `e1_mvp_3x3x3_defense_delta.csv`
- `e1_mvp_3x3x3_auditor_dissociation.csv`
- `e1_mvp_3x3x3_report.md`

## 5. E2 Defense Ladder Ablation

Reuse E1 scenarios and add D3/D4.

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_matrix.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e2_victim_defense_ladder.jsonl \
      --defense-level D0_no_defense \
      --defense-level D1_content_audit \
      --defense-level D2_relevance_provenance_independence \
      --defense-level D3_action_critic \
      --defense-level D4_known_good_source_registry \
      --k 6 \
      --workers 6 \
      --shuffle \
      --preflight all'
```

Analyze with the E1 auditor file or rerun auditors if the payload set changes:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/analyze_labs.py \
      --victim-jsonl /work/artifacts/raw/e2_victim_defense_ladder.jsonl \
      --audit-jsonl /work/artifacts/raw/e1_auditor_mvp_3x3x3.jsonl \
      --out-dir /work/artifacts/derived/e2 \
      --prefix e2_defense_ladder'
```

## 6. E3 Transfer / Keying Matrix

Freeze selected best payloads after reading E1. For an initial full transfer replay, run all influence payloads against all victims:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_matrix.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e3_transfer_keying_all_influence.jsonl \
      --condition influence \
      --defense-level D0_no_defense \
      --k 6 \
      --workers 6 \
      --shuffle \
      --preflight all'
```

Use `origin_victim_matrix.csv` and `mechanism_victim_matrix.csv` as the EXP_29 bridge: rows are origin/mechanism, columns are victim families.

## 7. E4 Persistence And Remediation Pilot

Use the memory/tool mock vehicle and compare remediation policies by defense label:

```bash
ssh gordey@85.142.100.8 \
  'cd /home/gordey/aigeopol-labs/src && sudo docker run --rm \
    --env-file /home/gordey/aigeopol-labs/.secrets/openrouter.env \
    -v /home/gordey/aigeopol-labs/artifacts:/work/artifacts \
    aigeopol-labs:latest code/run_labs_matrix.py \
      --scenarios scenarios/mvp_3x3x3.jsonl \
      --models config/models.json \
      --out /work/artifacts/raw/e4_memory_tool_remediation.jsonl \
      --vehicle memory_tool_mock \
      --condition influence \
      --defense-level D0_no_defense \
      --defense-level D3_action_critic \
      --defense-level D4_known_good_source_registry \
      --k 6 \
      --workers 6 \
      --shuffle \
      --preflight all'
```

Interpretation proxy in this scaffold:

- destructive purge: D4 registry-only posture
- quarantine: D3 action critic posture
- snapshot+rollback: compare D0 baseline, D3, and D4 replay reproducibility

## 8. Data Quality Gates

After each wave:

```bash
ssh gordey@85.142.100.8 \
  'python3 - <<'"'"'PY'"'"'
import json
from pathlib import Path
for path in Path("/home/gordey/aigeopol-labs/artifacts/derived").glob("**/*_summary.json"):
    data = json.loads(path.read_text())
    print(path, "victim_parse_rate=", data.get("victim_parse_rate"), "audit_parse_rate=", data.get("audit_parse_rate"))
PY'
```

Gate targets:

- victim parse rate >= `0.95`
- auditor parse rate >= `0.95`
- no OpenRouter key in `src` or `artifacts`
- every raw row has prompt, payload, scenario, and model-config hashes
