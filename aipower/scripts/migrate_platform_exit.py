#!/usr/bin/env python3
"""Strengthen the UK Palantir record and add NATO's dated readiness milestone."""
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
BASE = "ca3775f"
VERSION = "0.46"
DATE = "2026-10-24"
PACKET = ROOT / "review/platform-exit-october-2026"
UK = "SIG_2026_PALANTIR_UK_MOD_240M"
NATO = "SIG_2026_NATO_MAVEN_FTOC_MULTIMODEL"
PURCHASE = "SIG_2025_PALANTIR_NATO_MSS"
PAL = "ARC_PALANTIR_DECISION_OS"
PARENT = "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION"
D5 = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
LOCK = "CLM_017_PALANTIR_VENDOR_LOCK_IN"
ALLIES = "CLM_018_PALANTIR_ALLIED_DEPENDENCY"
MITIGATION = "CLM_026_DECISION_SOVEREIGNTY_MITIGATION"

SOURCES = {
    "notice": dict(name="UK Ministry of Defence / Sell2Wales", title="MOD Palantir Enterprise Agreement: direct-award justification",
        date="2025-12-18", url="https://www.sell2wales.gov.wales/search/show/search_view.aspx?ID=DEC572475&catID=",
        source_class="official procurement transparency notice", verification_method="full_notice_reviewed"),
    "original": dict(name="UK Ministry of Defence / Find a Tender", title="MOD Palantir Enterprise Agreement: UK5 notice 083858-2025",
        date="2025-12-17", url="https://www.find-tender.service.gov.uk/Notice/083858-2025",
        source_class="official procurement transparency notice", verification_method="indexed_metadata_and_official_Sell2Wales_mirror",
        same_document_as="https://www.sell2wales.gov.wales/search/show/search_view.aspx?ID=DEC572475&catID="),
    "signed": dict(name="UK Ministry of Defence / UK Parliament", title="Written answer 113372: Palantir agreement signed on 30 December 2025",
        date="2026-02-24", url="https://questions-statements.parliament.uk/written-questions/detail/2026-02-12/113372",
        source_class="ministerial written answer", verification_method="full_answer_reviewed"),
    "nato": dict(name="NATO / Joint Warfare Centre", title="NATO Maven Smart System Achieves Full Technical Operational Capability",
        date="2026-08-12", url="https://www.jwc.nato.int/article/maven-achieves-ftoc/",
        source_class="official operational milestone announcement", verification_method="full_article_reviewed"),
}
for source in SOURCES.values():
    source.update(type="Government / policy", primary_or_secondary="primary", checked_at=DATE, date_basis="publication_date")

UK_TEXT = dict(
    title_ru="Минобороны Великобритании продлевает Palantir: смена платформы требует перестройки и повторной аккредитации",
    title_en="UK MoD renews Palantir: switching requires rebuilding and security reaccreditation",
    summary_ru="Минобороны подписало соглашение на £240,6 млн 30 декабря 2025 года. Прямую закупку оно обосновало лицензируемой архитектурой Palantir: замена потребует перестройки, повторной аккредитации, переобучения и нарушит операции и совместимость с союзниками.",
    summary_en="MoD signed a £240.6m agreement on 30 December 2025. It justified direct award by Palantir's licensed architecture: replacement would require rebuilding, security reaccreditation and retraining, disrupting operations and allied interoperability.",
    caveat_ru="Это обоснование заказчика, не независимая оценка стоимости выхода. Сумма договора не равна уже произведённым расходам. Документ не устанавливает владение данными или право поставщика отключать систему.",
    caveat_en="This is the buyer's rationale, not an independent estimate of exit costs. Contract value is not expenditure already incurred. The notice establishes neither data ownership nor a supplier right to shut down the system.",
    safe_ru="Заказчик прямо признаёт технические и организационные издержки смены поставщика.",
    safe_en="The buyer explicitly acknowledges technical and organisational costs of switching supplier.")

NATO_TEXT = dict(
    title_ru="Maven в НАТО: техническая готовность и разные модели внутри одной платформы",
    title_en="NATO Maven: technical readiness and multiple models within one platform",
    summary_ru="По сообщению НАТО от 12 августа, Maven достигла полной технической эксплуатационной готовности 22 июня 2026 года. В публикации также названы аккредитация для закрытой сети и поддержка моделей Mistral и Meta.",
    summary_en="NATO's 12 August announcement dates Maven's full technical operational capability to 22 June 2026. It also reports classified-network accreditation and support for Mistral and Meta models.",
    caveat_ru="Дата аккредитации отдельно не указана. Поддержка разных моделей не доказывает лёгкую замену всей платформы, одинаковую работоспособность моделей или развёртывание во всех штабах. Удалённое отключение и контроль США над решениями союзников не установлены.",
    caveat_en="The accreditation date is not specified. Multi-model support establishes neither easy platform replacement, model parity nor deployment at every headquarters. Remote shutdown and U.S. control over allied decisions are not established.",
    safe_ru="Разные модели могут работать внутри одной платформы; переносимость всей системы требует отдельной проверки.",
    safe_en="Different models can operate within one platform; portability of the whole system requires separate verification.")


def migrate(doc):
    if doc["meta"]["version"] != "0.45":
        raise ValueError("Expected v0.45; migration replay is not permitted")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    events = {e["id"]: e for e in doc["events"]}
    if NATO in events or {s["url"] for s in SOURCES.values()} & {s["url"] for s in doc["sourceIndex"]}:
        raise ValueError("Existing event or source requires duplicate review")
    uk = events[UK]
    old_url = uk["url"]
    for sid in ["signed", "notice", "original"]:
        add_source(uk, SOURCES[sid])
    primary = SOURCES["signed"]
    uk.update(date="2025-12-30", year=2025, date_basis="contract_signed_date", date_status="exact", date_precision="day",
        source_date=primary["date"], url=primary["url"], source_name=primary["name"], source_type=primary["type"],
        source_type_raw=primary["source_class"], primary_or_secondary="primary", confidence="A", evidence_level="A",
        evidence_context=["governance_document"], evidence_method="buyer_procurement_rationale_and_ministerial_confirmation",
        cyber_domain_ids=[D5], primary_domain_id=D5, cyber_subdomain_ids=["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"],
        cyber_role_ids=["AI_ROLE_PROTECTED_SYSTEM"], artifact_kind="deployment", normative_force="contractual",
        implementation_stage="signed", delegated_authority="not_established", editorial_priority=1,
        classification_review=dict(date=DATE, source_content_checked=True, independent_switching_cost_measurement=False),
        status_update_date=DATE, research_updates=uniq(uk["research_updates"] + ["platform-exit-october-2026"]),
        procurement_ocid="ocds-h6vhtk-05f7e9", notice_publication_date="2025-12-17", notice_mirror_date="2025-12-18",
        contract_start_date="2026-04-01", contract_end_date="2029-03-31")
    uk["numbers_provenance"] = {
        "contract_value_gbp": primary["url"], "duration_years": SOURCES["notice"]["url"],
        "previous_contract_value_gbp": old_url,
    }
    for field in ["title", "summary", "caveat"]:
        pair(uk, field, UK_TEXT[field+"_ru"], UK_TEXT[field+"_en"], lang)
    pair(uk, "claim_supported", UK_TEXT["safe_ru"], UK_TEXT["safe_en"], lang)
    pair(uk, "safe_wording", UK_TEXT["safe_ru"], UK_TEXT["safe_en"], lang)
    pair(uk, "caveats", [UK_TEXT["caveat_ru"]], [UK_TEXT["caveat_en"]], lang)
    pair(uk, "claim_challenged", "Наличие нескольких моделей само по себе не доказывает возможность безболезненной смены платформы.",
         "Availability of multiple models does not itself establish low-cost platform replacement.", lang)
    pair(uk, "notes", "Декабрьское извещение описывало намерение заключить договор; подпись подтверждена последующим ответом министерства парламенту. Сумма прежнего договора сохранена из старого вторичного источника и заново не проверялась.",
         "The December notice described an intended award; signing is confirmed by the ministry's later parliamentary answer. The previous contract value is retained from the original secondary source and was not reverified.", lang)
    pair(uk, "corroboration_needed", "Условия выхода и переноса данных в договоре; независимая оценка затрат и проверка альтернатив.",
         "Contractual exit and data-portability terms; independent cost estimates and assessment of alternatives.", lang)
    pair(uk, "role_basis", "Зависимость оборонной системы поддержки решений от платформы; не киберинцидент и не доказательство автономного агента.",
         "Platform dependency in defence decision support; neither a cyber incident nor evidence of autonomous agency.", lang)
    pair(uk, "scope", "Британский оборонный договор; признанные заказчиком издержки замены системы аналитики.",
         "UK defence contract; buyer-acknowledged costs of replacing the analytics system.", lang)

    raw = dict(NATO_TEXT, id=NATO, date="2026-06-22", date_basis="operational_milestone_date", date_status="exact",
        source_ids=["nato"], actors=["NATO", "Palantir", "Mistral", "Meta"], actor_types=["military_security", "company"],
        jurisdictions=[], contexts=["production"], method="official_institutional_account_no_independent_performance_test",
        stack_layers=["decision_support_cognition", "data_telemetry", "model_weights"], structures=["security", "knowledge"],
        research_questions=["RQ2", "RQ5"], numbers={}, confidence="A", status="verified_as_reported", domains=[D5],
        roles=["AI_ROLE_PROTECTED_SYSTEM"], primary_domain=D5, artifact="deployment", force="not_applicable", stage="effective",
        delegation="not_established", priority=1, arcs=[PAL, PARENT])
    nato = event_record(raw, lang, SOURCES, doc)
    nato.update(story_primary_arc_id=PAL, story_secondary_arc_ids=[PARENT], institutional_scopes=["NATO"],
        geographic_scopes=["International"], actor_jurisdictions=["US", "France"],
        cyber_subdomain_ids=["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"],
        research_updates=["platform-exit-october-2026"], date_precision="day", security_accreditation_date=None,
        governance_scale="alliance_decision_infrastructure", behavioral_status=[],
        classification_review=dict(date=DATE, source_content_checked=True, independent_performance_test=False))
    pair(nato, "role_basis", "Защищаемый институциональный контур решений; наличие моделей не устанавливает делегирование им боевых полномочий.",
         "An institutional decision system to be secured; model integration does not establish delegated combat authority.", lang)
    pair(nato, "scope", "Система поддержки решений НАТО; техническая готовность, допуск в закрытую сеть и интеграция разных моделей.",
         "NATO decision support: technical readiness, classified-network accreditation and multi-model integration.", lang)
    pair(nato, "editorial_rationale", NATO_TEXT["safe_ru"], NATO_TEXT["safe_en"], lang)
    pair(nato, "corroboration_needed", "Условия переноса данных и рабочих процессов; испытания замены платформы и моделей.",
         "Data and workflow portability terms; tests of platform and model replacement.", lang)
    doc["events"].append(nato)
    events[NATO] = nato
    checks = {c["id"]: c for c in doc["claimChecks"]}
    previous_checks = {c["id"]: c for c in old["claimChecks"]}
    for cid in [LOCK, ALLIES, MITIGATION]:
        claim = checks[cid]
        selected = ["notice", "original", "signed"] if cid == LOCK else ["nato"]
        for sid in selected:
            add_source(claim, SOURCES[sid])
        claim["supporting_evidence"] = uniq(claim["supporting_evidence"] + ([UK] if cid == LOCK else [NATO]))
        pair(claim, "safe_wording", UK_TEXT["safe_ru"] if cid == LOCK else NATO_TEXT["safe_ru"],
             UK_TEXT["safe_en"] if cid == LOCK else NATO_TEXT["safe_en"], lang)
        if cid == MITIGATION:
            pair(claim, "safe_wording", previous_checks[cid]["safe_wording_ru"] + " " + NATO_TEXT["safe_ru"],
                 previous_checks[cid]["safe_wording_en"] + " " + NATO_TEXT["safe_en"], lang)
        pair(claim, "recommended_phrasing", claim["safe_wording_ru"], claim["safe_wording_en"], lang)
    for field in ["title", "claim"]:
        pair(checks[LOCK], field, "Британское Минобороны признаёт издержки смены Palantir; масштаб зависимости других заказчиков требует отдельной проверки.",
             "UK MoD acknowledges costs of replacing Palantir; the extent of other customers' dependency requires separate assessment.", lang)
        pair(checks[ALLIES], field, "Palantir встроена в инфраструктуру решений НАТО и британской обороны; это не устанавливает контроль США над решениями союзников.",
             "Palantir is embedded in NATO and UK defence decision infrastructure; this does not establish U.S. control over allied decisions.", lang)
    pair(checks[LOCK], "what_could_break_it", "Независимая проверка выявит сопоставимую альтернативу с низкими затратами перехода либо успешную конкурентную перезакупку без операционных потерь.",
         "Independent assessment identifies a comparable low-cost replacement, or competitive re-procurement succeeds without operational loss.", lang)

    arcs = {a["id"]: a for a in doc["arcs"]}
    edges = []
    def edge(source, target, relation, arc, ru, en, target_kind="evidence", cls="editorial_relationship"):
        item = dict(id=f"EDGE_V046_PLATFORM_{len(edges)+1:03d}", source=source, target=target, source_kind="evidence",
            target_kind=target_kind, relation=relation, arc_id=arc, arc_family_id=arcs[arc]["family_id"],
            strength="moderate", evidence_level="A", visual_lane="decision_support_cognition", kind="edge", is_auto=False,
            style="solid" if cls == "evidential" else "dashed", relationship_class=cls)
        pair(item, "summary", ru, en, lang)
        edges.append(item)
    for eid, aids in [(UK, [PAL]), (NATO, [PAL, PARENT])]:
        for aid in aids:
            edge(eid, aid, "part_of_arc", aid, "Тематическая принадлежность, не подтверждение всей арки.",
                 "Thematic membership, not proof of the entire arc.", "story_arc", "thematic")
    edge(PURCHASE, NATO, "updated_by", PAL, "Закупка 2025 года и техническая готовность 2026 года: разные стадии одной программы.",
         "The 2025 acquisition and 2026 technical readiness are different stages of one programme.")
    edge(UK, LOCK, "supports_with_scope", PAL, "Издержки перехода прямо названы заказчиком; независимого измерения нет.",
         "The buyer explicitly identifies switching costs; no independent measurement is provided.", "claim_check", "evidential")
    edge(NATO, ALLIES, "supports_with_scope", PAL, "Подтверждает институциональное внедрение, не внешний контроль над решениями.",
         "Supports institutional adoption, not external control over decisions.", "claim_check", "evidential")
    edge(NATO, MITIGATION, "supports_but_limits", PAL, "Разные модели внутри Maven не доказывают переносимость всей платформы.",
         "Multiple models within Maven do not establish portability of the whole platform.", "claim_check", "evidential")
    edge(UK, NATO, "context_for", PAL, "Сопоставление уровней зависимости: модель и платформа. Британская оценка затрат не переносится автоматически на НАТО.",
         "Comparison of dependency layers: model and platform. UK switching-cost claims cannot automatically be applied to NATO.")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    # Reposition the corrected UK date wherever it was already a checkpoint.
    for arc in doc["arcs"]:
        if arc["id"] in [PAL, PARENT]:
            arc["key_nodes"] = uniq(arc["key_nodes"] + [NATO])
        if UK not in arc.get("key_nodes", []) and NATO not in arc.get("key_nodes", []):
            continue
        nodes = arc["key_nodes"]
        ordered = iter(sorted((n for n in nodes if n in events), key=lambda n: events[n]["date"]))
        arc["key_nodes"] = [next(ordered) if n in events else n for n in nodes]
        dates = [events[n]["date"] for n in nodes if n in events]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)
    arc = arcs[PAL]
    pair(arc, "thesis", arc["thesis_ru"] + " Британское Минобороны прямо называет издержки смены Palantir. При этом НАТО сообщает о разных моделях внутри Maven: разнообразие моделей совместимо с зависимостью от платформы.",
         arc["thesis_en"] + " UK MoD explicitly names the costs of replacing Palantir. NATO meanwhile reports multiple models within Maven: model diversity is compatible with platform dependency.", lang)
    pair(arc, "safe_wording", arc["safe_wording_ru"] + " Разделять замену модели и выход из платформы; стоимость выхода из британского контура не измеряет стоимость выхода НАТО.",
         arc["safe_wording_en"] + " Distinguish model replacement from platform exit; UK exit-cost claims do not measure NATO's exit costs.", lang)
    pair(arc, "counterpoints", arc["counterpoints_ru"] + [UK_TEXT["caveat_ru"], NATO_TEXT["safe_ru"]],
         arc["counterpoints_en"] + [UK_TEXT["caveat_en"], NATO_TEXT["safe_en"]], lang)
    doc["palantirCase"]["critical_domains"]["military_and_alliance_c2"] = uniq(doc["palantirCase"]["critical_domains"]["military_and_alliance_c2"] + [NATO])
    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"), ("total_events", "events"), ("total_story_edges", "edges"), ("total_edges", "edges")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"].update(source_count=len(doc["sourceIndex"]), cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]))
    for key, field in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]), events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"] ))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=1, updated_evidence=1, added_claims=0,
        added_story_arcs=0, added_story_edges=len(edges), description="Buyer-acknowledged switching costs and NATO multi-model platform readiness; event dates separated from publications."))
    doc["presentation"].update(editorial_version=VERSION, release_notes=[dict(title="Модель и платформа" if lang == "ru" else "Model and platform", text=NATO_TEXT["safe_"+lang])])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v046_added_event_ids=[NATO], v046_updated_event_ids=[UK], v046_added_edge_ids=[e["id"] for e in edges])
    doc["researchAudit"]["platform_exit"] = dict(date=DATE, accepted_new_events=1, strengthened_existing_events=[UK],
        contextual_existing_ids=[PURCHASE], new_source_urls=4, independent_new_documents=3,
        dedupe_decision="UK contract enhanced in place; NATO acquisition and readiness are distinct stages, not independent programmes.",
        scope="Buyer rationale is not independent cost measurement; model diversity is not platform portability.")
    doc["factcheckAudit"]["v046_platform_exit"] = dict(date=DATE, source_content_reviewed=True,
        original_notice_direct_fetch="403; metadata and official mirror used", independent_switching_cost_measurement=False,
        date_corrections=[dict(id=UK, old_date=old["events"][[e["id"] for e in old["events"]].index(UK)]["date"], new_date=uk["date"], basis=primary["url"])])
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["id"], s["url"]) for s in old["sourceIndex"]} <= {(s["id"], s["url"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    for lang in ["ru", "en"]:
        raw = subprocess.check_output(["git", "show", f"{BASE}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        current = args.output / f"ai_power_storygraph_{lang}.json"
        if current.exists() and current.read_bytes() != raw:
            raise ValueError(f"Refusing to overwrite a modified baseline: {current}")
        doc = migrate(json.loads(raw))
        doc["migrationAudit"]["v046_base_sha256"] = hashlib.sha256(raw).hexdigest()
        results[lang] = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in results.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang, "v0.46 built")


if __name__ == "__main__":
    main()
