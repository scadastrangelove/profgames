#!/usr/bin/env python3
"""Replay v0.51; enforce preservation, deduplication and evidence boundaries."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from cathedral_test import baseline as v049_baseline
import migrate_cathedral as prior
import migrate_stack_refresh as release
from validate import references

def baseline(lang):
 doc=prior.migrate(v049_baseline(lang))
 doc['migrationAudit']['v050_base_sha256']=prior.BASE_HASH[lang]
 assert hashlib.sha256((json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()==release.BASE_HASH[lang]
 return doc

def main():
 report=dict(version=release.VERSION,passed=False,checks=[])
 def ok(label,condition):
  if not condition:raise AssertionError(label)
  report['checks'].append(label)
 def content(e):return {k:v for k,v in e.items() if k not in {'edgeIds','arcIds','arcFamilyIds','relationTypes'}}
 docs={}
 for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
  old=baseline(lang);d=json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text());docs[lang]=d
  expected=release.migrate(copy.deepcopy(old));expected['migrationAudit']['v051_base_sha256']=release.BASE_HASH[lang]
  ok(lang+': exact migration replay',d==expected)
  ev={e['id']:e for e in d['events']};newids={r['id'] for r in release.RECORDS}
  ok(lang+': 41 unique new events',len(ev)==510 and len(d['events'])==510 and set(ev)-{e['id'] for e in old['events']}==newids)
  ok(lang+': old event bodies retained',all(content(e)==content(ev[e['id']]) for e in old['events']))
  ok(lang+': all old semantic edges retained',all(e in d['edges'] for e in old['edges']))
  for col in ['claims','gaps','counterarguments','thesisNodes']:
   byid={x['id']:x for x in d[col]}
   ok(lang+': preserved '+col,all(content(x)==content(byid[x['id']]) for x in old[col]))
  ok(lang+': all old source IDs and URLs retained',{(s['id'],s['url']) for s in old['sourceIndex']}<={(s['id'],s['url']) for s in d['sourceIndex']})
  oldurls={release.urlkey(s['url']) for s in old['sourceIndex']};oldids={s['id'] for s in old['sourceIndex']}
  urls=[release.urlkey(s['url']) for s in d['sourceIndex'] if s['id'] not in oldids]
  ok(lang+': 59 distinct new source URLs',len(urls)==59 and len(set(urls))==59 and not oldurls & set(urls))
  newedges=[e for e in d['edges'] if e['id'].startswith('EDGE_V051_')]
  sig=lambda e:(e['source'],e['target'],e['relation'],e['arc_id'])
  ok(lang+': 117 distinct new edges',len(newedges)==117 and len({sig(e) for e in newedges})==117 and not {sig(e) for e in newedges}&{sig(e) for e in old['edges']})
  ok(lang+': memberships are not evidence',all(e['relationship_class']=='thematic' for e in newedges if e['target_kind']=='arc'))
  ok(lang+': no new arc or hanging arc',[a['id'] for a in d['arcs']]==[a['id'] for a in old['arcs']] and not d['connectivity']['computed_hanging_arcs'])
  for a in d['arcs']:
   before=next(x for x in old['arcs'] if x['id']==a['id'])
   ok(lang+': checkpoints retained '+a['id'],set(before['key_nodes'])<=set(a['key_nodes']))
   if any(a['id'] in r['arcs'] for r in release.RECORDS):
    dates=[ev[n]['date'] for n in a['key_nodes'] if n in ev]
    ok(lang+': chronological '+a['id'],dates==sorted(dates))
  vocab=d['cyberFramework']
  for r in release.RECORDS:
   e=ev[r['id']]
   ok(lang+': localized '+e['id'],all(e[k]==e[k+'_'+lang] and e[k+'_en'] and e[k+'_ru'] for k in ['title','summary','caveat','safe_wording']))
   ok(lang+': real date and precision '+e['id'],e['date']==r['date'] and e['date']<release.DATE and e['date_precision']==('month' if len(e['date'])==7 else 'day'))
   ok(lang+': existing route '+e['id'],e['story_primary_arc_id']==r['arcs'][0] and len(e['stack_layer'])>0)
   ok(lang+': sources resolve '+e['id'],all(s['url'] in {s['url'] for s in d['sourceIndex']} for s in e['sources']))
   for field,dictionary in [('artifact_kind','artifact_kinds'),('normative_force','normative_forces'),('implementation_stage','implementation_stages'),('delegated_authority','delegated_authority_states')]:
    ok(lang+': '+field+' '+e['id'],e[field] in {x['id'] for x in vocab[dictionary]})
   ok(lang+': valid contexts '+e['id'],set(e['evidence_context'])<={x['id'] for x in vocab['evidence_contexts']})
   ok(lang+': scoped AI roles '+e['id'],set(e['cyber_role_ids'])<={x['id'] for x in vocab['roles']} and not e['behavioral_status'])
   if e.get('resilience_track_ids'):
    ok(lang+': resilience vocabulary '+e['id'],e['defense_evidence_kind'] in {x['id'] for x in vocab['defense_evidence_kinds']})
    ok(lang+': reciprocal resilience membership '+e['id'],all(e['id'] in t['event_ids'] for t in vocab['resilience_tracks'] if t['id'] in e['resilience_track_ids']))
  get=lambda key:ev[release.sid(key)]
  ok(lang+': PHP follow-up merged',release.sid('PHP2SHELL_ACTIVE_EXPLOITATION') not in ev and len(get('PHP2SHELL_DISCOVERY_REMEDIATION')['sources'])==5)
  ok(lang+': unrelated Binance attribution held',release.sid('BINANCE_FBI_ATTRIBUTION') not in ev)
  ok(lang+': Debian batch counted not AI-attributed',get('DEBIAN_DSA6602_KERNEL_PATCH_BATCH')['numbers']['unique_cve_ids']==611 and not get('DEBIAN_DSA6602_KERNEL_PATCH_BATCH')['cyber_role_ids'])
  ok(lang+': OpenAI discovery explicitly defensive',get('OPENAI_KERNEL_PIPELINE')['cyber_role_ids']==['AI_ROLE_DEFENSIVE_TOOL'])
  ok(lang+': memory categories distinguished','not a substitute for DRAM or HBM' in get('YMTC_NAND_SHIPMENT_RANK')['caveat_en'] and 'not established mass output' in get('CXMT_HBM3E_LIMITED_PRODUCTION_REPORTED')['caveat_en'])
  ok(lang+': Jais lineage and incomplete code release explicit','rather than Qwen' in get('JAIS3_OPEN_ARABIC_AGENTS')['summary_en'] and 'coming soon' in get('JAIS3_OPEN_ARABIC_AGENTS')['summary_en'])
  ok(lang+': conditional Chinese catalogue',get('CHINA_AI_TECH_EXPORT_CATALOGUE')['legal_components'][0]['stage']=='consultation' and get('CHINA_AI_TECH_EXPORT_CATALOGUE')['legal_components'][1]['stage']=='effective')
  ok(lang+': regional policy not election causation',get('NEW_YORK_DC_PERMIT_MORATORIUM')['date']=='2026-07-14' and get('TEXAS_ELECTION_DC_PAUSE_PLEDGE')['normative_force']=='not_applicable')
  ok(lang+': known actor aliases reused','EuroHPC JU' not in d['entityRegistry']['actors'] and 'NCSC' not in d['entityRegistry']['actors'])
  ok(lang+': all references valid',references(d)==d['referenceIntegrity'] and d['referenceIntegrity']['valid'])
  embedded=re.search(r'<script id="DATA" type="application/json">(.*?)</script>',(ROOT/name).read_text(),re.S)
  ok(lang+': HTML data exact',embedded is not None and json.loads(embedded.group(1))==d)
  try:release.migrate(copy.deepcopy(d))
  except ValueError:rejected=True
  else:rejected=False
  ok(lang+': repeat migration rejected',rejected)
 for col in ['events','claims','claimChecks','arcs','edges','sourceIndex']:
  ok('RU/EN IDs '+col,[x['id'] for x in docs['ru'][col]]==[x['id'] for x in docs['en'][col]])
 report.update(passed=True,assertions=len(report['checks']))
 (release.PACKET/'tests-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed',report['assertions'],'targeted checks')

if __name__=='__main__':main()
