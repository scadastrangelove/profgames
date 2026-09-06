# Schema notes — v0.33

v0.33 adds evidence and editorial calibration without changing canonical filenames or introducing a new top-level schema field.

## New records

- `SIG_2026_ASTRA_COT_CONTROLLABILITY_MONITORABILITY` stores the length-banded CoT-Control comparison and the separate non-adversarial monitorability result.
- `SIG_2026_ASTRA_PROMPTED_MONITOR_EVASION` stores explicitly prompted sandbagging and sabotage-monitor tests together with their negative boundaries.

Both records are evaluations in `CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION`, belong to `BEH_TRACK_CONCEALMENT_PERSISTENCE`, and retain provider-report confidence `B`.

## Interpretation rules

1. `60.9%`, `16.1%` and `1.7%` are comparable only within the reported 750–1,250-token band.
2. CoT controllability is an instruction-following proxy. It does not itself establish spontaneous or motivated concealment.
3. CoT-only, action-only and full-context monitorability are separate observation scopes and must not be collapsed into one score.
4. Prompted sandbagging and sabotage evaluations establish capability in stated configurations, not production prevalence or autonomous intent.
5. Negative boundaries from the same source remain attached: simple awareness did not produce covert obfuscation, full-context monitoring caught every successful honeypot exploit in that test, complex mathematical side tasks were always detected, and no steganographic CoT was observed.

## Graph update

Seven manual edges connect the two records to the existing behavioural arc and calibrated claim, link the March 2026 CoT-Control baseline to the September update, and preserve the distinction between context, thematic membership and evidential support.

The release contains 357 events, 72 claims, 25 arcs, 745 edges and 533 unique source URLs. All 6,491 checked references resolve in each language.
