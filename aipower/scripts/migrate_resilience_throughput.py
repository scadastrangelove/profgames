#!/usr/bin/env python3
"""Build the pinned v0.33 -> v0.34 bilingual resilience layer.

Both inputs are validated before either output is written. This script only
changes data; it never contacts a network, runs an experiment or pushes Git.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os
from collections import Counter
from pathlib import Path
from migrate_v031_agent_behavior import rebuild_sources, rebuild_counts, attach_edge_links, uniq
from validate import references
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'review/resilience-throughput'
DATE = '2026-09-06'
ARC = 'ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK'
FAMILY = 'ARC_FAMILY_CYBER_COGNITION_WAR'
CLAIM = 'CLM_VALID_FINDINGS_MAINTENANCE_CAPACITY'
D3 = 'CYBER_DOMAIN_03_NATIONAL_DEFENSE'
D4 = 'CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE'

def pair(obj, key, ru, en, lang):
    obj[key+'_ru'],obj[key+'_en'],obj[key] = ru,en,ru if lang=='ru' else en

def src(s):
    return {k:copy.deepcopy(v) for k,v in s.items() if k!='id'}

def add_source(e,s):
    if s['url'] not in {x.get('url') for x in e.get('sources',[])}:
        e.setdefault('sources',[]).append(src(s))

def event_record(r, lang, sources):
    ss=[src(sources[s]) for s in r['source_ids']]; p=ss[0]
    e={
        'id':r['id'],'kind':'event','date':r['date'],'year':int(r['date'][:4]),
        'date_basis':r['date_basis'],'date_status':r['date_status'],
        'source_date':r.get('source_date',p['date']),'url':p['url'],
        'source_name':p['name'],'source_type_raw':p['source_class'],
        'source_type':p['type'],'primary_or_secondary':'primary',
        'actors':r['actors'],'actor':', '.join(r['actors']),'actor_raw':', '.join(r['actors']),
        'actors_raw':r['actors'],'actor_facets_legacy':r['actors'],'actor_facets':r['actors'],
        'actor_entities':r['actors'],'actor_types':r['actor_types'],
        'actor_jurisdictions':r['jurisdictions'],'jurisdictions':r['jurisdictions'],
        'geography_raw':r['jurisdictions']+['Global'],'geography':r['jurisdictions'],
        'regions':[],'locations':r.get('locations',[]),'institutional_scopes':[],
        'geo_context':[],'geographic_scopes':['Global'],'geography_unclassified':[],
        'actor_unclassified':[],'actor_classification_status':'resolved','geography_classification_status':'resolved',
        'stack_layer':['cyber_security_patch'],'stack_layers':['cyber_security_patch'],
        'strange_structure':['security','knowledge'],'strange_structures':['security','knowledge'],
        'research_question':['RQ3','RQ4'],'exact_quote_short':'',
        'numbers':copy.deepcopy(r['numbers']),'money_status':r.get('money_status',''),
        'confidence':r['confidence'],'evidence_level':r['confidence'],'status':r['status'],
        'cyber_domain_ids':r['cyber_domain_ids'],'cyber_role_ids':r['roles'],
        'primary_domain_id':r['primary_domain_id'],'artifact_kind':r['artifact_kind'],
        'normative_force':r['normative_force'],'implementation_stage':r['implementation_stage'],
        'delegated_authority':r['delegated_authority'],
        'cyber_access_principal':r['delegated_authority'] in ['observed','evaluated'],
        'editorial_priority':r['priority'],'sources':ss,'edgeIds':[],
        'arcIds':[ARC],'arcFamilyIds':[FAMILY],'relationTypes':[],
        'research_updates':['resilience-throughput-v034'],
        'resilience_track_ids':r['tracks'],'defense_evidence_kind':r['defense_evidence_kind'],
        'defense_stage_ids':r['defense_stage_ids'],
        'pipeline_metrics':copy.deepcopy(r['pipeline_metrics']),
        'classification_review':{'date':DATE,'method':'primary_source_review_and_explicit_editorial_mapping',
             'source_url':p['url'],'independent_source_reverification':True,'independent_replication':False},
        'evidence_context':['governance_document'] if r['defense_evidence_kind'] in ['risk_assessment','announced_program','draft_proposal'] else ['ecosystem_measurement'],
        'evidence_method':r['defense_evidence_kind'],
    }
    for k in ['title','summary']:
        pair(e,k,r[k+'_ru'],r[k+'_en'],lang)
    for k in ['notes','caveat','corroboration_needed','claim_challenged','scope']:
        pair(e,k,r['caveat_ru'],r['caveat_en'],lang)
    for k in ['safe_wording','claim_supported']:
        pair(e,k,r['safe_ru'],r['safe_en'],lang)
    pair(e,'caveats',[r['caveat_ru']],[r['caveat_en']],lang)
    pair(e,'role_basis','Роли описывают функцию ИИ в этом свидетельстве, не массовую автономную эксплуатацию.',
         'Roles describe the function of AI in this evidence, not widespread autonomous operation.',lang)
    pair(e,'editorial_rationale','История потока реальных находок и ёмкости защитного цикла. '+r['safe_ru'],
         'Evidence on real-finding throughput and defensive-cycle capacity. '+r['safe_en'],lang)
    for k in ['pipeline_semantics','scheduled_effective_date','end_date','event_date','observed_at']:
        if k in r:e[k]=copy.deepcopy(r[k])
    return e

def patch_existing(d,raw,sources):
    lang=d['language']; ev={e['id']:e for e in d['events']}
    for id,ts in raw['existing_track_tags'].items():
        e=ev[id];e['resilience_track_ids']=uniq(e.get('resilience_track_ids',[])+ts)
        e['resilience_review']={'date':DATE,'method':'mapping_of_existing_evidence','new_source_verification':False}
    firefox=ev['SIG_2026_MYTHOS_FIREFOX_271']
    firefox['v033_source_snapshot']={k:copy.deepcopy(firefox.get(k)) for k in ['summary','numbers','source_name','source_type','url','source_date']}
    pair(firefox,'title','Firefox 150: выпущены исправления 271 уязвимости, найденной с помощью Mythos','Firefox 150 ships fixes for 271 Mythos-assisted vulnerability findings',lang)
    add_source(firefox,sources['S21'])
    p=sources['S21']
    firefox.update(url=p['url'],source_name=p['name'],source_type=p['type'],source_date=p['date'],primary_or_secondary='primary')
    pair(firefox,'summary','Mozilla подтверждает выпуск исправлений 271 уязвимости в Firefox 150 после первоначальной оценки Mythos. Команда перераспределила инженерные усилия; установка обновления всеми пользователями не измерена.',
         'Mozilla reports 271 security fixes shipped in Firefox 150 after its initial Mythos assessment. Engineering work was reprioritized; installation by all users was not measured.',lang)
    pair(firefox,'safe_wording',firefox['summary_ru'],firefox['summary_en'],lang)
    pair(firefox,'scope','Первичный отчёт участника программы, не независимая репликация модели. 271 — исправления в Firefox 150; прежние 423 из прессы относятся к другому охвату и не складываются с ними. Выпуск не равен downstream-установке.',
         'Primary participant report, not independent model replication. The 271 are Firefox 150 fixes; the earlier press figure of 423 has a different scope and is not additive. Release does not equal downstream installation.',lang)
    firefox['cyber_domain_ids']=uniq(firefox['cyber_domain_ids']+[D4])
    firefox['defense_evidence_kind']='released_fixes';firefox['defense_stage_ids']=['patch','release']
    firefox['resilience_review']['new_source_verification']=True
    firefox['pipeline_metrics']=[{'id':'firefox150_fixes','value':271,'unit':'security_fix','label_ru':'Исправления в Firefox 150','label_en':'Firefox 150 security fixes','as_of':'2026-04-21','population_ru':'Первоначальная оценка Mythos / Firefox 150','population_en':'Initial Mythos evaluation / Firefox 150','source_url':p['url']}]
    rust=ev['SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES']
    for sid in ['S23','S24']:add_source(rust,sources[sid])
    rust['cyber_domain_ids']=uniq(rust.get('cyber_domain_ids',[])+[D4])
    rust['defense_evidence_kind']='upstream_artifacts';rust['defense_stage_ids']=['validation','patch']
    rust['resilience_review']['new_source_verification']=True
    rust['editorial_priority']=1
    pair(rust,'editorial_rationale','Опорный пример перехода от AI-assisted поиска к принятым upstream-исправлениям за пределами крупнейших лабораторий. Проверены два публичных PR; весь агрегат находок не перепроверен.','Core example of AI-assisted discovery reaching upstream fixes outside the largest laboratories. Two public PRs were checked; the full aggregate was not re-audited.',lang)
    # Preserve the 6 August event and its 33 historical fixes. The new observation is not backdated.
    st={'observed_at':DATE,'event_date':None,'summary_dated':'2026-08-18',
        'reporter_claimed_resolved':37,'individually_checked_upstream_examples':2,
        'aggregate_recount_performed':False,'sources':[src(sources[x]) for x in ['S22','S23','S24']]}
    pair(st,'title','rust-in-peace: отдельное наблюдение сводки и принятых исправлений',
         'rust-in-peace: separate observation of the ledger and accepted fixes',lang)
    pair(st,'summary','В сводке автора, помеченной 18 августа, указано 37 fixed/merged. Отдельно проверены upstream PR fontations #2012 (5 августа) и h2 #936 (17 августа). Это два примера принятых исправлений, не сплошная перепроверка всех 37.',
         'The author’s summary dated 18 August lists 37 fixed/merged findings. Upstream PRs fontations #2012 (5 August) and h2 #936 (17 August) were individually checked. These are two accepted-fix examples, not a complete re-audit of all 37.',lang)
    pair(st,'date_note','Исходная запись 6 августа и её 33 исправления сохранены. В журнале есть остатки прежних агрегированных итогов; новые 101 сообщения не объявляются 101 подтверждённой уязвимостью. Private и rejected не включаются автоматически в подтверждённые.',
         'The original 6 August record and its 33 fixes are preserved. The log retains remnants of earlier aggregate totals; 101 submissions are not presented as 101 confirmed vulnerabilities. Private and rejected reports are not automatically validated findings.',lang)
    rust['current_state']=st
    ev['SIG_2026_HF_FORENSIC_GUARDRAIL_ASYMMETRY']['cyber_domain_ids']=uniq(ev['SIG_2026_HF_FORENSIC_GUARDRAIL_ASYMMETRY']['cyber_domain_ids']+[D4])

def make_claim(lang):
    c={'id':CLAIM,'kind':'claim','status':'partially_verified','confidence':'B','evidence_level':'B',
       'supporting_evidence':['SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG','SIG_2026_LINUX_NETDEV_VALID_FIX_OVERLOAD','SIG_2026_CURL_821_RELEASE_CAPACITY','SIG_2026_CURL_REPORTING_PAUSE','SIG_2026_CURL_822_SECURITY_RELEASE','SIG_2026_MYTHOS_FIREFOX_271','SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES'],
       'qualifying_evidence':['SIG_2026_EBA_FRONTIER_AI_PATCH_CYCLE_ASSESSMENT','SIG_2026_BOE_PATCHING_OPERATIONAL_RISK','SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION'],
       'date_relevant':'2026','stack_layer':['cyber_security_patch'],'strange_structure':['security','knowledge'],
       'geography':['Global'],'keywords':['validated findings','maintenance capacity','patch deployment','shared remediation'],
       'arcIds':[ARC],'arcFamilyIds':[FAMILY],'edgeIds':[],'relationTypes':[],'sources':[]}
    pair(c,'title','Реальные находки растут быстрее ёмкости сопровождения в отдельных значимых проектах',
         'Valid-finding throughput exceeds maintenance capacity in selected major projects',lang)
    pair(c,'claim','К лету 2026 года в ряде значимых проектов ограничением стала не только достоверность сообщений, но и способность перерабатывать поток реальных дефектов. AI-assisted поиск вскрывает накопленный запас ошибок; проверка, назначение ответственного, исправление, выпуск и установка требуют отдельной ёмкости. Масштаб эффекта по всей отрасли и вклад ИИ во весь поток не установлены.',
         'By summer 2026, selected major projects face not only report-validity constraints but also limits on processing genuine defects. AI-assisted discovery exposes accumulated flaws; validation, ownership, patching, release and installation require separate capacity. Industry-wide magnitude and AI’s share of the entire flow are not established.',lang)
    text_ru='Не «слоп исчез»: даже после проверки остаётся обязательная инженерная работа. Отчёты, патчи, CVE и развёрнутые исправления — разные единицы. Программы помощи не доказывают измеренное снижение риска.'
    text_en='Not “slop has disappeared”: real engineering work remains after validation. Reports, patches, CVEs and deployed fixes are different units. Assistance programs do not establish measured risk reduction.'
    for key in ['safe_wording','recommended_phrasing']:pair(c,key,text_ru,text_en,lang)
    pair(c,'caveats',[text_ru],[text_en],lang)
    return c

def vocabulary(d,raw):
    f=d['cyberFramework']
    if not any(x['id']=='cooperative_program' for x in f['artifact_kinds']):
        f['artifact_kinds'].append({'id':'cooperative_program','label_ru':'Совместная отраслевая программа','label_en':'Cooperative industry program'})
    kinds=[('historical_context','Исторический контекст','Historical context'),('maintainer_report','Отчёт мейнтейнера','Maintainer report'),('released_fixes','Выпущенные исправления','Released fixes'),('provider_operational_report','Операционный отчёт поставщика','Provider operational report'),('upstream_artifacts','Принятые upstream-артефакты','Accepted upstream artifacts'),('announced_program','Анонс и обязательства','Announcement and commitments'),('draft_proposal','Проект / RFC','Draft / RFC'),('launched_pilot','Запущенный пилот','Launched pilot'),('risk_assessment','Оценка риска','Risk assessment'),('product_preview','Предварительная версия продукта','Product preview')]
    f['defense_evidence_kinds']=[{'id':id,'label_ru':ru,'label_en':en} for id,ru,en in kinds]
    stages=[('discovery','Поиск','Discovery'),('validation','Проверка','Validation'),('ownership','Ответственный','Ownership'),('coordination','Координация','Coordination'),('patch','Патч принят','Patch accepted'),('release','Исправление выпущено','Fix released'),('deployment','Установлено','Deployed'),('revalidation','Повторно проверено','Revalidated'),('recovery','Услуга восстановлена','Service restored')]
    f['defense_stages']=[{'id':id,'label_ru':ru,'label_en':en} for id,ru,en in stages]
    f['resilience_tracks']=copy.deepcopy(raw['tracks'])
    for t in f['resilience_tracks']:
        t['event_ids']=[e['id'] for e in d['events'] if t['id'] in e.get('resilience_track_ids',[])]
    f['resilience_claim_id']=CLAIM
    f['resilience_note_ru']='Дорожки чтения, не новые домены и не шкала зрелости. Этапы обозначают предмет свидетельства, а не автоматически достигнутый результат. Кандидаты, проверенные находки, сообщения, патчи и установки не образуют общую последовательную воронку.'
    f['resilience_note_en']='Reading tracks, not new domains or a maturity scale. Stage tags identify what evidence concerns, not an automatically achieved outcome. Candidates, validated findings, reports, patches and installations do not form one shared sequential funnel.'
    f['updated_at']=DATE

def edges(d,raw):
    new=[]; signatures={(e['source'],e['target'],e['relation']) for e in d['edges']}
    def add(a,b,rel,ru,en,cls='editorial_relationship',target_kind='evidence',source_kind='evidence'):
        if (a,b,rel) in signatures:return
        signatures.add((a,b,rel))
        new.append({'id':f'EDGE_V034_RESILIENCE_{len(new)+1:03d}','source':a,'target':b,'source_kind':source_kind,'target_kind':target_kind,'relation':rel,'arc_id':ARC,'arc_family_id':FAMILY,'strength':'moderate','evidence_level':'B','visual_lane':'cyber_security_patch','style':'dashed' if cls=='thematic' else 'solid','summary_ru':ru,'summary_en':en,'kind':'edge','is_auto':False,'relationship_class':cls})
    for e in raw['events']:
        add(e['id'],ARC,'part_of_arc','Тематическая принадлежность; не доказательство эффективности всей рамки.','Thematic membership, not proof of framework-wide effectiveness.','thematic','story_arc')
    c=next(c for c in d['claims'] if c['id']==CLAIM)
    for id in c['supporting_evidence']:
        add(id,CLAIM,'supports_with_scope','Поддерживает ограниченный тезис о реальной работе и ёмкости сопровождения; метрики и популяции различаются.','Supports the scoped claim about genuine work and maintenance capacity; units and populations differ.','evidentiary_support','claim')
    for id in c['qualifying_evidence']:
        add(id,CLAIM,'qualifies','Ограничивает перенос результатов на частоту атак, все отрасли или доказанную эффективность.','Constrains extrapolation to attack incidence, all sectors or demonstrated effectiveness.','evidentiary_qualification','claim')
    add(CLAIM,ARC,'supports_arc','Ограниченный механизм потока находок внутри более широкой рамки устойчивости.','A scoped findings-throughput mechanism within the wider resilience framework.','editorial_relationship','story_arc','claim')
    links=[
      ('SIG_2026_CURL_BOUNTY_CLOSURE','SIG_2026_CURL_HIGH_QUALITY_TRANSITION','updated_by','Историческое изменение состава сообщений; причинность отмены выплат не установлена.','A historical change in report composition; bounty-removal causality is not established.'),
      ('SIG_2026_CURL_HIGH_QUALITY_TRANSITION','SIG_2026_CURL_821_RELEASE_CAPACITY','updated_by','После апрельской оценки — выпущенные исправления и вытеснение других работ.','The April assessment is followed by released fixes and displaced work.'),
      ('SIG_2026_CURL_821_RELEASE_CAPACITY','SIG_2026_CURL_REPORTING_PAUSE','context_for','Контекст операционной паузы; не оценка её причинной эффективности.','Context for the operating pause, not an estimate of its causal effectiveness.'),
      ('SIG_2026_CURL_REPORTING_PAUSE','SIG_2026_CURL_822_SECURITY_RELEASE','updated_by','После подтверждённой паузы исправления продолжают выходить.','Fixes continue to ship after the confirmed pause.'),
      ('SIG_2026_LINUX_NETDEV_VALID_FIX_OVERLOAD','SIG_2026_CURL_821_RELEASE_CAPACITY','parallel','Сопоставимые ограничения сопровождения; количество патчей не сравнивается с количеством уязвимостей.','Comparable maintenance constraints; patch counts are not compared to vulnerability counts.'),
      ('SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG','SIG_2026_AKRITES_SHARED_REMEDIATION','context_for','Подтверждённый backlog делает совместное исправление релевантным; это не доказательство причины запуска Akrites.','The validated backlog makes shared repair relevant; this does not establish why Akrites launched.'),
      ('SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES','SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG','parallel','AI-assisted поиск доходит до принятых исправлений в разных организационных моделях.','AI-assisted discovery reaches accepted fixes through different organizational models.'),
      ('SIG_2026_MYTHOS_FIREFOX_271','SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG','context_for','Отдельный партнёрский результат и агрегированный dashboard имеют разный охват; не суммируются.','A partner result and aggregate dashboard have different scopes and are not additive.'),
      ('SIG_2026_CODEX_SECURITY_VALIDATION_PREVIEW','SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION','context_for','Продуктовый этап валидации и отдельный операционный самоотчёт.','Product-level validation and a separate operational self-report.'),
      ('SIG_2026_BOE_FRONTIER_AI_HARNESS_ENGINEERING','SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION','parallel','Окружение, контекст и проверка результата; не доказанная зависимость двух инициатив.','Environment, context and outcome checks; no established dependency between the initiatives.'),
      ('SIG_2026_HF_FORENSIC_GUARDRAIL_ASYMMETRY','SIG_2026_OPEN_SECURE_AI_ALLIANCE','context_for','Инцидент цитируется участниками альянса; их пересказ не является независимым подтверждением.','Alliance participants cite the incident; their retelling is not independent corroboration.'),
      ('SIG_2026_OPEN_SECURE_AI_ALLIANCE','SIG_2026_SAFE_INCIDENT_LEARNING_RFC','updated_by','После анонса альянса опубликован конкретный RFC; его выполнение не установлено.','The alliance announcement is followed by a concrete RFC; implementation is not established.'),
      ('SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE','SIG_2026_SAFE_INCIDENT_LEARNING_RFC','context_for','Класс отказов, для которого RFC предлагает сохранение доказательств и проверяемые контроли.','A failure class for which the RFC proposes evidence preservation and testable controls.'),
      ('SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS','SIG_2026_SAFE_INCIDENT_LEARNING_RFC','context_for','Сопоставление требований к разбору, без утверждения об участии AISI в SAFE.','Comparison of review requirements, not a claim that AISI participates in SAFE.'),
      ('SIG_2026_OPENAI_COLLECTIVE_CYBER_DEFENSE_LETTER','SIG_2026_DAYBREAK_FRONTLINE_SUBSIDIZED_ACCESS','updated_by','Призыв дополнен объявленным обязательством по доступу и поддержке.','A call is followed by an announced access-and-support commitment.'),
      ('SIG_2026_DAYBREAK_FRONTLINE_SUBSIDIZED_ACCESS','SIG_2026_PROJECT_WATERSHED_250_PILOT','parallel','Разные программы доставки помощи; их бюджеты, участники и результаты не объединяются.','Distinct delivery programs; budgets, participants and outcomes are not pooled.'),
      ('SIG_2026_ORACLE_AI_ASSISTED_RECORD_PATCH_RELEASE','SIG_2026_BOE_PATCHING_OPERATIONAL_RISK','context_for','Объём исправлений сопоставлен с риском ускоренных изменений; конкретный системный сбой не установлен.','Patch volume is compared with accelerated-change risk; no specific systemic outage is established.'),
      ('SIG_2026_RAPID7_Q2_PATCH_CYCLE_COMPRESSION','SIG_2026_BOE_PATCHING_OPERATIONAL_RISK','context_for','Окно атаки и безопасная скорость изменений — разные ограничения.','The attack window and safe change speed are separate constraints.'),
      ('SIG_2026_AKRITES_SHARED_REMEDIATION','SIG_2026_US_GOLD_EAGLE_LAUNCH','parallel','Отраслевой и государственный механизмы координации; эффективность не переносится между ними.','Industry and government coordination mechanisms; effectiveness is not transferred between them.'),
    ]
    for args in links:add(*args)
    d['edges'].extend(new);attach_edge_links(d,{x['id'] for x in new})
    return [x['id'] for x in new]

def patch_arcs(d,newids):
    lang=d['language'];a=next(x for x in d['arcs'] if x['id']==ARC)
    pair(a,'thesis','Киберустойчивость ИИ включает безопасность систем, управление кибервозможностями, защитный цикл и межорганизационную координацию, отраслевую устойчивость и защиту решений и зависимостей. Реальные находки создают нагрузку после фильтра недостоверных сообщений: требуется довести результат до проверенного устранения, не нарушив критическую услугу. Доступ, право действовать и операционная ёмкость — отдельные ограничения.',
         'AI cyber resilience includes secure systems, capability governance, the defensive lifecycle and cross-organization coordination, sector resilience, and security of decisions and dependencies. Valid findings create work after invalid reports are filtered: results must reach verified remediation without disrupting essential services. Access, authority and operational capacity are separate constraints.',lang)
    a['key_nodes']=uniq(a['key_nodes']+newids+[CLAIM]);a['resilience_track_ids']=[x['id'] for x in d['cyberFramework']['resilience_tracks']]
    a['v034_note_ru']='Новый слой не заменяет прочие домены и не превращает альянсы, RFC и пилоты в измеренные результаты.'
    a['v034_note_en']='The new layer does not replace other domains or turn alliances, RFCs and pilots into measured outcomes.'
    b=next(x for x in d['arcs'] if x['id']=='ARC_CYBER_CLAIM_TO_CAVEAT')
    b['thesis_legacy_v033']={l:b.get('thesis_'+l,b.get('thesis','')) for l in ['ru','en']}
    for l in ['ru','en']:
        extra=(' После проверки остаётся поток реальных дефектов; пределы сопровождения и доставки исправлений рассматриваются отдельно от автономности атак.' if l=='ru' else ' Valid defects remain after triage; maintenance and patch-delivery constraints are assessed separately from attack autonomy.')
        b['thesis_'+l]=b['thesis_legacy_v033'][l]+extra
    b['thesis']=b['thesis_'+lang]

def migrate(d,raw):
    if d['meta']['version']!='0.33':raise ValueError('Expected v0.33 input')
    original=copy.deepcopy(d); lang=d['language'];sources={s['id']:s for s in raw['sources']}
    ids=[e['id'] for e in raw['events']]
    if len(ids)!=15 or len(set(ids))!=15 or set(ids)&{e['id'] for e in d['events']}:raise ValueError('Candidate collision / count')
    patch_existing(d,raw,sources)
    d['events'].extend(event_record(r,lang,sources) for r in raw['events'])
    d['claims'].append(make_claim(lang));vocabulary(d,raw)
    added=edges(d,raw);patch_arcs(d,ids)
    rebuild_sources(d);rebuild_counts(d)
    d['meta'].update(version='0.34',updated_at=DATE,schema_version='ai_stack_structural_power.v0.34.0-2026-09-06')
    entry={'version':'0.34','date':DATE,'description':'Validated-finding throughput, maintenance capacity, verified remediation and sector delivery; 15 bilingual records, one scoped claim, six local reading tracks, no new top-level arc.','added_evidence':15,'added_claims':1,'added_story_arcs':0,'added_story_edges':len(added),'updated_existing_evidence':list(raw['existing_track_tags'])}
    d['meta']['changelog']=[entry]+d['meta']['changelog']
    su=d['summary'];cnt=Counter(c['status'] for c in d['claims'])
    for key,collection in [('total_evidence_items','events'),('total_timeline_items','events'),('total_story_arcs','arcs'),('total_story_edges','edges'),('total_events','events'),('total_claims','claims'),('total_claim_checks','claimChecks'),('total_arcs','arcs'),('total_edges','edges'),('total_thesis_nodes','thesisNodes')]:su[key]=len(d[collection])
    su['cyber_framework_event_count']=sum(bool(e.get('primary_domain_id')) for e in d['events']);su['source_count']=len(d['sourceIndex']);su['claim_status_counts']=dict(cnt);su['stats'].update(cnt);su['stats']['total_claims']=len(d['claims'])
    finding={'ru':'ПРОПУСКНАЯ СПОСОБНОСТЬ ЗАЩИТЫ (v0.34): в ряде значимых проектов уже подтверждённые находки перегружают сопровождение. Разделены проверка, патч, выпуск, установка и восстановление; анонсы помощи не считаются доказанной эффективностью.', 'en':'DEFENSIVE CAPACITY (v0.34): validated findings already strain maintenance in selected major projects. Validation, patching, release, deployment and recovery are separate; assistance announcements are not evidence of effectiveness.'}
    su['key_findings']=[finding[lang]]+su['key_findings']
    d['presentation']['editorial_version']='0.34'
    d['presentation']['corrections']=[finding[lang]]+d['presentation'].get('corrections',[])
    d['presentation']['release_notes']=[{'title':('Поток реальных находок' if lang=='ru' else 'Valid-finding throughput'),'text':finding[lang]},{'title':('Шесть дорожек чтения' if lang=='ru' else 'Six reading tracks'),'text':('Сопровождение, проверенное устранение, общая работа, обучение на инцидентах, доступ и восстановление.' if lang=='ru' else 'Maintenance, verified remediation, shared repair, incident learning, access and recovery.')}]
    d['migrationAudit'].update(version='0.34',v034_base_commit=raw['meta']['base_commit'],v034_base_sha256=raw['meta']['base_sha256'][lang],v034_added_event_ids=ids,v034_added_claim_ids=[CLAIM],v034_added_edge_ids=added,v034_updated_event_ids=list(raw['existing_track_tags']),v034_source_package='review/resilience-throughput')
    d['factcheckAudit']['v034_scope']={'date':DATE,'accepted_records':15,'source_records':24,'deferred_records':len(raw['deferred']),'full_legacy_source_reaudit':False,'independent_experiment_replication':False,'note':'Primary publications and two upstream PRs reviewed; four candidates deferred. Existing metrics retain their original dates.'}
    d['connectivity'].update(edge_count=len(d['edges']),story_edges=len(d['edges']),last_recomputed=DATE,v0_34_added_evidence=15,v0_34_added_claims=1,v0_34_added_edges=len(added))
    d['referenceIntegrity']=references(d)
    if not d['referenceIntegrity']['valid']:raise ValueError(d['referenceIntegrity'])
    olddates={e['id']:e['date'] for e in original['events']};assert all(olddates.get(e['id'],e['date'])==e['date'] for e in d['events'])
    return d

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT,help='directory containing the exact v0.33 bilingual JSON pair')
    parser.add_argument('--output',type=Path,required=True,help='destination directory for the migrated JSON pair')
    args=parser.parse_args();raw=json.loads((PACKAGE/'candidates.json').read_text())
    loaded={}
    for lang in ['ru','en']:
        path=args.root/f'ai_power_storygraph_{lang}.json';data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=raw['meta']['base_sha256'][lang]:raise SystemExit(f'{path.name}: expected pinned v0.33 SHA-256; refusing input {digest}')
        loaded[lang]=json.loads(data)
    rendered={lang:(json.dumps(migrate(d,raw),ensure_ascii=False,indent=2)+'\n').encode() for lang,d in loaded.items()}
    args.output.mkdir(parents=True,exist_ok=True)
    for lang,data in rendered.items():
        path=args.output/f'ai_power_storygraph_{lang}.json';temp=path.with_suffix('.json.tmp');temp.write_bytes(data);os.replace(temp,path)
        d=json.loads(data);print(lang,len(d['events']),'events',len(d['claims']),'claims',len(d['edges']),'edges',len(d['sourceIndex']),'sources')
if __name__=='__main__':main()
