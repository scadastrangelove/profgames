#!/usr/bin/env python3
"""Build the pinned v0.35 -> v0.36 frontier-pacing update.

The migration separates binding national-security directives, company policy
proposals, public commitments and political rhetoric. It never contacts the
network and refuses inputs whose SHA-256 differs from the reviewed v0.35 pair.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review/frontier-pacing-september-2026"
DATE = "2026-09-14"
VERSION = "0.36"
CLAIM_ID = "CLM_031_FRONTIER_PACING_AUTHORITY"
ARC_ID = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"


def pair(obj, key, ru, en, lang):
    obj[key + "_ru"] = copy.deepcopy(ru)
    obj[key + "_en"] = copy.deepcopy(en)
    obj[key] = copy.deepcopy(ru if lang == "ru" else en)


def source_record(source):
    return {key: copy.deepcopy(value) for key, value in source.items() if key != "id"}


def add_source(node, source):
    urls = {item.get("url") for item in node.get("sources", []) if isinstance(item, dict)}
    if source["url"] not in urls:
        node.setdefault("sources", []).append(source_record(source))


def arc_families(doc, arc_ids):
    by_id = {arc["id"]: arc.get("family_id") for arc in doc["arcs"]}
    return uniq(by_id.get(arc_id) for arc_id in arc_ids)


def event_record(raw, lang, sources, doc):
    event_sources = [source_record(sources[source_id]) for source_id in raw["source_ids"]]
    primary = event_sources[0]
    event = {
        "id": raw["id"],
        "kind": "event",
        "date": raw["date"],
        "year": int(raw["date"][:4]),
        "source_date": primary["date"],
        "date_basis": raw["date_basis"],
        "date_status": raw["date_status"],
        "url": primary["url"],
        "source_name": primary["name"],
        "source_type_raw": primary["source_class"],
        "source_type": primary["type"],
        "primary_or_secondary": primary["primary_or_secondary"],
        "actor": ", ".join(raw["actors"]),
        "actor_raw": ", ".join(raw["actors"]),
        "actors_raw": copy.deepcopy(raw["actors"]),
        "actors": copy.deepcopy(raw["actors"]),
        "actor_facets_legacy": copy.deepcopy(raw["actors"]),
        "actor_facets": copy.deepcopy(raw["actors"]),
        "actor_entities": copy.deepcopy(raw["actors"]),
        "actor_types": copy.deepcopy(raw["actor_types"]),
        "actor_jurisdictions": copy.deepcopy(raw["jurisdictions"]),
        "geography_raw": copy.deepcopy(raw["jurisdictions"]),
        "geography": copy.deepcopy(raw["jurisdictions"]),
        "jurisdictions": copy.deepcopy(raw["jurisdictions"]),
        "regions": [],
        "locations": [],
        "institutional_scopes": ["national_security"] if raw["id"] in {
            "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS", "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL"
        } else [],
        "geo_context": [],
        "geographic_scopes": ["National"],
        "geography_unclassified": [],
        "actor_unclassified": [],
        "actor_classification_status": "resolved",
        "geography_classification_status": "resolved",
        "evidence_context": copy.deepcopy(raw["contexts"]),
        "evidence_method": raw["method"],
        "stack_layer": copy.deepcopy(raw["stack_layers"]),
        "stack_layers": copy.deepcopy(raw["stack_layers"]),
        "strange_structure": copy.deepcopy(raw["structures"]),
        "strange_structures": copy.deepcopy(raw["structures"]),
        "research_question": copy.deepcopy(raw["research_questions"]),
        "exact_quote_short": "",
        "numbers": copy.deepcopy(raw["numbers"]),
        "money_status": "",
        "confidence": raw["confidence"],
        "evidence_level": raw["confidence"],
        "status": raw["status"],
        "cyber_domain_ids": copy.deepcopy(raw["domains"]),
        "cyber_subdomain_ids": [],
        "cyber_role_ids": copy.deepcopy(raw["roles"]),
        "cyber_access_principal": False,
        "primary_domain_id": raw["primary_domain"],
        "artifact_kind": raw["artifact"],
        "normative_force": raw["force"],
        "implementation_stage": raw["stage"],
        "delegated_authority": raw["delegation"],
        "editorial_priority": raw["priority"],
        "sources": event_sources,
        "edgeIds": [],
        "arcIds": copy.deepcopy(raw["arcs"]),
        "arcFamilyIds": arc_families(doc, raw["arcs"]),
        "relationTypes": [],
        "research_updates": ["frontier-pacing-september-2026"],
        "classification_review": {
            "date": DATE,
            "method": raw["method"],
            "independent_source_reverification": len(raw["source_ids"]) > 1,
            "independent_replication": False,
        },
        "governance_scale": "provider_state_and_national_security_policy",
        "behavioral_mechanism_ids": [],
        "behavioral_status": ["policy_response"],
        "agent_population_scope": "not_applicable",
        "shared_writable_state": "unknown",
        "oversight_target": ["institutional_process"],
        "motivation_basis": "no_motivation_claim",
        "behavior_track_ids": [],
        "behavior_origin": "not_applicable",
        "concealment_targets": ["none"],
        "persistence_media": ["not_established"],
        "goal_source": "not_applicable",
        "candidate_evidence_tier": "primary_source_reviewed" if primary["primary_or_secondary"] == "primary" else "secondary_source_reviewed",
    }
    pair(event, "title", raw["title_ru"], raw["title_en"], lang)
    pair(event, "summary", raw["summary_ru"], raw["summary_en"], lang)
    pair(event, "claim_supported", raw["summary_ru"], raw["summary_en"], lang)
    for key in ["notes", "caveat", "corroboration_needed", "claim_challenged", "scope"]:
        pair(event, key, raw["caveat_ru"], raw["caveat_en"], lang)
    pair(event, "caveats", [raw["caveat_ru"]], [raw["caveat_en"]], lang)
    pair(event, "safe_wording", raw["safe_ru"], raw["safe_en"], lang)
    pair(
        event,
        "role_basis",
        "Роли описывают место ИИ в документе или споре и не приписывают модели самостоятельную волю.",
        "Roles describe AI's place in the document or dispute and do not attribute independent intent to a model.",
        lang,
    )
    pair(
        event,
        "editorial_rationale",
        "Карточка отделяет обязательное предписание, предложение, публичное обещание или риторику от данных об исполнении. " + raw["safe_ru"],
        "The record separates a binding directive, proposal, public commitment or rhetoric from implementation evidence. " + raw["safe_en"],
        lang,
    )
    return event


def arc_record(raw, lang):
    arc = {
        "id": raw["id"],
        "kind": "arc",
        "arc_type": raw["arc_type"],
        "status": raw["status"],
        "start_date": raw["start_date"],
        "end_date": raw["end_date"],
        "visual_lanes": copy.deepcopy(raw["visual_lanes"]),
        "key_nodes": [
            "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS",
            "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL",
            "export-13",
            "SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE",
            "export-14",
            "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL",
            "SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS",
            "SIG_2026_TRUMP_REJECTS_FRONTIER_PACING",
            CLAIM_ID,
        ],
        "family_id": raw["family_id"],
        "arc_kind": raw["arc_kind"],
        "parent_arc_id": raw["parent_arc_id"],
        "edgeIds": [],
        "arcIds": [raw["id"]],
        "arcFamilyIds": [raw["family_id"]],
        "relationTypes": [],
    }
    pair(arc, "title", raw["title_ru"], raw["title_en"], lang)
    pair(arc, "thesis", raw["thesis_ru"], raw["thesis_en"], lang)
    pair(arc, "safe_wording", raw["safe_wording_ru"], raw["safe_wording_en"], lang)
    pair(arc, "counterpoints", raw["counterpoints_ru"], raw["counterpoints_en"], lang)
    return arc


def claim_check_record(raw, lang, sources, doc):
    item = {
        "id": raw["id"],
        "kind": "claimCheck",
        "status": raw["status"],
        "confidence": raw["confidence"],
        "supporting_evidence": copy.deepcopy(raw["supporting_evidence"]),
        "qualifying_evidence": copy.deepcopy(raw["qualifying_evidence"]),
        "what_could_break_it_ru": raw["what_could_break_it_ru"],
        "what_could_break_it_en": raw["what_could_break_it_en"],
        "what_could_break_it": raw[f"what_could_break_it_{lang}"],
        "date_relevant": "2026",
        "stack_layer": ["governance_law", "model_weights", "cloud_inference", "decision_support_cognition"],
        "strange_structure": ["security", "knowledge", "production"],
        "geography": ["US", "Global"],
        "keywords": ["pacing", "frontier models", "checkpoints", "continuity", "reverse chokepoint", "structural power"],
        "sources": [source_record(sources[source_id]) for source_id in raw["source_ids"]],
        "arcIds": copy.deepcopy(raw["arc_ids"]),
        "arcFamilyIds": arc_families(doc, raw["arc_ids"]),
        "edgeIds": [],
        "relationTypes": [],
    }
    pair(item, "title", raw["title_ru"], raw["title_en"], lang)
    pair(item, "claim", raw["claim_ru"], raw["claim_en"], lang)
    pair(item, "safe_wording", raw["safe_ru"], raw["safe_en"], lang)
    pair(item, "recommended_phrasing", raw["safe_ru"], raw["safe_en"], lang)
    pair(item, "caveats", [raw["safe_ru"]], [raw["safe_en"]], lang)
    return item


def patch_existing_claims(doc, sources):
    lang = doc["language"]
    checks = {item["id"]: item for item in doc["claimChecks"]}
    decision = checks["CLM_026_DECISION_SOVEREIGNTY_MITIGATION"]
    decision["supporting_evidence"] = uniq(decision.get("supporting_evidence", []) + [
        "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS", "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL"
    ])
    decision["confidence"] = "A/B"
    pair(decision, "title",
         "Частные поставщики влияют на границы военных решений, а государство отвечает архитектурой заменяемости и контроля непрерывности",
         "Private suppliers shape military decision boundaries, while the state responds with replaceability and continuity controls", lang)
    pair(decision, "claim",
         "Зависимость военного контура от частных моделей создаёт для поставщика рычаг над доступом и условиями применения. Стратегия Пентагона и NSPM-11 теперь прямо требуют модульности, нескольких поставщиков и запрета на одностороннее отключение критичных систем; это подтверждает механизм снижения зависимости, но ещё не его полное исполнение.",
         "Reliance on private models gives suppliers leverage over access and conditions of use. The Pentagon strategy and NSPM-11 now explicitly require modularity, multiple suppliers and protection against unilateral shutdown of mission systems; this establishes the mitigation mechanism, not its complete implementation.", lang)
    pair(decision, "safe_wording",
         "Говорить о закреплённом механизме снижения зависимости в контуре национальной безопасности, а не о достигнутой независимости от поставщиков.",
         "Describe an established dependency-mitigation mechanism in the national-security enterprise, not achieved independence from suppliers.", lang)
    pair(decision, "recommended_phrasing", decision["safe_wording_ru"], decision["safe_wording_en"], lang)
    pair(decision, "caveats", [decision["safe_wording_ru"]], [decision["safe_wording_en"]], lang)
    for source_id in ["S01", "S02"]:
        add_source(decision, sources[source_id])
    decision["research_updates"] = uniq(decision.get("research_updates", []) + ["frontier-pacing-september-2026"])

    resilience = checks["CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"]
    resilience["supporting_evidence"] = uniq(resilience.get("supporting_evidence", []) + [
        "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL"
    ])
    pair(resilience, "title",
         "Государственная киберустойчивость ИИ охватывает не только оценку модели, но и темп, независимый контроль и непрерывность доступа",
         "Public AI cyber resilience extends beyond model evaluation to pacing, independent oversight and continuity of access", lang)
    pair(resilience, "claim",
         "В 2026 году меры разных юрисдикций охватили разработчиков, веса, полномочия агентов, среды исполнения, инфраструктуру, исправление и восстановление. NSPM-11 добавляет непрерывность критичного доступа, а предложение Амодеи — контрольные точки возможностей и постоянно встроенных внешних оценщиков. Это неоднородный набор действующих требований и предложений, а не единый мировой режим.",
         "In 2026, measures across jurisdictions covered developers, weights, agent authority, runtimes, infrastructure, remediation and recovery. NSPM-11 adds continuity of mission access, while Amodei's proposal adds capability checkpoints and permanently embedded external evaluators. This is a heterogeneous mix of operative requirements and proposals, not one global regime.", lang)
    pair(resilience, "safe_wording",
         "Разделять обязательные требования, надзорные позиции, внутренние политики и предложения. Наличие элемента в стеке не доказывает его внедрение или эффективность.",
         "Separate binding requirements, supervisory positions, internal policies and proposals. A component's presence in the stack does not establish implementation or effectiveness.", lang)
    pair(resilience, "recommended_phrasing", resilience["safe_wording_ru"], resilience["safe_wording_en"], lang)
    pair(resilience, "caveats", [resilience["safe_wording_ru"]], [resilience["safe_wording_en"]], lang)
    for source_id in ["S02", "S03"]:
        add_source(resilience, sources[source_id])
    resilience["research_updates"] = uniq(resilience.get("research_updates", []) + ["frontier-pacing-september-2026"])


def patch_existing_arcs(doc, raw):
    lang = doc["language"]
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    for event in raw["events"]:
        for arc_id in event["arcs"]:
            arc = arcs[arc_id]
            arc["key_nodes"] = uniq(arc.get("key_nodes", []) + [event["id"]])
            arc["end_date"] = max(arc.get("end_date", ""), event["date"])

    texts = {
        "ARC_QUIET_ACCESS_CONTROL": (
            "Контроль действует через проверку клиентов, уровни допуска, журналы запросов, отзыв аккаунтов, контрольные точки выпуска и доступ внешних оценщиков. NSPM-11 добавляет встречное ограничение: в контуре национальной безопасности поставщик не должен единолично отключать уже используемую систему. Это спор о том, кто управляет доступом, а не доказательство полной видимости одной стороны.",
            "Control operates through customer review, access tiers, request logs, account revocation, release checkpoints and external-evaluator access. NSPM-11 adds a countervailing constraint: in the national-security enterprise, a supplier should not unilaterally disable an adopted system. This is a contest over access authority, not evidence that either side has complete visibility.",
        ),
        "ARC_SOVEREIGN_FLOW_GATING": (
            "Государства и провайдеры оспаривают поставку чипов и моделей, допустимый доступ к выходам, темп разработки и непрерывность уже принятой системы. Предложение Амодеи опирается на экспортные ограничения ради сохранения преимущества США, тогда как NSPM-11 ограничивает обратный рычаг поставщика над государством. Подтверждены встречные механизмы контроля, но не единый режим и не окончательный баланс сил.",
            "States and providers contest chip and model supply, legitimate access to outputs, development pace and continuity of an adopted system. Amodei's proposal relies on export controls to preserve a U.S. lead, while NSPM-11 limits the supplier's reverse leverage over the state. The opposing control mechanisms are established, not one coherent regime or a final balance of power.",
        ),
        "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": (
            "Киберустойчивость ИИ включает разработку, испытания, исправление, восстановление, наблюдение за использованием, контроль темпа возможностей и непрерывность критичного доступа. NSPM-11 закрепляет часть требований для национальной безопасности; схема Амодеи предлагает контрольные точки и постоянно встроенных внешних оценщиков. Действующие нормы и предложения должны оставаться раздельными.",
            "AI cyber resilience includes development, testing, remediation, recovery, use monitoring, capability pacing and continuity of mission access. NSPM-11 establishes part of this for the national-security enterprise; Amodei's framework proposes checkpoints and permanently embedded external evaluators. Operative rules and proposals must remain distinct.",
        ),
        "ARC_PALANTIR_DECISION_OS": (
            "Palantir показывает захват структуры знания: институт интегрирует данные, строит общую оперативную картину и действует через программный слой частного поставщика. Стратегия Пентагона и NSPM-11 отвечают на такую зависимость требованиями модульности, нескольких поставщиков и контроля непрерывности доступа.",
            "Palantir illustrates knowledge-structure capture: an institution integrates data, builds a common operating picture and acts through a private supplier's software layer. The Pentagon strategy and NSPM-11 respond to such dependency with modularity, multiple suppliers and continuity controls.",
        ),
    }
    safe = {
        "ARC_QUIET_ACCESS_CONTROL": (
            "Различать контроль поставщика над сервисом, государственные закупочные полномочия и предложения саморегулирования; это разные источники власти.",
            "Distinguish supplier control over a service, state procurement authority and self-regulatory proposals; they are different sources of power.",
        ),
        "ARC_SOVEREIGN_FLOW_GATING": (
            "Не сводить встречные ограничения к полному контролю государства или компании; сфера действия, исполнение и судебные пределы различаются.",
            "Do not reduce opposing constraints to complete state or corporate control; scope, implementation and judicial limits differ.",
        ),
        "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": (
            "Отделять обязательные предписания и наблюдаемое исполнение от добровольных обещаний и проектов будущего режима.",
            "Separate binding directions and observed implementation from voluntary commitments and proposals for a future regime.",
        ),
        "ARC_PALANTIR_DECISION_OS": (
            "Не утверждать, что Palantir владеет государственными данными. Компания поставляет оперативный слой, через который институты интегрируют, запрашивают и используют чувствительные данные; степень зависимости зависит от архитектуры и контрактов.",
            "Do not say that Palantir owns government data. It supplies an operational layer through which institutions integrate, query and use sensitive data; dependency depends on architecture and contracts.",
        ),
    }
    for arc_id, (ru, en) in texts.items():
        pair(arcs[arc_id], "thesis", ru, en, lang)
        pair(arcs[arc_id], "safe_wording", safe[arc_id][0], safe[arc_id][1], lang)


def add_edges(doc, raw):
    new = []
    sequence = 0
    family_by_arc = {arc["id"]: arc.get("family_id", "") for arc in doc["arcs"]}

    def add(source, target, relation, ru, en, *, arc_id=ARC_ID, source_kind="evidence",
            target_kind="evidence", relationship_class="editorial_relationship", style="solid",
            evidence_level="A/B", strength="moderate", visual_lane="governance_law"):
        nonlocal sequence
        sequence += 1
        new.append({
            "id": f"EDGE_V036_PACING_{sequence:03d}",
            "source": source,
            "target": target,
            "source_kind": source_kind,
            "target_kind": target_kind,
            "relation": relation,
            "arc_id": arc_id,
            "arc_family_id": family_by_arc.get(arc_id, ""),
            "strength": strength,
            "evidence_level": evidence_level,
            "visual_lane": visual_lane,
            "style": style,
            "summary_ru": ru,
            "summary_en": en,
            "kind": "edge",
            "is_auto": False,
            "relationship_class": relationship_class,
        })

    for event in raw["events"]:
        for arc_id in event["arcs"]:
            add(event["id"], arc_id, "part_of_arc",
                "Тематическая принадлежность; связь не доказывает всю сюжетную дугу.",
                "Thematic membership; the link does not prove the whole story arc.",
                arc_id=arc_id, target_kind="story_arc", relationship_class="thematic", style="dashed")

    relation_by_event = {
        "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS": "supports_with_scope",
        "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL": "supports_with_scope",
        "SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE": "supports_with_scope",
        "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL": "supports_as_claim_not_fact",
        "SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS": "supports_as_claim_not_fact",
        "SIG_2026_TRUMP_REJECTS_FRONTIER_PACING": "supports_as_claim_not_fact",
    }
    for event_id, relation in relation_by_event.items():
        add(event_id, CLAIM_ID, relation,
            "Поддерживает утверждение о споре за полномочия только в пределах типа этого свидетельства.",
            "Supports the authority-contest claim only within this evidence type's stated scope.",
            target_kind="claim_check", relationship_class="evidential")

    add("export-14", CLAIM_ID, "qualifies",
        "Судебное решение показывает пределы исполнительной власти над поставщиком.",
        "The court ruling demonstrates limits on executive authority over a supplier.",
        source_kind="claim", target_kind="claim_check", relationship_class="evidential_qualification", style="dashed")
    add(CLAIM_ID, ARC_ID, "supports_arc",
        "Проверяемый тезис связывает темп, выпуск и непрерывность доступа без утверждения о едином режиме.",
        "The scoped claim connects pace, release and continuity without asserting one unified regime.",
        source_kind="claim_check", target_kind="story_arc", relationship_class="evidential")
    for thesis_id in ["THESIS_ACCESS_AS_POWER", "THESIS_DECISION_SOVEREIGNTY", "THESIS_CORE"]:
        add(CLAIM_ID, thesis_id, "supports_with_scope",
            "Встречные полномочия над темпом и доступом поддерживают тезис только с оговорками об исполнении и сфере действия.",
            "Opposing authority over pace and access supports the thesis only with implementation and scope caveats.",
            source_kind="claim_check", target_kind="synthetic_thesis", relationship_class="evidential")
    add("SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL", "CLM_026_DECISION_SOVEREIGNTY_MITIGATION", "materially_updates",
        "Меморандум переводит архитектурную рекомендацию о независимости от поставщика в обязательное направление для национальной безопасности.",
        "The memorandum turns supplier-dependency mitigation from an architectural recommendation into a binding national-security direction.",
        arc_id="ARC_PALANTIR_DECISION_OS", target_kind="claim_check")

    relationships = [
        ("SIG_2026_DOW_AI_STRATEGY_SPEED_WINS", "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL", "context_for", "Январская стратегия задаёт закупочную доктрину скорости и заменяемости, на фоне которой действует июньский меморандум.", "The January strategy supplies the speed-and-replaceability procurement context for the June memorandum."),
        ("SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "precedes_and_qualifies", "Подтверждённая пауза конкретного обучения предшествует более широкой схеме Амодеи, но не доказывает её принятие.", "A verified pause in one training run precedes Amodei's broader framework but does not establish its adoption."),
        ("SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS", "develops_into", "Предложение вызвало публичную поддержку, но лишь одно сопоставимое обязательство по внешним оценщикам.", "The proposal drew public endorsements but only one comparable external-evaluator commitment."),
        ("SIG_2026_TRUMP_REJECTS_FRONTIER_PACING", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "countermove", "Президентская реакция публично противопоставила предложению доктрину ускорения и конкуренции с Китаем.", "The presidential response publicly opposed the proposal with an acceleration and China-competition doctrine."),
        ("SIG_2026_DOW_AI_STRATEGY_SPEED_WINS", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "challenges", "Ведомственная доктрина скорости противостоит общему предложению замедлять рост возможностей, хотя их сферы действия различаются.", "The department's speed doctrine cuts against general capability pacing, although the two have different scopes."),
        ("SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL", "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "qualifies", "Право лаборатории задерживать выпуск ограничивается там, где государство закрепляет непрерывность уже принятой системы.", "A laboratory's release discretion is constrained where the state establishes continuity for an adopted mission system."),
    ]
    for source, target, relation, ru, en in relationships:
        add(source, target, relation, ru, en)

    doc["edges"].extend(new)
    attach_edge_links(doc, {edge["id"] for edge in new})
    return [edge["id"] for edge in new]


def update_metadata(doc, raw, added_edge_ids):
    lang = doc["language"]
    event_ids = [event["id"] for event in raw["events"]]
    doc["meta"].update(version=VERSION, updated_at=DATE, schema_version="ai_stack_structural_power.v0.36.0-2026-09-14")
    entry = {
        "version": VERSION,
        "date": DATE,
        "description": "Frontier-model pacing, embedded evaluators, national-security continuity controls and the public acceleration dispute.",
        "added_evidence": len(event_ids),
        "added_claims": 0,
        "added_claim_checks": 1,
        "added_story_arcs": 1,
        "added_story_edges": len(added_edge_ids),
        "updated_claim_checks": ["CLM_026_DECISION_SOVEREIGNTY_MITIGATION", "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"],
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
        "ru": "ТЕМП И НЕПРЕРЫВНОСТЬ (v0.36): лаборатории предъявили право замедлять обучение и выпуск, а государство — право требовать скорость, заменяемость и защиту от одностороннего отключения. Подтверждены встречные механизмы, а не общий режим или итоговый победитель.",
        "en": "PACE AND CONTINUITY (v0.36): laboratories asserted authority to slow training and release, while the state asserted speed, replaceability and protection against unilateral shutdown. The opposing mechanisms are established, not one common regime or a final winner.",
    }
    summary["key_findings"] = [finding[lang]] + summary.get("key_findings", [])
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["corrections"] = [finding[lang]] + doc["presentation"].get("corrections", [])
    doc["presentation"]["release_notes"] = [{
        "title": "Темп и непрерывность" if lang == "ru" else "Pace and continuity",
        "text": finding[lang],
    }, {
        "title": "Разная нормативная сила" if lang == "ru" else "Different legal force",
        "text": ("Стратегия и меморандум, предложение Амодеи, добровольные обещания и политическая риторика показаны раздельно."
                 if lang == "ru" else "The strategy and memorandum, Amodei proposal, voluntary commitments and political rhetoric remain separately classified."),
    }]
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update({
        "version": VERSION,
        "v036_base_commit": raw["meta"]["base_commit"],
        "v036_base_sha256": raw["meta"]["base_sha256"][lang],
        "v036_added_event_ids": event_ids,
        "v036_added_claim_check_ids": [CLAIM_ID],
        "v036_added_arc_ids": [ARC_ID],
        "v036_added_edge_ids": added_edge_ids,
        "v036_updated_claim_check_ids": ["CLM_026_DECISION_SOVEREIGNTY_MITIGATION", "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"],
        "v036_source_package": "review/frontier-pacing-september-2026",
    })
    doc["factcheckAudit"]["v036_scope"] = {
        "date": DATE,
        "accepted_records": len(event_ids),
        "source_records": len(raw["sources"]),
        "deferred_records": len(raw["deferred"]),
        "binding_documents": 2,
        "implemented_common_pacing_regime": False,
        "note": "Binding directives, a company proposal, differentiated industry endorsements and presidential rhetoric remain separate evidence types.",
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]),
        "story_edges": len(doc["edges"]),
        "last_recomputed": DATE,
        "v0_36_added_evidence": len(event_ids),
        "v0_36_added_claim_checks": 1,
        "v0_36_added_arcs": 1,
        "v0_36_added_edges": len(added_edge_ids),
        "v0_36_updated_arcs": sorted({arc_id for event in raw["events"] for arc_id in event["arcs"]}),
    })


def migrate(doc, raw):
    if doc["meta"]["version"] != "0.35":
        raise ValueError("Expected v0.35 input")
    original_dates = {event["id"]: event["date"] for event in doc["events"]}
    original_urls = {source["url"] for source in doc["sourceIndex"]}
    sources = {source["id"]: source for source in raw["sources"]}
    event_ids = [event["id"] for event in raw["events"]]
    all_ids = {node["id"] for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"] for node in doc.get(collection, [])}
    if len(event_ids) != 5 or len(set(event_ids)) != 5 or set(event_ids) & all_ids or {CLAIM_ID, ARC_ID} & all_ids:
        raise ValueError("Candidate count or ID collision")

    doc["arcs"].append(arc_record(raw["arc"], doc["language"]))
    doc["events"].extend(event_record(event, doc["language"], sources, doc) for event in raw["events"])
    doc["claimChecks"].append(claim_check_record(raw["claim_check"], doc["language"], sources, doc))
    patch_existing_claims(doc, sources)
    patch_existing_arcs(doc, raw)
    added_edge_ids = add_edges(doc, raw)
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, raw, added_edge_ids)
    doc["referenceIntegrity"] = references(doc)
    if not doc["referenceIntegrity"]["valid"]:
        raise ValueError(doc["referenceIntegrity"])
    if not all(next(item for item in doc["events"] if item["id"] == event_id)["date"] == date for event_id, date in original_dates.items()):
        raise ValueError("A pre-v0.36 event date changed")
    if not original_urls <= {source["url"] for source in doc["sourceIndex"]}:
        raise ValueError("A pre-v0.36 source URL was lost")
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="directory containing the exact v0.35 bilingual JSON pair")
    parser.add_argument("--output", type=Path, required=True, help="destination directory for the migrated JSON pair")
    args = parser.parse_args()
    raw = json.loads((PACKAGE / "candidates.json").read_text())
    loaded = {}
    for lang in ["ru", "en"]:
        path = args.root / f"ai_power_storygraph_{lang}.json"
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != raw["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{path.name}: expected pinned v0.35 SHA-256; refusing input {digest}")
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
