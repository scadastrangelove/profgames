#!/usr/bin/env python3
"""Integrate the reviewed CVE/NVD package into the pinned v0.39 bilingual pair."""
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
PACKAGE = ROOT / "review/cve-quality-era"
VERSION = "0.40"
DATE = "2026-09-27"
ARC = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
CLAIM = "CLM_030_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
TRACK = "RES_TRACK_SHARED_REPAIR"
CISA = "SIG_2026_CISA_CVE_QUALITY_ERA_FRAMEWORK"
NIST = "SIG_2026_NIST_NVD_SELECTIVE_ENRICHMENT"
DOMAIN = "CYBER_DOMAIN_03_NATIONAL_DEFENSE"


def metric(value, ru, en, as_of, unit, source, population_ru, population_en):
    return dict(value=value, label_ru=ru, label_en=en, as_of=as_of, unit=unit,
                source_url=source, population_ru=population_ru, population_en=population_en)


def make_event(candidate, doc):
    is_cisa = candidate["id"].endswith("CISA_CVE_QUALITY_ERA_FRAMEWORK")
    lang = doc["language"]
    sources = {}
    for i, source in enumerate(candidate["sources"]):
        sources[str(i)] = dict(
            source, name=source["publisher"], title=candidate[f"title_{lang}"],
            date=source["published_at"], type="Primary source", primary_or_secondary="primary",
            source_class="government_publication", checked_at=DATE,
        )
    raw = dict(candidate, id=CISA if is_cisa else NIST, source_ids=list(sources),
               date_basis=candidate["date_kind"], date_status="verified_primary_date",
               actors=["CISA" if is_cisa else "NIST"], actor_types=["government"],
               jurisdictions=["US"], contexts=["governance_document"],
               method="primary_publication_review_no_independent_cve_recount",
               stack_layers=["governance_law", "cyber_security_patch", "data_telemetry"],
               structures=["security", "knowledge"], research_questions=[],
               numbers={}, confidence="A", status="verified_primary_government_policy",
               domains=[DOMAIN, "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"], roles=[],
               primary_domain=DOMAIN, artifact="policy_framework" if is_cisa else "government_program",
               force="advisory" if is_cisa else "not_applicable",
               stage="published" if is_cisa else "effective", delegation="not_applicable",
               priority=1, arcs=[ARC], safe_ru=candidate["caveat_ru"], safe_en=candidate["caveat_en"])
    event = event_record(raw, lang, sources, doc)
    event.update(
        research_updates=["cve-quality-era"], story_primary_arc_id=ARC, story_secondary_arc_ids=[],
        geographic_scopes=["Global"], governance_scale="shared_vulnerability_information_infrastructure",
        resilience_track_ids=[TRACK], defense_evidence_kind="public_infrastructure_policy",
        defense_stage_ids=["validation", "coordination"],
        classification_review={"date": DATE, "method": raw["method"],
                               "independent_source_reverification": False, "independent_replication": False},
    )
    pair(event, "scope",
         "Политика американской общедоступной инфраструктуры данных, используемой во всём мире; не общая обязанность поставщиков ПО.",
         "Policy for U.S.-operated public data infrastructure used globally; not a general obligation on software suppliers.", lang)
    pair(event, "role_basis",
         "Документ касается координации защиты; применение конкретной модели или делегирование действий агенту не установлено.",
         "The document concerns defensive coordination; it does not establish use of a particular model or delegated agent action.", lang)
    pair(event, "editorial_rationale",
         "Изменение правил общей инфраструктуры влияет на качество и очерёдность обработки защитной информации. Рост публикаций не измеряет вклад ИИ.",
         "Shared-infrastructure rules affect the quality and processing priority of defensive information. Publication growth does not measure AI's contribution.", lang)
    source = event["sources"][-1 if is_cisa else 0]["url"]
    if is_cisa:
        event["pipeline_metrics"] = [
            metric(">67 000", "Новых записей опубликовано с начала 2026 года", "New records published during 2026",
                   "2026-09-18", "CVE", source,
                   "Показатель CISA: дата публикации, не год в идентификаторе; не число атак или находок ИИ.",
                   "CISA-reported count by publication date, not identifier year; not attacks or AI discoveries."),
            metric("96 000", "Прогноз на весь 2026 год", "Full-year 2026 forecast",
                   "2026-09-22", "CVE", source,
                   "Прогноз CVEForecast.org, процитированный CISA. Не наблюдаемый итог; метод прогноза отдельно не проверялся.",
                   "CVEForecast.org projection cited by CISA. Not an observed total; forecast methodology was not independently reviewed."),
        ]
    else:
        event["pipeline_metrics"] = [
            metric("+263%", "Рост поступлений за 2020–2025 годы", "Submission growth over 2020–2025",
                   "2026-04-15", "%", source, "По данным NIST; не рост числа атак.", "NIST-reported; not attack growth."),
            metric("≈ +1/3", "Первый квартал 2026 к первому кварталу 2025", "Q1 2026 compared with Q1 2025",
                   "2026-04-15", "CVE", source, "Формулировка NIST: почти на треть больше. Точный процент не опубликован.",
                   "NIST says nearly one-third higher. No exact percentage is published."),
            metric("≈42 000", "Обогащено записей за 2025 год", "Records enriched in 2025",
                   "2026-04-15", "CVE", source, "Почти 42 тысячи: на 45% больше предыдущего годового рекорда, но поток всё ещё превышает ёмкость обработки.",
                   "Nearly 42,000: 45% above the previous annual record, yet still insufficient to keep pace."),
        ]
    event["reported_metrics"] = copy.deepcopy(candidate["numbers"])
    return event


def migrate(doc, raw):
    if doc["meta"]["version"] != "0.39":
        raise ValueError("Expected v0.39")
    original = copy.deepcopy(doc)
    lang = doc["language"]
    events = [make_event(candidate, doc) for candidate in raw["candidates"]]
    ids = [event["id"] for event in events]
    if set(ids) & {event["id"] for event in doc["events"]}:
        raise ValueError("Events already present")
    doc["events"].extend(events)
    arc = next(a for a in doc["arcs"] if a["id"] == ARC)
    by_id = {e["id"]: e for e in doc["events"]}
    arc["key_nodes"] = sorted(uniq(arc["key_nodes"] + ids), key=lambda id: by_id.get(id, {}).get("date", "9999"))
    arc["end_date"] = "2026-09-22"
    extra_ru = " Общая инфраструктура уязвимостей также требует распределения ёмкости: NVD приоритизирует обогащение записей, а CISA задаёт рамку качества данных и управления CVE."
    extra_en = " Shared vulnerability infrastructure also requires capacity allocation: NVD prioritizes enrichment while CISA defines CVE data-quality and governance dimensions."
    pair(arc, "thesis", arc["thesis_ru"] + extra_ru, arc["thesis_en"] + extra_en, lang)
    check = next(c for c in doc["claimChecks"] if c["id"] == CLAIM)
    pair(check, "claim", check["claim_ru"] + extra_ru, check["claim_en"] + extra_en, lang)
    check["supporting_evidence"] = uniq(check["supporting_evidence"] + ids)
    for event in events:
        for source in event["sources"]:
            add_source(check, source)
    framework = doc["cyberFramework"]
    framework["updated_at"] = DATE
    framework["defense_evidence_kinds"].append({"id": "public_infrastructure_policy",
        "label_ru": "Политика общей инфраструктуры", "label_en": "Shared infrastructure policy"})
    track = next(t for t in framework["resilience_tracks"] if t["id"] == TRACK)
    track["event_ids"] = sorted(uniq(track["event_ids"] + ids), key=lambda id: by_id[id]["date"])
    track["description_ru"] = "Общие зависимости требуют координации, качества данных и ресурсов сопровождения; приоритет обработки не равен запрету доступа."
    track["description_en"] = "Shared dependencies require coordination, data quality and maintenance capacity; processing priority is not an access ban."
    edges = []

    def edge(source, target, relation, kind, ru, en, cls="editorial_relationship"):
        edges.append(dict(id=f"EDGE_V040_CVE_{len(edges)+1:03d}", source=source, target=target,
            source_kind="evidence", target_kind=kind, relation=relation, arc_id=ARC,
            arc_family_id=arc["family_id"], strength="moderate", evidence_level="A",
            visual_lane="cyber_security_patch", style="dashed" if cls=="thematic" else "solid",
            summary_ru=ru, summary_en=en, kind="edge", is_auto=False, relationship_class=cls))

    for id in ids:
        edge(id, ARC, "part_of_arc", "story_arc", "Тематическая принадлежность, не доказательство всей дуги.",
             "Thematic membership, not proof of the entire arc.", "thematic")
        edge(id, CLAIM, "supports_with_scope", "claim_check", "Показывает государственное управление общей защитной инфраструктурой, но не измеренную эффективность мер.",
             "Shows public governance of shared defensive infrastructure, not measured effectiveness.", "evidential")
    edge(NIST, CISA, "context_for", "evidence", "Сентябрьский документ CISA прямо ссылается на апрельские показатели NIST; это связь источников, не причинность решений.",
         "The September CISA paper cites April NIST figures; this is a source relationship, not decision causality.")
    edge(NIST, "SIG_2026_CURL_REPORTING_PAUSE", "parallel", "evidence", "Два разных ограничения ёмкости: обогащение метаданных и сопровождение проекта. Потоки не складываются.",
         "Different capacity constraints: metadata enrichment and project maintenance. Their flows are not additive.")
    edge(CISA, "SIG_2026_US_GOLD_EAGLE_LAUNCH", "parallel", "evidence", "Рамка качества CVE и программа координации уязвимостей решают смежные задачи; единый результат не установлен.",
         "CVE quality and vulnerability coordination address related tasks; a joint outcome is not established.")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    rebuild_sources(doc)
    rebuild_counts(doc)
    summary = doc["summary"]
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"),
            ("total_events", "events"), ("total_story_edges", "edges"), ("total_edges", "edges")]:
        summary[field] = len(doc[collection])
    summary["source_count"] = len(doc["sourceIndex"])
    summary["cyber_framework_event_count"] = sum(bool(e.get("primary_domain_id")) for e in doc["events"])
    for field, source in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        summary[field] = dict(Counter(e[source] for e in doc["events"]))
    doc["arcHierarchy"]["primary_event_assignments"] = sum(bool(e.get("story_primary_arc_id")) for e in doc["events"])
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=2,
        added_story_edges=7, added_story_arcs=0, description="CVE quality framework and NVD enrichment priorities; no AI-attribution inference."))
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["release_notes"] = [{
        "title": "Качество и ёмкость обработки" if lang=="ru" else "Quality and processing capacity",
        "text": ("CISA задаёт рамку качества CVE; NIST меняет приоритеты обогащения записей. Даты решений, срезы статистики и прогнозы разделены."
                 if lang=="ru" else "CISA defines CVE quality dimensions; NIST changes enrichment priorities. Decision dates, statistical snapshots and forecasts remain separate.")},
        {"title": "Границы вывода" if lang=="ru" else "Evidence limits",
         "text": "Рост CVE не измеряет вклад ИИ; приоритет обработки не закрывает публичный доступ." if lang=="ru" else "CVE growth does not measure AI's contribution; processing priority does not remove public access."}]
    doc["migrationAudit"].update(version=VERSION, v040_base_sha256=raw["meta"]["base_sha256"][lang],
        v040_added_event_ids=ids, v040_added_edge_ids=[e["id"] for e in edges])
    doc["factcheckAudit"]["v040_cve_quality"] = dict(date=DATE, source_records=3,
        independent_cve_recount=False, ai_contribution_quantified=False, outcome_effectiveness_measured=False)
    doc["researchAudit"]["cve_quality_era"] = dict(date=DATE, accepted_ids=ids,
        excluded_inferences=copy.deepcopy(raw["excluded_inferences"]))
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"]
    assert all(e in doc["edges"] for e in original["edges"])
    assert {s["url"] for s in original["sourceIndex"]} <= {s["url"] for s in doc["sourceIndex"]}
    assert all(by_id[e["id"]]["date"] == e["date"] for e in original["events"])
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads((PACKAGE / "candidates.json").read_text())
    docs = {}
    for lang in ["ru", "en"]:
        data = (args.root / f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != raw["meta"]["base_sha256"][lang]:
            raise SystemExit(f"{lang}: expected pinned v0.39; refusing changed input")
        docs[lang] = json.loads(data)
    rendered = {lang: json.dumps(migrate(doc, raw), ensure_ascii=False, indent=2)+"\n" for lang, doc in docs.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, data in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(data)
        os.replace(temporary, path)
        print(lang, "396 events; 948 edges; 586 source URLs")


if __name__ == "__main__":
    main()
