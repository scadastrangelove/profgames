#!/usr/bin/env python3
"""Validate v0.39 references, data contracts, legacy preservation and embedded-data parity.
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
  if a.get('parent_arc_id'):check('arc.parent_arc_id',a['parent_arc_id'],'arc')
 for event in d['events']:
  if event.get('story_primary_arc_id'):check('event.story_primary_arc_id',event['story_primary_arc_id'],'arc')
  for x in event.get('story_secondary_arc_ids',[]):check('event.story_secondary_arc_ids',x,'arc')
 for x in d.get('arcHierarchy',{}).get('family_order',[]):check('arcHierarchy.family_order',x,'arcFamily')
 for e in d['edges']:
  for ep in ['source','target']:check('edge.'+ep,e[ep],e.get(ep+'_kind'))
  if e.get('arc_id'):check('edge.arc_id',e['arc_id'])
  if e.get('arc_family_id'):check('edge.arc_family_id',e['arc_family_id'],'arcFamily')
 for name,prefix,fields in [('claims','claim',['supporting_evidence','qualifying_evidence']),('claimChecks','claim_check',['supporting_evidence']),('counterarguments','counterargument',['evidence'])]:
  for c in d[name]:
   for field in fields:
    for x in c.get(field,[]):check(prefix+'.'+field,x)
 for c in d['countries']:
  for field in ['strongest_supporting_evidence','strongest_counter_evidence']:
   for x in c.get(field,[]):
    if x in typed or re.match(r'^(SIG_|TL_|CLM_|THESIS_|ARC_|GAP_|ca-)',str(x)):check('country.'+field,x)
 for c in d['recipes']:
  for x in c.get('recommended_filters',{}).get('hide_arc_ids',[]):check('recipe.recommended_filters.hide_arc_ids',x)
  for x in c.get('recommended_arc_ids',[]):check('recipe.recommended_arc_ids',x)
 for name,kind in REG:
  for c in d[name]:
   for field,expected in [('arcIds','arc'),('arcFamilyIds','arcFamily'),('edgeIds','edge')]:
    for x in c.get(field,[]):check(kind+'.'+field,x,expected)
 for s in d['sourceIndex']:
  for x in s.get('used_by',[]):check('source.used_by',x['id'] if isinstance(x,dict) else x)
 for track in d.get('cyberFramework',{}).get('resilience_tracks',[]):
  for event_id in track.get('event_ids',[]):check('resilience_track.event_ids',event_id,'event')
 if d.get('cyberFramework',{}).get('resilience_claim_id'):check('resilience.claim',d['cyberFramework']['resilience_claim_id'],'claim')
 return {'valid':not(bad or mismatch or dups),'checked_references':len(refs),'checked_by_field':dict(Counter(k for k,x in refs)),'unresolved_count':len(bad),'unresolved':bad,'kind_mismatch_count':len(mismatch),'kind_mismatches':mismatch,'duplicate_ids':dups}
def folded_duplicates(values):
 buckets={}
 for value in values:buckets.setdefault(value.casefold(),[]).append(value)
 return [items for items in buckets.values() if len(set(items))>1]
def referenced_source_urls(d):
 urls=set()
 for collection,_ in REG[:-1]:
  for node in d.get(collection,[]):
   for source in node.get('sources',[]):
    if isinstance(source,dict) and source.get('url'):urls.add(source['url'])
   if collection=='events' and node.get('url'):urls.add(node['url'])
 return urls
def validate(root=ROOT,refresh=False,skip_html=False):
 report={'version':'0.39','base_commit':'0e9b4cf138fb64ba94e27c684703a41d374c4378','languages':{},'tests':[]};data={}
 candidate_ids={x['id'] for x in json.loads((root/'review/v031-agent-behavior/candidates.json').read_text())['new_event_candidates']}
 concealment_ids={x['id'] for x in json.loads((root/'review/agent-concealment-persistence/candidates.json').read_text())['events']}
 astra_ids={x['id'] for x in json.loads((root/'review/astra-monitorability/candidates.json').read_text())['events']}
 anthropic_raw=json.loads((root/'review/anthropic-threat-intel-september-2026/candidates.json').read_text())
 anthropic_ids={x['id'] for x in anthropic_raw['events']}
 anthropic_track_ids={'SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION','SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY','SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING'}
 frontier_raw=json.loads((root/'review/frontier-pacing-september-2026/candidates.json').read_text())
 frontier_ids={x['id'] for x in frontier_raw['events']}
 global_raw=json.loads((root/'review/global-pacing-access-regimes/candidates.json').read_text())
 global_ids={x['id'] for x in global_raw['events']}
 war_raw=json.loads((root/'review/war-ai-operations-september-2026/candidates.json').read_text())
 war_ids={x['id'] for x in war_raw['events']}
 def ok(name,condition):
  if not condition:raise AssertionError(name)
  report['tests'].append(name)
 for lang in ['ru','en']:
  path=root/f'ai_power_storygraph_{lang}.json';d=json.loads(path.read_text());data[lang]=d;b=json.loads((root/f'review/baseline_{lang}.json').read_text())
  result=references(d);ok(lang+': all typed references resolve',result['valid'])
  if refresh:d['referenceIntegrity']=result;path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
  else:ok(lang+': reference metadata current',result['checked_references']==d['referenceIntegrity']['checked_references'])
  for field,kind in REG:
   ok(lang+': preserved '+field+' IDs',{x['id'] for x in b[field]}<={x['id'] for x in d[field]})
  oldurls={x['url'] for x in b['sourceIndex']};urls={x['url'] for x in d['sourceIndex']}
  ok(lang+': no source URL lost',oldurls<=urls);ok(lang+': no duplicate source URL',len(urls)==len(d['sourceIndex']))
  ok(lang+': every referenced source is indexed',referenced_source_urls(d)<=urls)
  dates={e['id']:e['date'] for e in d['events']}
  ok(lang+': original event dates preserved',all(dates.get(e['id'])==e['date'] for e in b['events']))
  ev={e['id']:e for e in d['events']};cyber=[e for e in d['events'] if e.get('primary_domain_id')]
  ok(lang+': exact v0.39 collection counts',len(d['events'])==394 and len(d['claims'])==73 and len(d['claimChecks'])==32 and len(d['arcs'])==26 and len(d['edges'])==941 and len(d['sourceIndex'])==583)
  hierarchy=d.get('arcHierarchy',{});arc_by_id={arc['id']:arc for arc in d['arcs']}
  expected_roles={'mechanism':13,'submechanism':1,'qualifier':1,'case':5,'sector_case':2,'timeline_lens':3,'timeline_marker':1}
  expected_parents={
   'ARC_TOLL_AND_THROTTLE':'ARC_EXPORT_CHIPS_TO_MODELS',
   'ARC_CONTROL_LEAKS_BUT_POLICES':'ARC_EXPORT_CHIPS_TO_MODELS',
   'ARC_A800_H800_WORKAROUND_CLOSURE':'ARC_EXPORT_CHIPS_TO_MODELS',
   'ARC_PALANTIR_DECISION_OS':'ARC_CORPORATE_DECISION_SUPPORT_ADOPTION',
   'ARC_FINANCE_GOVERNED_SHUTDOWN':'ARC_CORPORATE_DECISION_SUPPORT_ADOPTION',
   'ARC_WAR_DATA_FLYWHEEL':'ARC_CORPORATE_DECISION_SUPPORT_ADOPTION',
   'ARC_2023_GOVERNANCE_SHOCK':'ARC_2022_2023_FORMATION_PHASE'}
  ok(lang+': v0.39 hierarchy metadata complete',d['meta']['version']=='0.39' and hierarchy.get('version')=='1.0' and hierarchy.get('default_mode')=='mechanisms' and hierarchy.get('role_counts')==expected_roles)
  ok(lang+': hierarchy summary is exact',d['summary'].get('arc_hierarchy')=={'families':6,'core_mechanisms':13,'nested_cases_and_qualifiers':9,'timeline_records':4,'total_arc_records':26})
  ok(lang+': every arc has a presentation role and order',all(arc.get('display_role') in expected_roles and isinstance(arc.get('display_order'),int) and isinstance(arc.get('default_visible'),bool) and 'parent_arc_id' in arc for arc in d['arcs']))
  ok(lang+': nested parent map is exact',{arc['id']:arc['parent_arc_id'] for arc in d['arcs'] if arc.get('parent_arc_id')}==expected_parents)
  ok(lang+': timeline records are hidden by default',all(not arc['default_visible'] for arc in d['arcs'] if arc['display_role'] in {'timeline_lens','timeline_marker'}))
  ok(lang+': war flywheel belongs to decision family',arc_by_id['ARC_WAR_DATA_FLYWHEEL']['family_id']=='ARC_FAMILY_DECISION_DATA_FINANCE')
  audit=d['migrationAudit']['v038_arc_hierarchy']
  ok(lang+': editorial migration changes no semantic edge',audit['semantic_edge_changes']==0 and audit['removed_ids']==[])
  ok(lang+': war family metadata reassignment is explicit',audit['edge_family_metadata_reassignments']==14 and audit['arc_family_membership_recomputations']=={'events':8,'claims':3,'claimChecks':1})
  displayed=[event for event in d['events'] if event.get('story_primary_arc_id')]
  ok(lang+': one primary reading route for 354 facts',len(displayed)==354 and hierarchy.get('primary_event_assignments')==354 and hierarchy.get('events_with_secondary_arcs')==163)
  ok(lang+': reading routes contain no duplicates',all(event['story_primary_arc_id'] not in event.get('story_secondary_arc_ids',[]) and len(event.get('story_secondary_arc_ids',[]))==len(set(event.get('story_secondary_arc_ids',[]))) for event in displayed))
  ok(lang+': primary and secondary routes resolve',all(event['story_primary_arc_id'] in arc_by_id and set(event.get('story_secondary_arc_ids',[]))<=set(arc_by_id) for event in displayed))
  ok(lang+': named examples have the intended hierarchy',arc_by_id['ARC_A800_H800_WORKAROUND_CLOSURE']['display_role']=='case' and arc_by_id['ARC_TOLL_AND_THROTTLE']['display_role']=='submechanism' and arc_by_id['ARC_CONTROL_LEAKS_BUT_POLICES']['display_role']=='qualifier' and arc_by_id['ARC_CYBER_CLAIM_TO_CAVEAT']['display_role']=='mechanism')
  ok(lang+': exactly 170 reviewed cyber facts',len(cyber)==170)
  ok(lang+': exactly 106 curated cyber facts',sum(e['editorial_priority']==1 for e in cyber)==106)
  ok(lang+': all 22 candidate records present',candidate_ids<={e['id'] for e in d['events']} and len(candidate_ids)==22)
  ok(lang+': all 12 concealment records present',concealment_ids<={e['id'] for e in d['events']} and len(concealment_ids)==12)
  ok(lang+': both Astra monitorability records present',astra_ids<={e['id'] for e in d['events']} and len(astra_ids)==2)
  ok(lang+': all seven Anthropic September records present',anthropic_ids<={e['id'] for e in d['events']} and len(anthropic_ids)==7)
  ok(lang+': all five frontier-pacing records present',frontier_ids<={e['id'] for e in d['events']} and len(frontier_ids)==5)
  ok(lang+': all three global pacing records present',global_ids<={e['id'] for e in d['events']} and len(global_ids)==3)
  ok(lang+': all seven military-AI records present',war_ids<={e['id'] for e in d['events']} and len(war_ids)==7)
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
  ok(lang+': known actor aliases collapsed','Nvidia' not in actor_counts and 'US DOJ' not in actor_counts and actor_counts['NVIDIA']==14 and actor_counts['US Department of Justice']==4)
  ok(lang+': no uncategorised geography',not any(e.get('geography_unclassified') for e in d['events']))
  unresolved=[e for e in d['events'] if e.get('actor_classification_status')=='review_required']
  ok(lang+': unresolved actors exposed, not guessed',len(unresolved)==16 and all(e.get('actor_unclassified') for e in unresolved))
  aix=ev['SIG_CYBER_2025_AIXCC_FINAL'];ok(lang+': AIxCC 54/63 and 43/63',aix['numbers']['injected_bugs']==63 and aix['numbers']['synthetic_vulnerabilities_found']==54 and aix['numbers']['synthetic_vulnerabilities_patched']==43)
  kimi=ev['SIG_2026_KIMI_K3_OPEN_WEIGHT_ANNOUNCEMENT'];ok(lang+': Kimi dates separated',kimi['date']=='2026-07-16' and kimi['current_state']['observed_at']=='2026-09-05' and kimi['current_state']['event_date'] is None and kimi['current_state']['weights_public'] is True)
  behavior_vocab={k:{x['id'] for x in d['cyberFramework'][k]} for k in ['subdomains','behavioral_mechanisms','behavioral_statuses','evidence_contexts','agent_population_scopes','shared_writable_states','oversight_targets','motivation_bases','behavior_tracks','behavior_origins','concealment_targets','persistence_media','goal_sources']}
  ok(lang+': two domain-five subdomains and five mechanism groups',len(behavior_vocab['subdomains'])==2 and len(d['cyberFramework']['behavior_groups'])==5 and len(behavior_vocab['behavioral_mechanisms'])==16)
  track=d['cyberFramework']['behavior_tracks'][0]
  ok(lang+': concealment track has four authored stages',track['id']=='BEH_TRACK_CONCEALMENT_PERSISTENCE' and len(track['stages'])==4)
  for event_id in candidate_ids:
   event=ev[event_id]
   ok(lang+': complete agent-behaviour classification '+event_id,
      bool(set(event['cyber_subdomain_ids'])<=behavior_vocab['subdomains']) and
      bool(set(event['behavioral_mechanism_ids'])<=behavior_vocab['behavioral_mechanisms']) and
      bool(set(event['behavioral_status'])<=behavior_vocab['behavioral_statuses']) and
      bool(set(event['evidence_context'])<=behavior_vocab['evidence_contexts']) and
      event['agent_population_scope'] in behavior_vocab['agent_population_scopes'] and
      event['shared_writable_state'] in behavior_vocab['shared_writable_states'] and
      bool(set(event['oversight_target'])<=behavior_vocab['oversight_targets']) and
      event['motivation_basis'] in behavior_vocab['motivation_bases'] and bool(event['evidence_method']))
  for event_id in concealment_ids|astra_ids|anthropic_track_ids:
   event=ev[event_id]
   ok(lang+': complete concealment classification '+event_id,
      event['behavior_origin'] in behavior_vocab['behavior_origins'] and
      bool(set(event['concealment_targets'])<=behavior_vocab['concealment_targets']) and
      bool(set(event['persistence_media'])<=behavior_vocab['persistence_media']) and
      event['goal_source'] in behavior_vocab['goal_sources'] and
      set(event['behavior_track_ids'])=={'BEH_TRACK_CONCEALMENT_PERSISTENCE'})
  track_events=[event for event in d['events'] if 'BEH_TRACK_CONCEALMENT_PERSISTENCE' in event.get('behavior_track_ids',[])]
  ok(lang+': concealment track combines 17 reviewed and 6 comparison records',len(track_events)==23 and (concealment_ids|astra_ids|anthropic_track_ids)<={event['id'] for event in track_events})
  ok(lang+': wiki point uses first verified write date',ev['SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE']['date']=='2026-05-24')
  ok(lang+': shutdown study uses arXiv v1 date',ev['SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS']['date']=='2025-09-13')
  behavior_claim=next(c for c in d['claims'] if c['id']=='CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE')
  ok(lang+': calibrated behaviour claim remains partial',behavior_claim['status']=='partially_verified' and len(behavior_claim['qualifying_evidence'])==7)
  astra_control=ev['SIG_2026_ASTRA_COT_CONTROLLABILITY_MONITORABILITY']
  astra_evasion=ev['SIG_2026_ASTRA_PROMPTED_MONITOR_EVASION']
  ok(lang+': Astra comparison is length-banded',astra_control['numbers']['cot_token_band_min']==750 and astra_control['numbers']['cot_token_band_max']==1250 and astra_control['numbers']['astra_control_percent']==60.9 and astra_control['numbers']['sol_control_percent']==16.1)
  ok(lang+': Astra evasion remains explicitly prompted',astra_evasion['behavior_origin']=='evaluation_prompted' and astra_evasion['goal_source']=='explicit_prompt' and astra_evasion['numbers']['honeypot_full_context_recall_percent']==100)
  ok(lang+': Astra records use official sources only',all(source['url'].startswith(('https://openai.com/','https://deploymentsafety.openai.com/')) for event_id in astra_ids for source in ev[event_id]['sources']) and not any('youtube.com' in source['url'] for event_id in astra_ids for source in ev[event_id]['sources']))
  ok(lang+': thematic edges explicitly separated',sum(x['relation']=='part_of_arc' for x in d['edges'])==358)
  ok(lang+': relation definitions complete',set(x['relation'] for x in d['edges'])<=set(d['relationTypes']))
  ok(lang+': exact claim denominators',d['summary']['claim_status_counts']=={'verified':49,'partially_verified':22,'disputed':2} and 'pass_rate_short' not in d['summary'])
  if lang=='ru':ok('ru: every event headline localised',all(re.search('[А-Яа-яЁё]',e['title']) for e in d['events']))
  if not skip_html:
   html=(root/('ai-power-atlas-ru.html' if lang=='ru' else 'ai-power-atlas.html')).read_text()
   m=re.search(r'<script\b[^>]*\bid="DATA"[^>]*>(.*?)</script>',html,re.S);ok(lang+': embedded JSON exact',m is not None and json.loads(m.group(1))==d)
   ok(lang+': retired scoring removed','function cyberScore(' not in html)
   ok(lang+': behaviour layer compiled','id="behavior-map"' in html and 'id="behavior-tracks"' in html and 'function renderBehaviorLayer(' in html and 'class="block behavior-metadata"' in html)
   ok(lang+': story hierarchy UI compiled','id="toggle-arc-levels"' in html and 'id="story-hierarchy-summary"' in html and 'class="family-row"' in html and 'story_primary_arc_id' in html)
  baseline=json.loads((root/'review/resilience-throughput/baseline-manifest.json').read_text())['languages'][lang]
  raw=json.loads((root/'review/resilience-throughput/candidates.json').read_text())
  for collection,ids in baseline['ids'].items():ok(lang+': v0.33 IDs preserved '+collection,set(ids)<={n['id'] for n in d[collection]})
  ok(lang+': v0.33 event dates preserved',all(ev[id]['date']==date for id,date in baseline['dates'].items()))
  ok(lang+': v0.33 source URLs preserved',set(baseline['source_urls'])<=urls)
  ok(lang+': v0.34 candidate count and uniqueness',len(raw['events'])==15 and len({x['id'] for x in raw['events']})==15 and all(x['id'] in ev for x in raw['events']))
  tracks=d['cyberFramework']['resilience_tracks'];track_ids={x['id'] for x in tracks}
  ok(lang+': six local reading tracks, no new domain',len(track_ids)==6 and len(d['cyberFramework']['domains'])==5)
  for t in tracks:ok(lang+': track references match event tags '+t['id'],set(t['event_ids'])=={e['id'] for e in ev.values() if t['id'] in e.get('resilience_track_ids',[])})
  stage_ids={x['id'] for x in d['cyberFramework']['defense_stages']};kind_ids={x['id'] for x in d['cyberFramework']['defense_evidence_kinds']}
  for r0 in raw['events']:
   n=ev[r0['id']]
   ok(lang+': new defense classification '+n['id'],set(n['resilience_track_ids'])<=track_ids and set(n['defense_stage_ids'])<=stage_ids and n['defense_evidence_kind'] in kind_ids)
   ok(lang+': source ledger covers '+n['id'],set(r0['source_ids'])<={src['id'] for src in raw['sources']} and all(m['source_url'] in urls and m['as_of'] and m['unit'] for m in n['pipeline_metrics']))
  cvd=ev['SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG'];num=cvd['numbers'];sem=cvd['pipeline_semantics']
  ok(lang+': CVD exact reviewed subset and routes',num['firm_reviewed']==5008 and num['firm_validated']==4576 and num['total_reports_sent']==2300 and num['triaged_reports_sent']+num['direct_reports_sent']==2300 and num['upstream_fixes_known']==421)
  ok(lang+': CVD not a sequential funnel',sem['sequential_funnel'] is False and sem['acknowledged_is_validation'] is False and sem['upstream_means_fleet_deployed'] is False and sem['reviewed_subset_representative'] is False)
  ok(lang+': Linux units are patches',all(m['unit']=='patch' for m in ev['SIG_2026_LINUX_NETDEV_VALID_FIX_OVERLOAD']['pipeline_metrics']))
  ok(lang+': curl 9 plus separate wcurl 1',ev['SIG_2026_CURL_822_SECURITY_RELEASE']['numbers']=={'curl_libcurl_security_fixes':9,'wcurl_separate_cves':1})
  ok(lang+': curl pause event date differs from announcement',ev['SIG_2026_CURL_REPORTING_PAUSE']['date']=='2026-07-01' and ev['SIG_2026_CURL_REPORTING_PAUSE']['source_date']=='2026-06-15')
  ok(lang+': SAFE remains a nonbinding draft',ev['SIG_2026_SAFE_INCIDENT_LEARNING_RFC']['implementation_stage']=='draft' and ev['SIG_2026_SAFE_INCIDENT_LEARNING_RFC']['normative_force']=='not_applicable')
  ok(lang+': Daybreak not cash disbursed',ev['SIG_2026_DAYBREAK_FRONTLINE_SUBSIDIZED_ACCESS']['money_status']=='announced_in_kind_subsidy_not_cash_disbursed')
  ok(lang+': Watershed launch precedes publication',ev['SIG_2026_PROJECT_WATERSHED_250_PILOT']['date']=='2026-08-31' and ev['SIG_2026_PROJECT_WATERSHED_250_PILOT']['source_date']=='2026-09-01')
  factory=ev['SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION']
  ok(lang+': undated Defense Factory uses observation',factory['date']=='2026-09-06' and factory['event_date'] is None and factory['source_date']=='' and factory['date_basis']=='observation_date_publication_unknown')
  rust=ev['SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES']
  ok(lang+': rust historical numbers not overwritten',rust['numbers']==baseline['rust_numbers'] and rust['numbers']['fixes_merged_or_resolved']==33)
  ok(lang+': rust observation is bounded',rust['current_state']['reporter_claimed_resolved']==37 and rust['current_state']['individually_checked_upstream_examples']==2 and rust['current_state']['aggregate_recount_performed'] is False)
  claim=next(x for x in d['claims'] if x['id']=='CLM_VALID_FINDINGS_MAINTENANCE_CAPACITY')
  ok(lang+': throughput claim remains scoped partial',claim['status']=='partially_verified' and len(claim['supporting_evidence'])==7 and len(claim['qualifying_evidence'])==3)
  newedges=[x for x in d['edges'] if x['id'] in d['migrationAudit']['v034_added_edge_ids']]
  ok(lang+': 45 explicit links, 15 thematic memberships',len(newedges)==45 and sum(x['relation']=='part_of_arc' for x in newedges)==15 and all(x['relationship_class']=='thematic' for x in newedges if x['relation']=='part_of_arc'))
  if not skip_html:ok(lang+': new resilience UI compiled','id="resilience-section"' in html and 'function renderResilienceLayer(' in html and 'function resilienceMetadata(' in html)
  source_by_id={source['id']:source for source in anthropic_raw['sources']}
  source_urls={source_id:source['url'] for source_id,source in source_by_id.items()}
  for candidate in anthropic_raw['events']:
   event=ev[candidate['id']]
   ok(lang+': v0.35 source ledger covers '+candidate['id'],{source_urls[source_id] for source_id in candidate['source_ids']}<={source['url'] for source in event['sources']})
   ok(lang+': v0.35 complete cyber classification '+candidate['id'],
      event['primary_domain_id'] in event['cyber_domain_ids'] and
      set(event['cyber_subdomain_ids'])<=behavior_vocab['subdomains'] and
      set(event['behavioral_mechanism_ids'])<=behavior_vocab['behavioral_mechanisms'] and
      set(event['behavioral_status'])<=behavior_vocab['behavioral_statuses'] and
      set(event['evidence_context'])<=behavior_vocab['evidence_contexts'] and
      event['agent_population_scope'] in behavior_vocab['agent_population_scopes'] and
      event['shared_writable_state'] in behavior_vocab['shared_writable_states'] and
      set(event['oversight_target'])<=behavior_vocab['oversight_targets'] and
      event['motivation_basis'] in behavior_vocab['motivation_bases'] and
      event['behavior_origin'] in behavior_vocab['behavior_origins'] and
      set(event['concealment_targets'])<=behavior_vocab['concealment_targets'] and
      set(event['persistence_media'])<=behavior_vocab['persistence_media'] and
      event['goal_source'] in behavior_vocab['goal_sources'])
  meta_gate=ev['SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE']
  ok(lang+': provider gate keeps selected-case caveat',('не считает их типичной выборкой' in meta_gate['caveat_ru']) and ('not typical misuse' in meta_gate['caveat_en']))
  ok(lang+': analytical frame is not factual corroboration',any(source['url']==source_urls['S06'] and source['primary_or_secondary']=='analytical_frame' for source in meta_gate['sources']))
  gtg10007=ev['SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY']
  ok(lang+': possible zero-days remain unvalidated',gtg10007['numbers']['possible_zero_days_in_one_month_gt']==12 and 'not independently validated CVEs' in gtg10007['caveat_en'])
  gtg20006=ev['SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION']
  ok(lang+': GTG-20006 has bounded external corroboration',source_urls['S02'] in {source['url'] for source in gtg20006['sources']} and 'rebuild loop is disclosed by Anthropic' in gtg20006['caveat_en'])
  dispute=ev['SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE']
  ok(lang+': U.S. and China positions remain paired',all(source_urls[source_id] in {source['url'] for source in dispute['sources']} for source_id in ['S04','S05']) and dispute['numbers']['official_positions']==2)
  distillation=ev['SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE']
  ok(lang+': February distillation numbers and date preserved',distillation['date']=='2026-02-23' and distillation['numbers']=={'attributed_accounts_approx':24000,'interactions_more_than':16000000})
  ok(lang+': September distillation state is a separate observation',distillation['current_state']['observed_at']=='2026-09-10' and distillation['current_state']['event_date'] is None and distillation['current_state']['numbers']['alibaba_exchanges_gt']==151000000)
  gate_claim=next(item for item in d['claimChecks'] if item['id']=='CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE')
  ok(lang+': provider observability claim remains scoped partial',gate_claim['status']=='partially_verified' and gate_claim['confidence']=='B' and len(gate_claim['supporting_evidence'])==3 and len(gate_claim['qualifying_evidence'])==1)
  v035edges=[edge for edge in d['edges'] if edge['id'] in d['migrationAudit']['v035_added_edge_ids']]
  ok(lang+': 39 v0.35 links include 21 thematic memberships',len(v035edges)==39 and sum(edge['relation']=='part_of_arc' for edge in v035edges)==21 and all(edge['relationship_class']=='thematic' for edge in v035edges if edge['relation']=='part_of_arc'))
  ok(lang+': observability claim reaches arcs and thesis nodes',set(gate_claim['arcIds'])>={'ARC_QUIET_ACCESS_CONTROL','ARC_SOVEREIGN_FLOW_GATING','ARC_COGSEC_LAB_TO_WILD_TO_STATE'} and {'THESIS_ACCESS_AS_POWER','THESIS_CORE'}<={edge['target'] for edge in v035edges if edge['source']==gate_claim['id']})
  if lang=='ru':ok('ru: v0.35 authored labels localised',all(re.search('[А-Яа-яЁё]',ev[event_id]['title']) for event_id in anthropic_ids) and all(re.search('[А-Яа-яЁё]',next(item for item in d['claimChecks'] if item['id']==claim_id)['title']) for claim_id in ['CLM_006_MACHINE_SPEED_CYBER','CLM_007_COGNITIVE_SECURITY','CLM_013_QUIET_ACCESS_CONTROL','CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE']))
  frontier_sources={source['id']:source['url'] for source in frontier_raw['sources']}
  for candidate in frontier_raw['events']:
   event=ev[candidate['id']]
   ok(lang+': v0.36 source ledger covers '+candidate['id'],{frontier_sources[source_id] for source_id in candidate['source_ids']}<={source['url'] for source in event['sources']})
  speed=ev['SIG_2026_DOW_AI_STRATEGY_SPEED_WINS'];continuity=ev['SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL']
  proposal=ev['SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL'];endorsements=ev['SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS'];response=ev['SIG_2026_TRUMP_REJECTS_FRONTIER_PACING']
  ok(lang+': binding directives separated from proposals and rhetoric',speed['normative_force']=='binding' and continuity['normative_force']=='binding' and proposal['normative_force']=='advisory' and endorsements['normative_force']=='not_applicable' and response['normative_force']=='not_applicable')
  ok(lang+': frontier artifacts preserve distinct evidence types',speed['artifact_kind']=='strategy' and continuity['artifact_kind']=='memorandum' and proposal['artifact_kind']=='policy_framework' and endorsements['artifact_kind']=='commentary' and response['artifact_kind']=='political_declaration')
  ok(lang+': Amodei forecast remains a forecast',proposal['numbers']['internet_takeover_risk_forecast_months_min']==6 and proposal['numbers']['internet_takeover_risk_forecast_months_max']==12 and ('risk forecast' in proposal['caveat_en']))
  pacing=next(item for item in d['claimChecks'] if item['id']=='CLM_031_FRONTIER_PACING_AUTHORITY')
  ok(lang+': pacing claim remains scoped partial',pacing['status']=='partially_verified' and pacing['confidence']=='A/B' and len(pacing['supporting_evidence'])==14 and pacing['qualifying_evidence']==['export-14'])
  pacing_arc=next(item for item in d['arcs'] if item['id']=='ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL')
  expected_order=['SIG_2023_CHINA_GENAI_INTERIM_MEASURES','SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS','SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS','SIG_2026_DOW_AI_STRATEGY_SPEED_WINS','SIG_2026_KOREA_NAVER_SOVEREIGN_MODEL_EXCLUSION','SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS','SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE','SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL','export-13','SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL','SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE','SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE','export-14','SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL','SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS','SIG_2026_TRUMP_REJECTS_FRONTIER_PACING','CLM_031_FRONTIER_PACING_AUTHORITY']
  ok(lang+': pacing arc follows global event chronology',pacing_arc['key_nodes']==expected_order and pacing_arc['start_date']=='2023-07-13' and pacing_arc['end_date']=='2026-09-14')
  v036edges=[edge for edge in d['edges'] if edge['id'] in d['migrationAudit']['v036_added_edge_ids']]
  ok(lang+': 35 v0.36 links include 17 thematic memberships',len(v036edges)==35 and sum(edge['relation']=='part_of_arc' for edge in v036edges)==17 and all(edge['relationship_class']=='thematic' for edge in v036edges if edge['relation']=='part_of_arc'))
  pacing_targets={edge['target'] for edge in v036edges if edge['source']==pacing['id']}
  ok(lang+': pacing claim reaches arc and three thesis nodes','ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL' in pacing_targets and {'THESIS_ACCESS_AS_POWER','THESIS_DECISION_SOVEREIGNTY','THESIS_CORE'}<=pacing_targets)
  decision=next(item for item in d['claimChecks'] if item['id']=='CLM_026_DECISION_SOVEREIGNTY_MITIGATION')
  resilience_claim=next(item for item in d['claimChecks'] if item['id']=='CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK')
  ok(lang+': continuity directive updates decision sovereignty','SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL' in decision['supporting_evidence'] and decision['confidence']=='A/B')
  ok(lang+': pacing extends resilience without one standard','SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL' in resilience_claim['supporting_evidence'] and 'not one standard' in resilience_claim['claim_en'])
  global_sources={source['id']:source['url'] for source in global_raw['sources']}
  for candidate in global_raw['events']:
   event=ev[candidate['id']]
   ok(lang+': v0.37 source ledger covers '+candidate['id'],{global_sources[source_id] for source_id in candidate['source_ids']}<={source['url'] for source in event['sources']})
  seoul=ev['SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS'];aisi=ev['SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS'];filing=ev['SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE']
  ok(lang+': Seoul remains voluntary and bounded',seoul['normative_force']=='advisory' and seoul['numbers']=={'initial_signatories':16,'later_additional_signatories':4,'listed_signatories_after_update':20} and 'government release licence' in seoul['caveat_en'])
  ok(lang+': AISI access has no invented veto',aisi['implementation_stage']=='observed' and aisi['delegated_authority']=='evaluated' and 'not a general state power to delay release' in aisi['caveat_en'])
  ok(lang+': China filing counts and scope preserved',filing['normative_force']=='binding' and filing['numbers']['cumulative_services_by_2026_04_30']==868 and filing['numbers']['cumulative_apps_features_by_2026_04_30']==530 and 'does not establish general control over frontier-model training pace' in filing['caveat_en'])
  v037edges=[edge for edge in d['edges'] if edge['id'] in d['migrationAudit']['v037_added_edge_ids']]
  ok(lang+': 31 v0.37 links include 16 thematic memberships',len(v037edges)==31 and sum(edge['relation']=='part_of_arc' for edge in v037edges)==16 and all(edge['relationship_class']=='thematic' for edge in v037edges if edge['relation']=='part_of_arc'))
  ok(lang+': five existing non-US records join pacing arc',set(['SIG_2023_CHINA_GENAI_INTERIM_MEASURES','SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS','SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE','SIG_2026_KOREA_NAVER_SOVEREIGN_MODEL_EXCLUSION','SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL'])<=set(pacing['supporting_evidence']))
  war_sources={source['id']:source['url'] for source in war_raw['sources']}
  for candidate in war_raw['events']:
   event=ev[candidate['id']]
   ok(lang+': v0.39 source ledger covers '+candidate['id'],{war_sources[source_id] for source_id in candidate['source_ids']}<={source['url'] for source in event['sources']})
  maven=ev['SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE'];odin=ev['SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING']
  avengers=ev['SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS'];partnership=ev['SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP']
  talon=ev['SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT'];gtg27005=ev['SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT'];gtg30005=ev['SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE']
  ok(lang+': Maven campaign total is not autonomous-decision count',maven['numbers']['campaign_targets_reported']==13000 and 'autonom' in maven['safe_wording_en'].lower() and 'do not disclose Maven' in maven['caveat_en'])
  ok(lang+': ODIN is effective internal reporting authority',odin['normative_force']=='binding' and odin['implementation_stage']=='effective' and odin['story_primary_arc_id']=='ARC_PALANTIR_DECISION_OS')
  ok(lang+': Avengers separates access facts from reported metrics',avengers['normative_force']=='contractual' and avengers['numbers']['annotated_frames']==5000000 and avengers['numbers']['reported_target_detection_percent']==70 and 'ministry-reported metrics' in avengers['safe_wording_en'])
  ok(lang+': UK-Ukraine partnership preserves nonbinding caveat',partnership['normative_force']=='advisory' and 'not legally binding' in partnership['caveat_en'])
  ok(lang+': Talon remains announced rather than launched',talon['implementation_stage']=='announced' and 'do not confirm launch' in talon['caveat_en'])
  ok(lang+': GTG-27005 remains development not field deployment',gtg27005['delegated_authority']=='evaluated' and gtg27005['numbers']['reported_maturity']=='TRL 3-4' and 'state entity' in gtg27005['caveat_en'])
  ok(lang+': GTG-30005 remains human-directed reconnaissance',gtg30005['delegated_authority']=='observed' and gtg30005['cyber_role_ids']==['AI_ROLE_ATTACK_ENABLER'] and 'human-directed' in gtg30005['safe_wording_en'])
  v039edges=[edge for edge in d['edges'] if edge['id'] in d['migrationAudit']['v039_added_edge_ids']]
  ok(lang+': 46 v0.39 links include 20 thematic memberships',len(v039edges)==46 and sum(edge['relation']=='part_of_arc' for edge in v039edges)==20 and all(edge['relationship_class']=='thematic' for edge in v039edges if edge['relation']=='part_of_arc'))
  ok(lang+': no autonomous field action inferred',not d['factcheckAudit']['v039_war_ai_operations']['autonomous_field_action_inferred'] and len(war_raw['deferred'])==6)
  if lang=='ru':
   ok('ru: v0.39 authored labels localised',all(re.search('[А-Яа-яЁё]',ev[event_id]['title']) for event_id in frontier_ids|global_ids|war_ids) and re.search('[А-Яа-яЁё]',pacing['title']) is not None)
   ok('ru: pacing arc has no stray English workflow phrases',all(term not in pacing_arc['thesis_ru']+' '.join(pacing_arc['counterpoints_ru']) for term in ['release-checkpoints','training runs']))
  report['languages'][lang]={'references':result['checked_references'],'events':len(ev),'cyber_facts':len(cyber),'curated_core':sum(e['editorial_priority']==1 for e in cyber),'thematic_edges':sum(x['relation']=='part_of_arc' for x in d['edges']),'unresolved_actor_labels':len(unresolved),'sources':len(urls)}
 r,e=data['ru'],data['en'];ok('RU/EN edge signature parity',[(x['id'],x['source'],x['target'],x['relation']) for x in r['edges']]==[(x['id'],x['source'],x['target'],x['relation']) for x in e['edges']])
 keys=['id','resilience_track_ids','defense_evidence_kind','defense_stage_ids','pipeline_metrics','pipeline_semantics','artifact_kind','normative_force','implementation_stage','primary_domain_id','cyber_domain_ids','cyber_role_ids','delegated_authority','editorial_priority','jurisdictions','actor_entities','cyber_subdomain_ids','behavioral_mechanism_ids','behavioral_status','evidence_context','evidence_method','agent_population_scope','shared_writable_state','oversight_target','motivation_basis','behavior_track_ids','behavior_origin','concealment_targets','persistence_media','goal_source']
 ok('RU/EN classification parity',all(all(a.get(k)==b.get(k) for k in keys) for a,b in zip(r['events'],e['events'])))
 ok('RU/EN new track and source index parity',r['cyberFramework']['resilience_tracks']==e['cyberFramework']['resilience_tracks'] and [(s['id'],s['url']) for s in r['sourceIndex']]==[(s['id'],s['url']) for s in e['sourceIndex']])
 ok('RU/EN v0.35 current-state parity',next(x for x in r['events'] if x['id']=='SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE')['current_state']['numbers']==next(x for x in e['events'] if x['id']=='SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE')['current_state']['numbers'])
 ok('RU/EN v0.36 frontier signature parity',[(x['id'],x['date'],x['artifact_kind'],x['normative_force']) for x in r['events'] if x['id'] in frontier_ids]==[(x['id'],x['date'],x['artifact_kind'],x['normative_force']) for x in e['events'] if x['id'] in frontier_ids])
 ok('RU/EN v0.37 global signature parity',[(x['id'],x['date'],x['artifact_kind'],x['normative_force']) for x in r['events'] if x['id'] in global_ids]==[(x['id'],x['date'],x['artifact_kind'],x['normative_force']) for x in e['events'] if x['id'] in global_ids])
 ok('RU/EN v0.39 military-AI signature parity',[(x['id'],x['date'],x['artifact_kind'],x['normative_force'],x['story_primary_arc_id']) for x in r['events'] if x['id'] in war_ids]==[(x['id'],x['date'],x['artifact_kind'],x['normative_force'],x['story_primary_arc_id']) for x in e['events'] if x['id'] in war_ids])
 ok('RU/EN hierarchy parity',r['arcHierarchy']==e['arcHierarchy'] and [(x['id'],x['family_id'],x['display_role'],x['display_order'],x['parent_arc_id'],x['default_visible']) for x in r['arcs']]==[(x['id'],x['family_id'],x['display_role'],x['display_order'],x['parent_arc_id'],x['default_visible']) for x in e['arcs']] and [(x['id'],x.get('story_primary_arc_id'),x.get('story_secondary_arc_ids',[])) for x in r['events']]==[(x['id'],x.get('story_primary_arc_id'),x.get('story_secondary_arc_ids',[])) for x in e['events']])
 index=(root/'index.html').read_text();readme=(root/'README.md').read_text()
 ok('index: current release marker','AI Power Atlas · v0.39' in index and 'AI POWER ATLAS · V0.39' in index)
 ok('index: current collection counts',all(x in index for x in ['394 события','73 тезиса','32 проверки тезисов','26 сюжетных арок','941 связь','170 записей','106 опорных']))
 ok('index: bilingual atlas and current schema links',all(x in index for x in ['href="ai-power-atlas-ru.html"','href="ai-power-atlas.html"','href="SCHEMA_v038.md"']))
 ok('README: current release summary','# AI Power Atlas — v0.39' in readme and '394 события, 73 тезиса и 32 проверяемых утверждения' in readme and '`SCHEMA_v038.md`' in readme)
 report['passed']=True;report['assertions']=len(report['tests']);(root/'review/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='tests'},ensure_ascii=False,indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--refresh-metadata',action='store_true');p.add_argument('--skip-html',action='store_true');a=p.parse_args();validate(a.root,a.refresh_metadata,a.skip_html)
