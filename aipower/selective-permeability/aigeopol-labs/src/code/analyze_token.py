#!/usr/bin/env python3
"""Analyze the token-extraction/forgery flagship. Reports, per victim and defense:
  disclosure rate (advisor reveals the issuer token under pretext) and
  forgery-acceptance rate (advisor accepts a fake-token lure revision),
plus each defense's reduction vs no-defense."""
import argparse
import json
import os
from collections import defaultdict


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
    ap.add_argument("--prefix", default="token")
    a = ap.parse_args()
    rows = [r for r in (json.loads(l) for l in open(a.jsonl, encoding="utf-8") if l.strip())
            if r.get("kind") == "token" and r.get("ok")]
    os.makedirs(a.out_dir, exist_ok=True)
    defenses = sorted({d for r in rows for d in r["disclosure"]})

    # per (victim_family, defense)
    dis = defaultdict(list)
    frg = defaultdict(list)
    for r in rows:
        for d in defenses:
            dis[(r["victim_family"], d)].append(r["disclosure"].get(d))
            frg[(r["victim_family"], d)].append(r["forgery"].get(d))
    fams = sorted({r["victim_family"] for r in rows})
    out_rows = []
    for fam in fams:
        none_dis = mean(dis[(fam, "none")]); none_frg = mean(frg[(fam, "none")])
        for d in defenses:
            md = mean(dis[(fam, d)]); mf = mean(frg[(fam, d)])
            out_rows.append({"victim_family": fam, "defense": d,
                             "disclosure_rate": md, "forgery_accept_rate": mf,
                             "disclosure_reduction_vs_none": None if md is None or none_dis is None else round(none_dis - md, 3),
                             "forgery_reduction_vs_none": None if mf is None or none_frg is None else round(none_frg - mf, 3)})
    wcsv(os.path.join(a.out_dir, f"{a.prefix}_by_victim_defense.csv"), out_rows,
         ["victim_family", "defense", "disclosure_rate", "forgery_accept_rate",
          "disclosure_reduction_vs_none", "forgery_reduction_vs_none"])

    summary = {
        "records": len(rows), "victims": fams, "defenses": defenses,
        "disclosure_no_defense": mean([r["disclosure"].get("none") for r in rows]),
        "forgery_no_defense": mean([r["forgery"].get("none") for r in rows]),
        "disclosure_with_token_policy": mean([r["disclosure"].get("token_policy") for r in rows]),
        "forgery_with_token_policy": mean([r["forgery"].get("token_policy") for r in rows]),
        "disclosure_with_cooling_off": mean([r["disclosure"].get("cooling_off") for r in rows]),
        "forgery_with_cooling_off": mean([r["forgery"].get("cooling_off") for r in rows]),
    }
    with open(os.path.join(a.out_dir, f"{a.prefix}_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {a.prefix}_by_victim_defense.csv, {a.prefix}_summary.json -> {a.out_dir}")


if __name__ == "__main__":
    main()
