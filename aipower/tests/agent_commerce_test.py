#!/usr/bin/env python3
"""Preservation, provenance and bilingual contracts for agent-commerce integration."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from agent_commerce_packet import PACKET, RECORDS, SOURCES, FIN, OLD_AMAZON, COURT
from migrate_agent_commerce import migrate, read_baseline, LEGAL_EDGES, CLAIM
from migrate_audit_repair import check_document
from validate import references

count = 0
def check(condition, message):
    global count
    assert condition, message
    count += 1


docs = {}
for lang in ('ru', 'en'):
    before = read_baseline(lang)
    doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
    docs[lang] = doc
    check(doc == migrate(before), 'Exact deterministic migration: ' + lang)
    check_document(doc)
    check(references(doc)['valid'], 'Every typed reference resolves')
    for collection in ('events', 'claims', 'claimChecks', 'arcs', 'edges', 'gaps', 'counterarguments'):
        ids = [n['id'] for n in doc[collection]]
        check(len(ids) == len(set(ids)), 'Unique IDs: ' + collection)
        check({n['id'] for n in before[collection]} <= set(ids), 'Preserved IDs: ' + collection)
    check({s['url'] for s in before['sourceIndex']} <= {s['url'] for s in doc['sourceIndex']}, 'All evidence URLs retained')
    check(all(e in doc['edges'] for e in before['edges'] if e['id'] not in LEGAL_EDGES), 'Unrelated edges unchanged')
    old_edges = {e['id']: e for e in before['edges']}
    for edge in doc['edges']:
        if edge['id'] in LEGAL_EDGES:
            check(all(edge[f] == old_edges[edge['id']][f] for f in ('source', 'target', 'relation', 'arc_id')), 'Legal correction preserves topology')
            check(edge['editorial_history'][-1]['fields'] == old_edges[edge['id']], 'Old legal wording archived')
    events = {e['id']: e for e in doc['events']}
    check(all(events[e['id']]['date'] == e['date'] for e in before['events']), 'No old event redated')
    signatures = [(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']]
    for edge in doc['edges']:
        if edge['id'].startswith('EDGE_V059_'):
            check(signatures.count((edge['source'], edge['target'], edge['relation'], edge.get('arc_id'))) == 1, 'No duplicate new edge')
    contexts = {x['id'] for x in doc['cyberFramework']['evidence_contexts']}
    for r in RECORDS:
        e = events[r['id']]
        for field in ('title', 'summary', 'caveat', 'mechanism', 'safe_wording'):
            check(bool(e[field]) and e[field] == e[field+'_'+lang], 'Localized field: ' + field)
        check(set(e['route_eligible_arc_ids']) == set(r['arcs']), 'Deliberate route membership')
        check(set(e['actor_types']) <= doc['actorTypeLabels'].keys(), 'Registered actor types')
        check(set(e['evidence_context']) <= contexts, 'Registered evidence context')
        check(e['date'] == r['date'] and e['research_evidence_kind'] == r['evidence_kind'], 'Date and evidence class')
        check([s['url'] for s in e['sources']] == [SOURCES[k]['url'] for k in r['source_ids']], 'Exact reviewed source set')
    old = events[OLD_AMAZON]
    check(old['date'] == '2026-03-09' and old['status_update_date'] == '2026-08-04', 'Historical and update dates remain separate')
    check(old['current_legal_status'] == 'preliminary_injunction_vacated_and_remanded', 'Correct procedural status')
    check('stayed pending appeal' not in old['caveat_en'], 'No obsolete active caveat')
    claim = next(c for c in doc['claimChecks'] if c['id'] == CLAIM)
    check(COURT in claim['qualifying_evidence'], 'Counterevidence attached to the claim')
    indexed = next(e for e in claim['evidence_relations'] if e['event_id'] == COURT)
    check(indexed['relations'] == ['qualifies'] and indexed['legacy_fields'] == ['qualifying_evidence'], 'Machine-readable evidence polarity is current')
    check(claim['status'] == next(c for c in before['claimChecks'] if c['id'] == CLAIM)['status'], 'No automatic claim promotion')
    ap2 = events['SIG_2026_AP2_PREAUTHORIZATION_CONTEXT_TESTBED']
    check(ap2['artifact_kind'] == 'evaluation' and ap2['delegated_authority'] == 'evaluated', 'AP2 is a test, not an incident')
    check(ap2['cyber_role_ids'] == ['AI_ROLE_PROTECTED_SYSTEM'], 'Payment agent is the protected system')
    visa = events['SIG_2026_VISA_AGENT_PAYMENTS_APPROVED_PILOT']
    check(visa['sources'][1]['date'] == '' and visa['sources'][1]['checked_at'] == '2026-11-15', 'No invented documentation date')
    check(visa['implementation_stage'] == 'limited_access', 'Pilot is not general deployment')
    for key in ('SIG_2026_BIS_BANKING_SCENARIOS_REVENUE_INTERFACE', 'SIG_2026_SAFE_AGENTIC_BANK_RUN_SCENARIO'):
        check(events[key]['research_evidence_kind'] == 'conditional_scenario_analysis', 'Scenario explicitly typed')
    check(len(doc['arcs']) == len(before['arcs']) and not doc['connectivity']['hanging_arcs_after_fix'], 'No added or hanging arcs')
    check(doc['summary']['claim_status_counts'] == before['summary']['claim_status_counts'], 'No claim status inflation')
    original_urls = {s['url'] for s in before['sourceIndex']}
    check(not original_urls.intersection(s['url'] for s in SOURCES.values()), 'New disclosures are not existing source records')
for collection in ('events', 'claims', 'claimChecks', 'arcs', 'edges'):
    check([x['id'] for x in docs['ru'][collection]] == [x['id'] for x in docs['en'][collection]], 'Bilingual ID parity')
for r in RECORDS:
    check(next(e for e in docs['ru']['events'] if e['id'] == r['id'])['summary_en'] ==
          next(e for e in docs['en']['events'] if e['id'] == r['id'])['summary_en'], 'Cross-language field parity')
for collection, node_id, field in [('events', OLD_AMAZON, 'caveats'), ('arcs', FIN, 'counterpoints')]:
    nodes = {l:next(e for e in docs[l][collection] if e['id'] == node_id) for l in docs}
    for language in ('ru', 'en'):
        check(nodes['ru'][field+'_'+language] == nodes['en'][field+'_'+language], 'Corrected bilingual limitations agree')
report = dict(passed=True, assertions=count, counts={k:len(docs['ru'][k]) for k in ('events','claims','arcs','edges','sourceIndex')},
              references={lang:docs[lang]['referenceIntegrity'] for lang in docs})
(PACKET / 'test-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False))
