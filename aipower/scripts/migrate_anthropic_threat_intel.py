#!/usr/bin/env python3
"""Build the pinned v0.34 -> v0.35 Anthropic threat-intelligence update.

The migration adds atomic evidence, updates three existing claim checks, and
maps provider observability/access control into the wider structural-power
graph. It never contacts the network and refuses unpinned inputs.
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
PACKAGE = ROOT / "review/anthropic-threat-intel-september-2026"
DATE = "2026-09-11"
VERSION = "0.35"
TRACK_ID = "BEH_TRACK_CONCEALMENT_PERSISTENCE"
NEW_CLAIM_ID = "CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE"
TRACK_EVENT_IDS = {
    "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
    "SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY",
    "SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING",
}


def pair(obj, key, ru, en, lang):
    obj[key + "_ru"] = copy.deepcopy(ru)
    obj[key + "_en"] = copy.deepcopy(en)
    obj[key] = copy.deepcopy(ru if lang == "ru" else en)


def source_record(raw):
    return {key: copy.deepcopy(value) for key, value in raw.items() if key != "id"}


def add_source(node, source):
    if source["url"] not in {item.get("url") for item in node.get("sources", []) if isinstance(item, dict)}:
        node.setdefault("sources", []).append(source_record(source))


def arc_families(doc, arc_ids):
    by_id = {arc["id"]: arc.get("family_id") for arc in doc["arcs"]}
    return uniq(by_id[arc_id] for arc_id in arc_ids if by_id.get(arc_id))


def event_record(raw, lang, sources, doc):
    event_sources = [source_record(sources[source_id]) for source_id in raw["source_ids"]]
    primary = event_sources[0]
    caveat = raw[f"caveat_{lang}"]
    summary = raw[f"summary_{lang}"]
    safe = raw[f"safe_{lang}"]
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
        "geography_raw": uniq(raw["jurisdictions"] + ["Global"]),
        "geography": copy.deepcopy(raw["jurisdictions"]),
        "jurisdictions": copy.deepcopy(raw["jurisdictions"]),
        "regions": [],
        "locations": [],
        "institutional_scopes": [],
        "geo_context": [],
        "geographic_scopes": ["Global"],
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
        "cyber_subdomain_ids": copy.deepcopy(raw.get("subdomains") or []),
        "cyber_role_ids": copy.deepcopy(raw["roles"]),
        "cyber_access_principal": raw["delegation"] in {"observed", "evaluated"},
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
        "research_updates": ["anthropic-threat-intel-september-2026"],
        "classification_review": {
            "date": DATE,
            "method": "primary_source_review_with_explicit_provider_telemetry_scope",
            "source_url": primary["url"],
            "independent_source_reverification": raw["id"] == "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
            "independent_replication": False,
        },
        "governance_scale": "provider_and_state_operational_evidence",
        "behavioral_mechanism_ids": copy.deepcopy(raw["mechanisms"]),
        "behavioral_status": copy.deepcopy(raw["behavioral_statuses"]),
        "agent_population_scope": raw["population"],
        "shared_writable_state": raw["shared_state"],
        "oversight_target": copy.deepcopy(raw["oversight"]),
        "motivation_basis": raw["motivation"],
        "behavior_track_ids": [TRACK_ID] if raw["id"] in TRACK_EVENT_IDS else [],
        "behavior_origin": raw["behavior_origin"],
        "concealment_targets": copy.deepcopy(raw["concealment_targets"]),
        "persistence_media": copy.deepcopy(raw["persistence_media"]),
        "goal_source": raw["goal_source"],
        "candidate_evidence_tier": "primary_source_reviewed",
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
        "Роли описывают функцию ИИ в конкретном свидетельстве и не доказывают автономное намерение модели.",
        "Roles describe AI's function in the specific evidence and do not establish autonomous model intent.",
        lang,
    )
    pair(
        event,
        "editorial_rationale",
        "Карточка разделяет наблюдаемый механизм, атрибуцию провайдера и более широкую интерпретацию. " + raw["safe_ru"],
        "The record separates observed mechanism, provider attribution and broader interpretation. " + raw["safe_en"],
        lang,
    )
    return event


def claim_check_record(raw, lang, sources, doc):
    safe = raw[f"safe_{lang}"]
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
        "date_relevant": "2025-2026",
        "stack_layer": ["cloud_inference", "data_telemetry", "governance_law"],
        "strange_structure": ["security", "knowledge", "production"],
        "geography": ["Global"],
        "keywords": ["panopticon", "chokepoint", "provider telemetry", "access revocation", "structural power"],
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


def patch_distillation(doc, raw, sources):
    event = next(item for item in doc["events"] if item["id"] == "SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE")
    if event["date"] != "2026-02-23" or event["numbers"].get("interactions_more_than") != 16_000_000:
        raise ValueError("Pinned February distillation record changed")
    update = raw["existing_updates"][event["id"]]
    for source_id in update["source_ids"]:
        add_source(event, sources[source_id])
    state = {
        "observed_at": update["observed_at"],
        "event_date": None,
        "numbers": copy.deepcopy(update["numbers"]),
        "sources": [source_record(sources[source_id]) for source_id in update["source_ids"]],
    }
    pair(state, "title", update["title_ru"], update["title_en"], doc["language"])
    pair(state, "summary", update["summary_ru"], update["summary_en"], doc["language"])
    pair(state, "date_note", update["date_note_ru"], update["date_note_en"], doc["language"])
    event["current_state"] = state
    event["research_updates"] = uniq(event.get("research_updates", []) + ["anthropic-threat-intel-september-2026"])


def patch_claim_checks(doc):
    lang = doc["language"]
    by_id = {item["id"]: item for item in doc["claimChecks"]}
    required = {"CLM_006_MACHINE_SPEED_CYBER", "CLM_007_COGNITIVE_SECURITY", "CLM_013_QUIET_ACCESS_CONTROL"}
    if required - set(by_id):
        raise ValueError(f"Missing claim checks: {sorted(required - set(by_id))}")

    updates = {
        "CLM_006_MACHINE_SPEED_CYBER": {
            "support": [
                "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
                "SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY",
                "SIG_2026_ANTHROPIC_GTG50014_CREDENTIAL_SUPPLY_CHAIN",
            ],
            "title_ru": "Поиск уязвимостей, построение эксплойтов и проведение кампаний с помощью агентов ускоряются",
            "title_en": "Agent-assisted vulnerability research, exploit construction and campaign execution are accelerating",
            "claim_ru": "К лабораторным и отдельным производственным свидетельствам добавились описанные Anthropic операции GTG-20006, GTG-10007 и GTG-50014: адаптация к средствам обнаружения, непрерывный поиск возможных уязвимостей нулевого дня и масштабирование кражи учётных данных. Это подтверждает рост темпа и объёма в выбранных кампаниях, но не устанавливает их обычную частоту, полностью автономное наступление или самостоятельный умысел модели.",
            "claim_en": "Anthropic's GTG-20006, GTG-10007 and GTG-50014 cases add production evidence to laboratory and earlier operational findings: adaptation to detection, continuous research for possible zero-days, and scaled credential theft. They establish greater tempo and volume in selected campaigns, not ordinary prevalence, fully autonomous offense or independent model intent.",
            "safe_ru": "Три случая показывают ускорение реальных операций под внешней целью. Это отобранная телеметрия провайдера; возможные уязвимости нулевого дня не равны подтверждённым CVE, а люди сохраняли выбор целей и способов монетизации.",
            "safe_en": "Three cases show acceleration of real operations under an external objective. This is selected provider telemetry; possible zero-days are not validated CVEs, and humans retained target and monetization choices.",
        },
        "CLM_007_COGNITIVE_SECURITY": {
            "support": [
                "SIG_2026_ANTHROPIC_STATE_SURVEILLANCE_BUREAUCRACY",
                "SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING",
            ],
            "title_ru": "Поддержка решений с помощью ИИ создаёт скрытую поверхность влияния",
            "title_en": "AI-mediated decision support creates a hidden influence surface",
            "claim_ru": "Помимо внедрения инструкций через данные, Anthropic описала использование Claude в конкретных государственных процессах слежки и девяти операциях влияния с постоянными доктринальными файлами и сокрытием происхождения сообщений. Это подтверждает механизм в реальной эксплуатации, но не доказывает массовость, убеждающий эффект или изменение государственных решений.",
            "claim_en": "Beyond instruction injection through data, Anthropic reports Claude use in specific state-surveillance workflows and nine influence operations using persistent doctrine files and attribution laundering. This establishes the mechanism in production, not its prevalence, persuasive impact or effect on state decisions.",
            "safe_ru": "Разделять существование аппарата производства и наблюдения от его воздействия. Большинство найденного контента получило мало или вовсе не получило подлинного вовлечения.",
            "safe_en": "Separate the existence of a production and surveillance apparatus from its effects. Most discovered content received little or no authentic engagement.",
            "confidence": "B/C",
        },
        "CLM_013_QUIET_ACCESS_CONTROL": {
            "support": [
                "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
                "SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE",
            ],
            "title_ru": "Контроль над возможностями ИИ часто действует через доступ и телеметрию, а не через публичный запрет",
            "title_en": "Control over AI capabilities often operates through access and telemetry rather than a public ban",
            "claim_ru": "Контроль проявляется через проверку клиентов, уровни допуска, журналы запросов, средства обнаружения и отзыв аккаунтов. Сентябрьский отчёт Anthropic показывает, что один частный узел может одновременно видеть часть потока и перекрывать доступ; спор США и КНР о дистилляции показывает, как частные условия превращаются в предмет национальной безопасности.",
            "claim_en": "Control appears through customer review, access tiers, request logs, detection and account revocation. Anthropic's September report shows one private node observing part of a flow and terminating access; the U.S.-China distillation dispute shows private access terms becoming a national-security issue.",
            "safe_ru": "Не утверждать, что провайдер видит всё или обладает государственным мандатом. Его наблюдаемость ограничена собственной платформой, а открытые веса и телеметрия на стороне заказчика меняют положение чокпойнта.",
            "safe_en": "Do not claim that a provider sees everything or holds public authority. Its visibility is bounded by its platform, while open weights and customer-side telemetry alter the chokepoint position.",
        },
    }
    for claim_id, update in updates.items():
        item = by_id[claim_id]
        if "v034_text" not in item:
            item["v034_text"] = {
                key: copy.deepcopy(item.get(key))
                for key in ["title", "claim", "safe_wording_ru", "safe_wording_en", "status", "confidence"]
            }
        item["supporting_evidence"] = uniq(item.get("supporting_evidence", []) + update["support"])
        pair(item, "title", update["title_ru"], update["title_en"], lang)
        pair(item, "claim", update["claim_ru"], update["claim_en"], lang)
        pair(item, "safe_wording", update["safe_ru"], update["safe_en"], lang)
        pair(item, "recommended_phrasing", update["safe_ru"], update["safe_en"], lang)
        pair(item, "caveats", [update["safe_ru"]], [update["safe_en"]], lang)
        if "confidence" in update:
            item["confidence"] = update["confidence"]
        item["research_updates"] = uniq(item.get("research_updates", []) + ["anthropic-threat-intel-september-2026"])


def patch_arcs(doc, raw):
    lang = doc["language"]
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    for event in raw["events"]:
        for arc_id in event["arcs"]:
            arcs[arc_id]["key_nodes"] = uniq(arcs[arc_id].get("key_nodes", []) + [event["id"]])
            arcs[arc_id]["end_date"] = max(arcs[arc_id].get("end_date", ""), event["date"])
    for arc_id in raw["claim_check"]["arc_ids"]:
        arcs[arc_id]["key_nodes"] = uniq(arcs[arc_id].get("key_nodes", []) + [NEW_CLAIM_ID])

    texts = {
        "ARC_QUIET_ACCESS_CONTROL": (
            "Контроль проявляется через проверку клиентов, уровни допуска, журналы запросов, средства обнаружения и отзыв аккаунтов. Отчёт Anthropic показывает частный узел одновременно как ограниченный паноптикум и чокпойнт: он видит часть проходящего через сервис процесса и может прекратить доступ. Это не означает полной видимости или публично-правового мандата.",
            "Control appears through customer review, access tiers, request logs, detection and account revocation. Anthropic's report shows a private node acting as a bounded observability hub and chokepoint: it sees part of the workflow crossing its service and can terminate access. This is neither complete visibility nor public-law authority.",
        ),
        "ARC_SOVEREIGN_FLOW_GATING": (
            "Государства и провайдеры оспаривают не только поставку чипов и моделей, но и допустимые способы доступа к модельным выходам. Американские ведомства квалифицируют промышленную дистилляцию как киберугрозу; КНР называет её нормальной практикой и защитой монополии. Подтверждён сам конфликт режимов, а не окончательная правовая или техническая оценка.",
            "States and providers contest not only chip and model supply but also legitimate access to model outputs. U.S. agencies frame industrial distillation as a cyber threat; China calls it ordinary practice and monopoly protection. The conflict between regimes is established, not a final legal or technical adjudication.",
        ),
        "ARC_COGSEC_LAB_TO_WILD_TO_STATE": (
            "Линия когнитивной безопасности теперь включает не только лабораторные атаки через инструкции, но и описанные провайдером процессы государственной слежки и операций влияния. Постоянные доктринальные файлы, сокрытие происхождения и массовая обработка потоков показывают рабочий механизм; распространённость и воздействие на аудиторию или решения остаются неустановленными.",
            "The cognitive-security line now includes not only laboratory instruction attacks but provider-reported state-surveillance and influence workflows. Persistent doctrine files, attribution laundering and large-scale flow processing establish an operating mechanism; prevalence and effects on audiences or decisions remain unestablished.",
        ),
        "ARC_CYBER_CLAIM_TO_CAVEAT": (
            "Новые операции добавляют свидетельства из реальной эксплуатации: адаптивную перестройку вредоносного кода, непрерывный поиск возможных уязвимостей и масштабирование кражи учётных данных. Они подтверждают ускорение в отдельных кампаниях, но не доказывают обычную частоту, валидность всех находок или полностью автономное стратегическое наступление.",
            "The new operations add production evidence of adaptive malware rebuilding, continuous research for possible vulnerabilities and scaled credential theft. They establish acceleration in selected campaigns, not ordinary prevalence, validity of every finding or fully autonomous strategic offense.",
        ),
        "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": (
            "Киберустойчивость включает не только разработку, испытания, исправление и восстановление, но и наблюдение за использованием размещённых моделей, корреляцию кампаний и отзыв доступа. Отчёт провайдера показывает эти средства в действии, однако не заменяет независимый аудит и не измеряет их полноту или ложные срабатывания.",
            "Cyber resilience includes not only development, testing, remediation and recovery but monitoring hosted-model use, correlating campaigns and revoking access. The provider report shows these controls operating, but it does not replace independent audit or measure coverage and false positives.",
        ),
    }
    for arc_id, (ru, en) in texts.items():
        arc = arcs[arc_id]
        if "v034_thesis" not in arc:
            arc["v034_thesis"] = {"ru": arc.get("thesis_ru", arc.get("thesis", "")), "en": arc.get("thesis_en", arc.get("thesis", ""))}
        pair(arc, "thesis", ru, en, lang)
        pair(
            arc,
            "safe_wording",
            "Отделять телеметрию провайдера, внешнюю корреляцию, официальные позиции и аналитическую рамку; ни один слой не заменяет остальные.",
            "Separate provider telemetry, external corroboration, official positions and analytical framing; no one layer substitutes for the others.",
            lang,
        )


def add_edges(doc, raw):
    family_by_arc = {arc["id"]: arc.get("family_id") for arc in doc["arcs"]}
    signatures = {(edge["source"], edge["target"], edge["relation"]) for edge in doc["edges"]}
    new = []

    def add(source, target, relation, ru, en, *, arc_id, target_kind, source_kind="evidence", relationship_class="editorial_relationship", strength="moderate", style="solid"):
        signature = (source, target, relation)
        if signature in signatures:
            return
        signatures.add(signature)
        new.append({
            "id": f"EDGE_V035_ANTHROPIC_{len(new) + 1:03d}",
            "source": source,
            "target": target,
            "source_kind": source_kind,
            "target_kind": target_kind,
            "relation": relation,
            "arc_id": arc_id,
            "arc_family_id": family_by_arc.get(arc_id),
            "strength": strength,
            "evidence_level": "B",
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
                "Тематическая принадлежность; связь не доказывает всю сюжетную дугу.",
                "Thematic membership; the link does not prove the whole story arc.",
                arc_id=arc_id, target_kind="story_arc", relationship_class="thematic", style="dashed",
            )

    existing_support = {
        "CLM_006_MACHINE_SPEED_CYBER": [
            "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
            "SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY",
            "SIG_2026_ANTHROPIC_GTG50014_CREDENTIAL_SUPPLY_CHAIN",
        ],
        "CLM_007_COGNITIVE_SECURITY": [
            "SIG_2026_ANTHROPIC_STATE_SURVEILLANCE_BUREAUCRACY",
            "SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING",
        ],
        "CLM_013_QUIET_ACCESS_CONTROL": [
            "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
            "SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE",
        ],
    }
    claim_arc = {
        "CLM_006_MACHINE_SPEED_CYBER": "ARC_CYBER_CLAIM_TO_CAVEAT",
        "CLM_007_COGNITIVE_SECURITY": "ARC_COGSEC_LAB_TO_WILD_TO_STATE",
        "CLM_013_QUIET_ACCESS_CONTROL": "ARC_QUIET_ACCESS_CONTROL",
    }
    for claim_id, event_ids in existing_support.items():
        for event_id in event_ids:
            add(
                event_id, claim_id, "supports_with_scope",
                "Поддерживает уточнённое утверждение только в границах телеметрии и оговорок источника.",
                "Supports the updated claim only within the source's telemetry and stated caveats.",
                arc_id=claim_arc[claim_id], target_kind="claim_check", relationship_class="evidential",
            )

    claim = raw["claim_check"]
    for event_id in claim["supporting_evidence"]:
        add(
            event_id, NEW_CLAIM_ID, "supports_with_scope",
            "Показывает сочетание частичной наблюдаемости потока и технического контроля доступа в конкретном контексте.",
            "Shows partial flow observability combined with technical access control in a specific context.",
            arc_id="ARC_QUIET_ACCESS_CONTROL", target_kind="claim_check", relationship_class="evidential",
        )
    for event_id in claim["qualifying_evidence"]:
        add(
            event_id, NEW_CLAIM_ID, "qualifies",
            "Показывает архитектуру, в которой видимость провайдера ограничена и часть телеметрии остаётся у заказчика.",
            "Shows an architecture in which provider visibility is bounded and some telemetry remains customer-side.",
            arc_id="ARC_QUIET_ACCESS_CONTROL", target_kind="claim_check", relationship_class="evidential_qualification", style="dashed",
        )
    for arc_id in claim["arc_ids"]:
        add(
            NEW_CLAIM_ID, arc_id, "supports_arc",
            "Проверяемое утверждение связывает наблюдаемость и отзыв доступа с этой дугой без заявления о полной видимости.",
            "The scoped claim connects observability and access revocation to this arc without asserting complete visibility.",
            arc_id=arc_id, target_kind="story_arc", source_kind="claim_check",
        )
    for thesis_id in ["THESIS_ACCESS_AS_POWER", "THESIS_CORE"]:
        add(
            NEW_CLAIM_ID, thesis_id, "supports_with_scope",
            "Совмещённые наблюдаемость и отзыв доступа поддерживают тезис о структурной власти при явных ограничениях охвата.",
            "Co-located observability and access revocation support the structural-power thesis within explicit scope limits.",
            arc_id="ARC_QUIET_ACCESS_CONTROL", target_kind="thesis", source_kind="claim_check", relationship_class="evidential",
        )

    add(
        "SIG_2026_ANTHROPIC_AI_MISUSE_ATTACK_MAP",
        "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
        "updated_by",
        "Сентябрьский отчёт расширяет июньскую карту новыми операциями и более явным описанием наблюдения и отключения.",
        "The September report extends the June map with new operations and a clearer account of observation and disruption.",
        arc_id="ARC_QUIET_ACCESS_CONTROL", target_kind="evidence", relationship_class="editorial_relationship", style="dashed",
    )
    add(
        "SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE",
        "SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE",
        "updated_by",
        "Февральское раскрытие перешло в сентябре в межгосударственный спор о доступе, согласии и национальной безопасности.",
        "The February disclosure developed into a September interstate dispute over access, consent and national security.",
        arc_id="ARC_SOVEREIGN_FLOW_GATING", target_kind="evidence", relationship_class="editorial_relationship", style="dashed",
    )

    doc["edges"].extend(new)
    attach_edge_links(doc, {edge["id"] for edge in new})
    return [edge["id"] for edge in new]


def update_metadata(doc, raw, added_edge_ids):
    lang = doc["language"]
    event_ids = [event["id"] for event in raw["events"]]
    doc["meta"].update(
        version=VERSION,
        updated_at=DATE,
        schema_version="ai_stack_structural_power.v0.35.0-2026-09-11",
    )
    entry = {
        "version": VERSION,
        "date": DATE,
        "description": "Anthropic September threat intelligence mapped into cyber capability, cognitive security, provider observability/access control and the U.S.-China distillation dispute.",
        "added_evidence": len(event_ids),
        "added_claims": 0,
        "added_claim_checks": 1,
        "added_story_arcs": 0,
        "added_story_edges": len(added_edge_ids),
        "updated_existing_evidence": ["SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE"],
        "updated_claim_checks": ["CLM_006_MACHINE_SPEED_CYBER", "CLM_007_COGNITIVE_SECURITY", "CLM_013_QUIET_ACCESS_CONTROL"],
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
        "ru": "ПАНОПТИКУМ И ЧОКПОЙНТ (v0.35): отчёт Anthropic показывает облачную инфраструктуру как узел частичной наблюдаемости и отзыва доступа. Это расширяет рамку за пределы киберинцидентов: контроль потока, государственная слежка, операции влияния и спор США и КНР о дистилляции сходятся в одном инфраструктурном механизме.",
        "en": "OBSERVABILITY AND ACCESS GATING (v0.35): Anthropic's report shows hosted infrastructure as a node of partial observability and access revocation. This extends beyond cyber incidents: flow control, state surveillance, influence operations and the U.S.-China distillation dispute converge on one infrastructure mechanism.",
    }
    summary["key_findings"] = [finding[lang]] + summary.get("key_findings", [])

    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["corrections"] = [finding[lang]] + doc["presentation"].get("corrections", [])
    doc["presentation"]["release_notes"] = [
        {
            "title": "Паноптикум и чокпойнт" if lang == "ru" else "Observability and access gating",
            "text": finding[lang],
        },
        {
            "title": "Разделение доказательств" if lang == "ru" else "Evidence separation",
            "text": (
                "Телеметрия Anthropic, независимая корреляция Microsoft, официальные позиции США и КНР и аналитическая рамка Habr помечены раздельно."
                if lang == "ru"
                else "Anthropic telemetry, Microsoft corroboration, U.S. and Chinese official positions, and the Habr analytical frame remain separately labelled."
            ),
        },
    ]
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update({
        "version": VERSION,
        "v035_base_commit": raw["meta"]["base_commit"],
        "v035_base_sha256": raw["meta"]["base_sha256"][lang],
        "v035_added_event_ids": event_ids,
        "v035_added_claim_check_ids": [NEW_CLAIM_ID],
        "v035_added_edge_ids": added_edge_ids,
        "v035_updated_event_ids": ["SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE"],
        "v035_updated_claim_check_ids": ["CLM_006_MACHINE_SPEED_CYBER", "CLM_007_COGNITIVE_SECURITY", "CLM_013_QUIET_ACCESS_CONTROL"],
        "v035_source_package": "review/anthropic-threat-intel-september-2026",
    })
    doc["factcheckAudit"]["v035_scope"] = {
        "date": DATE,
        "accepted_records": len(event_ids),
        "source_records": len(raw["sources"]),
        "deferred_records": len(raw["deferred"]),
        "full_report_sample_representative": False,
        "provider_telemetry_independently_replicated": False,
        "note": "Seven atomic records retained. The report's selected-case caveat, human goal-setting, possible-versus-validated vulnerability distinction, and separate U.S./China official positions are preserved.",
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]),
        "story_edges": len(doc["edges"]),
        "last_recomputed": DATE,
        "v0_35_added_evidence": len(event_ids),
        "v0_35_added_claim_checks": 1,
        "v0_35_added_edges": len(added_edge_ids),
        "v0_35_updated_arcs": sorted({arc_id for event in raw["events"] for arc_id in event["arcs"]}),
    })


def migrate(doc, raw):
    if doc["meta"]["version"] != "0.34":
        raise ValueError("Expected v0.34 input")
    original_dates = {event["id"]: event["date"] for event in doc["events"]}
    original_urls = {source["url"] for source in doc["sourceIndex"]}
    sources = {source["id"]: source for source in raw["sources"]}
    event_ids = [event["id"] for event in raw["events"]]
    all_ids = {node["id"] for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"] for node in doc.get(collection, [])}
    if len(event_ids) != 7 or len(set(event_ids)) != 7 or set(event_ids) & all_ids or NEW_CLAIM_ID in all_ids:
        raise ValueError("Candidate count or ID collision")

    patch_distillation(doc, raw, sources)
    doc["events"].extend(event_record(event, doc["language"], sources, doc) for event in raw["events"])
    doc["claimChecks"].append(claim_check_record(raw["claim_check"], doc["language"], sources, doc))
    patch_claim_checks(doc)
    patch_arcs(doc, raw)
    added_edge_ids = add_edges(doc, raw)
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, raw, added_edge_ids)
    doc["referenceIntegrity"] = references(doc)
    if not doc["referenceIntegrity"]["valid"]:
        raise ValueError(doc["referenceIntegrity"])
    if not all(next(item for item in doc["events"] if item["id"] == event_id)["date"] == date for event_id, date in original_dates.items()):
        raise ValueError("A pre-v0.35 event date changed")
    if not original_urls <= {source["url"] for source in doc["sourceIndex"]}:
        raise ValueError("A pre-v0.35 source URL was lost")
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="directory containing the exact v0.34 bilingual JSON pair")
    parser.add_argument("--output", type=Path, required=True, help="destination directory for the migrated JSON pair")
    args = parser.parse_args()
    raw = json.loads((PACKAGE / "candidates.json").read_text())
    loaded = {}
    for lang in ["ru", "en"]:
        path = args.root / f"ai_power_storygraph_{lang}.json"
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != raw["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{path.name}: expected pinned v0.34 SHA-256; refusing input {digest}")
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
        print(lang, len(doc["events"]), "events", len(doc["claimChecks"]), "claim checks", len(doc["edges"]), "edges", len(doc["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()
