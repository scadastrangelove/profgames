#!/usr/bin/env python3
"""Preservation, deduplication, bilingual and epistemic contracts for v0.58."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from economy_science_packet import package, PACKET
from migrate_economy_science import migrate, read_baseline
from migrate_audit_repair import check_document
from validate import references

checks = 0


def check(condition, message):
    global checks
    assert condition, message
    checks += 1


bundle = package()
targets = {d['input_id']: d['target_id'] for d in bundle['decisions']}
check(len(targets) == 45, 'Every input event receives one decision')
check(len(set(targets.values())) == 37, '45 observations resolve to 29 new and 8 existing events')
check(sum(len(e['economic_metrics']) for e in bundle['input']['events']) == 145, 'Input metrics preserved')
input_sources = {s['id'] for s in bundle['input']['sourceIndex']}
for event in bundle['input']['events']:
    check(all(set(m['source_ids']) <= input_sources for m in event['economic_metrics']), 'Metric provenance resolves')

documents = {}
for lang in ('ru', 'en'):
    before = read_baseline(lang)
    actual = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
    expected = migrate(before, bundle)
    check(actual == expected, 'Deterministic migration: ' + lang)
    documents[lang] = actual
    check_document(actual)
    check(references(actual)['valid'], 'Typed references: ' + lang)
    check({e['relation'] for e in actual['edges']} <= actual['relationTypes'].keys(), 'Every relation has a defined meaning')
    check('BIS' not in actual['entityRegistry']['actors'] and 'NBER / Google' not in actual['entityRegistry']['actors'], 'Actor aliases and compound entities not introduced')
    for collection in ('events', 'claims', 'claimChecks', 'arcs', 'edges', 'gaps', 'counterarguments'):
        old_ids = {e['id'] for e in before[collection]}
        new_ids = {e['id'] for e in actual[collection]}
        check(old_ids <= new_ids, 'All old IDs retained: ' + collection)
    check(all(e in actual['edges'] for e in before['edges']), 'Every original edge unchanged')
    normalize = lambda url: url.replace('%C2%A0', '').rstrip('\u00a0')
    check({normalize(s['url']) for s in before['sourceIndex']} <= {normalize(s['url']) for s in actual['sourceIndex']}, 'No evidence URL lost')
    by_id = {e['id']: e for e in actual['events']}
    check(set(targets.values()) <= by_id.keys(), 'All incoming observations map to published events')
    for record in bundle['events']:
        e = by_id[record['id']]
        check(e['title'] == e['title_'+lang] and e['summary'] == e['summary_'+lang], 'Localized visible text')
        check(e['caveat'] == e['caveat_'+lang] and bool(e['caveat']), 'Localized caveat')
        check(bool(e['actors']) and bool(e['sources']), 'Named actors and sources')
        check(set(e['route_eligible_arc_ids']) == set(record['arcs']), 'No accidental thematic routes')
    check(by_id['SIG_2026_MAYA_AGENT_REDISCOVERY_CORRECTION']['date'] == '2026-11-11', 'Correction date, not invented discovery')
    check('corrected the novelty claim' in by_id['SIG_2026_MAYA_AGENT_REDISCOVERY_CORRECTION']['summary_en'], 'Novelty correction visible')
    check(by_id['SIG_2025_MAYA_GLIHT_DETECTION_VALIDATION']['date'] == '2025-11-19', 'Publication year not volume year')
    check(by_id['SIG_2026_CHALMERS_AGENT_BIOLOGY_VALIDATION']['date'] == '2026-07-08', 'Paper date not September publicity')
    check(by_id['SIG_2026_AI_FUTURES_TIMELINE_REVISION']['event_or_forecast'] == 'forecast', 'Forecast not an observed capability')
    check('future' in by_id['SIG_2026_ANTHROPIC_EXPECTED_RD_THRESHOLD']['summary_en'], 'Expected threshold remains qualified')
    check('1.9' in by_id['SIG_2026_METR_ANTHROPIC_RD_ACCELERATION']['summary_en'], 'METR metric distinct from derived 1.7x')
    check('26%' in by_id['SIG_2026_ANTHROPIC_RD_AUTOMATION_INDEX']['summary_en'], 'Task share retained')
    for decision in bundle['decisions']:
        if decision['decision'] == 'enrich_existing':
            old = next(e for e in before['events'] if e['id'] == decision['target_id'])
            check(by_id[old['id']]['date'] == old['date'], 'Enrichment does not redate original events')

ru, en = documents['ru'], documents['en']
for collection in ('events', 'claims', 'arcs', 'edges'):
    check([e['id'] for e in ru[collection]] == [e['id'] for e in en[collection]], 'Bilingual ID and order parity')
check(ru['summary']['claim_status_counts'] == en['summary']['claim_status_counts'], 'Claim status parity')
check(ru['connectivity']['hanging_arcs_after_fix'] == [], 'No hanging arcs')
check(len(ru['arcs']) == 30, 'No duplicate thematic arcs')
report = dict(passed=True, assertions=checks, counts={k:len(ru[k]) for k in ('events','claims','arcs','edges','sourceIndex')},
    input_sha256=hashlib.sha256((PACKET / 'input-economy-ru.json').read_bytes()).hexdigest(),
    references={lang:documents[lang]['referenceIntegrity'] for lang in documents})
(PACKET / 'test-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False))
