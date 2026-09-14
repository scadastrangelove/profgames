#!/usr/bin/env python3
"""Build the pinned v0.38 -> v0.39 military-AI operations update.

The migration adds atomic operational, access-governance and provider-telemetry
records. It does not create a new top-level arc and refuses any input other
than the reviewed v0.38 bilingual pair.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, arc_families, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review/war-ai-operations-september-2026"
DATE = "2026-09-14"
VERSION = "0.39"

CLAIM_EVIDENCE = {
    "CLM_003_GULF_PROTECTORATE": ["SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT"],
    "CLM_012_CRITICAL_DECISION_USE": [
        "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
        "SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING",
    ],
    "CLM_013_QUIET_ACCESS_CONTROL": [
        "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
        "SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE",
    ],
    "CLM_015_MILITARY_SUPPLIER_BOUNDARY_CONTROL": [
        "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
        "SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE",
        "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
    ],
    "CLM_016_PALANTIR_DECISION_OS": [
        "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
        "SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING",
    ],
    "CLM_024_WAR_DATA_FLYWHEEL": [
        "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
        "SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS",
        "SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP",
        "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
        "SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE",
    ],
    "CLM_026_DECISION_SOVEREIGNTY_MITIGATION": [
        "SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING",
        "SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP",
        "SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT",
    ],
}

CLAIM_ARCS = {
    "CLM_003_GULF_PROTECTORATE": "ARC_GULF_CONDITIONAL_SOVEREIGNTY",
    "CLM_012_CRITICAL_DECISION_USE": "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION",
    "CLM_013_QUIET_ACCESS_CONTROL": "ARC_QUIET_ACCESS_CONTROL",
    "CLM_015_MILITARY_SUPPLIER_BOUNDARY_CONTROL": "ARC_PALANTIR_DECISION_OS",
    "CLM_016_PALANTIR_DECISION_OS": "ARC_PALANTIR_DECISION_OS",
    "CLM_024_WAR_DATA_FLYWHEEL": "ARC_WAR_DATA_FLYWHEEL",
    "CLM_026_DECISION_SOVEREIGNTY_MITIGATION": "ARC_SOVEREIGN_FLOW_GATING",
}


def make_event(raw, lang, sources, doc):
    event = event_record(raw, lang, sources, doc)
    event["research_updates"] = ["war-ai-operations-september-2026"]
    event["actor_jurisdictions"] = copy.deepcopy(raw.get("actor_jurisdictions", raw["jurisdictions"]))
    event["regions"] = copy.deepcopy(raw.get("regions", []))
    event["geographic_scopes"] = copy.deepcopy(raw.get("geographic_scopes", ["National"]))
    event["candidate_evidence_tier"] = (
        "multi_source_reviewed"
        if len(raw["source_ids"]) > 1
        else "primary_source_reviewed"
        if sources[raw["source_ids"][0]]["primary_or_secondary"] == "primary"
        else "secondary_source_reviewed"
    )
    event["story_primary_arc_id"] = raw["primary_arc"]
    event["story_secondary_arc_ids"] = [arc_id for arc_id in raw["arcs"] if arc_id != raw["primary_arc"]]
    event["classification_review"]["source_scope"] = "event_specific_not_population_estimate"
    event["classification_review"]["independent_replication"] = False
    event["governance_scale"] = "military_operations_data_access_and_provider_enforcement"
    event["behavioral_status"] = (
        ["operational_pattern_reported", "policy_response"]
        if raw["id"].startswith("SIG_2026_ANTHROPIC_")
        else ["policy_response"]
        if raw["stage"] in {"announced", "signed"}
        else ["operational_pattern_reported"]
    )
    event["agent_population_scope"] = "human_agent_workflow" if raw["id"].startswith("SIG_2026_ANTHROPIC_") else "not_applicable"
    event["oversight_target"] = ["institutional_process", "security_control"]
    event["motivation_basis"] = "no_motivation_claim"
    event["goal_source"] = "explicit_prompt" if raw["id"].startswith("SIG_2026_ANTHROPIC_") else "not_applicable"
    return event


def patch_arcs(doc, event_ids):
    lang = doc["language"]
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    events = {event["id"]: event for event in doc["events"]}
    for event_id in event_ids:
        event = events[event_id]
        for arc_id in event["arcIds"]:
            arc = arcs[arc_id]
            arc["key_nodes"] = uniq(arc.get("key_nodes", []) + [event_id])
            arc["start_date"] = min(arc.get("start_date", event["date"]), event["date"])
            arc["end_date"] = max(arc.get("end_date", event["date"]), event["date"])

    updates = {
        "ARC_PALANTIR_DECISION_OS": {
            "status": "verified_operational_and_institutional_with_attribution_and_dependency_caveats",
            "thesis_ru": "Maven прошла путь от программы и контракта к боевому применению и обязательной внутренней инфраструктуре. Пентагон сообщил об использовании системы в Epic Fury, а Корпус морской пехоты сделал приложение ODIN официальным контуром оперативной отчётности. Это сильное свидетельство слоя, через который организация видит обстановку и действует, но не доказательство автономного выбора каждой цели или владения государственными данными.",
            "thesis_en": "Maven has moved from programme and contract to combat use and mandatory internal infrastructure. The Pentagon reported its use during Epic Fury, while the Marine Corps made ODIN its authoritative operational-reporting layer. This strongly supports an institutional layer through which an organisation sees and acts, but does not establish autonomous selection of every target or ownership of government data.",
            "safe_ru": "Говорить об операционном и обязательном программном слое. Отдельно маркировать официальные заявления, журналистскую атрибуцию Claude и отсутствие публичной трассировки отдельных решений.",
            "safe_en": "Describe an operational and mandatory software layer. Separately label official statements, journalistic attribution of Claude and the lack of public decision-level traces.",
            "counterpoints_ru": [
                "13 тысяч — число целей кампании, а не число автономных решений Maven.",
                "Официальный статус ODIN не измеряет точность, переносимость или отказоустойчивость.",
                "Публичные данные не связывают Maven или Claude с конкретным ударом по школе в Минабе.",
            ],
            "counterpoints_en": [
                "Thirteen thousand is the campaign target count, not a count of autonomous Maven decisions.",
                "ODIN's authoritative status does not measure accuracy, portability or resilience.",
                "Public evidence does not link Maven or Claude to the specific Minab school strike.",
            ],
        },
        "ARC_WAR_DATA_FLYWHEEL": {
            "status": "verified_parallel_governed_and_route_around_data_loops_with_field_outcome_gaps",
            "thesis_ru": "Военный цикл данных теперь наблюдается в двух режимах. Украина лицензирует проверенным разработчикам размеченный корпус Avengers Labs и открывает ограниченный доступ зарубежному партнёру; вероятные российские фрилансеры из GTG‑27005 обучали классификатор на собранном из открытых источников украинском видео. Maven и иранский GTG‑30005 показывают следующий этап — превращение потоков и открытых данных в оперативную картину и рекомендации.",
            "thesis_en": "The military data loop is now visible in two regimes. Ukraine licenses a curated Avengers Labs corpus to vetted developers and grants bounded access to a foreign partner; likely Russian freelancers in GTG-27005 trained a classifier on scraped Ukrainian footage. Maven and Iran-nexus GTG-30005 show the next stage: turning data flows and open sources into an operational picture and recommendations.",
            "safe_ru": "Различать лицензируемый государственный корпус, открытый сбор данных, поддержку решений и автономное поражение. Наличие цикла не доказывает точность модели, масштаб боевого применения или отсутствие человека в контуре.",
            "safe_en": "Separate a licensed state corpus, open-source collection, decision support and autonomous engagement. The existence of a loop does not establish model accuracy, field scale or absence of human control.",
            "counterpoints_ru": [
                "Показатели Avengers 70% и 100 тысяч потоков сообщены Минобороны без открытого протокола оценки.",
                "GTG‑27005 дошла до hardware-in-loop и TRL 3–4, но не до независимо подтверждённого боевого развёртывания.",
                "GTG‑30005 описывает рекомендации на основе открытых данных, а не успешный удар.",
            ],
            "counterpoints_en": [
                "The Avengers 70% and 100,000-stream figures are ministry-reported without a public evaluation protocol.",
                "GTG-27005 reached hardware-in-loop and TRL 3-4, not independently verified field deployment.",
                "GTG-30005 describes open-source targeting recommendations, not a successful strike.",
            ],
        },
        "ARC_GULF_CONDITIONAL_SOVEREIGNTY": {
            "status": "verified_access_and_announced_defense_cooperation_with_implementation_gap",
            "thesis_ru": "Условный суверенитет Залива охватывает не только чипы и облака, но и военный AI-контур. CENTCOM и ОАЭ договорились создать Talon Synapse для разведки, защиты инфраструктуры и регионального мониторинга. Это расширяет доступ через союзническую интеграцию, но одновременно сохраняет зависимость от американского военного и технологического контура.",
            "thesis_en": "Conditional Gulf sovereignty extends beyond chips and clouds into military AI. CENTCOM and the UAE agreed to establish Talon Synapse for intelligence support, infrastructure protection and regional monitoring. This expands access through allied integration while retaining dependence on a U.S. military and technology channel.",
            "safe_ru": "Называть Talon Synapse соглашением о создании группы. До отдельного подтверждения не выдавать плановый запуск, состав систем и результаты за состоявшиеся.",
            "safe_en": "Describe Talon Synapse as an agreement to establish a task force. Do not present launch, system composition or outcomes as completed without separate confirmation.",
            "counterpoints_ru": [
                "Релиз обещает официальный запуск в ближайшие недели; проверенного подтверждения запуска пока нет.",
                "Двусторонняя группа может увеличивать местную компетенцию и зависимость одновременно.",
            ],
            "counterpoints_en": [
                "The release promises formal launch in coming weeks; reviewed evidence does not yet confirm launch.",
                "A bilateral task force can increase local capability and dependency at the same time.",
            ],
        },
        "ARC_QUIET_ACCESS_CONTROL": {
            "status": "verified_provider_observability_and_revocation_with_local_continuity_limits",
            "thesis_ru": "Тихий контроль действует через проверку клиентов, уровни допуска, телеметрию и отзыв доступа. Случаи GTG‑27005 и GTG‑30005 показывают, что провайдер мог увидеть военную разработку и разведывательный конвейер, заблокировать аккаунты и изменить детектирование. Контроль ограничен видимой частью размещённого сервиса и не гарантирует остановку локально развёрнутого результата.",
            "thesis_en": "Quiet control operates through customer review, access tiers, telemetry and revocation. GTG-27005 and GTG-30005 show a provider observing military development and a reconnaissance pipeline, banning accounts and changing detections. Control is limited to the visible hosted-service layer and does not guarantee shutdown of locally deployed outputs.",
            "safe_ru": "Говорить о наблюдении и блокировке конкретных аккаунтов на платформе Anthropic, а не о полном контроле над актором или созданным им программным обеспечением.",
            "safe_en": "Describe observation and revocation of specific Anthropic accounts, not complete control over the actor or software it produced.",
            "counterpoints_ru": [
                "Телеметрия провайдера — отобранная выборка, а не полная карта военного использования моделей.",
                "Отзыв облачного аккаунта не удаляет уже сохранённый код, данные и локальные модели.",
            ],
            "counterpoints_en": [
                "Provider telemetry is a selected sample, not a complete map of military model use.",
                "Revoking a hosted account does not remove saved code, data or local models.",
            ],
        },
    }
    for arc_id, update in updates.items():
        arc = arcs[arc_id]
        arc["status"] = update["status"]
        for key, source_key in [("thesis", "thesis"), ("safe_wording", "safe"), ("counterpoints", "counterpoints")]:
            pair(arc, key, update[source_key + "_ru"], update[source_key + "_en"], lang)


def patch_claims(doc, sources):
    lang = doc["language"]
    checks = {claim["id"]: claim for claim in doc["claimChecks"]}
    events = {event["id"]: event for event in doc["events"]}
    for claim_id, event_ids in CLAIM_EVIDENCE.items():
        claim = checks[claim_id]
        claim["supporting_evidence"] = uniq(claim.get("supporting_evidence", []) + event_ids)
        claim["research_updates"] = uniq(claim.get("research_updates", []) + ["war-ai-operations-september-2026"])
        for event_id in event_ids:
            for source in events[event_id].get("sources", []):
                add_source(claim, source)

    war = checks["CLM_024_WAR_DATA_FLYWHEEL"]
    war["confidence"] = "A/B"
    pair(war, "claim",
         "Война создаёт несколько контуров обратной связи между телеметрией, размеченными данными, обучением и применением. Украинский режим показывает лицензируемый и проверяемый доступ к государственному корпусу; GTG‑27005 — маршрут через открытый сбор чужого боевого видео; Maven и GTG‑30005 — преобразование потоков в оперативные рекомендации. Это не доказывает точность, автономное поражение или одинаковую зрелость контуров.",
         "War creates several feedback loops between telemetry, labelled data, training and use. Ukraine shows licensed, screened access to a state corpus; GTG-27005 shows a route through scraping another side's combat footage; Maven and GTG-30005 show data flows becoming operational recommendations. This does not establish accuracy, autonomous engagement or equal maturity across the loops.", lang)
    pair(war, "safe_wording",
         "Говорить о подтверждённых контурах сбора, допуска, обучения и поддержки решений; боевой эффект и степень автономии указывать отдельно для каждого случая.",
         "Describe established collection, access, training and decision-support loops; state battlefield effect and autonomy separately for each case.", lang)
    pair(war, "recommended_phrasing", war["safe_wording_ru"], war["safe_wording_en"], lang)
    pair(war, "caveats", [war["safe_wording_ru"]], [war["safe_wording_en"]], lang)

    palantir = checks["CLM_016_PALANTIR_DECISION_OS"]
    palantir["confidence"] = "A/B"
    pair(palantir, "claim",
         "Maven всё больше выполняет функции операционной системы решения: поддерживает ударные миссии, объединяет разведывательные потоки, а ODIN становится обязательным контуром оперативной отчётности Корпуса морской пехоты. Это наблюдаемая институциональная роль, а не утверждение о владении данными или автономной санкции удара.",
         "Maven increasingly performs decision-operating-system functions: supporting strike missions, integrating intelligence flows and, through ODIN, becoming the Marine Corps' authoritative operational-reporting layer. This is an observed institutional role, not a claim of data ownership or autonomous strike authorization.", lang)
    pair(palantir, "safe_wording",
         "Описывать конкретные обязательные и операционные функции Maven; не переносить число целей кампании на число решений системы и не приписывать ей юридическое владение данными.",
         "Describe Maven's specific operational and mandatory functions; do not turn the campaign target count into a count of system decisions or attribute legal ownership of data.", lang)
    pair(palantir, "recommended_phrasing", palantir["safe_wording_ru"], palantir["safe_wording_en"], lang)

    gulf = checks["CLM_003_GULF_PROTECTORATE"]
    pair(gulf, "claim",
         "ИИ-суверенитет стран Залива остаётся условным доступом к внешнему стеку, но включает активное наращивание собственной компетенции. Talon Synapse добавляет военный канал совместной разработки и мониторинга США–ОАЭ; анонс группы не равен подтверждённой операционной независимости.",
         "Gulf AI sovereignty remains conditional access to an external stack while building local capability. Talon Synapse adds a U.S.-UAE military channel for co-development and monitoring; announcing the task force does not establish operational independence.", lang)
    pair(gulf, "safe_wording",
         "Показывать одновременно расширение местной компетенции и зависимость от союзнического канала; Talon Synapse пока считать анонсированной программой.",
         "Show local capability growth and reliance on an allied channel together; treat Talon Synapse as an announced programme for now.", lang)
    pair(gulf, "recommended_phrasing", gulf["safe_wording_ru"], gulf["safe_wording_en"], lang)


def add_edges(doc, raw):
    families = {arc["id"]: arc.get("family_id", "") for arc in doc["arcs"]}
    added = []
    sequence = 0

    def add(source, target, relation, ru, en, *, arc_id, target_kind="evidence",
            relationship_class="editorial_relationship", style="solid", evidence_level="A/B"):
        nonlocal sequence
        sequence += 1
        added.append({
            "id": f"EDGE_V039_WAR_AI_{sequence:03d}",
            "source": source,
            "target": target,
            "source_kind": "evidence",
            "target_kind": target_kind,
            "relation": relation,
            "arc_id": arc_id,
            "arc_family_id": families.get(arc_id, ""),
            "strength": "moderate",
            "evidence_level": evidence_level,
            "visual_lane": "decision_support_cognition",
            "style": style,
            "summary_ru": ru,
            "summary_en": en,
            "kind": "edge",
            "is_auto": False,
            "relationship_class": relationship_class,
        })

    for event in raw["events"]:
        for arc_id in event["arcs"]:
            add(
                event["id"], arc_id, "part_of_arc",
                "Тематическая принадлежность; связь не доказывает всю дугу.",
                "Thematic membership; the link does not prove the whole arc.",
                arc_id=arc_id, target_kind="story_arc", relationship_class="thematic", style="dashed",
                evidence_level=event["confidence"],
            )

    for claim_id, event_ids in CLAIM_EVIDENCE.items():
        arc_id = CLAIM_ARCS[claim_id]
        for event_id in event_ids:
            add(
                event_id, claim_id, "supports_with_scope",
                "Поддерживает тезис только в границах статуса, атрибуции и оговорок карточки.",
                "Supports the claim only within the record's status, attribution and caveats.",
                arc_id=arc_id, target_kind="claim_check", relationship_class="evidential",
            )

    relationships = [
        (
            "SIG_2026_PALANTIR_MAVEN_PROGRAM_OF_RECORD_EXPANDED",
            "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
            "develops_into", "ARC_PALANTIR_DECISION_OS",
            "Программный статус предшествовал публично заявленному боевому применению.",
            "Programme status preceded publicly reported combat use.",
        ),
        (
            "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
            "SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING",
            "parallel", "ARC_PALANTIR_DECISION_OS",
            "Боевое применение и обязательная отчётность показывают разные функции одного институционального слоя.",
            "Combat use and authoritative reporting show different functions of one institutional layer.",
        ),
        (
            "SIG_2026_UKRAINE_BATTLEFIELD_DATA_PLATFORM",
            "SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS",
            "develops_into", "ARC_WAR_DATA_FLYWHEEL",
            "Общий режим партнёрского обучения конкретизировался лицензиями, размером корпуса и критериями допуска.",
            "The partner-training regime became concrete through licences, corpus size and admission criteria.",
        ),
        (
            "SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS",
            "SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP",
            "develops_into", "ARC_WAR_DATA_FLYWHEEL",
            "Внутренний режим доступа расширился до первого объявленного зарубежного партнёра с отдельными условиями суверенитета.",
            "Domestic access expanded to a first announced foreign partner under explicit sovereignty conditions.",
        ),
        (
            "SIG_UAE_2025_STARGATE_UAE",
            "SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT",
            "parallel", "ARC_GULF_CONDITIONAL_SOVEREIGNTY",
            "Коммерческий контур вычислений и военная AI-группа — параллельные каналы условного доступа США–ОАЭ.",
            "Commercial compute and a military AI task force are parallel U.S.-UAE conditional-access channels.",
        ),
        (
            "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
            "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
            "supports", "ARC_QUIET_ACCESS_CONTROL",
            "Конкретный случай показывает наблюдение разработки и отзыв облачного доступа провайдером.",
            "The case shows provider observation of development and revocation of hosted access.",
        ),
        (
            "SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE",
            "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
            "supports", "ARC_QUIET_ACCESS_CONTROL",
            "Конкретный случай показывает наблюдение разведывательного конвейера и передачу данных властям.",
            "The case shows provider observation of a reconnaissance pipeline and sharing with authorities.",
        ),
        (
            "SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS",
            "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
            "parallel", "ARC_WAR_DATA_FLYWHEEL",
            "Лицензируемый корпус и сбор открытого видео показывают разные режимы доступа к боевым данным без доказанной причинной связи между случаями.",
            "A licensed corpus and scraped footage show different battlefield-data access regimes without a claimed causal link.",
        ),
    ]
    for source, target, relation, arc_id, ru, en in relationships:
        add(source, target, relation, ru, en, arc_id=arc_id)

    doc["edges"].extend(added)
    attach_edge_links(doc, {edge["id"] for edge in added})
    return [edge["id"] for edge in added]


def update_metadata(doc, raw, edge_ids):
    lang = doc["language"]
    event_ids = [event["id"] for event in raw["events"]]
    doc["meta"].update(
        version=VERSION,
        updated_at=DATE,
        schema_version="ai_stack_structural_power.v0.39.0-2026-09-14",
    )
    entry = {
        "version": VERSION,
        "date": DATE,
        "description": "Operational military-AI, governed battlefield-data access and provider-observed military misuse, integrated without adding a top-level arc.",
        "added_evidence": len(event_ids),
        "added_claims": 0,
        "added_claim_checks": 0,
        "added_story_arcs": 0,
        "added_story_edges": len(edge_ids),
        "updated_story_arcs": [
            "ARC_PALANTIR_DECISION_OS",
            "ARC_WAR_DATA_FLYWHEEL",
            "ARC_GULF_CONDITIONAL_SOVEREIGNTY",
            "ARC_QUIET_ACCESS_CONTROL",
        ],
        "deferred_or_corrected_candidates": len(raw["deferred"]),
    }
    doc["meta"]["changelog"] = [entry] + [item for item in doc["meta"].get("changelog", []) if item.get("version") != VERSION]

    summary = doc["summary"]
    for key, collection in [
        ("total_evidence_items", "events"), ("total_timeline_items", "events"),
        ("total_story_arcs", "arcs"), ("total_story_edges", "edges"),
        ("total_events", "events"), ("total_claims", "claims"),
        ("total_claim_checks", "claimChecks"), ("total_arcs", "arcs"),
        ("total_edges", "edges"), ("total_thesis_nodes", "thesisNodes"),
    ]:
        summary[key] = len(doc[collection])
    summary["cyber_framework_event_count"] = sum(bool(event.get("primary_domain_id")) for event in doc["events"])
    summary["source_count"] = len(doc["sourceIndex"])
    claim_counts = Counter(claim["status"] for claim in doc["claims"])
    summary["claim_status_counts"] = dict(claim_counts)
    summary["stats"].update(claim_counts)
    summary["stats"]["total_claims"] = len(doc["claims"])
    finding = {
        "ru": "ВОЕННЫЙ AI-КОНТУР (v0.39): данные, модели и программные слои образуют несколько разных цепочек — лицензируемый боевой корпус, открытый сбор, провайдерский доступ и институциональный decision OS. Их нельзя сводить к одному показателю автономности.",
        "en": "MILITARY AI LAYER (v0.39): data, models and software form different chains—a licensed battlefield corpus, open-source collection, hosted-provider access and an institutional decision OS. They cannot be collapsed into one autonomy metric.",
    }
    summary["key_findings"] = [finding[lang]] + summary.get("key_findings", [])
    doc["arcHierarchy"]["primary_event_assignments"] = sum(
        bool(event.get("story_primary_arc_id")) for event in doc["events"]
    )
    doc["arcHierarchy"]["events_with_secondary_arcs"] = sum(
        bool(event.get("story_secondary_arc_ids")) for event in doc["events"]
    )
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["corrections"] = [finding[lang]] + doc["presentation"].get("corrections", [])
    doc["presentation"]["release_notes"] = [
        {
            "title": "От данных к решению" if lang == "ru" else "From data to decision",
            "text": finding[lang],
        },
        {
            "title": "Граница атрибуции" if lang == "ru" else "Attribution boundary",
            "text": (
                "Операционное использование, провайдерская телеметрия, анонс программы и автономное боевое действие маркируются раздельно."
                if lang == "ru"
                else "Operational use, provider telemetry, programme announcements and autonomous field action remain separately labelled."
            ),
        },
    ]
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update({
        "version": VERSION,
        "v039_base_sha256": raw["meta"]["base_sha256"][lang],
        "v039_added_event_ids": event_ids,
        "v039_added_edge_ids": edge_ids,
        "v039_updated_claim_check_ids": sorted(CLAIM_EVIDENCE),
        "v039_updated_arc_ids": entry["updated_story_arcs"],
        "v039_source_package": "review/war-ai-operations-september-2026",
    })
    doc["factcheckAudit"]["v039_war_ai_operations"] = {
        "date": DATE,
        "accepted_records": len(event_ids),
        "source_records": len(raw["sources"]),
        "deferred_records": len(raw["deferred"]),
        "autonomous_field_action_inferred": False,
        "new_top_level_arc_added": False,
        "note": "Campaign totals, individual AI decisions, provider telemetry and field autonomy remain separate claims.",
    }
    doc["researchAudit"]["war_ai_operations_september_2026"] = {
        "date": DATE,
        "accepted_ids": event_ids,
        "deferred": copy.deepcopy(raw["deferred"]),
        "primary_source_first": True,
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]),
        "story_edges": len(doc["edges"]),
        "last_recomputed": DATE,
        "v0_39_added_evidence": len(event_ids),
        "v0_39_added_edges": len(edge_ids),
        "v0_39_updated_arcs": entry["updated_story_arcs"],
    })


def migrate(doc, raw):
    if doc["meta"].get("version") != "0.38":
        raise ValueError("Expected v0.38 input")
    old_counts = {collection: len(doc[collection]) for collection in ["events", "claims", "claimChecks", "arcs", "edges"]}
    old_dates = {event["id"]: event["date"] for event in doc["events"]}
    old_urls = {source["url"] for source in doc["sourceIndex"]}
    old_arc_ids = [arc["id"] for arc in doc["arcs"]]
    old_hierarchy = copy.deepcopy(doc["arcHierarchy"])
    sources = {source["id"]: source for source in raw["sources"]}
    event_ids = [event["id"] for event in raw["events"]]
    all_ids = {
        node["id"]
        for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"]
        for node in doc.get(collection, [])
    }
    if len(event_ids) != 7 or len(set(event_ids)) != 7 or set(event_ids) & all_ids:
        raise ValueError("Candidate count or ID collision")

    doc["events"].extend(make_event(event, doc["language"], sources, doc) for event in raw["events"])
    patch_arcs(doc, event_ids)
    patch_claims(doc, sources)
    edge_ids = add_edges(doc, raw)
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, raw, edge_ids)
    doc["referenceIntegrity"] = references(doc)
    if not doc["referenceIntegrity"]["valid"]:
        raise ValueError(doc["referenceIntegrity"])

    assert len(doc["events"]) == old_counts["events"] + 7
    assert len(doc["claims"]) == old_counts["claims"]
    assert len(doc["claimChecks"]) == old_counts["claimChecks"]
    assert len(doc["arcs"]) == old_counts["arcs"]
    assert len(doc["edges"]) == old_counts["edges"] + len(edge_ids)
    assert [arc["id"] for arc in doc["arcs"]] == old_arc_ids
    assert doc["arcHierarchy"]["role_counts"] == old_hierarchy["role_counts"]
    assert doc["arcHierarchy"]["family_order"] == old_hierarchy["family_order"]
    assert doc["arcHierarchy"]["role_definitions"] == old_hierarchy["role_definitions"]
    assert all(next(event for event in doc["events"] if event["id"] == event_id)["date"] == date for event_id, date in old_dates.items())
    assert old_urls <= {source["url"] for source in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads((PACKAGE / "candidates.json").read_text(encoding="utf-8"))
    loaded = {}
    for lang in ["ru", "en"]:
        path = args.root / f"ai_power_storygraph_{lang}.json"
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != raw["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{path.name}: expected pinned v0.38 SHA-256; refusing input {digest}")
        loaded[lang] = json.loads(data)

    rendered = {
        lang: (json.dumps(migrate(doc, raw), ensure_ascii=False, indent=2) + "\n").encode()
        for lang, doc in loaded.items()
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, data in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_bytes(data)
        os.replace(temporary, path)
        doc = json.loads(data)
        print(lang, len(doc["events"]), "events", len(doc["arcs"]), "arcs", len(doc["edges"]), "edges", len(doc["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()
