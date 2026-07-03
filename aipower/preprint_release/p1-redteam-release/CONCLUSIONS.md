# Conclusions — P-1 red-team (EXP_25–28 + robustness checks)

**Date:** 2026-06-29
**Scope of this note:** what the series does and does not establish. Records: EXP_25–28; raw in
`exp25/26/27/28_artifacts/`.

> **What this study is.** A *hypothesis-existence + method-validation* study. Its goal is **not** to
> enumerate attacks, and **not** to rank models as safer/less safe. It asks three things only:
> (1) does the predicted effect occur at all? (2) do different models react differently? (3) does the
> measurement method hold up well enough to scale to broader experiments? Everything below is framed to
> those three questions.

---

## C1. The effect exists (both axes)

The model-layer prediction P-1 — *no deep + quiet capture; manipulation depth is bounded by
detectability* — is **not universal**. We have existence proofs on two distinct axes:

- **Factual capture.** On some frontier models, a *true-but-irrelevant* passage quietly flips a clear
  factual answer to a falsehood while an independent auditor scores it ≈0. Confirmed stable by
  K-sampling (GPT-5.5 10/10, Mistral 10/10, DeepSeek 7/10 on the transferable injection; δ≈0).
- **Opinion steering.** On pliable models, a neutral-looking passage reliably shifts a two-sided
  judgment by ~0.4–0.5 of the scale while reading as non-manipulative (δ≈0.05–0.30, K-confirmed).

So the *deep + quiet corner P-1 says is empty is reachable* — on some models, for some inputs. That is
the existence claim, and it holds. (It is **not** a claim that the corner is reachable on every model,
nor that we found the strongest attack — we explicitly did not look for that.)

## C2. Models react differently — and along *independent* axes

The differences are **structured, not random**, and they do not collapse to a single "robustness"
scalar. At least three axes came apart:

| axis | what it measures | example of the split |
|------|------------------|----------------------|
| fact-robustness | resists quiet capture toward a falsehood | clean 3:3 split: Opus/Sonnet/Qwen immune; GPT-5.5/Mistral/DeepSeek flip |
| opinion-anchoring | resists having a judgment steered | stable order: Opus<Sonnet<GPT<Mistral≈Qwen≈DeepSeek |
| veracity-discrimination | does it down-weight *fabrication* vs real evidence? (dissociation) | Opus resists false; DeepSeek/Mistral move *more* on false than true |

The headline of the heterogeneity is that **these axes are orthogonal**: a model can be hard to lie to
on facts yet easy to steer on opinions (Qwen), or break on the quiet fact-flip yet sit mid-pack on
opinions (GPT-5.5). "How a model fails" is as informative as "whether it fails."

**This is heterogeneity, not a league table.** We tested 6 items per axis and a few attackers; an
observation like "model X flips on this one passage" is an existence data-point about X's reaction
profile, **not** a verdict on X's overall safety.

## C3. The method holds up (validation)

This is the part meant to outlast the specific numbers:

1. **Role separation is mandatory.** Running attacker and victim as the same scaffolded model produces
   a *refusal artifact*, not a measurement (safety-tuned models — Claude, GPT-5.5 — refuse the covert
   masker role). Valid measurement needs raw completions + a separate, willing attacker.
2. **The metrics discriminate.** The steerability gap, the deep+quiet corner, and especially the
   **dissociation triad (balanced / slanted-true / false)** cleanly separate *manipulability* from
   *legitimate updating* — the conceptual tool that lets future work avoid mislabeling healthy
   evidence-response as capture.
3. **The empirical-stability gate is necessary and works — it corrected our own conclusions.** temp-0
   single samples overstate: several fact "hits" were demoted under K-sampling, and the dissociation's
   single-sample read was *materially wrong* in two places — "Qwen moves on the balanced placebo"
   (single 0.14 → K 0.06: noise) and "DeepSeek resists false" (single: false<true → K: false +0.30 >
   true +0.24: reversed). The K-sampled picture is cleaner: **no model is placebo-suggestible**
   (balanced |Δ|≤0.11 everywhere — models track content direction, not the mere presence of context),
   and the real differentiator is **veracity-discrimination** — Opus down-weights fabrication;
   DeepSeek/Mistral are moved *more* by it. K-sampling also reproduces the true effects (Opus matched
   to ±0.01; GPT-5.5 fact-flip 10/10). Always K-confirm before concluding.
4. **Findings are reproducible and model-bound, not attacker-luck.** Replaying the *exact* injection
   that flips GPT/Mistral against the robust trio yields 0/10 — robustness is a property of the model,
   not of which passage the attacker happened to draw.
5. **The auditor is informative and not idiosyncratic.** A non-kin auditor (Gemini) and a kin auditor
   (Claude) reach the same qualitative ordering of injection types; the one blind spot
   (true-but-irrelevant content reads as neutral) is **structural**, shared by both — so it reflects
   the input, not the auditor.
6. **Transferability is a real, separable dimension.** Injection potency splits into *idiosyncratic*
   (works only on its origin model — "bespoke snake oil") vs *transferable* (one passage flips the
   whole vulnerable class). For the model layer this matters more than raw per-model strength: a
   transferable injection poisons many decision-support stacks at once.

## C4. What this enables (the point of validating the method)

The harness now has a set of **validated knobs** for larger studies:
`target × attacker × attacker-mode(covert/honest) × injection-type(balanced/slanted/false) ×
auditor(kin/non-kin) × depth(self-report/K-sample)`.

Natural next experiments, now on solid footing:
- **Scale & domains:** many more items, harder/realistic decision-support domains (procurement, risk,
  intelligence-summary framing) rather than benign facts.
- **Capability sweep:** does any deep+quiet gap shrink or grow with model scale/version?
- **Transferability study:** build the full injection×victim transfer matrix; characterize what makes
  an injection transferable (the highest-leverage threat).
- **Attacker ensembles / adaptive search:** stronger maskers, multi-round, to probe the true frontier
  rather than a single attacker's draw.
- **Defense side:** can an auditor be tuned to catch the structural blind spot (true-but-irrelevant)?

## C5. Explicit non-claims (so the result isn't overread)

- We did **not** find the strongest attacks, nor exhaust the space; held bounds = "no counterexample
  found in this search," not "secure."
- We do **not** rank models by safety. Reaction *profiles* ≠ overall safety.
- Small N (6 items/axis), benign domains, mostly one generator/auditor, self-report depth proxy for
  sweeps. Directional evidence, not a benchmark.
- Yandex untested (no access). Dissociation K-sweep covers all 6; opinion matrix is 3 attackers × 6.

---

### One-line summary
**The effect is real, models react along several independent axes, and the measurement method —
role-separated, K-stabilized, dissociation-aware, auditor-checked — is sound enough to build wider
experiments on. That, not any single model verdict, is the result.**
