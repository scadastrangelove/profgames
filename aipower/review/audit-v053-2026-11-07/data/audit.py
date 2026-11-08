#!/usr/bin/env python3
"""Read-only independent audit. Only reports under this /tmp directory are written."""
import argparse
import bisect
import collections
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path('/Users/serg/Documents/zhet/build/profgames-aipower-frontier-pacing/aipower')
OUT = Path(__file__).resolve().parent
COLLS = ['events','claims','claimChecks','arcs','arcFamilies','thesisNodes','counterarguments','gaps','edges']
KINDS = dict(zip(COLLS, ['evidence','claim','claim_check','story_arc',None,'synthetic_thesis','counterargument','gap','edge']))

def load(name):
    path = ROOT / name
    text = path.read_text()
    lines = [m.start() for m in re.finditer('\n', text)]
    positions = {}
    duplicate_keys = []
    decoder = json.JSONDecoder()
    n = len(text)
    def skip(i):
        while i < n and text[i].isspace(): i += 1
        return i
    def parse(i, p):
        i = skip(i)
        positions[p] = bisect.bisect_left(lines, i) + 1
        if text[i] == '{':
            obj = {}; i = skip(i+1)
            while text[i] != '}':
                key, i = decoder.raw_decode(text, i)
                i = skip(i)
                assert text[i] == ':'
                value, i = parse(i+1, p+(key,))
                if key in obj: duplicate_keys.append([list(p),key])
                obj[key] = value
                i = skip(i)
                if text[i] == ',': i = skip(i+1)
                else: break
            assert text[i] == '}'
            return obj,i+1
        if text[i] == '[':
            arr = []; i = skip(i+1)
            while text[i] != ']':
                value,i = parse(i,p+(len(arr),))
                arr.append(value); i = skip(i)
                if text[i] == ',': i = skip(i+1)
                else: break
            assert text[i] == ']'
            return arr,i+1
        return decoder.raw_decode(text,i)
    doc,end = parse(0,())
    assert skip(end)==n and doc==json.loads(text)
    return doc, positions, duplicate_keys

def walk(value, path=()):
    yield path,value
    if isinstance(value,dict):
        for k,v in value.items(): yield from walk(v,path+(k,))
    elif isinstance(value,list):
        for k,v in enumerate(value): yield from walk(v,path+(k,))

def norm_url(url):
    s=urlsplit(url)
    query=[(k,v) for k,v in parse_qsl(s.query,keep_blank_values=True) if not k.startswith('utm_') and k not in {'fbclid','gclid'}]
    return urlunsplit((s.scheme.lower(),s.netloc.lower().removeprefix('www.'),s.path.rstrip('/'),urlencode(sorted(query)),''))

def scc(nodes, adjacency):
    index={}; low={}; stack=[]; active=set(); components=[]
    def visit(v):
        index[v]=low[v]=len(index); stack.append(v);active.add(v)
        for w in adjacency.get(v,[]):
            if w not in index: visit(w);low[v]=min(low[v],low[w])
            elif w in active:low[v]=min(low[v],index[w])
        if low[v]==index[v]:
            part=[]
            while True:
                w=stack.pop();active.remove(w);part.append(w)
                if w==v:break
            components.append(part)
    for v in nodes:
        if v not in index:visit(v)
    return components

def audit(lang):
    file=f'ai_power_storygraph_{lang}.json'
    d,pos,duplicate_keys=load(file)
    def loc(p):return f'{ROOT/file}:{pos.get(tuple(p),1)}'
    result=collections.defaultdict(list)
    result['duplicate_json_keys']=duplicate_keys
    nodes={n['id']:n for c in COLLS for n in d[c]}
    nodepaths={n['id']:(c,i) for c in COLLS for i,n in enumerate(d[c])}
    nodecoll={n['id']:c for c in COLLS for n in d[c]}
    arcs={n['id']:n for n in d['arcs']}; events={n['id']:n for n in d['events']}
    edges={n['id']:n for n in d['edges']}
    def emit(category,p,**kw):result[category].append(dict(path=list(p),location=loc(p),**kw))
    for c in COLLS+['sourceIndex','sourceGroups','recipes','visualLanes']:
        ids=collections.Counter(n['id'] for n in d[c])
        for id,count in ids.items():
            if count>1:emit('duplicate_ids',(c,),id=id,count=count)
        if c in KINDS and KINDS[c]:
            for i,n in enumerate(d[c]):
                if n.get('kind')!=KINDS[c]:emit('node_kind_variants',(c,i,'kind'),id=n['id'],value=n.get('kind'),expected=KINDS[c])
    all_defs=collections.defaultdict(list)
    for p,v in walk(d):
        if isinstance(v,dict) and isinstance(v.get('id'),str):all_defs[v['id']].append(p)
    # Inventory all ID-shaped leaves, including audit and provenance, without treating them all as graph links.
    inventory=collections.defaultdict(lambda:dict(count=0,examples=[],unresolved=[]))
    id_re=re.compile(r'^(?:SIG_|TL_|CLM_|THESIS_|ARC_|GAP_|EDGE_|AI_ROLE_|CYBER_|BEH_|RES_|SRC_|ca-|export-|infra-|capital-|compute-|model-|data-|governance-|sovereign-|cyber-|palantir-)')
    ref_keys={'key_nodes','arcIds','edgeIds','arcFamilyIds','supporting_evidence','qualifying_evidence','evidence','recommended_arc_ids','hide_arc_ids','family_order','used_by','event_ids','claim_ids','related_research_event_ids','source','target'}
    for p,v in walk(d):
        if not p or not isinstance(v,str):continue
        key=next((k for k in reversed(p) if isinstance(k,str)), '')
        if key=='id':continue
        if key in ref_keys or key.endswith(('_id','_ids')) or v in all_defs or (id_re.match(v) and ' ' not in v):
            pattern='.'.join('[]' if isinstance(x,int) else x for x in p)
            row=inventory[pattern];row['count']+=1
            if len(row['examples'])<3:row['examples'].append([v,loc(p)])
            if v not in all_defs and v and ' ' not in v:row['unresolved'].append([v,loc(p)])
    result['reference_inventory']=dict(inventory)
    # Explicitly typed live references across every non-audit graph/classifier container.
    fields={
      'arcIds':set(arcs),'recommended_arc_ids':set(arcs),'hide_arc_ids':set(arcs),'story_primary_arc_id':set(arcs),
      'story_secondary_arc_ids':set(arcs),'parent_arc_id':set(arcs),'arc_id':set(arcs)|{'AUTO_CLAIMCHECK_SUPPORT','AUTO_COUNTERARGUMENTS'},
      'arcFamilyIds':{n['id'] for n in d['arcFamilies']},'family_id':{n['id'] for n in d['arcFamilies']},
      'arc_family_id':{n['id'] for n in d['arcFamilies']},'family_order':{n['id'] for n in d['arcFamilies']},
      'edgeIds':set(edges),'key_nodes':set(nodes)-set(edges),
      'supporting_evidence':set(events),'qualifying_evidence':set(events),'evidence':set(events),
      'event_ids':set(events),'event_id':set(events),'related_research_event_ids':set(events),
      'claim_ids':{n['id'] for n in d['claims']},'resilience_claim_id':{n['id'] for n in d['claims']},
      'source':set(nodes)-set(edges),'target':set(nodes)-set(edges),
      'visual_lane':{n['id'] for n in d['visualLanes']},'visual_lanes':{n['id'] for n in d['visualLanes']},
      'relation':set(d['relationTypes']),'relationTypes':set(d['relationTypes']),'recommended_relations':set(d['relationTypes']),
    }
    field_vocab={'primary_domain_id':'domains','cyber_domain_ids':'domains','cyber_role_ids':'roles','artifact_kind':'artifact_kinds',
       'normative_force':'normative_forces','implementation_stage':'implementation_stages','delegated_authority':'delegated_authority_states',
       'cyber_subdomain_ids':'subdomains','behavioral_mechanism_ids':'behavioral_mechanisms','behavioral_status':'behavioral_statuses',
       'evidence_context':'evidence_contexts','agent_population_scope':'agent_population_scopes','shared_writable_state':'shared_writable_states',
       'oversight_target':'oversight_targets','motivation_basis':'motivation_bases','behavior_track_ids':'behavior_tracks','behavior_origin':'behavior_origins',
       'concealment_targets':'concealment_targets','persistence_media':'persistence_media','goal_source':'goal_sources',
       'resilience_track_ids':'resilience_tracks','defense_stage_ids':'defense_stages','defense_evidence_kind':'defense_evidence_kinds'}
    for k,v in field_vocab.items():fields[k]={n['id'] for n in d['cyberFramework'][v]}
    excluded={'migrationAudit','researchAudit','factcheckAudit','chronologyAudit','classifierAudit','referenceIntegrity','connectivity'}
    for p,v in walk(d):
        if not p or p[0] in excluded or any(isinstance(k,str) and ('legacy' in k or k in {'research_provenance','historical_versions','classification_review','research_updates','current_state','historical_snapshot'}) for k in p):continue
        if isinstance(v,dict):
            for k,x in v.items():
                if k not in fields or x is None or x=='':continue
                values=x if isinstance(x,list) else [x]
                for j,item in enumerate(values):
                    if isinstance(item,str) and item not in fields[k]:
                        emit('typed_ref_errors',p+(k,)+( (j,) if isinstance(x,list) else ()),value=item,field=k,actual_collection=nodecoll.get(item))
    # Edge kinds, metadata, and reverse adjacency lists.
    incident=collections.defaultdict(set); relation_sets=collections.defaultdict(set);arcsets=collections.defaultdict(set)
    for i,e in enumerate(d['edges']):
        for ep in ['source','target']:
            id=e[ep];incident[id].add(e['id']);relation_sets[id].add(e['relation'])
            if e.get('arc_id') in arcs:arcsets[id].add(e['arc_id'])
            actual=nodecoll.get(id); kind=e[ep+'_kind']
            aliases={'event':'events','evidence':'events','claim':'claims','claim_check':'claimChecks','claimCheck':'claimChecks',
                     'arc':'arcs','story_arc':'arcs','synthetic_thesis':'thesisNodes','thesis':'thesisNodes','gap':'gaps','counterargument':'counterarguments'}
            if aliases.get(kind)!=actual:emit('edge_kind_errors',('edges',i,ep+'_kind'),id=e['id'],endpoint=id,value=kind,actual=actual)
        if e.get('arc_id') in arcs and e.get('arc_family_id')!=arcs[e['arc_id']]['family_id']:
            emit('edge_family_errors',('edges',i,'arc_family_id'),id=e['id'],arc=e['arc_id'],value=e['arc_family_id'],expected=arcs[e['arc_id']]['family_id'])
        if e['relation']=='part_of_arc' and (e['target'] not in arcs or e['target']!=e['arc_id'] or e['relationship_class']!='thematic'):
            emit('membership_edge_errors',('edges',i),edge=e)
    for id,n in nodes.items():
        if nodecoll[id] in {'edges','arcFamilies'}:continue
        for field,expected in [('edgeIds',incident[id]),('relationTypes',relation_sets[id])]:
            actual=set(n.get(field,[])); missing=expected-actual;extra=actual-expected
            if missing or extra:emit('backlink_'+field,nodepaths[id]+(field,),id=id,missing=sorted(missing),extra=sorted(extra))
        expected={arcs[a]['family_id'] for a in n.get('arcIds',[]) if a in arcs}
        if set(n.get('arcFamilyIds',[]))!=expected:emit('backlink_arcFamilyIds',nodepaths[id]+('arcFamilyIds',),id=id,missing=sorted(expected-set(n.get('arcFamilyIds',[]))),extra=sorted(set(n.get('arcFamilyIds',[]))-expected))
        missing=arcsets[id]-set(n.get('arcIds',[]))
        if missing:emit('backlink_arcIds',nodepaths[id]+('arcIds',),id=id,missing=sorted(missing))
    key_members=collections.defaultdict(set);thematic=collections.defaultdict(set)
    for a in d['arcs']:
        for id in a['key_nodes']:key_members[id].add(a['id'])
    for e in d['edges']:
        if e['relation']=='part_of_arc':thematic[e['source']].add(e['target'])
    for id,e in events.items():
        candidates=(set(e.get('arcIds',[]))|key_members[id]|thematic[id])&set(arcs)
        routes=set(e.get('story_secondary_arc_ids',[]))|({e['story_primary_arc_id']} if e.get('story_primary_arc_id') else set())
        if candidates!=routes:emit('route_membership_mismatch',nodepaths[id],id=id,missing=sorted(candidates-routes),extra=sorted(routes-candidates),primary=e.get('story_primary_arc_id'))
        if e.get('story_primary_arc_id') not in e.get('arcIds',[]) and e.get('story_primary_arc_id'):emit('primary_not_in_arcIds',nodepaths[id],id=id,primary=e['story_primary_arc_id'])
    for i,a in enumerate(d['arcs']):
        dated=[(events[id]['date'],id) for id in a['key_nodes'] if id in events]
        inversions=[dict(previous=dated[j-1],current=dated[j]) for j in range(1,len(dated)) if dated[j][0]<dated[j-1][0]]
        if inversions:emit('arc_chronology_order',('arcs',i,'key_nodes'),id=a['id'],inversions=inversions)
        if dated and (a['start_date']!=min(x[0] for x in dated) or a['end_date']!=max(x[0] for x in dated)):
            emit('arc_date_bounds',('arcs',i),id=a['id'],actual=[a['start_date'],a['end_date']],expected=[min(x[0] for x in dated),max(x[0] for x in dated)])
        if a.get('parent_arc_id') and a['family_id']!=arcs[a['parent_arc_id']]['family_id']:emit('hierarchy_family',('arcs',i),id=a['id'],parent=a['parent_arc_id'])
        for id in a['key_nodes']:
            if id in nodes and a['id'] not in nodes[id].get('arcIds',[]):emit('key_node_not_in_arcIds',('arcs',i,'key_nodes'),id=a['id'],node=id)
    for p,v in walk(d):
        if isinstance(v,list) and v and all(isinstance(x,(str,int,float)) for x in v):
            dup=[x for x,n in collections.Counter(v).items() if n>1]
            if dup:emit('duplicate_list_items',p,duplicates=dup)
    for key in [('source','target','relation','arc_id'),('source','target','relation')]:
        buckets=collections.defaultdict(list)
        for e in d['edges']:buckets[tuple(e[k] for k in key)].append(e['id'])
        result['duplicate_edges_'+'_'.join(key)]=[dict(signature=k,ids=v) for k,v in buckets.items() if len(v)>1]
    for key in [('date','url'),('date','title'),('title',)]:
        buckets=collections.defaultdict(list)
        for e in d['events']:buckets[tuple(e[k] for k in key)].append(e['id'])
        result['event_duplicate_candidates_'+'_'.join(key)]=[dict(signature=k,ids=v) for k,v in buckets.items() if len(v)>1]
    for field in ['url','id']:
        buckets=collections.defaultdict(list)
        for i,s in enumerate(d['sourceIndex']):buckets[norm_url(s[field]) if field=='url' else s[field]].append([s['id'],loc(('sourceIndex',i)),s['url']])
        result['source_duplicate_'+field]=[dict(key=k,sources=v) for k,v in buckets.items() if len(v)>1]
    uses=collections.defaultdict(set)
    for c in COLLS:
        for n in d[c]:
            urls={s['url'] for s in n.get('sources',[]) if isinstance(s,dict) and s.get('url')}
            if c=='events' and n.get('url'):urls.add(n['url'])
            for url in urls:uses[url].add(n['id'])
    src_by_url={s['url']:s for s in d['sourceIndex']}
    for i,s in enumerate(d['sourceIndex']):
        actual={x['id'] if isinstance(x,dict) else x for x in s['used_by']};expected=uses[s['url']]
        if actual!=expected:emit('source_backlinks',('sourceIndex',i,'used_by'),id=s['id'],url=s['url'],missing=sorted(expected-actual),extra=sorted(actual-expected))
        for j,u in enumerate(s['used_by']):
            if isinstance(u,dict) and u.get('kind'):
                n=nodes.get(u['id'],{})
                if u['kind']!=n.get('kind'):emit('source_used_by_kind',('sourceIndex',i,'used_by',j),id=s['id'],user=u,actual_kind=n.get('kind'))
    grouped=set()
    for i,g in enumerate(d['sourceGroups']):
        expected=set()
        for j,s in enumerate(g['sources']):
            url=s.get('url') if isinstance(s,dict) else s
            grouped.add(url)
            if url in src_by_url:
                expected|={x['id'] if isinstance(x,dict) else x for x in src_by_url[url]['used_by']}
                if s!=src_by_url[url]:emit('source_group_stale_source',('sourceGroups',i,'sources',j),group=g['id'],url=url,fields=[k for k in set(s)|set(src_by_url[url]) if s.get(k)!=src_by_url[url].get(k)])
            else:emit('source_group_unindexed',('sourceGroups',i,'sources',j),group=g['id'],url=url)
        actual={x['id'] if isinstance(x,dict) else x for x in g['used_by']}
        if actual!=expected:emit('source_group_backlinks',('sourceGroups',i,'used_by'),id=g['id'],missing=sorted(expected-actual),extra=sorted(actual-expected))
    result['source_ungrouped']=sorted(set(src_by_url)-grouped)
    # Hierarchy must be acyclic. General editorial graph need not be a DAG.
    hier={a['id']:[a['parent_arc_id']] if a.get('parent_arc_id') else [] for a in d['arcs']}
    result['hierarchy_cycles']=[s for s in scc(arcs,hier) if len(s)>1 or s[0] in hier[s[0]]]
    node_ids=set(nodes)-set(edges)-{n['id'] for n in d['arcFamilies']}
    adj=collections.defaultdict(set);undirected=collections.defaultdict(set);reverse=collections.defaultdict(set)
    for e in d['edges']:
        adj[e['source']].add(e['target']);reverse[e['target']].add(e['source'])
        undirected[e['source']].add(e['target']);undirected[e['target']].add(e['source'])
        if e['source']==e['target']:emit('self_loop',nodepaths[e['id']],edge=e)
    result['graph_scc']=[s for s in scc(node_ids,adj) if len(s)>1]
    result['graph_components']=sorted(scc(node_ids,undirected),key=lambda x:-len(x))
    reachable=set();todo=[n['id'] for n in d['thesisNodes']]
    while todo:
        v=todo.pop()
        if v in reachable:continue
        reachable.add(v);todo.extend(reverse[v]-reachable)
    result['cannot_reach_thesis']=[dict(id=id,collection=nodecoll[id],degree=len(undirected[id]),location=loc(nodepaths[id])) for id in sorted(node_ids-reachable)]
    for i,e in enumerate(d['events']):
        if str(e['year'])!=e['date'][:4]:emit('event_year_mismatch',('events',i,'year'),id=e['id'],date=e['date'],year=e['year'])
    result['summary_recomputed']={'collections':{c:len(d[c]) for c in COLLS},'role_counts':dict(collections.Counter(a['display_role'] for a in d['arcs'])),
        'events_with_primary':sum(bool(e.get('story_primary_arc_id')) for e in d['events']),
        'events_with_secondary':sum(bool(e.get('story_secondary_arc_ids')) for e in d['events']),
        'event_kind_counts':dict(collections.Counter(e['kind'] for e in d['events']))}
    html=(ROOT/('ai-power-atlas-ru.html' if lang=='ru' else 'ai-power-atlas.html')).read_text()
    embedded=re.search(r'<script\b[^>]*\bid="DATA"[^>]*>(.*?)</script>',html,re.S)
    result['embedded_json_matches']=bool(embedded and json.loads(embedded.group(1))==d)
    return d,pos,dict(result)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--section');parser.add_argument('--lang',default='ru');args=parser.parse_args()
    report=OUT/'report.json'
    if args.section:
        data=json.loads(report.read_text());print(json.dumps(data[args.lang][args.section] if args.lang in data else data[args.section],ensure_ascii=False,indent=2));return
    inputs=['ai_power_storygraph_ru.json','ai_power_storygraph_en.json','scripts/build.py','scripts/validate.py','review/validation.json']
    before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs}
    ru,rpos,rr=audit('ru');en,epos,er=audit('en')
    differences=[]
    rflat={p:v for p,v in walk(ru) if not isinstance(v,(dict,list))}
    eflat={p:v for p,v in walk(en) if not isinstance(v,(dict,list))}
    for p in rflat.keys()|eflat.keys():
        if rflat.get(p)!=eflat.get(p):differences.append(dict(path=list(p),ru=rflat.get(p),en=eflat.get(p),ru_line=rpos.get(p),en_line=epos.get(p)))
    after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs}
    result={'root':str(ROOT),'hashes_before':before,'hashes_after':after,'inputs_unchanged':before==after,'ru':rr,'en':er,'parity_differences':differences}
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for lang in ['ru','en']:
        print(lang,json.dumps({k:len(v) if isinstance(v,(list,dict)) else v for k,v in result[lang].items() if k not in {'reference_inventory'}},ensure_ascii=False,indent=2))
    print('parity leaf differences',len(differences));print('inputs unchanged',result['inputs_unchanged']);print('report',report)

if __name__=='__main__':main()
