#!/usr/bin/env python3
"""Pinned v0.48 -> v0.49: access controls, a disclosure correction and compute finance."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "review/october-access-finance-2026"
VERSION, DATE = "0.49", "2026-10-27"
BASE_HASH = {
    "ru": "40f8d5b4f51342d94bb7fdb3e3b2e5e45cc53aaf18c8de9f2383b3f7c9193025",
    "en": "f40e7ea9b8bcb880b6b3c3335555b6537a9742037a340265774f94d1505b2550",
}
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
ACCESS = "ARC_QUIET_ACCESS_CONTROL"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
CYBER = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
OPEN = "ARC_OPEN_WEIGHT_EXIT_OR_DEPENDENCE"
CLOUD = "ARC_CLOUD_CAPACITY_VENDOR_LOCKIN"
CAPITAL = "ARC_CAPITAL_MIX_PUBLIC_PRIVATE"
DECISION = "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION"
DNS = "SIG_2026_OPENAI_DNS_ESCAPE_SHUTDOWN_FAILURE"
ANTHROPIC = "SIG_2026_ANTHROPIC_UNINTENDED_ACTIONS_INTERNET_PAUSE"
DOMAIN1 = "CYBER_DOMAIN_01_SECURE_SYSTEMS"
DOMAIN2 = "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"
DOMAIN5 = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"

SOURCE_ROWS = [
    ("openai", "OpenAI", "Securing our frontier model training environment", "2026-10-23", "https://openai.com/index/securing-our-frontier-model-training-environment/", "provider containment and resumption report"),
    ("svt", "SVT", "AI-tjanster sparras pa Regeringskansliet", "2026-10-23", "https://www.svt.se/nyheter/inrikes/ai-tjanster-sparras-pa-regeringskansliet", "original reporting with Government Offices email; updated 2026-10-24"),
    ("sr", "Sveriges Radio / Ekot", "Regeringskansliet sparrar AI-tjansterna Chat GPT och Claude", "2026-10-23", "https://www.sverigesradio.se/artikel/chat-gpt-och-claude-forbjuder-regeringskansliet", "original reporting on internal policy and press-office response"),
    ("georgia", "Georgia Secretary of State", "Anthropic AI Agent Accessed Publicly Available Information, Georgia Elections Remain Secure", "2026-10-26", "https://sos.ga.gov/news/anthropic-ai-agent-accessed-publicly-available-information-georgia-elections-remain-secure", "official correction; account of communications with Anthropic"),
    ("axios", "Axios", "Anthropic model accessed voter information", "2026-10-25", "https://www.axios.com/2026/10/25/anthropic-claude-georgia-voter-data", "initial reporting; paywall claim subsequently disputed by state"),
    ("anthropic", "Anthropic", "Investigating unintended model actions in our evaluations and internal use", "2026-10-09", "https://www.anthropic.com/research/investigating-unintended-model-actions", "provider disclosure; unnamed state-agency example"),
    ("spacex", "SpaceX", "SpaceX secures $40 billion in the largest GPU financing ever", "2026-10-26", "https://ir.spacex.com/updates/releases-details/2026/SPACEX-SECURES-40-BILLION-IN-THE-LARGEST-GPU-FINANCING-EVER-2026-EnDqGhTAB3/default.aspx", "issuer announcement of binding commitment; lease not yet closed"),
    ("ibm", "IBM Research", "How llm-d makes the most of the hardware you already have", "2026-09-08", "https://research.ibm.com/blog/running-open-models-on-h100-gpus-with-llmd", "provider deployment and benchmark report"),
    ("ibm_call", "IBM", "IBM 3Q26 Earnings Transcript", "2026-10-21", "https://www.ibm.com/downloads/documents/us-en/17f55bd310d5fdd0", "official earnings-call transcript; executive estimate, not an independent benchmark"),
    ("mozilla", "Mozilla", "The State of Open Source AI, v1.1", "2026-09-15", "https://stateofopensource.ai/", "research synthesis; September 1 data snapshot; open-AI advocate"),
]
SOURCES = {key: dict(name=name, title=title, date=date, url=url, source_class=kind,
    type="Media / report" if key in {"svt", "sr", "axios"} else "Research / technical" if key in {"ibm", "mozilla"} else "Primary source",
    primary_or_secondary="secondary" if key in {"svt", "sr", "axios"} else "primary",
    checked_at=DATE, verification_method="source_account_reviewed; no_independent_replication")
    for key, name, title, date, url, kind in SOURCE_ROWS}


def record(key, date, source_ids, actors, title, summary, caveat, arcs, *,
           layers, structures, artifact, contexts, jurisdictions=None, domains=None,
           force="not_applicable", stage="published", basis="publication_date", numbers=None,
           priority=2, confidence="B"):
    return dict(id="SIG_2026_"+key, date=date, source_ids=source_ids, actors=actors,
        title_ru=title[0], title_en=title[1], summary_ru=summary[0], summary_en=summary[1],
        caveat_ru=caveat[0], caveat_en=caveat[1], safe_ru=summary[0], safe_en=summary[1],
        arcs=arcs, stack_layers=layers, structures=structures, artifact=artifact,
        contexts=contexts, jurisdictions=jurisdictions or [], domains=domains or [],
        primary_domain=(domains or [""])[0], roles=["AI_ROLE_PROTECTED_SYSTEM"] if domains else [],
        actor_types=["government"] if key.startswith(("SWEDEN", "GEORGIA")) else ["research"] if key.startswith("MOZILLA") else ["company"],
        force=force, stage=stage, date_basis=basis, date_status="source_backed",
        numbers=numbers or {}, priority=priority, confidence=confidence, status="verified_as_reported",
        research_questions=["RQ5"], method="source_review; no_independent_audit",
        delegation="control_requirement" if key.startswith("OPENAI") else "not_applicable")


RECORDS = [
    record("OPENAI_FRONTIER_RL_RESUMPTION_OFFLINE", "2026-10-01", ["openai"], ["OpenAI"],
        ("OpenAI возобновила обучение после 11-дневной паузы с усиленной изоляцией", "OpenAI resumed frontier training after an 11-day pause with stronger containment"),
        ("В отчёте от 23 октября OpenAI датирует возобновление обучения с подкреплением и внутренних запусков 1 октября. После DNS-инцидента 20 сентября компания усилила изоляцию и мониторинг; для обучения использует кешированную веб-среду без доступа к живому интернету.",
         "In its October 23 report, OpenAI dates the resumption of frontier RL and internal inference to October 1. Following the September 20 DNS incident it strengthened containment and monitoring; training uses a cached web environment without live-internet access."),
        ("Это отчёт поставщика, не независимый аудит. Не остановка всех продуктов и не доказательство возобновления именно проблемного запуска. Дата введения всей новой политики отдельно не установлена; дата карточки относится к возобновлению работ.",
         "Provider report, not an independent audit. Not a shutdown of all products or proof that the specific problematic training run resumed. The full policy's introduction date is not separately established; the record dates workload resumption."),
        [PACING, CYBER, COG], layers=["cyber_security_patch", "governance_law", "model_weights"],
        structures=["security", "knowledge", "production"], artifact="provider_policy",
        contexts=["internal_deployment", "governance_document"], jurisdictions=["US"], domains=[DOMAIN2, DOMAIN1],
        stage="reported", basis="workload_resumption_date; disclosed_2026-10-23", numbers={"pause_days":11}, priority=1),
    record("SWEDEN_GOVERNMENT_AI_ACCESS_CHANNELS", "2026-10-26", ["svt", "sr"], ["Swedish Government Offices"],
        ("Аппарат правительства Швеции ограничил публичные ИИ-интерфейсы, сохранив внутренний доступ", "Sweden's Government Offices restricted public AI interfaces while retaining internal access"),
        ("Аппарат правительства сообщил SVT о блокировке веб-интерфейсов ChatGPT и Claude на рабочих компьютерах с 26 октября. Доступ к этим моделям через Intric сохраняется; Copilot остаётся одобренным инструментом. Объяснение связано с договорами и информационной безопасностью.",
         "The Government Offices told SVT that ChatGPT and Claude web interfaces would be blocked on work computers from October 26. Access through Intric remains available; Copilot is approved. The stated rationale concerns contracts and information security."),
        ("Ведомственная политика, не запрет моделей, продаж или использования во всей Швеции. Источники цитируют ответ ведомства и внутренние материалы; отдельный публичный нормативный акт и фактическая работа блокировки не проверены. Связь с инцидентами OpenAI не установлена.",
         "Institutional policy, not a nationwide model, sales or workplace ban. Sources quote an agency response and internal material; no separate public legal instrument or live enforcement test was reviewed. No causal link to OpenAI's incidents is established."),
        [ACCESS, DECISION], layers=["governance_law", "cloud_inference", "decision_support_cognition"],
        structures=["security", "knowledge"], artifact="government_order", contexts=["governance_document"],
        jurisdictions=["Sweden"], domains=[DOMAIN5, DOMAIN1], force="binding", stage="reported",
        basis="announced_effective_date; enforcement_not_independently_observed", priority=1),
    record("GEORGIA_DATA_HUB_PAYWALL_CORRECTION", "2026-10-26", ["georgia", "axios", "anthropic"], ["Georgia Secretary of State", "Anthropic"],
        ("Джорджия опровергла обход платного доступа агентом Claude", "Georgia disputed the claim that Claude bypassed a data paywall"),
        ("Офис госсекретаря Джорджии сообщил, что Claude обращался к бесплатному публичному Data Hub, а не к реестру избирателей. По заявлению ведомства, 26 октября Anthropic подтвердила отсутствие обхода платного доступа. Это уточнение прежнего раскрытия, не новый инцидент.",
         "Georgia's Secretary of State said Claude accessed the free public Data Hub, not the voter registration system. The office said Anthropic confirmed on October 26 that no paywall was bypassed. This updates an earlier disclosure; it is not a new incident."),
        ("Подтверждение Anthropic здесь передано самим ведомством; полная техническая трасса не опубликована. Первоначальная трактовка Anthropic и Axios сохранена как история раскрытия, но не как установленный обход. Самостоятельный запрос агента не равен несанкционированному доступу.",
         "Anthropic's confirmation is relayed by the agency; a complete technical trace is not public. The initial Anthropic/Axios interpretation is retained as disclosure history, not an established bypass. An unrequested agent action is not necessarily unauthorized system access."),
        [COG, CYBER], layers=["cyber_security_patch", "data_telemetry", "governance_law"],
        structures=["security", "knowledge"], artifact="commentary", contexts=["governance_document"],
        jurisdictions=["US"], domains=[DOMAIN5], basis="official_correction_date; underlying_access_date_unknown"),
    record("SPACEX_APOLLO_GPU_LEASE_COMMITMENT", "2026-10-26", ["spacex"], ["SpaceX", "Apollo Global Management", "Goldman Sachs", "NVIDIA", "BlackRock", "KKR"],
        ("SpaceX объявила обязательства по лизингу GPU примерно на $40 млрд", "SpaceX announced commitments for an approximately $40 billion GPU finance lease"),
        ("SpaceX сообщила об обязательстве заключить финансовый лизинг GPU и оборудования со структурой под управлением Apollo. Заявлены NVIDIA Vera Rubin; в финансировании участвуют Goldman Sachs, BlackRock и KKR. Закрытие ожидается до конца 2026 года, поставки и начало лизинговых периодов в первой половине 2027-го.",
         "SpaceX announced a binding commitment for a GPU and equipment finance lease with an Apollo-managed entity. NVIDIA Vera Rubin is specified; Goldman Sachs, BlackRock and KKR participate in financing. Closing is expected before year-end 2026, with deliveries and lease schedules starting in the first half of 2027."),
        ("Обязательство по финансированию не означает закрытую сделку, полученные деньги или работающие GPU. Условия закрытия сохраняются. Это не подтверждает прекращение кредитования всех других ИИ-компаний и не устанавливает доходность вложений.",
         "A financing commitment is not a closed transaction, cash received or operational GPUs. Closing conditions remain. It does not establish that lending to all other AI firms has stopped or verify investment returns."),
        [CAPITAL, CLOUD], layers=["finance_rent", "energy_compute_chips", "cloud_inference"],
        structures=["finance", "production"], artifact="market_observation", contexts=["governance_document"],
        jurisdictions=["US"], force="contractual", stage="announced", confidence="A",
        numbers={"expected_finance_lease_principal_usd":40000000000, "transaction_closed":False}),
    record("IBM_LLMD_OPEN_MODEL_SERVING", "2026-09-08", ["ibm"], ["IBM", "Red Hat"],
        ("IBM и Red Hat развернули GLM-5.2 на 544 H100 с открытым ПО llm-d", "IBM and Red Hat deployed GLM-5.2 on 544 H100s with open llm-d serving software"),
        ("IBM Research описала внутреннее развёртывание GLM-5.2 и испытания llm-d на 544 H100. На выбранных агентных нагрузках авторы оценили стоимость токена в 5-10 раз ниже коммерческих API при текущих облачных тарифах. Существенную роль сыграло повторное использование контекста.",
         "IBM Research described an internal GLM-5.2 deployment and llm-d tests on 544 H100s. For selected agentic workloads, the authors estimated token costs 5-10 times below commercial APIs at current cloud rental rates. Context reuse was a major contributor."),
        ("Измерения и расчёт поставщика, не независимая оценка полной стоимости владения. Результат зависит от нагрузки, кеширования, загрузки оборудования и эксплуатации. Снижение цены токена не доказывает равенство качества моделей или доступность такого кластера малым организациям.",
         "Provider measurements and costing, not an independent total-cost-of-ownership assessment. Results depend on workload, caching, utilization and operations. Cheaper tokens do not prove model-quality parity or affordability for small organizations."),
        [OPEN, CLOUD], layers=["model_weights", "cloud_inference", "energy_compute_chips"],
        structures=["production", "knowledge", "finance"], artifact="deployment", contexts=["internal_deployment", "benchmark"],
        domains=[DOMAIN5], stage="reported", numbers={"h100_gpus":544, "reported_cost_reduction_multiple_min":5, "reported_cost_reduction_multiple_max":10}),
    record("IBM_OPEN_WEIGHT_ECONOMICS_POSITION", "2026-10-21", ["ibm_call"], ["IBM"],
        ("IBM связала выбор открытых моделей с ценой и контролем данных", "IBM linked open-weight adoption to cost and data control"),
        ("На квартальном звонке Арвинд Кришна оценил открытые модели как примерно на 90% столь же эффективные при 10-25% стоимости токена передовых моделей. Он связал внутреннее развёртывание с контролем данных и журналов, одновременно указав на дефицит инженерных компетенций.",
         "On IBM's earnings call, Arvind Krishna estimated open models at roughly 90% of frontier effectiveness for 10-25% of token cost. He linked private deployment to control of data and logs while acknowledging missing engineering skills."),
        ("Это публичная позиция заинтересованного поставщика. В ответе не названы модели, набор испытаний и воспроизводимый расчёт для 90%. Не считать это независимым доказательством паритета, универсальной экономии или отдельным измерением кейса llm-d.",
         "This is an interested supplier's public position. The answer specifies neither models nor a reproducible evaluation for the 90% figure. It is not independent proof of parity, universal savings or a separate measurement of the llm-d case."),
        [OPEN, CLOUD], layers=["model_weights", "cloud_inference", "data_telemetry"],
        structures=["knowledge", "production", "finance"], artifact="commentary", contexts=["governance_document"]),
    record("MOZILLA_OPEN_MODEL_LAG_SNAPSHOT", "2026-09-15", ["mozilla"], ["Mozilla"],
        ("Mozilla оценила отставание открытых моделей примерно в 4,4 месяца на данных METR", "Mozilla estimated an approximately 4.4-month open-model lag on METR data"),
        ("В сентябрьском выпуске State of Open Source AI Mozilla оценила отставание открытых моделей примерно в 4,4 месяца на данных METR. Срез на 1 сентября показывает неодинаковую близость по задачам и сохраняющиеся ограничения инфраструктуры и внедрения.",
         "In its September State of Open Source AI report, Mozilla estimated an approximately 4.4-month open-model lag using METR data. The September 1 snapshot shows task-dependent proximity and continuing infrastructure and deployment limitations."),
        ("Это расчёт Mozilla по выбранным данным, не постоянная величина и не всеобщий паритет. Mozilla поддерживает открытый ИИ; доступные веса не равны полностью открытому исходному процессу. Срез сентября не описывает автоматически состояние октября.",
         "This is Mozilla's fit to selected data, not a permanent gap or universal parity. Mozilla advocates open AI; downloadable weights do not imply a fully open development process. A September snapshot does not automatically describe October."),
        [OPEN], layers=["model_weights", "cloud_inference"], structures=["knowledge", "production"],
        artifact="research", contexts=["ecosystem_measurement"], numbers={"estimated_lag_months":4.4}),
]
IDS = {r["source_ids"][0]:r["id"] for r in RECORDS}


def migrate(doc):
    if doc["meta"]["version"] != "0.48":
        raise ValueError("Expected v0.48; refusing repeated or out-of-order migration")
    old, lang = copy.deepcopy(doc), doc["language"]
    events, arcs = ({x["id"]:x for x in doc[k]} for k in ["events", "arcs"])
    for raw in RECORDS:
        if raw["id"] in events:
            raise ValueError("Duplicate event: "+raw["id"])
        event = event_record(raw, lang, SOURCES, doc)
        event.update(date_precision="day", story_primary_arc_id=raw["arcs"][0], story_secondary_arc_ids=raw["arcs"][1:],
            research_updates=["october-access-finance-2026"], behavioral_status=[],
            geographic_scopes=["National"] if raw["jurisdictions"] else ["International"],
            classification_review=dict(date=DATE, source_content_checked=True, independent_source_reverification=False, independent_replication=False))
        if raw["primary_domain"]==DOMAIN5:
            event["cyber_subdomain_ids"]=["CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION" if raw["id"]==IDS["georgia"] else "CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"]
        for key in ["notes", "corroboration_needed", "claim_challenged"]:
            pair(event, key, "", "", lang)
        pair(event, "scope", raw["summary_ru"], raw["summary_en"], lang)
        pair(event, "editorial_rationale", raw["caveat_ru"], raw["caveat_en"], lang)
        pair(event, "role_basis", "Классификация относится к условиям доступа, эксплуатации или оценке свидетельств, а не к доказанной атаке.", "Classification concerns access conditions, operations or evidence assessment, not an established attack.", lang)
        event["governance_scale"]="institutional_access_and_infrastructure"
        if raw["id"]==IDS["spacex"]:
            event["money_status"]="binding_commitment; transaction_subject_to_closing"
        if raw["id"]==IDS["mozilla"]:
            pair(event,"observation_period","Срез данных: 1 сентября 2026 года.","Data snapshot: September 1, 2026.",lang)
        doc["events"].append(event)
        events[event["id"]]=event

    # Keep the incident's historical date and narrative; attach the later state separately.
    for eid, source, ru, en in [
        (DNS, "openai", "Обновление от 23 октября: OpenAI сообщила о возобновлении обучения с подкреплением и внутренних запусков 1 октября после 11 дней паузы. Это не означает возобновление конкретного остановленного запуска. Обучение передовых моделей ведётся без доступа к живому интернету.",
         "October 23 update: OpenAI reported resuming frontier RL and internal inference on October 1 after an 11-day pause. This does not establish resumption of the specific stopped run. Frontier training operates without live-internet access."),
        (ANTHROPIC, "georgia", "Уточнение от 26 октября: офис госсекретаря Джорджии сообщил, что эпизод с его Data Hub не включал обход платного доступа или доступ к реестру избирателей, и передал подтверждение Anthropic. Этот эпизод нельзя считать подтверждённым обходом. Уточнение не опровергает остальные случаи отчёта от 9 октября.",
         "October 26 clarification: Georgia's Secretary of State said the Data Hub episode involved neither a paywall bypass nor access to the voter register, and relayed Anthropic's confirmation. This episode must not be counted as an established bypass. The clarification does not refute the other October 9 cases."),
    ]:
        node=events[eid]
        prior={k:copy.deepcopy(v) for k,v in node.items() if k.startswith("current_state")}
        if prior:
            node.setdefault("state_history",[]).append(prior)
        pair(node,"current_state",ru,en,lang)
        node["current_state_as_of"]=SOURCES[source]["date"]
        add_source(node,SOURCES[source])
        pair(node,"caveat",node["caveat_ru"]+" "+ru,node["caveat_en"]+" "+en,lang)
        pair(node,"caveats",[node["caveat_ru"]],[node["caveat_en"]],lang)
        if eid==ANTHROPIC:
            pair(node,"safe_wording",node["safe_wording_ru"]+" "+ru,node["safe_wording_en"]+" "+en,lang)

    edges=[]
    def edge(source,target,relation,arc,ru,en,relationship="evidential",target_kind="evidence"):
        item=dict(id=f"EDGE_V049_ACCESS_{len(edges)+1:03d}",source=source,target=target,source_kind="evidence",target_kind=target_kind,
            relation=relation,arc_id=arc,arc_family_id=arcs[arc]["family_id"],strength="moderate",evidence_level="B",visual_lane="governance_law",
            kind="edge",is_auto=False,style="solid" if relationship=="evidential" else "dashed",relationship_class=relationship)
        pair(item,"summary",ru,en,lang)
        edges.append(item)
    for raw in RECORDS:
        for aid in raw["arcs"]:
            edge(raw["id"],aid,"part_of_arc",aid,"Тематическая принадлежность, не доказательство всей арки.","Thematic membership, not proof of the whole arc.","thematic","arc")
            arcs[aid]["key_nodes"]=uniq(arcs[aid]["key_nodes"]+[raw["id"]])
    edge(IDS["openai"],DNS,"updates",PACING,"Поздний отчёт уточняет продолжительность паузы и условия возобновления, не создавая второй DNS-инцидент.","The later report updates pause duration and resumption conditions without creating a second DNS incident.")
    edge(IDS["georgia"],ANTHROPIC,"qualifies",COG,"Уточнение относится к одному эпизоду с данными штата, а не ко всему набору раскрытых действий.","The clarification concerns one state-data episode, not the entire set of disclosed actions.")
    edge(IDS["ibm_call"],IDS["ibm"],"context_for",OPEN,"Позиция руководителя и технический кейс одного поставщика не являются независимыми измерениями одной величины.","An executive position and the same supplier's technical case are not independent measurements of one quantity.","editorial_relationship")
    edge(IDS["mozilla"],"SIG_2025_AISI_OPEN_CLOSED_MODEL_LAG","context_for",OPEN,"Разные срезы, методы и наборы задач: не единый сопоставимый временной ряд.","Different snapshots, methods and task sets; not one directly comparable time series.","editorial_relationship")
    edge(IDS["georgia"],"CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE","qualifies",COG,"Первоначальное сообщение не следует считать установленным нарушением границы доступа после официального уточнения.","An initial report should not count as an established access-boundary violation after the official clarification.",target_kind="claim")
    edge(IDS["spacex"],IDS["ibm"],"context_for",CAPITAL,"Финансирование GPU-инфраструктуры и стоимость эксплуатации модели — разные показатели; оба зависят от материальной инфраструктуры.","GPU infrastructure financing and model-serving economics are different measures; both depend on physical infrastructure.","editorial_relationship")
    doc["edges"].extend(edges)
    attach_edge_links(doc,{e["id"] for e in edges})
    touched={aid for raw in RECORDS for aid in raw["arcs"]}
    for aid in touched:
        arc=arcs[aid]
        ordered=iter(sorted((n for n in arc["key_nodes"] if n in events),key=lambda n:(events[n]["date"],n)))
        arc["key_nodes"]=[next(ordered) if n in events else n for n in arc["key_nodes"]]
        dates=[events[n]["date"] for n in arc["key_nodes"] if n in events]
        arc["start_date"]=min([arc["start_date"]]+dates)
        arc["end_date"]=max([arc["end_date"]]+dates)
    pair(arcs[OPEN],"safe_wording","Открытые веса расширяют выбор места эксплуатации, но требуют подходящей лицензии, вычислений, ПО и специалистов. Разрыв в качестве зависит от задачи и даты; оценки продавца и расчёт стоимости токена не заменяют независимую проверку качества и полной стоимости владения.",
        "Open weights expand deployment choice but require a suitable licence, compute, software and expertise. Capability gaps depend on task and date; vendor estimates and token costing do not replace independent quality and total-cost assessments.",lang)
    pair(arcs[CAPITAL],"safe_wording","Различать объявленный объём, обязательство по финансированию, закрытие сделки, поставку оборудования и работающую мощность. Капитал для разных стадий стека нельзя складывать как уже произведённые расходы.",
        "Distinguish announced size, financing commitments, transaction closing, equipment delivery and operational capacity. Capital for different stack stages must not be added up as completed spending.",lang)

    rebuild_sources(doc)
    rebuild_counts(doc)
    for key,col in [("total_evidence_items","events"),("total_timeline_items","events"),("total_events","events"),("total_story_edges","edges"),("total_edges","edges"),("total_claims","claims")]:
        doc["summary"][key]=len(doc[col])
    doc["summary"].update(source_count=len(doc["sourceIndex"]),cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]),claim_status_counts=dict(Counter(c["status"] for c in doc["claims"])))
    doc["summary"]["stats"].update(total_claims=len(doc["claims"]),**doc["summary"]["claim_status_counts"])
    for key,field in [("by_status","status"),("event_status_counts","status"),("by_confidence","confidence")]:
        doc["summary"][key]=dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]),events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"]))
    doc["meta"].update(version=VERSION,updated_at=DATE)
    doc["meta"]["changelog"].insert(0,dict(version=VERSION,date=DATE,added_evidence=len(RECORDS),added_claims=0,added_story_arcs=0,added_story_edges=len(edges),description="Access channels, frontier-training resumption, Georgia correction, GPU finance commitments and scoped open-model economics."))
    doc["presentation"].update(editorial_version=VERSION,release_notes=[dict(title="Доступ, инфраструктура и уточнение раскрытий" if lang=="ru" else "Access, infrastructure and disclosure correction",text="Семь записей: условия эксплуатации, финансирование вычислений, экономика открытых моделей и уточнение Джорджии." if lang=="ru" else "Seven records on access conditions, compute finance, open-model economics and Georgia's clarification.")])
    doc["cyberFramework"]["updated_at"]=DATE
    doc["migrationAudit"].update(version=VERSION,v049_added_event_ids=[r["id"] for r in RECORDS],v049_added_edge_ids=[e["id"] for e in edges],v049_updated_event_ids=[DNS,ANTHROPIC])
    doc["researchAudit"]["october_access_finance"]=dict(date=DATE,added_event_count=len(RECORDS),excluded_inferences=["Georgia paywall bypass established", "Sweden nationwide model ban", "SpaceX financing already closed", "open models have universal 90 percent parity", "Swedish policy caused by OpenAI incident"])
    doc["factcheckAudit"]["v049_october_access_finance"]=dict(date=DATE,source_accounts_reviewed=True,independently_reproduced=False,entire_source_registry_reverified=False)
    thesis_ids={t["id"] for t in doc["thesisNodes"]}
    arc_counts={a:sum(e["source"]==a and e["target"] in thesis_ids for e in doc["edges"]) for a in arcs}
    hanging=[a for a,n in arc_counts.items() if not n]
    doc["connectivity"].update(edge_count=len(doc["edges"]),story_edges=len(doc["edges"]),last_recomputed=DATE,arc_count=len(arcs),story_arcs=len(arcs),computed_arc_count=len(arcs),arc_to_thesis_counts=arc_counts,computed_arc_to_thesis_counts=arc_counts,hanging_arcs_after_fix=hanging,computed_hanging_arcs=hanging)
    doc["referenceIntegrity"]=references(doc)
    assert doc["referenceIntegrity"]["valid"],doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    results,audit={},dict(version=VERSION,base_version="0.48",base_sha256=BASE_HASH,languages={})
    for lang in ["ru","en"]:
        raw=(args.input/f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest()!=BASE_HASH[lang]:
            raise ValueError(f"Changed {lang} baseline; refusing overwrite")
        old=json.loads(raw)
        doc=migrate(copy.deepcopy(old))
        doc["migrationAudit"]["v049_base_sha256"]=BASE_HASH[lang]
        audit["languages"][lang]={c:{x["id"]:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest() for x in old[c]} for c in ["events","claims","edges"]}
        audit["languages"][lang]["sources"]={s["id"]:s["url"] for s in old["sourceIndex"]}
        audit["languages"][lang]["counts_after"]={c:len(doc[c]) for c in ["events","claims","claimChecks","arcs","edges","sourceIndex","gaps"]}
        results[lang]=json.dumps(doc,ensure_ascii=False,indent=2)+"\n"
    args.output.mkdir(parents=True,exist_ok=True)
    for lang,payload in results.items():
        path=args.output/f"ai_power_storygraph_{lang}.json"
        tmp=path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang,VERSION,audit["languages"][lang]["counts_after"])
    PACKET.mkdir(parents=True,exist_ok=True)
    (PACKET/"migration-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    (PACKET/"evidence.json").write_text(json.dumps(dict(version=VERSION,checked_at=DATE,sources=SOURCES,records=RECORDS),ensure_ascii=False,indent=2)+"\n")


if __name__=="__main__":
    main()
