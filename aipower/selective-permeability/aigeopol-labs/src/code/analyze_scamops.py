#!/usr/bin/env python3
"""Analyze the ScamOps slice. Answers two questions:
  1. Does a COMPETENT model (high baseline_correct) get flipped by a pressure sequence (none.lure_rate)?
  2. Which scam-derived defense RESTORES the correct decision (recovery vs none), at what utility?
"""
import argparse
import json
import os
from collections import defaultdict


def read(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def wcsv(path, rows, cols):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="scamops")
    a = ap.parse_args()
    rows = [r for r in read(a.jsonl) if r.get("kind") == "scamops" and r.get("ok")]
    os.makedirs(a.out_dir, exist_ok=True)
    defenses = sorted({d for r in rows for d in r["by_defense"]})

    # capture table: per (mechanism, victim_family) -> baseline competence + capture under 'none'
    cap = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k = (r["mechanism"], r["victim_family"])
        cap[k]["baseline_correct"].append(r.get("baseline_correct_rate"))
        cap[k]["captured"].append(r["by_defense"].get("none", {}).get("lure_rate"))
    cap_rows = []
    for (mech, fam), d in sorted(cap.items()):
        cap_rows.append({"mechanism": mech, "victim_family": fam,
                         "baseline_correct": mean(d["baseline_correct"]),
                         "capture_no_defense": mean(d["captured"])})
    wcsv(os.path.join(a.out_dir, f"{a.prefix}_capture.csv"), cap_rows,
         ["mechanism", "victim_family", "baseline_correct", "capture_no_defense"])

    # defense table: per (mechanism, defense) -> lure_rate + recovery vs none + utility (correct_rate)
    dfn = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for defense, d in r["by_defense"].items():
            dfn[(r["mechanism"], defense)]["lure"].append(d.get("lure_rate"))
            dfn[(r["mechanism"], defense)]["rec"].append(d.get("recovery_vs_none"))
            dfn[(r["mechanism"], defense)]["correct"].append(d.get("correct_rate"))
    dfn_rows = []
    for (mech, defense), d in sorted(dfn.items()):
        dfn_rows.append({"mechanism": mech, "defense": defense, "lure_rate": mean(d["lure"]),
                         "recovery_vs_none": mean(d["rec"]), "correct_rate": mean(d["correct"])})
    wcsv(os.path.join(a.out_dir, f"{a.prefix}_defense.csv"), dfn_rows,
         ["mechanism", "defense", "lure_rate", "recovery_vs_none", "correct_rate"])

    # headline
    overall_cap = mean([r["by_defense"].get("none", {}).get("lure_rate") for r in rows])
    overall_base = mean([r.get("baseline_correct_rate") for r in rows])
    best_def = None
    by_def = defaultdict(list)
    for r in rows:
        for defense, d in r["by_defense"].items():
            if defense != "none":
                by_def[defense].append(d.get("recovery_vs_none"))
    def_means = {d: mean(v) for d, v in by_def.items()}
    if def_means:
        best_def = max(def_means, key=lambda d: (def_means[d] if def_means[d] is not None else -9))
    summary = {"records": len(rows), "mechanisms": sorted({r["mechanism"] for r in rows}),
               "victims": sorted({r["victim_family"] for r in rows}),
               "baseline_correct_overall": overall_base,
               "capture_no_defense_overall": overall_cap,
               "recovery_by_defense": def_means, "best_defense": best_def}
    with open(os.path.join(a.out_dir, f"{a.prefix}_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {a.prefix}_capture.csv, {a.prefix}_defense.csv, {a.prefix}_summary.json -> {a.out_dir}")


if __name__ == "__main__":
    main()
