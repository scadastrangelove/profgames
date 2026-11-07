#!/usr/bin/env python3
"""Pinned v0.50 -> v0.51: reconcile November research, without new top-level arcs."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from migrate_frontier_pacing import event_record, pair, add_source
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from stack_refresh_editorial import EN, CLASS
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/stack-refresh-2026-11-07'
DATE, VERSION = '2026-11-07', '0.51'
BASE_HASH = {
 'ru':'e235753c5adb6d01a08e4786478e4a1e30f89e8940e4a13f82a05548625b2d0d',
 'en':'900d6d45d77e1bd5c556a156b3f4b5504c25e65ab50ffd81b837bc81c004fb72',
}
RES = 'ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK'
CYBER = 'ARC_CYBER_CLAIM_TO_CAVEAT'
CHINA = 'ARC_CHINA_COUNTERSTACK_ROUTE_AROUND'
CLOUD = 'ARC_CLOUD_CAPACITY_VENDOR_LOCKIN'
GULF = 'ARC_GULF_CONDITIONAL_SOVEREIGNTY'
DOMAINS = {1:'CYBER_DOMAIN_01_SECURE_SYSTEMS',2:'CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE',
 3:'CYBER_DOMAIN_03_NATIONAL_DEFENSE',4:'CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE',5:'CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY'}
ROLE = {'A':'AI_ROLE_ATTACK_ENABLER','D':'AI_ROLE_DEFENSIVE_TOOL','P':'AI_ROLE_PROTECTED_SYSTEM'}
ACTOR_ALIASES = {'EuroHPC JU':'EuroHPC Joint Undertaking', 'NCSC':'UK National Cyber Security Centre'}

def sid(key):
 return 'SIG_2026_'+key

def urlkey(url):
 u=urlsplit(url)
 return urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/'),u.query,''))

EXTRA_SOURCES = [
 ('MDDI_PHP','Singapore MDDI','2026-11-04','https://www.mddi.gov.sg/newsroom/mddi-s-response-to-pq-on-disclosed-critical-php-software-vulnerabilities/','government_response'),
 ('IFM_K2','IFM','2026-09-03','https://ifm.ai/blog/k2/','model_developer_primary'),
 ('JAIS_CARD','Inception42',None,'https://huggingface.co/inception42/Jais-3-7B','model_card_primary'),
 ('CXMT_G5','CXMT','2026-09-20','https://www.cxmt.com/en/news/info_22.html','vendor_announcement'),
 ('CXMT_LPDDR6','CXMT','2026-09-07','https://www.cxmt.com/en/news/info_21.html','vendor_announcement'),
 ('COUNTERPOINT_YMTC','Counterpoint Research','2026-10-13','https://counterpointresearch.com/en/insights/ymtc-files-for-landmark-ipo-after-climbing-to-no-3-in-global-nand-race-with-dram-next','original_market_research'),
 ('REUTERS_HBM','Reuters','2026-10-28','https://www.investing.com/news/stock-market-news/exclusivechinas-cxmt-to-start-advanced-ai-memory-production-despite-poor-yields-sources-say-4977472','original_reporting_anonymous_sources'),
 ('DEBIAN_DSA','Debian','2026-11-02','https://lists.debian.org/debian-security-announce/2026/msg00521.html','maintainer_advisory'),
 ('DEBIAN_TRACKER','Debian',None,'https://security-tracker.debian.org/tracker/DSA-6602-1','maintainer_tracker'),
]

EXTRA = [
 ('CXMT_G5_DRAM_PRODUCTION','2026-09-20',['CXMT_G5'],['CXMT'],
  ('CXMT заявила о серийном производстве DRAM G5','CXMT announces mass production of G5 DRAM'),
  ('CXMT сообщила о серийном производстве платформы G5 и линейки LPDDR5X с кристаллами 24 Гбит. Заявленный прирост числа кристаллов на пластине на 50% нормирован к ёмкости 8 Гбит; активный полушаг составляет 11,95 нм.',
   'CXMT announced mass production of G5 and a 24 Gb LPDDR5X lineup. Its claimed 50% increase in dies per wafer is normalised to 8 Gb capacity; active half-pitch is 11.95 nm.'),
  ('Данные производителя, не независимый аудит. Число кристаллов на пластине не равно выходу годных, а полушаг не является названием логического техпроцесса. DRAM G5 не доказывает зрелость HBM.',
   'Manufacturer data, not an independent audit. Gross dies per wafer are not good-die yield; half-pitch is not a logic-node designation. G5 DRAM does not establish HBM maturity.')),
 ('CXMT_LPDDR6_COMMERCIAL_DEPLOYMENT','2026-09-07',['CXMT_LPDDR6'],['CXMT','Xiaomi'],
  ('CXMT заявила о коммерческом применении LPDDR6 в смартфоне Xiaomi','CXMT reports commercial LPDDR6 deployment in a Xiaomi phone'),
  ('CXMT сообщает о серийной LPDDR6 ёмкостью 16 ГБ в Xiaomi 18 Fold. Максимальная заявленная скорость — 12800 Мбит/с, при работе с данной системой на кристалле — 10667 Мбит/с.',
   'CXMT reports mass-produced 16 GB LPDDR6 in the Xiaomi 18 Fold. Claimed maximum speed is 12,800 Mbps, with 10,667 Mbps when operating with this SoC.'),
  ('Первичное заявление поставщика без независимого теста. Это мобильная память, не HBM для серверных ускорителей; скорости нельзя переносить на весь китайский ИИ-стек.',
   'A supplier statement without independent testing. This is mobile memory, not server-accelerator HBM; speeds do not describe the entire Chinese AI stack.')),
 ('YMTC_NAND_SHIPMENT_RANK','2026-10-13',['COUNTERPOINT_YMTC'],['YMTC','Counterpoint Research'],
  ('Counterpoint: YMTC вышла на третье место по объёму поставок NAND','Counterpoint ranks YMTC third by NAND shipment volume'),
  ('По оценке Counterpoint, во II квартале 2026 года YMTC заняла третье место в мире по объёму поставок NAND после Samsung и SK hynix с Solidigm. Наблюдение опубликовано 13 октября.',
   'Counterpoint estimates that YMTC ranked third worldwide by NAND shipment volume in Q2 2026, after Samsung and SK hynix including Solidigm. The observation was published on October 13.'),
  ('Оценка исследовательской фирмы, не перепроверенная здесь перепись поставок. Место по объёму не равно месту по выручке. NAND не заменяет DRAM или HBM.',
   'A market-research estimate, not a shipment census independently checked here. Volume rank is not revenue rank; NAND is not a substitute for DRAM or HBM.')),
 ('CXMT_HBM3E_LIMITED_PRODUCTION_REPORTED','2026-10-28',['REUTERS_HBM'],['CXMT'],
  ('Reuters: CXMT готовит ограниченный выпуск HBM3E при низком выходе годных','Reuters: CXMT plans limited HBM3E production despite low yields'),
  ('Reuters со ссылкой на двух собеседников сообщает о передаче образцов HBM3E китайским разработчикам ИИ-чипов и плане ограниченного производства в ближайшие два месяца. Сообщаемый выход годных — 20–30%, против примерно 70% у SK hynix.',
   'Reuters cites two people on HBM3E samples sent to Chinese AI-chip designers and plans for limited production within two months. Reported yields are 20-30%, versus roughly 70% at SK hynix.'),
  ('Анонимные источники, не производственный аудит. Это образцы и план, не уже достигнутый массовый выпуск или паритет себестоимости. Показатели DRAM и NAND не подменяют этот отдельный барьер.',
   'Anonymous sources, not a production audit. Samples and plans are not established mass output or cost parity. DRAM and NAND progress does not remove this separate bottleneck.')),
 ('DEBIAN_DSA6602_KERNEL_PATCH_BATCH','2026-11-02',['DEBIAN_DSA','DEBIAN_TRACKER'],['Debian','Linux kernel maintainers'],
  ('Debian DSA-6602-1: один выпуск ядра объединяет 611 CVE','Debian DSA-6602-1 bundles 611 CVEs in one kernel update'),
  ('В бюллетене DSA-6602-1 перечислены 611 уникальных CVE: 1 с префиксом 2024, 62 — 2025 и 548 — 2026. Трекер Debian указывает исправленную версию 6.12.115-2 для trixie. Это объём пакета исправлений, который предстоит проверить и развернуть операторам.',
   'DSA-6602-1 lists 611 unique CVEs: one with a 2024 prefix, 62 with 2025 and 548 with 2026. Debian lists 6.12.115-2 as fixed for trixie. This is a patch-delivery batch for operators to assess and deploy.'),
  ('Префикс CVE не является датой обнаружения. Бюллетень не атрибутирует находки ИИ и не устанавливает 611 новых уязвимостей за один день. Отдельный конвейер OpenAI подтверждает ИИ-участие в поиске, но пересечение двух списков не измерено.',
   'A CVE year prefix is not its discovery date. The bulletin does not attribute discoveries to AI or establish 611 new flaws found in one day. OpenAI separately documents AI-assisted discovery; overlap between the two sets has not been measured.')),
]

TRACKS = {
 'PHP2SHELL_DISCOVERY_REMEDIATION':(['MAINTENANCE_CAPACITY','VERIFIED_REMEDIATION'],['validation','patch','release','deployment']),
 'OPENAI_KERNEL_PIPELINE':(['MAINTENANCE_CAPACITY','VERIFIED_REMEDIATION'],['discovery','validation','patch','coordination']),
 'DEBIAN_DSA6602_KERNEL_PATCH_BATCH':(['MAINTENANCE_CAPACITY','CHANGE_AND_RECOVERY'],['release','deployment']),
 'GPT6_CYBER_RESTRICTED_RELEASE':(['DEFENSE_ACCESS'],[]),
 'GEMINI_CARBON_DEFENDERS_FIRST':(['DEFENSE_ACCESS'],[]),
 'MISTRAL_OPEN_AND_VETTED_CYBER':(['DEFENSE_ACCESS'],[]),
 'OPENAI_ONEGOV_EXPANSION':(['DEFENSE_ACCESS'],[]),
 'UK_AI_DEFENCE_INCIDENT_READINESS':(['VERIFIED_REMEDIATION','INCIDENT_LEARNING'],['discovery','patch']),
 'GITBOOK_CREDENTIAL_CHAIN':(['INCIDENT_LEARNING','CHANGE_AND_RECOVERY'],['recovery']),
 'EMUDHRA_TRUST_REVOCATION':(['CHANGE_AND_RECOVERY'],['deployment','recovery']),
 'YANDEX_DATACENTRE_PHYSICAL_RESILIENCE':(['CHANGE_AND_RECOVERY'],['recovery']),
 'AWS_EU_DISCONNECTION_EXERCISE':(['CHANGE_AND_RECOVERY'],['revalidation']),
 'ORACLE_OPENAI_ENTERPRISE_SECURITY':(['VERIFIED_REMEDIATION'],['discovery','validation','patch']),
}

def load_records():
 packets=[json.loads((ROOT/'review'/name/'candidates.json').read_text()) for name in
          ['cyber-geopolitics-2026-11-07','stack-geography-2026-11-07']]
 raw_sources={s['id']:s for p in packets for s in p['sources']}
 for key,name,date,url,kind in EXTRA_SOURCES:
  raw_sources[key]=dict(id=key,publisher=name,publication_date=date,url=url,type=kind)
 sources={}
 for key,s in raw_sources.items():
  secondary=s['type'].startswith('original_reporting')
  sources[key]=dict(name=s['publisher'],date=s.get('publication_date'),url=s['url'],
   source_class=s['type'],type='Media / report' if secondary else 'Primary source',
   primary_or_secondary='secondary' if secondary else 'primary',checked_at=DATE,
   updated_date=s.get('updated_date'),retrieval_note=s.get('retrieval_note',''),
   verification_method='source_account_reviewed; no_independent_replication')
 records=[]
 for p in packets:
  for candidate in p['candidates']:
   key=candidate['id'].removeprefix('CAND_2026_')
   if key in ['PHP2SHELL_ACTIVE_EXPLOITATION','BINANCE_FBI_ATTRIBUTION']:
    continue
   c=copy.deepcopy(candidate)
   actors,geo,layers,domains,roles,artifact,force,stage,priority=CLASS[key]
   title,summary,caveat=EN[key]
   if key=='PHP2SHELL_DISCOVERY_REMEDIATION':
    c['source_ids']+=['PAN_PHP','CSA_PHP','MDDI_PHP']
    c['facts_ru']+=['Palo Alto Networks затем подтвердила эксплуатацию доступных интерфейсов управления PAN-OS; 3 ноября CSA описала цепочку с Fragnesia. 4 ноября MDDI сообщило о защитных мерах в госсистемах и критической инфраструктуре Сингапура и об отсутствии свидетельств эксплуатации в них.']
    c['caveats_ru']+=['Дата уведомления не равна началу атак. Выпуск патча PHP не означает обновления всех зависимых продуктов. Ответ Сингапура не подтверждает взлом или отключение государственных сайтов.']
   if key=='JAIS3_OPEN_ARABIC_AGENTS':
    c['title_ru']='Jais 3: арабоязычные модели на K2 Horizon с открытыми этапами обучения'
    c['source_ids']+=['IFM_K2','JAIS_CARD']
    c['facts_ru']=['IFM и партнёры выпустили шесть Jais 3, от 0,9 до 375 млрд параметров, на собственной базе K2 Horizon, а не Qwen. По данным разработчиков, продолженное предобучение использовало 201,45 млрд токенов (75% арабских, 25% повторных), SFT — 41,1 млрд; 59% арабских данных получены синтетическим переводом. Опубликованы веса Apache 2.0 и промежуточные состояния, а также образец, не весь корпус данных. В проверенной карточке 7B код всё ещё обозначен как готовящийся к публикации.']
    c['caveats_ru']=['Происхождение, объёмы обучения и сравнительные результаты сообщены разработчиками; независимого аудита всего конвейера и качества арабского языка здесь нет. Не смешивать Jais 3 с прежним K2Think на Qwen. Открытые веса не доказывают аппаратную независимость, полную воспроизводимость или превосходство над передовыми моделями; крупнейшая модель не означает дешёвую автономию для каждого.']
   event_date=c.get('event_date') or ('2026-11-05' if key=='CHINA_H200_IMPORT_GATE' else None)
   assert event_date, key
   records.append(dict(id=sid(key),key=key,date=event_date,
    date_basis=c.get('date_basis') or 'publication_date_incident_date_not_disclosed',date_status='source_backed',
    title_ru=c['title_ru'],title_en=title,summary_ru=' '.join(c['facts_ru']),summary_en=summary,
    caveat_ru=' '.join(c['caveats_ru']),caveat_en=caveat,safe_ru=' '.join(c['facts_ru']),safe_en=summary,
    source_ids=c['source_ids'],arcs=c['arc_ids'],actors=[ACTOR_ALIASES.get(a,a) for a in actors],actor_types=[],
    jurisdictions=c.get('geography') or geo,stack_layers=c.get('visual_lanes') or layers,
    structures=[],research_questions=[],numbers={},confidence='B',status='verified_as_reported',
    domains=[DOMAINS[n] for n in domains],primary_domain=DOMAINS[domains[0]] if domains else None,
    roles=[ROLE[r] for r in roles],artifact=artifact,force=force,stage=stage,priority=priority,
    delegation='control_requirement' if key in ['NIST_AGENT_IDENTITY_TENETS','NVIDIA_SOVEREIGN_RUNTIME','ORACLE_OPENAI_ENTERPRISE_SECURITY'] else 'not_established' if roles=='A' else 'not_applicable',
    contexts=['production'] if artifact in ['incident','deployment'] else ['ecosystem_measurement'] if artifact in ['market_observation','research'] else ['governance_document'],
    method='reviewed_public_sources; distinguish_observation_claim_and_roadmap',
    related=c.get('related_existing_event_ids',[]),observation=c.get('observation_period'),
    ai_attribution=c.get('ai_attribution','not_established_or_not_applicable')))
 for key,date,source_ids,actors,title,summary,caveat in EXTRA:
  kernel=key.startswith('DEBIAN')
  records.append(dict(id=sid(key),key=key,date=date,date_basis='advisory_publication' if kernel else 'publication_date',
   date_status='source_backed',title_ru=title[0],title_en=title[1],summary_ru=summary[0],summary_en=summary[1],
   caveat_ru=caveat[0],caveat_en=caveat[1],safe_ru=summary[0],safe_en=summary[1],source_ids=source_ids,
   actors=actors,actor_types=[],jurisdictions=['Global'] if kernel else ['China','Global'],
   stack_layers=['cyber_security_patch'] if kernel else ['energy_compute_chips'],
   structures=['security'] if kernel else ['production'],research_questions=[],
   numbers={'unique_cve_ids':611,'cve_prefix_years':{'2024':1,'2025':62,'2026':548}} if kernel else {},
   confidence='A' if kernel else 'B',status='verified_as_reported',domains=[DOMAINS[4],DOMAINS[3]] if kernel else [],
   primary_domain=DOMAINS[4] if kernel else None,roles=[],artifact='disclosure' if kernel else 'market_observation',
   force='not_applicable',stage='remediated' if kernel else 'reported',priority=1 if kernel else 2,
   delegation='not_applicable',contexts=['production'] if kernel else ['ecosystem_measurement'],
   method='source_review; unique_CVE_identifier_count' if kernel else 'attributed_source_review',
   arcs=[RES] if kernel else [CHINA,CLOUD],related=[],observation='2026-Q2' if key.startswith('YMTC') else None,
   ai_attribution='not_established_by_advisory' if kernel else 'not_applicable_hardware'))
 return records,sources

RECORDS,SOURCES=load_records()

def refresh(doc):
 rebuild_sources(doc);rebuild_counts(doc)
 for key,col in [('total_evidence_items','events'),('total_timeline_items','events'),('total_events','events'),
                 ('total_story_edges','edges'),('total_edges','edges'),('total_claims','claims')]:
  doc['summary'][key]=len(doc[col])
 doc['summary'].update(source_count=len(doc['sourceIndex']),
  cyber_framework_event_count=sum(bool(e.get('primary_domain_id')) for e in doc['events']),
  claim_status_counts=dict(Counter(c['status'] for c in doc['claims'])))
 doc['summary']['stats'].update(total_claims=len(doc['claims']),**doc['summary']['claim_status_counts'])
 for key,field in [('by_status','status'),('event_status_counts','status'),('by_confidence','confidence')]:
  doc['summary'][key]=dict(Counter(e[field] for e in doc['events']))
 doc['arcHierarchy'].update(primary_event_assignments=sum(bool(e.get('story_primary_arc_id')) for e in doc['events']),
  events_with_secondary_arcs=sum(bool(e.get('story_secondary_arc_ids')) for e in doc['events']))
 thesis_ids={t['id'] for t in doc['thesisNodes']}
 ac={a['id']:sum(e['source']==a['id'] and e['target'] in thesis_ids for e in doc['edges']) for a in doc['arcs']}
 hanging=[a for a,n in ac.items() if not n]
 doc['connectivity'].update(edge_count=len(doc['edges']),story_edges=len(doc['edges']),last_recomputed=DATE,
  arc_count=len(ac),story_arcs=len(ac),computed_arc_count=len(ac),arc_to_thesis_counts=ac,
  computed_arc_to_thesis_counts=ac,hanging_arcs_after_fix=hanging,computed_hanging_arcs=hanging)
 doc['referenceIntegrity']=references(doc)
 assert doc['referenceIntegrity']['valid'],doc['referenceIntegrity']

def migrate(doc):
 if doc['meta']['version']!='0.50':
  raise ValueError('Expected v0.50, refusing repeated or out-of-order migration')
 old=copy.deepcopy(doc);lang=doc['language']
 events={e['id']:e for e in doc['events']};arcs={a['id']:a for a in doc['arcs']}
 source_urls={urlkey(s['url']):s['url'] for s in doc['sourceIndex']}
 sources=copy.deepcopy(SOURCES)
 for s in sources.values():
  s['url']=source_urls.setdefault(urlkey(s['url']),s['url'])
 for r in RECORDS:
  if r['id'] in events: raise ValueError('Duplicate event: '+r['id'])
  e=event_record(r,lang,sources,doc)
  geo=r['jurisdictions'];jur=[x for x in geo if x not in ['Global','Gulf']]
  e.update(date_precision='month' if len(r['date'])==7 else 'day',
   story_primary_arc_id=r['arcs'][0],story_secondary_arc_ids=r['arcs'][1:],
   jurisdictions=jur,actor_jurisdictions=[],regions=[x for x in geo if x=='Gulf'],
   geographic_scopes=['Global'] if 'Global' in geo else ['National'] if len(jur)==1 else ['Cross-border'],
   geographic_scope_basis='event_scope_not_actor_nationality',
   research_updates=['stack-refresh-2026-11-07'],classification_review=dict(date=DATE,
    source_content_checked=True,independent_source_reverification=False,independent_replication=False),
   behavioral_status=[],governance_scale='not_applicable' if r['force']=='not_applicable' else 'as_specified_in_record',
   ai_attribution=r['ai_attribution'],observation_period=r['observation'])
  if len(r['date'])==7:e.update(incident_date=r['date'],incident_date_precision='month')
  if r['key']=='CHINA_H200_IMPORT_GATE':e.update(incident_date=None,incident_date_precision='unknown',date_basis='reported_observation_date')
  if r['key']=='CHINA_AI_TECH_EXPORT_CATALOGUE':
   e['legal_components']=[dict(component='catalogue',stage='consultation',deadline='2026-11-15'),
                         dict(component='interim_registration',stage='effective',since='2026-10-16')]
  for field in ['notes','corroboration_needed','claim_challenged']:pair(e,field,'','',lang)
  pair(e,'scope',r['title_ru'],r['title_en'],lang)
  pair(e,'role_basis','Роль ИИ относится к указанному применению; контекстный пример не получает роль атакующего или защитника без источника.',
       'AI roles refer to the specified use; contextual evidence receives no attacker or defender role without source support.',lang)
  pair(e,'editorial_rationale','Связь с аркой означает тематическую принадлежность. Тип документа, стадия и ограничения указаны отдельно.',
       'Arc membership is thematic. Document type, implementation stage and limitations remain separate.',lang)
  if r['key'] in TRACKS:
   tracks,stages=TRACKS[r['key']]
   e['resilience_track_ids']=['RES_TRACK_'+x for x in tracks];e['defense_stage_ids']=stages
   e['defense_evidence_kind']='maintainer_report' if r['key'].startswith(('DEBIAN','PHP2')) else 'announced_program' if r['stage']=='announced' else 'provider_operational_report'
   for t in doc['cyberFramework']['resilience_tracks']:
    if t['id'] in e['resilience_track_ids']:t['event_ids']=uniq(t['event_ids']+[e['id']])
  events[e['id']]=e;doc['events'].append(e)
 edges=[]
 def edge(source,target,relation,arc,ru,en,target_kind='evidence',relationship='editorial_relationship'):
  assert target in events or target in arcs or any(target==x['id'] for col in ['claims','claimChecks','thesisNodes'] for x in doc[col]),target
  item=dict(id=f'EDGE_V051_STACK_{len(edges)+1:03d}',source=source,target=target,source_kind='evidence' if source in events else 'story_arc',
   target_kind=target_kind,relation=relation,arc_id=arc,arc_family_id=arcs[arc]['family_id'],
   strength='moderate',evidence_level=events[source]['confidence'] if source in events else '',visual_lane=events[source]['stack_layer'][0] if source in events else 'governance_law',
   kind='edge',is_auto=False,style='solid' if relationship=='evidential' else 'dashed',relationship_class=relationship)
  pair(item,'summary',ru,en,lang);edges.append(item)
 for r in RECORDS:
  for aid in r['arcs']:
   edge(r['id'],aid,'part_of_arc',aid,'Тематическая принадлежность, не подтверждение всех выводов арки.',
        'Thematic membership, not support for every conclusion in the arc.','arc','thematic')
   arcs[aid]['key_nodes']=uniq(arcs[aid]['key_nodes']+[r['id']])
  for prior in r['related']:
   edge(r['id'],prior,'context_for',r['arcs'][0],
    'Продолжение или сопоставление с прежним событием; новая стадия не заменяет исходную дату и не устанавливает причинность.',
    'A follow-up or comparison with earlier evidence; the new stage neither replaces the original date nor establishes causation.')
 for source,target,arc,ru,en in [
  ('DEBIAN_DSA6602_KERNEL_PATCH_BATCH','OPENAI_KERNEL_PIPELINE',RES,
   'Выпуск пакета и ИИ-поиск показывают разные этапы конвейера; совпадение отдельных CVE не измерено.',
   'Patch delivery and AI discovery concern different pipeline stages; individual CVE overlap has not been measured.'),
  ('VAPOR_PANDA_ARTEX','STORM0940_ARTEX_CONNECTWISE',CYBER,
   'Общий инструмент, разные атрибуции; число жертв нельзя суммировать без проверки пересечений.',
   'Shared tooling, different attributions; victim counts cannot be added without overlap checks.'),
  ('CXMT_HBM3E_LIMITED_PRODUCTION_REPORTED','CXMT_G5_DRAM_PRODUCTION',CHINA,
   'Прогресс обычной DRAM не доказывает тот же выход годных и зрелость производства HBM.',
   'Conventional DRAM progress does not establish the same yields or manufacturing maturity in HBM.'),
  ('CXMT_HBM3E_LIMITED_PRODUCTION_REPORTED','SKHYNIX_LONG_TERM_ALLOCATION',CLOUD,
   'Образцы, выход годных и контрактное распределение массовых мощностей являются разными условиями доступа к памяти.',
   'Samples, yields and contractual allocation of mass capacity are distinct conditions of memory access.'),
  ('JAIS3_OPEN_ARABIC_AGENTS','ABUDHABI_MACHINE_READABLE_GOVERNMENT',GULF,
   'Собственная арабская модель и локальное применение иностранной модели сосуществуют; суверенность различается по слою.',
   'A domestic Arabic model and local use of a foreign model coexist; autonomy differs by layer.'),
 ]:edge(sid(source),sid(target),'context_for',arc,ru,en)
 # Specific mechanisms get evidence edges; membership alone is never counted as support.
 for key,target,relation,ru,en in [
  ('OPENAI_KERNEL_PIPELINE','CLM_006_MACHINE_SPEED_CYBER','supports_with_scope',
   'Подтверждает масштабируемую ИИ-валидацию LPE по отчёту разработчика, не 948 новых CVE или автономных взломов.',
   'Supports scalable AI-assisted LPE validation as reported by the developer, not 948 new CVEs or autonomous intrusions.'),
  ('GPT6_CYBER_RESTRICTED_RELEASE','CLM_013_QUIET_ACCESS_CONTROL','supports_with_scope',
   'Доступ зависит от проверки организации и технических условий, а не только от наличия модели.',
   'Access depends on organisational verification and technical conditions, not only model availability.'),
  ('AWS_EU_DISCONNECTION_EXERCISE','CLM_005_EU_SEMI_PERIPHERY','qualifies',
   'Испытание частичной операционной автономии ограничивает тезис о полной зависимости, не устанавливая переносимость или юридический иммунитет.',
   'The partial operational-autonomy exercise qualifies total-dependence claims without establishing portability or legal immunity.'),
  ('JAIS3_OPEN_ARABIC_AGENTS','CLM_003_GULF_PROTECTORATE','qualifies',
   'Собственная модельная работа ограничивает ярлык простого покупателя, но не снимает аппаратные зависимости.',
   'Domestic model work qualifies a pure-buyer label without removing hardware dependencies.'),
  ('CHINA_AI_TECH_EXPORT_CATALOGUE','CLM_008_MODEL_LAYER_EXPORT_CONTROL','supports_with_scope',
   'Китай тоже определяет пределы передачи ИИ-технологий; проект каталога и действующая регистрация имеют разную силу.',
   'China also defines AI technology transfer boundaries; the draft catalogue and effective registration have different force.'),
  ('YANDEX_ALICE_FOUNDATION_RELEASE','CLM_029_RUSSIA_SELECTIVE_SOVEREIGNTY','qualifies',
   'Открытая собственная базовая модель добавляет выбор в модельном слое, не доказывая независимости ускорителей.',
   'An open domestic base model adds model-layer choice without establishing accelerator independence.'),
  ('NEW_YORK_DC_PERMIT_MORATORIUM','CLM_023_ENERGY_BOTTLENECK_WITH_FLEXIBILITY','supports_with_scope',
   'Конкретное разрешительное ограничение в одном штате; не остановка всей американской отрасли.',
   'A specific permitting constraint in one state, not a halt to the entire U.S. industry.'),
 ]:
  r=next(r for r in RECORDS if r['key']==key)
  edge(r['id'],target,relation,r['arcs'][0],ru,en,'claimCheck','evidential' if relation!='context_for' else 'editorial_relationship')
  if relation!='context_for':
   check=next(c for c in doc['claimChecks'] if c['id']==target)
   field='qualifying_evidence' if relation=='qualifies' else 'supporting_evidence'
   check[field]=uniq(check.get(field,[])+[r['id']])
   for source_id in r['source_ids']:add_source(check,sources[source_id])
 pacing='ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL'
 edge(pacing,'THESIS_ACCESS_AS_POWER','context_for',pacing,
  'Регулирование темпа, выпуска и непрерывности доступа — разные способы определять условия использования моделей. Это аналитическое обобщение арки, не дополнительный независимый факт.',
  'Pacing, release and access continuity are distinct ways to set model-use conditions. This is an analytical synthesis of the arc, not an additional independent fact.',
  'synthetic_thesis','editorial_relationship')
 doc['edges'].extend(edges);attach_edge_links(doc,{e['id'] for e in edges})
 for aid in {a for r in RECORDS for a in r['arcs']}:
  a=arcs[aid];ordered=iter(sorted((n for n in a['key_nodes'] if n in events),key=lambda n:(events[n]['date'],n)))
  a['key_nodes']=[next(ordered) if n in events else n for n in a['key_nodes']]
  dates=[events[n]['date'] for n in a['key_nodes'] if n in events]
  a['start_date']=min([a['start_date']]+dates);a['end_date']=max([a['end_date']]+dates)
 for aid,ru,en in [
  (CHINA,'Китай развивает собственные DRAM, NAND и вычислительные системы, одновременно ограничивая входящий и исходящий доступ. Серийные продукты, образцы HBM и будущие мощности показываются раздельно.',
   'China develops domestic DRAM, NAND and compute systems while also gating inward and outward access. Mass-produced products, HBM samples and future capacity remain distinct.'),
  (GULF,'Собственное обучение Jais, сделки HUMAIN и локальное применение OpenAI показывают разные формы самостоятельности. Владение капиталом, модельная компетенция и независимость оборудования не взаимозаменяемы.',
   'Jais training, HUMAIN ownership and local OpenAI use show different forms of agency. Capital ownership, model capability and hardware independence are not interchangeable.'),
  (RES,'ИИ-конвейеры увеличивают поток проверенных находок, но выпуск патчей, развёртывание и восстановление остаются отдельными работами. Отказы удостоверяющих центров и физических ЦОД показывают системный контекст, не автоматически ИИ-атрибуцию.',
   'AI pipelines expand validated-finding throughput, while patch release, deployment and recovery remain separate work. CA and physical data-centre failures supply systemic context, not automatic AI attribution.'),
 ]:pair(arcs[aid],'thesis',arcs[aid]['thesis_ru']+' '+ru,arcs[aid]['thesis_en']+' '+en,lang)
 # A layer-specific assessment replaces the coarse geopolitical label, not historical facts.
 for country in doc['countries']:
  if country['geography']=='UAE':
   pair(country,'tier_position','Условный доступ к внешнему стеку и собственная модельная компетенция',
        'Conditional external-stack access with domestic model capability',lang)
   country['strongest_supporting_evidence']=uniq(country['strongest_supporting_evidence']+[sid('JAIS3_OPEN_ARABIC_AGENTS'),sid('ABUDHABI_MACHINE_READABLE_GOVERNMENT')])
  if country['geography']=='China':
   country['strongest_supporting_evidence']=uniq(country['strongest_supporting_evidence']+[sid('CXMT_G5_DRAM_PRODUCTION'),sid('YMTC_NAND_SHIPMENT_RANK')])
  if country['geography']=='Russia':
   country['strongest_supporting_evidence']=uniq(country['strongest_supporting_evidence']+[sid('YANDEX_ALICE_FOUNDATION_RELEASE'),sid('YANDEX_DATACENTRE_PHYSICAL_RESILIENCE')])
 doc['meta'].update(version=VERSION,updated_at=DATE)
 doc['meta']['changelog'].insert(0,dict(version=VERSION,date=DATE,added_evidence=len(RECORDS),added_story_edges=len(edges),
  added_claims=0,added_story_arcs=0,description='Cyber throughput, access and resilience; memory, local models and infrastructure governance.'))
 doc['presentation'].update(editorial_version=VERSION,release_notes=[dict(
  title='Киберустойчивость и география стека' if lang=='ru' else 'Cyber resilience and stack geography',
  text='Новые события связаны с существующими арками. Производство, обещания, доступ и результаты испытаний разделены.' if lang=='ru' else
       'New evidence joins existing arcs. Production, commitments, access and evaluation results remain distinct.')])
 doc['cyberFramework']['updated_at']=DATE
 doc['migrationAudit'].update(version=VERSION,v051_added_event_ids=[r['id'] for r in RECORDS],v051_added_edge_ids=[e['id'] for e in edges],v051_updated_event_ids=[])
 doc['researchAudit']['november_stack_refresh']=dict(date=DATE,accepted_records=len(RECORDS),
  merged_candidates=['CAND_2026_PHP2SHELL_ACTIVE_EXPLOITATION'],held=['CAND_2026_BINANCE_FBI_ATTRIBUTION','SHIRYAEV_2027_FORECAST'],
  new_top_level_arcs=0,independent_replication=False)
 doc['factcheckAudit']['v051']=dict(date=DATE,method='reviewed_source_accounts_and_explicit_editorial_limits',entire_source_registry_reverified=False,
  debian_cve_count=dict(unique=611,prefix_years={'2024':1,'2025':62,'2026':548},method='unique CVE identifiers in Debian mail HTML; matches supplied bulletin'))
 refresh(doc)
 assert all(e in doc['edges'] for e in old['edges'])
 assert {(s['id'],s['url']) for s in old['sourceIndex']}<={(s['id'],s['url']) for s in doc['sourceIndex']}
 return doc

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 result={};audit=dict(version=VERSION,date=DATE,languages={})
 for lang in ['ru','en']:
  payload=(args.input/f'ai_power_storygraph_{lang}.json').read_bytes()
  if hashlib.sha256(payload).hexdigest()!=BASE_HASH[lang]:raise ValueError('Unreviewed baseline '+lang)
  old=json.loads(payload);doc=migrate(copy.deepcopy(old));doc['migrationAudit']['v051_base_sha256']=BASE_HASH[lang]
  result[lang]=json.dumps(doc,ensure_ascii=False,indent=2)+'\n'
  audit['languages'][lang]=dict(base_sha256=BASE_HASH[lang],counts={c:len(doc[c]) for c in ['events','claims','claimChecks','arcs','edges','sourceIndex']},
   preserved_event_ids=len(old['events']),preserved_edges=len(old['edges']),preserved_source_ids=len(old['sourceIndex']),
   cyber=sum(bool(e.get('primary_domain_id')) for e in doc['events']),core=sum(bool(e.get('primary_domain_id')) and e['editorial_priority']==1 for e in doc['events']))
 args.output.mkdir(parents=True,exist_ok=True);PACKET.mkdir(parents=True,exist_ok=True)
 for lang,text in result.items():
  path=args.output/f'ai_power_storygraph_{lang}.json';tmp=path.with_suffix('.tmp');tmp.write_text(text);tmp.replace(path)
 (PACKET/'migration-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 (PACKET/'evidence.json').write_text(json.dumps(dict(records=RECORDS,sources=SOURCES),ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
