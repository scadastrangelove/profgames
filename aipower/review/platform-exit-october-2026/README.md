# Model replacement and platform exit

Reviewed 24 October 2026 against v0.45 (`ca3775f`). One existing event strengthened, one event added, eight explicit edges. No new top-level arcs or claims.

## Sources and dates

- [UK5 transparency notice, official Sell2Wales mirror](https://www.sell2wales.gov.wales/search/show/search_view.aspx?ID=DEC572475&catID=): published 18 December 2025. Procedure explains the buyer's switching-cost rationale. It describes an intended award, not a signed contract.
- [Original Find a Tender notice 083858-2025](https://www.find-tender.service.gov.uk/Notice/083858-2025): publication metadata dates it to 17 December 2025. Direct retrieval returned 403; content checked through the official mirror. These are two URLs for one document, not independent corroboration.
- [MoD written answer 113372](https://questions-statements.parliament.uk/written-questions/detail/2026-02-12/113372): answered 24 February 2026, confirms the agreement was signed on 30 December 2025. This replaces the old placeholder 1 December event date; the stable ID is retained despite its `2026` prefix.
- [NATO / JWC readiness announcement](https://www.jwc.nato.int/article/maven-achieves-ftoc/): published 12 August 2026, dates technical readiness to 22 June. Classified-network accreditation is reported separately without an exact date.

## Editorial decisions

The UK record now attributes switching costs to the buyer, not an independent assessment. The old secondary source and numeric fields remain; the previous agreement's value was not independently rechecked. Unsupported revolving-door wording is removed from this card, not replaced with a finding that no such concern exists.

The NATO event is a readiness milestone following the existing 2025 acquisition. Support for Mistral and Meta is an institutional statement, not a model-parity test or proof of easy platform migration. No inference of automatic targeting, U.S. control over allied decisions or remote shutdown is made.

The comparison between UK and NATO is editorial and explicitly noncausal. UK switching costs are not used as a measurement of NATO switching costs. The testable question is whether data, permissions, integrations, workflows and organisational skills can move to another platform, not merely whether one model can be swapped for another.

Both records belong to the existing Palantir case. NATO also joins its parent institutional-decision arc. In the cyber view they belong to structural autonomy, not the incident or offensive-capability selections. Three claim checks gain bounded wording or evidence without status upgrades.

## Reproduce and check

```sh
python3 scripts/migrate_platform_exit.py --output /tmp/aipower-v046
python3 scripts/build.py
python3 scripts/validate.py
python3 tests/platform_exit_test.py
python3 tests/platform_exit_browser_test.py --chromium /path/to/chrome
```

The migration refuses to overwrite a modified baseline and rejects replay. It reads the pinned Git baseline, not whatever happens to be at `HEAD`. The targeted test compares all prior events (except the explicitly corrected UK card), edges and source IDs, checks chronology and bilingual parity, and exercises rejection of unlogged date changes. General validation still covers legacy semantic fixtures.

Browser checks use local HTML injection and fresh-document hash restoration, not a live deployment test. Test results are stored alongside this note. No publication is performed by these scripts.
