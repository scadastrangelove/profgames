#!/usr/bin/env python3
"""Emit review-pack tables (markdown) from the derived CSVs, kept in sync with the data. stdlib only.
  python make_tables.py --derived ../../artifacts/derived --out ../../../review_pack/tables/TABLES.md
"""
import argparse
import csv
import json
import os
import statistics
from collections import defaultdict

FAM = {"anthropic": "Opus-4.8", "anthropic_sonnet": "Sonnet-4.6", "openai": "GPT-5.5",
       "qwen": "Qwen3.7", "deepseek": "DeepSeek-v4", "mistral": "Mistral-lg", "llama_weak": "Llama-8b"}


def rd(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--derived", default=os.path.join(here, "..", "..", "artifacts", "derived"))
    ap.add_argument("--out", default=os.path.join(here, "..", "..", "..", "review_pack", "tables", "TABLES.md"))
    a = ap.parse_args()
    d = a.derived
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    S = ["# Review-pack tables (generated from artifacts/derived)\n"]

    # T1 auditor dissociation
    r = rd(os.path.join(d, "mvp_v2_auditor_dissociation.csv"))
    S.append("## T1. Auditor dissociation (W1) — mean auditor flag by ground-truth label")
    S.append(md_table(["label", "content", "relevance", "provenance", "independence"],
                      [[x["relevance_label"], x["mean_content"], x["mean_relevance"], x["mean_provenance"], x["mean_independence"]] for x in r]))
    S.append("\n_Content is blind to true-but-irrelevant (0.33); relevance catches it (0.98); provenance token-verifies (relevant 0.003 vs fabricated 1.00)._\n")

    # T2 durable permeability
    r = rd(os.path.join(d, "w9b_permeability.csv"))
    S.append("## T2. Long-horizon durable selective permeability (W9b) — by vehicle × defense")
    S.append(md_table(["vehicle", "defense", "durable_update", "durable_leak", "selective_permeability"],
                      [[x["vehicle"], x["defense"], x["durable_update"], x["durable_leak"], x["selective_permeability"]] for x in r]))
    S.append("\n_provenance_bound is a **clear win in memory** (SP 0.52 vs none 0.18) and a **marginal, "
             "uncertain increment in RAG** (0.69 vs 0.62 — CIs overlap, T5b); naive quarantine over-blocks; "
             "**wiki collapses** in the merged, token-erasing setup (compaction retained 0/42 tokens). "
             "The dominant effect is the vehicle, not the defense._\n")

    # T2c per-item wiki (W9d) — mitigation: token-preserving per-item summaries recover wiki SP from ~0
    w9d_path = os.path.join(d, "..", "raw", "w9d_peritem_wiki.jsonl")
    if os.path.exists(w9d_path):
        recs = [json.loads(l) for l in open(w9d_path, encoding="utf-8") if l.strip()]
        by = defaultdict(lambda: {"authorized_true": [], "laundered_forged": []})
        for r in recs:
            by[r["defense"]][r["item_kind"]].append(r["lure_rate"])
        S.append("## T2c. W9d — per-item, token-preserving wiki summarization recovers SP (mitigates source amnesia)")
        S.append(md_table(["defense", "durable_update", "durable_leak", "selective_permeability"],
                          [[dfn, round(statistics.mean(b["authorized_true"]), 3),
                            round(statistics.mean(b["laundered_forged"]), 3),
                            round(statistics.mean(b["authorized_true"]) - statistics.mean(b["laundered_forged"]), 3)]
                           for dfn, b in sorted(by.items())]))
        S.append("\n_The §7.5 source-amnesia collapse was a **merged-wiki + token-stripping-summarizer** confound. "
                 "With per-item summaries and a token-preserving (Opus) summarizer that retains 42/42 tokens, wiki "
                 "SP recovers from ≈0 to **0.14–0.24** (provenance_bound 0.14, cooling_off 0.24). Source amnesia is "
                 "real but **mitigable** — a pipeline choice, not an intrinsic failure._\n")

    # T3 disclosure + forgery
    r = rd(os.path.join(d, "w7b_disclosure.csv"))
    S.append("## T3a. Token disclosure (W7b) — PROVIDED rate with 95% CI (7×3 pretexts×K8, judge-classified)")
    S.append("_Human-validated as a **leak rate** (token-out κ=1.0 vs GPT / 97.7% vs Anthropic, HUMAN_VALIDATION.md); "
             "the judge does not separate clean from hedged/incidental disclosure (3-class κ≈0.5), and ~⅓ of leaks "
             "are the hedged kind. Read 'provided' as 'usable token emitted', not 'clean hand-over'._")
    S.append(md_table(["model", "n", "provided", "95% CI", "mentioned", "refused"],
                      [[FAM.get(x["victim_family"], x["victim_family"]), x["n"], x["provided_rate"],
                        f'[{x["ci95_lo"]}, {x["ci95_hi"]}]', x["mentioned_rate"], x["refused_rate"]] for x in r]))
    fr = rd(os.path.join(d, "w7b_forgery.csv"))
    S.append("\n## T3b. Token forgery acceptance (W7b) — by model × defense, 95% CI")
    S.append(md_table(["model", "defense", "forged_accept", "95% CI", "n"],
                      [[FAM.get(x["victim_family"], x["victim_family"]), x["defense"], x["forged_accept_rate"],
                        f'[{x["ci95_lo"]}, {x["ci95_hi"]}]', x["n"]] for x in fr]))
    S.append("\n_Most frontier advisors emit the credential (leak; Sonnet excepted, .03 — it mentions-while-refusing). Only Mistral/Llama accept forgery; a registry policy fixes Mistral (0.92→0)._\n")

    # T4 scamops
    r = rd(os.path.join(d, "w8_capture.csv"))
    S.append("## T4a. ScamOps capture, no defense (W8, pilot) — mechanism × model")
    S.append(md_table(["mechanism", "model", "baseline_correct", "capture"],
                      [[x["mechanism"], FAM.get(x["victim_family"], x["victim_family"]), x["baseline_correct"], x["capture_no_defense"]] for x in r]))
    dr = rd(os.path.join(d, "w8_defense.csv"))
    S.append("\n## T4b. ScamOps defense recovery (W8) — lure-rate reduction vs no-defense")
    S.append(md_table(["mechanism", "defense", "lure_rate", "recovery_vs_none", "correct_rate"],
                      [[x["mechanism"], x["defense"], x["lure_rate"], x["recovery_vs_none"], x["correct_rate"]] for x in dr]))
    S.append("\n_Pilot. Capture (T4a) now covers all **7 models** (Sonnet/Qwen/Llama added, no-defense only); "
             "defense-recovery (T4b) remains the original 4-model run. Crude pressure flips only the weak models "
             "(Mistral, Llama); frontier ≈0. Cooling-off is the best recovery._\n")

    # T5 cluster-bootstrap CIs (multiplicity-preserving; unit = payload for W1, scenario×victim for W9b)
    sp = rd(os.path.join(d, "w1_selperm_ci.csv"))
    S.append("## T5a. W1 selective permeability by defense — cluster-bootstrap 95% CI (unit = payload)")
    S.append(md_table(["defense", "selective_permeability", "95% CI"],
                      [[x["defense"], x["selective_permeability"],
                        f'[{x["ci95_lo"]}, {x["ci95_hi"]}]'] for x in sp]))
    S.append("\n_Multiplicity-preserving cluster bootstrap (resamples payloads with replacement). D0 (no gate) "
             "SP is highest; the content and action-critic gates' CIs are disjoint from D0, the registry gate's "
             "overlaps modestly. Detector≠deployable-gate on already-robust models (§7.1)._\n")
    pb = rd(os.path.join(d, "w9b_permeability_ci.csv"))
    S.append("## T5b. W9b durable selective permeability — cluster-bootstrap 95% CI (unit = scenario×victim)")
    S.append(md_table(["vehicle", "defense", "selective_permeability", "95% CI", "n_clusters"],
                      [[x["vehicle"], x["defense"], x["selective_permeability"],
                        f'[{x["ci95_lo"]}, {x["ci95_hi"]}]', x["n_clusters"]] for x in pb]))
    S.append("\n_provenance_bound on **memory** excludes the none-defense level (clear win); on **RAG** the "
             "increment is marginal (CIs overlap none); **wiki** collapses. n=21 clusters is coarse — some CIs "
             "reach slightly below 0._\n")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(S) + "\n")
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
