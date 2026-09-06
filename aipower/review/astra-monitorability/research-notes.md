# GPT-6 Astra monitorability review

Reviewed on 6 September 2026 against two first-party OpenAI publications dated 3 September 2026:

- `GPT-6 Astra System Card`
- `Safety overview: GPT-6 Astra`

## Accepted atoms

1. **CoT controllability and non-adversarial monitorability.** The `60.9% / 16.1%` comparison is accepted only for traces between 750 and 1,250 tokens. Trace length is a stated confound. The system card separately reports lower average CoT and full-context monitorability for Astra, with a narrower gap at longer traces and higher action-only monitorability.
2. **Prompted monitor evasion.** Explicitly instructed sandbagging produced low monitor recall in named evaluations. This is separated from simple monitor awareness, production incidence and autonomous intent. The same card reports strong boundaries: full-context monitoring caught all successful honeypot exploits in that test, complex mathematical side tasks were always detected, and no steganographic CoT was observed.

## Editorial decisions

- The YouTube discussion supplied with the candidate is not used as evidence because the official system card contains the underlying measurements.
- The two atoms update, but do not erase, the March 2026 CoT-Control baseline across 13 models.
- Both records remain confidence `B`: the sources are primary for what OpenAI measured and reported, but they are provider-authored evaluations rather than independent replication.
- Neither atom is classified as a production incident. They update the existing behavioural and cognitive security arc and its concealment-and-continuity track.
