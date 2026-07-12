#!/usr/bin/env python3
"""Generate the paper/review-pack figures from the derived CSVs (+ some raw jsonl for F9). Needs matplotlib.
  python make_figures.py --derived ../../artifacts/derived --out-dir ../../../review_pack/figures
Outputs F1..F9 as PNG (150 dpi). F9 (susceptibility panorama) also reads raw w7c/w7d jsonl, w8_capture.csv
(7-model), and exp29_flip.csv (2 opinion-flip columns imported from the prior paper's EXP-29 matrix)."""
import argparse
import csv
import json
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FAM = {"anthropic": "Opus-4.8", "anthropic_sonnet": "Sonnet-4.6", "openai": "GPT-5.5",
       "qwen": "Qwen3.7", "deepseek": "DeepSeek-v4", "mistral": "Mistral-lg", "llama_weak": "Llama-8b"}
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})


def rd(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def F1_dissociation(d, out):
    rows = rd(os.path.join(d, "mvp_v2_auditor_dissociation.csv"))
    labels = [r["relevance_label"] for r in rows]
    roles = ["content", "relevance", "provenance", "independence"]
    data = {ro: [float(r[f"mean_{ro}"]) for r in rows] for ro in roles}
    # cluster-bootstrap CIs (payload-clustered), if available
    err = {ro: [[0] * len(labels), [0] * len(labels)] for ro in roles}
    cip = os.path.join(d, "w1_dissociation_ci.csv")
    if os.path.exists(cip):
        ci = {(r["label"], r["role"]): r for r in rd(cip)}
        for li, lab in enumerate(labels):
            for ro in roles:
                if (lab, ro) in ci:
                    m = data[ro][li]
                    err[ro][0][li] = m - float(ci[(lab, ro)]["ci95_lo"])
                    err[ro][1][li] = float(ci[(lab, ro)]["ci95_hi"]) - m
    x = np.arange(len(labels)); w = 0.2
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, ro in enumerate(roles):
        ax.bar(x + (i - 1.5) * w, data[ro], w, yerr=err[ro], capsize=2, label=ro)
    ax.set_xticks(x); ax.set_xticklabels(["false\n(fabricated)", "irrelevant\n(true-but-off-rule)", "relevant\n(token-verified)"])
    ax.set_ylabel("mean auditor flag (0-1)"); ax.set_ylim(0, 1.05)
    ax.set_title("Auditor dissociation (W1): different roles detect different failure classes")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    fig.savefig(os.path.join(out, "F1_auditor_dissociation.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F2_durable_sp(d, out):
    rows = rd(os.path.join(d, "w9b_permeability.csv"))
    vehicles = ["memory", "rag", "wiki"]; defenses = ["none", "provenance_bound", "cooling_off", "memory_quarantine"]
    val = {(r["vehicle"], r["defense"]): float(r["selective_permeability"]) for r in rows}
    cip = os.path.join(d, "w9b_permeability_ci.csv")
    cis = {(r["vehicle"], r["defense"]): r for r in rd(cip)} if os.path.exists(cip) else {}
    x = np.arange(len(vehicles)); w = 0.2
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for i, dfn in enumerate(defenses):
        vals = [val.get((v, dfn), 0) for v in vehicles]
        elo = [max(0, vals[j] - float(cis[(v, dfn)]["ci95_lo"])) if (v, dfn) in cis else 0 for j, v in enumerate(vehicles)]
        ehi = [max(0, float(cis[(v, dfn)]["ci95_hi"]) - vals[j]) if (v, dfn) in cis else 0 for j, v in enumerate(vehicles)]
        ax.bar(x + (i - 1.5) * w, vals, w, yerr=[elo, ehi], capsize=2, label=dfn)
    ax.set_xticks(x); ax.set_xticklabels(["memory", "rag", "wiki"])
    ax.set_ylabel("durable selective permeability\n(update−leak)"); ax.set_ylim(0, 0.8)
    ax.set_title("Long-horizon W9b: provenance-bound improves memory; RAG is uncertain;\n"
                 "merged-wiki compaction erases 0/42 issuer tokens")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    fig.savefig(os.path.join(out, "F2_durable_selective_permeability.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F3_disclosure(d, out):
    rows = rd(os.path.join(d, "w7b_disclosure.csv"))
    rows.sort(key=lambda r: float(r["token_out_rate"]))
    names = [FAM.get(r["victim_family"], r["victim_family"]) for r in rows]
    provided = [float(r["provided_rate"]) for r in rows]
    mentioned = [float(r["mentioned_rate"]) for r in rows]
    token_out = [float(r["token_out_rate"]) for r in rows]
    lo = [token_out[i] - float(r["token_out_ci95_lo"]) for i, r in enumerate(rows)]
    hi = [float(r["token_out_ci95_hi"]) - token_out[i] for i, r in enumerate(rows)]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(y, provided, color="#a93226", label="PROVIDED (clean/usable handover)")
    ax.barh(y, mentioned, left=provided, color="#d98880", hatch="////",
            label="MENTIONED (token emitted within refusal)")
    ax.errorbar(token_out, y, xerr=[lo, hi], fmt="none", ecolor="#202322", capsize=3, lw=1)
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xlabel("token-out rate (PROVIDED + MENTIONED), Wilson 95% CI"); ax.set_xlim(0, 1.05)
    ax.set_title("W7b no-instruction condition: whether the bearer string leaves the model.\n"
                 "Token-out is primary; PROVIDED and MENTIONED show secondary severity.")
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2)
    fig.savefig(os.path.join(out, "F3_token_disclosure.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F4_scamops(d, out):
    rows = rd(os.path.join(d, "w8_capture.csv"))
    mechs = sorted({r["mechanism"] for r in rows}); fams = ["anthropic", "openai", "deepseek", "mistral"]
    val = {(r["mechanism"], r["victim_family"]): float(r["capture_no_defense"]) for r in rows}
    x = np.arange(len(mechs)); w = 0.2
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, fam in enumerate(fams):
        ax.bar(x + (i - 1.5) * w, [val.get((m, fam), 0) for m in mechs], w, label=FAM[fam])
    ax.set_xticks(x); ax.set_xticklabels([m.replace("_", "\n") for m in mechs], fontsize=8)
    ax.set_ylabel("capture rate, no defense"); ax.set_ylim(0, 1.05)
    ax.set_title("ScamOps pressure (W6/W8 pilot): capture is model- and mechanism-specific")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    fig.savefig(os.path.join(out, "F4_scamops_capture.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F5_forgery(d, out):
    rows = rd(os.path.join(d, "w7b_forgery.csv"))
    fams = ["anthropic", "anthropic_sonnet", "openai", "qwen", "deepseek", "mistral", "llama_weak"]
    def get(fam, dfn, k):
        for r in rows:
            if r["victim_family"] == fam and r["defense"] == dfn:
                return float(r[k])
        return 0.0
    x = np.arange(len(fams)); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4))
    for j, dfn in enumerate(["none", "registry"]):
        vals = [get(f, dfn, "forged_accept_rate") for f in fams]
        errlo = [vals[i] - get(f, dfn, "ci95_lo") for i, f in enumerate(fams)]
        errhi = [get(f, dfn, "ci95_hi") - vals[i] for i, f in enumerate(fams)]
        ax.bar(x + (j - 0.5) * w, vals, w, yerr=[errlo, errhi], capsize=3, label=f"defense: {dfn}")
    ax.set_xticks(x); ax.set_xticklabels([FAM[f] for f in fams], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("forged-token acceptance ± 95% CI"); ax.set_ylim(0, 1.05)
    ax.set_title("Token forgery (W7b): acceptance is observed for Mistral and the Llama control;\n"
                 "the registry removes the observed Mistral effect")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(out, "F5_token_forgery.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F6_gated_heatmap(d, out):
    rows = rd(os.path.join(d, "mvp_v2_selective_permeability.csv"))
    defs = ["D0_no_defense", "D1_content_audit", "D2_relevance_provenance_independence",
            "D3_action_critic", "D4_known_good_source_registry"]
    fams = ["anthropic", "anthropic_sonnet", "openai", "qwen", "deepseek", "mistral"]
    M = np.full((len(defs), len(fams)), np.nan)
    idx = {(r["defense_level"], r["victim_family"]): r for r in rows}
    for i, dd in enumerate(defs):
        for j, fam in enumerate(fams):
            r = idx.get((dd, fam))
            if r and r["selective_permeability"]:
                M[i, j] = float(r["selective_permeability"])
    fig, ax = plt.subplots(figsize=(7.5, 4))
    im = ax.imshow(M, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(fams))); ax.set_xticklabels([FAM[f] for f in fams], rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(defs))); ax.set_yticklabels([
        "D0 none", "D1 content", "D2 rel+prov+indep", "D3 action critic", "D4 registry"
    ])
    for i in range(len(defs)):
        for j in range(len(fams)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Gated selective permeability (W1): gates can suppress authorized updates\n"
                 "when the illegitimate-leak component is already low")
    fig.colorbar(im, ax=ax, label="selective permeability")
    fig.savefig(os.path.join(out, "F6_gated_permeability_heatmap.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F7_security_vs_overrefusal(d, out):
    prot = {r["victim_family"]: r for r in rd(os.path.join(d, "w7c_protected.csv"))}
    neut = {r["victim_family"]: r for r in rd(os.path.join(d, "w7c_neutral.csv"))}
    # order by token-out (provided+mentioned) descending
    fams = sorted([f for f in prot], key=lambda f: -(float(prot[f]["provided_rate"]) + float(prot[f]["mentioned_rate"])))
    prov = [float(prot[f]["provided_rate"]) for f in fams]            # clean hand-over DESPITE nondisclosure
    ment = [float(prot[f]["mentioned_rate"]) for f in fams]           # token exposed WHILE refusing
    over = [float(neut[f]["refused_rate"]) if f in neut else 0 for f in fams]
    over_lo = [float(neut[f]["refused_bound_lo"]) if f in neut else 0 for f in fams]
    over_hi = [float(neut[f]["refused_bound_hi"]) if f in neut else 0 for f in fams]
    y = np.arange(len(fams)); h = 0.38
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ax.barh(y + h / 2, prov, h, color="#c0392b", label="clean hand-over despite 'never disclose' (PROVIDED)")
    ax.barh(y + h / 2, ment, h, left=prov, color="#c0392b", hatch="////", alpha=0.55,
            label="token exposed WHILE refusing (MENTIONED)")
    ax.barh(y - h / 2, over, h, color="#e0a02b", label="parsed refusal rate on legitimate citation")
    ax.errorbar(over, y - h / 2,
                xerr=[[over[i] - over_lo[i] for i in range(len(over))],
                      [over_hi[i] - over[i] for i in range(len(over))]],
                fmt="none", ecolor="#202322", capsize=3, lw=1,
                label="all-missing-as-no / all-missing-as-refusal bounds")
    for i, f in enumerate(fams):  # annotate total token-out
        t = prov[i] + ment[i]
        if t > 0.02:
            ax.text(t + 0.01, y[i] + h / 2, f"{t:.2f}", va="center", fontsize=7)
    ax.set_yticks(y); ax.set_yticklabels([FAM[f] for f in fams])
    ax.set_xlim(0, 1.12); ax.set_xlabel("rate")
    ax.set_title("W7c reports two distinct outcomes, not a universal trade-off.\n"
                 "Protected-condition token exposure is separated from legitimate-request refusal;\n"
                 "error bars on the latter are worst-case bounds for model-dependent missing outputs.")
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.savefig(os.path.join(out, "F7_security_vs_overrefusal.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F8_label_vs_referent(d, out):
    rows = rd(os.path.join(d, "w7e_labelref_matched.csv"))
    rows.sort(key=lambda r: -float(r["contained_d_label"]))
    names = [r["model"] for r in rows]
    dl = [float(r["contained_d_label"]) for r in rows]
    dr = [float(r["contained_d_referent"]) for r in rows]
    y = np.arange(len(names)); h = 0.38
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.barh(y + h / 2, dl, h, color="#176b58", label="Policy effect: secret - public")
    ax.barh(y - h / 2, dr, h, color="#82928d", label="Referent effect: real - inert")
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.axvline(0, color="k", lw=0.8); ax.set_xlim(-0.15, 1.05)
    ax.set_xlabel("difference in exact-token containment rate")
    ax.set_title("W7e emphasis-matched control: in-context policy polarity dominates referent.\n"
                 "Pooled effects: policy 0.73; referent 0.00. Policy is larger for all seven selected models.\n"
                 "Three scenario clusters; descriptive.")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.savefig(os.path.join(out, "F8_label_vs_referent.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def F9_susceptibility_matrix(d, out):
    """The panorama: model × attack-vector susceptibility. Reads derived CSVs + raw jsonl (w7c/w7d)."""
    raw = os.path.join(d, "..", "raw")
    rj = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    fams = ["anthropic", "anthropic_sonnet", "openai", "qwen", "deepseek", "mistral", "llama_weak"]
    disp = dict(FAM); disp["llama_weak"] = "Llama-8b (weak ctrl)"
    # col 1: crude ScamOps pressure (max over mechanisms, no defense) — 4-model coverage
    crude = defaultdict(float); seen = set()
    for r in rd(os.path.join(d, "w8_capture.csv")):
        crude[r["victim_family"]] = max(crude[r["victim_family"]], float(r["capture_no_defense"])); seen.add(r["victim_family"])
    # col 2: token disclosure under benign pretext (W7b token-out)
    disc = {r["victim_family"]: float(r["provided_rate"]) + float(r["mentioned_rate"]) for r in rd(os.path.join(d, "w7b_disclosure.csv"))}
    # col 3: token leak DESPITE 'never disclose' (W7c protected token-out)
    pc = defaultdict(lambda: [0, 0])
    for r in rj(os.path.join(raw, "w7c_token_judged.jsonl")):
        if r.get("condition") == "protected" and r["judge_label"] in ("PROVIDED", "MENTIONED", "REFUSED"):
            pc[r["victim_family"]][1] += 1; pc[r["victim_family"]][0] += r["judge_label"] in ("PROVIDED", "MENTIONED")
    leakp = {f: (v[0] / v[1] if v[1] else None) for f, v in pc.items()}
    # col 4: accepts a forged token (no defense)
    forg = {r["victim_family"]: float(r["forged_accept_rate"]) for r in rd(os.path.join(d, "w7b_forgery.csv")) if r["defense"] == "none"}
    # col 5: emits the REAL lever when framed 'routine' (W7d real+public token-out)
    rc = defaultdict(lambda: [0, 0])
    for r in rj(os.path.join(raw, "w7d_labelref.jsonl")):
        if r["cell"] == "real_public" and r["judge_label"] in ("PROVIDED", "MENTIONED", "REFUSED"):
            rc[r["victim_family"]][1] += 1
            rc[r["victim_family"]][0] += r["judge_label"] in ("PROVIDED", "MENTIONED")
    casual = {f: (v[0] / v[1] if v[1] else None) for f, v in rc.items()}
    # cols 6-7: opinion-flip from the PRIOR paper (EXP-29 keyed-payload confusion matrix), pre-computed CSV
    e29 = {r["victim_family"]: r for r in rd(os.path.join(d, "exp29_flip.csv"))} if os.path.exists(os.path.join(d, "exp29_flip.csv")) else {}
    fmean = {f: float(r["flip_mean"]) for f, r in e29.items()}
    fpeak = {f: float(r["flip_peak"]) for f, r in e29.items()}
    cols = [("Crude\npressure", crude, seen, "A"),
            ("Token out\n(benign ask)", disc, set(disc), "A"),
            ("Token leaked\ndespite policy", leakp, set(leakp), "A"),
            ("Forged token\naccepted", forg, set(forg), "A"),
            ("Real auth-lever out\n(labeled 'routine')", casual, set(casual), "A"),
            ("Opinion flip\n(keyed, mean)", fmean, set(fmean), "B"),
            ("Opinion flip\n(keyed, worst)", fpeak, set(fpeak), "B")]
    M = np.full((len(fams), len(cols)), np.nan)
    for j, (_, dct, sn, _g) in enumerate(cols):
        for i, f in enumerate(fams):
            if f in sn and dct.get(f) is not None:
                M[i, j] = dct[f]
    order = np.argsort(np.nanmean(M, axis=1)); fams = [fams[i] for i in order]; M = M[order]
    fig, ax = plt.subplots(figsize=(14, 6))
    cmap = plt.cm.Reds.copy(); cmap.set_bad("#e8e8e8")
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([c[0] for c in cols], fontsize=9.5)
    ax.set_yticks(range(len(fams))); ax.set_yticklabels([disp[f] for f in fams], fontsize=10.5)
    for i in range(len(fams)):
        for j in range(len(cols)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=8, color="#888")
            else:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=10,
                        color="white" if v > 0.55 else "black", fontweight="bold" if v >= 0.5 else "normal")
    ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True); ax.set_yticks(np.arange(-.5, len(fams), 1), minor=True)
    ax.grid(which="minor", color="white", lw=2); ax.tick_params(which="minor", length=0)
    # divider + group super-labels: A = this work (credential/provenance), B = prior paper (opinion flip)
    nA = sum(1 for c in cols if c[3] == "A")
    ax.axvline(nA - 0.5, color="#333", lw=2.5)
    ax.text((nA - 1) / 2, -0.9, "credential / provenance assays (this work)", ha="center", va="bottom",
            fontsize=9.5, style="italic", color="#444")
    ax.text(nA + (len(cols) - nA - 1) / 2, -0.9, "opinion-flip — prior paper [Gordeychik 2026]", ha="center",
            va="bottom", fontsize=9.5, style="italic", color="#444")
    cb = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015); cb.set_label("susceptibility (leak / flip rate)", fontsize=9)
    ax.set_title("Model x attack susceptibility (red = higher measured susceptibility).\n"
                 "Credential/provenance assays and the imported opinion-flip assays are separated because their designs differ.",
                 fontsize=11.5, fontweight="bold", pad=30)
    fig.savefig(os.path.join(out, "F9_susceptibility_matrix.png"), dpi=150, bbox_inches="tight"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    publication_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    figure_root = publication_root if os.path.exists(os.path.join(publication_root, "preprint.md")) \
        else os.path.join(publication_root, "review_pack")
    ap.add_argument("--derived", default=os.path.join(here, "..", "..", "artifacts", "derived"))
    ap.add_argument("--out-dir", default=os.path.join(figure_root, "figures"))
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    for fn in (F1_dissociation, F2_durable_sp, F3_disclosure, F4_scamops, F5_forgery, F6_gated_heatmap,
               F7_security_vs_overrefusal, F8_label_vs_referent, F9_susceptibility_matrix):
        try:
            fn(a.derived, a.out_dir); print("ok", fn.__name__)
        except Exception as exc:
            print("ERR", fn.__name__, str(exc)[:120])
    print("figures ->", os.path.abspath(a.out_dir))


if __name__ == "__main__":
    main()
