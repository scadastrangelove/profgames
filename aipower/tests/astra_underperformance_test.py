#!/usr/bin/env python3
"""Check v0.57 preservation, factual distinctions, classifiers and replay."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from migrate_astra_underperformance import baseline, migrate, PACKET
from migrate_crosscutting_expansion import baseline as baseline055, migrate as migrate056, PACKET as PACKET056
from validate import references

package = json.loads((PACKET / 'accepted.json').read_text())
report = dict(checks=0, languages={})


def check(value, label):
    assert value, label
    report['checks'] += 1


for lang in ('ru', 'en'):
    before = baseline(lang)
    doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
    check(migrate056(baseline055(lang), json.loads((PACKET056 / 'accepted.json').read_text()),
                     doc['crosscuttingViews']) == before, 'v0.55 -> v0.56 replay')
    check(migrate(before, package) == doc, 'v0.56 -> v0.57 replay')
    events = {e['id']: e for e in doc['events']}
    for old in before['events']:
        check(old == events[old['id']], 'existing event preserved: ' + old['id'])
    for key in ('claims', 'claimChecks', 'thesisNodes', 'counterarguments', 'gaps', 'crosscuttingViews'):
        check(before[key] == doc[key], 'unchanged ' + key)
    check(all(e in doc['edges'] for e in before['edges']), 'old edges unchanged')
    check({s['url'] for s in before['sourceIndex']} <= {s['url'] for s in doc['sourceIndex']}, 'sources retained')
    event = events[package['event']['id']]
    check(len(doc['events']) == len(before['events']) + 1, 'one event only')
    check(event['date'] == '2026-08-20' and event['source_date'] == '2026-11-04', 'observation vs source date')
    check(event['current_state']['observed_at'] == '2026-11-04', 'later report visible in updates')
    check(event['behavior_origin'] == 'deployment_observed', 'not prompted sandbagging')
    check(event['goal_source'] == 'unknown' and event['motivation_basis'] == 'no_motivation_claim', 'no inferred objective')
    check('BEH_STRATEGIC_CONCEALMENT' not in event['behavioral_mechanism_ids'], 'no unsupported strategic label')
    for field, vocabulary in [('cyber_subdomain_ids', 'subdomains'), ('behavioral_mechanism_ids', 'behavioral_mechanisms'),
                              ('behavioral_status', 'behavioral_statuses'), ('evidence_context', 'evidence_contexts'),
                              ('oversight_target', 'oversight_targets'), ('concealment_targets', 'concealment_targets')]:
        check(set(event[field]) <= {v['id'] for v in doc['cyberFramework'][vocabulary]}, 'valid '+field)
    for field in ('title', 'summary', 'caveat', 'mechanism'):
        check(all(event.get(field+'_'+language) for language in ('ru', 'en')), 'bilingual '+field)
    check(set(event['edgeIds']) == {e['id'] for e in doc['edges'] if e['source'] == event['id']}, 'backlinks exact')
    check(all(e['relation'] == 'part_of_arc' for e in doc['edges'] if e['source'] == event['id']), 'thematic links only')
    check(references(doc)['valid'], 'all references resolve')
    check(not doc['connectivity']['hanging_arcs_after_fix'], 'no hanging arcs')
    report['languages'][lang] = dict(events=len(events), edges=len(doc['edges']), sources=len(doc['sourceIndex']),
                                    references=references(doc)['checked_references'])
report['passed'] = True
(PACKET / 'tests.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
