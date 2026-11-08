#!/usr/bin/env python3
"""Repair the 2026-11-07 data audit without changing release metadata.

Run with -B. Dry-run is the default; --apply updates both canonical documents
only after bilingual validation, preservation checks and an idempotence check.
The first write retains a reversible field journal under the new review folder.
"""
from __future__ import annotations

import argparse
import calendar
import copy
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_KEY = "audit_repair_2026_11_08"
REVIEW_DIR = "review/audit-repair-2026-11-08"
NODE_COLLECTIONS = (
    "events", "claims", "claimChecks", "arcs", "arcFamilies", "thesisNodes",
    "counterarguments", "gaps",
)
CANONICAL = "SIG_2026_OPENAI_GPT56_VETTED_PARTNERS"
ALIAS = "SIG_2026_OPENAI_GPT56_STAGED_RELEASE"
CONTEXT_ARC = "ARC_2023_GOVERNANCE_SHOCK"
CONTEXT_EVENT = "SIG_2021_EU_AI_ACT_PROPOSAL"
FINANCE = "CLM_025_FINANCE_AI_KILL_SWITCH"
UK_EVENT = "SIG_2026_UK_FINANCE_AI_STRESS_TESTS"
KIND_ALIASES = {
    "evidence": "event", "claim_check": "claimCheck",
    "story_arc": "arc", "synthetic_thesis": "thesis",
}

CONTRACT = {
    "version": 1,
    "reading_routes": (
        "Retain authored primary/secondary routes. Add membership only from an "
        "arc's key_nodes or a direct part_of_arc/key_node event-arc edge. "
        "An edge's arc_id, including supports_with_scope, qualifies, updates and "
        "context_for, is not itself membership. Keep arcIds as the broader "
        "association index; non-route associations live in context_arc_ids. "
        "route_eligible_arc_ids is the ordered union of primary/secondary routes. "
        "Explicit context_nodes override membership, including historical context "
        "outside a timeline lens. Reading routes never imply positive evidence."
    ),
    "aliases": (
        "Resolve record_aliases and canonical_event_id before presentation/counting; "
        "omit events with presentation_hidden=true from duplicate presentation. "
        "exclude_from_presentation is a synchronized compatibility flag. Keep "
        "both records and all original source/target IDs. canonical_source and "
        "canonical_target redirect affected edges for presentation only. "
        "Aggregate canonical_edge_ids and sources/caveats from alias_event_ids; "
        "do not count the alias as independent corroboration."
    ),
    "evidence": (
        "supporting_evidence is retained as a legacy evidence-reference list, "
        "not a guarantee of positive polarity. evidence_relations records exact "
        "manual relations where available; otherwise retain the existing auto "
        "relation or mark the reference unspecified. Never infer polarity from "
        "a title, ID substring or a claim-check status."
    ),
    "backlinks": "edgeIds is the exact set of incident original edges, including auto edges.",
    "intervals": (
        "start_date/end_date cover in-period key_nodes; context_nodes retain "
        "historical prerequisites without extending the timeline lens. "
        "context_start_date/context_end_date describe that separate context. "
        "Month/year event dates denote their full possible calendar interval."
    ),
    "sources": (
        "One displayed sources entry per exact URL within a node. citation_variants "
        "retains every original citation object, including title and other metadata. "
        "No global sourceIndex/sourceGroups records or provenance are rewritten."
    ),
    "actor_types": (
        "Use reviewed exact-name entries for actors already in entityRegistry, "
        "and only classifierTaxonomy.actors.type_labels values. No substring, "
        "topic, publisher or co-actor inference. Unnamed or unreviewed actors "
        "remain explicitly unresolved in audit_actor_types. Existing nonempty "
        "types outside this repair are not reclassified."
    ),
    "counts": "Legacy counts describe stored records; presentation_counts excludes aliases.",
    "factcheck": "Internal consistency repair of stored evidence, not a new source fact-check.",
}

FINANCE_RU = (
    "В финансах ИИ становится предметом операционного управления, но стадии и "
    "юрисдикции различаются. В связанном свидетельстве RBI предлагает проект "
    "правил с независимой проверкой, ответственностью руководства и возможностью "
    "ограничения или отключения моделей; внедрение ещё не подтверждено. "
    "Регуляторы США собирают информацию и применяют существующие рамки. "
    "Британский парламентский комитет призывает к специальным ИИ-стресс-тестам, "
    "которые на дату свидетельства ещё не введены. Это поддерживает общий тезис "
    "о переходе к управлению рисками ИИ, но не доказывает, что все перечисленные "
    "меры уже обязательны во всех трёх юрисдикциях."
)
FINANCE_EN = (
    "Finance is moving toward operational AI governance, but jurisdictions and "
    "stages differ. In the linked evidence, RBI proposes draft rules covering "
    "independent validation, board accountability and the ability to limit or "
    "decommission models; implementation is not established. U.S. regulators "
    "are gathering information and applying existing frameworks. The UK "
    "parliamentary committee calls for AI-specific stress tests that had not "
    "yet been adopted at the evidence date. This supports the general shift "
    "toward AI risk governance, not a claim that every listed control is "
    "already mandatory across all three jurisdictions."
)
TRANSLATIONS = {
    "CLM_001_INFRA_RACE": "The frontier-AI race increasingly runs through chips, energy, data centres, cloud capacity and long-term capital expenditure, not only model releases.",
    "CLM_002_TIERING": "U.S. policy has moved toward explicit tiers of access to AI chips and compute, but the regime's specific architecture is unstable and requires a dated formulation.",
    "CLM_004_EXPORT_CONTROLS_AS_LEVERAGE": "State export controls already materially affect private AI-chip sales, revenue and deployment decisions, turning commercial infrastructure into geopolitical leverage.",
    "CLM_005_EU_SEMI_PERIPHERY": "The EU is expanding public compute and industrial policy, but dependence on hyperscaler cloud and external frontier infrastructure remains a major constraint.",
    "CLM_008_MODEL_LAYER_EXPORT_CONTROL": "In June 2026, export-control logic extended from chips and data centres to frontier/cyber models themselves: Anthropic temporarily disabled Mythos/Fable following a reported government order, while OpenAI restricted GPT-5.6-preview at the government's request. Until primary order or licence documents are published, describe this as reported or company-confirmed access control, not a fully reconstructed legal regime.",
    "CLM_009_MYTHOS_CAPABILITY": "Mythos-related reporting and Mozilla-style defender evidence strongly suggest a step-change in AI-assisted vulnerability discovery; however, independent rediscovery tests and classified-test caveats mean we should not state that autonomous machine-speed 0-day exploitation is established.",
    "CLM_010_360_COUNTER_STACK": "360 claims a Chinese counterpart to Mythos, Tulongfeng, and an automated defensive system, Yitianzhen. Reuters confirms that the statements were made and reports the figures as company claims, while explicitly noting that it could not independently verify the capability claims.",
    "CLM_011_AGENT_HARNESS_ROUTE_AROUND": "Zhou/360 frame the Chinese response not as a direct race for the strongest base model, but as an agent-harness approach: model, security data, tools, memory and multi-agent coordination. This is an important strategic narrative and a plausible engineering hypothesis, not yet a demonstrated parity result.",
    "CLM_012_CRITICAL_DECISION_USE": "AI is already embedded in critical workflows: military command and control, mission planning and targeting support; banking lending, KYC and sanctions screening; investment-banking preparation; and cyber defence of legacy infrastructure. For military cases, say decision support or targeting support, not autonomous killing.",
    "CLM_014_BIOTECH_CBRN_GATING": "CBRN/biotech shows a distinct regime: providers build real-time and asynchronous filters and monitoring, while legitimate dual-use users may receive vetted exemptions instead of a blanket refusal. This is a layer of governance by access.",
    "CLM_015_MILITARY_SUPPLIER_BOUNDARY_CONTROL": "Embedding commercial models in military workflows creates a decision-sovereignty problem: states seek any lawful use, providers seek guardrails, and the resulting boundary of use is set by contracts, review procedures and technical filters.",
    "CLM_019_PALANTIR_DATA_SOVEREIGNTY_COUNTERARGUMENT": "Do not state that Palantir owns or controls NHS or state data. More safely: Palantir supplies the operational software layer through which public institutions integrate, query and act on sensitive data; formal ownership and control may remain with the state, while dependency and access-control risks remain contested.",
    "CLM_020_SCALE_PRIMARY_NUMBERS": "According to Stanford AI Index 2026, global private AI investment was $344.7 billion (+127.5%) and corporate investment $581.7 billion (+130%); the U.S. figure was $285.9 billion versus China's $12.4 billion (23.1 times). Private figures understate China: guidance funds provided about $184 billion to AI in 2000-2023; $912 billion covers all industries, not AI alone.",
    "CLM_021_CHIP_TOLL_REGIME": "As described in the 2026 evidence, chip access is metered through tolls and throttles: H200/MI325X case-by-case review (25% tariff, 50% cap, KYC and U.S. inspection), Blackwell denial, and H20 access under a 15% arrangement. Beijing also restricts access, while Huawei targets 600,000 Ascend 910C units. Describe access metering by generation, price and monitoring, not a blanket embargo.",
    "CLM_022_CONTROLS_LEAK_BUT_POLICE": "Controls are not airtight: smuggling and transshipment through third countries occur. Those countries consequently become control nodes, and the stack becomes subject to customs, licensing, KYC and inspections. Leverage does not need to be airtight to be structural.",
    "CLM_023_ENERGY_BOTTLENECK_WITH_FLEXIBILITY": "Energy is a foundational AI-stack layer: growing load creates regional bottlenecks and political resistance. Data centres are not necessarily wholly inflexible loads: workload orchestration and load shifting can reduce some grid stress. This does not remove energy-related power, but makes it manageable and locally variable.",
    FINANCE: FINANCE_EN,
}

# Exact reviewed identities, not token/name heuristics. Roles use the existing
# taxonomy; individual politicians and ambiguous institutional labels are deferred.
ACTOR_GROUPS = {
    "company": (
        "ASML", "Alibaba", "Amazon / AWS", "Bull", "CXMT", "ConnectWise",
        "CrowdStrike", "DeepSeek", "Faros AI", "GitBook", "Google",
        "Google DeepMind", "Google Research", "HUMAIN", "Huawei", "Klarna",
        "Microsoft", "Microsoft Research", "Mindbox", "Mistral", "NVIDIA",
        "OpenAI", "Oracle", "Palo Alto Networks", "SK hynix", "Saudi Aramco",
        "StrongDM", "TSMC", "Wiz", "Xiaomi", "YMTC", "Yandex", "eMudhra",
        "Alibaba Cloud Apsara Lab",
    ),
    "government": (
        "ADAFSA", "Abu Dhabi Government", "China Government",
        "China Ministry of Commerce", "China Ministry of Science and Technology",
        "EuroHPC Joint Undertaking", "India Ministry of Agriculture and Farmers Welfare",
        "NASA", "New York State Government", "Texas State Government",
        "UK AI Security Institute", "UK Council for Science and Technology",
        "UK Government", "UK National Cyber Security Centre", "UK Treasury Committee",
        "US General Services Administration", "CSA Singapore",
    ),
    "research": (
        "AIST", "Chung-Ang University", "Counterpoint Research", "Dartmouth College",
        "ECMWF", "EMBL-EBI", "EPFL Swiss Plasma Center", "HSE", "JKU", "KAUST",
        "MBZUAI", "METR", "MIPT", "NASK", "National Bureau of Economic Research",
        "Princeton Plasma Physics Laboratory", "Princeton University", "RAND",
        "Russian Academy of Sciences", "Santa Fe Institute", "Skoltech",
        "Stanford Digital Economy Lab", "Sun Yat-sen University", "TU Dresden",
        "Tohoku University", "Tsinghua University", "Universidade Federal de Minas Gerais",
        "University of Chicago", "University of Pennsylvania",
        "University of Science and Technology of China", "University of Sydney",
        "Vesuvius Challenge", "UK AI Security Institute",
    ),
    "civil_society": ("Debian", "Mozilla", "PHP Foundation", "Precision Development"),
    "workforce_users": ("Linux kernel maintainers",),
    "financial_institution": ("Bank for International Settlements", "PIF", "World Bank"),
    "multilateral": ("Bank for International Settlements", "ESA", "International Labour Organization", "World Bank"),
    "regulator": ("NIST",),
    "threat_actor": ("Storm-0940", "Storm-3358", "VAPOR PANDA"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(items):
    return list(dict.fromkeys(items))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(encoded(value).encode("utf-8")).hexdigest()


def nodes(doc):
    return {n["id"]: n for col in NODE_COLLECTIONS for n in doc[col]}


def citation_records(node):
    records = []
    for source in node.get("sources", []):
        if isinstance(source, dict) and "citation_variants" in source:
            records.extend(source["citation_variants"])
        else:
            records.append(source)
    return records


def manifest(doc):
    collections = NODE_COLLECTIONS + ("edges", "sourceIndex", "sourceGroups")
    citations = {
        node_id: sorted(encoded(s) for s in citation_records(node))
        for node_id, node in nodes(doc).items() if node.get("sources")
    }
    return {
        "counts": {col: len(doc[col]) for col in collections},
        "id_hashes": {col: digest(sorted(n["id"] for n in doc[col])) for col in collections},
        "event_dates_sha256": digest({e["id"]: e["date"] for e in doc["events"]}),
        "edge_endpoints_sha256": digest({e["id"]: [e["source"], e["target"]] for e in doc["edges"]}),
        "source_index_sha256": digest(doc["sourceIndex"]),
        "source_groups_sha256": digest(doc["sourceGroups"]),
        "citation_provenance_sha256": digest(citations),
        "citation_record_count": sum(len(v) for v in citations.values()),
        "unique_source_urls": len({s["url"] for s in doc["sourceIndex"]}),
        "auto_edge_ids_sha256": digest(sorted(e["id"] for e in doc["edges"] if e.get("is_auto"))),
        "auto_edge_count": sum(bool(e.get("is_auto")) for e in doc["edges"]),
        "release_metadata_sha256": digest(doc["meta"]),
    }


def repair_polarity(doc):
    manual = defaultdict(list)
    for edge in doc["edges"]:
        if not edge.get("is_auto"):
            manual[edge["source"], edge["target"]].append(edge)
    for edge in doc["edges"]:
        if not edge.get("is_auto") or edge.get("arc_id") != "AUTO_CLAIMCHECK_SUPPORT":
            continue
        counterparts = manual[edge["source"], edge["target"]]
        relations = {e["relation"] for e in counterparts}
        require(len(relations) <= 1, f"Ambiguous manual polarity for {edge['id']}: {relations}")
        if relations and edge["relation"] not in relations:
            edge["audit_original_relation"] = edge["relation"]
            edge["audit_original_summaries"] = {
                k: v for k, v in edge.items() if k.startswith("summary")
            }
            edge["relation"] = next(iter(relations))
            edge["polarity_basis_edge_ids"] = [e["id"] for e in counterparts]
            en = f"Evidence relation {edge['relation']} follows manual edge(s) {', '.join(edge['polarity_basis_edge_ids'])}; the legacy evidence list does not imply positive support."
            ru = f"Отношение {edge['relation']} взято из ручных рёбер {', '.join(edge['polarity_basis_edge_ids'])}; список свидетельств не означает положительного подтверждения."
            edge.update(summary_ru=ru, summary_en=en)
            if "summary" in edge:
                edge["summary"] = ru if doc["language"] == "ru" else en
    for check in doc["claimChecks"]:
        check["evidence_linkage_semantics"] = "neutral_linkage_not_positive_support"
        refs = unique(check.get("supporting_evidence", []) + check.get("qualifying_evidence", []))
        check["evidence_relations"] = []
        for event_id in refs:
            edges = [e for e in doc["edges"] if e["source"] == event_id and e["target"] == check["id"]]
            authored = [e for e in edges if not e.get("is_auto")]
            # Legacy field name: event_id is a typed evidence-node reference;
            # qualifying evidence can also be a claim, such as export-14.
            check["evidence_relations"].append({
                "event_id": event_id,
                "relations": unique(e["relation"] for e in (authored or edges)),
                "edge_ids": [e["id"] for e in edges],
                "basis": "manual_edges" if authored else "existing_auto_edges" if edges else "unspecified_reference",
                "legacy_fields": [f for f in ("supporting_evidence", "qualifying_evidence") if event_id in check.get(f, [])],
            })


def repair_wording(doc, ru):
    checks = {c["id"]: c for c in doc["claimChecks"]}
    originals = {c["id"]: c for c in ru["claimChecks"]}
    finance = checks[FINANCE]
    finance.update(safe_wording_ru=FINANCE_RU, safe_wording_en=FINANCE_EN)
    finance["safe_wording"] = FINANCE_RU if doc["language"] == "ru" else FINANCE_EN
    for check_id, translation in TRANSLATIONS.items():
        check = checks[check_id]
        if not check.get("safe_wording_en"):
            require(bool(originals[check_id].get("safe_wording_ru")), f"Missing Russian caveat: {check_id}")
            check["safe_wording_en"] = translation
        if doc["language"] == "en" and not check.get("safe_wording"):
            check["safe_wording"] = check["safe_wording_en"]
        check.setdefault("audit_translation", {
            "source_field": "safe_wording_ru", "source_language": "ru",
            "method": "reviewed_translation_of_stored_caveat" if check_id != FINANCE else "jurisdiction_and_stage_correction",
            "source_text": FINANCE_RU if check_id == FINANCE else originals[check_id]["safe_wording_ru"],
            "independent_factcheck": False,
        })


def repair_actors(doc):
    events = {e["id"]: e for e in doc["events"]}
    uk = events[UK_EVENT]
    require("UK Treasury Committee" in uk["actors_raw"], "UK actor correction lacks raw evidence")
    for field in ("actor_entities", "actor_facets"):
        uk[field] = unique("UK Treasury Committee" if a == "US Treasury" else a for a in uk[field])
    uk["actor_jurisdictions"] = [j for j in uk["actor_jurisdictions"] if j != "US"]
    uk["actor_types"] = unique(uk["actor_types"] + ["government"])
    uk["audit_actor_identity"] = {
        "basis": "actors_raw explicitly names UK Treasury Committee, FCA and Bank of England",
        "replaced_entity": "US Treasury", "replacement_entity": "UK Treasury Committee",
        "legacy_raw_facets_retained": True,
    }
    registered = set(doc["entityRegistry"]["actors"]) | {"UK Treasury Committee"}
    taxonomy = doc["classifierTaxonomy"]["actors"]["type_labels"]
    mapping = defaultdict(list)
    for actor_type, actors in ACTOR_GROUPS.items():
        require(actor_type in taxonomy, f"Unknown actor type: {actor_type}")
        for actor in actors:
            require(actor in registered, f"Unregistered actor mapping: {actor}")
            mapping[actor].append(actor_type)
    targets = unique(doc["migrationAudit"]["v051_added_event_ids"] + doc["migrationAudit"]["v052_added_event_ids"])
    entries = []
    for actor, types in sorted(mapping.items()):
        evidence = [e for e in doc["events"] if actor in e["actor_entities"]]
        entries.append({
            "actor": actor, "actor_types": types,
            "basis": "explicit_editorial_identity_mapping_to_existing_taxonomy",
            "evidence_event_ids": [e["id"] for e in evidence],
            "source_urls": unique(s["url"] for e in evidence for s in e.get("sources", []) if s.get("url")),
        })
    doc["entityRegistry"]["audit_actor_type_entries"] = entries
    for event_id in targets:
        event = events[event_id]
        resolved = [a for a in event["actor_entities"] if a in mapping]
        unresolved = [a for a in event["actor_entities"] if a not in mapping]
        types = unique(t for a in resolved for t in mapping[a])
        if not event.get("actor_types"):
            event["actor_types"] = types
        event["audit_actor_types"] = {
            "registry_field": "entityRegistry.audit_actor_type_entries",
            "resolved_entities": resolved, "unresolved_entities": unresolved,
            "status": "resolved" if resolved and not unresolved else "partial" if resolved else "review_required",
            "reason": "exact_reviewed_identity" if resolved and not unresolved else "unreviewed_entity_identity" if unresolved else "no_actor_entity_in_stored_record",
        }


def repair_alias(doc):
    events = {e["id"]: e for e in doc["events"]}
    canonical, alias = events[CANONICAL], events[ALIAS]
    require(canonical["date"] == alias["date"] and canonical["url"] == alias["url"], "Duplicate event evidence changed")
    canonical.update(canonical_event_id=CANONICAL, alias_event_ids=[ALIAS], exclude_from_presentation=False, presentation_hidden=False)
    alias.update(canonical_event_id=CANONICAL, exclude_from_presentation=True, presentation_hidden=True)
    existing = doc.setdefault("record_aliases", {})
    require(existing.get(ALIAS, CANONICAL) == CANONICAL, "Conflicting canonical alias")
    existing[ALIAS] = CANONICAL
    for event in (canonical, alias):
        event.setdefault("audit_original_status", event["status"])
        event["status"] = "verified_as_reported"
        event["dedupe_note_en"] = "Same dated rollout decision and Reuters URL. Preserve both IDs and original records; present the vetted-partners record once, with the union of both records' edges, citations and caveats. Not independent corroboration."
        event["dedupe_note_ru"] = "Одна дата, одно решение о выпуске и один URL Reuters. Оба ID и исходные записи сохранены; показывать запись о проверенных партнёрах один раз, объединяя связи, цитаты и оговорки обеих записей. Это не независимое подтверждение."
    for edge in doc["edges"]:
        for endpoint in ("source", "target"):
            if edge[endpoint] == ALIAS:
                edge["canonical_" + endpoint] = CANONICAL
    canonical["canonical_edge_ids"] = [e["id"] for e in doc["edges"] if {e["source"], e["target"]} & {ALIAS, CANONICAL}]
    canonical["canonical_provenance_event_ids"] = [CANONICAL, ALIAS]


def date_bounds(value):
    if len(value) == 4:
        start, end = value + "-01-01", value + "-12-31"
    elif len(value) == 7:
        year, month = map(int, value.split("-"))
        start, end = value + "-01", value + f"-{calendar.monthrange(year, month)[1]:02d}"
    else:
        start = end = value
    date.fromisoformat(start)
    date.fromisoformat(end)
    return start, end


def repair_intervals(doc):
    events = {e["id"]: e for e in doc["events"]}
    for arc in doc["arcs"]:
        if arc["id"] == CONTEXT_ARC:
            arc["key_nodes"] = [n for n in arc["key_nodes"] if n != CONTEXT_EVENT]
            arc["context_nodes"] = unique(arc.get("context_nodes", []) + [CONTEXT_EVENT])
        bounds = [date_bounds(events[n]["date"]) for n in arc["key_nodes"] if n in events]
        if bounds:
            start = min([arc["start_date"]] + [b[0] for b in bounds])
            end = max([arc["end_date"]] + [b[1] for b in bounds])
            require(arc.get("display_role") not in {"timeline_marker", "timeline_lens"} or (start, end) == (arc["start_date"], arc["end_date"]), f"Unreviewed timeline expansion: {arc['id']}")
            arc.update(start_date=start, end_date=end)
        context = [date_bounds(events[n]["date"]) for n in arc.get("context_nodes", []) if n in events]
        if context:
            arc.update(context_start_date=min(b[0] for b in context), context_end_date=max(b[1] for b in context))


def route_memberships(doc, event):
    direct, context = set(), set()
    for arc in doc["arcs"]:
        if event["id"] in arc.get("key_nodes", []):
            direct.add(arc["id"])
        if event["id"] in arc.get("context_nodes", []):
            context.add(arc["id"])
    arc_ids = {a["id"] for a in doc["arcs"]}
    for edge in doc["edges"]:
        if edge["relation"] in {"part_of_arc", "key_node"}:
            if edge["source"] == event["id"] and edge["target"] in arc_ids:
                direct.add(edge["target"])
            if edge["target"] == event["id"] and edge["source"] in arc_ids:
                direct.add(edge["source"])
    return direct - context, context


def repair_routes(doc):
    arcs = {a["id"]: a for a in doc["arcs"]}
    for event in doc["events"]:
        old = unique(([event["story_primary_arc_id"]] if event.get("story_primary_arc_id") else []) + event.get("story_secondary_arc_ids", []))
        direct, context = route_memberships(doc, event)
        require(set(old) <= set(arcs), f"Unknown authored route: {event['id']}")
        routes = [a for a in old if a not in context] + sorted(direct - set(old))
        event["route_eligible_arc_ids"] = routes
        if routes:
            event["story_primary_arc_id"], event["story_secondary_arc_ids"] = routes[0], routes[1:]
        else:
            event.pop("story_primary_arc_id", None)
            event.pop("story_secondary_arc_ids", None)
        associations = set(event.get("arcIds", [])) & set(arcs)
        context_only = sorted((associations | context) - set(routes))
        if context_only or "context_arc_ids" in event:
            event["context_arc_ids"] = context_only
        if context_only:
            event["audit_route_context"] = [{
                "arc_id": a,
                "reason": "explicit_historical_context" if a in context else "association_without_direct_membership",
                "edge_ids": [e["id"] for e in doc["edges"] if e.get("arc_id") == a and event["id"] in (e["source"], e["target"])],
            } for a in context_only]
    doc["arcHierarchy"]["primary_event_assignments"] = sum(bool(e.get("story_primary_arc_id")) for e in doc["events"])
    doc["arcHierarchy"]["events_with_secondary_arcs"] = sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"])


def repair_sources(doc):
    for node in nodes(doc).values():
        grouped = {}
        cleaned = []
        for source in node.get("sources", []):
            url = source.get("url") if isinstance(source, dict) else None
            if not url or url not in grouped:
                cleaned.append(source)
                if url:
                    grouped[url] = source
                continue
            keeper = grouped[url]
            if "citation_variants" not in keeper:
                keeper["citation_variants"] = [copy.deepcopy(keeper)]
            keeper["citation_variants"].extend(copy.deepcopy(source.get("citation_variants", [source])))
        if "sources" in node:
            node["sources"] = cleaned


def repair_indexes(doc):
    by_id = nodes(doc)
    incident = defaultdict(list)
    for edge in doc["edges"]:
        for endpoint in ("source", "target"):
            require(edge[endpoint] in by_id, f"Unknown endpoint: {edge['id']} {endpoint}")
            if not edge.get(endpoint + "_kind"):
                edge[endpoint + "_kind"] = KIND_ALIASES.get(by_id[edge[endpoint]]["kind"], by_id[edge[endpoint]]["kind"])
            incident[edge[endpoint]].append(edge)
    for node_id, node in by_id.items():
        edges = incident[node_id]
        if edges or "edgeIds" in node:
            node["edgeIds"] = unique(e["id"] for e in edges)
        if "relationTypes" in node:
            node["relationTypes"] = unique(e["relation"] for e in edges)
    for count_key, field in (("actors", "actor_entities"), ("actor_entities", "actor_entities"), ("actor_types", "actor_types"), ("actor_jurisdictions", "actor_jurisdictions")):
        doc["counts"][count_key] = dict(Counter(v for e in doc["events"] for v in e.get(field, [])))
    doc["counts"]["relation_types"] = dict(Counter(e["relation"] for e in doc["edges"]))
    doc["entityRegistry"]["actors"] = sorted(doc["counts"]["actor_entities"], key=str.casefold)
    for key in ("by_status", "event_status_counts"):
        doc["summary"][key] = dict(Counter(e["status"] for e in doc["events"]))
    # Reuse the existing read-only reference checker; do not invoke its writer.
    from validate import references
    doc["referenceIntegrity"] = references(doc)


def check_document(doc):
    by_id = nodes(doc)
    require(len(by_id) == sum(len(doc[c]) for c in NODE_COLLECTIONS), "Duplicate node IDs")
    require(len({e['id'] for e in doc['edges']}) == len(doc['edges']), "Duplicate edge IDs")
    require(doc["referenceIntegrity"]["valid"], "Invalid typed references")
    incident = defaultdict(set)
    for edge in doc["edges"]:
        for endpoint in ("source", "target"):
            expected = KIND_ALIASES.get(by_id[edge[endpoint]]["kind"], by_id[edge[endpoint]]["kind"])
            actual = KIND_ALIASES.get(edge.get(endpoint + "_kind"), edge.get(endpoint + "_kind"))
            require(actual == expected, f"Wrong endpoint kind: {edge['id']}")
            incident[edge[endpoint]].add(edge["id"])
    for node_id, node in by_id.items():
        require(set(node.get("edgeIds", [])) == incident[node_id], f"Incomplete/nonincident backlinks: {node_id}")
        urls = [s["url"] for s in node.get("sources", []) if isinstance(s, dict) and s.get("url")]
        require(len(urls) == len(set(urls)), f"Duplicate displayed citation: {node_id}")
    arcs = {a["id"] for a in doc["arcs"]}
    for event in doc["events"]:
        direct, context = route_memberships(doc, event)
        routes = ([event["story_primary_arc_id"]] if event.get("story_primary_arc_id") else []) + event.get("story_secondary_arc_ids", [])
        require(len(routes) == len(set(routes)), f"Duplicate route: {event['id']}")
        require(event.get("route_eligible_arc_ids") == routes, f"Route eligibility mismatch: {event['id']}")
        require(direct <= set(routes) and not context & set(routes), f"Membership contract: {event['id']}")
        require((set(event.get("arcIds", [])) & arcs) - set(routes) <= set(event.get("context_arc_ids", [])), f"Unexplained route gap: {event['id']}")
    for arc in doc["arcs"]:
        for node_id in arc.get("key_nodes", []):
            if by_id[node_id]["kind"] == "event":
                start, end = date_bounds(by_id[node_id]["date"])
                require(arc["start_date"] <= start <= end <= arc["end_date"], f"Checkpoint outside interval: {arc['id']} {node_id}")
    for check in doc["claimChecks"]:
        require(bool(check.get("safe_wording_en") or check.get("safe_wording")), f"Missing English caveat: {check['id']}")
    for alias_id, canonical_id in doc.get("record_aliases", {}).items():
        require(alias_id != canonical_id and canonical_id in by_id, "Invalid alias target")
        alias, canonical = by_id[alias_id], by_id[canonical_id]
        require(alias.get("canonical_event_id") == canonical_id and alias.get("presentation_hidden") is True, "Invalid alias presentation")
        require(alias.get("exclude_from_presentation") is True and not canonical.get("presentation_hidden"), "Conflicting hidden flags")
        require(alias_id in canonical.get("alias_event_ids", []), "Missing canonical backlink")


def patch_document(doc, ru):
    before = manifest(doc)
    repair_polarity(doc)
    repair_wording(doc, ru)
    repair_actors(doc)
    repair_alias(doc)
    repair_intervals(doc)
    repair_routes(doc)
    repair_sources(doc)
    repair_indexes(doc)
    doc["auditRepair"] = {
        "id": AUDIT_KEY, "date": "2026-11-08", "contract": CONTRACT,
        "event_aliases": {ALIAS: CANONICAL},
        "presentation_counts": {"events": sum(not e.get("presentation_hidden") for e in doc["events"]), "stored_events": len(doc["events"]), "preserved_aliases": sum(bool(e.get("presentation_hidden")) for e in doc["events"])},
        "actor_type_review_queue": [{"event_id": e["id"], **e["audit_actor_types"]} for e in doc["events"] if e.get("audit_actor_types", {}).get("status") in {"partial", "review_required"}],
    }
    require(manifest(doc) == before, "Preservation invariant failed")
    doc["migrationAudit"].setdefault(AUDIT_KEY, {"date": "2026-11-08", "preserved": before, "removed_ids": [], "removed_source_urls": [], "release_metadata_unchanged": True})
    check_document(doc)


def field_changes(before, after, path=()):
    """A reversible journal; lists are atomic to preserve order and provenance."""
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(set(before) | set(after)):
            if key not in before or key not in after:
                result.append({"path": list(path + (key,)), "before_exists": key in before, "after_exists": key in after, "before": before.get(key), "after": after.get(key)})
            else:
                result.extend(field_changes(before[key], after[key], path + (key,)))
        return result
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after) and all(isinstance(a, dict) and isinstance(b, dict) and a.get("id") and a.get("id") == b.get("id") for a, b in zip(before, after)):
        return [change for i, (a, b) in enumerate(zip(before, after)) for change in field_changes(a, b, path + (i,))]
    if before != after:
        return [{"path": list(path), "before_exists": True, "after_exists": True, "before": before, "after": after}]
    return []


def findings_summary(before, after):
    old, new = nodes(before), nodes(after)
    missing = sum(len(set(n.get("edgeIds", [])) - set(old[k].get("edgeIds", []))) for k, n in new.items())
    return {
        "polarity_corrections": [e["id"] for e in after["edges"] if "audit_original_relation" in e],
        "restored_english_caveats": [c["id"] for c in before["claimChecks"] if not (c.get("safe_wording_en") or c.get("safe_wording"))],
        "backlinks_added": missing,
        "backlink_nodes_updated": sum(old[k].get("edgeIds") != n.get("edgeIds") for k, n in new.items()),
        "actor_types_filled": sum(not old[e["id"]].get("actor_types") and bool(e.get("actor_types")) for e in after["events"]),
        "actor_type_review_queue": after["auditRepair"]["actor_type_review_queue"],
        "interval_changes": [{"id": a["id"], "before": [old[a["id"]]["start_date"], old[a["id"]]["end_date"]], "after": [a["start_date"], a["end_date"]]} for a in after["arcs"] if any(old[a["id"]][k] != a[k] for k in ("start_date", "end_date"))],
        "context_route_decisions": [{"event_id": e["id"], "decisions": e["audit_route_context"]} for e in after["events"] if e.get("audit_route_context")],
        "endpoint_kinds_filled": sum(not e.get(k) for e in before["edges"] for k in ("source_kind", "target_kind")),
        "presentation_events": after["auditRepair"]["presentation_counts"],
    }


def prepare_documents(documents):
    require(set(documents) == {"ru", "en"}, "Both canonical languages are required")
    result = copy.deepcopy(documents)
    for lang, doc in result.items():
        require(doc["language"] == lang, "Language/file mismatch")
        patch_document(doc, documents["ru"])
    for col in NODE_COLLECTIONS + ("edges", "sourceIndex"):
        require({n["id"] for n in result["ru"][col]} == {n["id"] for n in result["en"][col]}, f"Bilingual IDs differ: {col}")
    for col, fields in {
        "events": ("actor_types", "actor_entities", "actor_jurisdictions", "edgeIds", "story_primary_arc_id", "story_secondary_arc_ids", "route_eligible_arc_ids", "context_arc_ids", "canonical_event_id", "exclude_from_presentation", "presentation_hidden"),
        "edges": ("source", "target", "relation", "source_kind", "target_kind"),
        "arcs": ("key_nodes", "context_nodes", "start_date", "end_date"),
        "claimChecks": ("safe_wording_en", "evidence_relations"),
    }.items():
        ru = {n["id"]: n for n in result["ru"][col]}
        for node in result["en"][col]:
            require(all(node.get(k) == ru[node["id"]].get(k) for k in fields), f"Bilingual repair mismatch: {node['id']}")
    for lang in result:
        second = copy.deepcopy(result[lang])
        patch_document(second, result["ru"])
        require(second == result[lang], f"Non-idempotent migration: {lang}")
    return result


def write_documents(root, original_bytes, documents):
    paths = {lang: root / f"ai_power_storygraph_{lang}.json" for lang in ("ru", "en")}
    for lang, path in paths.items():
        require(path.read_bytes() == original_bytes[lang], f"Concurrent JSON change; refusing to overwrite {path}")
    payloads = {lang: (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8") for lang, doc in documents.items()}
    staged = {}
    try:
        for lang, path in paths.items():
            if payloads[lang] == original_bytes[lang]:
                continue
            fd, name = tempfile.mkstemp(prefix=".audit-repair-", dir=root)
            staged[lang] = Path(name)
            with os.fdopen(fd, "wb") as output:
                output.write(payloads[lang])
                output.flush()
                os.fsync(output.fileno())
            os.chmod(name, path.stat().st_mode)
        # Check both inputs again after staging, before either replacement.
        for lang, path in paths.items():
            require(path.read_bytes() == original_bytes[lang], f"Concurrent JSON change during staging: {path}")
        for lang, staged_path in staged.items():
            os.replace(staged_path, paths[lang])
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = {lang: (args.root / f"ai_power_storygraph_{lang}.json").read_bytes() for lang in ("ru", "en")}
    before = {lang: json.loads(payload) for lang, payload in raw.items()}
    after = prepare_documents(before)
    report = {"id": AUDIT_KEY, "contract": CONTRACT, "languages": {}}
    for lang in before:
        report["languages"][lang] = {
            "input_sha256": hashlib.sha256(raw[lang]).hexdigest(),
            "before_sha256": digest(before[lang]), "after_sha256": digest(after[lang]),
            "before": manifest(before[lang]), "after": manifest(after[lang]),
            "findings": findings_summary(before[lang], after[lang]),
            "changes": field_changes(before[lang], after[lang]),
            "idempotent": True,
        }
    changed = any(before[lang] != after[lang] for lang in before)
    if args.apply and changed:
        destination = args.root / REVIEW_DIR / "migration-audit.json"
        require(not destination.exists(), f"Review journal already exists; refusing to overwrite {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Save the reversible journal before replacing either canonical input.
        with destination.open("x", encoding="utf-8") as output:
            json.dump(report, output, ensure_ascii=False, indent=2)
            output.write("\n")
        write_documents(args.root, raw, after)
    print(json.dumps({"applied": args.apply and changed, "changed": changed, "idempotent": True,
                      "languages": {lang: {"counts": value["after"]["counts"],
                        "citation_records": value["after"]["citation_record_count"],
                        "backlinks_added": value["findings"]["backlinks_added"],
                        "actor_types_filled": value["findings"]["actor_types_filled"],
                        "presentation": value["findings"]["presentation_events"]}
                        for lang, value in report["languages"].items()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
