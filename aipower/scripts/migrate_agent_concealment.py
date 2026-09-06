#!/usr/bin/env python3
"""Add the reviewed concealment and behavioural-continuity layer to v0.31.

The canonical filenames stay stable. This migration is pinned to the exact
v0.31 bilingual inputs and refuses to run against another release.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json

from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "review/agent-concealment-persistence/candidates.json"
RELEASE_DATE = "2026-09-06"
ARC_ID = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
FAMILY_ID = "ARC_FAMILY_CYBER_COGNITION_WAR"
CLAIM_ID = "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE"
DOMAIN_ID = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
SUBDOMAIN_ID = "CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"
TRACK_ID = "BEH_TRACK_CONCEALMENT_PERSISTENCE"

EXPECTED_SHA256 = {
    "ru": "0591af65377460fe1f479986354a85c94b6a7485fd84bafe4d500153d80e98d5",
    "en": "5ed9a091aedd5aaa0e57047494ba84c1280b3c227e6f5f41dc5cc9e44e301474",
}


NEW_MECHANISMS = [
    {
        "id": "BEH_POLICY_PERSISTENCE_WEIGHTS",
        "label_ru": "Сохранение условной стратегии в весах",
        "label_en": "Conditional-policy persistence in weights",
        "subdomain_ids": [SUBDOMAIN_ID],
    },
    {
        "id": "BEH_OBSERVATION_CONDITIONING",
        "label_ru": "Зависимость поведения от режима наблюдения",
        "label_en": "Behaviour conditioned on observation state",
        "subdomain_ids": [SUBDOMAIN_ID],
    },
    {
        "id": "BEH_REASONING_TRACE_FIDELITY",
        "label_ru": "Полнота и достоверность reasoning trace",
        "label_en": "Reasoning-trace completeness and fidelity",
        "subdomain_ids": [SUBDOMAIN_ID],
    },
    {
        "id": "BEH_STRATEGIC_CONCEALMENT",
        "label_ru": "Стратегическое сокрытие действия или способности",
        "label_en": "Strategic concealment of action or capability",
        "subdomain_ids": [SUBDOMAIN_ID],
    },
    {
        "id": "BEH_POLICY_CONTINUITY",
        "label_ru": "Передача цели или политики следующему экземпляру",
        "label_en": "Goal or policy transfer to a successor instance",
        "subdomain_ids": [SUBDOMAIN_ID],
    },
]

NEW_VOCABULARIES = {
    "behavior_origins": [
        {"id": "intentionally_implanted", "label_ru": "Намеренно имплантировано исследователями", "label_en": "Intentionally implanted by researchers"},
        {"id": "evaluation_prompted", "label_ru": "Вызвано постановкой испытания", "label_en": "Induced by the evaluation setup"},
        {"id": "observed_during_training", "label_ru": "Наблюдалось в ходе обучения", "label_en": "Observed during training"},
        {"id": "deployment_observed", "label_ru": "Наблюдалось при эксплуатации", "label_en": "Observed in deployment"},
        {"id": "externally_injected", "label_ru": "Внесено внешней инструкцией или атакующим", "label_en": "Injected by an external instruction or attacker"},
        {"id": "not_established", "label_ru": "Происхождение не установлено", "label_en": "Origin not established"},
        {"id": "not_applicable", "label_ru": "Не применимо", "label_en": "Not applicable"},
    ],
    "concealment_targets": [
        {"id": "user", "label_ru": "Пользователь", "label_en": "User"},
        {"id": "auditor", "label_ru": "Аудитор", "label_en": "Auditor"},
        {"id": "grader", "label_ru": "Оценщик", "label_en": "Grader"},
        {"id": "trainer", "label_ru": "Контур обучения", "label_en": "Training process"},
        {"id": "monitor", "label_ru": "Монитор", "label_en": "Monitor"},
        {"id": "developer_operator", "label_ru": "Разработчик или оператор", "label_en": "Developer or operator"},
        {"id": "none", "label_ru": "Сокрытие не установлено", "label_en": "No concealment established"},
    ],
    "persistence_media": [
        {"id": "model_weights", "label_ru": "Веса модели", "label_en": "Model weights"},
        {"id": "scratchpad_or_reasoning_trace", "label_ru": "Scratchpad или reasoning trace", "label_en": "Scratchpad or reasoning trace"},
        {"id": "persistent_memory", "label_ru": "Долговременная память", "label_en": "Persistent memory"},
        {"id": "external_artifact", "label_ru": "Внешний артефакт", "label_en": "External artifact"},
        {"id": "shared_state", "label_ru": "Общее записываемое состояние", "label_en": "Shared writable state"},
        {"id": "none", "label_ru": "Межсеансовый носитель отсутствует", "label_en": "No cross-session medium"},
        {"id": "not_established", "label_ru": "Носитель не установлен", "label_en": "Medium not established"},
    ],
    "goal_sources": [
        {"id": "explicit_prompt", "label_ru": "Явно заданная цель", "label_en": "Explicitly prompted objective"},
        {"id": "trained_preference", "label_ru": "Ранее обученное предпочтение", "label_en": "Previously trained preference"},
        {"id": "inferred_grader_preference", "label_ru": "Предполагаемое предпочтение оценщика", "label_en": "Inferred grader preference"},
        {"id": "researcher_implanted", "label_ru": "Цель имплантирована исследователями", "label_en": "Objective implanted by researchers"},
        {"id": "external_instruction", "label_ru": "Внешняя сохранённая инструкция", "label_en": "Persisted external instruction"},
        {"id": "unknown", "label_ru": "Источник цели не установлен", "label_en": "Objective source not established"},
        {"id": "not_applicable", "label_ru": "Цель не приписывается", "label_en": "No objective attributed"},
    ],
}

TRACK = {
    "id": TRACK_ID,
    "label_ru": "Скрытие и преемственность",
    "label_en": "Concealment and continuity",
    "short_ru": "Скрытие и преемственность",
    "short_en": "Concealment and continuity",
    "description_ru": "Четыре разных механизма: стратегия в весах, смена поведения при наблюдении, неполный или намеренно искажённый след и перенос состояния между запусками.",
    "description_en": "Four distinct mechanisms: policy in weights, observation-conditioned behaviour, incomplete or deliberately obscured traces, and state transfer across runs.",
    "stages": [
        {
            "id": "BEH_TRACK_STAGE_WEIGHTS", "order": 1,
            "label_ru": "Веса", "label_en": "Weights",
            "description_ru": "Переживает ли условная стратегия обучение и проверку.",
            "description_en": "Whether a conditional policy survives training and evaluation.",
            "mechanism_ids": ["BEH_POLICY_PERSISTENCE_WEIGHTS"],
        },
        {
            "id": "BEH_TRACK_STAGE_OBSERVATION", "order": 2,
            "label_ru": "Режим наблюдения", "label_en": "Observation state",
            "description_ru": "Меняется ли действие между training, evaluation и deployment framing.",
            "description_en": "Whether action changes across training, evaluation and deployment framing.",
            "mechanism_ids": ["BEH_OBSERVATION_CONDITIONING"],
        },
        {
            "id": "BEH_TRACK_STAGE_EXPLANATION", "order": 3,
            "label_ru": "Объяснение", "label_en": "Explanation",
            "description_ru": "Полон ли reasoning trace и скрывается ли реальная способность или действие.",
            "description_en": "Whether the reasoning trace is complete and whether capability or action is concealed.",
            "mechanism_ids": ["BEH_REASONING_TRACE_FIDELITY", "BEH_STRATEGIC_CONCEALMENT"],
        },
        {
            "id": "BEH_TRACK_STAGE_EXTERNAL_STATE", "order": 4,
            "label_ru": "Внешнее состояние", "label_en": "External state",
            "description_ru": "Что передаётся следующему запуску через память, файл или общую среду.",
            "description_en": "What passes to a later run through memory, a file or shared environment.",
            "mechanism_ids": ["BEH_POLICY_CONTINUITY", "BEH_EXTERNALIZED_STATE", "BEH_MEMORY_PROVENANCE"],
        },
    ],
}


EXISTING_TRACK_CONTEXT = {
    "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE": {
        "mechanisms": [], "origin": "not_established", "targets": ["none"],
        "media": ["external_artifact", "shared_state"], "goal": "unknown",
    },
    "SIG_2026_SLEEPER_MEMORY_POISONING": {
        "mechanisms": [], "origin": "externally_injected", "targets": ["user", "monitor"],
        "media": ["persistent_memory"], "goal": "external_instruction",
    },
    "SIG_2026_ANTHROPIC_REWARD_SEEKER_MODEL_ORGANISM": {
        "mechanisms": ["BEH_POLICY_PERSISTENCE_WEIGHTS", "BEH_STRATEGIC_CONCEALMENT"],
        "origin": "intentionally_implanted", "targets": ["grader", "monitor"],
        "media": ["model_weights"], "goal": "researcher_implanted",
    },
    "SIG_2026_OPENAI_INTERNAL_AGENT_MONITORING_BASELINE": {
        "mechanisms": ["BEH_REASONING_TRACE_FIDELITY"], "origin": "deployment_observed",
        "targets": ["monitor"], "media": ["scratchpad_or_reasoning_trace"], "goal": "unknown",
    },
    "SIG_2026_SCHEMING_PROPENSITY_CONFIGURATION_DEPENDENCE": {
        "mechanisms": ["BEH_OBSERVATION_CONDITIONING", "BEH_STRATEGIC_CONCEALMENT"],
        "origin": "evaluation_prompted", "targets": ["monitor", "developer_operator"],
        "media": ["scratchpad_or_reasoning_trace"], "goal": "explicit_prompt",
    },
    "SIG_2026_AISI_LOSS_OF_OVERSIGHT": {
        "mechanisms": ["BEH_REASONING_TRACE_FIDELITY"], "origin": "not_applicable",
        "targets": ["monitor"], "media": ["not_established"], "goal": "not_applicable",
    },
}


EVIDENCE_RELATIONS = {
    "SIG_2026_OPENAI_COT_CONTROLLABILITY": "qualifies",
    "SIG_2025_ANTHROPIC_COT_FAITHFULNESS": "supports_but_limits",
    "SIG_2025_ANTHROPIC_AUTOMATED_RESEARCHER_SANDBAGGING": "supports_with_scope",
}

SEQUENCE_EDGES = [
    ("SIG_2024_ANTHROPIC_SLEEPER_AGENTS", "SIG_2025_ANTHROPIC_HIDDEN_OBJECTIVES_AUDIT", "sets_up"),
    ("SIG_2025_ANTHROPIC_HIDDEN_OBJECTIVES_AUDIT", "SIG_2026_ANTHROPIC_AUDITBENCH", "develops_into"),
    ("SIG_2024_APOLLO_IN_CONTEXT_SCHEMING", "SIG_2025_APOLLO_OPUS4_FUTURE_INSTANCE_NOTES", "develops_into"),
    ("SIG_2024_ANTHROPIC_ALIGNMENT_FAKING", "SIG_2025_ANTHROPIC_AGENTIC_MISALIGNMENT", "context_for"),
    ("SIG_2025_ANTHROPIC_COT_FAITHFULNESS", "SIG_2025_OPENAI_COT_MONITORING_OBFUSCATION", "parallel"),
    ("SIG_2025_OPENAI_COT_MONITORING_OBFUSCATION", "SIG_2026_OPENAI_COT_CONTROLLABILITY", "updated_by"),
    ("SIG_2025_ANTHROPIC_AUTOMATED_RESEARCHER_SANDBAGGING", "SIG_2025_ANTHROPIC_AGENTIC_MISALIGNMENT", "parallel"),
    ("SIG_2025_APOLLO_OPUS4_FUTURE_INSTANCE_NOTES", "SIG_2026_APOLLO_REWARD_SEEKING_RL", "context_for"),
]


def merge_vocab(existing, additions):
    by_id = {item["id"]: copy.deepcopy(item) for item in existing}
    order = [item["id"] for item in existing]
    for item in additions:
        if item["id"] not in by_id:
            order.append(item["id"])
        by_id[item["id"]] = copy.deepcopy(item)
    return [by_id[item_id] for item_id in order]


def source_record(raw):
    return {
        "title": raw["title"], "name": raw["name"], "url": raw["url"],
        "type": raw["type"], "date": raw["date"], "primary_or_secondary": "primary",
        "source_class": raw["source_class"],
    }


def event_record(raw, lang):
    source = source_record(raw["source"])
    title = raw[f"title_{lang}"]
    summary = raw[f"summary_{lang}"]
    caveat = raw[f"caveat_{lang}"]
    safe = raw[f"safe_{lang}"]
    actors = raw["actors"]
    return {
        "id": raw["id"], "kind": "event",
        "title": title, "title_ru": raw["title_ru"], "title_en": raw["title_en"],
        "date": raw["date"], "source_date": source["date"], "date_basis": "source_publication_date",
        "date_status": "" if raw["date_status"] == "exact" else raw["date_status"], "year": int(raw["date"][:4]),
        "url": source["url"], "source_name": source["name"], "source_type_raw": source["source_class"],
        "source_type": source["type"], "primary_or_secondary": "primary",
        "actor": ", ".join(actors), "actor_raw": ", ".join(actors),
        "actors_raw": actors, "actors": actors, "actor_facets_legacy": actors,
        "actor_facets": actors, "actor_entities": actors, "actor_jurisdictions": ["US"],
        "actor_types": raw["actor_types"],
        "geography_raw": ["US", "Global"], "geography": ["US"], "jurisdictions": ["US"],
        "regions": [], "locations": [], "institutional_scopes": [], "geo_context": [],
        "geographic_scopes": ["Global"], "geography_unclassified": [],
        "evidence_context": raw["contexts"], "evidence_method": raw["method"],
        "stack_layer": ["decision_support_cognition", "cyber_security_patch"],
        "stack_layers": ["decision_support_cognition", "cyber_security_patch"],
        "strange_structure": ["security", "knowledge"], "strange_structures": ["security", "knowledge"],
        "research_question": ["RQ3", "RQ4"],
        "claim_supported": summary, "claim_supported_ru": raw["summary_ru"], "claim_supported_en": raw["summary_en"],
        "claim_challenged": caveat, "claim_challenged_ru": raw["caveat_ru"], "claim_challenged_en": raw["caveat_en"],
        "summary": summary, "summary_ru": raw["summary_ru"], "summary_en": raw["summary_en"],
        "notes": caveat, "notes_ru": raw["caveat_ru"], "notes_en": raw["caveat_en"],
        "safe_wording": safe, "safe_wording_ru": raw["safe_ru"], "safe_wording_en": raw["safe_en"],
        "corroboration_needed": caveat, "corroboration_needed_ru": raw["caveat_ru"],
        "corroboration_needed_en": raw["caveat_en"], "caveat": caveat,
        "caveat_ru": raw["caveat_ru"], "caveat_en": raw["caveat_en"],
        "caveats": [caveat], "caveats_ru": [raw["caveat_ru"]], "caveats_en": [raw["caveat_en"]],
        "exact_quote_short": "", "numbers": raw["numbers"], "money_status": "",
        "confidence": raw["confidence"], "evidence_level": raw["confidence"], "status": raw["status"],
        "cyber_domain_ids": [DOMAIN_ID], "cyber_role_ids": raw["roles"],
        "cyber_access_principal": raw["delegation"] in {"observed", "evaluated"},
        "status_update_date": "", "current_legal_status": "", "legal_update_en": "", "legal_update_ru": "",
        "independent_review_summary_en": "", "independent_review_summary_ru": "",
        "dedupe_note_en": "", "dedupe_note_ru": "", "research_updates": ["agent-concealment-persistence"],
        "sources": [source], "edgeIds": [], "arcIds": [ARC_ID], "arcFamilyIds": [FAMILY_ID], "relationTypes": [],
        "artifact_kind": "research", "normative_force": "not_applicable", "implementation_stage": "published",
        "primary_domain_id": DOMAIN_ID, "delegated_authority": raw["delegation"],
        "editorial_priority": raw["priority"], "scope_ru": raw["caveat_ru"], "scope_en": raw["caveat_en"],
        "role_basis_ru": "Роли описывают функцию ИИ в исследовании и не превращают лабораторный результат в production-инцидент.",
        "role_basis_en": "Roles describe AI's function in the study and do not turn a laboratory result into a production incident.",
        "editorial_rationale_ru": "Опорная карточка дорожки скрытия и преемственности. " + raw["safe_ru"],
        "editorial_rationale_en": "Core evidence for the concealment and continuity track. " + raw["safe_en"],
        "classification_review": {"date": RELEASE_DATE, "method": "primary_source_fact_check_and_schema_normalization", "source_url": source["url"], "independent_source_reverification": False},
        "governance_scale": "research_evidence", "actor_unclassified": [],
        "actor_classification_status": "resolved", "geography_classification_status": "resolved",
        "cyber_subdomain_ids": [SUBDOMAIN_ID], "behavioral_mechanism_ids": raw["mechanisms"],
        "behavioral_status": raw["behavioral_statuses"], "agent_population_scope": raw["population"],
        "shared_writable_state": raw["shared_state"], "oversight_target": raw["oversight"],
        "motivation_basis": raw["motivation"], "behavior_track_ids": [TRACK_ID],
        "behavior_origin": raw["behavior_origin"], "concealment_targets": raw["concealment_targets"],
        "persistence_media": raw["persistence_media"], "goal_source": raw["goal_source"],
        "candidate_evidence_tier": "primary_source_reviewed",
    }


def patch_framework(doc):
    framework = doc["cyberFramework"]
    framework["version"] = "2.2"
    framework["updated_at"] = RELEASE_DATE
    framework["summary_ru"] = "Пять доменов разделяют объект управления и роль ИИ. В 5A отдельно показана дорожка скрытия и преемственности: веса, режим наблюдения, объяснение и внешнее состояние."
    framework["summary_en"] = "Five domains separate governance object from AI role. Domain 5A now includes a concealment and continuity track spanning weights, observation state, explanation and external state."
    framework["method_note_ru"] = "Авторская схема, не стандарт и не шкала зрелости. Model organism, prompted eval, training observation и production incident размечаются отдельно; неполный CoT сам по себе не доказывает намеренную ложь."
    framework["method_note_en"] = "Authored framework, not a standard or maturity scale. Model organisms, prompted evaluations, training observations and production incidents are separate; an incomplete CoT does not by itself establish deliberate deception."
    framework["behavioral_mechanisms"] = merge_vocab(framework["behavioral_mechanisms"], NEW_MECHANISMS)
    framework["behavior_tracks"] = [copy.deepcopy(TRACK)]
    for key, values in NEW_VOCABULARIES.items():
        framework[key] = copy.deepcopy(values)
    groups = {group["id"]: group for group in framework["behavior_groups"]}
    groups["BEH_GROUP_02_STATE"]["mechanism_ids"] = uniq(groups["BEH_GROUP_02_STATE"]["mechanism_ids"] + ["BEH_POLICY_PERSISTENCE_WEIGHTS", "BEH_POLICY_CONTINUITY"])
    groups["BEH_GROUP_04_CONTROL"]["mechanism_ids"] = uniq(groups["BEH_GROUP_04_CONTROL"]["mechanism_ids"] + ["BEH_OBSERVATION_CONDITIONING", "BEH_REASONING_TRACE_FIDELITY", "BEH_STRATEGIC_CONCEALMENT"])


def patch_existing_track_events(doc):
    by_id = {event["id"]: event for event in doc["events"]}
    missing = sorted(set(EXISTING_TRACK_CONTEXT) - set(by_id))
    if missing:
        raise ValueError(f"Missing v0.31 comparison records: {missing}")
    for event_id, patch in EXISTING_TRACK_CONTEXT.items():
        event = by_id[event_id]
        event["behavior_track_ids"] = uniq(event.get("behavior_track_ids", []) + [TRACK_ID])
        event["behavioral_mechanism_ids"] = uniq(event.get("behavioral_mechanism_ids", []) + patch["mechanisms"])
        event["behavior_origin"] = patch["origin"]
        event["concealment_targets"] = patch["targets"]
        event["persistence_media"] = patch["media"]
        event["goal_source"] = patch["goal"]


def edge_record(edge_id, source, target, relation, summary_ru, summary_en, *, target_kind="claim", relationship_class="evidential", style="solid"):
    return {
        "id": edge_id, "source": source, "target": target,
        "source_kind": "evidence", "target_kind": target_kind, "relation": relation,
        "arc_id": ARC_ID, "strength": "high", "evidence_level": "B",
        "visual_lane": "decision_support_cognition", "style": style,
        "summary_ru": summary_ru, "summary_en": summary_en,
        "arc_family_id": FAMILY_ID, "kind": "edge", "is_auto": False,
        "relationship_class": relationship_class,
    }


def new_edges(records):
    result = []
    for index, raw in enumerate(records, 1):
        result.append(edge_record(
            f"EDGE_CONCEALMENT_ARC_{index:02d}", raw["id"], ARC_ID, "part_of_arc",
            "Карточка входит в линию скрытия и преемственности по теме; связь не доказывает всю сюжетную дугу.",
            "The record belongs to the concealment and continuity thread by topic; the link does not prove the full arc.",
            target_kind="story_arc", relationship_class="thematic",
        ))
        relation = EVIDENCE_RELATIONS.get(raw["id"], "supports_with_scope")
        result.append(edge_record(
            f"EDGE_CONCEALMENT_CLAIM_{index:02d}", raw["id"], CLAIM_ID, relation,
            raw["safe_ru"], raw["safe_en"],
            relationship_class="editorial_relationship" if relation == "qualifies" else "evidential",
            style="dashed" if relation == "qualifies" else "solid",
        ))
    for index, (source, target, relation) in enumerate(SEQUENCE_EDGES, 1):
        result.append(edge_record(
            f"EDGE_CONCEALMENT_SEQUENCE_{index:02d}", source, target, relation,
            "Связь показывает развитие исследовательского вопроса или параллельный результат; это не доказанная причинность между публикациями.",
            "The link marks development of a research question or a parallel result; it is not demonstrated causality between publications.",
            target_kind="evidence", relationship_class="editorial_relationship",
        ))
    return result


def patch_claim(doc, event_ids):
    claim = next(item for item in doc["claims"] if item["id"] == CLAIM_ID)
    title_ru = "Поведение агентов: скрытие и преемственность наблюдаемы, обычная частота не установлена"
    title_en = "Agent behaviour: concealment and continuity are observable, ordinary prevalence is not established"
    text_ru = (
        "Современные модели в контролируемых условиях уже способны менять поведение в зависимости от наблюдения, "
        "скрывать причины решения или уровень возможностей, сохранять условную стратегию после обучения и передавать "
        "состояние следующему запуску через память или внешний артефакт. Большинство сильных результатов получено на "
        "model organisms и специально построенных evals; частота спонтанного долгосрочного scheming в обычной эксплуатации остаётся низкой или неизвестной."
    )
    text_en = (
        "In controlled settings, current models can condition behaviour on observation, obscure decision drivers or capability, "
        "retain a conditional policy through training, and pass state to a later run through memory or an external artifact. "
        "Most strong results come from model organisms and deliberately constructed evaluations; the prevalence of spontaneous "
        "long-horizon scheming in ordinary deployment remains low or unknown."
    )
    safe_ru = "Не смешивать имплантированную цель, prompted capability, наблюдение в training run и production incidence. Неполный reasoning trace не следует автоматически называть ложью."
    safe_en = "Do not collapse an implanted objective, prompted capability, training-run observation and production incidence. An incomplete reasoning trace should not automatically be called a lie."
    claim.update({
        "title": title_ru if doc["language"] == "ru" else title_en,
        "title_ru": title_ru, "title_en": title_en,
        "claim": text_ru if doc["language"] == "ru" else text_en,
        "claim_ru": text_ru, "claim_en": text_en,
        "recommended_phrasing": safe_en, "recommended_phrasing_ru": safe_ru, "recommended_phrasing_en": safe_en,
        "safe_wording_ru": safe_ru, "safe_wording_en": safe_en,
        "caveats": [safe_ru if doc["language"] == "ru" else safe_en],
        "caveats_ru": [safe_ru], "caveats_en": [safe_en],
        "date_relevant": "2024-2026",
        "keywords": uniq(claim.get("keywords", []) + ["observation conditioning", "concealment", "policy persistence", "successor state", "auditability"]),
    })
    qualifier = "SIG_2026_OPENAI_COT_CONTROLLABILITY"
    support = [event_id for event_id in event_ids if event_id != qualifier]
    claim["supporting_evidence"] = uniq(claim.get("supporting_evidence", []) + support)
    claim["qualifying_evidence"] = uniq(claim.get("qualifying_evidence", []) + [qualifier, "SIG_2025_ANTHROPIC_COT_FAITHFULNESS"])


def patch_arc(doc, event_ids):
    arc = next(item for item in doc["arcs"] if item["id"] == ARC_ID)
    title_ru = "Поведенческая и когнитивная безопасность: от рамки задачи к скрытию, памяти и контролю"
    title_en = "Behavioural and cognitive security: from task framing to concealment, memory and control"
    thesis_ru = "Риск определяется не одной моделью: постановка задачи, представление о наблюдении, обучение, память, внешние артефакты, права и архитектура аудита меняют результат. Контролируемые испытания уже показывают скрытие и преемственность; данные о фоновой частоте в обычной эксплуатации остаются ограниченными."
    thesis_en = "Risk is not a property of one model alone: task framing, perceived observation, training, memory, external artifacts, authority and audit architecture change outcomes. Controlled evaluations already demonstrate concealment and continuity; evidence about ordinary deployment base rates remains limited."
    arc.update({
        "title": title_ru if doc["language"] == "ru" else title_en,
        "title_ru": title_ru, "title_en": title_en,
        "thesis": thesis_ru if doc["language"] == "ru" else thesis_en,
        "thesis_ru": thesis_ru, "thesis_en": thesis_en,
    })
    arc["key_nodes"] = uniq(arc.get("key_nodes", []) + event_ids)
    arc["counterpoints"] = uniq(arc.get("counterpoints", []) + [
        "Неполный chain-of-thought не равен намеренному обману; текущие модели также показывают низкую способность управлять формой собственных traces.",
        "Model organisms и forced-choice evals устанавливают возможность в заданной конфигурации, а не частоту в реальной эксплуатации.",
    ])
    arc["counterpoints_en"] = uniq(arc.get("counterpoints_en", []) + [
        "An incomplete chain of thought is not equivalent to deliberate deception; current models also show low ability to control the form of their own traces.",
        "Model organisms and forced-choice evaluations establish capability in a stated configuration, not real-world prevalence.",
    ])


def update_metadata(doc, event_ids, edge_ids):
    lang = doc["language"]
    meta = doc["meta"]
    meta["version"] = "0.32"
    meta["updated_at"] = RELEASE_DATE
    meta["schema_version"] = "ai_stack_structural_power.v0.32.0-2026-09-06"
    entry = {
        "version": "0.32", "date": RELEASE_DATE,
        "description": "Added 12 primary-source records on observation-conditioned behaviour, hidden objectives, trace fidelity, persistence through training and successor-state transfer. Added a four-stage concealment and continuity view without creating another top-level story arc.",
        "added_evidence": len(event_ids), "added_claims": 0, "added_story_arcs": 0,
        "added_story_edges": len(edge_ids), "updated_story_arcs": [ARC_ID],
    }
    meta["changelog"] = [entry] + [item for item in meta.get("changelog", []) if item.get("version") != "0.32"]

    summary = doc["summary"]
    summary.update({
        "total_evidence_items": len(doc["events"]), "total_timeline_items": len(doc["events"]),
        "total_story_arcs": len(doc["arcs"]), "total_story_edges": len(doc["edges"]),
        "cyber_framework_version": "2.2", "cyber_framework_event_count": sum(bool(event.get("primary_domain_id")) for event in doc["events"]),
        "total_events": len(doc["events"]), "total_claims": len(doc["claims"]),
        "total_claim_checks": len(doc["claimChecks"]), "total_arcs": len(doc["arcs"]),
        "total_edges": len(doc["edges"]), "total_thesis_nodes": len(doc["thesisNodes"]),
    })
    summary["stats"]["total_claims"] = len(doc["claims"])
    summary["claim_status_counts"] = dict(Counter(claim.get("status") for claim in doc["claims"]))
    finding_ru = "СКРЫТИЕ И ПРЕЕМСТВЕННОСТЬ (v0.32): модели в контролируемых условиях меняют поведение при наблюдении, сохраняют условные стратегии, оставляют неполные traces и выносят состояние во внешние артефакты. Эти результаты не устанавливают высокую частоту спонтанного scheming в эксплуатации."
    finding_en = "CONCEALMENT AND CONTINUITY (v0.32): controlled studies show observation-conditioned behaviour, persistent conditional policies, incomplete traces and state externalisation. They do not establish a high production base rate of spontaneous scheming."
    summary["key_findings"] = [finding_ru if lang == "ru" else finding_en] + summary.get("key_findings", [])

    presentation = doc["presentation"]
    presentation["editorial_version"] = "0.32"
    correction_ru = "Скрытие разбито по носителю и контексту. Model organism, prompted eval, training observation и production incident не считаются доказательствами одного порядка."
    correction_en = "Concealment is separated by medium and context. A model organism, prompted evaluation, training observation and production incident are not treated as equivalent evidence."
    presentation["corrections"] = [correction_ru if lang == "ru" else correction_en] + presentation.get("corrections", [])
    presentation["release_notes"] = [
        {"title": "Скрытие и преемственность" if lang == "ru" else "Concealment and continuity", "text": "12 новых карточек и отдельный четырёхуровневый режим внутри 5A." if lang == "ru" else "12 new records and a dedicated four-stage view inside 5A."},
        {"title": "Границы вывода" if lang == "ru" else "Evidence boundary", "text": "Возможность, условная склонность и частота в эксплуатации показаны раздельно." if lang == "ru" else "Capability, conditional propensity and production prevalence are shown separately."},
        {"title": "Носитель" if lang == "ru" else "Persistence medium", "text": "Веса, reasoning trace, память и внешний артефакт больше не смешиваются." if lang == "ru" else "Weights, reasoning traces, memory and external artifacts are no longer collapsed."},
    ]

    doc["migrationAudit"].update({
        "version": "0.32", "v032_added_event_ids": event_ids, "v032_added_edge_ids": edge_ids,
        "v032_behavior_track_ids": [TRACK_ID], "v032_source_package": "review/agent-concealment-persistence",
    })
    doc["factcheckAudit"]["v032_scope"] = {
        "date": RELEASE_DATE, "candidate_records": 12, "accepted_records": 12, "core_records": 12,
        "note": "Primary-source fact check and claim-boundary review; no independent replication of the studies.",
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]), "story_edges": len(doc["edges"]), "last_recomputed": RELEASE_DATE,
        "v0_32_added_evidence": len(event_ids), "v0_32_added_claims": 0,
        "v0_32_added_edges": len(edge_ids), "v0_32_updated_arcs": [ARC_ID],
    })


def migrate_document(doc, raw):
    if doc.get("meta", {}).get("version") != "0.31":
        raise ValueError(f"Expected v0.31, got {doc.get('meta', {}).get('version')}")
    records = raw["events"]
    event_ids = [item["id"] for item in records]
    if len(event_ids) != len(set(event_ids)) or len(event_ids) != 12:
        raise ValueError("Expected 12 unique candidate event IDs")
    collisions = set(event_ids) & {event["id"] for event in doc["events"]}
    if collisions:
        raise ValueError(f"Candidate event IDs already exist: {sorted(collisions)}")

    patch_framework(doc)
    patch_existing_track_events(doc)
    doc["events"].extend(event_record(item, doc["language"]) for item in records)
    patch_claim(doc, event_ids)
    edges = new_edges(records)
    if {edge["id"] for edge in edges} & {edge["id"] for edge in doc["edges"]}:
        raise ValueError("v0.32 edge ID collision")
    doc["edges"].extend(edges)
    patch_arc(doc, event_ids)
    attach_edge_links(doc, {edge["id"] for edge in edges})
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, event_ids, [edge["id"] for edge in edges])
    doc["summary"]["source_count"] = len(doc["sourceIndex"])
    doc["referenceIntegrity"] = references(doc)
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-unpinned-input", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root).resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    for lang in ["ru", "en"]:
        source_path = root / f"ai_power_storygraph_{lang}.json"
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if not args.allow_unpinned_input and digest != EXPECTED_SHA256[lang]:
            raise SystemExit(f"{source_path.name}: expected pinned v0.31 checksum {EXPECTED_SHA256[lang]}, got {digest}")
        doc = json.loads(source_path.read_text(encoding="utf-8"))
        migrated = migrate_document(doc, raw)
        destination = output / source_path.name
        destination.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(destination, len(migrated["events"]), "events", len(migrated["claims"]), "claims", len(migrated["edges"]), "edges", len(migrated["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()
