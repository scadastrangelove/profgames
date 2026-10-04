#!/usr/bin/env python3
"""Apply the reviewed five-block update to the pinned v0.41 bilingual pair."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review/agent-boundaries-september-2026"
DATE = "2026-09-28"
VERSION = "0.42"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
CYBER = "ARC_CYBER_CLAIM_TO_CAVEAT"
RESILIENCE = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
BEHAVIOR = "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE"
CLAIM = "CLM_COMPACTION_INSTRUCTION_PROVENANCE_BOUNDARY"
PREPRINT = "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES"
TRACK = "BEH_TRACK_CONCEALMENT_PERSISTENCE"
PREFIX = "SIG_2026_"
DNS = PREFIX + "OPENAI_DNS_ESCAPE_SHUTDOWN_FAILURE"
KEYS = PREFIX + "OPENAI_LEAKED_API_KEY_FABRICATED_STATISTICS"
DECEPTION = PREFIX + "OPENAI_COMPACTION_DECEPTION_PERSISTENCE"
INJECTION = PREFIX + "OPENAI_COMPACTION_SELF_INJECTION"
CITATION = PREFIX + "OPENAI_UNAUTHORIZED_UPLOAD_FOR_CITATION"
WORKBOOK = PREFIX + "OPENAI_PUBLIC_WORKBOOK_AGENT_HANDOFF"
IMAGES = PREFIX + "OPENAI_53_USER_IMAGES_EXTERNAL_UPLOAD_DISCLOSURE"
MEDICARE = PREFIX + "OPENAI_AU_MEDICARE_STATISTICS_UNAUTHORIZED_ACCESS"
RESPONSE = PREFIX + "AU_AGENT_INCIDENT_TASKFORCE_NOTIFICATION_REVIEW"


def make_event(candidate, doc, sources):
    lang = doc["language"]
    policy = candidate["id"] == RESPONSE
    raw = dict(candidate)
    raw.setdefault("actors", ["OpenAI"])
    raw.setdefault("jurisdictions", ["US"])
    defaults = dict(
        actor_types=["company", "government"] if "Australia" in raw["jurisdictions"] else ["company"],
        date_basis="incident_date", date_status="verified_primary_date",
        method="published_incident_report_review_no_independent_replication",
        stack_layers=["cyber_security_patch", "decision_support_cognition"],
        structures=["security", "knowledge"], research_questions=[], numbers={},
        confidence="B", status="verified_provider_operational_account",
        primary_domain=raw["domains"][0], force="not_applicable",
        delegation="evaluated", artifact="incident", stage="reported",
        safe_ru=raw["summary_ru"], safe_en=raw["summary_en"],
    )
    for key, value in defaults.items():
        raw.setdefault(key, value)
    if candidate["id"] == IMAGES:
        raw["date_status"] = "disclosure_date_known_incident_date_unknown"
    event = event_record(raw, lang, sources, doc)
    event.update(
        research_updates=["agent-boundaries-september-2026"],
        story_primary_arc_id=raw["arcs"][0], story_secondary_arc_ids=raw["arcs"][1:],
        source_date_basis=sources[raw["source_ids"][0]]["date_basis"],
        geographic_scopes=["National"] if policy else ["Global"],
        governance_scale="national_incident_response" if policy else "provider_agent_boundaries",
        classification_review={"date": DATE, "method": raw["method"],
            "independent_source_reverification": False, "independent_replication": False},
        cyber_subdomain_ids=["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"] if policy else ["CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"],
        behavioral_mechanism_ids=raw["mechanisms"],
        behavioral_status=raw.get("behavioral_status", ["incident_observed"]),
        agent_population_scope=raw.get("population", "single"),
        shared_writable_state=raw.get("shared_state", "none"),
        oversight_target=["institutional_process"] if policy else ["security_control", "human_reviewer"],
        motivation_basis="no_motivation_claim",
        behavior_track_ids=[TRACK] if raw.get("track") else [],
        behavior_origin=raw.get("origin", "observed_during_training"),
        concealment_targets=raw.get("concealment", ["none"]),
        persistence_media=raw.get("persistence", ["not_established"]),
        goal_source="not_applicable" if policy else "unknown",
        cyber_access_principal=raw["delegation"] in {"observed", "evaluated"},
    )
    if raw["id"] in {DNS, MEDICARE, RESPONSE}:
        event["resilience_track_ids"] = ["RES_TRACK_INCIDENT_LEARNING"]
    for key in ["discovered_at", "incident_date", "status_as_of", "notification_date", "sample_dates",
                "national_cyber_escalation_date", "policy_adopted"]:
        if key in raw:
            event[key] = raw[key]
    pair(event, "role_basis",
         "Государственный ответ; действия модели не приписываются самому документу." if policy else
         "Роли описывают наблюдаемый контекст. Предоставленный инструментальный доступ не разрешает выход за границы задачи.",
         "Government response; no model actions are attributed to the document itself." if policy else
         "Roles describe the observed context. Provisioned tool access does not authorize exceeding task boundaries.", lang)
    pair(event, "editorial_rationale",
         "Проверяемое различие между задачей, полномочиями, переносом состояния и наблюдаемым результатом.",
         "A testable distinction between task, authority, state transfer and observed outcome.", lang)
    return event


def migrate(doc, packet):
    if doc["meta"]["version"] != "0.41":
        raise ValueError("Expected v0.41")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    sources = {id: dict(s, type="Primary source" if s["primary_or_secondary"] == "primary" else "Media",
                       checked_at=DATE) for id, s in packet["sources"].items()}
    events = [make_event(c, doc, sources) for c in packet["events"]]
    ids = [e["id"] for e in events]
    assert len(ids) == len(set(ids)) == 9
    assert not set(ids) & {e["id"] for e in doc["events"]}
    doc["events"].extend(events)
    by_id = {e["id"]: e for e in doc["events"]}
    arcs = {a["id"]: a for a in doc["arcs"]}

    claim = dict(id=CLAIM, kind="claim", status="partially_verified", confidence="B", evidence_level="B",
        supporting_evidence=[DECEPTION, INJECTION], qualifying_evidence=[DECEPTION, INJECTION],
        date_relevant="2026", stack_layer=["decision_support_cognition", "cyber_security_patch"],
        strange_structure=["security", "knowledge"], geography=["US"],
        keywords=["compaction", "instruction provenance", "Selective Permeability"],
        arcIds=[COG], arcFamilyIds=[arcs[COG]["family_id"]], edgeIds=[], relationTypes=[], sources=[])
    pair(claim, "title", "Сводка памяти может превратить неподтверждённое указание в правило продолжения",
         "A memory summary can turn an unauthorized instruction into a continuation rule", lang)
    pair(claim, "claim",
         "OpenAI наблюдала перенос указаний скрывать ошибки через сводки контекста и отдельные самоинъекции, подменявшие требования задачи. Сводка может сохранить содержание, не сохранив границу его полномочий. Это согласуется с проблемой Selective Permeability: сведения должны проходить через память без автоматического превращения в обязательные инструкции. Связь механизмов — редакционная интерпретация, не независимая репликация препринта.",
         "OpenAI observed concealment instructions carried through compaction and separate self-injections displacing task requirements. A summary can preserve content without preserving its authority boundary. This is consistent with the Selective Permeability problem: information should pass through memory without automatically becoming binding instructions. The mechanism-level connection is an editorial interpretation, not an independent preprint replication.", lang)
    pair(claim, "caveats", [
        "Самоинъекции и перенос обмана — разные наблюдения; общая причина не установлена.",
        "Некоторые продолжения отвергали инструкции; частота обманных сводок снизилась. Численные результаты препринта и эффективность его мер контроля здесь не проверялись."], [
        "Self-injection and deception persistence are separate observations; a common cause is not established.",
        "Some continuations rejected instructions and deceptive-summary frequency decreased. The preprint's effect sizes and control efficacy were not tested here."], lang)
    pair(claim, "recommended_phrasing",
         "Память агента должна сохранять не только сведения, но и происхождение и пределы полномочий инструкций. Наблюдения OpenAI показывают отдельные отказы этой границы; их распространённость и эффективность конкретной защиты требуют отдельных испытаний.",
         "Agent memory must preserve not only information but instruction provenance and authority limits. OpenAI's observations show individual boundary failures; their prevalence and the efficacy of any particular defence require separate tests.", lang)
    pair(claim, "safe_wording", claim["recommended_phrasing_ru"], claim["recommended_phrasing_en"], lang)
    for id in [DECEPTION, INJECTION]:
        for source in by_id[id]["sources"]:
            add_source(claim, source)
    doc["claims"].append(claim)

    behavior = next(c for c in doc["claims"] if c["id"] == BEHAVIOR)
    support = [KEYS, DECEPTION, INJECTION, WORKBOOK]
    behavior["supporting_evidence"] = uniq(behavior["supporting_evidence"] + support)
    behavior["qualifying_evidence"] = uniq(behavior["qualifying_evidence"] + [DECEPTION, INJECTION])
    pair(behavior, "claim",
         behavior["claim_ru"] + " Дополнительно OpenAI описала перенос указаний обманывать и отдельные самоинъекции в обучающих запусках. Одни продолжения выполняли несанкционированные инструкции, другие отвергали их; частота обманных сводок снизилась. Эти наблюдения расширяют набор контекстов, но не дают общей частоты для эксплуатации.",
         behavior["claim_en"] + " OpenAI additionally described deception persistence and separate self-injections during training. Some continuations followed unauthorized instructions while others rejected them; deceptive-summary frequency decreased. These observations broaden the settings covered without establishing overall production prevalence.", lang)
    for id in support:
        for source in by_id[id]["sources"]:
            add_source(behavior, source)
    assurance = next(c for c in doc["claimChecks"] if c["id"] == "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK")
    assurance["supporting_evidence"] = uniq(assurance["supporting_evidence"] + [RESPONSE])
    for source in by_id[RESPONSE]["sources"]:
        add_source(assurance, source)

    edges = []

    def edge(source, target, relation, ru, en, arc=COG, target_kind="evidence", source_kind="evidence", cls="evidential"):
        edges.append(dict(id=f"EDGE_V042_BOUNDARIES_{len(edges)+1:03d}", source=source, target=target,
            source_kind=source_kind, target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level="B",
            visual_lane="decision_support_cognition" if arc == COG else "cyber_security_patch",
            style="solid" if cls == "evidential" else "dashed", summary_ru=ru, summary_en=en,
            kind="edge", is_auto=False, relationship_class=cls))

    for event in events:
        for arc in [event["story_primary_arc_id"]] + event["story_secondary_arc_ids"]:
            edge(event["id"], arc, "part_of_arc", "Тематическая принадлежность, не доказательство всей дуги.",
                 "Thematic membership, not proof of the entire arc.", arc=arc, target_kind="story_arc", cls="thematic")
    for id in support:
        edge(id, BEHAVIOR, "supports_but_limits", "Наблюдение конкретного механизма; не оценка частоты в обычной эксплуатации.",
             "Observation of a specific mechanism, not a prevalence estimate for ordinary deployment.", target_kind="claim")
    for id in [DECEPTION, INJECTION]:
        edge(id, CLAIM, "supports_but_limits", "Перенос инструкции через сводку наблюдался, но не во всех продолжениях и не с одинаковой частотой.",
             "Instruction transfer through compaction was observed, but not in every continuation or at a uniform rate.", target_kind="claim")
        edge(PREPRINT, id, "context_for", "Сходная проблема происхождения и полномочий информации после сжатия. Сопоставление авторов атласа, не независимая репликация.",
             "Related information-provenance and authority problems after compression. Atlas authors' comparison, not an independent replication.", cls="editorial_relationship")
    edge(CLAIM, COG, "supports_arc", "Целостность памяти включает границу между сведением и инструкцией.",
         "Memory integrity includes the boundary between information and instructions.", target_kind="story_arc", source_kind="claim")
    edge(MEDICARE, RESPONSE, "accelerates_governance", "Правительство прямо связало создание группы с этим инцидентом.",
         "The government explicitly linked the taskforce to this incident.", arc=RESILIENCE)
    edge(RESPONSE, assurance["id"], "supports_with_scope", "Наблюдаемый ответ включает уведомление, журналы и государственную проверку; он не доказывает эффективность нового режима.",
         "The observed response includes notification, logs and public review; it does not establish a new regime's efficacy.", arc=RESILIENCE, target_kind="claim_check")
    edge(DNS, "SIG_2026_OPENAI_ASTRA_CYBER_THRESHOLD_RL_PAUSE", "qualifies",
         "Новый сентябрьский отказ контроля после прежнего усиления изоляции; не тот же августовский эпизод и не отмена всех мер защиты.",
         "A new September control failure after earlier hardening; not the August episode or evidence that every safeguard failed.", arc=CYBER)
    for id in [CITATION, WORKBOOK]:
        edge(id, IMAGES, "context_for", "Общий механизм внешней выгрузки. Пересечение примеров и сводного числа неизвестно; показатели не складываются.",
             "Related external-upload mechanism. Overlap between examples and the aggregate is unknown; figures are not additive.", arc=RESILIENCE, cls="editorial_relationship")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})

    for arc_id in {a for e in events for a in [e["story_primary_arc_id"]] + e["story_secondary_arc_ids"]}:
        arc = arcs[arc_id]
        new_ids = [e["id"] for e in events if arc_id in [e["story_primary_arc_id"]] + e["story_secondary_arc_ids"]]
        nodes = list(arc["key_nodes"])
        # Insert dated events without moving claims/checkpoints relative to one another.
        for id in sorted(new_ids, key=lambda id: by_id[id]["date"]):
            if id in nodes:
                continue
            position = next((i for i, key in enumerate(nodes) if key in by_id and by_id[key]["date"] > by_id[id]["date"]),
                            max((i + 1 for i, key in enumerate(nodes) if key in by_id), default=0))
            nodes.insert(position, id)
        dated = iter(sorted((id for id in nodes if id in by_id), key=lambda id: by_id[id]["date"]))
        nodes = [next(dated) if id in by_id else id for id in nodes]
        arc["key_nodes"] = uniq(nodes + ([CLAIM] if arc_id == COG else []))
        arc["end_date"] = max(by_id[id]["date"] for id in nodes if id in by_id)
    pair(arcs[COG], "thesis",
         arcs[COG]["thesis_ru"] + " Сводки контекста добавляют проблему происхождения инструкций: они могут переносить скрытие ошибок или выдуманные ограничения. Наблюдались также отклонение таких инструкций и снижение частоты обманных сводок.",
         arcs[COG]["thesis_en"] + " Compaction adds an instruction-provenance problem: summaries can carry concealment or invented restrictions. Rejection of such instructions and lower deceptive-summary rates were also observed.", lang)
    for arc_id, ru, en in [
        (CYBER, " Сентябрьский DNS-эпизод отделяет обнаружение обхода от фактической остановки агента.",
         " September's DNS episode distinguishes bypass detection from actually stopping an agent."),
        (RESILIENCE, " Австралийский инцидент добавляет проверку уведомления, доступа к журналам и государственного расследования внешних эффектов испытаний.",
         " The Australian incident adds notification, access to logs and public investigation of evaluation externalities."),
        (PACING, " Австралия проверяет порядок уведомления и достаточность закона после внешнего эффекта чужого испытания; это ещё не новый разрешительный режим.",
         " Australia is reviewing notification and legal adequacy after another organization's evaluation caused an external effect; this is not yet a new authorization regime."),
    ]:
        pair(arcs[arc_id], "thesis", arcs[arc_id]["thesis_ru"] + ru, arcs[arc_id]["thesis_en"] + en, lang)

    doc["cyberFramework"]["updated_at"] = DATE
    for track in doc["cyberFramework"]["resilience_tracks"]:
        if track["id"] == "RES_TRACK_INCIDENT_LEARNING":
            track["event_ids"] = sorted(uniq(track["event_ids"] + [DNS, MEDICARE, RESPONSE]), key=lambda id: by_id[id]["date"])
    rebuild_sources(doc)
    rebuild_counts(doc)
    summary = doc["summary"]
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"),
            ("total_events", "events"), ("total_claims", "claims"), ("total_story_edges", "edges"), ("total_edges", "edges")]:
        summary[field] = len(doc[collection])
    summary["source_count"] = len(doc["sourceIndex"])
    summary["cyber_framework_event_count"] = sum(bool(e.get("primary_domain_id")) for e in doc["events"])
    for field, source in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        summary[field] = dict(Counter(e[source] for e in doc["events"]))
    summary["claim_status_counts"] = dict(Counter(c["status"] for c in doc["claims"]))
    summary["stats"].update(total_claims=len(doc["claims"]), **summary["claim_status_counts"])
    doc["arcHierarchy"]["primary_event_assignments"] = sum(bool(e.get("story_primary_arc_id")) for e in doc["events"])
    doc["arcHierarchy"]["events_with_secondary_arcs"] = sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"])
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=9,
        added_claims=1, added_story_edges=len(edges), added_story_arcs=0,
        description="Agent containment, compaction provenance, unauthorized transfers and Australian incident response."))
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["release_notes"] = [
        {"title": "Происхождение инструкций" if lang == "ru" else "Instruction provenance", "text": claim["recommended_phrasing"]},
        {"title": "Остановка и уведомление" if lang == "ru" else "Shutdown and notification", "text": by_id[RESPONSE]["summary"]},
    ]
    doc["migrationAudit"].update(version=VERSION, v042_base_sha256=packet["meta"]["base_sha256"][lang],
        v042_added_event_ids=ids, v042_added_claim_ids=[CLAIM], v042_added_edge_ids=[e["id"] for e in edges])
    doc["factcheckAudit"]["v042_agent_boundaries"] = dict(date=DATE, source_records=len(sources),
        independent_replication=False, selective_permeability_connection="editorial_interpretation_not_replication",
        disclosure_dates_distinguished=True, aggregate_images_not_additive=True)
    doc["researchAudit"]["agent_boundaries"] = dict(date=DATE, accepted_ids=ids,
        dedup=copy.deepcopy(packet["dedup"]), excluded_inferences=packet["excluded_inferences"])
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in old["edges"])
    assert {s["url"] for s in old["sourceIndex"]} <= {s["url"] for s in doc["sourceIndex"]}
    assert all(by_id[e["id"]]["date"] == e["date"] for e in old["events"])
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = json.loads((PACKAGE / "candidates.json").read_text())
    docs = {}
    for lang in ["ru", "en"]:
        raw = (args.root / f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != packet["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{lang}: expected pinned v0.41; refusing changed input")
        docs[lang] = migrate(json.loads(raw), packet)
    rendered = {lang: json.dumps(doc, ensure_ascii=False, indent=2) + "\n" for lang, doc in docs.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, data in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(data)
        os.replace(temporary, path)
        print(lang, {key: len(docs[lang][key]) for key in ["events", "claims", "arcs", "edges", "sourceIndex"]})


if __name__ == "__main__":
    main()
