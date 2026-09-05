#!/usr/bin/env python3
"""Validate v0.30 references, data contracts, legacy preservation and embedded-data parity.
No third-party dependencies. --refresh-metadata updates counts only; assertions always run.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
REG=[('events','event'),('claims','claim'),('claimChecks','claimCheck'),('arcs','arc'),('arcFamilies','arcFamily'),('thesisNodes','thesis'),('counterarguments','counterargument'),('gaps','gap'),('edges','edge')]
VIRTUAL={'AUTO_CLAIMCHECK_SUPPORT','AUTO_COUNTERARGUMENTS'}
def references(d):
 typed={};dups=[];refs=[];bad=[];mismatch=[]
 for arr,kind in REG:
  for n in d[arr]:
   if n['id'] in typed:dups.append(n['id'])
   typed[n['id']]=kind
 def check(field,id,expected=None):
  expected={'evidence':'event','synthetic_thesis':'thesis','claim_check':'claimCheck','story_arc':'arc'}.get(expected,expected)
  refs.append((field,id))
  if id not in typed and id not in VIRTUAL:bad.append((field,id))
  elif expected and id in typed and typed[id]!=expected:mismatch.append((field,id,expected,typed[id]))
 for a in d['arcs']:
  for x in a.get('key_nodes',[]):check('arc.key_nodes',x)
  if a.get('family_id'):check('arc.family_id',a['family_id'],'arcFamily')
 for e in d['edges']:
  for ep in ['source','target']:check('edge.'+ep,e[ep],e.get(ep+'_kind'))
  if e.get('arc_id'):check('edge.arc_id',e['arc_id'])
  if e.get('arc_family_id'):check('edge.arc_family_id',e['arc_family_id'],'arcFamily')
 for name,prefix,field in [('claims','claim','supporting_evidence'),('claimChecks','claim_check','supporting_evidence'),('counterarguments','counterargument','evidence')]:
  for c in d[name]:
   for x in c.get(field,[]):check(prefix+'.'+field,x)
 for c in d['countries']:
  for field in ['strongest_supporting_evidence','strongest_counter_evidence']:
   for x in c.get(field,[]):
    if x in typed or re.match(r'^(SIG_|TL_|CLM_|THESIS_|ARC_|GAP_|ca-)',str(x)):check('country.'+field,x)
 for c in d['recipes']:
  for x in c.get('recommended_filters',{}).get('hide_arc_ids',[]):check('recipe.recommended_filters.hide_arc_ids',x)
  for x in c.get('recommended_arc_ids',[]):check('recipe.recommended_arc_ids',x)
 for name,kind in [('events','event'),('claims','claim'),('claimChecks','claimCheck')]:
  for c in d[name]:
   for field in ['arcIds','edgeIds']:
    for x in c.get(field,[]):check(kind+'.'+field,x)
 for s in d['sourceIndex']:
  for x in s.get('used_by',[]):check('source.used_by',x['id'] if isinstance(x,dict) else x)
 return {'valid':not(bad or mismatch or dups),'checked_references':len(refs),'checked_by_field':dict(Counter(k for k,x in refs)),'unresolved_count':len(bad),'unresolved':bad,'kind_mismatch_count':len(mismatch),'kind_mismatches':mismatch,'duplicate_ids':dups}
def folded_duplicates(values):
 buckets={}
 for value in values:buckets.setdefault(value.casefold(),[]).append(value)
 return [items for items in buckets.values() if len(set(items))>1]
def validate(root=ROOT,refresh=False,skip_html=False):
 report={'version':'0.30','base_commit':'156e39a21b5a523092ccb2975e5aa38f489f52b6','languages':{},'tests':[]};data={}
 def ok(name,condition):
  if not condition:raise AssertionError(name)
  report['tests'].append(name)
 for lang in ['ru','en']:
  path=root/f'ai_power_storygraph_{lang}.json';d=json.loads(path.read_text());data[lang]=d;b=json.loads((root/f'review/baseline_{lang}.json').read_text())
  result=references(d);ok(lang+': all typed references resolve',result['valid'])
  if refresh:d['referenceIntegrity']=result;path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
  else:ok(lang+': reference metadata current',result['checked_references']==d['referenceIntegrity']['checked_references'])
  for field,kind in REG:
   ok(lang+': preserved '+field+' IDs',{x['id'] for x in b[field]}=={x['id'] for x in d[field]})
  oldurls={x['url'] for x in b['sourceIndex']};urls={x['url'] for x in d['sourceIndex']}
  ok(lang+': no source URL lost',oldurls<=urls);ok(lang+': no duplicate source URL',len(urls)==len(d['sourceIndex']))
  ok(lang+': original event dates preserved',{e['id']:e['date'] for e in d['events']}=={e['id']:e['date'] for e in b['events']})
  ev={e['id']:e for e in d['events']};cyber=[e for e in d['events'] if e.get('primary_domain_id')]
  ok(lang+': exactly 97 reviewed cyber facts',len(cyber)==97)
  vocab={k:{x['id'] for x in d['cyberFramework'][k]} for k in ['domains','roles','artifact_kinds','normative_forces','implementation_stages','delegated_authority_states']}
  for e in cyber:
   ok(lang+': valid classification '+e['id'],e['primary_domain_id'] in e['cyber_domain_ids'] and set(e['cyber_domain_ids'])<=vocab['domains'] and set(e['cyber_role_ids'])<=vocab['roles'] and e['artifact_kind'] in vocab['artifact_kinds'] and e['normative_force'] in vocab['normative_forces'] and e['implementation_stage'] in vocab['implementation_stages'] and e['delegated_authority'] in vocab['delegated_authority_states'] and e['editorial_priority'] in [1,2,3] and bool(e.get('scope_'+lang)))
  ok(lang+': no live mixed legal_force field',not any('legal_force' in e or 'evidence_type' in e for e in d['events']))
  fixtures={
   'SIG_2026_CA_SB53_EFFECTIVE':('binding',None),
   'SIG_2026_MYTHOS_FIREFOX_271':('not_applicable','AI_ROLE_DEFENSIVE_TOOL'),
   'SIG_2025_CLAUDE_ORCHESTRATED_ESPIONAGE':('not_applicable','AI_ROLE_ATTACK_ENABLER')}
  for id,(force,role) in fixtures.items():ok(lang+': semantic fixture '+id,ev[id]['normative_force']==force and (not role or role in ev[id]['cyber_role_ids']))
  for e in cyber:
   if 'FSTEC' in e['id'] and '117' in e['id']:ok(lang+': FSTEC scoped binding',e['normative_force']=='binding' and e['editorial_priority']==1)
   if 'ECHOLEAK' in e['id']:ok(lang+': EchoLeak protected + attack',set(['AI_ROLE_PROTECTED_SYSTEM','AI_ROLE_ATTACK_ENABLER'])<=set(e['cyber_role_ids']))
  ok(lang+': Armenia and Pakistan in jurisdiction facets',all(x in d['counts']['jurisdictions'] for x in ['Armenia','Pakistan']))
  ok(lang+': Cloudflare in actor facets','Cloudflare' in d['counts']['actor_entities'])
  actor_counts=Counter(x for e in d['events'] for x in e.get('actor_entities',[]))
  ok(lang+': actor selector counts match events',dict(actor_counts)==d['counts']['actor_entities'])
  ok(lang+': actor registry matches selector',set(d['entityRegistry']['actors'])==set(actor_counts))
  ok(lang+': actor selector has no case-fold duplicates',not folded_duplicates(actor_counts))
  ok(lang+': jurisdiction selector has no case-fold duplicates',not folded_duplicates(d['counts']['jurisdictions']))
  ok(lang+': known actor aliases collapsed','Nvidia' not in actor_counts and 'US DOJ' not in actor_counts and actor_counts['NVIDIA']==12 and actor_counts['US Department of Justice']==4)
  ok(lang+': no uncategorised geography',not any(e.get('geography_unclassified') for e in d['events']))
  unresolved=[e for e in d['events'] if e.get('actor_classification_status')=='review_required']
  ok(lang+': unresolved actors exposed, not guessed',len(unresolved)==16 and all(e.get('actor_unclassified') for e in unresolved))
  aix=ev['SIG_CYBER_2025_AIXCC_FINAL'];ok(lang+': AIxCC 54/63 and 43/63',aix['numbers']['injected_bugs']==63 and aix['numbers']['synthetic_vulnerabilities_found']==54 and aix['numbers']['synthetic_vulnerabilities_patched']==43)
  kimi=ev['SIG_2026_KIMI_K3_OPEN_WEIGHT_ANNOUNCEMENT'];ok(lang+': Kimi dates separated',kimi['date']=='2026-07-16' and kimi['current_state']['observed_at']=='2026-09-05' and kimi['current_state']['event_date'] is None and kimi['current_state']['weights_public'] is True)
  ok(lang+': thematic edges explicitly separated',sum(x['relation']=='part_of_arc' for x in d['edges'])==233)
  ok(lang+': relation definitions complete',set(x['relation'] for x in d['edges'])<=set(d['relationTypes']))
  ok(lang+': exact claim denominators',d['summary']['claim_status_counts']=={'verified':49,'partially_verified':20,'disputed':2} and 'pass_rate_short' not in d['summary'])
  if lang=='ru':ok('ru: every event headline localised',all(re.search('[А-Яа-яЁё]',e['title']) for e in d['events']))
  if not skip_html:
   html=(root/('ai-power-atlas-ru.html' if lang=='ru' else 'ai-power-atlas.html')).read_text()
   m=re.search(r'<script\b[^>]*\bid="DATA"[^>]*>(.*?)</script>',html,re.S);ok(lang+': embedded JSON exact',m is not None and json.loads(m.group(1))==d)
   ok(lang+': retired scoring removed','function cyberScore(' not in html)
  report['languages'][lang]={'references':result['checked_references'],'events':len(ev),'cyber_facts':len(cyber),'curated_core':sum(e['editorial_priority']==1 for e in cyber),'thematic_edges':sum(x['relation']=='part_of_arc' for x in d['edges']),'unresolved_actor_labels':len(unresolved),'sources':len(urls)}
 r,e=data['ru'],data['en'];ok('RU/EN edge signature parity',[(x['id'],x['source'],x['target'],x['relation']) for x in r['edges']]==[(x['id'],x['source'],x['target'],x['relation']) for x in e['edges']])
 keys=['artifact_kind','normative_force','implementation_stage','primary_domain_id','cyber_domain_ids','cyber_role_ids','delegated_authority','editorial_priority','jurisdictions','actor_entities']
 ok('RU/EN classification parity',all(all(a.get(k)==b.get(k) for k in keys) for a,b in zip(r['events'],e['events'])))
 report['passed']=True;report['assertions']=len(report['tests']);(root/'review/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='tests'},ensure_ascii=False,indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--refresh-metadata',action='store_true');p.add_argument('--skip-html',action='store_true');a=p.parse_args();validate(a.root,a.refresh_metadata,a.skip_html)
