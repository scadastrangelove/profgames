#!/usr/bin/env python3
"""Replay the pinned knowledge release and check retention and evidence boundaries."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import migrate_knowledge_outcomes as release
from validate import references

BASE='5b725eda3f0066fdbd8ddaa5523f9ef05bedacfc'

def main():
 report=dict(version=release.VERSION,passed=False,checks=[])
 def ok(label,condition):
  if not condition:raise AssertionError(label)
  report['checks'].append(label)
 def content(e):return {k:v for k,v in e.items() if k not in {'edgeIds','arcIds','arcFamilyIds','relationTypes'}}
 docs={}
 for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
  raw=subprocess.check_output(['git','show',BASE+f':aipower/ai_power_storygraph_{lang}.json'],cwd=ROOT)
  ok(lang+': pinned baseline hash',hashlib.sha256(raw).hexdigest()==release.BASE_HASH[lang])
  old=json.loads(raw);d=json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text());docs[lang]=d
  ok(lang+': exact migration replay',release.migrate(copy.deepcopy(old))==d)
  ev={e['id']:e for e in d['events']};oldids={e['id'] for e in old['events']}
  added=set(d['migrationAudit']['v052_added_event_ids']);merged=set(release.MERGES.values())
  ok(lang+': 52 unique additions; 510 retained',len(added)==52 and len(ev)==562 and set(ev)-oldids==added and oldids<=set(ev))
  ok(lang+': unchanged unrelated event bodies',all(content(e)==content(ev[e['id']]) for e in old['events'] if e['id'] not in merged))
  ok(lang+': all 1314 old edges retained',len(old['edges'])==1314 and all(e in d['edges'] for e in old['edges']))
  for col in ['claims','claimChecks','gaps','counterarguments','thesisNodes']:
   byid={x['id']:x for x in d[col]}
   ok(lang+': preserved '+col,all(content(x)==content(byid[x['id']]) for x in old[col]))
  ok(lang+': original source IDs and URLs retained',{(s['id'],s['url']) for s in old['sourceIndex']}<={(s['id'],s['url']) for s in d['sourceIndex']})
  oldurls={s['url'] for s in old['sourceIndex']};urls={s['url'] for s in d['sourceIndex']}
  ok(lang+': 79 added URLs',len(urls)==818 and len(urls-oldurls)==79)
  newedges=[e for e in d['edges'] if e['id'].startswith('EDGE_V052_')]
  sig=lambda e:(e['source'],e['target'],e['relation'],e['arc_id'])
  ok(lang+': 76 distinct added edges',len(newedges)==76 and len({sig(e) for e in newedges})==76 and not {sig(e) for e in newedges}&{sig(e) for e in old['edges']})
  ok(lang+': 59 memberships are not evidence',sum(e['relation']=='part_of_arc' for e in newedges)==59 and all(e['relationship_class']=='thematic' for e in newedges if e['relation']=='part_of_arc'))
  ok(lang+': no automatic thesis confirmation',not any(e['relation'].startswith('support') for e in newedges))
  ok(lang+': no hanging arcs',not d['connectivity']['computed_hanging_arcs'])
  arcs={a['id']:a for a in d['arcs']}
  for a in old['arcs']:
   ok(lang+': checkpoints preserved '+a['id'],set(a['key_nodes'])<=set(arcs[a['id']]['key_nodes']))
  for aid,role,parent,*_ in release.ARCS:
   a=arcs[aid];dates=[ev[n]['date'] for n in a['key_nodes'] if n in ev]
   ok(lang+': chronological and connected '+aid,bool(dates) and dates==sorted(dates) and any(e['source']==aid and e['target'].startswith('THESIS_') for e in newedges))
   ok(lang+': hierarchy '+aid,a['parent_arc_id']==parent and a['display_role']==role and a['default_visible']==(not bool(parent)))
  mapping=d['researchAudit']['knowledge_outcomes']['candidate_mapping']
  ok(lang+': all 53 candidate decisions retained',len(mapping)==53 and {m['candidate_id'] for m in mapping}==set(release.ID_MAP))
  for c in release.CANDIDATES:
   e=ev[release.event_id(c)];label=lang+': '+c['id']
   ok(label+' bilingual content',all(e[k]==e[k+'_'+lang] and e[k+'_ru'] and e[k+'_en'] for k in ['title','summary','caveat','safe_wording']))
   ok(label+' research provenance',e['research_provenance']==c and e['research_track']==c['track'])
   ok(label+' dated and routed',e['date']<=release.DATE and e['story_primary_arc_id']==release.TRACK_ARCS[c['track']] and bool(e['stack_layer']))
   ok(label+' source links preserved',{s['url'] for s in c['sources']}<={s['url'] for s in e['sources']}<=urls)
   ok(label+' not a cyber incident',not e.get('primary_domain_id') and not e.get('cyber_role_ids'))
   if 'pending' in c.get('integration_status','') or 'discrepancy' in c.get('integration_status',''):
    ok(label+' limited review visible',e['status']=='partially_verified' and e['confidence']=='C')
   if c.get('geo_roles'):ok(label+' geographic roles separate',e['geo_roles']==c['geo_roles'])
  qje=ev['SIG_2023_NBER_GENAI_TACIT_KNOWLEDGE']
  ok(lang+': one QJE study with preserved historical evidence',qje['date']=='2023-04-20' and qje['research_revision_date']=='2025-02-04' and qje['numbers']['workers']==5172 and qje['numbers']['average_productivity_gain_percent_approx']==15 and bool(qje['historical_versions']) and 'SIG_2025_QJE_GENERATIVE_AI_AT_WORK' not in ev)
  faros=next(e for e in ev.values() if e.get('research_candidate_id','').endswith('FAROS_DELIVERY_REVIEW_PRESSURE'))
  ok(lang+': Faros observation is not publication',faros['date_basis']=='source_observation_not_publication' and faros['date_status']=='publication_date_unknown' and faros['publication_date'] is None)
  klarna=ev['SIG_2024_KLARNA_WORKLOAD_EQUIVALENT']
  ok(lang+': workload not layoffs','does not establish 700 layoffs' in klarna['caveat_en'])
  ok(lang+': cyber selection unchanged',sum(bool(e.get('primary_domain_id')) for e in ev.values())==252)
  ok(lang+': all references resolve',references(d)==d['referenceIntegrity'] and d['referenceIntegrity']['valid'])
  embedded=re.search(r'<script id="DATA" type="application/json">(.*?)</script>',(ROOT/name).read_text(),re.S)
  ok(lang+': exact embedded data',embedded is not None and json.loads(embedded.group(1))==d)
  try:release.migrate(copy.deepcopy(d))
  except ValueError:rejected=True
  else:rejected=False
  ok(lang+': repeat migration rejected',rejected)
 for col in ['events','claims','claimChecks','arcs','edges','sourceIndex']:
  ok('RU/EN identity parity '+col,[x['id'] for x in docs['ru'][col]]==[x['id'] for x in docs['en'][col]])
 report.update(passed=True,assertions=len(report['checks']))
 (release.PACKET/'tests-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed',report['assertions'],'knowledge integration checks')

if __name__=='__main__':main()
