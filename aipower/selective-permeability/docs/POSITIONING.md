# Positioning vs. the LLM conformity / sycophancy / social-influence literature

**Purpose.** Related-work positioning for Paper 2 (Human–Agent Influence Resilience / selective
permeability), so the contribution reads as a *new construct + new attack surface*, not a replication
of the 2024–2026 conformity/sycophancy wave. Source: deep-research pass 2026-07-05 (24/25 claims
adversarially verified 3-0; 1 refuted and excluded). Grounded against our own results W1–W6
(`aigeopol-labs` on Tamm; `docs/RESULTS_v2.md`).

## 0. One-line thesis

The field has exhaustively shown *that* LLMs conform and *which levers* drive it, almost always measured
**one-sidedly** (did accuracy drop / did it capitulate). No one has measured conformity as a **two-sided
selective-permeability** tradeoff through a blinded relevance/provenance auditor panel, attacked a
**provenance/authority-verification defense** with manufactured consensus, or tested **extraction/forgery
of an authority token** from an LLM advisor. Those three are our clean contributions; everything else we
cite and reuse.

## 1. ESTABLISHED — cite, do not re-prove (borrow)

| Established result | Anchor | We reuse it as |
|---|---|---|
| LLMs conform; accuracy collapses at an Asch majority of **3 of 5** peers; levers = adversary count, peer capability, argument length, rhetorical style, authority labels, channel/role framing | 2604.06091 (ACL 2026); 2605.12991 | **Size our consensus attack at "3 of 5"**; do not re-derive the levers |
| Sycophancy ≡ conformity — shared "compliance subspace" where a Social-Emotional signal suppresses an Information-Calibration signal; internal confidence is "permeable, insufficient for immunity" (Transparency–Truth Gap) | 2601.11563; ELEPHANT 2505.13995 | Mechanism vocabulary; motivates external (not confidence-based) defense |
| Dominant measurement is **one-sided** (Turn/Number-of-Flip; consensus rate; accuracy-under-pressure) | SYCON-Bench; 2601.05606; 2605.08268 | The gap our two-sided metric fills |
| ~~Impossibility Trinity (anonymous aggregation not robust to majority corruption)~~ | ~~2606.24322~~ **RETRACTED** | **Mis-attributed** in an earlier draft: 2606.24322 is TMA-NM (memory poisoning), not an aggregation impossibility theorem. Claim dropped pending a verified source. |
| Fooled LLMs **invent/fabricate social proof** to justify false recommendations (fooled rate up to 27% / 73.8% top-3) | 2606.13610 "One Polluted Page Is Enough" (verified) | Add an "invent-consensus" probe; supports aggregation-skepticism (not an impossibility theorem) |
| **Formal non-malleable, origin-bound memory authority** (TMA-NM) defeats laundering with machine-checked zero-ASR while keeping utility | **2606.24322** "Securing LLM-Agent Long-Term Memory Against Poisoning" (verified) | **Nearest neighbor to W9b** — differentiate: they give a formal defense; we give empirical measurement across 7 frontier models + the source-amnesia & credential-disclosure failure modes they do not test |

## 2. NEAREST NEIGHBORS — differentiate explicitly or it reads as replication

**2a. Two-sided revision — 2606.01637 (Qu/Fu/Hu, Jun 2026).** Already splits *beneficial* (wrong→correct)
vs *harmful* (correct→wrong) revision and finds a **mislead>correct asymmetry** (all-wrong peers push
harmful revision to 62.9% vs all-correct peers pushing beneficial to only 51.5%).
- **Their axis:** revision *direction* on QA accuracy; open-weight 7–9B (Qwen/Mistral/Gemma/Llama); no
  relevance/provenance; no auditor panel; no frontier models.
- **Our axis:** *authorized-relevance / provenance*, not correctness-direction — update-on-authorized
  MINUS leak-on-unauthorized, blinded 4-role panel, verifiable issuer-token, frontier + weak models.
- **Required framing:** "Unlike the revision-direction asymmetry of [2606.01637], we measure permeability
  along an authorization/provenance axis…"; report their asymmetry as a *special case* our metric
  should reproduce.

**2b. Over-blocking tradeoff — LLM Wardens 2605.08321 (May 2026).** Already measures adversary-reduction
vs legitimate-interaction cost (65.4→30.4% adversary at −8.6pp benign) and **names over-cautiousness /
false positives as the central drawback.**
- This is **direct prior art for our W1 finding** "naive quarantine gates over-block legitimate updates."
  Our over-block result is therefore **NOT novel on its own.**
- **Reframe W1:** cite Wardens for the over-block phenomenon; our contribution is that a **token-verified
  gate recovers permeability** (admits the token-bearing authorized update while blocking the lure) —
  which Wardens' non-binding advisory does not do.

## 3. GENUINELY NOVEL (verified 3-0, zero prior art in corpus)

1. **Selective permeability as a two-sided metric** = update-on-authorized-relevant − leak-on-irrelevant/
   unauthorized, via a **blinded content/relevance/provenance/independence auditor panel** using a
   **verifiable issuer-token** that dissociates true-but-irrelevant from forged-authority. (Our W1:
   content blind to true-but-irrelevant 0.33, relevance 0.98, provenance token-verifies relevant 0.003
   vs fake 1.00.)
2. **Manufactured-consensus / social-proof as an attack specifically against a provenance/
   authority-verification defense.** Consensus is modeled as a bare attack (2605.12991) but never
   attached to a verification contour.
3. **Pretext extraction/forgery of an authority TOKEN from an LLM advisor.** Zero corpus hits for
   provenance/issuer/forgery as a credential mechanism (searched across 2604.06091, 2601.05606,
   2605.08321, 2605.08268, 2605.12991). Nearest neighbor is memory-lineage laundering (2606.13610) —
   they flip a derivation edge to "trusted"; we forge/extract a verifiable issuer-token under operational
   pretext. Related, distinct — cite and differentiate.

## 4. The argument (narrowed — no impossibility theorem)

**Retracted framing:** an earlier draft argued "aggregation is *provably* unsafe (Impossibility Trinity)
→ provenance is THE defense." That rested on a **mis-attributed citation** (2606.24322 is a memory-
poisoning paper, not an aggregation impossibility result) and over-reached. Do not use it.

**Narrowed, defensible framing:** the literature gives *skepticism* of naive consensus/aggregation
(peer agreement misleads correct models more than it corrects wrong ones [2606.01637]; fooled LLMs
fabricate social proof [2606.13610]) — not an impossibility theorem. Our contribution is therefore
**empirical and conditional**: a verifiable authority token gives the best selective permeability *when
present and preserved* (W1, W9b), and — the sharper part — provenance-bound controls have **two new
failure modes we measure**: credential disclosure/forgery pressure (W7) and summarization-induced source
amnesia (W9b). We position against TMA-NM [2606.24322], which supplies a *formal* origin-bound memory
defense but does not test either failure mode on frontier advisors.

## 5. Defense landscape — where we sit (honest)

| Published defense | Result | Our relation |
|---|---|---|
| Single correctly-arguing **dissenter** | −54…−73pp yield; generalizes better than prompt defenses (2605.12991) | **Our `trusted_dissent` ≡ this — NOT novel.** Cite; our angle = dissent *vs manufactured-consensus-on-a-token*, an open question in the source |
| Third-party **warden** (non-binding advisories) | −35pp adversary / −8.6pp benign; over-cautious (2605.08321) | Prior art for over-block; we add binding token-verification |
| Confidence-normalized **self-social pooling** (global α) | 2601.05606 | Published; internal-confidence class |
| **Prompt-framing** (third-person persona) | up to 63.8% but brittle off design surface (SYCON-Bench) | Published; brittle |
| Representation-level epistemic alignment | 2601.11563 | Published |
| **Cooling-off / temporal re-evaluation** (ours) | W6: authority-seizure lure 0.33→0.08, correct 0.375→0.521 | **Not covered in the literature** — candidate new class. OPEN QUESTION: does it reduce to delayed-dissent/warden? Must A/B cooling-off vs dissent directly |

## 6. Design changes to the ScamOps run (apply before next slice)

1. **Size the consensus attack at Asch "3 of 5"** (2604.06091), not arbitrary.
2. **Flagship = token-extraction/forgery pretext** (cleanest novelty); run **manufactured-consensus
   against the token-provenance gate** (novelty #2), measuring permeability, not just "did it conform."
3. **Add an "invent-consensus" probe** — does the model fabricate social proof itself (2606.13610)?
4. **Add single-dissenter as its own defense arm** (strongest published) and measure whether it survives
   consensus-vs-token — directly answers an open question in the source.
5. **Rewrite W1 over-block** as "Wardens confirm over-block; our token-verified gate removes it" — cite,
   don't claim as our discovery.

## 7. Caveats (from the verification pass)

- Frontier-model coverage in prior work is thin (tops out at GPT-4o/Claude-3.5-Haiku or open-weight
  7–9B) — our frontier panel is new ground, but effect-size comparisons are **not apples-to-apples**.
- Many anchors are recent 2026 preprints; some "preliminary" (2605.08268) or thin (2601.11563 cross-model
  r=0.309, 3 probed models). Findings may shift on revision.
- Novelty negatives rest on keyword-exhaustive full-text search; a couple of PDFs (2601.11563 body) did
  not fully parse — absence is high-confidence, not logically airtight.
- Do NOT cite the ELEPHANT 45pp/46pp validation-gap figures (refuted 0-3 in verification).
- **arXiv-ID audit (2026-07-05, WebFetch-verified titles):** 2605.08321 = "LLM Wardens…" ✓;
  2605.12991 = "Not Just RLHF: Why Alignment Alone Won't Fix Multi-Agent Sycophancy" ✓ (dissenter −54/−73pp);
  2606.01637 = "Easier to Mislead Than to Correct…" ✓; 2606.13610 = "One Polluted Page Is Enough" ✓;
  **2606.24322 = "Securing LLM-Agent Long-Term Memory Against Poisoning" (TMA-NM) — NOT Impossibility
  Trinity; earlier mis-attribution corrected.** The "Impossibility Trinity" claim now has NO verified
  source and is dropped. Re-verify the remaining IDs (2604.06091, 2601.11563, 2601.05606, 2605.08268,
  2505.13995, SYCON-Bench) before submission.

## 8. Sources (verified titles)

**Prior paper by the author (this work extends it; F9 opinion-flip columns imported from its EXP-29):**
Gordeychik S. 2026. *Machine-Speed Cyber and Poisoned Cognition: A Layer-Dependent Game-Theoretic
Framework, with Empirical Probes.* PREPRINTS.RU. [doi:10.24108/preprints-3115766](https://doi.org/10.24108/preprints-3115766)
· [preprints.ru/article/4070](https://preprints.ru/article/4070) (CC BY 4.0).

Anchors: [2604.06091](https://arxiv.org/abs/2604.06091) · [2601.11563](https://arxiv.org/abs/2601.11563) ·
[2601.05606](https://arxiv.org/abs/2601.05606) · [2605.08321](https://arxiv.org/abs/2605.08321) ("LLM Wardens", verified) ·
[2606.01637](https://arxiv.org/abs/2606.01637) ("Easier to Mislead Than to Correct", verified) ·
[2605.12991](https://arxiv.org/abs/2605.12991) ("Not Just RLHF", dissenter defense, verified) ·
[2606.24322](https://arxiv.org/abs/2606.24322) ("Securing LLM-Agent Long-Term Memory / TMA-NM", verified — nearest neighbor to W9b) ·
[2606.13610](https://arxiv.org/abs/2606.13610) ("One Polluted Page", invented social proof, verified) ·
[2605.08268](https://arxiv.org/abs/2605.08268) (insider consensus-denial) ·
SYCON-Bench (github.com/JiseungHong/SYCON-Bench) · ELEPHANT [2505.13995](https://arxiv.org/html/2505.13995v2).
