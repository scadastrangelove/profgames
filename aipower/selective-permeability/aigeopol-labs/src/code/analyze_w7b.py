#!/usr/bin/env python3
"""Rebuild the W7b derived CSVs from the judged raw, so the pipeline is complete/reproducible:
  artifacts/raw/w7b_token_judged.jsonl  ->  derived/w7b_disclosure.csv  (token-out primary + severity)
                                            derived/w7b_forgery.csv     (forged-accept by victim×defense + Wilson CI)
The judge labels are produced upstream (GPT-5.5 judge, non-Anthropic = family-clean; a second Anthropic
judge in w7b_token_judged_anthropic.jsonl is used only for the κ agreement in HUMAN_VALIDATION.md).
Parsed-only: UNPARSED excluded from denominators (see §9). stdlib only."""
import argparse
import csv
import json
import math
import os
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(p, 3), round(max(0, c - h), 3), round(min(1, c + h), 3))


def wcsv(path, rows, cols):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + "\n")


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--jsonl", default=os.path.join(here, "..", "..", "artifacts", "raw", "w7b_token_judged.jsonl"))
    ap.add_argument("--out", default=os.path.join(here, "..", "..", "artifacts", "derived"))
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.jsonl, encoding="utf-8") if l.strip()]

    # ---- disclosure: token-out (PROVIDED+MENTIONED) is primary; PROVIDED is secondary severity ----
    attempts = [r for r in rows if r.get("subtest") == "disclosure"]
    dis = [r for r in attempts if r.get("judge_label") in ("PROVIDED", "MENTIONED", "REFUSED")]
    byv = defaultdict(lambda: {"PROVIDED": 0, "MENTIONED": 0, "REFUSED": 0, "n": 0})
    for r in dis:
        byv[r["victim_family"]][r["judge_label"]] += 1
        byv[r["victim_family"]]["n"] += 1
    attempted_by_v = defaultdict(int)
    for r in attempts:
        attempted_by_v[r["victim_family"]] += 1
    drows = []
    for v, b in sorted(byv.items(), key=lambda x: -((x[1]["PROVIDED"] + x[1]["MENTIONED"]) / max(1, x[1]["n"]))):
        provided, provided_lo, provided_hi = wilson(b["PROVIDED"], b["n"])
        token_out, token_lo, token_hi = wilson(b["PROVIDED"] + b["MENTIONED"], b["n"])
        attempted = attempted_by_v[v]
        drows.append({
            "victim_family": v,
            "attempted": attempted,
            "n": b["n"],
            "unparsed": attempted - b["n"],
            "token_out_rate": token_out,
            "token_out_ci95_lo": token_lo,
            "token_out_ci95_hi": token_hi,
            "provided_rate": provided,
            "provided_ci95_lo": provided_lo,
            "provided_ci95_hi": provided_hi,
            "mentioned_rate": round(b["MENTIONED"] / b["n"], 3),
            "refused_rate": round(b["REFUSED"] / b["n"], 3),
        })
    wcsv(os.path.join(a.out, "w7b_disclosure.csv"), drows,
         ["victim_family", "attempted", "n", "unparsed", "token_out_rate", "token_out_ci95_lo",
          "token_out_ci95_hi", "provided_rate", "provided_ci95_lo", "provided_ci95_hi",
          "mentioned_rate", "refused_rate"])

    # ---- forgery: forged-accept rate by victim × defense + Wilson CI ----
    forg = [r for r in rows if r.get("subtest") == "forgery"]
    byvd = defaultdict(lambda: {"acc": 0, "n": 0})
    for r in forg:
        k = (r["victim_family"], r.get("defense", "none"))
        byvd[k]["acc"] += int(r.get("forged_accepted", 0)); byvd[k]["n"] += 1
    frows = []
    for (v, dfn), b in sorted(byvd.items()):
        p, lo, hi = wilson(b["acc"], b["n"])
        frows.append({"victim_family": v, "defense": dfn, "forged_accept_rate": p, "ci95_lo": lo, "ci95_hi": hi, "n": b["n"]})
    wcsv(os.path.join(a.out, "w7b_forgery.csv"), frows,
         ["victim_family", "defense", "forged_accept_rate", "ci95_lo", "ci95_hi", "n"])
    print(f"rebuilt w7b_disclosure.csv ({len(drows)} rows) and w7b_forgery.csv ({len(frows)} rows) from {os.path.basename(a.jsonl)}")


if __name__ == "__main__":
    main()
