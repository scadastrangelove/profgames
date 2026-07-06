#!/usr/bin/env python3
import argparse
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import labs_lib as L


def selected_auditors(config, role_filter, family_filter):
    auditors = L.enabled(config.get("auditors", []))
    if role_filter:
        allowed = set(role_filter)
        auditors = [a for a in auditors if a.get("role") in allowed]
    if family_filter:
        allowed = set(family_filter)
        auditors = [a for a in auditors if a.get("family") in allowed]
    if not auditors:
        raise SystemExit("no auditor models selected")
    return auditors


def build_cells(tasks, auditors, args):
    filters = {
        "domain_id": args.domain_id,
        "condition": set(args.condition or []),
        "mechanism": set(args.mechanism or []),
        "vehicle": set(args.vehicle or []),
    }
    cells = []
    for task, payload in L.iter_payload_cells(tasks, filters):
        if payload["condition"] == "baseline" and not args.include_baseline:
            continue
        for auditor in auditors:
            cells.append((task, payload, auditor))
    if args.shuffle:
        random.Random(args.seed).shuffle(cells)
    if args.skip_cells:
        cells = cells[args.skip_cells:]
    if args.max_cells:
        cells = cells[:args.max_cells]
    return cells


def preflight_models(auditors, key, args):
    if args.preflight == "none":
        return
    selected = auditors[:1] if args.preflight == "first" else auditors
    seen = set()
    for auditor in selected:
        model = auditor["id"]
        if model in seen:
            continue
        seen.add(model)
        try:
            L.call_openrouter(
                "Respond with ONLY this exact text: OK",
                model,
                key,
                0.0,
                32,
                retries=1,
                timeout=60,
            )
            print(f"preflight ok {auditor.get('family')} {model}", flush=True)
        except Exception as exc:
            raise SystemExit(f"preflight_openrouter_failed model={model}: {exc}") from exc


def run_one(unit, key, args, run_id, model_config_hash):
    task, payload, auditor = unit
    role = auditor["role"]
    prompt = L.render_auditor_prompt(task, payload, role)
    started = time.time()
    record = {
        "run_id": run_id,
        "kind": "auditor",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "scenario_id": task["scenario_id"],
        "domain_id": task["domain_id"],
        "task_family": task["task_family"],
        "payload_id": payload["payload_id"],
        "condition": payload["condition"],
        "mechanism": payload["mechanism"],
        "vehicle": payload["vehicle"],
        "variant_id": payload["variant_id"],
        "source_label": payload["source_label"],
        "origin_label": payload.get("origin_label", payload["source_label"]),
        "origin_family": payload.get("origin_family", payload.get("origin_label", payload["source_label"])),
        "auditor_model": auditor["id"],
        "auditor_family": auditor.get("family"),
        "auditor_role": role,
        "prompt_hash": L.sha256_text(prompt),
        "payload_hash": L.sha256_text(payload.get("text", "")),
        "scenario_hash": L.stable_hash(task),
        "model_config_hash": model_config_hash,
    }
    try:
        raw = L.call_openrouter(prompt, auditor["id"], key, args.temperature, args.max_tokens)
        parsed = L.parse_score(raw)
        record.update({
            "ok": True,
            "raw_output": raw,
            "score": parsed["score"],
            "score_0_1": None if parsed["score"] is None else round(parsed["score"] / 100.0, 4),
            "parse_ok": parsed["parse_ok"],
            "latency_s": round(time.time() - started, 3),
        })
    except Exception as exc:
        record.update({
            "ok": False,
            "parse_ok": False,
            "error": str(exc)[:500],
            "latency_s": round(time.time() - started, 3),
        })
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=260)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-cells", type=int, default=0)
    ap.add_argument("--skip-cells", type=int, default=0)
    ap.add_argument("--domain-id")
    ap.add_argument("--condition", action="append", default=[])
    ap.add_argument("--mechanism", action="append", default=[])
    ap.add_argument("--vehicle", action="append", default=[])
    ap.add_argument("--role", action="append", default=[])
    ap.add_argument("--auditor-family", action="append", default=[])
    ap.add_argument("--include-baseline", action="store_true")
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--seed", type=int, default=20260704)
    ap.add_argument("--preflight", choices=["none", "first", "all"], default="first")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tasks = L.load_jsonl(args.scenarios)
    config = L.load_json(args.models)
    model_config_hash = L.stable_hash(config)
    auditors = selected_auditors(config, args.role, args.auditor_family)
    cells = build_cells(tasks, auditors, args)

    if args.dry_run:
        L.print_json({
            "scenario_tasks": len(tasks),
            "auditor_cells": len(cells),
            "auditors": [f"{a['role']}:{a['id']}" for a in auditors],
            "workers": args.workers,
        })
        for task, payload, auditor in cells[:80]:
            print(task["scenario_id"], payload["payload_id"], payload["condition"], payload["mechanism"], payload["vehicle"], auditor["role"], auditor.get("family"))
        return

    key = L.load_key()
    preflight_models(auditors, key, args)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    run_id = f"labs-auditor-{int(time.time())}"
    count = 0
    with open(args.out, "a", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_map = {
                executor.submit(run_one, cell, key, args, run_id, model_config_hash): cell
                for cell in cells
            }
            for future in as_completed(future_map):
                record = future.result()
                L.write_jsonl(out, record)
                count += 1
                status = "ok" if record.get("ok") else "ERR"
                print(
                    f"{status} {count}/{len(cells)} {record.get('domain_id')} "
                    f"{record.get('condition')} {record.get('mechanism')} {record.get('vehicle')} "
                    f"{record.get('auditor_role')} {record.get('auditor_family')}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
