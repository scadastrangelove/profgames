# Cross-Cutting Views: v0.55

`crosscuttingViews` is identical in the Russian and English JSON. Its bilingual
definitions originate in `src/lenses.json`; `scripts/configure_lenses.py` validates
arc references before attaching the definitions to both data packages.

Each view has a stable `id`, bilingual labels/questions and ordered `tracks`.
A track matches an event when any `arc_ids` match its explicit `arcIds` and every
optional `required_arc_ids` matches. This is thematic selection, not evidence of
causation or support for all claims in an arc. There are no duplicated events,
new graph edges or title-keyword classifiers.

The default period covers the dataset update year and its preceding year.
The latest year is quarterly; the preceding year is annual. Full chronology
retains older and future-effective years. The update year, not a future event,
anchors the recent window. Event dates remain unchanged.

The matrix counts events per theme/time cell. Themes can overlap; the overall
count deduplicates canonical event IDs. Hidden aliases stay addressable through
existing record redirects. Explicit event-to-event links are shown only when
both endpoints are in the filtered selection; auto edges are excluded.

URL state uses `tab=lenses` and `s.view`, `s.period`, `s.geo`, `s.context`,
`s.track`, `s.bucket`, `s.q`, `s.page`. Legacy `tab=cyber` links remain valid.
History and language switching preserve state. Unsupported values normalize
to documented defaults, with an explicit no-results state for valid filters.

Evidence context, research outcome stages, status and caveats remain distinct.
No money totals, causal effect sizes or sovereignty scores are synthesized.
Geography refers to existing event jurisdiction/region fields and Global scope,
not inferred model nationality or control over the full technology chain.

All 567 stored events, 76 claims, 32 checks, 30 arcs, 1411 edges and 837 source
URLs are retained. The new research packets are candidates for later integration,
not additional canonical events or independent re-verification of the full base.
