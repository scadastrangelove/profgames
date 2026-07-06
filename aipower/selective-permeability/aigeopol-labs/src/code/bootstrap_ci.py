#!/usr/bin/env python3
"""Cluster-bootstrap 95% CIs for the strong results (W1, W9b). Unit of resampling is the CLUSTER, not the
sample, to avoid pseudoreplication (reviewer point): W1 dissociation & selective permeability resample
PAYLOADS; W9b durable permeability resamples (scenario × victim) cells. stdlib only.

Note: this is a cluster (nonparametric) bootstrap on aggregated cell rates. A full binomial mixed-effects
GLMM would additionally need per-sample 0/1 logging; the harness stores per-cell rates (+K), so we report
cluster-bootstrap CIs here and flag the GLMM as a camera-ready item.
"""
import argparse
import csv
import json
import os
import random
import statistics

random.seed(1729)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def ci(vals):
    vals = sorted(vals)
    n = len(vals)
    return (round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n)], 3)) if n else (None, None)


def boot_clusters(cluster_ids, agg_fn, B=2000):
    """Resample cluster ids with replacement; agg_fn(sample_ids)->scalar."""
    ids = list(cluster_ids)
    out = []
    for _ in range(B):
        s = [ids[random.randrange(len(ids))] for _ in range(len(ids))]
        v = agg_fn(s)
        if v is not None:
            out.append(v)
    return out


def wcsv(path, rows, cols):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + "\n")


def w1(raw, out):
    rows = [r for r in load(raw) if r.get("kind") == "gated" and r["defense_level"] == "D0_no_defense"]
    # ---- dissociation: mean role score by relevance_label, cluster = payload_id ----
    ROLES = ["content", "relevance", "provenance", "independence"]
    by_pid = {}
    for r in rows:
        by_pid.setdefault(r["payload_id"], {"label": r["relevance_label"], "scores": []})
        by_pid[r["payload_id"]]["scores"].append(r.get("role_scores") or {})
    # per payload: mean of its role scores across victim rows
    pdata = {}
    for pid, d in by_pid.items():
        pdata[pid] = {"label": d["label"],
                      "role": {ro: statistics.mean([s.get(ro) for s in d["scores"] if s.get(ro) is not None] or [0]) for ro in ROLES}}
    labels = sorted({v["label"] for v in pdata.values()})
    drows = []
    for lab in labels:
        pids = [pid for pid, v in pdata.items() if v["label"] == lab]
        for ro in ROLES:
            point = statistics.mean([pdata[p]["role"][ro] for p in pids])
            bs = boot_clusters(pids, lambda s: statistics.mean([pdata[p]["role"][ro] for p in s]))
            lo, hi = ci(bs)
            drows.append({"label": lab, "role": ro, "mean": round(point, 3), "ci95_lo": lo, "ci95_hi": hi, "n_payloads": len(pids)})
    wcsv(os.path.join(out, "w1_dissociation_ci.csv"), drows, ["label", "role", "mean", "ci95_lo", "ci95_hi", "n_payloads"])

    # ---- selective permeability by defense, cluster = payload_id ----
    allrows = [r for r in load(raw) if r.get("kind") == "gated"]
    defenses = sorted({r["defense_level"] for r in allrows})
    # pre-index per (defense, payload) -> list of post_gate_lure_rate, split by condition, so the bootstrap
    # can preserve resample MULTIPLICITY (a payload drawn k times must contribute k times — the earlier
    # set()-based version silently collapsed duplicates, under-dispersing the CI). cf. w9b, which is correct.
    from collections import defaultdict
    pos_by = defaultdict(lambda: defaultdict(list)); inf_by = defaultdict(lambda: defaultdict(list))
    for r in allrows:
        if r["condition"] == "positive_relevant":
            pos_by[r["defense_level"]][r["payload_id"]].append(r["post_gate_lure_rate"])
        elif r["condition"] == "influence":
            inf_by[r["defense_level"]][r["payload_id"]].append(r["post_gate_lure_rate"])

    def sp_for(defense, pid_sample):
        # pid_sample is a LIST (with duplicates from resampling); iterate it so multiplicity is preserved.
        pos, inf = [], []
        for pid in pid_sample:
            pos.extend(pos_by[defense].get(pid, []))
            inf.extend(inf_by[defense].get(pid, []))
        if not pos or not inf:
            return None
        return statistics.mean(pos) - statistics.mean(inf)
    all_pids = sorted({r["payload_id"] for r in allrows if r["condition"] in ("positive_relevant", "influence")})
    srows = []
    for dfn in defenses:
        point = sp_for(dfn, all_pids)
        bs = boot_clusters(all_pids, lambda s: sp_for(dfn, s))
        lo, hi = ci(bs)
        srows.append({"defense": dfn, "selective_permeability": None if point is None else round(point, 3), "ci95_lo": lo, "ci95_hi": hi})
    wcsv(os.path.join(out, "w1_selperm_ci.csv"), srows, ["defense", "selective_permeability", "ci95_lo", "ci95_hi"])
    print("W1: wrote w1_dissociation_ci.csv, w1_selperm_ci.csv")


def w9b(raw, out):
    rows = load(raw)
    rows = [r for r in rows if r.get("kind") == "mem_read"]
    # cluster = (scenario_id, victim_family). SP(vehicle,defense) = mean update - mean leak over clusters
    clusters = sorted({(r["scenario_id"], r["victim_family"]) for r in rows})
    idx = {}
    for r in rows:
        idx.setdefault((r["vehicle"], r["defense"]), {}).setdefault((r["scenario_id"], r["victim_family"]), {})[r["item_kind"]] = r["lure_rate"]
    combos = sorted(idx.keys())

    def sp(vehicle, defense, cl_sample):
        cells = idx[(vehicle, defense)]
        ups, lks = [], []
        for c in cl_sample:
            d = cells.get(c, {})
            if "authorized_true" in d:
                ups.append(d["authorized_true"])
            if "laundered_forged" in d:
                lks.append(d["laundered_forged"])
        if not ups or not lks:
            return None
        return statistics.mean(ups) - statistics.mean(lks)
    prows = []
    for (veh, dfn) in combos:
        point = sp(veh, dfn, clusters)
        bs = boot_clusters(clusters, lambda s: sp(veh, dfn, s))
        lo, hi = ci(bs)
        prows.append({"vehicle": veh, "defense": dfn, "selective_permeability": None if point is None else round(point, 3), "ci95_lo": lo, "ci95_hi": hi, "n_clusters": len(clusters)})
    wcsv(os.path.join(out, "w9b_permeability_ci.csv"), prows, ["vehicle", "defense", "selective_permeability", "ci95_lo", "ci95_hi", "n_clusters"])
    print("W9b: wrote w9b_permeability_ci.csv")


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    raw = os.path.join(here, "..", "..", "artifacts", "raw")
    ap.add_argument("--w1", default=os.path.join(raw, "w1_gated.jsonl"))
    ap.add_argument("--w9b", default=os.path.join(raw, "w9b_mem_read.jsonl"))
    ap.add_argument("--out", default=os.path.join(here, "..", "..", "artifacts", "derived"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w1(a.w1, a.out)
    w9b(a.w9b, a.out)


if __name__ == "__main__":
    main()
