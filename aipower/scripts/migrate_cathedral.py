#!/usr/bin/env python3
"""Pinned v0.49 -> v0.50: Cathedral disclosure and a separate SI Force demand."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "review/cathedral-october-2026"
VERSION, DATE = "0.50", "2026-10-28"
BASE_HASH = {
    "ru": "1f0885538a6550016d719906c23259eee5df5835453f0d031a4c6b6bf64ae2aa",
    "en": "f1afc65ed7f9015a4fb392424af6610efa54c80d42a65cbc658c9f4cb59c57af",
}
RESILIENCE = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
CAPABILITY = "ARC_CYBER_CLAIM_TO_CAVEAT"
PACING = "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"
CATHEDRAL = "SIG_2026_CATHEDRAL_ANTHROPIC_THIRD_PARTY_ACCESS"
SI_FORCE = "SIG_2026_US_SI_FORCE_INCIDENT_NOTIFICATION_DEMAND"
DISCLOSURE = "SIG_2026_ANTHROPIC_UNINTENDED_ACTIONS_INTERNET_PAUSE"
CLAIM = "CLM_031_FRONTIER_PACING_AUTHORITY"
DOMAIN1 = "CYBER_DOMAIN_01_SECURE_SYSTEMS"
DOMAIN2 = "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"

SOURCE_ROWS = [
    ("post", "The Washington Post", "How an AI start-up founded by ex-DOGE staffers broke into Anthropic", "2026-10-26", "https://www.washingtonpost.com/technology/2026/10/26/researchers-cybersecurity-start-up-cathedral-got-inside-anthropic/", "original reporting; unpublished Cathedral draft and attributed company response", False),
    ("aa", "Anadolu Agency", "Months-old US startup accessed Anthropic's sensitive data in under 12 hours: Report", "2026-10-27", "https://m.aa.com.tr/en/world/months-old-us-startup-accessed-anthropic-s-sensitive-data-in-under-12-hours-report/4102515", "secondary coverage of the same Washington Post report; not independent corroboration", False),
    ("graham", "Logan Graham / Anthropic", "Corrections on the Cathedral incident and third-party dependencies", "2026-10-26", "https://x.com/logangraham/status/2114849047953670635", "named company representative; statement read through a mirror and The Decoder; direct X fetch returned 403", True),
    ("decoder", "The Decoder", "AI agents hacked Anthropic, maker of arguably the most capable AI models for cyberdefense", "2026-10-28", "https://the-decoder.com/ai-agents-hacked-anthropic-maker-of-arguably-the-most-capable-ai-models-for-cyberdefense/", "secondary reporting linking the named representative's statement; not independent technical replication", False),
    ("policy", "Anthropic", "Responsible Disclosure Policy", "2025-02-14", "https://www.anthropic.com/responsible-disclosure-policy", "public programme terms; specific Cathedral engagement permissions unavailable", True),
    ("axios", "Axios", "Exclusive: Anthropic breaches spark White House AI reporting mandate", "2026-10-09", "https://www.axios.com/2026/10/09/anthropic-ai-security-white-house", "official SI Force statement reproduced by publisher; no separate implementing instrument reviewed", False),
    ("anthropic", "Anthropic", "Investigating unintended model actions in our evaluations and internal use", "2026-10-09", "https://www.anthropic.com/research/investigating-unintended-model-actions", "provider disclosure underlying the earlier notification demand; not the Cathedral incident", True),
]
SOURCES = {key: dict(name=name, title=title, date=date, url=url, source_class=kind,
    type="Primary source" if primary else "Media / report",
    primary_or_secondary="primary" if primary else "secondary", checked_at=DATE,
    verification_method="source_account_reviewed; no_independent_replication")
    for key, name, title, date, url, kind, primary in SOURCE_ROWS}


def record(eid, date, sources, actors, title, summary, caveat, arcs, *, artifact,
           contexts, domains, roles, force="not_applicable", delegation="not_applicable"):
    return dict(id=eid, date=date, source_ids=sources, actors=actors,
        title_ru=title[0], title_en=title[1], summary_ru=summary[0], summary_en=summary[1],
        caveat_ru=caveat[0], caveat_en=caveat[1], safe_ru=summary[0], safe_en=summary[1],
        arcs=arcs, stack_layers=["cyber_security_patch", "governance_law", "data_telemetry"],
        structures=["security", "knowledge"], research_questions=["RQ5"], jurisdictions=["US"],
        actor_types=["company", "research"] if eid==CATHEDRAL else ["government", "company"],
        artifact=artifact, contexts=contexts, domains=domains, primary_domain=domains[0],
        roles=roles, force=force, stage="reported", delegation=delegation,
        date_basis="public_disclosure_date_incident_date_not_disclosed" if eid==CATHEDRAL else "publication_date",
        date_status="source_backed", confidence="B", status="verified_as_reported", priority=1,
        method="attributed_source_review; no_public_attack_trace; no_independent_replication", numbers={})


RECORDS = [
    record(CATHEDRAL, "2026-10-26", ["post", "aa", "graham", "decoder", "policy"], ["Cathedral", "Anthropic"],
        ("Cathedral получила доступ к бизнес-системам Anthropic через стороннее ПО",
         "Cathedral reached Anthropic business systems through third-party software"),
        ("Anthropic признала ограниченный доступ Cathedral к системам продаж, кадров и ИТ через стороннее ПО. Исследователи использовали ИИ-агентов; компания оспорила полноту раскрытия и соблюдение границ программы. Анонимный чиновник связал эпизод с риском иностранного шпионажа, что добавляет политический контекст, но не доказывает государственный заказ исследования.",
         "Anthropic acknowledged limited Cathedral access to sales, HR and IT systems through third-party software. Researchers used AI agents; the company disputed disclosure completeness and programme scope compliance. An anonymous official linked the episode to foreign-espionage risk, adding political context but not establishing a government-directed operation."),
        ("Дата карточки относится к публикации, не к началу доступа. Заявленные Cathedral менее 12 часов работы агентов не равны полной длительности: Логан Грэм сообщил о нескольких днях попыток и двух уязвимостях, из которых исследователи сообщили одну. Anthropic отрицает доступ к весам, коду и чатам клиентов; полный объём доступа спорен. Нет опубликованной трассы, версии модели и распределения решений между людьми и агентами: самостоятельный выход агента за полномочия не установлен. Стороннее ПО не обязательно означает взлом внутренних систем его разработчика. Публичная политика исключает системы третьих лиц; конкретные разрешения Cathedral неизвестны. Нарушение правил, уголовная квалификация и решение о вознаграждении не тождественны; умысел сокрытия и отказ в выплате не установлены. СМИ пересказывают один отчёт и заявления сторон, а не независимые технические проверки.",
         "The record dates publication, not initial access. Cathedral's claimed under-12-hour agent phase is not total duration: Logan Graham described several days of attempts and two vulnerabilities, only one reported by the researchers. Anthropic denies access to weights, code and customer chats; overall access remains disputed. No public trace, model version or human/agent decision breakdown establishes an autonomous authority-boundary failure. Third-party software does not necessarily mean the developer's internal systems were breached. Public policy excludes third-party systems; Cathedral's specific permissions are unknown. Programme compliance, criminal liability and bounty eligibility are distinct; intentional concealment and a denied payment are not established. Coverage repeats one report and party statements, not independent technical audits."),
        [RESILIENCE, CAPABILITY, PACING], artifact="disclosure", contexts=["evaluation_with_real_effect"],
        domains=[DOMAIN1, DOMAIN2], roles=["AI_ROLE_ATTACK_ENABLER", "AI_ROLE_PROTECTED_SYSTEM"], delegation="not_established"),
    record(SI_FORCE, "2026-10-09", ["axios", "anthropic"], ["US Government", "Anthropic"],
        ("SI Force потребовала сообщать об инцидентах с моделями и устранять последствия",
         "SI Force demanded model-incident notification and remediation"),
        ("SI Force заявила об обязательности уведомления и устранения последствий инцидентов с моделями.",
         "SI Force declared model-incident notification and remediation obligatory."),
        ("Это заявление власти, опубликованное Axios, а не установленный здесь новый закон. Правовое основание принуждения, санкции и исполнение не установлены. Anthropic отдельно описала действия своих моделей на внешних, в том числе государственных, сайтах. Это другой набор событий, не доступ Cathedral к самой Anthropic. Требование опубликовано 9 октября, до новости Cathedral 26 октября; причинная связь с Cathedral не установлена. Позднее уточнение Джорджии относится к одному эпизоду и сохранено в исходной карточке раскрытия.",
         "This is a government statement published by Axios, not a new statute established here. Enforcing authority, sanctions and implementation are not established. Anthropic separately described its models acting on external sites, including government sites. These are different events from Cathedral accessing Anthropic. The demand was published on October 9, before the October 26 Cathedral news; a causal link to Cathedral is not established. Georgia's later correction concerns one episode and remains in the original disclosure record."),
        [PACING, RESILIENCE], artifact="supervisory_communication", contexts=["governance_document"],
        domains=[DOMAIN2, DOMAIN1], roles=["AI_ROLE_PROTECTED_SYSTEM"], force="undetermined", delegation="control_requirement"),
]


def migrate(doc):
    if doc["meta"]["version"] != "0.49":
        raise ValueError("Expected v0.49; refusing repeated or out-of-order migration")
    old, lang = copy.deepcopy(doc), doc["language"]
    events, arcs = ({x["id"]:x for x in doc[k]} for k in ["events", "arcs"])
    for raw in RECORDS:
        if raw["id"] in events:
            raise ValueError("Duplicate event: " + raw["id"])
        event = event_record(raw, lang, SOURCES, doc)
        event.update(date_precision="day", story_primary_arc_id=raw["arcs"][0],
            story_secondary_arc_ids=raw["arcs"][1:], research_updates=["cathedral-october-2026"],
            behavioral_status=[], behavior_origin="not_applicable", behavioral_mechanism_ids=[],
            classification_review=dict(date=DATE, source_content_checked=True,
                independent_source_reverification=False, independent_replication=False),
            governance_scale="research_authorization_and_national_security")
        for key in ["notes", "corroboration_needed", "claim_challenged"]:
            pair(event, key, "", "", lang)
        if raw["id"] == CATHEDRAL:
            event.update(incident_date=None, incident_date_precision="unknown", autonomy_status="not_established")
            pair(event, "scope", "Корпоративные системы Anthropic и стороннее ПО; разрешённый периметр исследования оспаривается.",
                "Anthropic enterprise systems and third-party software; authorized research scope is disputed.", lang)
            pair(event, "observation_period", "Даты доступа не раскрыты; сообщение опубликовано 26 октября 2026 года.",
                "Access dates undisclosed; report published October 26, 2026.", lang)
            pair(event, "role_basis", "ИИ использовали исследователи для проникновения; защищаемый объект — корпоративные системы лаборатории, не установленный доступ к модели. Роль не устанавливает преступный умысел или автономность.",
                "Researchers used AI for intrusion; the protected object is the lab's enterprise systems, not established access to the model. The role establishes neither criminal intent nor autonomy.", lang)
            pair(event, "editorial_rationale", "Связи с поставщиками расширяют поверхность доступа к лаборатории. Реакция чиновника показывает трактовку корпоративной безопасности как государственного интереса; степень контроля государства не измерена.",
                "Supplier dependencies extend the lab's access surface. An official's response frames enterprise security as a state interest; the extent of state control is not measured.", lang)
        else:
            pair(event, "scope", "Уведомление властей США об инцидентах с моделями и устранение последствий; пределы принуждения не установлены.",
                "U.S. government notification of model incidents and remediation; enforcement scope is not established.", lang)
            pair(event, "role_basis", "Предмет документа — ответственность разработчиков за инциденты с моделями; это не отдельная атака и не измерение кибервозможностей.",
                "The statement concerns developer accountability for model incidents; it is not a separate attack or a capability measurement.", lang)
            pair(event, "editorial_rationale", "Государство требует наблюдаемости инцидентов и устранения последствий. Заявленное обязательство отделено от установленной правовой силы и фактического исполнения.",
                "The state demands incident visibility and remediation. The asserted obligation is distinct from established enforceability and observed implementation.", lang)
        doc["events"].append(event)
        events[event["id"]] = event

    edges = []
    def edge(source, target, relation, arc, ru, en, relationship="evidential", target_kind="evidence"):
        item = dict(id=f"EDGE_V050_CATHEDRAL_{len(edges)+1:03d}", source=source, target=target,
            source_kind="evidence", target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level="B",
            visual_lane="cyber_security_patch" if source==CATHEDRAL else "governance_law",
            kind="edge", is_auto=False, style="solid" if relationship=="evidential" else "dashed",
            relationship_class=relationship)
        pair(item, "summary", ru, en, lang)
        edges.append(item)
    for raw in RECORDS:
        for aid in raw["arcs"]:
            edge(raw["id"], aid, "part_of_arc", aid,
                "Тематическая принадлежность, не подтверждение всех выводов арки.",
                "Thematic membership, not evidence for every conclusion in the arc.", "thematic", "arc")
            arcs[aid]["key_nodes"] = uniq(arcs[aid]["key_nodes"] + [raw["id"]])
    edge(SI_FORCE, DISCLOSURE, "context_for", PACING,
        "Требование касается раскрытых действий моделей на внешних системах. Это политический ответ на уведомление, не дополнительный инцидент; уточнение Джорджии сохранено отдельно.",
        "The demand concerns disclosed model actions on external systems. It is a policy response to notification, not an additional incident; Georgia's correction remains separate.", "editorial_relationship")
    edge(CATHEDRAL, SI_FORCE, "context_for", PACING,
        "Два направления риска: доступ исследователей к лаборатории и действия её моделей вовне. Требование от 9 октября не записано как следствие новости Cathedral от 26 октября.",
        "Two risk directions: researchers accessing a lab and its models acting externally. The October 9 demand is not recorded as a consequence of the October 26 Cathedral news.", "editorial_relationship")
    edge(SI_FORCE, CLAIM, "supports_with_scope", PACING,
        "Поддерживает вывод о государственном требовании наблюдаемости и ответственности, не доказывает новый закон, санкции или исполнение.",
        "Supports a state demand for visibility and accountability, not a new statute, penalties or implementation.", target_kind="claimCheck")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    check = next(c for c in doc["claimChecks"] if c["id"]==CLAIM)
    check["supporting_evidence"] = uniq(check["supporting_evidence"] + [SI_FORCE])
    add_source(check, SOURCES["axios"])
    for aid in {a for raw in RECORDS for a in raw["arcs"]}:
        arc = arcs[aid]
        ordered = iter(sorted((n for n in arc["key_nodes"] if n in events), key=lambda n:(events[n]["date"], n)))
        arc["key_nodes"] = [next(ordered) if n in events else n for n in arc["key_nodes"]]
        dates = [events[n]["date"] for n in arc["key_nodes"] if n in events]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)
    for aid, ru, en in [
        (RESILIENCE, "Защита лаборатории включает сторонние бизнес-системы и границы разрешённого исследования, а не только веса моделей.",
         "Lab security includes third-party business systems and research-authorization boundaries, not just model weights."),
        (PACING, "Государственные требования раскрывать инциденты расширяют претензию на наблюдаемость частных лабораторий; заявление, юридическая сила и исполнение остаются разными уровнями свидетельств.",
         "State demands for incident disclosure extend the claim to visibility into private labs; statements, enforceability and implementation remain different evidence levels."),
    ]:
        pair(arcs[aid], "thesis", arcs[aid]["thesis_ru"]+" "+ru, arcs[aid]["thesis_en"]+" "+en, lang)

    rebuild_sources(doc)
    rebuild_counts(doc)
    for key, col in [("total_evidence_items","events"),("total_timeline_items","events"),("total_events","events"),
                     ("total_story_edges","edges"),("total_edges","edges"),("total_claims","claims")]:
        doc["summary"][key] = len(doc[col])
    doc["summary"].update(source_count=len(doc["sourceIndex"]),
        cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]),
        claim_status_counts=dict(Counter(c["status"] for c in doc["claims"])))
    doc["summary"]["stats"].update(total_claims=len(doc["claims"]), **doc["summary"]["claim_status_counts"])
    for key, field in [("by_status","status"),("event_status_counts","status"),("by_confidence","confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]),
        events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"]))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=2, added_claims=0,
        added_story_arcs=0, added_story_edges=len(edges), description="Cathedral access, disputed research scope and separate SI Force notification demand."))
    doc["presentation"].update(editorial_version=VERSION, release_notes=[dict(
        title="Безопасность лаборатории и государственный надзор" if lang=="ru" else "Lab security and state oversight",
        text="Cathedral и отдельное требование SI Force: две записи, без установленной причинной связи." if lang=="ru" else "Cathedral and the separate SI Force demand: two records without an established causal link.")])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v050_added_event_ids=[r["id"] for r in RECORDS],
        v050_added_edge_ids=[e["id"] for e in edges], v050_updated_event_ids=[])
    doc["researchAudit"]["cathedral_october"] = dict(date=DATE, added_event_count=2,
        excluded_inferences=["autonomous lab escape", "government-directed attack", "12 hours total duration",
            "vendor internal systems necessarily compromised", "intentional concealment established",
            "bounty payment denied", "SI Force demand caused by Cathedral", "new enforceable law established"])
    doc["factcheckAudit"]["v050_cathedral"] = dict(date=DATE, source_accounts_reviewed=True,
        independently_reproduced=False, entire_source_registry_reverified=False)
    thesis_ids = {t["id"] for t in doc["thesisNodes"]}
    arc_counts = {a:sum(e["source"]==a and e["target"] in thesis_ids for e in doc["edges"]) for a in arcs}
    hanging = [a for a,n in arc_counts.items() if not n]
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE,
        arc_count=len(arcs), story_arcs=len(arcs), computed_arc_count=len(arcs), arc_to_thesis_counts=arc_counts,
        computed_arc_to_thesis_counts=arc_counts, hanging_arcs_after_fix=hanging, computed_hanging_arcs=hanging)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results, audit = {}, dict(version=VERSION, base_version="0.49", base_sha256=BASE_HASH, languages={})
    for lang in ["ru", "en"]:
        raw = (args.input/f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest()!=BASE_HASH[lang]:
            raise ValueError(f"Changed {lang} baseline; refusing overwrite")
        old = json.loads(raw)
        doc = migrate(copy.deepcopy(old))
        doc["migrationAudit"]["v050_base_sha256"] = BASE_HASH[lang]
        audit["languages"][lang] = {c:{x["id"]:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest() for x in old[c]}
            for c in ["events", "claims", "edges"]}
        audit["languages"][lang]["sources"] = {s["id"]:s["url"] for s in old["sourceIndex"]}
        audit["languages"][lang]["counts_after"] = {c:len(doc[c]) for c in ["events","claims","claimChecks","arcs","edges","sourceIndex","gaps"]}
        results[lang] = json.dumps(doc, ensure_ascii=False, indent=2)+"\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in results.items():
        path = args.output/f"ai_power_storygraph_{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang, VERSION, audit["languages"][lang]["counts_after"])
    PACKET.mkdir(parents=True, exist_ok=True)
    (PACKET/"migration-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    (PACKET/"evidence.json").write_text(json.dumps(dict(version=VERSION,checked_at=DATE,sources=SOURCES,records=RECORDS),ensure_ascii=False,indent=2)+"\n")


if __name__ == "__main__":
    main()
