#!/usr/bin/env python3
"""Pinned v0.51 -> v0.52: science, medicine, work and learning, with study-family dedup."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import event_record, pair, add_source
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/science-medicine-work-2026-11-07'
DATE, VERSION = '2026-11-07', '0.52'
BASE_HASH = {'ru':'6e59265525ba0e2e3871843221b81c07daed3ac2cc98852ef9e68c8251888863',
             'en':'43e01a8ae286c5a0d3d0551c431874bfcd35403ed36c96effad95698befca9db'}
KNOW = 'ARC_KNOWLEDGE_PRODUCTION_VALIDATION'
MED = 'ARC_MEDICAL_AI_TRANSLATION'
WORK = 'ARC_WORK_COMPETENCE_DISTRIBUTION'
EDU = 'ARC_EDUCATION_COMPETENCE'
DATA = 'ARC_DATA_LICENSING_AS_INPUT_LAYER'
CORP = 'ARC_CORPORATE_DECISION_SUPPORT_ADOPTION'
FAMILY = 'ARC_FAMILY_DECISION_DATA_FINANCE'
TRACK_ARCS = {'science':KNOW,'medicine':MED,'work':WORK,'education':EDU}
MERGES = {'WORK_CAND_2025_QJE_GENERATIVE_AI_AT_WORK':'SIG_2023_NBER_GENAI_TACIT_KNOWLEDGE'}
REUSED_IDS = {'MED_CAND_2026_JAMA_SCRIBE_WORKFLOW':'SIG_2026_JAMA_AMBIENT_AI_SCRIBE_WORKFLOW',
 'MED_CAND_2025_THERABOT_TRIAL':'SIG_2025_DARTMOUTH_THERABOT_RCT',
 'WORK_CAND_2026_NBER_FIRM_DATA':'SIG_2026_NBER_FIRM_DATA_AI_EXPECTATIONS_GAP'}
ACTORS = {
 'ALPHAFOLD_DATABASE_ACCESS':['Google DeepMind','EMBL-EBI'],
 'ALPHAFOLD3_ACADEMIC_RELEASE':['Google DeepMind'], 'ALPHAPROOF_IMO':['Google DeepMind'],
 'ALPHAEVOLVE_ALGORITHMS':['Google DeepMind'], 'MATTERGEN_SYNTHESIS':['Microsoft Research'],
 'ALETHEIA_RESEARCH_AGENT':['Google DeepMind'], 'GOOGLE_WETLAB_AGENTS':['Google Research'],
 'OPENAI_SCIENTIFIC_RELEASE_GOVERNANCE':['OpenAI'], 'AI_INFOCARE_PATIENT_SUMMARIES':['TU Dresden'],
 'THERABOT_TRIAL':['Dartmouth College'], 'STANFORD_CANARIES_UPDATE':['Stanford Digital Economy Lab'],
 'ILO_TASK_EXPOSURE':['International Labour Organization','NASK'],
 'NBER_FIRM_DATA':['National Bureau of Economic Research'],
 'EXOMINER_301_VALIDATIONS':['NASA'], 'EXOMINER_PLUS_TESS_CANDIDATES':['NASA'],
 'HUBBLE_ANOMALYMATCH_ARCHIVE':['ESA'], 'ITHACA_EPIGRAPHY':['Google DeepMind'],
 'AENEAS_CONTEXTUALIZATION':['Google DeepMind'],
 'VESUVIUS_FIRST_PASSAGES':['Vesuvius Challenge'], 'VESUVIUS_PHERC1667':['Vesuvius Challenge'],
 'STRONGDM_VALIDATION_ENVIRONMENT':['StrongDM'], 'OPENAI_HARNESS_ENGINEERING':['OpenAI'],
 'FAROS_DELIVERY_REVIEW_PRESSURE':['Faros AI'], 'METR_PRODUCTIVITY_RCT':['METR'],
 'METR_PRODUCTIVITY_SELECTION_UPDATE':['METR'], 'KLARNA_WORKLOAD_EQUIVALENT':['Klarna'],
}
ACTOR_ALIASES = {'DeepMind':'Google DeepMind','University of Chicago':'University of Chicago',
 'ECMWF':'ECMWF','USTC and collaborating Chinese institutions':'University of Science and Technology of China',
 'World Bank research team':'World Bank','University of Pennsylvania research team':'University of Pennsylvania'}
COUNTRY = {'US':'US','GB':'UK','CN':'China','CH':'Switzerland','KR':'South Korea','SA':'Saudi Arabia',
 'AU':'Australia','RU':'Russia','DE':'Germany','NO':'Norway','AT':'Austria','BR':'Brazil','JP':'Japan','NG':'Nigeria','TR':'Turkey','IL':'Israel','IN':'India'}
ARCS = [
 (KNOW,'mechanism','',30,('Производство знания: модели, данные и проверка','Knowledge production: models, data and validation'),
  ('ИИ расширяет поиск, моделирование и повторное чтение архивов. Получение кандидата, независимая проверка и практическое применение требуют разных ресурсов. Открытые данные могут расширять доступ, а концентрация моделей и установок может его ограничивать.',
   'AI expands search, modelling and archive reanalysis. Candidate generation, independent validation and practical use require different resources. Open data can widen access, while concentrated models and facilities may constrain it.'),
  ('Научный результат не доказывает ни монополию, ни национальную независимость. Различать вычислительное предсказание, физическую проверку и общественный эффект.',
   'A scientific result establishes neither monopoly nor national independence. Separate computational prediction, physical validation and societal effects.')),
 (MED,'sector_case',KNOW,31,('Медицина: от модели к результату для пациента','Medicine: from models to patient outcomes'),
  ('Клинические исследования показывают положительные, нулевые и неодинаковые эффекты. Доступность обследования, симптомы, рабочее время врача и исход лечения являются разными результатами.',
   'Clinical studies show positive, null and heterogeneous effects. Screening access, symptoms, clinician time and treatment outcomes are distinct results.'),
  ('Тест модели не заменяет клиническое испытание. Ранняя фаза не означает одобренное лечение; удобство работы не доказывает снижение смертности.',
   'A model benchmark does not replace a clinical trial. Early phases do not establish approved treatment; workflow convenience does not establish reduced mortality.')),
 (WORK,'sector_case',CORP,25,('Труд: производительность, найм и проверка','Work: productivity, hiring and verification'),
  ('ИИ меняет задачи и организацию проверки. Производительность, занятость, найм новичков, зарплаты и распределение доходов измеряются отдельно. Самоотчёты компаний и результаты экспериментов имеют разную доказательную силу.',
   'AI changes tasks and verification work. Productivity, employment, entry-level hiring, wages and income distribution are measured separately. Company self-reports and experiments have different evidentiary strength.'),
  ('Эквивалент объёма работы не равен числу увольнений. Подверженность задач автоматизации не является прогнозом потери рабочих мест.',
   'Workload equivalents are not layoff counts. Task exposure to automation is not a forecast of job losses.')),
 (EDU,'sector_case',KNOW,32,('Обучение: ответы и самостоятельная компетенция','Learning: answers and independent competence'),
  ('Доступ к ответу может улучшать выполнение задания, не улучшая самостоятельный результат. Эффект зависит от педагогики, роли учителя и условий проверки без помощника.',
   'Access to answers can improve task completion without improving unaided performance. Effects depend on pedagogy, teacher involvement and testing without assistance.'),
  ('Исследования разных стран не являются соревнованием национальных моделей. Различаются предметы, участники, контрольные условия и длительность.',
   'Studies in different countries are not a competition between national models. Subjects, participants, controls and duration differ.')),
]

def load_candidates():
 pack=json.loads((PACKET/'candidates.json').read_text())
 result=copy.deepcopy(pack['candidates'])
 pult=json.loads((ROOT/'review/pult-software-production/candidates.json').read_text())
 wanted={r['id'] for r in pack['reuse_candidates']}
 for c in pult['candidates']:
  if c['id'] not in wanted: continue
  c=copy.deepcopy(c);c.update(track='work',stack_layers=['decision_support_cognition'],
   integration_status=c['review_status'],outcome_stage='engineering_workflow',prior_record_refs=[])
  c['mechanism_ru']='Организация проверки и среды исполнения влияет на результат; трудовые последствия требуют отдельных измерений.'
  c['mechanism_en']='Verification and execution environments shape outcomes; labour effects require separate measurement.'
  if c['date'] is None:
   c.update(publication_date=None,date=c['observed_at'],date_kind='source_observation_not_publication')
   c['title_ru']='Faros: наблюдение отчёта о нагрузке на проверку кода'
   c['title_en']='Faros: observation of a report on code-review pressure'
   c['caveat_ru']='Дата на шкале обозначает наблюдение страницы 27 сентября, не выпуск отчёта или период измерения. '+c['caveat_ru']
   c['caveat_en']='The timeline date is the September 27 page observation, not publication or measurement. '+c['caveat_en']
  result.append(c)
 # The correction is imported as an attributed workload claim, not as a layoff fact.
 result.append(dict(id='WORK_CAND_2024_KLARNA_WORKLOAD_EQUIVALENT',date='2024-02-28',date_kind='reporting_date',track='work',
  title_ru='Klarna: заявленный эквивалент работы 700 сотрудников поддержки',title_en='Klarna reports a 700-support-worker workload equivalent',
  summary_ru='По сообщению Reuters, Klarna заявила, что помощник обрабатывает две трети обращений в чат и объём работы, эквивалентный примерно 700 сотрудникам. Это заявление компании об автоматизации задач.',
  summary_en='Reuters reported Klarna saying its assistant handled two-thirds of service chats and work equivalent to roughly 700 employees. This is a company claim about task automation.',
  caveat_ru='Эквивалент объёма работы не устанавливает 700 увольнений. Из сообщения нельзя определить распределение результата между штатом, подрядчиками, ростом спроса и изменением качества.',
  caveat_en='A workload equivalent does not establish 700 layoffs. The report does not resolve effects on staff, contractors, demand growth or service quality.',
  sources=[dict(url='https://www.reuters.com/technology/teleperformance-shares-plunge-ai-disruption-concerns-2024-02-28/',publisher='Reuters',type='secondary',access='existing_reviewed_companion_record')],
  geography=['Sweden','Global'],stack_layers=['decision_support_cognition'],evidence_kind='reported_company_workload_claim',outcome_stage='reported_workload_equivalent',
  integration_status='reuse_with_correction',prior_record_refs=[dict(file='profgames_ai_signals.jsonl',id='SIG_2024_KLARNA_700_AGENT_EQUIVALENT')],related_existing_event_ids=[],
  proposed_arc_ids=[CORP],mechanism_ru='Автоматизация задачи и изменение занятости должны измеряться раздельно.',mechanism_en='Task automation and employment changes must be measured separately.'))
 return result

CANDIDATES=load_candidates()
def event_id(c):
 if c['id'] in MERGES:return MERGES[c['id']]
 return REUSED_IDS.get(c['id'],'SIG_'+c['id'].split('_CAND_',1)[1])
ID_MAP={c['id']:event_id(c) for c in CANDIDATES}

def migrate(doc):
 if doc['meta']['version']!='0.51':raise ValueError('Expected reviewed v0.51; repeated migration rejected')
 old=copy.deepcopy(doc);lang=doc['language'];ev={x['id']:x for x in doc['events']};arcs={a['id']:a for a in doc['arcs']}
 for aid,role,parent,order,title,thesis,safe in ARCS:
  a=dict(id=aid,kind='arc',arc_type='knowledge_and_institutional_outcomes',status='scoped_mixed_evidence',
   family_id=FAMILY,arc_kind=role,parent_arc_id=parent,display_role=role,display_order=order,default_visible=not bool(parent),
   start_date=DATE,end_date='2021-01-01',visual_lanes=['data_telemetry','model_weights','decision_support_cognition'],key_nodes=[],edgeIds=[],arcIds=[aid],arcFamilyIds=[FAMILY],relationTypes=[])
  for key,values in [('title',title),('thesis',thesis),('safe_wording',safe),('counterpoints',([safe[0]],[safe[1]]))]:pair(a,key,*values,lang)
  doc['arcs'].append(a);arcs[aid]=a
 aliases={x.casefold():x for x in doc['entityRegistry']['actors']}
 newids=[];mapping=[]
 for c in CANDIDATES:
  eid=event_id(c);primary=TRACK_ARCS[c['track']]
  # Retain only explicit access or deployment routes, not every old catch-all proposal.
  secondary=[a for a in c.get('proposed_arc_ids',[]) if a not in {DATA,CORP,'ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK'}]
  if c['id'].endswith(('ALPHAFOLD_DATABASE_ACCESS','ALPHAFOLD3_ACADEMIC_RELEASE','OPENAI_SCIENTIFIC_RELEASE_GOVERNANCE')):secondary.append(DATA)
  routes=uniq([primary]+secondary)
  actors=next((v for k,v in ACTORS.items() if c['id'].endswith(k)),c.get('geo_roles',{}).get('developer_organizations',[]))
  actors=[ACTOR_ALIASES.get(x,x) for x in actors if not any(t in x.lower() for t in ['collaborator','partners','participating','school'])]
  actors=uniq(aliases.setdefault(x.casefold(),x) for x in actors)
  geo=c.get('geography',[]);sources={}
  for i,s in enumerate(c['sources']):
   secondary_source=s.get('type')=='secondary'
   sources[str(i)]=dict(name=s['publisher'],title=s['publisher'],url=s['url'],date=s.get('published_at') or '',
    source_class=c['evidence_kind'],type='Media / report' if secondary_source else 'Research / technical',
    primary_or_secondary='secondary' if secondary_source else 'primary',checked_at=s.get('checked_at','2026-09-27' if c['id'].startswith('PULT') else DATE),
    verification_method='reviewed_source_account_not_independent_replication',access=s.get('access','primary_page_reviewed'))
  pending='pending' in c.get('integration_status','') or 'discrepancy' in c.get('integration_status','')
  raw=dict(id=eid,date=c['date'],date_basis=c['date_kind'],date_status='publication_date_unknown' if c.get('date_kind')=='source_observation_not_publication' else 'source_backed',
   source_ids=list(sources),actors=actors,actor_types=[],jurisdictions=geo,contexts=['ecosystem_measurement'],
   method=c['evidence_kind'],stack_layers=c['stack_layers'],structures=['knowledge','production'],research_questions=[],numbers=c.get('numbers',{}),
   confidence='C' if pending else 'B',status='partially_verified' if pending else 'verified_as_reported',domains=[],roles=[],primary_domain=None,
   artifact='research',force='not_applicable',stage='published',delegation='not_applicable',priority=2,arcs=routes)
  for k in ['title','summary','caveat']:
   for l in ['ru','en']:raw[k+'_'+l]=c[k+'_'+l]
  if c['id']=='MED_CAND_2026_JAMA_SCRIBE_WORKFLOW':
   raw['caveat_ru']=raw['caveat_ru'].replace('; старую формулировку о снижении работы после смены надо исправить','.');raw['caveat_en']=raw['caveat_en'].replace('; the old after-hours claim needs correction','')
  raw.update(safe_ru=raw['summary_ru'],safe_en=raw['summary_en'])
  if c['id'] in MERGES:
   e=ev[eid];e['historical_versions']=e.get('historical_versions',[])+[dict(date=e['date'],title_ru=e.get('title_ru',e['title']),title_en=e.get('title_en',e['title']),summary_ru=e.get('summary_ru',e['summary']),summary_en=e.get('summary_en',e['summary']),numbers=copy.deepcopy(e.get('numbers',{})),sources=copy.deepcopy(e['sources']))]
   for s in sources.values():add_source(e,s)
   for k in ['title','summary','caveat','safe_wording']:pair(e,k,raw.get(k+'_ru',raw['summary_ru']),raw.get(k+'_en',raw['summary_en']),lang)
   pair(e,'caveats',[raw['caveat_ru']],[raw['caveat_en']],lang)
   e.update(status_update_date=c['date'],research_revision_date=c['date'],numbers=dict(workers=5172,average_productivity_gain_percent_approx=15),confidence='B',evidence_level='B',status='verified_as_reported',geography=geo)
   pair(e,'claim_supported',raw['summary_ru'],raw['summary_en'],lang)
   # One study family, original time anchor retained; article revision is not another experiment.
   pair(e,'date_note','Исходное сообщение: 2023 год; журнальная версия обновлена 4 февраля 2025 года. Это одно семейство исследования.',
        'Original report: 2023; journal version updated on 4 February 2025. This is one study family.',lang)
   routes=uniq([primary]+e.get('arcIds',[])+[CORP])
  else:
   if eid in ev:raise ValueError('Unreviewed duplicate event '+eid)
   e=event_record(raw,lang,sources,doc);doc['events'].append(e);ev[eid]=e;newids.append(eid)
  e.update(story_primary_arc_id=primary,story_secondary_arc_ids=[a for a in routes if a!=primary],
   jurisdictions=[g for g in geo if g not in {'Global','Europe','Gulf'}],regions=[g for g in geo if g in {'Europe','Gulf'}],
   geographic_scopes=['Global'] if 'Global' in geo else ['Cross-border'] if len(geo)>1 else ['National'] if geo else [],
   actor_jurisdictions=uniq(COUNTRY[x] for x in c.get('geo_roles',{}).get('developer_country_codes',[]) if x in COUNTRY),
   behavioral_status=[],governance_scale='not_applicable',research_updates=uniq(e.get('research_updates',[])+['knowledge-outcomes-2026-11-07']),
   research_track=c['track'],research_candidate_id=c['id'],research_evidence_kind=c['evidence_kind'],research_outcome_stage=c['outcome_stage'],
   research_review_status=c.get('integration_status'),research_provenance=copy.deepcopy(c),
   classification_review=dict(date=DATE,source_account_reviewed=True,independent_source_reverification=False,independent_replication=False))
  e['date_precision']='month' if len(e['date'])==7 else 'day'
  for key in ['geo_roles','study_family','study_period','observation_period','first_publication_date','disclosure_date','subsequent_milestones','prior_milestones','institutional_announcement_date','preprint_date','publication_date','report_period']:
   if key in c:e[key]=copy.deepcopy(c[key])
  if c.get('qualifies_candidate_id'):e['related_research_event_ids']=[ID_MAP[c['qualifies_candidate_id']]]
  for field in ['notes','corroboration_needed','claim_challenged']:pair(e,field,'','',lang)
  pair(e,'scope',c['title_ru'],c['title_en'],lang)
  pair(e,'mechanism',c['mechanism_ru'],c['mechanism_en'],lang)
  mapping.append(dict(candidate_id=c['id'],event_id=eid,action='merged_study_revision' if c['id'] in MERGES else 'added',review_status=c.get('integration_status')))
 edges=[]
 def edge(source,target,relation,aid,ru,en,tk='evidence',relationship='editorial_relationship'):
  signature=(source,target,relation,aid)
  if any((x['source'],x['target'],x['relation'],x.get('arc_id'))==signature for x in doc['edges']+edges):return
  x=dict(id=f'EDGE_V052_KNOWLEDGE_{len(edges)+1:03d}',kind='edge',source=source,target=target,source_kind='evidence' if source in ev else 'story_arc',
   target_kind=tk,relation=relation,arc_id=aid,arc_family_id=arcs[aid]['family_id'],strength='moderate',evidence_level='B',
   visual_lane='decision_support_cognition',is_auto=False,style='dashed',relationship_class=relationship)
  pair(x,'summary',ru,en,lang);edges.append(x)
 for c in CANDIDATES:
  eid=event_id(c);e=ev[eid];primary=e['story_primary_arc_id']
  for aid in [primary]+e['story_secondary_arc_ids']:
   edge(eid,aid,'part_of_arc',aid,'Тематическая принадлежность, не подтверждение всех выводов арки.','Thematic membership, not support for every conclusion in the arc.','arc','thematic')
   arcs[aid]['key_nodes']=uniq(arcs[aid]['key_nodes']+[eid])
  related=c.get('related_existing_event_ids',[])+[ID_MAP[x] for x in c.get('related_candidate_ids',[])]+e.get('related_research_event_ids',[])
  for other in uniq(related):
   if other!=eid:edge(eid,other,'context_for',primary,'Сопоставление результатов или методов; не независимое подтверждение причинности.','Comparison of findings or methods; not independent confirmation of causality.')
 for aid,thesis in [(KNOW,'THESIS_CORE'),(MED,'THESIS_DECISION_SOVEREIGNTY'),(WORK,'THESIS_CORE'),(EDU,'THESIS_DECISION_SOVEREIGNTY')]:
  edge(aid,thesis,'context_for',aid,'Аналитическая связь: производство, проверка и освоение знания влияют на возможности участников. Концентрация власти требует отдельных свидетельств.',
       'Analytical connection: production, validation and learning shape participants\' capabilities. Concentration of power requires separate evidence.','synthetic_thesis')
 for aid,role,parent,*_ in ARCS:
  if parent:edge(aid,parent,'context_for',aid,'Отраслевой сюжет уточняет основной механизм.','The sector case qualifies the parent mechanism.','arc')
 doc['edges'].extend(edges);attach_edge_links(doc,{x['id'] for x in edges})
 touched={x['arc_id'] for x in edges}
 for aid in touched:
  a=arcs[aid];dates=[ev[x]['date'] for x in a['key_nodes'] if x in ev]
  ordered=iter(sorted((x for x in a['key_nodes'] if x in ev),key=lambda x:(ev[x]['date'],x)))
  a['key_nodes']=[next(ordered) if x in ev else x for x in a['key_nodes']]
  if dates:a.update(start_date=min([a['start_date']]+dates),end_date=max([a['end_date']]+dates))
 doc['arcHierarchy']['role_counts']=dict(Counter(a['display_role'] for a in doc['arcs']))
 doc['summary']['arc_hierarchy']=dict(families=len(doc['arcFamilies']),core_mechanisms=14,nested_cases_and_qualifiers=12,timeline_records=4,total_arc_records=30)
 doc['meta'].update(version=VERSION,updated_at=DATE)
 doc['meta']['changelog'].insert(0,dict(version=VERSION,date=DATE,added_evidence=len(newids),updated_evidence=1,added_story_edges=len(edges),added_story_arcs=4,description='Knowledge production, clinical translation, work and education; study-family dedup and geographic roles.'))
 doc['presentation'].update(editorial_version=VERSION,release_notes=[dict(title='Наука, медицина, труд и обучение' if lang=='ru' else 'Science, medicine, work and learning',
  text='Одна основная арка и три вложенных сюжета. Результат, проверка, доступ и общественный эффект разделены.' if lang=='ru' else 'One core arc and three nested cases. Results, validation, access and societal effects remain distinct.')])
 doc['migrationAudit'].update(version=VERSION,v052_added_event_ids=newids,v052_updated_event_ids=list(MERGES.values()),v052_added_edge_ids=[x['id'] for x in edges],v052_base_sha256=BASE_HASH[lang])
 doc['researchAudit']['knowledge_outcomes']=dict(date=DATE,candidate_mapping=mapping,independent_replication=False,
  source_review_scope='Previously collected research packages; no new whole-registry reverification',
  corrections_in_atlas=['Canaries descriptive not causal','JAMA date and after-hours scope','NBER February publication','Klarna workload equivalent not layoffs'],
  companion_files_modified=False)
 refresh(doc)
 assert all(x in doc['edges'] for x in old['edges'])
 assert {(s['id'],s['url']) for s in old['sourceIndex']}<={(s['id'],s['url']) for s in doc['sourceIndex']}
 return doc

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 results={};report=dict(version=VERSION,date=DATE,languages={})
 for lang in ['ru','en']:
  raw=(args.input/f'ai_power_storygraph_{lang}.json').read_bytes()
  if hashlib.sha256(raw).hexdigest()!=BASE_HASH[lang]:raise ValueError('Unreviewed baseline '+lang)
  d=migrate(json.loads(raw));results[lang]=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
  report['languages'][lang]=dict(base_sha256=BASE_HASH[lang],counts={k:len(d[k]) for k in ['events','claims','claimChecks','arcs','edges','sourceIndex']},mapping=d['researchAudit']['knowledge_outcomes']['candidate_mapping'])
 args.output.mkdir(parents=True,exist_ok=True)
 for lang,body in results.items():(args.output/f'ai_power_storygraph_{lang}.json').write_text(body)
 (PACKET/'integration-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({l:r['counts'] for l,r in report['languages'].items()},indent=2))

if __name__=='__main__':main()
