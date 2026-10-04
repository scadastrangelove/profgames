#!/usr/bin/env python3
"""Add the reviewed Grok consultation, court filing and Meridian announcement."""
import argparse
import copy
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-04"
VERSION = "0.43"
DECISION = "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
ENERGY = "ARC_ENERGY_GRID_POLITICS"
MAVEN = "ARC_PALANTIR_DECISION_OS"
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
DOMAIN = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
CHAT = "SIG_2025_TRUMP_GROK_MADURO_CONSULTATION_REPORTED"
COURT = "SIG_2026_GROK_MAVEN_ENERGY_NATIONAL_SECURITY_FILING"
MERIDIAN = "SIG_2026_US_PROJECT_MERIDIAN_ANNOUNCEMENT"

SOURCES = {
    "time": dict(title="What Trump Has Built", name="TIME", date="2026-10-01",
        url="https://time.com/article/2026/10/01/donald-trump-2026-interview/",
        type="Press / wire", source_class="unnamed eyewitness reporting", primary_or_secondary="secondary"),
    "doj": dict(title="United States motion for intervention and dismissal, NAACP v. X.AI, with Stanley declaration",
        name="U.S. Department of Justice", date="2026-06-15", url="https://www.justice.gov/opa/media/1446141/dl",
        type="Government / policy", source_class="court filing and official declaration", primary_or_secondary="primary"),
    "speech": dict(title="Hegseth Names Musk, Gingrich and Anduril's Luckey to Project Meridian",
        name="WSJ / Yahoo Finance", date="2026-09-30",
        url="https://finance.yahoo.com/video/hegseth-names-musk-gingrich-anduril-205400034.html",
        type="Primary source", source_class="recorded official speech and transcript", primary_or_secondary="primary"),
}

RECORDS = [
    dict(id=CHAT, date="2025-12", date_basis="reported_event_month", date_status="month_known_day_unknown",
        source_ids=["time"], actors=["Donald Trump", "Elon Musk", "xAI"], jurisdictions=["US", "Venezuela"],
        actor_types=["government", "company"], contexts=["production"], artifact="discussion", stage="reported",
        status="reported_unnamed_eyewitness", confidence="C", priority=1,
        arcs=[DECISION, COG], stack_layers=["decision_support_cognition", "model_weights"],
        title_ru="Time: Трамп спрашивал Grok о реакции на возможный захват Мадуро",
        title_en="TIME: Trump asked Grok about reactions to a possible Maduro capture",
        summary_ru="По рассказу неназванного очевидца журналу Time, в декабре 2025 года Трамп обсуждал с Grok реакцию венесуэльцев на возможный захват Мадуро. Техническая запись беседы не опубликована.",
        summary_en="An unnamed eyewitness told TIME that Trump consulted Grok in December 2025 about Venezuelans' reactions to a possible Maduro capture. No technical conversation record was published.",
        caveat_ru="Рассказ очевидца, не независимая запись. План операции и причинное влияние ответа на решение не установлены. Неизвестны версия, инструменты и инструкции; отсутствие публичного журнала не доказывает отсутствие внутреннего. Точный день встречи неизвестен.",
        caveat_en="An eyewitness account, not an independently available recording. Operational planning and a causal effect on the decision are not established. Version, tools and instructions are unknown; no public log does not mean no internal log. The meeting day is unknown.",
        safe_ru="Сообщение о консультации по политическим последствиям, не доказательство планирования операции моделью.",
        safe_en="A reported consultation about political consequences, not evidence of model-authored operational planning.",
        rationale_ru="Неформальный вход модельной оценки в обсуждение государственного решения. Влияние поставщика и доверие к ответу остаются вопросами анализа, не доказанным управлением решением.",
        rationale_en="An informal route for a model assessment into discussion of a state decision. Supplier influence and trust remain analytical questions, not demonstrated control of the decision."),
    dict(id=COURT, date="2026-06-15", date_basis="court_filing_date", date_status="exact",
        source_ids=["doj"], actors=["U.S. Department of Justice", "Chief Digital and Artificial Intelligence Office", "xAI", "NAACP"],
        jurisdictions=["US", "Iran"], actor_types=["government", "military_security", "company", "civil_society"],
        contexts=["governance_document"], artifact="memorandum", stage="published",
        status="verified_official_filing_operational_claim", confidence="A/B", priority=1,
        arcs=[ENERGY, MAVEN, DECISION],
        stack_layers=["energy_compute_chips", "cloud_inference", "decision_support_cognition", "governance_law"],
        title_ru="Минюст США ссылается на военное применение Grok в споре об энергоснабжении xAI",
        title_en="DOJ cites Grok military use in litigation over xAI's power supply",
        summary_ru="В ходатайстве от 15 июня Минюст просит прекратить экологический иск к xAI. Декларация Кэмерона Стэнли связывает Grok Gov с применением Maven в Epic Fury; военная зависимость приводится как аргумент против ограничения электроснабжения и вычислительных мощностей.",
        summary_en="In its June 15 motion, DOJ seeks dismissal of an environmental suit against xAI. Cameron Stanley's declaration links Grok Gov to Maven use in Epic Fury; military dependence is invoked against limits on power and compute capacity.",
        caveat_ru="Факт подачи документа подтверждён; результативность модели заявлена чиновником, а не независимо измерена. Это позиция стороны, не решение суда или экологическое исключение. Показатели кампании не измеряют число автономных решений и не складываются с прежней карточкой Epic Fury.",
        caveat_en="The filing is established; model effectiveness is an official assertion, not an independent measurement. This is a litigant's position, not a court ruling or environmental exemption. Campaign figures do not count autonomous decisions and are not additive with the existing Epic Fury record.",
        safe_ru="Военная зависимость от коммерческой модели используется в судебном аргументе в защиту её инфраструктуры.",
        safe_en="Military reliance on a commercial model is used in a legal argument defending its infrastructure.",
        rationale_ru="Связь безопасности, частных вычислений и энергетического регулирования. Документ одновременно раскрывает заявленное применение модели и политико-правовую защиту инфраструктуры.",
        rationale_en="A connection between security, private compute and energy regulation. The filing discloses claimed model use alongside political and legal protection of infrastructure."),
    dict(id=MERIDIAN, date="2026-09-30", date_basis="official_announcement_date", date_status="exact",
        source_ids=["speech"], actors=["U.S. Department of Defense", "Elon Musk", "Anduril", "Palmer Luckey", "Newt Gingrich"],
        jurisdictions=["US"], actor_types=["government", "military_security", "company"],
        contexts=["governance_document"], artifact="government_program", stage="announced",
        status="verified_announcement", confidence="A", priority=2,
        arcs=[DECISION, PACING], stack_layers=["governance_law", "decision_support_cognition"],
        title_ru="Project Meridian: представители технологических компаний участвуют в исследовании будущего войны",
        title_en="Project Meridian brings technology leaders into a study of future warfare",
        summary_ru="Хегсет объявил Project Meridian под руководством Эмила Майкла. Соруководители — Илон Маск, Палмер Лаки и Ньют Гингрич; выводы исследования должны быть представлены через 120 дней.",
        summary_en="Hegseth announced Project Meridian under Emil Michael, co-led by Elon Musk, Palmer Luckey and Newt Gingrich, with findings due within 120 days.",
        caveat_ru="Объявление исследования, не передача оперативного командования, контракт или состоявшееся внедрение. Участие поставщиков позволяет исследовать влияние на приоритеты, но само по себе не доказывает захват регулятора или коррупцию.",
        caveat_en="A study announcement, not transfer of operational command, a contract or completed deployment. Supplier participation raises questions about agenda-setting but does not itself establish regulatory capture or corruption.",
        safe_ru="Поставщики технологий получают формальную консультативную роль в обсуждении будущих военных потребностей.",
        safe_en="Technology suppliers gain a formal advisory role in examining future military needs.",
        rationale_ru="Не только поставка модели, но и участие поставщика в определении будущего спроса. Исследовательский мандат не равен полномочию принимать военные решения.",
        rationale_en="Beyond model supply, suppliers participate in defining future demand. A research mandate is not authority to make operational military decisions."),
]


def migrate(doc):
    if doc["meta"]["version"] != "0.42":
        raise ValueError("Expected v0.42; refusing replay or a different baseline")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    arcs = {a["id"]: a for a in doc["arcs"]}
    ids = [r["id"] for r in RECORDS]
    assert not set(ids) & {e["id"] for e in doc["events"]}
    for record in RECORDS:
        raw = dict(record, method="source_review_not_independent_operational_replication", structures=["security", "knowledge", "production"],
            research_questions=[], numbers={}, domains=[DOMAIN], primary_domain=DOMAIN,
            roles=[],
            force="not_applicable", delegation="not_established" if record["id"] == CHAT else "not_applicable")
        e = event_record(raw, lang, SOURCES, doc)
        e.update(research_updates=["grok-decision-power-october-2026"],
            story_primary_arc_id=raw["arcs"][0], story_secondary_arc_ids=raw["arcs"][1:],
            institutional_scopes=["national_security"], source_date_basis="publication_date",
            date_precision="month" if e["id"] == CHAT else "day",
            geographic_scopes=["Cross-border"] if len(raw["jurisdictions"]) > 1 else ["National"],
            actor_jurisdictions=["US"], governance_scale="state_decisions_and_private_ai_infrastructure",
            behavioral_status=[], cyber_subdomain_ids=["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"],
            classification_review=dict(date=DATE, method=raw["method"], independent_replication=False,
                independent_source_reverification=False, source_content_checked=True))
        pair(e, "editorial_rationale", raw["rationale_ru"], raw["rationale_en"], lang)
        if e["id"] == CHAT:
            e.update(incident_date=None, event_date_range={"start": "2025-12-01", "end": "2025-12-31"}, disclosed_at="2026-10-01")
        if e["id"] == COURT:
            e.update(operational_event_date=None, case_number="3:26-cv-00074-DMB-JMV",
                source_locator="Doc 59, pp. 1, 6; Exhibit A, Doc 58-1, paragraphs 5-10",
                numbers={"reported_munitions_over": 2000, "reported_distinct_targets": 2000, "reported_window_hours": 96},
                operational_claim_status="official_assertion_not_independent_measurement")
        if e["id"] == MERIDIAN:
            e["numbers"] = {"study_deadline_days": 120, "co_leads": 3}
        doc["events"].append(e)

    added = []
    def edge(source, target, relation, arc, kind, ru, en, cls="evidential", confidence="B"):
        item = dict(id=f"EDGE_V043_GROK_{len(added)+1:03d}", source=source, target=target,
            source_kind="evidence", target_kind=kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level=confidence,
            visual_lane="decision_support_cognition", style="solid" if cls == "evidential" else "dashed",
            kind="edge", is_auto=False, relationship_class=cls)
        pair(item, "summary", ru, en, lang)
        added.append(item)
    for raw in RECORDS:
        for arc in raw["arcs"]:
            edge(raw["id"], arc, "part_of_arc", arc, "story_arc", "Тематическая принадлежность, не доказательство всей дуги.",
                "Thematic membership, not proof of the entire arc.", "thematic", raw["confidence"])
        edge(raw["id"], "THESIS_DECISION_SOVEREIGNTY", "supports_with_scope", raw["arcs"][0], "synthetic_thesis",
            raw["safe_ru"], raw["safe_en"], confidence=raw["confidence"])
    edge(COURT, "THESIS_CORE", "supports_with_scope", ENERGY, "synthetic_thesis",
        "Национальная безопасность используется как довод в защите частной энергетической и вычислительной инфраструктуры; исход спора не установлен.",
        "National security is invoked to defend private energy and compute infrastructure; the dispute's outcome is not established.")
    edge(COURT, "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE", "context_for", MAVEN, "evidence",
        "Дополнительная атрибуция модели в той же кампании. Разные периоды наблюдения; показатели не складываются.",
        "Additional model attribution in the same campaign. Different observation windows; figures are not additive.", "editorial_relationship")
    doc["edges"].extend(added)
    attach_edge_links(doc, {e["id"] for e in added})
    events = {e["id"]: e for e in doc["events"]}
    for aid in {a for r in RECORDS for a in r["arcs"]}:
        arc = arcs[aid]
        nodes = uniq(arc["key_nodes"] + [r["id"] for r in RECORDS if aid in r["arcs"]])
        dated = iter(sorted((i for i in nodes if i in events), key=lambda i: events[i]["date"]))
        arc["key_nodes"] = [next(dated) if i in events else i for i in nodes]
        dates = [events[i]["date"] for i in nodes if i in events]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)
    for aid, ru, en in [
        (DECISION, " Доступ поставщика к обсуждению решений бывает неформальным и институциональным: от сообщаемой прессой беседы с моделью до объявленной консультативной роли в Project Meridian.",
            " Suppliers can enter decision discussions informally or institutionally: through a press-reported model consultation or an announced advisory role in Project Meridian."),
        (ENERGY, " В споре об энергоснабжении xAI Минюст США использовал зависимость военных от Grok как аргумент против прекращения работы инфраструктуры. Это судебная позиция, а не установленное исключение из экологических требований.",
            " In litigation over xAI's power supply, DOJ invoked military reliance on Grok against infrastructure shutdown. This is a litigation position, not an established environmental exemption."),
        (MAVEN, " Июньский судебный документ добавляет официальную атрибуцию Grok Gov внутри Maven; вклад конкретной модели в отдельные удары публично не измерен.",
            " A June court filing adds official attribution of Grok Gov within Maven; the model's contribution to individual strikes is not publicly measured."),
    ]:
        pair(arcs[aid], "thesis", arcs[aid].get("thesis_ru", arcs[aid].get("thesis", "")) + ru,
            arcs[aid].get("thesis_en", arcs[aid].get("thesis", "")) + en, lang)
    doc["criticalDecisionUse"]["military_state_security"] = uniq(doc["criticalDecisionUse"]["military_state_security"] + [CHAT, COURT, MERIDIAN])
    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"), ("total_events", "events"),
            ("total_story_edges", "edges"), ("total_edges", "edges")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"]["source_count"] = len(doc["sourceIndex"])
    doc["summary"]["cyber_framework_event_count"] = sum(bool(e.get("primary_domain_id")) for e in doc["events"])
    for field, source in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        doc["summary"][field] = dict(Counter(e[source] for e in doc["events"]))
    doc["arcHierarchy"]["primary_event_assignments"] = sum(bool(e.get("story_primary_arc_id")) for e in doc["events"])
    doc["arcHierarchy"]["events_with_secondary_arcs"] = sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"])
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=3,
        added_claims=0, added_story_arcs=0, added_story_edges=len(added),
        description="Reported Grok consultation, military reliance in energy litigation, and Project Meridian."))
    doc["presentation"]["editorial_version"] = VERSION
    doc["presentation"]["release_notes"] = [{"title": "Решения и инфраструктура" if lang == "ru" else "Decisions and infrastructure",
        "text": "Беседа с Grok, судебный аргумент о военной зависимости и Project Meridian отмечены раздельно." if lang == "ru" else
        "The Grok consultation, military-dependence litigation argument and Project Meridian are recorded separately."}]
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v043_added_event_ids=ids, v043_added_edge_ids=[e["id"] for e in added])
    doc["factcheckAudit"]["v043_grok_decision_power"] = dict(date=DATE, accepted_records=3,
        independent_replication=False, causality_from_consultation_established=False, autonomous_strikes_established=False,
        legal_filing_not_judgment=True, sources_checked=list(SOURCES.values()))
    doc["researchAudit"]["grok_decision_power"] = dict(date=DATE, accepted_ids=ids,
        dedup="Existing Epic Fury record retained; court filing adds model attribution and energy-litigation mechanism. Campaign totals are not additive.")
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    links = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
    assert all({k: v for k, v in e.items() if k not in links} == {k: v for k, v in events[e["id"]].items() if k not in links} for e in old["events"])
    assert all(e in doc["edges"] for e in old["edges"])
    assert {s["url"]: s["id"] for s in old["sourceIndex"]}.items() <= {s["url"]: s["id"] for s in doc["sourceIndex"]}.items()
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rendered = {}
    for lang in ["ru", "en"]:
        raw = (args.root / f"ai_power_storygraph_{lang}.json").read_bytes()
        doc = migrate(json.loads(raw))
        doc["migrationAudit"]["v043_base_sha256"] = hashlib.sha256(raw).hexdigest()
        rendered[lang] = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in rendered.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(payload)
        os.replace(temporary, path)
        print(lang, "v0.43: 3 events, 12 edges, 3 source URLs added")


if __name__ == "__main__":
    main()
