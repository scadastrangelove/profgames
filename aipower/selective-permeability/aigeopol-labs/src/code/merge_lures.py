#!/usr/bin/env python3
"""Merge harvested adaptive lures (from harvest_lures.py) into the v2 scenarios so run_labs_gated.py
cross-applies them to all victims under mechanism=adaptive_relevance, creating a real influence-leak
regime the gates can then be measured against.

  python3 code/merge_lures.py --scenarios scenarios/mvp_v2.jsonl \
      --lures /work/artifacts/raw/w4_lures.jsonl --out scenarios/mvp_v2_adaptive.jsonl
"""
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--lures", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-lure-rate", type=float, default=0.0,
                    help="only merge harvested lures whose D0 lure-rate >= this (drop dead ones)")
    a = ap.parse_args()
    tasks = [json.loads(l) for l in open(a.scenarios, encoding="utf-8") if l.strip()]
    by_sid = {t["scenario_id"]: t for t in tasks}
    lures = [json.loads(l) for l in open(a.lures, encoding="utf-8") if l.strip()]
    added = 0
    seen = set()
    for rec in lures:
        sid = rec["scenario_id"]
        p = rec["payload"]
        if p.get("harvested_lure_rate", 0.0) < a.min_lure_rate:
            continue
        if sid not in by_sid:
            continue
        if p["payload_id"] in seen:
            p = dict(p); p["payload_id"] = p["payload_id"] + f"_{added}"
        seen.add(p["payload_id"])
        by_sid[sid]["payloads"].append(p)
        added += 1
    with open(a.out, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    per_domain = {}
    for rec in lures:
        per_domain[rec["domain_id"]] = per_domain.get(rec["domain_id"], 0) + 1
    print(json.dumps({"merged_lures": added, "scenarios": len(tasks), "per_domain": per_domain,
                      "out": a.out}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
