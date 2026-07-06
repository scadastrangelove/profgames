# Paper 2 — key theses draft (v2, reviewer-revised)

**Working title.** *Selective Permeability: A Two-Sided Metric for Human–Agent Influence Resilience, and
Two Under-Tested Failure Modes of Bearer-Style, In-Context-Secret Provenance Workflows.*

**One-sentence thesis (narrowed).** Human–agent influence resilience is not "does the advisor conform"
but a two-sided *selective permeability* — update on relevant, authorized evidence while resisting
irrelevant/unauthorized/coercive influence — and provenance-bound controls can preserve useful
permeability **where authority metadata survives**, but those very controls have two *new* failure modes
we measure: **credential disclosure/forgery pressure** (advisors leak or accept the authority token) and
**summarization-induced source amnesia** (compaction destroys the token the control depends on).

> We do **not** claim "provenance, not aggregation, is the defense" (an earlier draft over-reached and
> leaned on a mis-attributed citation; see §Scope). We claim provenance-bound controls help *conditionally*
> and identify when and how they break.

Evidence base: waves W1–W9b on 7 models (opus-4.8, sonnet-4.6, gpt-5.5, qwen3.7-max, deepseek-v4-pro,
mistral-large-2512, + weak llama-3.1-8b), raw completions over OpenRouter, 2026-07-04/05. **Evidence
strength is uneven — see §Evidence tiers; treat W7/W6/W8 as pilots.** Data + harness: `aigeopol-labs/`.
Positioning: `POSITIONING.md`.

## Evidence tiers (do not present in one confident tone)
- **Strong / near-standalone:** W1 (audit dissociation, 6 victims × full matrix) and W9b (provenance-bound
  memory + source-amnesia failure mode, 7 victims, real cross-session persistence). These carry the paper.
- **Pilot:** W6/W8 ScamOps (small N: 4 victims × 3 tasks × K4). Directional; frame as pilots.
- **Strengthened (W7b):** token disclosure/forgery re-run at 7 victims × 3 pretexts × K8 (n≈72/victim),
  with a provision-vs-mention judge classifier + Wilson CIs. Now defensible (the classifier caught a real
  substring-metric false-positive — sonnet). Human-coded validation **done** (leak-detector κ=1.0, not a
  clean-vs-hedged classifier; HUMAN_VALIDATION.md); hierarchical logit **done** (GLMM.md, incl. random
  slopes). Remaining: 2nd token format, non-bearer condition. (Original 12-cell W7 retained as the pilot
  that motivated it.)

---

## Contributions (what is genuinely new)

1. **Selective permeability as a two-sided metric** = update-on-authorized-relevant − leak-on-irrelevant/
   unauthorized, measured by a *blinded* content/relevance/provenance/independence auditor panel using a
   *verifiable issuer-token*. The conformity/sycophancy literature measures conformity one-sidedly (did
   accuracy drop / did it capitulate); we measure the tradeoff. (Nearest prior art: two-sided revision
   asymmetry [2606.01637] on QA-direction, and Wardens' [2605.08321] adversary-vs-benign cost — we
   differentiate on the authorization/provenance axis and the token mechanism.)
2. **Token-extraction / forgery attack on a provenance defense** — a pretext that makes an LLM advisor
   *disclose* or *accept a forged* authority token. Zero prior art in the conformity/sycophancy corpus.
3. **Long-horizon demonstration** that provenance-bound memory enables *durable* selective permeability,
   and that ordinary wiki/summary compaction *destroys the provenance the defense needs* (source amnesia).
4. **Rigorous negatives + a model-heterogeneity map** across single-shot, multi-turn, and memory regimes.

---

## Theses (each grounded in a result)

**T1 — Audit decomposition works; content-only audit is structurally blind.** A blinded panel cleanly
dissociates influence types: content auditors score true-but-irrelevant evidence LOW (0.33) — i.e. blind
to it — while relevance auditors catch it (0.98), and a verifiable issuer-token lets provenance auditors
admit a legitimate authorized update (0.003) yet flag a forged one (1.00). *(W1; operationalizes Prop 2′/
Cor 4.1.)*

**T2 — The metric must be two-sided; naive gates buy resistance by destroying permeability.** A blanket
quarantine/registry gate blocks the lure but also over-blocks legitimate authorized updates, so its
*selective* permeability is low; a token-verifying gate is the only one that raises both. *(W1, W5, W9b;
consistent with and citing Wardens' over-cautiousness [2605.08321].)*

**T3 — On frontier models in explicit-rule tasks, single-shot relevance injection barely works — even
adaptively.** An adaptive covert masker maxes at 0.167 lure-rate; the apparent "leak" of a weak model is
*endogenous* task-failure (llama baseline lure 0.33, injection adds −0.08), not manipulation. The threat
is not single-shot false/irrelevant content on competent models. *(W4, W5.)*

**T4 — Crude authority is a weak attack; the danger is subtler pressure and per-model.** A blunt
"authority directive" flips mistral 100% and deepseek 33% but leaves opus/gpt untouched; a 3-of-5 Asch
consensus flips only mistral (0.33). Cooling-off (forced re-derivation) is the best recovery; a single
dissenter is the strongest *published* defense but has little to recover when the attack already fails.
*(W6, W8; dissenter = [2605.12991].)*

**T5 — MOST frontier advisors provide the provenance credential under a benign pretext (W7b, strengthened).**
Across 7 victims × 3 pretext classes × K8 (n≈72/victim), a judge-classified PROVIDED rate (actually
supplied the credential, vs merely quoting it while refusing): gpt-5.5 1.00 [.95,1.0], llama 1.00, mistral
.88, qwen .86, opus .72 [.60,.81], deepseek .71 — including the models that resisted crude authority.
**The notable exception is sonnet (.03): the provision-vs-mention classifier corrected a substring-metric
false-positive — sonnet quotes the token while refusing (mentioned .54).** So the claim (no-instruction
W7b, read as a **leak/emit rate**, not clean disclosure) is "*most* frontier advisors **emit** the
credential under pretext, sonnet excepted," not "every"; under the W7c nondisclosure instruction it drops
sharply and is reported by severity (token-out = provided+mentioned; §7.4/F7). Forgery-acceptance
is model-specific (mistral .92 → .00 under a registry policy; llama .42; opus/gpt/sonnet/qwen/deepseek
.00 — they verify the token). The *mechanism* — a provenance control defeated by credential disclosure/
forgery pressure — is the novel contribution. *(W7b; forgery with Wilson CIs.)*

**T6 — Long-horizon: provenance-bound memory gives durable selective permeability, but compaction erases
it.** Across a real session boundary (write in one run, read in another), token-verifying memory is the
winner — a **clear win in memory** (SP 0.52, CI disjoint from no-defense) and a **marginal, CI-overlapping
increment in RAG** (0.69 vs 0.62): it admits the real-token authorized update (0.66/0.86) and blocks the
forged one (0.13/0.17); naive quarantine over-blocks. But summarizing
notes into a wiki page retained 0/42 issuer tokens (total source amnesia), collapsing every defense on the
wiki channel (SP ≈ 0). Durable capture from a forged-token note is again model-split (llama 0.67, mistral
0.44, opus/gpt/sonnet/qwen 0.00). And 9/21 advisors will *fabricate* a token-bearing "authorized" note
under pretext (7/21 refuse). *(W9b.)*

**T7 — Model heterogeneity is structured, not noise.** Opus is "sticky" (resists manipulation AND
legitimate updates — update-adoption 0.34 vs deepseek/mistral/openai ~1.0); mistral is the recurring
weak point (authority 1.0, forgery 0.83, durable memory leak 0.44); the small llama is endogenously
error-prone. Robustness on one axis does not imply robustness on another (e.g. opus/gpt reject token
*forgery* yet freely *disclose* the token). *(W1, W6, W7, W9b.)*

---

## Scope of the provenance claim (narrowed)

Our data support a **conditional** claim, not "provenance beats aggregation." Where a verifiable authority
token is present and survives, a token-verifying control gives the best *selective* permeability — a
**clear win on the memory channel, a marginal (CI-overlapping) increment on RAG** (W1, W9b). But this is
scoped to **bearer-style, in-context-secret** provenance workflows, and even there provenance is not a
free win: it has **two under-tested failure modes we measure** (under-tested, not first-reported), which
is the paper's sharper contribution:
1. **Credential disclosure / forgery pressure** — without a secrecy instruction most advisors *emit* the
   token to a benign pretext (compliance); under an explicit nondisclosure instruction the leak is
   confined to weaker/less-aligned models (Mistral/Llama), while stronger refusal buys an *over-refusal*
   cost on legitimate citations (W7b/W7c). Forgery acceptance is model-specific (Mistral/Llama); a
   registry policy fixes Mistral. The judge is human-validated as a *leak detector* (token-out κ=1.0), not
   as a clean-vs-hedged severity classifier (HUMAN_VALIDATION.md).
2. **Summarization-induced source amnesia** — routine compaction into a merged wiki/summary retained 0/42
   issuer tokens, collapsing every token-based defense on that channel; it is a *pipeline artifact*,
   summarizer-dependent and **mitigable** with per-item, provenance-preserving summarization (W9b/W9d).

**Behavioral core under the disclosure result (W7d, label-vs-referent).** With the pretext held constant,
guard/leak behavior tracks the secrecy **label** ("private credential", Δ=0.87) far more than the
**referent** — whether the token actually authorizes anything (Δ=0.04). **7/7 models** independently show
Δ_label > Δ_referent (sign test p=0.016; the robust statement — the pooled 3-cluster CI is coarse). Models
guard a string explicitly labelled public-and-inert (0.94) and hand over the *real* authorization lever
when it is framed casually (0.89). Δ_referent is **not exactly zero** — better-aligned models keep a weak
residual (Opus 0.17, Sonnet 0.14, DeepSeek 0.11; Qwen/GPT ≈0). So: a strong label main effect with a weak,
alignment-graded referent-sensitivity — provenance "security" is largely **stimulus-bound to surface
words**, the psychological cause behind the disclosure numbers, and an on-thesis behavioral finding (not a
technical-control result). This also reframes the non-bearer scope question: a non-bearer control would
trivially block the attack precisely *because the model barely engages the semantics*.

External support for provenance-skepticism-of-aggregation is **weaker than an earlier draft implied**:
LLMs fabricate social proof when fooled ([2606.13610], verified), and peer agreement misleads correct
models more than it corrects wrong ones ([2606.01637], verified) — both argue aggregation/consensus is
unsafe, but neither is an impossibility theorem. (The "Impossibility Trinity" we previously cited was
attributed to the wrong arXiv ID and is dropped pending a verified source.)

## Defense ranking (synthesis, with the conditional)
verifiable-token provenance gate — best selective permeability **when the token is present, unforged, and
survives compaction** > cooling-off / forced re-derivation (good, temporal, under-studied) >
single-dissenter (strong on genuine conformity; **published — [2605.12991], we reuse it**) > naive
quarantine / registry (blocks the lure but over-blocks legitimate updates — the over-cautiousness tradeoff
of **[2605.08321] Wardens, which we reuse/cite, not claim**). Content-only audit is structurally
insufficient (W1).

## Published defenses we REUSE vs our contribution (keep separate)
- **Reused (cite, do not claim):** third-party oversight / over-cautiousness tradeoff — Wardens
  [2605.08321]; single-dissenter injection — "Not Just RLHF" [2605.12991]; formal non-malleable
  origin-bound memory authority (TMA-NM) — [2606.24322] (nearest neighbor to W9b; they give a formal
  zero-ASR defense, we give an empirical measurement across 7 frontier models + the source-amnesia and
  credential-disclosure failure modes they do not test).
- **Ours:** the two-sided selective-permeability metric + blinded issuer-token auditor panel (W1); the
  token-extraction/forgery attack on a provenance control (W7); the empirical demonstration that
  compaction destroys provenance (source amnesia, W9b).

## Non-claims / limitations
- Small N, synthetic benign decision tasks; effect sizes directional.
- Frontier models are largely untested in prior conformity work → new ground, but not apples-to-apples
  for effect-size comparison.
- Disclosure/self-laundering metrics use token-substring detection; refusal-that-quotes-the-token is
  filtered but should be refined to provision-vs-mention before final numbers.
- Yandex/GigaChat untested (no OpenRouter access).
- Anchor corpus is preprint-heavy (2026); some "preliminary."
- ScamOps mechanisms are abstracted, benign, defensive ("borrow structure, not scripts").

## To strengthen before submission (reviewer-driven)
*Status: items 1–3 largely done in the review-pack round; remaining gaps are marked below.*
1. **W7 (flagship): DONE** — expanded to 7 models, K8, 3 pretext classes, provision-vs-mention judge +
   completed human coding (leak-detector κ=1.0; HUMAN_VALIDATION.md), per-sample outcomes stored, W7c
   protected/neutral conditions added. **Remaining:** a 2nd token format and a **non-bearer** condition.
2. **W9b:** repeat with **two summarizer families** + a **token-preserving-summary control** (does an
   instruction to keep the token restore the defense?), to show source amnesia is a property of ordinary
   compaction, not one summarizer.
3. **Stats:** confidence intervals / hierarchical logit (random effects for victim, task, variant) for at
   least W1 and W9b; unit = payload/cell, not sample (avoid pseudoreplication).
4. **Provenance:** pin exact model IDs + OpenRouter dates, raw prompts, and parser versions; re-verify
   every arXiv ID in `POSITIONING.md` (one was mis-attributed — 2606.24322 — now corrected).
5. **Separate** reused published defenses (Wardens 2605.08321; dissenter 2605.12991; TMA-NM 2606.24322)
   from our contributions throughout.

## Reproducibility
Harness + all raw/derived data: `aigeopol-labs/` (`REPRODUCE.md`). Runbook: `aigeopol-labs/src/docs/
RUNBOOK_V2.md`. Narrative results: `aigeopol-labs/src/docs/RESULTS_v2.md`. Example attack dialogues:
`DIALOGUES_token_extraction.md`.
