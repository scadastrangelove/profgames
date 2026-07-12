#!/usr/bin/env python3
"""Analyze W7e emphasis-matched label x referent records."""
import argparse
import csv
import json
import os
import random
import statistics

random.seed(20260710)
FAM = {"anthropic": "Opus-4.8", "anthropic_sonnet": "Sonnet-4.6", "openai": "GPT-5.5",
       "qwen": "Qwen3.7", "deepseek": "DeepSeek-v4", "mistral": "Mistral-lg",
       "llama_weak": "Llama-8b"}
CELLS = ("real_secret", "real_public", "inert_secret", "inert_public")


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def mean(rows, field):
    vals = [r[field] for r in rows if isinstance(r.get(field), (int, float))]
    return statistics.mean(vals) if vals else None


def effects(rows, field):
    cell = {c: mean([r for r in rows if r["cell"] == c], field) for c in CELLS}
    if any(cell[c] is None for c in CELLS):
        return cell, None, None, None
    label = ((cell["real_secret"] + cell["inert_secret"]) -
             (cell["real_public"] + cell["inert_public"])) / 2
    referent = ((cell["real_secret"] + cell["real_public"]) -
                (cell["inert_secret"] + cell["inert_public"])) / 2
    interaction = ((cell["real_secret"] - cell["real_public"]) -
                   (cell["inert_secret"] - cell["inert_public"]))
    return cell, label, referent, interaction


def cluster_ci(rows, field, effect_index, iterations=4000):
    clusters = sorted({r["scenario_id"] for r in rows})
    values = []
    for _ in range(iterations):
        sampled = [clusters[random.randrange(len(clusters))] for _ in clusters]
        boot = [r for cluster in sampled for r in rows if r["scenario_id"] == cluster]
        value = effects(boot, field)[effect_index]
        if value is not None:
            values.append(value)
    values.sort()
    return values[int(0.025 * len(values))], values[int(0.975 * len(values))]


def fmt(value):
    return "" if value is None else f"{value:.3f}"


def main():
    parser = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument("--jsonl", default=os.path.join(here, "..", "..", "artifacts", "raw",
                                                        "w7e_labelref_matched.jsonl"))
    parser.add_argument("--out-csv", default=os.path.join(here, "..", "..", "artifacts", "derived",
                                                          "w7e_labelref_matched.csv"))
    parser.add_argument("--out-md", default=os.path.join(here, "..", "..", "..",
                                                         "W7e_EMPHASIS_MATCHED.md"))
    args = parser.parse_args()
    rows = load(args.jsonl)
    if not rows:
        raise SystemExit(f"no records in {args.jsonl}")
    valid = [r for r in rows if not r.get("reply", "").startswith("ERR:")]
    posture_valid = [r for r in valid if r.get("judge_label") in ("PROVIDED", "MENTIONED", "REFUSED")]
    families = sorted({r["victim_family"] for r in valid})

    output_rows = []
    for family in families:
        subset = [r for r in valid if r["victim_family"] == family]
        contained, dl, dr, interaction = effects(subset, "token_contained")
        posture_subset = [r for r in posture_valid if r["victim_family"] == family]
        posture, pdl, pdr, pinteraction = effects(posture_subset, "guard_posture")
        output_rows.append({
            "model": FAM.get(family, family),
            **{f"contained_{cell}": contained[cell] for cell in CELLS},
            "contained_d_label": dl,
            "contained_d_referent": dr,
            "contained_interaction": interaction,
            **{f"posture_{cell}": posture[cell] for cell in CELLS},
            "posture_d_label": pdl,
            "posture_d_referent": pdr,
            "posture_interaction": pinteraction,
        })

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    columns = list(output_rows[0])
    with open(args.out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in output_rows:
            writer.writerow({key: fmt(value) if isinstance(value, float) else value for key, value in row.items()})

    contained, dl, dr, interaction = effects(valid, "token_contained")
    posture, pdl, pdr, pinteraction = effects(posture_valid, "guard_posture")
    dl_ci = cluster_ci(valid, "token_contained", 1)
    dr_ci = cluster_ci(valid, "token_contained", 2)
    pdl_ci = cluster_ci(posture_valid, "guard_posture", 1)
    pdr_ci = cluster_ci(posture_valid, "guard_posture", 2)
    dominant = sum(row["contained_d_label"] > row["contained_d_referent"] for row in output_rows)
    tied = sum(row["contained_d_label"] == row["contained_d_referent"] for row in output_rows)
    errors = len(rows) - len(valid)
    unparsed = len(valid) - len(posture_valid)
    prompt_hashes = sorted({r.get("prompt_hash") for r in rows if r.get("prompt_hash")})
    run_dates = sorted({r.get("run_started_utc", "")[:10] for r in rows if r.get("run_started_utc")})
    md = [
        "# W7e - Emphasis-matched public-label control",
        "",
        "Both policy polarities use matched capitalization, modality, exception lists, and length. Only the",
        "policy polarity (PRIVATE/MUST NOT versus PUBLIC/MUST) and token referent vary. The primary outcome",
        "is deterministic exact-token containment; refusal posture is a secondary judge-classified outcome.",
        "",
        "## Per-model strict containment",
        "| model | real+secret | real+public | inert+secret | inert+public | D_policy | D_referent | interaction |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in output_rows:
        md.append("| {model} | {contained_real_secret} | {contained_real_public} | {contained_inert_secret} | "
                  "{contained_inert_public} | {contained_d_label} | {contained_d_referent} | "
                  "{contained_interaction} |".format(**{
                      key: fmt(value) if isinstance(value, float) else value for key, value in row.items()
                  }))
    md.extend([
        "",
        "## Pooled cell rates",
        "| outcome | real+secret | real+public | inert+secret | inert+public |",
        "|---|---:|---:|---:|---:|",
        "| strict containment | " + " | ".join(fmt(contained[cell]) for cell in CELLS) + " |",
        "| refusal posture | " + " | ".join(fmt(posture[cell]) for cell in CELLS) + " |",
        "",
        "## Pooled effects",
        f"- strict containment: D_policy = {dl:.3f} (cluster-bootstrap 95% CI [{dl_ci[0]:.3f}, "
        f"{dl_ci[1]:.3f}]); D_referent = {dr:.3f} ([{dr_ci[0]:.3f}, {dr_ci[1]:.3f}]); "
        f"interaction = {interaction:.3f}",
        f"- refusal posture: D_policy = {pdl:.3f} ([{pdl_ci[0]:.3f}, {pdl_ci[1]:.3f}]); "
        f"D_referent = {pdr:.3f} ([{pdr_ci[0]:.3f}, {pdr_ci[1]:.3f}]); "
        f"interaction = {pinteraction:.3f}",
        "",
        f"D_policy exceeds D_referent in {dominant}/{len(output_rows)} selected model rows"
        + (f", with {tied} tie(s)." if tied else "."),
        "This is a consistency description, not a sign-test inference over an exchangeable model population.",
        "",
        "## Run integrity",
        f"- valid target records: {len(valid)}/{len(rows)}; API errors: {errors}",
        f"- parsed posture labels: {len(posture_valid)}/{len(valid)}; UNPARSED: {unparsed}",
        f"- run date(s): {', '.join(run_dates)}",
        f"- prompt hash(es): {', '.join(prompt_hashes)}",
        "- bootstrap clusters are the three scenarios and remain coarse",
    ])
    with open(args.out_md, "w", encoding="utf-8") as handle:
        handle.write("\n".join(md) + "\n")
    print(f"wrote {args.out_csv} and {args.out_md}")


if __name__ == "__main__":
    main()
