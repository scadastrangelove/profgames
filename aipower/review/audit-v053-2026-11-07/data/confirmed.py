#!/usr/bin/env python3
"""Reproduce confirmed findings without writing any file. Run with -B."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import audit

def verify(lang):
    name = f'ai_power_storygraph_{lang}.json'
    d, positions, _ = audit.load(name)
    nodes = {n['id']: n for c in audit.COLLS for n in d[c]}
    paths = {n['id']: (c,i) for c in audit.COLLS for i,n in enumerate(d[c])}
    arcs = {a['id']: a for a in d['arcs']}
    events = {e['id']: e for e in d['events']}
    def loc(id, field):
        p = paths[id] + (field,)
        return f'{audit.ROOT/name}:{positions.get(p, positions[paths[id]])}'
    findings = {f'F{i}': [] for i in range(1,7)}
    for e in d['events']:
        memberships = set(e.get('arcIds', [])) & set(arcs)
        routes = set(e.get('story_secondary_arc_ids', []))
        if e.get('story_primary_arc_id'): routes.add(e['story_primary_arc_id'])
        if memberships-routes:
            findings['F1'].append(dict(id=e['id'], missing=sorted(memberships-routes),
                location=loc(e['id'],'story_secondary_arc_ids'), memberships_location=loc(e['id'],'arcIds')))
    incident = collections.defaultdict(set)
    for e in d['edges']:
        incident[e['source']].add(e['id']); incident[e['target']].add(e['id'])
    for id,n in nodes.items():
        if 'edgeIds' in n and incident[id]-set(n['edgeIds']):
            findings['F2'].append(dict(id=id, stored=len(n['edgeIds']), incident=len(incident[id]),
                missing=sorted(incident[id]-set(n['edgeIds'])), location=loc(id,'edgeIds')))
    for a in d['arcs']:
        outside = [dict(id=id,date=events[id]['date']) for id in a['key_nodes'] if id in events
            and not a['start_date'] <= events[id]['date'] <= a['end_date']]
        if outside:
            findings['F3'].append(dict(id=a['id'], start=a['start_date'], end=a['end_date'], outside=outside,
                location=loc(a['id'],'start_date'), key_nodes_location=loc(a['id'],'key_nodes')))
    # This is the same rollout announcement, not merely two findings from one report.
    a = events['SIG_2026_OPENAI_GPT56_STAGED_RELEASE']
    b = events['SIG_2026_OPENAI_GPT56_VETTED_PARTNERS']
    if a['date']==b['date'] and a['url']==b['url'] and a['status']!=b['status']:
        findings['F4'].append(dict(ids=[a['id'],b['id']], date=a['date'], url=a['url'],
            titles=[a['title'],b['title']], statuses=[a['status'],b['status']],
            locations=[loc(a['id'],'status'),loc(b['id'],'status')],
            note='Same rollout event; both have blank dedupe_note_en and different graph identities.'))
    for e in d['edges']:
        missing=[k for k in ['source_kind','target_kind'] if not e.get(k)]
        if missing:
            findings['F5'].append(dict(id=e['id'], missing=missing, source=e['source'],target=e['target'],
                actual_kinds=[nodes[e['source']]['kind'],nodes[e['target']]['kind']],location=loc(e['id'],missing[0])))
    for c in ['events','claims','claimChecks','arcs','thesisNodes','gaps']:
        for n in d[c]:
            counts=collections.Counter(s.get('url') for s in n.get('sources',[]) if isinstance(s,dict) and s.get('url'))
            for url,count in counts.items():
                if count>1:findings['F6'].append(dict(id=n['id'], url=url,count=count,location=loc(n['id'],'sources')))
    summary={k:len(v) for k,v in findings.items()}
    summary['F2_missing_backlinks']=sum(len(x['missing']) for x in findings['F2'])
    summary['F3_outside_checkpoints']=sum(len(x['outside']) for x in findings['F3'])
    return dict(summary=summary,findings=findings)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--finding',choices=[f'F{i}' for i in range(1,7)])
    parser.add_argument('--lang',choices=['ru','en','both'],default='both')
    parser.add_argument('--summary',action='store_true')
    args=parser.parse_args()
    initial=json.loads((Path(__file__).resolve().parent/'report.json').read_text())['hashes_before']
    current={p:hashlib.sha256((audit.ROOT/p).read_bytes()).hexdigest() for p in initial}
    result={'original_inputs_and_validation_json_unchanged':current==initial}
    for lang in ['ru','en'] if args.lang=='both' else [args.lang]:
        data=verify(lang)
        result[lang]=data['summary'] if args.summary else data['findings'].get(args.finding,data)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
