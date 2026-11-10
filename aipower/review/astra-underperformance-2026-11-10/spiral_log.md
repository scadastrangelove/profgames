# Release loop: v0.57

- Added the source-reviewed Astra record; preserved prior events, claims and edges.
- Measured: exact v0.55 -> v0.56 -> v0.57 replay and source/ID conservation pass.
- Review found an inactive-route picker reset; serialized the selected view mode.
- Browser regression found RU's older addEventListener plus onclick double dispatch;
  aligned RU with EN's replaceable onclick navigation and tested the real page.
- Anti-overfit: generic route-state restoration; no model-title or event-ID UI branch.
- Debt: no newly identified release blocker. Experiment replication and exhaustive
  source re-verification are outside this release's scope, not claimed as completed.
