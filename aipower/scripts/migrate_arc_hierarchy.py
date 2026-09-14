#!/usr/bin/env python3
"""Apply the v0.37 -> v0.38 editorial story-arc hierarchy migration.

The migration changes presentation semantics only. It preserves every event,
claim, arc, edge, source URL and legacy ID from the pinned v0.37 inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from validate import references


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.38"
DATE = "2026-09-14"
PINNED_SHA256 = {
    "ru": "ed8a710c12002e82d0415fe1620f2954b576323776365b8a6cac99650dc7d320",
    "en": "ad1e39f2c3ab41cbdf708f3aa5ba6a58b3a9d2796be81b3321bc369997a23741",
}

FAMILY_ORDER = [
    "ARC_FAMILY_ACCESS_CONTROL",
    "ARC_FAMILY_COUNTERSTACK_SOVEREIGNTY",
    "ARC_FAMILY_CYBER_COGNITION_WAR",
    "ARC_FAMILY_INFRASTRUCTURE_CAPITAL",
    "ARC_FAMILY_DECISION_DATA_FINANCE",
    "ARC_FAMILY_FORMATION_TIMELINE",
]

# role, order, parent, default-visible, optional family move
ARC_LAYOUT = {
    "ARC_EXPORT_CHIPS_TO_MODELS": ("mechanism", 10, "", True, None),
    "ARC_TOLL_AND_THROTTLE": ("submechanism", 11, "ARC_EXPORT_CHIPS_TO_MODELS", False, None),
    "ARC_CONTROL_LEAKS_BUT_POLICES": ("qualifier", 12, "ARC_EXPORT_CHIPS_TO_MODELS", False, None),
    "ARC_A800_H800_WORKAROUND_CLOSURE": ("case", 13, "ARC_EXPORT_CHIPS_TO_MODELS", False, None),
    "ARC_QUIET_ACCESS_CONTROL": ("mechanism", 20, "", True, None),
    "ARC_SOVEREIGN_FLOW_GATING": ("mechanism", 30, "", True, None),
    "ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL": ("mechanism", 40, "", True, None),

    "ARC_OPEN_WEIGHT_EXIT_OR_DEPENDENCE": ("mechanism", 10, "", True, None),
    "ARC_GULF_CONDITIONAL_SOVEREIGNTY": ("case", 20, "", False, None),
    "ARC_CHINA_COUNTERSTACK_ROUTE_AROUND": ("case", 30, "", False, None),
    "ARC_RUSSIA_SELECTIVE_SOVEREIGNTY": ("case", 40, "", False, None),

    "ARC_CYBER_CLAIM_TO_CAVEAT": ("mechanism", 10, "", True, None),
    "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK": ("mechanism", 20, "", True, None),
    "ARC_COGSEC_LAB_TO_WILD_TO_STATE": ("mechanism", 30, "", True, None),

    "ARC_CAPITAL_MIX_PUBLIC_PRIVATE": ("mechanism", 10, "", True, None),
    "ARC_CLOUD_CAPACITY_VENDOR_LOCKIN": ("mechanism", 20, "", True, None),
    "ARC_ENERGY_GRID_POLITICS": ("mechanism", 30, "", True, None),

    "ARC_DATA_LICENSING_AS_INPUT_LAYER": ("mechanism", 10, "", True, None),
    "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION": ("mechanism", 20, "", True, None),
    "ARC_PALANTIR_DECISION_OS": ("case", 21, "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION", False, None),
    "ARC_FINANCE_GOVERNED_SHUTDOWN": ("sector_case", 22, "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION", False, None),
    "ARC_WAR_DATA_FLYWHEEL": (
        "sector_case", 23, "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION", False,
        "ARC_FAMILY_DECISION_DATA_FINANCE",
    ),

    "ARC_2016_2021_METERED_ACCESS_FORMATION": ("timeline_lens", 10, "", False, None),
    "ARC_2021_STATE_INSTITUTIONALIZATION": ("timeline_lens", 20, "", False, None),
    "ARC_2022_2023_FORMATION_PHASE": ("timeline_lens", 30, "", False, None),
    "ARC_2023_GOVERNANCE_SHOCK": ("timeline_marker", 31, "ARC_2022_2023_FORMATION_PHASE", False, None),
}

TITLE_PATCHES = {
    "ARC_TOLL_AND_THROTTLE": (
        "Лицензируемый доступ: цена, объём и условия",
        "Licensed access: price, volume and conditions",
    ),
    "ARC_CONTROL_LEAKS_BUT_POLICES": (
        "Обход, правоприменение и наблюдаемость",
        "Evasion, enforcement and observability",
    ),
    "ARC_CHINA_COUNTERSTACK_ROUTE_AROUND": (
        "Китайский контрстек: собственная инфраструктура, открытые веса и внутренний допуск",
        "China's counter-stack: domestic infrastructure, open weights and internal access gates",
    ),
    "ARC_CYBER_CLAIM_TO_CAVEAT": (
        "Кибервозможности моделей: от испытаний к операциям",
        "Model cyber capabilities: from evaluations to operations",
    ),
    "ARC_CAPITAL_MIX_PUBLIC_PRIVATE": (
        "Режимы финансирования и инфраструктурные обязательства",
        "Financing regimes and infrastructure commitments",
    ),
    "ARC_OPEN_WEIGHT_EXIT_OR_DEPENDENCE": (
        "Открытые веса и перенос зависимости",
        "Open weights and dependency transfer",
    ),
    "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION": (
        "ИИ как интерфейс институциональных решений",
        "AI as an interface for institutional decisions",
    ),
    "ARC_RUSSIA_SELECTIVE_SOVEREIGNTY": (
        "Россия: селективный суверенитет и внешние зависимости",
        "Russia: selective sovereignty and external dependencies",
    ),
}

THESIS_PATCHES = {
    "ARC_CONTROL_LEAKS_BUT_POLICES": (
        "Обходы и утечки становятся объектом правоприменения, контроля транзита и наблюдения. Они не делают режим герметичным, но могут повышать цену, задержку и риск доступа.",
        "Evasion and leakage become objects of enforcement, transit control and observation. They do not make the regime airtight, but can raise the cost, delay and risk of access.",
    ),
    "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION": (
        "С 2021 года генеративные модели входят в профессиональные и государственные рабочие процессы как интерфейс поиска, суммаризации, подготовки и контроля знания вокруг решений. Это расширяет роль поставщика и внутреннего программного слоя, но не доказывает автономную передачу ему полномочий принимать решения.",
        "Since 2021, generative models have entered professional and public-sector workflows as interfaces for search, summarisation, preparation and control of knowledge around decisions. This expands the role of the provider and the internal software layer without establishing autonomous delegation of decision authority.",
    ),
}

SAFE_PATCHES = {
    "ARC_CONTROL_LEAKS_BUT_POLICES": (
        "Показывать измеримые эпизоды обхода и правоприменения отдельно. Наличие enforcement не доказывает полноту контроля, а отдельное изъятие не измеряет масштаб серого рынка.",
        "Present measured evasion and enforcement episodes separately. Enforcement does not establish complete control, and one seizure does not measure the scale of the grey market.",
    ),
    "ARC_CORPORATE_DECISION_SUPPORT_ADOPTION": (
        "Говорить, что ИИ становится интерфейсом вокруг решений, а не что он уже автономно принимает корпоративные или государственные решения.",
        "Say that AI is becoming an interface around decisions, not that it already makes corporate or public decisions autonomously.",
    ),
}

FAMILY_PATCHES = {
    "ARC_FAMILY_CYBER_COGNITION_WAR": {
        "label_ru": "Кибервозможности, устойчивость и когнитивная безопасность",
        "label_en": "Cyber capability, resilience and cognitive security",
        "summary_ru": "Кибервозможности моделей, реальные операции, защитный цикл, поведение агентов и целостность решений.",
        "summary_en": "Model cyber capabilities, operational evidence, the defensive lifecycle, agent behaviour and decision integrity.",
    },
    "ARC_FAMILY_DECISION_DATA_FINANCE": {
        "label_ru": "Решения, данные и отраслевые контуры",
        "label_en": "Decisions, data and sector systems",
        "summary_ru": "Лицензируемые данные, интерфейсы решений и их проявления в государственном управлении, финансах и военных циклах обратной связи.",
        "summary_en": "Licensed data, decision interfaces and their expression in public administration, finance and military feedback loops.",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def localised(doc: dict, ru, en):
    return ru if doc["language"] == "ru" else en


def patch_arc_text(arc: dict, key: str, ru, en, lang: str) -> None:
    arc[f"{key}_ru"] = ru
    arc[f"{key}_en"] = en
    arc[key] = ru if lang == "ru" else en


def event_arc_candidates(doc: dict) -> dict[str, set[str]]:
    by_event = {event["id"] for event in doc["events"]}
    candidates = {event_id: set() for event_id in by_event}
    for event in doc["events"]:
        candidates[event["id"]].update(arc_id for arc_id in event.get("arcIds", []) if arc_id in ARC_LAYOUT)
    for arc in doc["arcs"]:
        for node_id in arc.get("key_nodes", []):
            if node_id in candidates:
                candidates[node_id].add(arc["id"])
    for edge in doc["edges"]:
        if edge.get("relation") == "part_of_arc" and edge.get("source") in candidates:
            target = edge.get("target")
            if target in ARC_LAYOUT:
                candidates[edge["source"]].add(target)
    return candidates


def assign_display_membership(doc: dict) -> None:
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    family_rank = {family_id: index for index, family_id in enumerate(FAMILY_ORDER)}
    role_rank = {
        "case": 0,
        "sector_case": 1,
        "submechanism": 2,
        "mechanism": 3,
        "qualifier": 4,
        "timeline_lens": 5,
        "timeline_marker": 6,
    }
    candidates = event_arc_candidates(doc)
    for event in doc["events"]:
        existing_order = {arc_id: index for index, arc_id in enumerate(event.get("arcIds", []))}
        choices = sorted(
            candidates[event["id"]],
            key=lambda arc_id: (
                role_rank.get(arcs[arc_id].get("display_role"), 99),
                0 if arc_id in existing_order else 1,
                existing_order.get(arc_id, 999),
                family_rank.get(arcs[arc_id].get("family_id"), 99),
                arcs[arc_id].get("display_order", 999),
                arc_id,
            ),
        )
        if not choices:
            event.pop("story_primary_arc_id", None)
            event.pop("story_secondary_arc_ids", None)
            continue
        event["story_primary_arc_id"] = choices[0]
        event["story_secondary_arc_ids"] = choices[1:]


def patch_document(doc: dict) -> None:
    lang = doc["language"]
    arcs = {arc["id"]: arc for arc in doc["arcs"]}
    if set(arcs) != set(ARC_LAYOUT):
        missing = sorted(set(arcs) ^ set(ARC_LAYOUT))
        raise ValueError(f"Arc layout does not cover the exact v0.37 arc set: {missing}")

    for family in doc["arcFamilies"]:
        family["display_order"] = FAMILY_ORDER.index(family["id"]) + 1
        family.update(FAMILY_PATCHES.get(family["id"], {}))

    for arc_id, (role, order, parent, visible, family_move) in ARC_LAYOUT.items():
        arc = arcs[arc_id]
        arc["display_role"] = role
        arc["display_order"] = order
        arc["default_visible"] = visible
        arc["parent_arc_id"] = parent
        if family_move:
            arc["family_id"] = family_move
        if arc_id in TITLE_PATCHES:
            patch_arc_text(arc, "title", *TITLE_PATCHES[arc_id], lang)
        if arc_id in THESIS_PATCHES:
            patch_arc_text(arc, "thesis", *THESIS_PATCHES[arc_id], lang)
        if arc_id in SAFE_PATCHES:
            patch_arc_text(arc, "safe_wording", *SAFE_PATCHES[arc_id], lang)

    edge_family_reassignments = 0
    for edge in doc["edges"]:
        if edge.get("arc_id") in arcs:
            family_id = arcs[edge["arc_id"]]["family_id"]
            edge_family_reassignments += edge.get("arc_family_id") != family_id
            edge["arc_family_id"] = family_id

    membership_recomputations = {}
    for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"]:
        changed = 0
        for node in doc.get(collection, []):
            arc_ids = [arc_id for arc_id in node.get("arcIds", []) if arc_id in arcs]
            if arc_ids:
                family_ids = list(dict.fromkeys(arcs[arc_id]["family_id"] for arc_id in arc_ids))
                changed += node.get("arcFamilyIds") != family_ids
                node["arcFamilyIds"] = family_ids
        if changed:
            membership_recomputations[collection] = changed

    assign_display_membership(doc)
    primary_count = sum(bool(event.get("story_primary_arc_id")) for event in doc["events"])
    multi_count = sum(bool(event.get("story_secondary_arc_ids")) for event in doc["events"])
    role_counts = dict(Counter(arc["display_role"] for arc in doc["arcs"]))
    doc["arcHierarchy"] = {
        "version": "1.0",
        "default_mode": "mechanisms",
        "family_order": FAMILY_ORDER,
        "role_counts": role_counts,
        "role_definitions": [
            {"id": "mechanism", "label_ru": "основной механизм", "label_en": "core mechanism"},
            {"id": "submechanism", "label_ru": "подмеханизм", "label_en": "submechanism"},
            {"id": "qualifier", "label_ru": "уточнение", "label_en": "qualifier"},
            {"id": "case", "label_ru": "кейс", "label_en": "case"},
            {"id": "sector_case", "label_ru": "отраслевой кейс", "label_en": "sector case"},
            {"id": "timeline_lens", "label_ru": "временная линза", "label_en": "timeline lens"},
            {"id": "timeline_marker", "label_ru": "временная отметка", "label_en": "timeline marker"},
        ],
        "method_note_ru": "Иерархия определяет маршрут чтения, а не силу доказательства. Один факт получает основную позицию для показа; все прежние тематические и доказательные связи сохраняются.",
        "method_note_en": "The hierarchy defines a reading route, not evidentiary strength. Each classified fact receives one primary display position while all previous thematic and evidentiary links remain.",
        "primary_event_assignments": primary_count,
        "events_with_secondary_arcs": multi_count,
    }

    doc["summary"]["arc_hierarchy"] = {
        "families": len(doc["arcFamilies"]),
        "core_mechanisms": role_counts.get("mechanism", 0),
        "nested_cases_and_qualifiers": sum(role_counts.get(role, 0) for role in ["submechanism", "qualifier", "case", "sector_case"]),
        "timeline_records": role_counts.get("timeline_lens", 0) + role_counts.get("timeline_marker", 0),
        "total_arc_records": len(doc["arcs"]),
    }

    doc.setdefault("presentation", {})["release_notes"] = (
        [
            {
                "title": "От плоского списка к механизму",
                "text": "На первом уровне остаются 13 механизмов в шести семействах. Кейсы, подмеханизмы, уточнения и временные линзы сохранены, но больше не конкурируют с ними как равноправные сюжеты.",
            },
            {
                "title": "Связи не потеряны",
                "text": "Основной маршрут нужен только для размещения факта на карте. Все прежние идентификаторы, тематические принадлежности, доказательные рёбра, даты и источники сохранены.",
            },
        ]
        if lang == "ru"
        else [
            {
                "title": "From a flat list to mechanisms",
                "text": "The first level now contains 13 mechanisms in six families. Cases, submechanisms, qualifiers and timeline lenses remain available without competing as peer stories.",
            },
            {
                "title": "No links were discarded",
                "text": "A primary route only places a fact on the map. All previous identifiers, thematic memberships, evidentiary edges, dates and sources remain intact.",
            },
        ]
    )

    doc["meta"].update(
        version=VERSION,
        updated_at=DATE,
        schema_version="ai_stack_structural_power.v0.38.0-2026-09-14",
    )
    entry = {
        "version": VERSION,
        "date": DATE,
        "description": "Editorial hierarchy separates core mechanisms, nested submechanisms, qualifiers, cases and timeline lenses without removing legacy records or links.",
        "added_evidence": 0,
        "added_claims": 0,
        "added_claim_checks": 0,
        "added_story_arcs": 0,
        "added_story_edges": 0,
        "restructured_story_arcs": len(doc["arcs"]),
    }
    doc["meta"]["changelog"] = [entry] + [item for item in doc["meta"].get("changelog", []) if item.get("version") != VERSION]
    doc.setdefault("migrationAudit", {})["v038_arc_hierarchy"] = {
        "date": DATE,
        "source_version": "0.37",
        "preserved_counts": {key: len(doc[key]) for key in ["events", "claims", "claimChecks", "arcs", "edges", "sourceIndex"]},
        "family_order": FAMILY_ORDER,
        "role_counts": role_counts,
        "renamed_arc_ids": sorted(TITLE_PATCHES),
        "family_reassignment": {"ARC_WAR_DATA_FLYWHEEL": "ARC_FAMILY_DECISION_DATA_FINANCE"},
        "primary_event_assignments": primary_count,
        "events_with_secondary_arcs": multi_count,
        "semantic_edge_changes": 0,
        "edge_family_metadata_reassignments": edge_family_reassignments,
        "arc_family_membership_recomputations": membership_recomputations,
        "removed_ids": [],
    }
    doc["referenceIntegrity"] = references(doc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    for lang in ["ru", "en"]:
        source = args.root / f"ai_power_storygraph_{lang}.json"
        actual = sha256(source)
        if actual != PINNED_SHA256[lang]:
            raise SystemExit(f"Pinned {lang} input mismatch: {actual}")
        doc = json.loads(source.read_text(encoding="utf-8"))
        if doc["meta"].get("version") != "0.37":
            raise SystemExit(f"Expected v0.37 {lang} input")
        patch_document(doc)
        target = args.output / source.name
        target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(target, len(doc["events"]), len(doc["arcs"]), len(doc["edges"]))


if __name__ == "__main__":
    main()
