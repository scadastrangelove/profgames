#!/usr/bin/env python3
"""Judicial evidence, bilingual metadata and preservation contracts."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from judicial_power_packet import PACKET, RECORDS, SOURCES, EXISTING, RELATIONS
from migrate_judicial_power import migrate, read_baseline
from validate import references

checks = 0
def check(condition, label):
    global checks
    assert condition, label
    checks += 1

docs = {}
for lang in ('ru','en'):
    doc = json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text())
    docs[lang] = doc
    before = read_baseline(lang)
    check(doc == migrate(before), 'Exact deterministic migration')
    check(references(doc)['valid'], 'Every typed reference resolves')
    for col in ('events','claims','claimChecks','arcs','edges','gaps','counterarguments'):
        ids = [e['id'] for e in doc[col]]
        check(len(ids)==len(set(ids)), 'Unique IDs: '+col)
        check({e['id'] for e in before[col]} <= set(ids), 'Preserved IDs: '+col)
    check(all(e in doc['edges'] for e in before['edges']), 'All old edges unchanged')
    check({s['url'] for s in before['sourceIndex']} <= {s['url'] for s in doc['sourceIndex']}, 'No source URL lost')
    check(doc['claims']==before['claims'] and doc['claimChecks']==before['claimChecks'], 'No claim or status inflation')
    ev = {e['id']:e for e in doc['events']}
    check(all(ev[e['id']]['date']==e['date'] for e in before['events']), 'Old chronology unchanged')
    signatures = [(e['source'],e['target'],e['relation'],e.get('arc_id')) for e in doc['edges']]
    for e in doc['edges']:
        if e['id'].startswith('EDGE_V060_'):
            check(signatures.count((e['source'],e['target'],e['relation'],e.get('arc_id')))==1, 'No duplicate new edges')
    for r in RECORDS:
        e = ev[r['id']]
        for f in ('title','summary','safe_wording','caveat','mechanism'):
            check(bool(e[f]) and e[f]==e[f+'_'+lang], 'Localized '+f)
        check(e['legal_topics']==r['legal_topics'], 'Explicit thematic classification')
        check(e['legal_proceeding']==r['legal_proceeding'], 'Procedural metadata preserved')
        check(set(e['actor_types'])<=doc['actorTypeLabels'].keys(), 'Registered actor types')
        check([s['url'] for s in e['sources']]==[SOURCES[k]['url'] for k in r['source_ids']], 'Exact source provenance')
        if e['legal_proceeding']['phase']=='complaint_filed':
            check(e['artifact_kind']=='court_filing' and e['normative_force']=='not_applicable', 'Complaint is not a binding order')
            check(e['cyber_role_ids']==[] and e['delegated_authority']=='not_applicable', 'No invented observed attack role')
    for eid in EXISTING:
        old = next(e for e in before['events'] if e['id']==eid)
        check(all(ev[eid][k]==v for k,v in old.items()), 'Existing evidence unchanged except added legal annotations')
    check(ev[RECORDS[5]['id']]['date']=='2026-08-27' and ev[RECORDS[5]['id']]['source_date']=='2026-09-25', 'Event date distinct from later court source')
    check(ev[RECORDS[8]['id']]['sources'][1]['date']=='', 'Unknown appeal publication day not fabricated')
    check(not doc['connectivity']['hanging_arcs_after_fix'], 'No hanging arcs')
    check(len(doc['arcs'])==len(before['arcs']), 'No duplicate thematic arcs')
for col in ('events','claims','arcs','edges'):
    check([e['id'] for e in docs['ru'][col]]==[e['id'] for e in docs['en'][col]], 'Language ID parity')
for eid in [r['id'] for r in RECORDS]+list(EXISTING):
    a,b=[next(e for e in docs[l]['events'] if e['id']==eid) for l in ('ru','en')]
    check(a['legal_proceeding']==b['legal_proceeding'], 'Bilingual legal metadata parity')
report = dict(passed=True, assertions=checks, references={l:references(d)['checked_references'] for l,d in docs.items()},
    new_events=len(RECORDS), new_edges=sum(len(r['arcs']) for r in RECORDS)+len(RELATIONS))
(PACKET/'test-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
