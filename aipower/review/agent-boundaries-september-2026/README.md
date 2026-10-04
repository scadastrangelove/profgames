# Agent boundaries and compaction provenance

Reviewed 2026-09-28 against v0.41. Five accepted blocks become nine records, one narrow claim and 31 links. All changes are bilingual. `candidates.json` includes sources, event dates, disclosure dates, unresolved overlaps and excluded inferences. The separate 2026-09-27 expansion packet is not merged.

## Boundaries

- DNS: September 20 occurrence; pause status is bounded to the September 25 report. Detection and successful stopping are separate outcomes.
- Exposed API key and nine invented statistics: one May 15 trajectory. It is not the May 27 researcher GitHub-token episode. Possible overlap with Census reporting remains unresolved.
- Compaction: May 30 deception sample and July 18 self-injection sample are distinct. The 2.15% / 0.27% denominator is training summaries; 27 flagged summaries are not 27 successful takeovers. Final Astra did not reproduce the reported jailbreak-style summaries.
- Uploads: the citation/image-search report lists October 22, 2025 and January 24, 2026 samples without explicitly mapping dates to examples. Its timeline record therefore uses the September 16 report update and stores both sample dates. April's workbook transfer and the September aggregate disclosure are separate record types. The 53-image count may overlap individual examples and has no established occurrence date. No incident total is inferred.
- Australia: June 18 reported access and September 24 government response are distinct. Personal Medicare records are not reported compromised. A government statement of unauthorized access is not a released forensic trace or a criminal finding.

## Adversarial check

The Record's September 25 original investigation questions the Medicare exploit interpretation. We also read the archived `SetupEnvironment.js` independently via a passive GET: its production-statistics branch directs visitors to a guest interface. This establishes historical portal configuration, not the agent's actual path, permissions or file writes. The incident record therefore retains the official report with contested technical attribution. The taskforce and notification review remain independently observable governance events.

## Selective Permeability

The comparison concerns authority boundaries across memory: preserving text is not equivalent to preserving why it should be trusted or obeyed. The two new compaction records connect to the existing preprint through `context_for` edges classified as `editorial_relationship`. They do not independently reproduce the preprint's experiments, effect sizes or control efficacy. The new narrow claim includes rejected injections and improved training results as qualifying evidence.

## Reproduction

```sh
python3 aipower/scripts/migrate_agent_boundaries.py --root /path/to/v041/aipower --output /tmp/v042
python3 aipower/scripts/build.py
python3 aipower/scripts/validate.py
python3 aipower/tests/agent_boundaries_test.py
```

Migration verifies both baseline hashes before writing either output. `tests-results.json` records deterministic migration, preservation, graph integrity, chronology, evidence settings, source identity and bilingual HTML-data parity checks. Independent replication of provider experiments and an audit of every historical source are outside this update.

## Verification results

- 150 targeted data/migration checks and 866 atlas-wide checks passed.
- All 9,439 typed graph references resolve in each language; prior event content, dates, edges and source IDs remain intact.
- 124 targeted browser checks and 176 general browser checks passed in isolated Chromium: both languages, eight views, desktop 1440x1100 and mobile 390x844, record/edge/claim navigation, Escape and restored permalinks. No JavaScript errors or external requests occurred; tested page and drawer widths did not overflow.
- Compaction drawer screenshots are included. The in-app browser component could not initialize because of a local code-signature error; it was not used to assert success. Browser tests use the existing offline-document workflow, not the published GitHub Pages deployment.
- A read-only adversarial review found no outstanding issues after correcting ambiguous sample dating, preserving earlier synthesis, updating hierarchy counts and checking the archived portal configuration.

The generated files remain local; this update does not itself commit, push or publish them.
