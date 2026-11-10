#!/usr/bin/env python3
"""Evidence-preservation, migration and editorial-contract tests for v0.56."""
import copy
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build
from migrate_crosscutting_expansion import baseline, migrate, PACKET
from validate import references

package = json.loads((PACKET / 'accepted.json').read_text())
framework = json.loads((ROOT / 'src/lenses.json').read_text())
report = {'checks': 0, 'languages': {}}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--snapshot-v057', action='store_true', help='Check the preserved v0.56 input to v0.57')
args = parser.parse_args()


def check(value, message):
    if not value:
        raise AssertionError(message)
    report['checks'] += 1


for lang in ('ru', 'en'):
    old = baseline(lang)
    if args.snapshot_v057:
        from migrate_astra_underperformance import baseline as baseline056
        doc = baseline056(lang)
    else:
        doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
    check(migrate(old, package, framework) == doc, lang + ': exact deterministic replay')
    check(old['meta']['version'] == '0.55' and doc['meta']['version'] == '0.56', 'release boundary')
    updates = {u['event_id']: u for u in package.get('updates', [])}
    old_events, new_events = {e['id']: e for e in old['events']}, {e['id']: e for e in doc['events']}
    added = {e['id'] for e in package['events']}
    check(set(new_events) - set(old_events) == added, 'exact additions')
    check(set(old_events) <= set(new_events), 'no event loss')
    for eid, before in old_events.items():
        allowed = {'edgeIds', 'relationTypes', 'arcIds', 'arcFamilyIds'}
        if eid in updates:
            update = updates[eid]
            allowed.update(update.get('fields', {}))
            for key in update.get('bilingual_fields', []):
                allowed.update([key, key+'_ru', key+'_en'])
            allowed.update(['editorial_history', 'research_updates', 'sources'])
        check({k: v for k, v in before.items() if k not in allowed} ==
              {k: v for k, v in new_events[eid].items() if k not in allowed}, 'preserved event: ' + eid)
        approved_date = updates.get(eid, {}).get('fields', {}).get('date', before['date'])
        check(approved_date == new_events[eid]['date'], 'only approved date correction: ' + eid)
    for key in ('claims', 'claimChecks', 'thesisNodes', 'counterarguments', 'gaps'):
        check(old[key] == doc[key], 'no unreviewed claim rewrite: ' + key)
    check(all(e in doc['edges'] for e in old['edges']), 'all old semantic edges unchanged')
    old_sources = {s['id']: s for s in old['sourceIndex']}
    new_sources = {s['id']: s for s in doc['sourceIndex']}
    for sid, source in old_sources.items():
        check(new_sources[sid]['url'] == source['url'], 'source identity: ' + sid)
    check(len({s['url'] for s in doc['sourceIndex']}) == len(doc['sourceIndex']), 'source URL dedup')
    check(doc['referenceIntegrity'] == references(doc) and references(doc)['valid'], 'all typed references')
    check(doc['crosscuttingViews'] == framework, 'shared definitions')
    check([v['id'] for v in framework['views']] == ['knowledge', 'economy', 'sovereignty', 'delegation'], 'view order')
    for eid in added:
        event = new_events[eid]
        check(all(event.get(f'{key}_{language}') for key in ['title', 'summary', 'caveat', 'mechanism'] for language in ('ru', 'en')), 'bilingual evidence: ' + eid)
        check(event['date'] <= '2026-11-10', 'no invented future observation: ' + eid)
        check(set(event['actor_types']) <= set(doc['actorTypeLabels']), 'actor vocabulary: ' + eid)
        check(set(event['evidence_context']) <= {v['id'] for v in doc['cyberFramework']['evidence_contexts']}, 'context vocabulary: ' + eid)
        check(event['artifact_kind'] in {v['id'] for v in doc['cyberFramework']['artifact_kinds']}, 'artifact vocabulary: ' + eid)
        incident = {e['id'] for e in doc['edges'] if eid in [e['source'], e['target']]}
        check(incident == set(event['edgeIds']), 'complete backlinks: ' + eid)
        check(event['route_eligible_arc_ids'] == event['arcIds'], 'route membership: ' + eid)
        check(all(s['primary_or_secondary'] == 'primary' for s in event['sources']), 'primary sources: ' + eid)
    check(doc['connectivity']['hanging_arcs_after_fix'] == [], 'no hanging arcs')
    mattergen = new_events['SIG_2025_MATTERGEN_SYNTHESIS']
    check(mattergen['date'] == '2025-01-16' and mattergen['current_state']['observed_at'] == '2026-04-20', 'publication and later reanalysis dates separated')
    check('SIG_2026_MATTERGEN_NOVELTY_REANALYSIS' not in new_events, 'study-family deduplication')
    report['languages'][lang] = {'events': len(doc['events']), 'edges': len(doc['edges']),
        'sources': len(doc['sourceIndex']), 'references': references(doc)['checked_references']}

with tempfile.TemporaryDirectory(prefix='atlas-v056-build-') as tmp:
    target = Path(tmp)
    shutil.copytree(ROOT / 'src', target / 'src')
    (target / 'review').mkdir()
    for lang in ('ru', 'en'):
        shutil.copy2(ROOT / f'ai_power_storygraph_{lang}.json', target)
    build(target)
    for name in ('ai-power-atlas-ru.html', 'ai-power-atlas.html', 'review/compiled-ru.js', 'review/compiled-en.js'):
        check((target / name).read_bytes() == (ROOT / name).read_bytes(), 'reproducible build: ' + name)
report['passed'] = True
(PACKET / 'tests.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
