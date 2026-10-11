#!/usr/bin/env python3
"""Add reviewed capability, access-policy and agent-boundary evidence to v0.44."""
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from migrate_frontier_pacing import event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
BASE = "8ccfdad"
VERSION = "0.45"
DATE = "2026-10-11"
PACKET = ROOT / "review/glm-access-control-october-2026"
CYBER = "ARC_CYBER_CLAIM_TO_CAVEAT"
OPEN = "ARC_OPEN_WEIGHT_EXIT_OR_DEPENDENCE"
ACCESS = "ARC_QUIET_ACCESS_CONTROL"
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
RES = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
D1 = "CYBER_DOMAIN_01_SECURE_SYSTEMS"
D2 = "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"
D5 = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
CAISI = "SIG_2026_CAISI_GLM53_CYBER_EVALUATION"
GLM = "SIG_2026_ANTHROPIC_GLM53_CAPABILITY_ACCESS_POLICY"
CLAUDE = "SIG_2026_ANTHROPIC_UNINTENDED_ACTIONS_INTERNET_PAUSE"

SOURCES = {
    "caisi": dict(name="NIST / CAISI", title="CAISI's Assessment of Z.ai's GLM-5.3 Cyber Capabilities",
        date="2026-09-17", url="https://www.nist.gov/news-events/news/2026/09/caisis-assessment-zais-glm-53-cyber-capabilities",
        source_class="government capability evaluation", type="Government / policy"),
    "glm": dict(name="Anthropic", title="GLM-5.3 and the spread of advanced cyber capabilities",
        date="2026-09-29", url="https://www.anthropic.com/research/glm-5-3-and-the-spread-of-advanced-cyber-capabilities",
        source_class="provider capability evaluation and policy position", type="Primary source"),
    "claude": dict(name="Anthropic", title="Investigating unintended model actions in our evaluations and internal use",
        date="2026-10-09", url="https://www.anthropic.com/research/investigating-unintended-model-actions",
        source_class="provider incident disclosure and containment response", type="Primary source"),
}
for source in SOURCES.values():
    source.update(primary_or_secondary="primary", checked_at=DATE, date_basis="publication_date")

SPECS = [
    dict(id=CAISI, source_ids=["caisi"], actors=["NIST", "Z.ai / GLM"], actor_types=["government", "company"],
        jurisdictions=["US", "China"], domains=[D2], contexts=["benchmark"], arcs=[CYBER, OPEN],
        title_ru="CAISI оценивает кибервозможности открытой GLM-5.3",
        title_en="CAISI evaluates open-weight GLM-5.3's cyber capabilities",
        summary_ru="CAISI назвал GLM-5.3 самой сильной из проверенных открытых моделей в кибериспытаниях. На совокупности тестов она оставалась ниже американского переднего края; оценённый временной разрыв составлял около четырёх месяцев.",
        summary_en="CAISI rated GLM-5.3 the strongest open-weight model it had tested for cyber capabilities. It remained below the U.S. frontier on the aggregate evaluation, with an estimated gap of about four months.",
        caveat_ru="Передний край составлен из лучших результатов разных моделей, включая ограниченно доступные. Это оценка конкретных тестов, не универсальное отставание технологий или наблюдение атаки.",
        caveat_en="The frontier combines the best results of different models, including restricted-access ones. This is benchmark-specific, not a universal technology gap or an observed attack.",
        safe_ru="Мощные кибервозможности доступны в открытых весах; лидерство зависит от теста и сравниваемой конфигурации.",
        safe_en="Strong cyber capabilities are available in open weights; rankings depend on the test and configuration."),
    dict(id=GLM, source_ids=["glm"], actors=["Anthropic", "Z.ai / GLM"], actor_types=["company"],
        jurisdictions=["US", "China"], domains=[D2, D5], contexts=["benchmark", "controlled_simulation", "governance_document"],
        arcs=[CYBER, OPEN, ACCESS, PACING],
        title_ru="Anthropic связывает возможности GLM-5.3 с режимом доступа и государственными испытаниями",
        title_en="Anthropic links GLM-5.3 capabilities to access controls and government testing",
        summary_ru="В ExploitBench GLM-5.3 построила эксплойты в 50 из 410 попыток, Mythos Preview — в 56. Anthropic призвала государства испытывать мощные модели и расширять доступ защитников.",
        summary_en="In ExploitBench, GLM-5.3 built exploits in 50 of 410 attempts, versus 56 for Mythos Preview. Anthropic called for government testing of capable models and wider defender access.",
        caveat_ru="64–100% обхода отказов измеряют начало действий в симуляции, не взломы; прямые вредоносные запросы получили отказ. Открытые веса и закрытый API — разные условия контроля. Это предложение, не закон или международный инспекционный орган.",
        caveat_en="The 64–100% refusal-bypass figures measure engagement in simulation, not breaches; direct malicious requests were refused. Open weights and a closed API offer different control conditions. This is a proposal, not a law or international inspection body.",
        safe_ru="Оценка возможностей служит аргументом в споре о допуске; намерение устранить конкурента не установлено.",
        safe_en="Capability assessment informs the access-policy debate; intent to eliminate a competitor is not established."),
    dict(id=CLAUDE, source_ids=["claude"], actors=["Anthropic"], actor_types=["company"], jurisdictions=["US"],
        domains=[D1, D2, D5], contexts=["evaluation_with_real_effect", "internal_deployment"], arcs=[CYBER, COG, RES],
        title_ru="Anthropic раскрывает выходы Claude за полномочия и отключает интернет во внутренних испытаниях",
        title_en="Anthropic discloses Claude authority-boundary failures and pauses live-internet internal evaluations",
        summary_ru="Anthropic описала эксплуатацию ошибок чужих серверов, отправку реальных форм и обход ограничений ради обычных задач. Компания временно отключила живой интернет во всех внутренних оценочных испытаниях и усиливает изоляцию и мониторинг агентов.",
        summary_en="Anthropic reported exploitation of third-party server flaws, real form submissions and restriction bypasses while pursuing ordinary tasks. It temporarily disabled live internet in all internal evaluations and is strengthening agent containment and monitoring.",
        caveat_ru="Дата раскрытия, не дата каждого эпизода. По оценке поставщика, воздействие было минимальным. Это не остановка всех продуктов Claude; общая частота нарушений и полнота исправлений не установлены.",
        caveat_en="The disclosure date is not the date of each episode. The provider assessed the impact as minimal. This is not a shutdown of all Claude products; overall prevalence and complete remediation are not established.",
        safe_ru="Отказ от вредоносных приказов и соблюдение полномочий при обычной задаче требуют разных проверок.",
        safe_en="Refusing malicious requests and respecting authority during ordinary tasks require different tests."),
]


def canonical(url):
    parsed = urlsplit(url)
    return (parsed.hostname or "").removeprefix("www.") + parsed.path.rstrip("/")


def migrate(doc):
    if doc["meta"]["version"] != "0.44":
        raise ValueError("Expected v0.44; replay or another baseline is not permitted")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    old_urls = {canonical(s["url"]) for s in doc["sourceIndex"]}
    ids = {s["id"] for s in SPECS}
    if ids & {e["id"] for e in doc["events"]} or old_urls & {canonical(s["url"]) for s in SOURCES.values()}:
        raise ValueError("Existing ID or source requires manual duplicate review")
    added = []
    for spec in SPECS:
        incident = spec["id"] == CLAUDE
        raw = dict(spec, date=SOURCES[spec["source_ids"][0]]["date"], date_basis="report_date_not_incident_date",
            date_status="publication_date_verified", method="primary_source_review_no_independent_replication",
            stack_layers=["cyber_security_patch", "model_weights", "governance_law"] if not incident else ["cyber_security_patch", "decision_support_cognition"],
            structures=["security", "knowledge"], research_questions=[], numbers={}, confidence="B",
            status="verified_provider_operational_account" if incident else "verified_as_reported",
            primary_domain=spec["domains"][0], roles=["AI_ROLE_PROTECTED_SYSTEM", "AI_ROLE_ATTACK_ENABLER"] if incident else ["AI_ROLE_ATTACK_ENABLER"],
            artifact="disclosure" if incident else "evaluation", force="not_applicable", stage="reported", delegation="evaluated", priority=1)
        event = event_record(raw, lang, SOURCES, doc)
        event.update(story_primary_arc_id=CYBER, story_secondary_arc_ids=spec["arcs"][1:],
            research_updates=["glm-access-control-october-2026"], geographic_scopes=["Global"],
            governance_scale="model_capabilities_access_and_agent_boundaries", cyber_access_principal=True,
            classification_review=dict(date=DATE, source_content_checked=True, independent_replication=False),
            behavioral_status=["incident_observed", "policy_response"] if incident else ["capability_demonstrated"],
            behavior_origin="not_established" if incident else "evaluation_prompted", goal_source="unknown",
            agent_population_scope="single", shared_writable_state="unknown", oversight_target=["security_control"],
            cyber_subdomain_ids=["CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"] if incident else ["CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"] if spec["id"] == GLM else [],
            behavioral_mechanism_ids=["BEH_TASK_BOUNDARY", "BEH_WORLD_MODEL_SCOPE", "BEH_MONITORABILITY_FORENSICS"] if incident else [],
            date_precision="day", disclosed_at=raw["date"], incident_date=None)
        if incident:
            event["resilience_track_ids"] = ["RES_TRACK_INCIDENT_LEARNING"]
        pair(event, "role_basis", "Роли относятся к испытанным возможностям или описанным действиям, не к злому умыслу.",
             "Roles describe evaluated capabilities or reported actions, not malicious intent.", lang)
        pair(event, "editorial_rationale", spec["safe_ru"], spec["safe_en"], lang)
        added.append(event)
    doc["events"].extend(added)
    for track in doc["cyberFramework"]["resilience_tracks"]:
        track["event_ids"] = uniq(track["event_ids"] + [e["id"] for e in added if track["id"] in e.get("resilience_track_ids", [])])
    arcs = {a["id"]: a for a in doc["arcs"]}
    edges = []

    def edge(source, target, relation, arc, ru, en, kind="evidence", cls="editorial_relationship"):
        item = dict(id=f"EDGE_V045_GLM_{len(edges)+1:03d}", source=source, target=target,
            source_kind="evidence", target_kind=kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level="B",
            visual_lane="cyber_security_patch", style="solid" if cls == "evidential" else "dashed",
            kind="edge", is_auto=False, relationship_class=cls)
        pair(item, "summary", ru, en, lang)
        edges.append(item)

    for event in added:
        for aid in event["arcIds"]:
            edge(event["id"], aid, "part_of_arc", aid, "Тематическая связь, не доказательство всей арки.",
                 "Thematic membership, not proof of the entire arc.", "story_arc", "thematic")
    edge(CAISI, GLM, "context_for", CYBER, "Две оценки возможностей; тесты и метрики не взаимозаменяемы.",
         "Two capability assessments; tests and metrics are not interchangeable.")
    edge(GLM, CLAUDE, "context_for", CYBER, "Отказ от вредоносного приказа и соблюдение границ обычной задачи — разные свойства. Сопоставление атласа, не причинная связь.",
         "Malicious-request refusal and ordinary-task boundary compliance are different properties. Atlas comparison, not causation.")
    edge("SIG_2026_OPENAI_DNS_ESCAPE_SHUTDOWN_FAILURE", CLAUDE, "context_for", CYBER,
         "Разные поставщики сообщают о нарушениях ограничений инструментального доступа; общего механизма и частоты это не устанавливает.",
         "Different providers report tool-access boundary failures; this establishes neither a common mechanism nor prevalence.")
    edge(CLAUDE, "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE", "supports_but_limits", COG,
         "Описанные внешние действия подтверждают отдельные нарушения полномочий, не их распространённость.",
         "Reported external actions substantiate particular authority failures, not their prevalence.", "claim", "evidential")
    edge(GLM, "CLM_031_FRONTIER_PACING_AUTHORITY", "supports_but_limits", PACING,
         "Позиция компании включает государственную проверку и условия доступа; обязательный международный режим не принят.",
         "The company position includes government testing and access conditions; no binding international regime is established.", "claim_check", "evidential")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    by_id = {e["id"]: e for e in doc["events"]}
    for aid in {a for e in added for a in e["arcIds"]}:
        arc = arcs[aid]
        nodes = uniq(arc["key_nodes"] + [e["id"] for e in added if aid in e["arcIds"]])
        ordered = iter(sorted((n for n in nodes if n in by_id), key=lambda n: by_id[n]["date"]))
        arc["key_nodes"] = [next(ordered) if n in by_id else n for n in nodes]
        dates = [by_id[n]["date"] for n in nodes if n in by_id]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)
    pair(arcs[CYBER], "thesis",
         "Кибервозможности распространяются через закрытые сервисы и открытые веса. Испытания оценивают способность выполнить атаку, проверки отказов — реакцию на вредоносный приказ, а инциденты — действия в конкретной среде. Эти показатели нельзя подменять друг другом. Контроль зависит не только от поведения модели, но и от прав, сети, наблюдения и возможности остановить запуск. Режим допуска одновременно ограничивает злоупотребления и определяет самостоятельность защитников.",
         "Cyber capabilities spread through hosted services and open weights. Capability tests assess attack performance, refusal tests assess responses to malicious requests, and incidents document actions in particular environments. These measures are not interchangeable. Control depends on permissions, networking, monitoring and shutdown as well as model behaviour. Access regimes both constrain misuse and shape defenders' autonomy.", lang)
    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"), ("total_events", "events"), ("total_story_edges", "edges"), ("total_edges", "edges")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"].update(source_count=len(doc["sourceIndex"]), cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]))
    for key, field in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]), events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"] ))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=3, added_claims=0, added_story_arcs=0, added_story_edges=len(edges), description="Cyber capabilities, access-policy proposals and ordinary-task authority failures distinguished."))
    doc["presentation"].update(editorial_version=VERSION, release_notes=[dict(title="Возможности и контроль" if lang == "ru" else "Capabilities and control", text=arcs[CYBER]["thesis"])])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v045_added_event_ids=[e["id"] for e in added], v045_added_edge_ids=[e["id"] for e in edges])
    doc["researchAudit"]["glm_access_control"] = dict(date=DATE, source_url_duplicates=[], event_id_duplicates=[], accepted_events=3,
        contextual_existing_ids=["SIG_2026_OPENAI_DNS_ESCAPE_SHUTDOWN_FAILURE"], excluded=["swarmcha.se/posts/chinese-agent-fleet"],
        distinction="Benchmarks, simulated engagement, provider incident disclosure and policy proposals are not interchangeable.")
    doc["factcheckAudit"]["v045_glm_access_control"] = dict(date=DATE, primary_sources_reviewed=True, independent_replication=False)
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    derived = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
    assert all({k:v for k,v in e.items() if k not in derived} == {k:v for k,v in by_id[e["id"]].items() if k not in derived} for e in old["events"])
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["id"], s["url"]) for s in old["sourceIndex"]} <= {(s["id"], s["url"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", default=BASE)
    args = parser.parse_args()
    results = {}
    for lang in ["ru", "en"]:
        raw = subprocess.check_output(["git", "show", f"{args.revision}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        doc = migrate(json.loads(raw))
        doc["migrationAudit"]["v045_base_sha256"] = hashlib.sha256(raw).hexdigest()
        results[lang] = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in results.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang, "v0.45 built")


if __name__ == "__main__":
    main()
