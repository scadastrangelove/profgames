# Judicial Power / Судебная власть: 17 ноября 2026

Nine events, 25 edges and ten primary URLs extend existing arcs. The court lens contains twelve canonical records, including the existing Bartz ruling and two Amazon/Perplexity records. No claim or arc is added.

## Evidence Boundaries

- California, Arkansas and the nonprofit coalition: confirmed filings and requested relief, not established wrongdoing or granted injunctions. The California complaint's 80 loss-of-control episodes are not 80 independently proven intrusions. Arkansas predates California's cyber-focused suit.
- Google: the December 2025 final district-court judgment and September 2026 implementation report are distinct. Qualified Competitor admission is conditional. Ordered access is not proof that all data have been delivered.
- Anthropic: section 3252 and section 4713 are different statutory proceedings. The August result is verified through the subsequent official appellate opinion; the September result does not reverse it.
- GEMA: first-instance ruling on specific lyrics, not a final EU-wide training prohibition. Getty: a bounded secondary-copyright holding, not blanket training permission. Appeal papers represent a party, not a new ruling. Their exact first-publication day is unknown.
- Existing Bartz: historical June 2025 fair-use ruling; this packet is not a full update of its settlement history.

## Data Contract

`legal_topics` is an explicitly reviewed topic list. It does not classify records from title keywords. `legal_proceeding` separates `phase`, `relief_requested_ru/en`, `outcome_ru/en`, `status_as_of`, court, case number and limits on implementation evidence. Court filings have no binding normative force. Legal stages are visible in cards and drawers in both languages.

`baseline-*.json.gz` and their SHA-256 manifest preserve the complete pre-migration v0.59 documents. `reviewed-records.json` contains the source packet; `migration-audit.json` records additions. Existing IDs, dates, source URLs and edge objects are retained. Arc membership remains thematic; comparison edges do not imply causal coordination or a universal precedent.

## Reproduce

From the repository root:

```sh
python3 -B aipower/scripts/migrate_judicial_power.py
python3 -B aipower/scripts/build.py
python3 -B aipower/scripts/validate.py
python3 -B aipower/tests/judicial_power_test.py
node --test aipower/tests/lenses_test.js aipower/tests/audit_navigation_test.js aipower/tests/audit_visuals_test.js
python3 -B aipower/tests/judicial_power_browser_test.py
```

Browser checks require Playwright and Chrome. Reports and screenshots are stored alongside this file. This release includes the previously prepared v0.59 banking/agent-commerce update. Research verification is scoped to the reviewed sources, not a complete docket audit or fresh verification of every atlas source.

## Verification

- General validator: 1,030 assertions; 17,772 typed references resolve in each language.
- Judicial migration: 294 assertions; all prior IDs, edges and source URLs preserved.
- JavaScript navigation, visual and view tests: 39 tests passed.
- Judicial browser tests: 313 assertions across RU/EN and desktop/mobile.
- Existing cross-cutting views: 129 browser assertions; banking regression: 145. No JavaScript errors or page overflow in the checked viewports.

The resulting dataset contains 650 stored events (649 visible), 79 claims, 32 claim checks, 30 arcs, 1,608 edges and 997 source URLs. Claim verification statuses were not promoted by this judicial packet.
