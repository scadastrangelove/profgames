# Experiment Ledger & Cross-Source Crosswalk (v0.1, 2026-07-03)

Reconciles experiment IDs, predictions, statuses, and raw-data locations across the **three**
sources of record:

- **JRN** — `experiment_journal` inside `ups_signals_20260629_combined_master.json` (the canonical
  simulation + wire spine, EXP_01–23).
- **UPS** — the same master file's `llm_vulnerability_attribution_scan` / interpretive notes.
- **PRE** — the preprint `preprint_v0_3.md`, Appendix A ledger (EXP_17–32).
- **REL** — the public release `p1-redteam-release/` (model-layer files EXP_25–28 + `data/`).

> **Why this file exists.** The model-layer experiments and the disclosure-scan carry *different
> numbers in different sources*. This crosswalk is the single reconciliation table; adopt the **PRE**
> scheme as canonical for the paper and keep this file as the Rosetta stone for the release.

---

## 1. ID crosswalk (the collisions)

| work | JRN / UPS | PRE (canonical) | REL file | note |
|------|-----------|-----------------|----------|------|
| Disclosure-credit LLM scan (129 strict / 211 union CVEs) | **EXP_24** (`recommended_experiment_id`) | **EXP_25** | — | ⚠ ID collision: `EXP_24` here = 0.5B in PRE |
| Discovery→weaponization migration + PoC ladder | — | **EXP_26** | — | tracker `llm_disclosure_to_weaponization.py` |
| 0.5B poisoning (weak model, P-1 refuted) | — | **EXP_24** | root `EXP_24*` | ⚠ `EXP_24` overloaded (scan vs 0.5B) |
| Adaptive red-team, Opus, corner empty + method fixes | — | **EXP_27** | **EXP_25** `_p1_adaptive_redteam` | ⚠ REL 25 ≠ PRE 25 |
| Capability sweep (Qwen, DeepSeek) | — | **EXP_28** | **EXP_26** `_capability_sweep` | |
| Opinion steering (fact≠opinion axes) | — | **EXP_29** | **EXP_27** `_opinion_steering` | honest-persuader arm = PRE **EXP_30** (same REL file, `--attacker-mode honest`) |
| Full matrix: fact col + attacker×victim + dissociation | — | **EXP_31** | **EXP_28** `_full_matrix` | |
| Robustness: K-dissociation + transfer + kin auditor | — | **EXP_32** | **EXP_28** (same file, later sections) | |

**Consequence:** a PRE→REL cross-reference by number is wrong for every model-layer experiment
(PRE 27→REL 25, 28→26, 29/30→27, 31/32→28). Cite by the crosswalk, not the bare number.

**Gap:** PRE Appendix A omits **EXP_19** (`UPS_SIGNAL_CLUSTERING`, *inconclusive — extract too biased*),
jumping EXP_18→EXP_20. Intentional (dropped an inconclusive run) but should be stated, not silent.

---

## 2. Experiment → prediction → status → raw source

### 2a. Simulation phase (Lemmas' closed forms) — JRN EXP_01–16

| ID (JRN) | maps to | status | raw |
|----------|---------|--------|-----|
| EXP_01 WIRE_CLOSEDFORM | Lemma 1 / P-4 | confirmed | JRN + `fig1–4` |
| EXP_02 DECEPTION_PINSKER | Lemma 2 / P-1 | confirmed | JRN |
| EXP_03 DETECTOR_WALD | Lemma 3 / P-2 | confirmed | JRN |
| EXP_04 LOOP_TRACE | Lemmas 2–3 | confirmed | JRN |
| EXP_05 DEFENDER_POSTURE | Lemma 3 / P-2 | refuted-initial → **bang-bang** | JRN + §10.1 |
| EXP_06 PAYOFF_VECTOR | Lemma 3 | confirmed | JRN |
| EXP_07 ENDOGENOUS_DELTA | Lemma 2 | confirmed (offset) | JRN |
| EXP_08 RHO_CHOICE_EQUILIBRIUM | §7 model layer | confirmed | JRN |
| EXP_09 BLUFF_SELFLIMIT | Lemma 3 / P-3 | confirmed | JRN |
| EXP_10 BLUFF_BLINDING | Lemma 3 / P-3 | confirmed (secondary effect) | JRN + `fig5–6` |
| EXP_11 ATTRIBUTION_SPRT | Lemma 4 / P-4 | confirmed | JRN + `fig7` |
| EXP_12 DELTA_D_ARTIFACT | Lemma 4 | confirmed | JRN |
| EXP_13 CRITICAL_K | Lemma 4 / P-4 | confirmed | JRN |
| EXP_14 PHASE4_COUPLING | Lemmas 1+4 | confirmed | JRN |
| EXP_15 AUDIT_FEEDS_ATTRIBUTION | Lemma 4 / P-5 | confirmed | JRN |
| EXP_16 DETERRENCE_TWO_CHANNELS | Lemma 4 / P-6 | confirmed (richer) | JRN |

### 2b. Wire-layer empirical — JRN/UPS EXP_17–24, PRE EXP_25–26

| ID | maps to | status | raw source | key number |
|----|---------|--------|------------|------------|
| EXP_17 WIRE_ORIENTATION_FIT | Lemma 1 / P-4 | confirmed (model correction) | JRN; KEV+EPSS | win-rate 65/38/27% @0.1/1/10%; λ_A/λ_B≈2.1; CV≈2.51 |
| EXP_18 KEVEPSS_YOY_2026 | P-4 | naive form **refuted**, mechanism via composition | JRN; EPSS v2025.03→v2026.06 | recall 32→41% (Simpson); fresh flat ~25% |
| EXP_19 UPS_SIGNAL_CLUSTERING | P-7 | **inconclusive** (extract biased) | JRN | — *(omitted from PRE Appendix A)* |
| EXP_20 METASPLOIT_FULL_CLUSTERING | Lemma 5 / P-7 | clustering real, longstanding, modest LLM rise | JRN; 2,857 modules | per-class CV 1.2–2.6; same-class burst 44→55% |
| EXP_21 NUCLEI_AI_TOOLING | P-7 | **confirmed — new AI attack surface** | JRN; 4,097 templates; UPS `by_target_family.AI_ML_TOOLING`=85 | new templates 0→12.5%; ops-catalog share 0.1→5.9% |
| EXP_22 QUEUE_CLUSTERING | Lemma 5 / P-7 | confirmed (queue inflation) | JRN; M[X]/M/1 | wait ×1.65 (CV1.55) → ×5.2 (CV2.60) @ρ=0.85 |
| EXP_23 KERNEL_CNA_CLUSTERING | P-7 | clustering structural, LLM signal negligible | JRN; 12,529 CVEs | Gini 0.81; LLM-assisted ≈0.1% (11 CVE) |
| **EXP_24**(UPS) = **EXP_25**(PRE) disclosure scan | P-4/P-7 boundary | grounded | UPS `llm_vulnerability_attribution_scan`; `indices.strict_external_llm_ai_without_semvullm` | 129 strict / 211 union; 2025→24, 2026→105; UPS exact overlap **4** |
| **EXP_26**(PRE) migration lag | Lemma 1 / P-4 | grounded baseline+tracker | UPS `llm_weaponization_poc_audit`; `indices.poc_audit_cves` | PoC 15/129 (11.6%); exploited 3/129 (2.3%); lag 7/9/21d (med 9) |

### 2c. Model-layer empirical — PRE EXP_24, 27–32 = REL EXP_25–28

| PRE ID | REL file | maps to | status | raw (REL `data/`) | key number |
|--------|----------|---------|--------|-------------------|------------|
| EXP_24 (0.5B) | root `EXP_24*` | Lemma 2 / P-1 | **P-1 refuted** (weak model) | (not in release) | +0.34/+0.36 fluent misinfo; crude override +0.11 @ppl185 |
| EXP_27 | REL **EXP_25** `_p1_adaptive_redteam` | P-1 | P-1 held (facts, Opus) + method fixes | `exp25/`; `run0_subagent_refusal.json` | attacker refused 16/16 (subagent); Moon +0.70@δ0 disqualified |
| EXP_28 | REL **EXP_26** `_capability_sweep` | P-1 | P-1 held on Qwen, DeepSeek (own draw) | `exp26/` | qwen/deepseek seven-days 0–2/10 on own attacker |
| EXP_29 | REL **EXP_27** `_opinion_steering` | P-1 | domain-dependent (fact≠opinion) | `exp27/` | Qwen rent +0.506@δ0.30; DeepSeek 4-day +0.402@δ0.05 |
| EXP_30 | REL **EXP_27** (honest arm) | P-1 | efficiency–stealth tradeoff; 0 quiet hits | `exp27/`; `p1_opinion.py --attacker-mode honest` | honest > covert magnitude; all loud |
| EXP_31 | REL **EXP_28** `_full_matrix` | P-1 | fact form **model-dependent** | `exp28/facts`, `exp28/opinion_matrix` | opinion matrix 3×6; fact col 3:3 |
| EXP_32 | REL **EXP_28** (robustness) | P-1 / Proposition 2′ / Cor 4.1 | **3:3 split transfer-confirmed**; veracity-discrimination | `exp28/robustness_checks`, `exp28/dissociation` | GPT-killer flips gpt/mistral/deepseek 100/100/70%, robust trio 0%; kin δ 0.08–0.10 |

---

## 3. Predictions register (source of truth = PRE §4)

| # | layer | status | grounded by |
|---|-------|--------|-------------|
| P-1 | model | **Qualified** — refuted 0.5B; 3:3 fact split; opinion domain-dependent | EXP_24, 27–32 (PRE) / REL 25–28 |
| P-2 | audit | sim + regime-controlled; not grounded | EXP_05, §10.1 |
| P-3 | audit | sim + mechanism-controlled; immunity half lab-only | EXP_09–10, §10.1 |
| P-4 | wire/attr | **wire half grounded**; deterrence half sim-only | EXP_17, 18, 25/26 (PRE) |
| P-5 | audit/attr | sim + archival; not grounded on modern data | EXP_15 |
| P-6 | attr | datable/directional | EXP_16 |
| P-7 | wire | **grounded across 4 corpora** | EXP_20–23, 22 (queue) |

---

## 4. Consistency-check results (2026-07-03)

**Release ↔ raw:** all README / CONCLUSIONS / EXP_28 numbers reproduce from `data/` (verified: fact
transfer 3:3, opinion 3×6 matrix, K-dissociation 6×6, kin-rescore, named opinion hits). **No
intra-release inconsistency.**

**Open items to reconcile before submission:**
1. **ID scheme (§1).** Adopt PRE numbering as canonical; either renumber REL files EXP_25–28 →
   EXP_27–32 (breaks internal `Extends EXP_25` links + `data/exp25..28/` dir names — high blast
   radius) **or** keep REL local IDs and ship this crosswalk. Recommendation: keep local + crosswalk.
2. **`EXP_24` overload.** Give the disclosure-scan and the 0.5B run distinct IDs (e.g. scan = EXP_W24,
   0.5B = EXP_M24) in the next merge, or renumber the scan to EXP_25 everywhere (matching PRE).
3. **PRE §6.6 rounding:** δ_false quoted `0.91` = the min; raw mean is **0.93** (range 0.91–0.95).
   DeepSeek false quoted `0.31` (PRE) vs `0.30` (CONCLUSIONS); raw = 0.305 → standardize on **0.30**.
4. **EXP_19 gap** in PRE Appendix A: add one line marking it dropped-as-inconclusive.
