# Access, infrastructure and disclosure correction

Release v0.49, reviewed 27 October 2026. Seven records, two updated records,
20 links and nine new source URLs. No new top-level arcs or claims.

## Editorial Decisions

| Record | Source-backed observation | Limit |
| --- | --- | --- |
| OpenAI resumption | Provider dates frontier RL/internal inference resumption to October 1, after 11 days | Not all products; no proof that the specific stopped run resumed; no independent containment audit |
| Sweden | SVT and Ekot quote Government Offices on public web interfaces, Intric and approved Copilot | Institutional access policy, not a nationwide ban; enforcement not independently observed |
| Georgia | Secretary of State's October 26 correction says public free Data Hub, no voter-register access or paywall bypass | Office relays Anthropic's confirmation; full technical trace unavailable; other disclosed cases not refuted |
| SpaceX | Issuer announces binding commitment for approximately $40bn GPU finance lease | Subject to closing; delivery expected H1 2027; not cash received or operational GPUs |
| IBM llm-d | Internal deployment and vendor benchmarks on 544 H100s | Selected workloads and token cost, not independently measured TCO or quality parity |
| IBM earnings call | CEO's public estimate and data-control argument | Interested supplier position, not a reproducible 90% effectiveness benchmark |
| Mozilla | September report fits an approximately 4.4-month lag to METR data | September 1 snapshot; task-dependent, not a fixed October gap or universal parity |

Full URLs, dates, bilingual descriptions and caveats are in `evidence.json`.
The two older incident records retain their dates and historical summaries;
new state information is appended to visible caveats. The Georgia record is
commentary/correction, not an additional attack. Neither provider pause nor
Swedish access policy establishes causality between the two.

The IBM technical report and earnings-call position are explicitly related,
not counted as independent measurements. Mozilla and the existing AISI result
use different snapshots and methods. SpaceX finance is connected to compute
infrastructure, not evidence of open-model quality or profitability.

## Reproduction

`scripts/migrate_october_access.py` requires the exact v0.48 bilingual baseline
SHA-256 values and rejects repeated application. `migration-audit.json` records
prior object hashes, source identities and resulting counts.

From `aipower`:

```sh
python3 scripts/build.py
python3 scripts/validate.py
python3 tests/october_access_test.py
python3 tests/october_access_browser_test.py --chromium "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

The data test replays the prior migrations, checks unchanged objects and dates,
typed references, URL/link deduplication and embedded-JSON parity. Browser tests
cover both languages, search, source links, arc navigation, Back, Escape,
permalinks, cyber inclusion and desktop/mobile overflow. They do not independently
replicate provider claims or re-audit the entire source registry.

## Results

- General validation: 944 checks; 11,064 typed references resolve per language.
- Migration and evidence checks: 222 passed; all earlier IDs, edges and URLs retained.
- Browser regression: 176 passed; targeted navigation/correction checks: 184 passed.
- Both languages were checked at 1440px and 390px; no JavaScript errors,
  external runtime requests or horizontal page overflow were found.
- Later clarifications appear immediately below the record title, before the
  classification block and historical account. Other current-state objects
  retain their existing specialized rendering.

These are local build/QA results. Public deployment is verified separately
after pushing the release; no remote-deployment result is implied by them.
