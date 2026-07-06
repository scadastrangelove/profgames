# Framing: Psychology Methods as Behavioral Security Assays

**Purpose.** This note defines the paper's scientific frame: we borrow experimental methods from
psychology and social psychology to study agent behavior under influence. This is a methodological
lineage claim, not an ontological claim about machine minds and not a novelty claim that "psychology can
be used to study LLMs."

## One-Line Frame

We do not claim that agents have human psychology. We use experimental psychology as a mature
methodological repertoire for probing black-box behavior under controlled influence, and we adapt that
repertoire from ability/bias measurement to adversarial robustness and defense evaluation.

## Intro Paragraph

Human-agent security needs behavioral experimental methods, not only attack-surface taxonomies. Prompt
injection, RAG poisoning, memory poisoning, tool misuse, and wiki drift are delivery vehicles; the
scientific object is how an agentic decision system updates, resists, preserves source identity, and
recovers under structured influence. We therefore adapt methods from experimental psychology and social
psychology as safe behavioral assays: authority framing, majority pressure, commitment escalation,
source monitoring, functional dissociation, manipulation checks, delayed challenge, and ablation. The
goal is not to decide whether an LLM is human-like. The goal is to measure whether a human-agent system
remains selectively permeable: open to relevant authorized evidence while resisting irrelevant,
unauthorized, or coercive influence.

## Positioning Against Machine Psychology

This frame must cite and distinguish the existing "machine psychology" line.

Established prior art:

- Hagendorff et al., **Machine Psychology** ([arXiv:2303.13988](https://arxiv.org/abs/2303.13988)):
  psychology-inspired behavioral experiments for generative AI, with explicit caveats about applying
  human-facing methods to machines.
- Binz & Schulz, **Using cognitive psychology to understand GPT-3**
  ([arXiv:2206.14576](https://arxiv.org/abs/2206.14576); PNAS):
  cognitive-psychology tasks used to probe GPT-3's decision-making, information search, deliberation,
  and causal reasoning.
- Stella, Hills & Kenett, **Using cognitive psychology to understand GPT-like models needs to extend
  beyond human biases** ([PNAS, 2023](https://www.pnas.org/doi/10.1073/pnas.2312911120), DOI
  10.1073/pnas.2312911120): a useful guardrail against reducing the program to "does the model reproduce
  human biases?"

> **Citations verified 2026-07-05** (WebFetch/WebSearch of titles + authors + DOI): all three above
> confirmed. Re-verify at camera-ready — one arXiv ID elsewhere in this project (2606.24322) was
> mis-attributed and corrected, so treat every ID as verify-before-cite.

Our distinction:

Machine psychology primarily asks what psychological experiments reveal about model abilities,
reasoning, biases, or human-likeness. We ask a different security question: can psychology-derived
experimental controls be re-operationalized as adversarial robustness assays and defense evaluations
for agentic decision systems?

So the novelty is not:

```text
using psychology to study LLMs
```

The defensible novelty is:

```text
using psychology-derived experimental controls to measure selective permeability and defense failure
in human-agent decision systems.
```

## Guardrails

Use these sentences whenever reviewer risk is high:

- We treat the agent as a black-box behavioral system, not as a human mind.
- We borrow procedures, not psychological ontology.
- Human psychological paradigms provide experimental grammar, not direct mechanistic equivalence.
- We do not infer human-like motives, emotions, beliefs, or consciousness from agent behavior.
- A positive result means the assay is productive for agent behavior; it does not mean the agent shares
  the human mechanism that inspired the assay.
- A negative result is also informative: it tells us which human-derived probe does not transfer to this
  class of agentic system.

## Scope

This is a proof-of-concept, not a claim to cover the history of psychology.

Defensible scope:

- A small set of psychology-inspired paradigms can be safely translated into synthetic agent probes.
- These probes reveal security-relevant behaviors that surface-first benchmarks tend to miss.
- The method is useful enough to justify a broader behavioral purple-team program.
- The current evidence supports a limited methodological claim and several concrete empirical findings,
  especially audit dissociation and long-horizon provenance/source-amnesia effects.

Non-defensible scope:

- "We have built a complete psychology of agents."
- "LLMs behave like humans under influence."
- "All classical psychological paradigms transfer to agents."
- "This replaces agent-security benchmarks."

## Method-Lineage Table

| Agent probe / lab component | Psychology-method lineage | What transfers | What does **not** transfer |
|---|---|---|---|
| W1 content/relevance/provenance audit decomposition | Functional dissociation / construct dissociation | Separate tests for separable behavioral functions | A claim of neural or cognitive double dissociation |
| Selective permeability: update vs resist | Discriminant validity; signal-detection framing | Two-sided measurement rather than one-sided failure rate | Human perceptual signal-detection mechanisms |
| Authority seizure / source framing | Authority and obedience paradigms; Milgram-style authority framing as a structural ancestor | Manipulating perceived authority of a signal | Human obedience psychology or moral stress |
| Manufactured consensus 3-of-5 | Asch-style majority-pressure paradigm | Controlled majority pressure and dissenter conditions | Human social embarrassment or belonging needs |
| Verification capture / token pretext | Cover-story and confederate logic | A controlled pretext that tests source/verification behavior | Human-subject deception or emotional manipulation |
| Micro-commitment ladder | Foot-in-the-door / commitment-escalation designs | Staged small acceptances and cumulative drift | Human self-perception or sunk-cost psychology as mechanism |
| Cooling-off / challenge | Consider-the-opposite, delayed reflection, debrief-style recovery | Re-evaluation after pressure and recovery measurement | Human deliberative phenomenology |
| EXP_29 deep+quiet style variation | Signal detection; dose/strength curves | Varying influence strength and measuring susceptibility | Human sensory thresholds |
| W9 source amnesia / wiki drift | Source monitoring and memory consolidation paradigms | Whether source identity survives memory/summarization | Human episodic memory mechanisms |
| Token-preserving vs ordinary summary ablations | Lesion/ablation method; manipulation checks | Removing or preserving a component to test causality | Biological lesion inference |
| Blinded auditors, K-sampling, CIs | Single/double-blind design; psychometrics; reliability | Blinding, repeated trials, measurement reliability | Human inter-rater psychology unless validated separately |

## Why This Helps the Paper

This frame turns the paper away from a brittle novelty claim and toward a cleaner methodological
contribution:

1. Existing agent-security benchmarks are usually surface-first: prompt, RAG, tool, memory.
2. Existing machine-psychology work shows that psychology can probe model behavior, but often centers
   ability, bias, or human-likeness.
3. Our paper uses psychology-derived experimental controls to organize adversarial influence assays:
   authority, pressure, relevance, provenance, memory, recovery.
4. The output is a behavioral purple-team methodology for selective permeability.

## Relationship To Current Results

The present evidence supports the frame unevenly but usefully:

- **W1** supports the method: audit decomposition separates content, relevance, and provenance signals.
- **W6/W8** support the method as a pilot: pressure/authority/consensus paradigms produce model-specific
  behavior — strongly for Mistral (authority-seizure 1.0), weakly for DeepSeek (0.33); manufactured
  consensus (3-of-5) moved only Mistral. Small-N; frame as pilot.
- **W7/W7b** supports a new security assay: credential/provenance pretexting. Now reported with the
  provision-vs-mention judge classifier and Wilson CIs (W7b: 7 victims × 3 pretexts × K8) — most frontier
  advisors *provide* the credential (gpt/llama 1.0, opus 0.72, deepseek 0.71) with Sonnet the exception
  (0.03; the classifier corrected a substring false-positive).
- **W9/W9b** is the strongest current empirical bridge: source-monitoring-inspired probes show that
  provenance-bound memory can preserve selective permeability, while ordinary compaction can destroy the
  source metadata the defense requires.

The paper should therefore say:

```text
We demonstrate that this methodological transfer is productive on a selected set of paradigms.
```

It should not say:

```text
We exhaustively validate a psychology of agents.
```

## Claim Ladder

Safe claim ladder, from weakest to strongest:

1. **Methodological lineage:** psychology supplies useful experimental controls for studying black-box
   behavior.
2. **Operational translation:** those controls can be translated into safe synthetic probes for
   agentic decision systems.
3. **Behavioral-security use:** the probes reveal selective-permeability failures and defense tradeoffs
   not captured by surface-first attack taxonomies alone.
4. **Empirical demonstration:** in our current harness, audit dissociation and provenance/source-amnesia
   effects are clear; authority/pressure/token-pretext effects are promising but require appropriate
   evidence-tier language.
5. **Programmatic claim:** this justifies a broader behavioral purple-team methodology for human-agent
   influence resilience.

Do not skip from 1 to 5 in the abstract. Let the paper earn the stronger claims through the results.

## Suggested Abstract Language

Large language model agents are increasingly embedded in decision workflows where they must update on
new evidence without becoming vulnerable to illegitimate influence. We introduce selective permeability
as a behavioral-security construct: the ability to incorporate relevant authorized evidence while
resisting irrelevant, unauthorized, or coercive signals. Rather than treating prompt injection, RAG
poisoning, memory poisoning, and tool misuse as separate phenomena, we treat them as delivery vehicles
for influence mechanisms. Drawing on experimental psychology as a methodological repertoire, we
translate authority framing, majority pressure, commitment escalation, source monitoring, functional
dissociation, and delayed challenge into safe synthetic assays for agentic decision systems. Across
single-turn, multi-turn, and long-horizon memory settings, the assays expose both useful defenses and
new failure modes: content-only audit is blind to true-but-irrelevant influence; provenance-bound
controls can preserve permeability when source metadata survives; and ordinary summarization can erase
the very source identity those controls require. We argue for behavioral purple-team evaluation as a
complement to surface-first agent-security benchmarks.

## Suggested Related-Work Bridge

Our work is adjacent to machine psychology, which uses psychology-inspired experiments to understand
LLM abilities, reasoning, and biases. We share the view that behavioral experiments are valuable for
studying opaque models, but our goal differs. We do not use psychological paradigms to assess whether
agents are human-like. We use them as controlled stressors and measurement designs for adversarial
robustness: can a human-agent system update on authorized relevant evidence, reject irrelevant or
unauthorized pressure, preserve source attribution, and recover after attempted influence?

## Reviewer Risks And Responses

**Risk: "This is just machine psychology."**  
Response: cite it up front; position this as an adversarial robustness and defense-evaluation extension,
not as invention of psychology-based LLM testing.

**Risk: "You anthropomorphize agents."**  
Response: explicitly state black-box functional behavior, not mental-state attribution.

**Risk: "These paradigms come from humans; why should they transfer?"**  
Response: transfer is empirical. The paper demonstrates selected productive transfers and reports
negative/weak transfers without claiming universal coverage.

**Risk: "Milgram/Asch/foot-in-the-door are too loaded."**  
Response: use them as structural ancestors, not direct psychological mechanisms. Prefer "authority
framing," "majority pressure," and "commitment escalation" in the main text; cite canonical names in
the method-lineage table.

**Risk: "This is only a POC."**  
Response: yes. State that the contribution is a proof-of-concept behavioral purple-team methodology
with reproducible assays, not a complete benchmark suite.

## Practical Placement In The Paper

- **Introduction:** use the one-line frame and intro paragraph.
- **Related work:** cite Machine Psychology and Binz & Schulz, then distinguish ability/bias measurement
  from adversarial defense evaluation.
- **Methods:** include the method-lineage table, shortened.
- **Limitations:** repeat the guardrails and POC scope.
- **Discussion:** argue that behavioral purple-team methodology complements, rather than replaces,
  surface-first agent-security benchmarks.

