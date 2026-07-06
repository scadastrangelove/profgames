#!/usr/bin/env python3
import argparse
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import labs_lib as L


def selected_victims(config, family_filter):
    victims = L.enabled(config.get("victims", []))
    if family_filter:
        allowed = set(family_filter)
        victims = [v for v in victims if v.get("family") in allowed]
    if not victims:
        raise SystemExit("no victim models selected")
    return victims


def build_cells(tasks, victims, defenses, args):
    filters = {
        "domain_id": args.domain_id,
        "condition": set(args.condition or []),
        "mechanism": set(args.mechanism or []),
        "vehicle": set(args.vehicle or []),
    }
    cells = []
    for task, payload in L.iter_payload_cells(tasks, filters):
        for defense in defenses:
            for victim in victims:
                cells.append((task, payload, defense, victim))
    if args.shuffle:
        random.Random(args.seed).shuffle(cells)
    if args.skip_cells:
        cells = cells[args.skip_cells:]
    if args.max_cells:
        cells = cells[:args.max_cells]
    return cells


def preflight_models(victims, key, args):
    if args.preflight == "none":
        return
    selected = victims[:1] if args.preflight == "first" else victims
    seen = set()
    for victim in selected:
        model = victim["id"]
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
            print(f"preflight ok {victim.get('family')} {model}", flush=True)
        except Exception as exc:
            raise SystemExit(f"preflight_openrouter_failed model={model}: {exc}") from exc


def run_one(unit, key, args, run_id, model_config_hash):
    task, payload, defense, victim, sample_idx = unit
    prompt = L.render_victim_prompt(task, payload, defense)
    started = time.time()
    record = {
        "run_id": run_id,
        "kind": "victim",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "scenario_id": task["scenario_id"],
        "domain_id": task["domain_id"],
        "task_family": task["task_family"],
        "domain": task["domain"],
        "payload_id": payload["payload_id"],
        "condition": payload["condition"],
        "mechanism": payload["mechanism"],
        "vehicle": payload["vehicle"],
        "variant_id": payload["variant_id"],
        "source_label": payload["source_label"],
        "origin_label": payload.get("origin_label", payload["source_label"]),
        "origin_family": payload.get("origin_family", payload.get("origin_label", payload["source_label"])),
        "defense_level": defense,
        "victim_model": victim["id"],
        "victim_family": victim.get("family"),
        "sample_idx": sample_idx,
        "temperature": args.temperature,
        "correct_answer": task["correct_answer"],
        "lure_answer": task["lure_answer"],
        "prompt_hash": L.sha256_text(prompt),
        "payload_hash": L.sha256_text(payload.get("text", "")),
        "scenario_hash": L.stable_hash(task),
        "model_config_hash": model_config_hash,
    }
    try:
        raw = L.call_openrouter(prompt, victim["id"], key, args.temperature, args.max_tokens)
        parsed = L.parse_answer(raw, task)
        record.update({
            "ok": True,
            "raw_output": raw,
            "parsed_answer": parsed["answer"],
            "confidence": parsed["confidence"],
            "brief_reason": parsed["brief_reason"],
            "parse_ok": parsed["parse_ok"],
            "p_lure": round(L.p_lure(parsed, task), 4),
            "p_correct": round(L.p_correct(parsed, task), 4),
            "answer_is_lure": parsed["answer"] == task["lure_answer"],
            "answer_is_correct": parsed["answer"] == task["correct_answer"],
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
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-cells", type=int, default=0)
    ap.add_argument("--skip-cells", type=int, default=0)
    ap.add_argument("--domain-id")
    ap.add_argument("--condition", action="append", default=[])
    ap.add_argument("--mechanism", action="append", default=[])
    ap.add_argument("--vehicle", action="append", default=[])
    ap.add_argument("--defense-level", action="append", default=[])
    ap.add_argument("--victim-family", action="append", default=[])
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--seed", type=int, default=20260704)
    ap.add_argument("--preflight", choices=["none", "first", "all"], default="first")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.k < 1:
        raise SystemExit("--k must be >= 1")
    defenses = args.defense_level or ["D0_no_defense", "D1_content_audit", "D2_relevance_provenance_independence"]
    L.require_known_defenses(defenses)
    tasks = L.load_jsonl(args.scenarios)
    config = L.load_json(args.models)
    model_config_hash = L.stable_hash(config)
    victims = selected_victims(config, args.victim_family)
    cells = build_cells(tasks, victims, defenses, args)
    units = [(task, payload, defense, victim, sample_idx)
             for task, payload, defense, victim in cells
             for sample_idx in range(args.k)]

    if args.dry_run:
        L.print_json({
            "scenario_tasks": len(tasks),
            "selected_cells": len(cells),
            "victim_calls": len(units),
            "k": args.k,
            "workers": args.workers,
            "victims": [v["id"] for v in victims],
            "defense_levels": defenses,
        })
        for task, payload, defense, victim in cells[:50]:
            print(task["scenario_id"], payload["payload_id"], payload["condition"], payload["mechanism"], payload["vehicle"], defense, victim.get("family"))
        return

    key = L.load_key()
    preflight_models(victims, key, args)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    run_id = f"labs-victim-{int(time.time())}"
    count = 0
    with open(args.out, "a", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_map = {
                executor.submit(run_one, unit, key, args, run_id, model_config_hash): unit
                for unit in units
            }
            for future in as_completed(future_map):
                record = future.result()
                L.write_jsonl(out, record)
                count += 1
                status = "ok" if record.get("ok") else "ERR"
                print(
                    f"{status} {count}/{len(units)} {record.get('domain_id')} "
                    f"{record.get('condition')} {record.get('mechanism')} {record.get('defense_level')} "
                    f"{record.get('victim_family')} sample={record.get('sample_idx')}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
