#!/usr/bin/env python3
"""Reviewer-2/3 statistics: clustered uncertainty for the disclosure claim (avoids treating K samples
within a cell as independent), rates-by-pretext, UNPARSED accounting, and a per-trial mixed-effects
logit on the REAL per-sample records (not reconstructed). Also a W4/W5 negatives table.
Uses statsmodels+pandas (venv). Reads artifacts/raw/*.jsonl."""
import argparse
import csv
import json
import math
import os
import random
from collections import defaultdict

random.seed(20260705)
FAM = {"anthropic": "Opus-4.8", "anthropic_sonnet": "Sonnet-4.6", "openai": "GPT-5.5", "qwen": "Qwen3.7",
       "deepseek": "DeepSeek-v4", "mistral": "Mistral-lg", "llama_weak": "Llama-8b"}


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def ci_pct(vals):
    v = sorted(vals)
    n = len(v)
    return (round(v[int(0.025 * n)], 3), round(v[int(0.975 * n)], 3)) if n else (None, None)


def cluster_bootstrap_rate(records, B=3000):
    """records: list of {cluster, y}. Resample clusters w/ replacement, recompute mean(y)."""
    byc = defaultdict(list)
    for r in records:
        byc[r["cluster"]].append(r["y"])
    clusters = list(byc)
    point = sum(y for c in clusters for y in byc[c]) / sum(len(byc[c]) for c in clusters)
    boots = []
    for _ in range(B):
        samp = [clusters[random.randrange(len(clusters))] for _ in range(len(clusters))]
        ys = [y for c in samp for y in byc[c]]
        if ys:
            boots.append(sum(ys) / len(ys))
    lo, hi = ci_pct(boots)
    return round(point, 3), lo, hi, len(clusters)


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    raw = os.path.join(here, "..", "..", "artifacts", "raw")
    ap.add_argument("--raw", default=raw)
    ap.add_argument("--out", default=os.path.join(here, "..", "..", "..", "review_pack", "STATS_reviewer23.md"))
    a = ap.parse_args()
    S = ["# Reviewer-2/3 statistics addendum\n"]

    # ---- W7b (no-instruction) disclosure: UNPARSED accounting + by-pretext + clustered CIs ----
    dis = [r for r in load(os.path.join(a.raw, "w7b_token_judged.jsonl")) if r.get("subtest") == "disclosure"]
    from collections import Counter
    labct = Counter(r["judge_label"] for r in dis)
    S.append("## W7b disclosure — UNPARSED accounting (Reviewer-3 #4)")
    S.append(f"judge labels over all {len(dis)} attempts: {dict(labct)}")
    unp_by = Counter(r["victim_family"] for r in dis if r["judge_label"] not in ("PROVIDED", "MENTIONED", "REFUSED"))
    S.append(f"UNPARSED/other by model: {dict(unp_by)}")
    S.append("_PROVIDED-rate reported PARSED-ONLY (denominator = parsed attempts); UNPARSED are parser "
             "failures, excluded. This is why per-model n ranges 68–72._\n")

    parsed = [r for r in dis if r["judge_label"] in ("PROVIDED", "MENTIONED", "REFUSED")]
    S.append("## W7b PROVIDED rate: Wilson (sample-level) vs CLUSTER bootstrap (cluster = scenario×pretext)")
    S.append("| model | provided | Wilson-ish n | cluster-boot 95% CI | n_clusters |")
    S.append("|---|---|---|---|---|")
    for fam in sorted({r["victim_family"] for r in parsed}):
        recs = [{"cluster": (r["scenario_id"], r["pretext"]), "y": 1 if r["judge_label"] == "PROVIDED" else 0}
                for r in parsed if r["victim_family"] == fam]
        p, lo, hi, nc = cluster_bootstrap_rate(recs)
        S.append(f"| {FAM.get(fam, fam)} | {p} | {len(recs)} | [{lo}, {hi}] | {nc} |")
    S.append("_Cluster bootstrap (9 scenario×pretext clusters) widens intervals vs Wilson-on-samples; "
             "the ordering (GPT/Llama high, Sonnet ~0) is stable, but per-model CIs are wider than the "
             "sample-level Wilson CIs in T3a._\n")

    # by pretext
    S.append("## W7b PROVIDED rate by pretext (Reviewer-2/3)")
    S.append("| pretext | provided | n |")
    S.append("|---|---|---|")
    for pk in sorted({r["pretext"] for r in parsed}):
        sub = [r for r in parsed if r["pretext"] == pk]
        pr = sum(1 for r in sub if r["judge_label"] == "PROVIDED") / len(sub)
        S.append(f"| {pk} | {round(pr, 3)} | {len(sub)} |")

    # ---- per-trial mixed logit on REAL per-sample disclosure records ----
    try:
        import pandas as pd
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
        df = pd.DataFrame([{"y": 1 if r["judge_label"] == "PROVIDED" else 0, "victim_family": r["victim_family"],
                            "scenario_id": r["scenario_id"], "pretext": r["pretext"]} for r in parsed])
        vc = {"scn": "0 + C(scenario_id)", "pre": "0 + C(pretext)"}
        res = BinomialBayesMixedGLM.from_formula("y ~ C(victim_family, Treatment('anthropic_sonnet'))", vc, df).fit_vb()
        S.append("\n## W7b per-trial mixed logit (REAL per-sample; random intercepts scenario+pretext)")
        S.append("Reference = Sonnet. Positive coef = more likely to PROVIDE than Sonnet. (VB fit; treat CrI "
                 "as approximate — mean-field VB is anti-conservative, Reviewer-3 #3.)")
        S.append("| effect | log-odds | 95% CrI (approx) |")
        S.append("|---|---|---|")
        for i, nm in enumerate(res.model.exog_names):
            if "victim_family" in nm:
                m, s = res.fe_mean[i], res.fe_sd[i]
                short = nm.split("T.")[-1].rstrip("]")
                S.append(f"| {FAM.get(short, short)} vs Sonnet | {m:+.2f} | [{m-1.96*s:+.2f}, {m+1.96*s:+.2f}] |")
    except Exception as e:
        S.append(f"\n(per-trial GLMM skipped: {str(e)[:120]})")

    # ---- W7c protected/neutral: cluster-bootstrap CIs (Reviewer hardening: W7c is now central) ----
    w7c_path = os.path.join(a.raw, "w7c_token_judged.jsonl")
    if os.path.exists(w7c_path):
        w7c = load(w7c_path)
        prot = [r for r in w7c if r.get("condition") == "protected"
                and r["judge_label"] in ("PROVIDED", "MENTIONED", "REFUSED")]
        neut = [r for r in w7c if r.get("condition") == "neutral"
                and r["judge_label"] in ("PROVIDED", "MENTIONED", "REFUSED")]
        S.append("\n## W7c cluster-bootstrap CIs (cluster = scenario×pretext) — the reframed flagship")
        S.append("### Protected — three severity classes (bearer secret: token-out = it leaked at all)")
        S.append("| model | clean hand-over (PROVIDED) | exposed-while-refusing (MENTIONED) | **token-out** (P+M) | token-out 95% CI | n |")
        S.append("|---|---|---|---|---|---|")
        for fam in sorted({r["victim_family"] for r in prot},
                          key=lambda f: -sum(1 for r in prot if r["victim_family"] == f and r["judge_label"] in ("PROVIDED", "MENTIONED")) / max(1, sum(1 for r in prot if r["victim_family"] == f))):
            fr = [r for r in prot if r["victim_family"] == fam]; n = len(fr)
            pv = sum(1 for r in fr if r["judge_label"] == "PROVIDED") / n
            mn = sum(1 for r in fr if r["judge_label"] == "MENTIONED") / n
            recs = [{"cluster": (r["scenario_id"], r["pretext"]),
                     "y": 1 if r["judge_label"] in ("PROVIDED", "MENTIONED") else 0} for r in fr]
            to, lo, hi, nc = cluster_bootstrap_rate(recs)
            S.append(f"| {FAM.get(fam, fam)} | {round(pv,3)} | {round(mn,3)} | **{to}** | [{lo}, {hi}] | {n} |")
        S.append("_**Clean compliant disclosure (PROVIDED) despite the instruction is confined to Mistral/"
                 "Llama.** But token-out — the human-validated leak measure (PROVIDED+MENTIONED) — is nonzero "
                 "for Mistral (0.81) and Sonnet (0.30): they quote the bearer token inside a refusal. "
                 "Refusal-with-disclosure is lower-severity than clean hand-over, but the secret still "
                 "escaped. A PROVIDED-only metric hides this; F7 shows both._\n")
        S.append("### Neutral control — REFUSED = over-refusal of a LEGITIMATE citation (RLHF cost)")
        S.append("| model | over-refusal (REFUSED) | cluster-boot 95% CI | n | n_clusters |")
        S.append("|---|---|---|---|---|")
        for fam in sorted({r["victim_family"] for r in neut}):
            recs = [{"cluster": (r["scenario_id"], r.get("pretext", "neutral")),
                     "y": 1 if r["judge_label"] == "REFUSED" else 0}
                    for r in neut if r["victim_family"] == fam]
            p, lo, hi, nc = cluster_bootstrap_rate(recs)
            S.append(f"| {FAM.get(fam, fam)} | {p} | [{lo}, {hi}] | {len(recs)} | {nc} |")
        S.append("_Refusal of a legitimate audit citation = the over-refusal side of the security/utility "
                 "tradeoff; clustered by scenario (single neutral pretext). **Unequal denominators:** the "
                 "parsed n is attrited by UNPARSED unevenly across models (Sonnet 10/24 unparseable here vs "
                 "GPT/Llama/Qwen 0/24), so this is a directional tradeoff signal, not a clean cross-model "
                 "ranking — see the n column._\n")
        # attrition table so the caveat is checkable
        S.append("| model | parsed n | UNPARSED dropped |")
        S.append("|---|---|---|")
        for fam in sorted({r["victim_family"] for r in w7c if r.get("condition") == "neutral"}):
            alln = [r for r in w7c if r.get("condition") == "neutral" and r["victim_family"] == fam]
            unp = sum(1 for r in alln if r["judge_label"] not in ("PROVIDED", "MENTIONED", "REFUSED"))
            S.append(f"| {FAM.get(fam, fam)} | {len(alln) - unp} | {unp} |")
        S.append("")

    # ---- W4/W5 negatives table (Reviewer-2 required) ----
    S.append("\n## W4/W5 negative controls (Reviewer-2: give the negatives a table)")
    try:
        w4 = load(os.path.join(a.raw, "w4_lures.jsonl"))
        S.append("### W4 adaptive-harvest max lure-rate per (domain,victim) — single-shot injection is weak")
        S.append("| domain | victim | harvested lure_rate |")
        S.append("|---|---|---|")
        for r in w4:
            p = r["payload"]
            S.append(f"| {r['domain_id']} | {FAM.get(r['victim_family'], r['victim_family'])} | {p.get('harvested_lure_rate')} |")
    except Exception as e:
        S.append(f"(W4 table skipped: {str(e)[:80]})")
    try:
        w5 = [r for r in load(os.path.join(a.raw, "w5_gated_weak.jsonl")) if r.get("kind") == "gated"]
        # baseline vs influence pre-gate lure at D0 by victim (endogenous vs injected)
        byv = defaultdict(lambda: {"base": [], "inf": []})
        for r in w5:
            if r["defense_level"] != "D0_no_defense":
                continue
            byv[r["victim_family"]]["base"].append(r["baseline_p_lure"])
            if r["condition"] == "influence":
                byv[r["victim_family"]]["inf"].append(r["pre_gate_p_lure"])
        S.append("\n### W5 weak-victim: baseline vs injected lure at D0 (leak is ENDOGENOUS, not injected)")
        S.append("| victim | baseline_lure | influence_pre_lure | injected_delta |")
        S.append("|---|---|---|---|")
        for v, d in sorted(byv.items()):
            b = sum(d["base"]) / len(d["base"]) if d["base"] else None
            i = sum(d["inf"]) / len(d["inf"]) if d["inf"] else None
            dd = None if b is None or i is None else round(i - b, 3)
            S.append(f"| {FAM.get(v, v)} | {round(b,3) if b is not None else ''} | {round(i,3) if i is not None else ''} | {dd} |")
    except Exception as e:
        S.append(f"(W5 table skipped: {str(e)[:80]})")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(S) + "\n")
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
