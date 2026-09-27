#!/usr/bin/env python3
"""Integrate reviewed AI-discovery evidence and Gates's oversight position into v0.40."""
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
PACKAGE = ROOT / "review/ai-discovery-gates"
DATE = "2026-09-27"
VERSION = "0.41"
ARC = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
CLAIM = "CLM_AI_ASSISTED_DISCOVERY_CONFIRMED_CONTRIBUTION"
CAPACITY = "CLM_VALID_FINDINGS_MAINTENANCE_CAPACITY"
AUTHORITY = "CLM_031_FRONTIER_PACING_AUTHORITY"
TRACK = "RES_TRACK_MAINTENANCE_CAPACITY"
REPAIR = "RES_TRACK_VERIFIED_REMEDIATION"
DOMAIN = "CYBER_DOMAIN_03_NATIONAL_DEFENSE"
GATES = "SIG_2026_GATES_MANDATORY_AI_OVERSIGHT_INTERVIEW"
VULNCHECK = "SIG_2026_VULNCHECK_AI_DISCOVERY_EXPLOITATION_COHORT"
EXISTING_SUPPORT = [
    "SIG_2026_MYTHOS_FIREFOX_271", "SIG_2026_CURL_HIGH_QUALITY_TRANSITION",
    "SIG_2026_CURL_822_SECURITY_RELEASE", "SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG",
    "SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES",
]
UNITS_RU = {"CVE": "CVE", "vulnerabilities": "уязвимости", "% submissions": "% сообщений",
    "merged fixes": "принятые исправления", "reviewed findings": "проверенные находки",
    "confirmed exploited": "подтверждённая эксплуатация", "security bugs fixed": "исправленные ошибки безопасности"}


def make_event(candidate, doc, sources):
    lang = doc["language"]
    policy = candidate.get("policy", False)
    observational = candidate.get("observational", False)
    raw = dict(candidate, actor_types=["person" if policy else "organization"],
        date_basis="publication_date", date_status="verified_primary_date",
        contexts=["governance_document" if policy else "ecosystem_measurement" if observational else "production"],
        method="published_source_review_no_independent_replication",
        stack_layers=["governance_law", "cyber_security_patch"] if policy else ["cyber_security_patch"],
        structures=["security", "knowledge"], research_questions=[], numbers={},
        status="verified_as_speech_not_as_fact" if policy else "verified_as_reported",
        domains=["CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"] if policy else [DOMAIN, "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        roles=[] if policy or observational else ["AI_ROLE_DEFENSIVE_TOOL"],
        primary_domain="CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE" if policy else DOMAIN,
        force="not_applicable", delegation="not_applicable", arcs=[PACING if policy else ARC],
        safe_ru=candidate["summary_ru"], safe_en=candidate["summary_en"])
    event = event_record(raw, lang, sources, doc)
    event.update(research_updates=["ai-discovery-gates"],
        story_primary_arc_id=raw["arcs"][0], story_secondary_arc_ids=[],
        geographic_scopes=["National" if policy else "Global"],
        governance_scale="public_oversight_position" if policy else "software_security_research_and_maintenance",
        classification_review={"date": DATE, "method": raw["method"],
                               "independent_source_reverification": False, "independent_replication": False},
        behavioral_status=["policy_response"] if policy else [],
    )
    pair(event, "role_basis",
         "Публичное предложение надзора; действия модели здесь не наблюдаются." if policy else
         "Анализ опубликованных находок; атрибуция атакующему ИИ не устанавливается." if observational else
         "Источник прямо описывает применение ИИ для поиска или проверки дефектов с участием специалистов.",
         "A public oversight proposal; no model actions are observed here." if policy else
         "Analysis of published findings; attacker AI use is not established." if observational else
         "The source explicitly describes AI use for discovery or validation with expert involvement.", lang)
    pair(event, "editorial_rationale",
         "Предложение обязательного надзора добавляет государство к спору о темпе развития и условиях доступа." if policy else
         "Связь метода поиска с результатом проверяется на уровне проекта или программы; единицы и границы выборки указаны отдельно.",
         "Proposed mandatory oversight brings government into the dispute over development pace and access conditions." if policy else
         "Discovery methods are linked to outcomes within projects or programs; units and cohort limits remain explicit.", lang)
    if policy:
        event["interview_recorded_at"] = "2026-09-23"
        event["policy_adopted"] = False
        event["forecast_probability_established"] = False
    else:
        event["resilience_track_ids"] = [TRACK] + ([REPAIR] if candidate.get("remediation_track") else [])
        event["defense_evidence_kind"] = candidate["defense_evidence_kind"]
        event["defense_stage_ids"] = candidate["stages"]
        event["pipeline_metrics"] = [dict(
            value=m["value"], unit=m["unit"], unit_ru=UNITS_RU[m["unit"]], unit_en=m["unit"],
            label_ru=m["label_ru"], label_en=m["label_en"],
            as_of=m["as_of"], source_url=sources[m["source"]]["url"],
            population_ru=m.get("population_ru", candidate["caveat_ru"]),
            population_en=m.get("population_en", candidate["caveat_en"]),
        ) for m in candidate["metrics"]]
    return event


def migrate(doc, packet):
    if doc["meta"]["version"] != "0.40":
        raise ValueError("Expected v0.40")
    original = copy.deepcopy(doc)
    lang = doc["language"]
    sources = {id: dict(s, type="Primary source" if s["primary_or_secondary"] == "primary" else "Media",
                       checked_at=DATE) for id, s in packet["sources"].items()}
    events = [make_event(candidate, doc, sources) for candidate in packet["events"]]
    ids = [e["id"] for e in events]
    assert not set(ids) & {e["id"] for e in doc["events"]}
    assert not {s["url"] for s in sources.values()} & {s["url"] for s in doc["sourceIndex"]}
    doc["events"].extend(events)
    by_id = {e["id"]: e for e in doc["events"]}
    arcs = {a["id"]: a for a in doc["arcs"]}
    claims = {c["id"]: c for c in doc["claims"]}
    supporting = [id for id in ids if id not in [GATES, VULNCHECK]] + EXISTING_SUPPORT
    claim = dict(id=CLAIM, kind="claim", status="verified", confidence="B", evidence_level="B",
        supporting_evidence=supporting, qualifying_evidence=[VULNCHECK], date_relevant="2026",
        stack_layer=["cyber_security_patch"], strange_structure=["security", "knowledge"],
        geography=["Global"], keywords=["AI-assisted discovery", "attribution", "CVE", "remediation"],
        arcIds=[ARC], arcFamilyIds=[arcs[ARC]["family_id"]], edgeIds=[], relationTypes=[], sources=[])
    pair(claim, "title", "ИИ уже увеличивает поток находок; доля во всём росте CVE не измерена",
         "AI already contributes to discovery growth; its share of total CVE growth is unmeasured", lang)
    pair(claim, "claim",
         "Применение ИИ к поиску уязвимостей даёт подтверждённые CVE и принятые исправления. Mozilla и curl подтверждают результаты; Wordfence фиксирует рост заявленного использования ИИ, Microsoft и Google перестраивают обработку находок. Данные OpenSSL дают атрибуцию конкретных раскрытий. Это подтверждает вклад ИИ в растущий поток, но не определяет его долю во всём приросте CVE.",
         "AI-assisted vulnerability research produces confirmed CVEs and accepted fixes. Mozilla and curl validate outcomes; Wordfence tracks increased reported AI use, while Microsoft and Google adapt their processing pipelines. OpenSSL data attributes specific disclosures. This establishes AI's contribution to a growing flow, without quantifying its share of the overall CVE increase.", lang)
    pair(claim, "caveats", [
        "Неполная публичная атрибуция задаёт нижнюю границу наблюдаемого вклада, а не доказывает его малость.",
        "Исходные исследования пересекаются: свод METR и карточки проектов нельзя складывать.",
        "Больше находок не означает автоматически большую вероятность эксплуатации или отраслевой перевес атакующих."], [
        "Incomplete public attribution is a lower bound on observed contribution, not evidence that the actual contribution is negligible.",
        "The studies overlap: METR's synthesis and individual project records must not be summed.",
        "More findings do not automatically imply greater exploitation likelihood or an industry-wide attacker advantage."], lang)
    pair(claim, "recommended_phrasing",
         "ИИ — подтверждённый фактор роста находок в ряде проектов и программ. Его вклад в общий прирост CVE пока не выражен надёжной отраслевой долей.",
         "AI is a confirmed contributor to discovery growth in multiple projects and programs. No reliable industry-wide share of overall CVE growth has yet been established.", lang)
    pair(claim, "safe_wording", claim["recommended_phrasing_ru"], claim["recommended_phrasing_en"], lang)
    for id in supporting + [VULNCHECK]:
        for source in by_id[id].get("sources", []):
            if isinstance(source, dict) and source.get("url"):
                add_source(claim, source)
    doc["claims"].append(claim)
    capacity = claims[CAPACITY]
    capacity_support = ["SIG_2026_CURL_AI_FIXES_MYTHOS_REVIEW", "SIG_2026_WORDFENCE_AI_REPORTING_SHARE"]
    capacity_qualify = ["SIG_2026_WINDOWS_MDASH_DISCOVERY_CAPACITY", "SIG_2026_CHROME_AI_SECURITY_FIX_THROUGHPUT"]
    capacity["supporting_evidence"] = uniq(capacity["supporting_evidence"] + capacity_support)
    capacity["qualifying_evidence"] = uniq(capacity["qualifying_evidence"] + capacity_qualify)
    pair(capacity, "claim",
         "В ряде проектов поток подтверждённых находок требует больше ресурсов сопровождения: это видно по паузе curl и очереди Linux netdev. ИИ увеличивает предложение находок, но проверка, назначение ответственного, исправление и установка остаются отдельной работой. Microsoft и Chrome показывают также способность наращивать обработку и выпуск; общий дефицит по всей отрасли не измерен.",
         "In some projects, validated findings require more maintenance capacity, as shown by curl's pause and the Linux netdev queue. AI increases discovery supply, while validation, ownership, patching and deployment remain distinct work. Microsoft and Chrome also show processing and release capacity expanding; an industry-wide shortfall is not measured.", lang)
    pair(capacity, "recommended_phrasing",
         "Поток качественных находок создаёт дополнительную инженерную нагрузку. В одних проектах возникает очередь, в других расширяют проверку и выпуск исправлений.",
         "A larger flow of valid findings creates additional engineering work. Some projects develop queues; others expand validation and release capacity.", lang)
    pair(capacity, "safe_wording", capacity["recommended_phrasing_ru"], capacity["recommended_phrasing_en"], lang)
    authority = next(c for c in doc["claimChecks"] if c["id"] == AUTHORITY)
    authority["supporting_evidence"] = uniq(authority["supporting_evidence"] + [GATES])
    for source in by_id[GATES]["sources"]:
        add_source(authority, source)
    pair(authority, "claim", authority["claim_ru"] + " Сентябрьское интервью Гейтса добавляет публичное требование обязательного государственного надзора, но не новый действующий режим.",
         authority["claim_en"] + " Gates's September interview adds a public demand for mandatory government oversight, not a new operational regime.", lang)
    for arc_id in [ARC, PACING]:
        arc = arcs[arc_id]
        new_ids = [e["id"] for e in events if e["story_primary_arc_id"] == arc_id]
        # Preserve existing claim/checkpoint positions while inserting dated events.
        nodes = list(arc["key_nodes"])
        for id in sorted(new_ids, key=lambda id: by_id[id]["date"]):
            later = next((i for i, key in enumerate(nodes) if key in by_id and by_id[key]["date"] > by_id[id]["date"]), None)
            position = later if later is not None else max((i + 1 for i, key in enumerate(nodes) if key in by_id), default=0)
            nodes.insert(position, id)
        arc["key_nodes"] = uniq(nodes + ([CLAIM] if arc_id == ARC else []))
        arc["end_date"] = max(by_id[id]["date"] for id in arc["key_nodes"] if id in by_id)
    pair(arcs[ARC], "thesis",
         "Киберустойчивость связывает безопасность ИИ-систем, управление возможностями моделей, защитную инфраструктуру, отраслевую готовность и независимость решений. ИИ уже приносит подтверждённые находки; способность проверить и устранить их зависит от ресурсов проектов и общих служб. Исправления Chrome и Firefox, очереди curl и Linux, приоритеты NVD и рамка качества CVE показывают разные участки этого процесса.",
         "Cyber resilience connects AI-system security, model-capability governance, defensive infrastructure, sector readiness and independent decisions. AI already produces validated findings; processing and remediation depend on project and shared-service capacity. Chrome and Firefox fixes, curl and Linux queues, NVD priorities and the CVE quality framework show different parts of this process.", lang)
    pair(arcs[PACING], "thesis", arcs[PACING]["thesis_ru"] + " Призыв Гейтса к обязательному надзору показывает отдельную позицию: не только добровольные паузы лабораторий, но и публично устанавливаемые правила мониторинга.",
         arcs[PACING]["thesis_en"] + " Gates's call for mandatory oversight adds a distinct position: not only voluntary lab pauses, but publicly defined monitoring requirements.", lang)
    framework = doc["cyberFramework"]
    framework["updated_at"] = DATE
    framework["defense_evidence_kinds"].append({"id": "research_measurement",
        "label_ru": "Исследовательское измерение", "label_en": "Research measurement"})
    for track in framework["resilience_tracks"]:
        track["event_ids"] = sorted(uniq(track["event_ids"] + [e["id"] for e in events if track["id"] in e.get("resilience_track_ids", [])]), key=lambda id: by_id[id]["date"])
        if track["id"] == TRACK:
            track["claim_ids"] = [CLAIM, CAPACITY]
            track["description_ru"] = "Подтверждённый вклад ИИ в находки, рост потока и нагрузка на сопровождение. Метод поиска, проверка, выпуск и эксплуатация учитываются отдельно."
            track["description_en"] = "Confirmed AI contributions, growing discovery flow and maintenance demands. Discovery method, validation, release and exploitation are measured separately."
    edges = []

    def edge(source, target, relation, kind, ru, en, arc_id=ARC, source_kind="evidence", cls="evidential"):
        edges.append(dict(id=f"EDGE_V041_DISCOVERY_{len(edges)+1:03d}", source=source, target=target,
            source_kind=source_kind, target_kind=kind, relation=relation, arc_id=arc_id,
            arc_family_id=arcs[arc_id]["family_id"], strength="moderate", evidence_level="B",
            visual_lane="governance_law" if arc_id == PACING else "cyber_security_patch",
            style="dashed" if cls == "thematic" else "solid", summary_ru=ru, summary_en=en,
            kind="edge", is_auto=False, relationship_class=cls))

    for event in events:
        edge(event["id"], event["story_primary_arc_id"], "part_of_arc", "story_arc",
             "Тематическая принадлежность, не доказательство всей дуги.", "Thematic membership, not proof of the entire arc.",
             arc_id=event["story_primary_arc_id"], cls="thematic")
    for id in supporting:
        edge(id, CLAIM, "supports_with_scope", "claim",
             "Свидетельство вклада ИИ в пределах описанного проекта или программы; показатели разных публикаций не складываются.",
             "Evidence of AI contribution within the described project or program; figures across publications are not additive.")
    edge(VULNCHECK, CLAIM, "qualifies", "claim", "Рост находок не устанавливает повышенную вероятность эксплуатации; наблюдение ограничено срезом и задержкой обнаружения.",
         "Discovery growth does not establish higher exploitation likelihood; follow-up and detection lag limit the observation.")
    edge(CLAIM, ARC, "supports_arc", "story_arc", "Подтверждённый рост находок объясняет часть задач защитного цикла, не результат всех мер.",
         "Confirmed discovery growth motivates parts of the defensive lifecycle, not the effectiveness of every measure.", source_kind="claim")
    edge(CLAIM, CAPACITY, "qualifies", "claim", "Рост предложения находок объясняет нагрузку, но сам по себе не доказывает превышение ёмкости каждого проекта.",
         "Growing discovery supply explains demand, but alone does not prove every project's capacity is exceeded.", source_kind="claim")
    for id in capacity_support:
        edge(id, CAPACITY, "supports_with_scope", "claim", "Рост потока и объёма проверки; не самостоятельное доказательство очереди или отраслевого дефицита.",
             "Increased flow and review work; not standalone proof of a backlog or industry-wide shortfall.")
    for id in capacity_qualify:
        edge(id, CAPACITY, "qualifies", "claim", "Обработка и выпуск исправлений тоже масштабируются: ограничение не одинаково для всех проектов.",
             "Processing and fix releases also scale: constraints are not uniform across projects.")
    edge(GATES, AUTHORITY, "supports_with_scope", "claim_check", "Публичное требование государственных правил; не свидетельство принятия закона.",
         "A public demand for government rules; not evidence of enacted law.", arc_id=PACING)
    for source, target, ru, en in [
        ("SIG_2026_FIREFOX_CLAUDE_22_CVES", "SIG_2026_MYTHOS_FIREFOX_271", "Разные мартовский и апрельский результаты Mozilla; не общая сумма.", "Separate March and April Mozilla outcomes, not an additive total."),
        ("SIG_2026_CURL_HIGH_QUALITY_TRANSITION", "SIG_2026_CURL_AI_FIXES_MYTHOS_REVIEW", "Апрельская смена качества и майская оценка исправлений описывают разные срезы одного проекта.", "April's quality transition and May's fix assessment describe different snapshots of one project."),
        ("SIG_2026_CURL_AI_FIXES_MYTHOS_REVIEW", "SIG_2026_CURL_821_RELEASE_CAPACITY", "Оценка накопленных результатов предшествует июньскому выпуску; пересечение исправлений не исключено.", "The cumulative assessment precedes June's release; fixes may overlap."),
    ]:
        edge(source, target, "context_for", "evidence", ru, en, cls="editorial_relationship")
    edge("SIG_2026_GATES_AI_TRANSITION_INSTITUTIONS_ESSAY", GATES, "context_for", "evidence",
         "Августовское эссе и сентябрьское интервью: разные публикации, во второй конкретнее требование обязательного надзора.",
         "Separate August essay and September interview; the latter makes mandatory oversight more explicit.", arc_id=PACING, cls="editorial_relationship")
    edge(GATES, "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL", "parallel", "evidence",
         "Сопоставимые позиции о надзоре, но не единая программа и не свидетельство согласованного замедления.",
         "Related oversight positions, not a joint program or evidence of coordinated slowing.", arc_id=PACING, cls="editorial_relationship")
    edge(CLAIM, "SIG_2026_CISA_CVE_QUALITY_ERA_FRAMEWORK", "context_for", "evidence",
         "Данные о методе поиска дополняют общий счётчик CVE, не заменяя его причинным разложением.",
         "Discovery-method evidence complements aggregate CVE counts without providing a causal decomposition.", source_kind="claim", cls="editorial_relationship")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
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
    doc["arcHierarchy"]["primary_event_assignments"] = sum(bool(e.get("story_primary_arc_id")) for e in doc["events"])
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(events),
        added_claims=1, added_story_edges=len(edges), added_story_arcs=0,
        description="Confirmed AI discovery contribution, differentiated metrics and Gates's mandatory-oversight position."))
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["release_notes"] = [
        {"title": "Подтверждённый вклад ИИ" if lang == "ru" else "Confirmed AI contribution",
         "text": claim["recommended_phrasing"]},
        {"title": "Государственный надзор" if lang == "ru" else "Public oversight",
         "text": by_id[GATES]["summary"]},
    ]
    doc["migrationAudit"].update(version=VERSION, v041_base_sha256=packet["meta"]["base_sha256"][lang],
        v041_added_event_ids=ids, v041_added_claim_ids=[CLAIM], v041_added_edge_ids=[e["id"] for e in edges])
    doc["factcheckAudit"]["v041_discovery_and_gates"] = dict(date=DATE, source_records=len(sources),
        ai_contribution_confirmed_in_named_projects=True, global_cve_growth_share_quantified=False,
        independent_aggregate_recount=False, gates_statement_not_adopted_policy=True)
    doc["researchAudit"]["ai_discovery_and_gates"] = dict(date=DATE, accepted_ids=ids,
        dedup=copy.deepcopy(packet["dedup"]), excluded_inferences=packet["excluded_inferences"])
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in original["edges"])
    assert {s["url"] for s in original["sourceIndex"]} <= {s["url"] for s in doc["sourceIndex"]}
    assert all(by_id[e["id"]]["date"] == e["date"] for e in original["events"])
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = json.loads((PACKAGE / "candidates.json").read_text())
    docs = {}
    for lang in ["ru", "en"]:
        data = (args.root / f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != packet["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{lang}: expected pinned v0.40; refusing changed input")
        docs[lang] = migrate(json.loads(data), packet)
    rendered = {lang: json.dumps(doc, ensure_ascii=False, indent=2) + "\n" for lang, doc in docs.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, data in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(data)
        os.replace(temporary, path)
        print(lang, {field: len(docs[lang][field]) for field in ["events", "claims", "arcs", "edges", "sourceIndex"]})


if __name__ == "__main__":
    main()
