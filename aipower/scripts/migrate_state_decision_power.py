#!/usr/bin/env python3
"""Merge reviewed institutional AI evidence, preserving dates and existing records."""
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit

from migrate_frontier_pacing import event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "review/state-ai-decision-power-2026-10-04/candidates.json"
BASE = "0016ee8"
DATE = "2026-10-04"
VERSION = "0.44"
D = "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION"
E = "ARC_ENERGY_GRID_POLITICS"
G = "ARC_SOVEREIGN_FLOW_GATING"
F = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
DATA = "ARC_DATA_LICENSING_AS_INPUT_LAYER"
DOMAIN = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"

# Genesis has three separately dated institutional acts, not three discoveries.
SPECS = [
    dict(candidate="CAND_US_DETACHMENT_201", id="SIG_2025_US_ARMY_DETACHMENT_201", actors=["US Army", "Palantir", "Meta", "OpenAI", "Thinking Machines Lab"], country="US", artifact="government_program", stage="announced", priority=1,
        title_en="U.S. Army brings technology executives into its reserve advisory corps",
        summary_en="The Army announced Detachment 201 and the June 13 commissioning of Shyam Sankar, Andrew Bosworth, Kevin Weil and Bob McGrew as reserve lieutenant colonels. They would advise on technology projects while retaining commercial careers.",
        caveat_en="The announcement establishes designated advisory roles, not operational command, procurement authority or corruption.",
        safe_en="Technology suppliers gain an institutional advisory role in defining military technology needs."),
    dict(candidate="CAND_UK_CONSULT_PUBLIC_RESPONSES", id="SIG_2025_UK_CONSULT_PUBLIC_POLICY_PILOT", actors=["UK Department for Science, Innovation and Technology", "Scottish Government", "OpenAI"], country="UK", artifact="evaluation", stage="reported", priority=1,
        title_en="Consult groups public consultation responses before policy deliberation",
        summary_en="DSIT reported that Consult analysed more than 2,000 responses to a Scottish consultation on cosmetic procedures. Officials reviewed every response in this first trial. A July government release separately identified GPT-4o as the model used by Consult.",
        caveat_en="Accuracy and savings are developer-reported. Human review in the pilot proves neither manipulation nor the independence of every later decision. Planned removal of exhaustive manual reading is not verified deployment.",
        safe_en="A model mediates the information presented to policymakers without taking over the final policy decision."),
    dict(candidate="CAND_UK_RAID_PROCEDURAL_EXCEPTIONS", id="SIG_2026_UK_RAID_AI_DELIVERY_EXCEPTIONS", actors=["UK Ministry of Defence", "Rowden"], country="UK", artifact="government_program", stage="announced", priority=1,
        title_en="UK RAID taskforce receives procedural exceptions to accelerate military AI adoption",
        summary_en="The Rapid AI Delivery Taskforce reports to the Chief of the Defence Staff and initially targets intelligence analysis and military planning. The government states that it has exemptions from standard financial and procedural controls; Rowden is among its first partners.",
        caveat_en="The publication does not specify every exemption. It is not a blanket legal waiver or evidence of autonomous combat decisions; the announcement also retains oversight and assurance requirements.",
        safe_en="Military urgency changes institutional adoption procedures, without establishing unrestricted authority or combat outcomes."),
    dict(candidate="CAND_UAE_REGULATORY_INTELLIGENCE", id="SIG_2025_UAE_REGULATORY_INTELLIGENCE_OFFICE", actors=["Government of the United Arab Emirates"], country="UAE", artifact="government_program", stage="adopted", priority=2,
        title_en="UAE approves an AI-assisted Regulatory Intelligence Office",
        summary_en="The Cabinet approved an office and system connecting laws, judgments, procedures and public services to identify gaps and propose legislative changes.",
        caveat_en="Approval and intended functions are established. The source does not identify a model or supplier, prove autonomous enactment, or measure the promised 70 percent acceleration.",
        safe_en="AI is assigned a role in preparing legal recommendations; autonomous lawmaking is not established."),
    dict(candidate="CAND_US_AI_INFRASTRUCTURE_PERMITTING", id="SIG_2025_US_AI_INFRASTRUCTURE_PERMITTING_EO14318", actors=["US Government", "Donald Trump"], country="US", artifact="government_order", stage="effective", force="binding", cyber=False, priority=2,
        title_en="Executive Order 14318 directs accelerated support and permitting for AI infrastructure",
        summary_en="The order directs faster permitting, consideration of financial support and federal land access. Protecting national security is one route by which projects can qualify.",
        caveat_en="This is not a blanket exemption from environmental statutes or a judgment in the xAI case. Implementation remains subject to applicable law and available appropriations.",
        safe_en="Strategic importance is a criterion for preferential administrative treatment of AI infrastructure."),
    dict(candidate="CAND_US_GENESIS_CONTROLLED_SCIENCE_PLATFORM", id="SIG_2025_US_GENESIS_PLATFORM_ORDER", actors=["US Department of Energy", "US Government"], country="US", artifact="government_order", stage="directed", force="binding", priority=1, source_indices=[0],
        title_ru="Указ о Genesis объединяет научную ИИ-платформу с правилами допуска и интеллектуальных прав",
        summary_ru="Указ 14363 учреждает Genesis Mission и поручает создать American Science and Security Platform. Предусмотрены объединение вычислений, моделей и научных данных, проверка участников, правила доступа и распределение интеллектуальных прав.",
        caveat_ru="Учреждение программы и поручения не доказывают завершённое развёртывание платформы. Это не передача всех государственных данных компаниям или исключительное право одного поставщика.",
        safe_ru="Государственная научная ИИ-платформа проектируется вместе с условиями допуска, использования данных и прав на результаты.",
        title_en="Genesis order couples a scientific AI platform with access and intellectual-property rules",
        summary_en="Executive Order 14363 establishes Genesis Mission and directs creation of the American Science and Security Platform. It combines compute, models and scientific data with participant vetting, access controls and intellectual-property arrangements.",
        caveat_en="Establishment and directions do not prove completed deployment. The order does not transfer all government data to companies or grant one supplier exclusivity.",
        safe_en="A state scientific AI platform is designed together with admission, data-use and intellectual-property rules."),
    dict(candidate="CAND_US_GENESIS_CONTROLLED_SCIENCE_PLATFORM", id="SIG_2025_US_GENESIS_24_PARTNER_MOUS", date="2025-12-18", actors=["US Department of Energy", "OpenAI", "Anthropic", "Microsoft", "Palantir", "xAI"], country="US", artifact="memorandum", stage="signed", cyber=False, priority=2, source_indices=[1], arcs=[DATA,D],
        title_ru="DOE объявляет о 24 соглашениях о сотрудничестве в Genesis Mission",
        summary_ru="Министерство энергетики США сообщило о MOU с 24 организациями, включая поставщиков моделей, облаков и вычислительного оборудования. DOE указало, что продукты программы должны быть независимы от конкретной архитектуры.",
        caveat_ru="Соглашения о сотрудничестве не равны результатам исследований, эксклюзивным контрактам или безусловному доступу к государственным данным. Число партнёров относится к 18 декабря 2025 года.",
        safe_ru="Частные поставщики входят в государственную научную программу на уровне соглашений; эксклюзивность не установлена.",
        title_en="DOE announces 24 Genesis Mission collaboration agreements",
        summary_en="DOE announced MOUs with 24 organisations, including model, cloud and hardware suppliers, and stated that products for the programme would be architecture-agnostic.",
        caveat_en="Collaboration agreements are not research outcomes, exclusive contracts or unconditional access to government data. The partner count is dated December 18, 2025.",
        safe_en="Private suppliers join a state scientific programme through agreements; exclusivity is not established."),
    dict(candidate="CAND_US_GENESIS_CONTROLLED_SCIENCE_PLATFORM", id="SIG_2026_US_GENESIS_CONSORTIUM_LAUNCH", date="2026-02-09", actors=["US Department of Energy", "TechWerx", "RTI International"], country="US", artifact="cooperative_program", stage="launched", cyber=False, priority=2, source_indices=[2], arcs=[D,DATA],
        title_ru="Консорциум Genesis вводит рабочие группы участников по моделям, данным и инфраструктуре",
        summary_ru="DOE объявило запуск Genesis Mission Consortium под администрированием TechWerx. Консорциум должен координировать партнёрства и рабочие группы участников по моделям, данным, вычислениям и автоматизации.",
        caveat_ru="Организация сотрудничества не доказывает передачу государственных полномочий компаниям или достижение научных результатов. Это отдельная стадия ранее учреждённой программы, не новая независимая программа.",
        safe_ru="Участники научной ИИ-платформы получают организованный канал совместной разработки технических подходов.",
        title_en="Genesis consortium establishes member working groups for models, data and infrastructure",
        summary_en="DOE announced the Genesis Mission Consortium, administered by TechWerx, to coordinate partnerships and member-driven working groups on models, data, compute and automation.",
        caveat_en="Organising collaboration does not prove transfer of state authority to companies or achieved scientific outcomes. This is a later stage of the same programme, not an independent programme.",
        safe_en="Scientific AI platform participants receive an organised channel for co-developing technical approaches."),
    dict(candidate="CAND_UK_MODEL_ARENA", id="SIG_2025_UK_DEFENCE_AI_MODEL_ARENA", actors=["UK Ministry of Defence", "Advai", "National Security Strategic Investment Fund"], country="UK", artifact="evaluation", stage="announced", priority=2,
        title_en="UK Defence announces comparative AI evaluation before procurement",
        summary_en="DAIC announced a Model Arena developed with Advai and NSSIF, comparing performance, reliability, robustness and security against military requirements. The target launch was March 2026.",
        caveat_en="The announcement, not operational launch or reduced dependency, is verified. Vendor neutrality is an organiser claim; comparative evaluation is a mitigation mechanism, not proof of independence.",
        safe_en="State-defined comparative evaluation can limit supplier influence; the announced mitigation's effectiveness is unproven."),
    dict(candidate="CAND_ALBANIA_DIELLA_RESPONSIBILITY", id="SIG_2025_ALBANIA_DIELLA_PM_RESPONSIBILITY", actors=["Government of Albania", "Edi Rama"], country="Albania", artifact="government_order", stage="effective", force="binding", priority=2,
        title_en="Albania assigns responsibility for virtual Diella to the prime minister",
        summary_en="The official government composition published at the swearing-in assigns Prime Minister Edi Rama responsibility for establishing and operating virtual Diella.",
        caveat_en="This does not establish model legal personality, autonomous procurement decisions or fulfilled anticorruption promises. September 19 is the ceremony and publication date, not the first announcement or decree date.",
        safe_en="An AI interface is institutionalised while responsibility remains assigned to a human officeholder.")
]


def canonical_url(url):
    p = urlsplit(url)
    return (p.hostname or "").removeprefix("www.") + p.path.rstrip("/")


def duplicate_review(doc, packet):
    report = []
    old_urls = {canonical_url(s["url"]) for s in doc["sourceIndex"]}
    for spec in SPECS:
        candidate = next(c for c in packet["candidates"] if c["id"] == spec["candidate"])
        selected = [candidate["sources"][i] for i in spec.get("source_indices", range(len(candidate["sources"])))]
        matches = [s["url"] for s in selected if canonical_url(s["url"]) in old_urls]
        title = spec["title_en"]
        closest = sorted(((SequenceMatcher(None, title.lower(), e.get("title_en", e["title"]).lower()).ratio(), e["id"]) for e in doc["events"]), reverse=True)[:3]
        assert not matches, (spec["id"], "source already indexed; review before adding", matches)
        assert spec["id"] not in {e["id"] for e in doc["events"]}
        assert not any(spec.get("date", candidate["date"]) == e["date"] and title.casefold() == e.get("title_en", e["title"]).casefold() for e in doc["events"])
        report.append(dict(id=spec["id"], source_url_matches=matches, title_neighbours=[dict(id=i, similarity=round(s,3)) for s,i in closest],
            related_existing_ids=candidate["related_existing_ids"], decision="new_dated_event", candidate_id=candidate["id"]))
    return report


def migrate(doc, packet):
    if doc["meta"]["version"] != "0.43":
        raise ValueError("Expected v0.43; refusing replay or a different baseline")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    dedup = duplicate_review(doc, packet)
    arcs = {a["id"]: a for a in doc["arcs"]}
    added = []
    for spec in SPECS:
        c = next(c for c in packet["candidates"] if c["id"] == spec["candidate"])
        sources = {}
        for i in spec.get("source_indices", range(len(c["sources"]))):
            src = c["sources"][i]
            sources[str(i)] = dict(url=src["url"], date=src["published"], title=urlsplit(src["url"]).path.rstrip("/").split("/")[-1].replace("-", " "),
                name=urlsplit(src["url"]).hostname, type="Government / policy", source_class="official government publication", primary_or_secondary="primary")
        cyber = spec.get("cyber", True)
        companies = {"Palantir", "Meta", "OpenAI", "Thinking Machines Lab", "Rowden", "Microsoft", "Anthropic", "xAI", "Advai"}
        raw = dict(id=spec["id"], date=spec.get("date", c["date"]), date_basis="source_publication_date", date_status="exact",
            source_ids=list(sources), actors=spec["actors"], actor_types=["government"] + (["company"] if companies.intersection(spec["actors"]) else []),
            jurisdictions=[spec["country"]], contexts=["governance_document"], method="primary_source_review_not_outcome_replication",
            stack_layers=["governance_law", "decision_support_cognition"], structures=["knowledge", "production", "security"], research_questions=[], numbers={},
            status="verified_announcement" if spec["stage"] in {"announced", "adopted", "launched", "signed"} else "verified_as_reported" if spec["stage"] == "reported" else "verified",
            confidence="A", domains=[DOMAIN] if cyber else [], primary_domain=DOMAIN if cyber else "", roles=[],
            artifact=spec["artifact"], force=spec.get("force", "not_applicable"), stage=spec["stage"], delegation="not_applicable", priority=spec["priority"], arcs=spec.get("arcs", c["arc_ids"]))
        for field, key in [("title", "title_ru"), ("summary", "fact_ru"), ("caveat", "caveat_ru"), ("safe", "mechanism_ru")]:
            raw[field+"_ru"] = spec.get(field+"_ru", c[key])
            raw[field+"_en"] = spec[field+"_en"]
        if spec["candidate"] == "CAND_US_AI_INFRASTRUCTURE_PERMITTING":
            raw["stack_layers"] = ["energy_compute_chips", "cloud_inference", "governance_law", "finance_rent"]
        if "GENESIS" in spec["id"]:
            raw["stack_layers"] = ["data_telemetry", "model_weights", "energy_compute_chips", "governance_law"]
        if spec["id"] == "SIG_2025_UK_CONSULT_PUBLIC_POLICY_PILOT":
            raw.update(date_basis="report_date_not_incident_date", contexts=["controlled_evaluation"], numbers={"consultation_responses_more_than":2000})
        if spec["id"] == "SIG_2025_US_GENESIS_24_PARTNER_MOUS":
            raw["numbers"] = {"announced_partner_mous":24}
        event = event_record(raw, lang, sources, doc)
        event.update(story_primary_arc_id=raw["arcs"][0], story_secondary_arc_ids=raw["arcs"][1:],
            research_updates=["state-ai-decision-power-october-2026"], behavioral_status=[],
            cyber_subdomain_ids=["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"] if cyber else [],
            governance_scale="institutional_decisions_and_infrastructure", date_precision="day",
            classification_review=dict(date=DATE, source_content_checked=True, independent_replication=False, independent_source_reverification=False))
        if spec["id"] == "SIG_2025_UK_CONSULT_PUBLIC_POLICY_PILOT":
            event.update(incident_date=None, disclosed_at=raw["date"], supplier_identification_published_at="2025-07-21")
        if spec["id"] == "SIG_2025_UK_DEFENCE_AI_MODEL_ARENA":
            event.update(planned_launch_month="2026-03", operational_launch_verified=False)
        pair(event, "editorial_rationale", raw["safe_ru"], raw["safe_en"], lang)
        added.append(event)
    doc["events"].extend(added)
    edges = []

    def link(source, target, relation, arc, kind, ru, en, cls="editorial_relationship"):
        edge = dict(id=f"EDGE_V044_STATE_{len(edges)+1:03d}", source=source, target=target, source_kind="evidence", target_kind=kind,
            relation=relation, arc_id=arc, arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level="A",
            visual_lane="governance_law", style="solid" if cls == "evidential" else "dashed", kind="edge", is_auto=False, relationship_class=cls)
        pair(edge, "summary", ru, en, lang)
        edges.append(edge)

    for event in added:
        for arc in event["arcIds"]:
            link(event["id"], arc, "part_of_arc", arc, "story_arc", "Тематическая принадлежность, не доказательство всей дуги.", "Thematic membership, not proof of the whole arc.", "thematic")
        arena = event["id"] == "SIG_2025_UK_DEFENCE_AI_MODEL_ARENA"
        thesis = "THESIS_ACCESS_AS_POWER" if "GENESIS" in event["id"] else "THESIS_CORE" if event["id"].endswith("EO14318") else "THESIS_DECISION_SOVEREIGNTY"
        link(event["id"], thesis, "qualifies" if arena else "supports_with_scope", event["story_primary_arc_id"], "synthetic_thesis",
            event["safe_wording_ru"], event["safe_wording_en"], "evidential_qualification" if arena else "evidential")
    for source, target, arc, ru, en in [
        ("SIG_2025_US_ARMY_DETACHMENT_201", "SIG_2026_US_PROJECT_MERIDIAN_ANNOUNCEMENT", D, "Два разных канала участия поставщиков в военном технологическом консультировании; не одна программа.", "Two distinct channels of supplier participation in military technology advice; not one programme."),
        ("SIG_2025_US_AI_INFRASTRUCTURE_PERMITTING_EO14318", "SIG_2026_GROK_MAVEN_ENERGY_NATIONAL_SECURITY_FILING", E, "Общий инфраструктурный режим и конкретная судебная позиция используют аргумент безопасности; причинная связь не установлена.", "A general infrastructure regime and a specific litigation position invoke security; causation is not established."),
        ("SIG_2026_UK_RAID_AI_DELIVERY_EXCEPTIONS", "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS", F, "Сходные доктрины ускорения в разных юрисдикциях, не единый режим.", "Comparable acceleration doctrines in different jurisdictions, not a unified regime."),
        ("SIG_2025_US_GENESIS_PLATFORM_ORDER", "SIG_2025_US_GENESIS_24_PARTNER_MOUS", DATA, "Соглашения являются следующей стадией той же программы; не отдельным результатом исследований.", "Agreements are a later stage of the same programme, not a separate research outcome."),
        ("SIG_2025_US_GENESIS_24_PARTNER_MOUS", "SIG_2026_US_GENESIS_CONSORTIUM_LAUNCH", DATA, "Консорциум организует сотрудничество по той же программе; стадии не считаются независимыми программами.", "The consortium organises collaboration within the same programme; stages are not independent programmes.")]:
        link(source, target, "context_for", arc, "evidence", ru, en)
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    by_event = {e["id"]:e for e in doc["events"]}
    for aid in {a for e in added for a in e["arcIds"]}:
        arc = arcs[aid]
        nodes = uniq(arc["key_nodes"] + [e["id"] for e in added if aid in e["arcIds"]])
        ordered = iter(sorted((n for n in nodes if n in by_event), key=lambda n:by_event[n]["date"]))
        arc["key_nodes"] = [next(ordered) if n in by_event else n for n in nodes]
        dates = [by_event[n]["date"] for n in nodes if n in by_event]
        arc["start_date"] = min([arc["start_date"]]+dates)
        arc["end_date"] = max([arc["end_date"]]+dates)
    # Replace the affected synthesis rather than accumulating release notes in narrative prose.
    for aid, ru, en in [
        (D, "ИИ входит в институциональные решения через подготовку сведений, рабочие интерфейсы и консультативные роли поставщиков. Consult группирует обращения граждан; Detachment 201 и Meridian включают технологических руководителей в военное консультирование; ОАЭ планируют ИИ-подготовку правовых рекомендаций. Распределение власти зависит от проверки, правил закупки и человеческой ответственности: Model Arena и полномочия премьера по Diella показывают разные попытки сохранить эти границы.",
            "AI enters institutional decisions through information preparation, working interfaces and supplier advisory roles. Consult groups public responses; Detachment 201 and Meridian bring technology leaders into military advice; the UAE plans AI-assisted legal recommendations. Power depends on evaluation, procurement rules and human accountability: Model Arena and the prime minister's responsibility for Diella illustrate different attempts to retain these boundaries."),
        (E, "Энергия и подключение к сети ограничивают вычислительные мощности. Государства могут менять условия строительства ради стратегических целей: американский указ 14318 ускоряет разрешительные процедуры, а в споре xAI Минюст ссылается на военную зависимость от Grok. Указ и судебный довод не равны безусловному освобождению от экологических требований; ограничения сетей и местные конфликты сохраняют значение.",
            "Power and grid access constrain compute. States can alter construction conditions for strategic aims: U.S. Executive Order 14318 accelerates permitting, while DOJ invokes military reliance on Grok in the xAI dispute. Neither the order nor the litigation argument constitutes an unconditional environmental exemption; grid limits and local disputes still matter.")]:
        pair(arcs[aid], "thesis", ru, en, lang)
    doc["criticalDecisionUse"]["military_state_security"] = uniq(doc["criticalDecisionUse"]["military_state_security"] + [SPECS[i]["id"] for i in [0,2,8]])
    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items","events"),("total_timeline_items","events"),("total_events","events"),("total_story_edges","edges"),("total_edges","edges")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"].update(source_count=len(doc["sourceIndex"]), cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]))
    for key, field in [("by_status","status"),("event_status_counts","status"),("by_confidence","confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]), events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"]))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0,dict(version=VERSION,date=DATE,added_evidence=len(added),added_claims=0,added_story_arcs=0,added_story_edges=len(edges),description="State decision interfaces, supplier advisory roles, strategic infrastructure and public evaluation safeguards."))
    doc["presentation"].update(editorial_version=VERSION,release_notes=[dict(title="Государственные решения" if lang=="ru" else "State decisions", text="Внедрение, анонсы, предписания и ответственность разделены." if lang=="ru" else "Deployment, announcements, directions and accountability are distinguished.")])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION,v044_added_event_ids=[e["id"] for e in added],v044_added_edge_ids=[e["id"] for e in edges])
    doc["researchAudit"]["state_decision_power"] = dict(date=DATE,accepted_dossiers=8,accepted_events=len(added),dedup=dedup,held_topics=[x["topic"] for x in packet["follow_up"]])
    doc["factcheckAudit"]["v044_state_decision_power"] = dict(date=DATE,primary_sources_reviewed=True,independent_outcome_replication=False,genesis_milestones_not_independent_programmes=True)
    doc["connectivity"].update(edge_count=len(doc["edges"]),story_edges=len(doc["edges"]),last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"]
    links = {"edgeIds","arcIds","arcFamilyIds","relationTypes"}
    assert all({k:v for k,v in e.items() if k not in links} == {k:v for k,v in by_event[e["id"]].items() if k not in links} for e in old["events"])
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["url"],s["id"]) for s in old["sourceIndex"]} <= {(s["url"],s["id"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--revision",help="Read the baseline JSON from an existing Git revision")
    args=parser.parse_args()
    packet=json.loads(PACKET.read_text())
    results={}
    for lang in ["ru","en"]:
        raw=(subprocess.check_output(["git","show",f"{args.revision}:aipower/ai_power_storygraph_{lang}.json"],cwd=args.root)
             if args.revision else (args.root/f"ai_power_storygraph_{lang}.json").read_bytes())
        doc=migrate(json.loads(raw),packet)
        doc["migrationAudit"]["v044_base_sha256"]=hashlib.sha256(raw).hexdigest()
        results[lang]=json.dumps(doc,ensure_ascii=False,indent=2)+"\n"
    args.output.mkdir(parents=True,exist_ok=True)
    for lang,payload in results.items():
        path=args.output/f"ai_power_storygraph_{lang}.json"
        tmp=path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang,"v0.44 built")


if __name__ == "__main__":
    main()
