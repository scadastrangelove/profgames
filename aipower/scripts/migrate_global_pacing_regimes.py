#!/usr/bin/env python3
"""Build the pinned v0.36 -> v0.37 global pacing/access update."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, arc_families, event_record, pair, source_record
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review/global-pacing-access-regimes"
DATE = "2026-09-14"
VERSION = "0.37"
ARC_ID = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
CLAIM_ID = "CLM_031_FRONTIER_PACING_AUTHORITY"
EXISTING_GLOBAL_EVENTS = [
    "SIG_2023_CHINA_GENAI_INTERIM_MEASURES",
    "SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS",
    "SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE",
    "SIG_2026_KOREA_NAVER_SOVEREIGN_MODEL_EXCLUSION",
    "SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL",
]


def make_event(raw, lang, sources, doc):
    event = event_record(raw, lang, sources, doc)
    event["research_updates"] = ["global-pacing-access-regimes"]
    event["governance_scale"] = {
        "SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS": "multilateral_voluntary_provider_commitment",
        "SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS": "national_evaluator_provider_collaboration",
        "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE": "national_public_service_filing_regime",
    }[raw["id"]]
    event["geographic_scopes"] = ["International"] if raw["id"].startswith("SIG_2024_SEOUL") else ["National"]
    return event


def patch_pacing_arc(doc):
    lang = doc["language"]
    arc = next(item for item in doc["arcs"] if item["id"] == ARC_ID)
    arc.update({
        "status": "verified_mixed_voluntary_binding_evaluation_procurement_and_rhetoric",
        "start_date": "2023-07-13",
        "end_date": "2026-09-14",
        "key_nodes": [
            "SIG_2023_CHINA_GENAI_INTERIM_MEASURES",
            "SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS",
            "SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS",
            "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS",
            "SIG_2026_KOREA_NAVER_SOVEREIGN_MODEL_EXCLUSION",
            "SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS",
            "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE",
            "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL",
            "export-13",
            "SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL",
            "SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE",
            "SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE",
            "export-14",
            "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL",
            "SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS",
            "SIG_2026_TRUMP_REJECTS_FRONTIER_PACING",
            CLAIM_ID,
        ],
    })
    pair(arc, "title",
         "Темп, допуск и непрерывность доступа к передовым моделям",
         "Frontier-model pacing, release gates and continuity of access", lang)
    pair(arc, "thesis",
         "За пределами США контроль над передовым ИИ также строится вокруг контрольных точек, но они устроены по-разному. Сеульские обязательства задают добровольные пороги разработки и выпуска; британский AISI получает ограниченную дорелизную видимость; ЕС располагает законными полномочиями оценки и ограничения доступности; Китай применяет регистрацию публичных сервисов; Корея развивает собственные модели и критерии происхождения. Американский спор о скорости и праве лаборатории на паузу является одной версией более общего конфликта за темп, допуск и непрерывность.",
         "Outside the United States, control over advanced AI also takes the form of checkpoints, but the mechanisms differ. The Seoul commitments set voluntary development and deployment thresholds; UK AISI receives bounded pre-release visibility; the EU has statutory evaluation and availability-restriction powers; China operates a filing gate for public services; and Korea pursues domestic models and provenance criteria. The U.S. dispute over speed and a laboratory's ability to pause is one version of a broader contest over pace, release and continuity.", lang)
    pair(arc, "safe_wording",
         "Различать добровольные обязательства, сотрудничество с оценщиком, обязательный допуск на рынок, регистрацию публичного сервиса и закупочную политику. Их общая тема — контрольная точка; правовая сила, объект контроля и наблюдаемое исполнение различаются.",
         "Distinguish voluntary commitments, evaluator collaboration, binding market access, public-service filing and procurement policy. Their common feature is a checkpoint; legal force, control object and observed implementation differ.", lang)
    pair(arc, "counterpoints", [
        "Сеульские обязательства не создали общего графика обучения и допускают разные корпоративные рамки.",
        "Дорелизный доступ AISI не равен общему праву государства задерживать выпуск.",
        "Китайский реестр охватывает публичные сервисы, а не весь цикл обучения модели.",
        "Полномочия ЕС действуют в пределах AI Act и не образуют мирового режима.",
        "Корейские программы уменьшают зависимость от поставщика, но сами по себе не замедляют фронтир.",
        "Предложение Амодеи и поддержка руководителей лабораторий не доказывают согласованного изменения темпа.",
    ], [
        "The Seoul commitments did not create a common training schedule and allow different company frameworks.",
        "AISI's pre-release access is not a general state power to delay deployment.",
        "China's registry governs public-facing services, not the whole model-training lifecycle.",
        "EU powers operate within the AI Act and do not constitute a global regime.",
        "Korean programmes reduce supplier dependency but do not by themselves slow the frontier.",
        "Amodei's proposal and executive endorsements do not establish a coordinated pace change.",
    ], lang)


def patch_claims(doc, raw, sources):
    lang = doc["language"]
    checks = {item["id"]: item for item in doc["claimChecks"]}
    claim = checks[CLAIM_ID]
    new_ids = [event["id"] for event in raw["events"]]
    claim["supporting_evidence"] = uniq(claim.get("supporting_evidence", []) + new_ids + EXISTING_GLOBAL_EVENTS)
    claim["confidence"] = "A/B"
    claim["geography"] = ["US", "UK", "EU", "China", "South Korea", "Global"]
    claim["keywords"] = uniq(claim.get("keywords", []) + ["release gate", "filing", "pre-deployment evaluation", "sovereign model"])
    claim["date_relevant"] = "2023-2026"
    pair(claim, "title",
         "Власть над передовым ИИ включает темп, допуск, наблюдаемость и непрерывность",
         "Power over frontier AI includes pace, release, observability and continuity", lang)
    pair(claim, "claim",
         "В разных юрисдикциях контроль над передовым ИИ проявляется как набор разных полномочий: лаборатория может приостановить обучение, добровольная рамка — связать порог риска с разработкой или выпуском, государственный оценщик — получить дорелизный доступ, регулятор — требовать регистрацию или оценку перед публичным доступом, а заказчик — добиваться заменяемости и непрерывности. Документы и административная практика подтверждают эти механизмы, но не единый мировой режим и не измеренное глобальное замедление.",
         "Across jurisdictions, control over advanced AI appears through different powers: a laboratory can pause training, a voluntary framework can link a risk threshold to development or deployment, a state evaluator can receive pre-release access, a regulator can require filing or evaluation before public access, and a customer can demand replaceability and continuity. Documents and administrative practice establish these mechanisms, not one global regime or a measured worldwide slowdown.", lang)
    pair(claim, "safe_wording",
         "Говорить о сходной логике контрольных точек при разной правовой силе и разных объектах контроля. Не называть это международным соглашением о замедлении или полным государственным контролем над моделями.",
         "Describe a shared checkpoint logic with different legal force and control objects. Do not call it an international slowdown agreement or complete state control over models.", lang)
    pair(claim, "recommended_phrasing", claim["safe_wording_ru"], claim["safe_wording_en"], lang)
    pair(claim, "caveats", [claim["safe_wording_ru"]], [claim["safe_wording_en"]], lang)
    pair(claim, "what_could_break_it",
         "Данные о фактическом соблюдении корпоративных порогов, влиянии оценок на сроки выпуска, применении полномочий ЕС, качестве китайского реестра и результатах корейских программ могут усилить или ослабить сравнительный вывод.",
         "Evidence on compliance with company thresholds, evaluation effects on release timing, use of EU powers, the quality of China's registry and outcomes of Korean programmes could strengthen or weaken the comparison.", lang)
    for source in sources.values():
        add_source(claim, source)
    claim["research_updates"] = uniq(claim.get("research_updates", []) + ["global-pacing-access-regimes"])

    resilience = checks["CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"]
    resilience["supporting_evidence"] = uniq(resilience.get("supporting_evidence", []) + new_ids + [
        "SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS",
        "SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE",
    ])
    pair(resilience, "claim",
         "Киберустойчивость ИИ складывается из безопасной разработки, испытаний возможностей, национальной защиты, отраслевого восстановления и защиты решений. Сравнительный слой добавляет дорелизный доступ оценщиков, пороги выпуска, обязательный допуск публичных сервисов и непрерывность критичного доступа. Это набор взаимодополняющих механизмов разной нормативной силы, а не единый стандарт.",
         "AI cyber resilience combines secure development, capability testing, national defence, sector recovery and decision protection. The comparative layer adds pre-release evaluator access, deployment thresholds, mandatory gates for public services and continuity of mission access. These are complementary mechanisms of different legal force, not one standard.", lang)
    pair(resilience, "safe_wording",
         "Показывать полный стек контролей, но отдельно маркировать закон, административную практику, добровольное обязательство, испытание и программу. Наличие механизма не доказывает его эффективность.",
         "Show the full control stack while separately labelling law, administrative practice, voluntary commitment, evaluation and programme. The existence of a mechanism does not establish effectiveness.", lang)
    pair(resilience, "recommended_phrasing", resilience["safe_wording_ru"], resilience["safe_wording_en"], lang)
    pair(resilience, "caveats", [resilience["safe_wording_ru"]], [resilience["safe_wording_en"]], lang)
    for source in sources.values():
        add_source(resilience, source)
    resilience["research_updates"] = uniq(resilience.get("research_updates", []) + ["global-pacing-access-regimes"])


def patch_event_and_arc_membership(doc, raw):
    events = {event["id"]: event for event in doc["events"]}
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    new_ids = {event["id"] for event in raw["events"]}
    for event in raw["events"]:
        node = events[event["id"]]
        for arc_id in event["arcs"]:
            arc = arcs[arc_id]
            arc["key_nodes"] = uniq(arc.get("key_nodes", []) + [event["id"]])
            arc["start_date"] = min(arc.get("start_date", event["date"]), event["date"])
            arc["end_date"] = max(arc.get("end_date", event["date"]), event["date"])
            node["arcIds"] = uniq(node.get("arcIds", []) + [arc_id])
            node["arcFamilyIds"] = uniq(node.get("arcFamilyIds", []) + [arc.get("family_id")])
    for event_id in EXISTING_GLOBAL_EVENTS:
        node = events[event_id]
        node["arcIds"] = uniq(node.get("arcIds", []) + [ARC_ID])
        node["arcFamilyIds"] = uniq(node.get("arcFamilyIds", []) + [arcs[ARC_ID]["family_id"]])
        node["research_updates"] = uniq(node.get("research_updates", []) + ["global-pacing-access-regimes"])
    patch_pacing_arc(doc)

    lang = doc["language"]
    texts = {
        "ARC_QUIET_ACCESS_CONTROL": (
            "Тихий контроль действует через проверку клиентов, уровни допуска, журналы, отзыв аккаунтов, пороги выпуска и доступ оценщиков. Сеульские обязательства формулируют добровольный порог, британский AISI получает ограниченный доступ до выпуска, а ЕС и Китай используют разные обязательные контуры допуска. Эти механизмы дают разную видимость и не складываются в одного всевидящего регулятора.",
            "Quiet control operates through customer review, access tiers, logs, account revocation, release thresholds and evaluator access. The Seoul commitments define a voluntary threshold, UK AISI receives bounded pre-release access, and the EU and China use different binding access gates. These mechanisms provide different visibility and do not add up to one all-seeing regulator.",
        ),
        "ARC_SOVEREIGN_FLOW_GATING": (
            "Суверенный контроль потоков охватывает не только чипы, данные и капитал, но и выпуск сервиса, видимость контрольной точки и непрерывность доступа. ЕС регулирует доступность на рынке, Китай ведёт обязательный реестр публичных сервисов, Корея использует критерии происхождения и собственные модели, а США соединяют экспортные ограничения с закупочной заменяемостью.",
            "Sovereign flow control covers not only chips, data and capital but also service release, checkpoint visibility and continuity of access. The EU governs market availability, China operates a mandatory registry for public services, Korea uses provenance criteria and domestic models, and the United States combines export controls with procurement replaceability.",
        ),
        "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": (
            "Киберустойчивость ИИ включает безопасную разработку, оценку возможностей, защиту, отраслевое восстановление и безопасность решений. Сравнительный слой показывает дополнительные контрольные точки: добровольные пороги разработки и выпуска, дорелизный доступ оценщика, обязательную оценку или регистрацию публичного сервиса и непрерывность критичного доступа.",
            "AI cyber resilience includes secure development, capability evaluation, defence, sector recovery and decision security. The comparative layer adds further checkpoints: voluntary development and deployment thresholds, pre-release evaluator access, mandatory evaluation or filing for public services, and continuity of mission access.",
        ),
        "ARC_CHINA_COUNTERSTACK_ROUTE_AROUND": (
            "Китайский контрстек сочетает обход внешних ограничений с внутренним контролем допуска. Открытые веса и собственная инфраструктура расширяют альтернативный маршрут, тогда как обязательная регистрация публичных генеративных сервисов показывает, что этот маршрут остаётся внутри национальной контрольной точки.",
            "China's counter-stack combines routes around external constraints with domestic access control. Open weights and domestic infrastructure expand an alternative route, while mandatory filing of public generative-AI services shows that the route remains inside a national checkpoint.",
        ),
    }
    safe = {
        "ARC_QUIET_ACCESS_CONTROL": (
            "Разделять добровольный порог, договорный доступ оценщика и обязательный регуляторный допуск; каждый видит и контролирует разную часть цикла.",
            "Separate a voluntary threshold, contractual evaluator access and a binding regulatory gate; each observes and controls a different part of the lifecycle.",
        ),
        "ARC_SOVEREIGN_FLOW_GATING": (
            "Не называть разные национальные механизмы единым режимом и не путать регистрацию сервиса с контролем обучения модели.",
            "Do not call different national mechanisms one regime or conflate service filing with control over model training.",
        ),
        "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": (
            "Различать существование элемента контроля, его обязательность, применение и измеренную эффективность.",
            "Distinguish a control's existence, binding force, implementation and measured effectiveness.",
        ),
        "ARC_CHINA_COUNTERSTACK_ROUTE_AROUND": (
            "Описывать одновременно внешний маршрут обхода и внутренний режим допуска, не выдавая число регистраций за аудит безопасности.",
            "Describe the external route-around and domestic gate together without treating filing counts as a security audit.",
        ),
    }
    for arc_id, (ru, en) in texts.items():
        pair(arcs[arc_id], "thesis", ru, en, lang)
        pair(arcs[arc_id], "safe_wording", safe[arc_id][0], safe[arc_id][1], lang)
    assert new_ids <= set(events)


def add_edges(doc, raw):
    added = []
    families = {arc["id"]: arc.get("family_id", "") for arc in doc["arcs"]}
    sequence = 0

    def add(source, target, relation, ru, en, *, arc_id=ARC_ID, source_kind="evidence",
            target_kind="evidence", relationship_class="editorial_relationship", style="solid",
            evidence_level="A/B", strength="moderate", visual_lane="governance_law"):
        nonlocal sequence
        sequence += 1
        added.append({
            "id": f"EDGE_V037_GLOBAL_{sequence:03d}", "source": source, "target": target,
            "source_kind": source_kind, "target_kind": target_kind, "relation": relation,
            "arc_id": arc_id, "arc_family_id": families.get(arc_id, ""), "strength": strength,
            "evidence_level": evidence_level, "visual_lane": visual_lane, "style": style,
            "summary_ru": ru, "summary_en": en, "kind": "edge", "is_auto": False,
            "relationship_class": relationship_class,
        })

    for event in raw["events"]:
        for arc_id in event["arcs"]:
            add(event["id"], arc_id, "part_of_arc",
                "Тематическая принадлежность; связь не доказывает всю сюжетную дугу.",
                "Thematic membership; the link does not prove the whole story arc.",
                arc_id=arc_id, target_kind="story_arc", relationship_class="thematic", style="dashed")
    for event_id in EXISTING_GLOBAL_EVENTS:
        add(event_id, ARC_ID, "part_of_arc",
            "Существующий факт включён в сравнительную дугу; связь не приравнивает национальные режимы.",
            "The existing fact joins the comparative arc; the link does not equate national regimes.",
            target_kind="story_arc", relationship_class="thematic", style="dashed")

    for event_id in [event["id"] for event in raw["events"]] + EXISTING_GLOBAL_EVENTS:
        add(event_id, CLAIM_ID, "supports_with_scope",
            "Поддерживает сравнительный тезис только в пределах указанной правовой силы и объекта контроля.",
            "Supports the comparative claim only within the stated legal force and control object.",
            target_kind="claim_check", relationship_class="evidential")

    relationships = [
        ("SIG_2023_CHINA_GENAI_INTERIM_MEASURES", "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE", "institutionalizes",
         "Административная статистика показывает применение режима регистрации, созданного временными мерами 2023 года.",
         "Administrative counts show operation of the filing regime created by the 2023 Interim Measures."),
        ("SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS", "SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS", "context_for",
         "Многосторонние обязательства создают контекст для дорелизной оценки, но не доказывают причинность конкретного доступа AISI.",
         "The multilateral commitments provide context for pre-release evaluation but do not establish that they caused AISI's access."),
        ("SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "precedes_and_qualifies",
         "Добровольные пороги существовали до предложения Амодеи и ограничивают тезис о полной новизне идеи.",
         "Voluntary thresholds predated Amodei's proposal and qualify claims that the idea was wholly new."),
        ("SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "precedes_and_qualifies",
         "Государственный оценщик уже получал дорелизный доступ, хотя Амодеи предлагает более постоянную и глубокую модель присутствия.",
         "A state evaluator already received pre-release access, although Amodei proposes a more continuous and deeply embedded model."),
        ("SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "parallel",
         "Полномочия ЕС дают обязательный контур оценки и ограничения доступности, параллельный корпоративному предложению, но не тождественный ему.",
         "EU powers create a binding evaluation and availability gate parallel to, but distinct from, the company proposal."),
        ("SIG_2026_KOREA_NAVER_SOVEREIGN_MODEL_EXCLUSION", "SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL", "context_for",
         "Критерии происхождения и контроля весов создают контекст для программы собственной кибермодели без доказательства прямой причинности.",
         "Weight provenance and control criteria provide context for the domestic cyber-model programme without establishing direct causation."),
        ("SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS", "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE", "parallel",
         "Политика жизненного цикла агентов и действующий реестр сервисов показывают соседние, но самостоятельные контуры китайского регулирования.",
         "Agent lifecycle policy and the operating service registry show adjacent but separate Chinese governance channels."),
    ]
    for source, target, relation, ru, en in relationships:
        add(source, target, relation, ru, en)

    doc["edges"].extend(added)
    attach_edge_links(doc, {edge["id"] for edge in added})
    return [edge["id"] for edge in added]


def update_metadata(doc, raw, added_edge_ids):
    lang = doc["language"]
    event_ids = [event["id"] for event in raw["events"]]
    doc["meta"].update(version=VERSION, updated_at=DATE, schema_version="ai_stack_structural_power.v0.37.0-2026-09-14")
    entry = {
        "version": VERSION, "date": DATE,
        "description": "Global comparison of voluntary thresholds, pre-release evaluator access, market and service gates, and sovereign continuity programmes.",
        "added_evidence": len(event_ids), "added_claims": 0, "added_claim_checks": 0,
        "added_story_arcs": 0, "added_story_edges": len(added_edge_ids),
        "updated_claim_checks": [CLAIM_ID, "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"],
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
        "ru": "СРАВНЕНИЕ РЕЖИМОВ (v0.37): контрольные точки существуют за пределами США, но регулируют разные объекты — разработку и выпуск, дорелизную оценку, доступ на рынок, регистрацию сервиса или непрерывность поставок. Это не единый мировой режим замедления.",
        "en": "REGIME COMPARISON (v0.37): checkpoints exist beyond the United States, but govern different objects—development and deployment, pre-release evaluation, market access, service filing or supply continuity. This is not one global slowdown regime.",
    }
    summary["key_findings"] = [finding[lang]] + summary.get("key_findings", [])
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["corrections"] = [finding[lang]] + doc["presentation"].get("corrections", [])
    doc["presentation"]["release_notes"] = [{
        "title": "Разные контрольные точки" if lang == "ru" else "Different checkpoints",
        "text": finding[lang],
    }, {
        "title": "Нормативная сила" if lang == "ru" else "Legal force",
        "text": ("Добровольные обязательства, доступ оценщика, законный допуск и административная регистрация показаны раздельно."
                 if lang == "ru" else "Voluntary commitments, evaluator access, statutory gates and administrative filing remain separately classified."),
    }]
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update({
        "version": VERSION,
        "v037_base_commit": raw["meta"]["base_commit"],
        "v037_base_sha256": raw["meta"]["base_sha256"][lang],
        "v037_added_event_ids": event_ids,
        "v037_added_edge_ids": added_edge_ids,
        "v037_reused_event_ids": EXISTING_GLOBAL_EVENTS,
        "v037_updated_claim_check_ids": [CLAIM_ID, "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"],
        "v037_updated_arc_ids": [ARC_ID, "ARC_QUIET_ACCESS_CONTROL", "ARC_SOVEREIGN_FLOW_GATING", "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK", "ARC_CHINA_COUNTERSTACK_ROUTE_AROUND"],
        "v037_source_package": "review/global-pacing-access-regimes",
    })
    doc["factcheckAudit"]["v037_scope"] = {
        "date": DATE, "accepted_records": len(event_ids), "source_records": len(raw["sources"]),
        "deferred_records": len(raw["deferred"]), "implemented_common_pacing_regime": False,
        "note": "Voluntary commitments, evaluator access, binding market powers, service filing and sovereignty programmes remain separate evidence types.",
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]), "story_edges": len(doc["edges"]), "last_recomputed": DATE,
        "v0_37_added_evidence": len(event_ids), "v0_37_added_edges": len(added_edge_ids),
        "v0_37_updated_arcs": doc["migrationAudit"]["v037_updated_arc_ids"],
    })


def migrate(doc, raw):
    if doc["meta"]["version"] != "0.36":
        raise ValueError("Expected v0.36 input")
    original_dates = {event["id"]: event["date"] for event in doc["events"]}
    original_urls = {source["url"] for source in doc["sourceIndex"]}
    sources = {source["id"]: source for source in raw["sources"]}
    new_ids = [event["id"] for event in raw["events"]]
    all_ids = {node["id"] for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"] for node in doc.get(collection, [])}
    if len(new_ids) != 3 or len(set(new_ids)) != 3 or set(new_ids) & all_ids:
        raise ValueError("Candidate count or ID collision")
    doc["events"].extend(make_event(event, doc["language"], sources, doc) for event in raw["events"])
    patch_claims(doc, raw, sources)
    patch_event_and_arc_membership(doc, raw)
    added_edge_ids = add_edges(doc, raw)
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, raw, added_edge_ids)
    doc["referenceIntegrity"] = references(doc)
    if not doc["referenceIntegrity"]["valid"]:
        raise ValueError(doc["referenceIntegrity"])
    current_dates = {event["id"]: event["date"] for event in doc["events"]}
    if not all(current_dates[event_id] == date for event_id, date in original_dates.items()):
        raise ValueError("A pre-v0.37 event date changed")
    if not original_urls <= {source["url"] for source in doc["sourceIndex"]}:
        raise ValueError("A pre-v0.37 source URL was lost")
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="directory containing the exact v0.36 bilingual JSON pair")
    parser.add_argument("--output", type=Path, required=True, help="destination directory for the migrated JSON pair")
    args = parser.parse_args()
    raw = json.loads((PACKAGE / "candidates.json").read_text())
    loaded = {}
    for lang in ["ru", "en"]:
        path = args.root / f"ai_power_storygraph_{lang}.json"
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != raw["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{path.name}: expected pinned v0.36 SHA-256; refusing input {digest}")
        loaded[lang] = json.loads(data)
    rendered = {lang: (json.dumps(migrate(doc, raw), ensure_ascii=False, indent=2) + "\n").encode() for lang, doc in loaded.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, data in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_bytes(data)
        os.replace(temporary, path)
        doc = json.loads(data)
        print(lang, len(doc["events"]), "events", len(doc["claimChecks"]), "claim checks", len(doc["arcs"]), "arcs", len(doc["edges"]), "edges", len(doc["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()
