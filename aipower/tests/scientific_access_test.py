#!/usr/bin/env python3
"""Replay the two pinned releases and verify preservation and access-policy scope."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import migrate_knowledge_outcomes as knowledge
import migrate_scientific_access as release
from validate import references

BASE = '5b725eda3f0066fdbd8ddaa5523f9ef05bedacfc'
BACKLINKS = {'edgeIds', 'arcIds', 'arcFamilyIds', 'relationTypes'}


def baseline(lang):
    raw = subprocess.check_output(['git', 'show', BASE + f':aipower/ai_power_storygraph_{lang}.json'], cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest() == knowledge.BASE_HASH[lang]
    doc = knowledge.migrate(json.loads(raw))
    encoded = (json.dumps(doc, ensure_ascii=False, indent=2) + '\n').encode()
    assert hashlib.sha256(encoded).hexdigest() == release.BASE_HASH[lang]
    return doc


def main():
    report = dict(version=release.VERSION, passed=False, checks=[])
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report['checks'].append(label)
    def body(node):
        return {k: v for k, v in node.items() if k not in BACKLINKS}
    docs = {}
    for lang, filename in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
        old = baseline(lang)
        doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
        docs[lang] = doc
        ok(lang + ': exact migration replay from pinned v0.51 and v0.52', release.migrate(copy.deepcopy(old)) == doc)
        events = {e['id']: e for e in doc['events']}
        old_ids = {e['id'] for e in old['events']}
        added = {r['id'] for r in release.RECORDS}
        ok(lang + ': five unique additions; 562 retained', len(events) == 567 and set(events) - old_ids == added and old_ids <= set(events))
        ok(lang + ': all previous event bodies unchanged', all(body(e) == body(events[e['id']]) for e in old['events']))
        ok(lang + ': all 1390 previous edges unchanged', len(old['edges']) == 1390 and all(e in doc['edges'] for e in old['edges']))
        for col in ['claims', 'claimChecks', 'arcs', 'gaps', 'counterarguments', 'thesisNodes']:
            before = {x['id']: x for x in old[col]}
            after = {x['id']: x for x in doc[col]}
            ok(lang + ': no new or removed ' + col, set(before) == set(after))
            ok(lang + ': no status inflation ' + col, all(x.get('status') == after[i].get('status') for i, x in before.items()))
            if col not in ['arcs', 'claimChecks']:
                ok(lang + ': unchanged bodies ' + col, all(body(x) == body(after[i]) for i, x in before.items()))
        checks = {x['id']: x for x in doc['claimChecks']}
        for c in old['claimChecks']:
            now = checks[c['id']]
            ok(lang + ': claim-check evidence retained ' + c['id'], set(c.get('supporting_evidence', [])) <= set(now.get('supporting_evidence', [])))
            if c['id'] not in release.TEXT_UPDATES:
                ok(lang + ': unrelated claim-check unchanged ' + c['id'], body(c) == body(now))
        arcs = {a['id']: a for a in doc['arcs']}
        for arc in old['arcs']:
            ok(lang + ': all prior checkpoints retained ' + arc['id'], set(arc['key_nodes']) <= set(arcs[arc['id']]['key_nodes']))
        for aid in {a for r in release.RECORDS for a in r['arcs']}:
            dates = [events[n]['date'] for n in arcs[aid]['key_nodes'] if n in events]
            ok(lang + ': chronological arc ' + aid, dates == sorted(dates))
        for nid, (field, _, _) in release.TEXT_UPDATES.items():
            before = next(x for x in old['arcs'] + old['claimChecks'] if x['id'] == nid)
            now = (arcs | checks)[nid]
            ok(lang + ': previous text preserved ' + nid, now['editorial_history'][-1]['text'] == before[field])
        old_sources = {(s['id'], s['url']) for s in old['sourceIndex']}
        sources = {(s['id'], s['url']) for s in doc['sourceIndex']}
        urls = {url for _, url in sources}
        ok(lang + ': source IDs retained; six new URLs', old_sources <= sources and len(sources) == len(urls) == 824 and len(sources - old_sources) == 6)
        edges = [e for e in doc['edges'] if e['id'].startswith('EDGE_V053_')]
        signature = lambda e: (e['source'], e['target'], e['relation'], e.get('arc_id'))
        sigs = {signature(e) for e in edges}
        ok(lang + ': 21 new edges without semantic duplicates', len(edges) == len(sigs) == 21 and not sigs & {signature(e) for e in old['edges']})
        ok(lang + ': ten thematic memberships', sum(e['relation'] == 'part_of_arc' for e in edges) == 10 and all(e['relationship_class'] == 'thematic' for e in edges if e['relation'] == 'part_of_arc'))
        ok(lang + ': six comparisons do not assert causation', sum(e['relation'] == 'context_for' for e in edges) == 6)
        ok(lang + ': five scoped evidence links', sum(e['relation'] == 'supports_with_scope' for e in edges) == 5)
        for r in release.RECORDS:
            e = events[r['id']]
            label = lang + ': ' + r['id']
            ok(label + ' bilingual text', all(e[k] == e[k + '_' + lang] and e[k + '_ru'] and e[k + '_en'] for k in ['title', 'summary', 'caveat', 'safe_wording', 'mechanism']))
            ok(label + ' dated and routed', e['date'] == r['date'] <= release.DATE and e['story_primary_arc_id'] == r['arcs'][0] and e['story_secondary_arc_ids'] == r['arcs'][1:])
            ok(label + ' provenance retained', e['research_provenance'] == r)
            ok(label + ' all source URLs indexed', {s['url'] for s in e['sources']} <= urls)
            ok(label + ' provider review not independent replication', e['classification_review']['source_content_checked'] and not e['classification_review']['independent_replication'])
            ok(label + ' no inferred participant country', not e['actor_jurisdictions'] and bool(e['geographic_scope_basis']))
            ok(label + ' correct cyber inclusion', bool(e.get('primary_domain_id')) == (r['id'] == release.CVP))
        bio, dna, ros = [events[i] for i in [release.BIO, release.DNA, release.ROSALIND]]
        ok(lang + ': five cases are not five weapon incidents', bio['numbers']['reported_case_studies'] == 5 and not any(bio[k] for k in ['targets_named', 'malicious_intent_established', 'weapon_creation_established']))
        ok(lang + ': DNA letter remains proposal with explicit date basis', dna['status'] == 'proposal_not_enacted' and dna['normative_force'] == 'advisory' and dna['date_basis'] == 'first_contemporaneous_reporting' and dna['source_date'] == '')
        ok(lang + ': Rosalind publication separate from observed access terms', ros['date'] == '2026-10-30' and ros['current_state']['observed_at'] == '2026-11-07' and bool(ros['current_state']['date_note']))
        cvp = events[release.CVP]
        ok(lang + ': CVP limited access and evaluation denominator', cvp['normative_force'] == 'contractual' and cvp['implementation_stage'] == 'limited_access' and cvp['numbers']['red_team_successes'] == 34 and cvp['numbers']['attempts_per_tier'] == 50)
        ok(lang + ': one additional curated cyber card', sum(bool(e.get('primary_domain_id')) for e in events.values()) == 253 and sum(bool(e.get('primary_domain_id')) and e['editorial_priority'] == 1 for e in events.values()) == 159)
        ok(lang + ': all typed references resolve', references(doc) == doc['referenceIntegrity'] and doc['referenceIntegrity']['valid'])
        ok(lang + ': no hanging arcs', not doc['connectivity']['computed_hanging_arcs'])
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', (ROOT / filename).read_text(), re.S)
        ok(lang + ': generated HTML matches canonical JSON', embedded is not None and json.loads(embedded.group(1)) == doc)
        try:
            release.migrate(copy.deepcopy(doc))
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang + ': repeated migration rejected', rejected)
    for col in ['events', 'claims', 'claimChecks', 'arcs', 'edges', 'sourceIndex']:
        ok('RU/EN identity parity ' + col, [x['id'] for x in docs['ru'][col]] == [x['id'] for x in docs['en'][col]])
    report.update(passed=True, assertions=len(report['checks']))
    (release.PACKET / 'tests-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Passed', report['assertions'], 'scientific access integration checks')


if __name__ == '__main__':
    main()
