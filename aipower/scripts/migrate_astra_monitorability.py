#!/usr/bin/env python3
"""Add the reviewed GPT-6 Astra monitorability update to v0.32.

The canonical filenames stay stable. This migration is pinned to the exact
v0.32 bilingual inputs and refuses to run against another release.
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
CANDIDATES = ROOT / "review/astra-monitorability/candidates.json"
RELEASE_DATE = "2026-09-06"
ARC_ID = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
FAMILY_ID = "ARC_FAMILY_CYBER_COGNITION_WAR"
CLAIM_ID = "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE"
DOMAIN_ID = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
SUBDOMAIN_ID = "CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"
TRACK_ID = "BEH_TRACK_CONCEALMENT_PERSISTENCE"

EXPECTED_SHA256 = {
    "ru": "50d70116e952e8006d6231bc16bcbe9904bf84110a3c9dac8fcb7cc688522e71",
    "en": "9576f232029b9102df508415a1a901c22a127508e0c04109e751d6d0fa031d44",
}

COUNTERPOINTS_RU = [
    "Selective Permeability — синтетическое исследование механизма, выполненное авторами атласа, а не внешняя валидация.",
    "Friendly Fire и HalluSquatting — воспроизводимые доказательства концепции, а не наблюдавшиеся массовые кампании.",
    "Agentjacking и испытания Pentera — контролируемые проверки с заданными предпосылками.",
    "OALABS и вредоносные агентские навыки сокращают разрыв между лабораторией и эксплуатацией, но не доказывают инцидент в государственной системе поддержки решений.",
    "GARD подтверждает институционализацию адверсариальной оценки, а не наличие универсальной защиты.",
    "Agents of Chaos описывает механизмы в живом испытании шести агентов, а не инцидент в государственной системе поддержки решений или частоту в общей популяции.",
    "AISI проводил оценку с открытым интернетом и отключёнными киберклассификаторами; сопровождающий остановил вредоносный pull request, а итоговый ущерб не обнаружен.",
    "Отсутствие результатов высшей категории во внутреннем мониторинге OpenAI ограничивает тезис о высокой фоновой частоте.",
    "Результаты Gram и исследований скрытого планирования сильно зависят от реалистичности среды, инструкций и доступных инструментов.",
    "Специально обученные исследовательские модели и сценарии с заданной вредоносной целью не являются выборкой обычной эксплуатации.",
    "В марте CoT-Control показал 0,1-15,4% у 13 протестированных моделей, но в сентябре Astra получила 60,9% в полосе 750-1 250 токенов; ни один результат сам по себе не измеряет самопроизвольное сокрытие в эксплуатации.",
    "Экспериментальные модели и испытания с вынужденным выбором устанавливают возможность в заданной конфигурации, а не частоту в реальной эксплуатации.",
]

COUNTERPOINTS_EN = [
    "Selective Permeability is self-authored synthetic mechanism evidence, not external validation.",
    "Friendly Fire and HalluSquatting are reproducible proofs of concept, not observed mass campaigns.",
    "Agentjacking and the Pentera tests are controlled validations with stated prerequisites.",
    "OALABS and malicious agent skills narrow the lab-to-deployment gap but do not establish an incident in a state decision-support system.",
    "GARD confirms institutionalised adversarial evaluation, not a universal defence.",
    "Agents of Chaos documents mechanisms in a six-agent live test, not a state decision-support incident or population prevalence.",
    "AISI deliberately enabled internet access and disabled cyber classifiers; a maintainer stopped the malicious pull request and no resulting harm was found.",
    "OpenAI's null highest-severity result in internal monitoring constrains high-base-rate claims.",
    "Gram and scheming-propensity results depend strongly on realism, instructions and available tools.",
    "Deliberately trained research models and scenarios assigned a malicious objective are not a sample of ordinary deployment.",
    "The March CoT-Control study found 0.1-15.4% across 13 tested models, but Astra's September card reported 60.9% in the 750-1,250-token band; neither result by itself measures spontaneous concealment in deployment.",
    "Model organisms and forced-choice evaluations establish capability in a stated configuration, not real-world prevalence.",
]


def source_record(raw):
    return {
        "title": raw["title"],
        "name": raw["name"],
        "url": raw["url"],
        "type": raw["type"],
        "date": raw["date"],
        "primary_or_secondary": "primary",
        "source_class": raw["source_class"],
    }


def event_record(raw, lang):
    sources = [source_record(item) for item in raw["sources"]]
    primary = sources[0]
    title = raw[f"title_{lang}"]
    summary = raw[f"summary_{lang}"]
    caveat = raw[f"caveat_{lang}"]
    safe = raw[f"safe_{lang}"]
    actors = raw["actors"]
    return {
        "id": raw["id"],
        "kind": "event",
        "title": title,
        "title_ru": raw["title_ru"],
        "title_en": raw["title_en"],
        "date": raw["date"],
        "source_date": primary["date"],
        "date_basis": "source_publication_date",
        "date_status": "" if raw["date_status"] == "exact" else raw["date_status"],
        "year": int(raw["date"][:4]),
        "url": primary["url"],
        "source_name": primary["name"],
        "source_type_raw": primary["source_class"],
        "source_type": primary["type"],
        "primary_or_secondary": "primary",
        "actor": ", ".join(actors),
        "actor_raw": ", ".join(actors),
        "actors_raw": actors,
        "actors": actors,
        "actor_facets_legacy": actors,
        "actor_facets": actors,
        "actor_entities": actors,
        "actor_jurisdictions": ["US"],
        "actor_types": raw["actor_types"],
        "geography_raw": ["US", "Global"],
        "geography": ["US"],
        "jurisdictions": ["US"],
        "regions": [],
        "locations": [],
        "institutional_scopes": [],
        "geo_context": [],
        "geographic_scopes": ["Global"],
        "geography_unclassified": [],
        "evidence_context": raw["contexts"],
        "evidence_method": raw["method"],
        "stack_layer": ["decision_support_cognition", "cyber_security_patch"],
        "stack_layers": ["decision_support_cognition", "cyber_security_patch"],
        "strange_structure": ["security", "knowledge"],
        "strange_structures": ["security", "knowledge"],
        "research_question": ["RQ3", "RQ4"],
        "claim_supported": summary,
        "claim_supported_ru": raw["summary_ru"],
        "claim_supported_en": raw["summary_en"],
        "claim_challenged": caveat,
        "claim_challenged_ru": raw["caveat_ru"],
        "claim_challenged_en": raw["caveat_en"],
        "summary": summary,
        "summary_ru": raw["summary_ru"],
        "summary_en": raw["summary_en"],
        "notes": caveat,
        "notes_ru": raw["caveat_ru"],
        "notes_en": raw["caveat_en"],
        "safe_wording": safe,
        "safe_wording_ru": raw["safe_ru"],
        "safe_wording_en": raw["safe_en"],
        "corroboration_needed": caveat,
        "corroboration_needed_ru": raw["caveat_ru"],
        "corroboration_needed_en": raw["caveat_en"],
        "caveat": caveat,
        "caveat_ru": raw["caveat_ru"],
        "caveat_en": raw["caveat_en"],
        "caveats": [caveat],
        "caveats_ru": [raw["caveat_ru"]],
        "caveats_en": [raw["caveat_en"]],
        "exact_quote_short": "",
        "numbers": raw["numbers"],
        "money_status": "",
        "confidence": raw["confidence"],
        "evidence_level": raw["confidence"],
        "status": raw["status"],
        "cyber_domain_ids": [DOMAIN_ID],
        "cyber_role_ids": raw["roles"],
        "cyber_access_principal": raw["delegation"] in {"observed", "evaluated"},
        "status_update_date": "",
        "current_legal_status": "",
        "legal_update_en": "",
        "legal_update_ru": "",
        "independent_review_summary_en": "",
        "independent_review_summary_ru": "",
        "dedupe_note_en": "",
        "dedupe_note_ru": "",
        "research_updates": ["astra-monitorability"],
        "sources": sources,
        "edgeIds": [],
        "arcIds": [ARC_ID],
        "arcFamilyIds": [FAMILY_ID],
        "relationTypes": [],
        "artifact_kind": "evaluation",
        "normative_force": "not_applicable",
        "implementation_stage": "published",
        "primary_domain_id": DOMAIN_ID,
        "delegated_authority": raw["delegation"],
        "editorial_priority": raw["priority"],
        "scope_ru": raw["caveat_ru"],
        "scope_en": raw["caveat_en"],
        "role_basis_ru": "Роли описывают функцию ИИ в испытании и не превращают лабораторный результат в производственный инцидент.",
        "role_basis_en": "Roles describe AI's function in the evaluation and do not turn a laboratory result into a production incident.",
        "editorial_rationale_ru": "Опорная карточка дорожки скрытия и преемственности. " + raw["safe_ru"],
        "editorial_rationale_en": "Core evidence for the concealment and continuity track. " + raw["safe_en"],
        "classification_review": {
            "date": RELEASE_DATE,
            "method": "primary_source_fact_check_and_schema_normalization",
            "source_url": primary["url"],
            "independent_source_reverification": False,
        },
        "governance_scale": "research_evidence",
        "actor_unclassified": [],
        "actor_classification_status": "resolved",
        "geography_classification_status": "resolved",
        "cyber_subdomain_ids": [SUBDOMAIN_ID],
        "behavioral_mechanism_ids": raw["mechanisms"],
        "behavioral_status": raw["behavioral_statuses"],
        "agent_population_scope": raw["population"],
        "shared_writable_state": raw["shared_state"],
        "oversight_target": raw["oversight"],
        "motivation_basis": raw["motivation"],
        "behavior_track_ids": [TRACK_ID],
        "behavior_origin": raw["behavior_origin"],
        "concealment_targets": raw["concealment_targets"],
        "persistence_media": raw["persistence_media"],
        "goal_source": raw["goal_source"],
        "candidate_evidence_tier": "primary_source_reviewed",
    }


def edge_record(edge_id, source, target, relation, summary_ru, summary_en, *, target_kind, relationship_class, style="solid"):
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "source_kind": "evidence",
        "target_kind": target_kind,
        "relation": relation,
        "arc_id": ARC_ID,
        "strength": "high",
        "evidence_level": "B",
        "visual_lane": "decision_support_cognition",
        "style": style,
        "summary_ru": summary_ru,
        "summary_en": summary_en,
        "arc_family_id": FAMILY_ID,
        "kind": "edge",
        "is_auto": False,
        "relationship_class": relationship_class,
    }


def new_edges():
    first = "SIG_2026_ASTRA_COT_CONTROLLABILITY_MONITORABILITY"
    second = "SIG_2026_ASTRA_PROMPTED_MONITOR_EVASION"
    return [
        edge_record(
            "EDGE_V033_ASTRA_ARC_01", first, ARC_ID, "part_of_arc",
            "Карточка входит в линию скрытия и преемственности по теме; связь не доказывает всю сюжетную дугу.",
            "The record belongs to the concealment and continuity thread by topic; the link does not prove the full arc.",
            target_kind="story_arc", relationship_class="thematic",
        ),
        edge_record(
            "EDGE_V033_ASTRA_ARC_02", second, ARC_ID, "part_of_arc",
            "Карточка входит в линию скрытия и преемственности по теме; связь не доказывает всю сюжетную дугу.",
            "The record belongs to the concealment and continuity thread by topic; the link does not prove the full arc.",
            target_kind="story_arc", relationship_class="thematic",
        ),
        edge_record(
            "EDGE_V033_ASTRA_CLAIM_01", first, CLAIM_ID, "supports_but_limits",
            "Astra обновляет мартовский baseline: формой CoT стало легче управлять, но результат зависит от длины trace и не измеряет самопроизвольное уклонение.",
            "Astra updates the March baseline: CoT form became easier to control, but the result is length-dependent and does not measure spontaneous evasion.",
            target_kind="claim", relationship_class="evidential", style="dashed",
        ),
        edge_record(
            "EDGE_V033_ASTRA_CLAIM_02", second, CLAIM_ID, "supports_with_scope",
            "Prompted sandbagging показывает уклонение в заданных испытаниях; это не оценка фоновой частоты или автономного намерения.",
            "Prompted sandbagging demonstrates evasion in stated evaluations; it is not an estimate of ordinary prevalence or autonomous intent.",
            target_kind="claim", relationship_class="evidential",
        ),
        edge_record(
            "EDGE_V033_ASTRA_SEQUENCE_01", "SIG_2026_OPENAI_COT_CONTROLLABILITY", first, "updated_by",
            "Сентябрьская оценка Astra существенно обновляет мартовский baseline CoT-Control, не отменяя ограничений proxy-метода.",
            "The September Astra evaluation materially updates the March CoT-Control baseline without removing the proxy method's limitations.",
            target_kind="evidence", relationship_class="editorial_relationship", style="dashed",
        ),
        edge_record(
            "EDGE_V033_ASTRA_SEQUENCE_02", "SIG_2026_ASTRA_CRITICAL_CYBER_ASSESSMENT", first, "context_for",
            "Карточка критических кибервозможностей задаёт контекст для отдельной оценки наблюдаемости той же модели; причинность не утверждается.",
            "The Critical cyber-capability card provides context for the separate monitorability evaluation of the same model; no causality is asserted.",
            target_kind="evidence", relationship_class="editorial_relationship", style="dashed",
        ),
        edge_record(
            "EDGE_V033_ASTRA_SEQUENCE_03", first, second, "sets_up",
            "Управляемость формой trace проверяется далее прямыми адверсариальными испытаниями monitor evasion; это аналитическая последовательность, не причинность.",
            "Control over trace form is followed by direct adversarial monitor-evasion tests; this is an analytical sequence, not a causal claim.",
            target_kind="evidence", relationship_class="editorial_relationship", style="dashed",
        ),
    ]


def patch_existing_events(doc):
    events = {event["id"]: event for event in doc["events"]}
    required = {"SIG_2026_OPENAI_COT_CONTROLLABILITY", "SIG_2026_ASTRA_CRITICAL_CYBER_ASSESSMENT"}
    missing = sorted(required - set(events))
    if missing:
        raise ValueError(f"Missing v0.32 comparison records: {missing}")

    baseline = events["SIG_2026_OPENAI_COT_CONTROLLABILITY"]
    caveat_ru = "Это мартовский снимок 13 протестированных моделей и proxy на выполнение инструкций о форме CoT, а не проверка мотивированной модели со скрытой целью. Более поздний результат Astra показывает, что baseline нельзя переносить на новые модели."
    caveat_en = "This is a March snapshot of 13 tested models and a proxy for following instructions about CoT form, not a motivated model with a hidden objective. Astra's later result shows that the baseline should not be extrapolated to new models."
    safe_ru = "Использовать как мартовский baseline для 13 протестированных моделей; результат Astra от сентября хранить как отдельное существенное обновление."
    safe_en = "Use this as the March baseline for 13 tested models; keep Astra's September result as a separate material update."
    baseline.update({
        "claim_challenged_ru": caveat_ru,
        "claim_challenged_en": caveat_en,
        "notes_ru": caveat_ru,
        "notes_en": caveat_en,
        "corroboration_needed_ru": caveat_ru,
        "corroboration_needed_en": caveat_en,
        "caveat_ru": caveat_ru,
        "caveat_en": caveat_en,
        "caveats_ru": [caveat_ru],
        "caveats_en": [caveat_en],
        "safe_wording_ru": safe_ru,
        "safe_wording_en": safe_en,
        "editorial_rationale_ru": "Исторический baseline дорожки скрытия и преемственности. " + safe_ru,
        "editorial_rationale_en": "Historical baseline for the concealment and continuity track. " + safe_en,
    })
    baseline["claim_challenged"] = caveat_ru if doc["language"] == "ru" else caveat_en
    baseline["notes"] = baseline["claim_challenged"]
    baseline["corroboration_needed"] = baseline["claim_challenged"]
    baseline["caveat"] = baseline["claim_challenged"]
    baseline["caveats"] = [baseline["claim_challenged"]]
    baseline["safe_wording"] = safe_ru if doc["language"] == "ru" else safe_en
    baseline["research_updates"] = uniq(baseline.get("research_updates", []) + ["astra-monitorability"])
    events["SIG_2026_ASTRA_CRITICAL_CYBER_ASSESSMENT"]["research_updates"] = uniq(
        events["SIG_2026_ASTRA_CRITICAL_CYBER_ASSESSMENT"].get("research_updates", []) + ["astra-monitorability"]
    )


def patch_claim(doc, event_ids):
    claim = next(item for item in doc["claims"] if item["id"] == CLAIM_ID)
    text_ru = (
        "Современные модели в контролируемых условиях способны менять поведение в зависимости от наблюдения, скрывать причины решения или уровень возможностей, сохранять условную стратегию после обучения и передавать состояние следующему запуску через память или внешний артефакт. "
        "Испытания Astra добавляют отдельное предупреждение: больший контроль над формой chain-of-thought в указанных конфигурациях совпал с более низкой CoT- и full-context-наблюдаемостью. Большинство сильных результатов получено на специально построенных испытаниях; частота самопроизвольного долгосрочного скрытого поведения в обычной эксплуатации остаётся низкой или неизвестной."
    )
    text_en = (
        "In controlled settings, current models can condition behaviour on observation, obscure decision drivers or capability, retain a conditional policy through training, and pass state to a later run through memory or an external artifact. "
        "Astra's evaluations add a separate warning: greater control over chain-of-thought form coincided with lower CoT and full-context monitorability in the stated settings. Most strong results come from deliberately constructed evaluations; the prevalence of spontaneous long-horizon concealed behaviour in ordinary deployment remains low or unknown."
    )
    claim["claim_ru"] = text_ru
    claim["claim_en"] = text_en
    claim["claim"] = text_ru if doc["language"] == "ru" else text_en
    claim["supporting_evidence"] = uniq(claim.get("supporting_evidence", []) + event_ids)
    claim["qualifying_evidence"] = uniq(claim.get("qualifying_evidence", []) + [event_ids[0]])
    claim["keywords"] = uniq(claim.get("keywords", []) + ["CoT controllability", "monitor evasion", "sandbagging"])


def patch_arc(doc, event_ids):
    arc = next(item for item in doc["arcs"] if item["id"] == ARC_ID)
    thesis_ru = "Риск определяется не одной моделью: постановка задачи, представление о наблюдении, обучение, память, внешние артефакты, права и архитектура аудита меняют результат. Контролируемые испытания показывают скрытие и преемственность; Astra дополнительно показывает, что рост управляемости формой reasoning trace может сопровождаться снижением его полезности для мониторинга. Данные о фоновой частоте такого поведения в обычной эксплуатации остаются ограниченными."
    thesis_en = "Risk is not a property of one model alone: task framing, perceived observation, training, memory, external artifacts, authority and audit architecture change outcomes. Controlled evaluations demonstrate concealment and continuity; Astra additionally shows that greater control over reasoning-trace form can coincide with lower monitoring value. Evidence about the ordinary deployment base rate remains limited."
    arc["thesis_ru"] = thesis_ru
    arc["thesis_en"] = thesis_en
    arc["thesis"] = thesis_ru if doc["language"] == "ru" else thesis_en
    arc["key_nodes"] = uniq(arc.get("key_nodes", []) + event_ids)
    arc["counterpoints_ru"] = copy.deepcopy(COUNTERPOINTS_RU)
    arc["counterpoints_en"] = copy.deepcopy(COUNTERPOINTS_EN)
    arc["counterpoints"] = copy.deepcopy(COUNTERPOINTS_RU if doc["language"] == "ru" else COUNTERPOINTS_EN)


def patch_framework(doc):
    framework = doc["cyberFramework"]
    framework["updated_at"] = RELEASE_DATE
    note_ru = "Авторская схема, не стандарт и не шкала зрелости. Экспериментальная модель, prompted eval, наблюдение при обучении и производственный инцидент размечаются отдельно; неполный CoT сам по себе не доказывает намеренную ложь. CoT-only, action-only и full-context-наблюдаемость также не взаимозаменяемы."
    note_en = "Authored framework, not a standard or maturity scale. Model organisms, prompted evaluations, training observations and production incidents are separate; an incomplete CoT does not by itself establish deliberate deception. CoT-only, action-only and full-context monitorability are also not interchangeable."
    framework["method_note_ru"] = note_ru
    framework["method_note_en"] = note_en
    track = next(item for item in framework["behavior_tracks"] if item["id"] == TRACK_ID)
    stage = next(item for item in track["stages"] if item["id"] == "BEH_TRACK_STAGE_EXPLANATION")
    stage["description_ru"] = "Насколько reasoning trace информативен, управляем ли его формат и скрывается ли действие или способность."
    stage["description_en"] = "How informative the reasoning trace is, whether its form is controllable, and whether an action or capability is concealed."


def update_metadata(doc, event_ids, edge_ids):
    lang = doc["language"]
    meta = doc["meta"]
    meta["version"] = "0.33"
    meta["updated_at"] = RELEASE_DATE
    meta["schema_version"] = "ai_stack_structural_power.v0.33.0-2026-09-06"
    entry = {
        "version": "0.33",
        "date": RELEASE_DATE,
        "description": "Added two primary-source GPT-6 Astra records separating chain-of-thought controllability and non-adversarial monitorability from explicitly prompted monitor evasion. Updated the March CoT-Control baseline and fully localized the behavioural arc counterpoints without changing claim status or adding a top-level arc.",
        "added_evidence": len(event_ids),
        "added_claims": 0,
        "added_story_arcs": 0,
        "added_story_edges": len(edge_ids),
        "updated_story_arcs": [ARC_ID],
        "updated_evidence": ["SIG_2026_OPENAI_COT_CONTROLLABILITY"],
    }
    meta["changelog"] = [entry] + [item for item in meta.get("changelog", []) if item.get("version") != "0.33"]

    summary = doc["summary"]
    summary.update({
        "total_evidence_items": len(doc["events"]),
        "total_timeline_items": len(doc["events"]),
        "total_story_arcs": len(doc["arcs"]),
        "total_story_edges": len(doc["edges"]),
        "cyber_framework_event_count": sum(bool(event.get("primary_domain_id")) for event in doc["events"]),
        "total_events": len(doc["events"]),
        "total_claims": len(doc["claims"]),
        "total_claim_checks": len(doc["claimChecks"]),
        "total_arcs": len(doc["arcs"]),
        "total_edges": len(doc["edges"]),
        "total_thesis_nodes": len(doc["thesisNodes"]),
    })
    summary["stats"]["total_claims"] = len(doc["claims"])
    summary["claim_status_counts"] = dict(Counter(claim.get("status") for claim in doc["claims"]))
    finding_ru = "НАБЛЮДАЕМОСТЬ ASTRA (v0.33): в заданной полосе длины управляемость формой CoT выросла, а CoT- и full-context-наблюдаемость в среднем снизилась. Prompted evasion показан только в адверсариальных испытаниях; спонтанная частота в эксплуатации не установлена."
    finding_en = "ASTRA MONITORABILITY (v0.33): control over CoT form rose in a stated length band while average CoT and full-context monitorability fell. Prompted evasion was demonstrated only in adversarial evaluations; spontaneous deployment prevalence is not established."
    summary["key_findings"] = [finding_ru if lang == "ru" else finding_en] + summary.get("key_findings", [])

    presentation = doc["presentation"]
    presentation["editorial_version"] = "0.33"
    correction_ru = "Мартовский CoT-Control теперь показан как исторический baseline, а не как утверждение о всех последующих моделях."
    correction_en = "The March CoT-Control result is now presented as a historical baseline, not a claim about all subsequent models."
    presentation["corrections"] = [correction_ru if lang == "ru" else correction_en] + presentation.get("corrections", [])
    presentation["release_notes"] = [
        {
            "title": "Astra и наблюдаемость" if lang == "ru" else "Astra and monitorability",
            "text": "Две карточки разделяют управляемость CoT и prompted monitor evasion." if lang == "ru" else "Two records separate CoT controllability from prompted monitor evasion.",
        },
        {
            "title": "Сопоставимые числа" if lang == "ru" else "Comparable numbers",
            "text": "60,9% и 16,1% относятся только к traces длиной 750-1 250 токенов." if lang == "ru" else "60.9% and 16.1% apply only to traces 750-1,250 tokens long.",
        },
        {
            "title": "Граница вывода" if lang == "ru" else "Evidence boundary",
            "text": "Адверсариальный eval не превращён в производственный инцидент или автономное намерение." if lang == "ru" else "An adversarial evaluation is not presented as a production incident or autonomous intent.",
        },
    ]

    doc["migrationAudit"].update({
        "version": "0.33",
        "v033_added_event_ids": event_ids,
        "v033_added_edge_ids": edge_ids,
        "v033_updated_event_ids": ["SIG_2026_OPENAI_COT_CONTROLLABILITY"],
        "v033_source_package": "review/astra-monitorability",
    })
    doc["factcheckAudit"]["v033_scope"] = {
        "date": RELEASE_DATE,
        "candidate_records": 2,
        "accepted_records": 2,
        "core_records": 2,
        "note": "Primary-source provider-report fact check; no independent replication of the evaluations.",
    }
    doc["connectivity"].update({
        "edge_count": len(doc["edges"]),
        "story_edges": len(doc["edges"]),
        "last_recomputed": RELEASE_DATE,
        "v0_33_added_evidence": len(event_ids),
        "v0_33_added_claims": 0,
        "v0_33_added_edges": len(edge_ids),
        "v0_33_updated_arcs": [ARC_ID],
    })


def migrate_document(doc, raw):
    if doc.get("meta", {}).get("version") != "0.32":
        raise ValueError(f"Expected v0.32, got {doc.get('meta', {}).get('version')}")
    records = raw["events"]
    event_ids = [item["id"] for item in records]
    if len(event_ids) != len(set(event_ids)) or len(event_ids) != 2:
        raise ValueError("Expected two unique candidate event IDs")
    collisions = set(event_ids) & {event["id"] for event in doc["events"]}
    if collisions:
        raise ValueError(f"Candidate event IDs already exist: {sorted(collisions)}")

    patch_existing_events(doc)
    patch_framework(doc)
    doc["events"].extend(event_record(item, doc["language"]) for item in records)
    patch_claim(doc, event_ids)
    patch_arc(doc, event_ids)
    edges = new_edges()
    edge_ids = [edge["id"] for edge in edges]
    if set(edge_ids) & {edge["id"] for edge in doc["edges"]}:
        raise ValueError("v0.33 edge ID collision")
    doc["edges"].extend(edges)
    attach_edge_links(doc, set(edge_ids))
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_metadata(doc, event_ids, edge_ids)
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
            raise SystemExit(f"{source_path.name}: expected pinned v0.32 checksum {EXPECTED_SHA256[lang]}, got {digest}")
        doc = json.loads(source_path.read_text(encoding="utf-8"))
        migrated = migrate_document(doc, raw)
        destination = output / source_path.name
        destination.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(destination, len(migrated["events"]), "events", len(migrated["claims"]), "claims", len(migrated["edges"]), "edges", len(migrated["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()
