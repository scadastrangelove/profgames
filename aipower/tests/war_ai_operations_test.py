#!/usr/bin/env python3
"""Regression checks for the v0.39 military-AI operations update."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review/war-ai-operations-september-2026/candidates.json"
EVENT_IDS = {
    "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE",
    "SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING",
    "SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS",
    "SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP",
    "SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT",
    "SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT",
    "SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE",
}


def load(lang):
    return json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text(encoding="utf-8"))


def main():
    raw = json.loads(PACKAGE.read_text(encoding="utf-8"))
    docs = {lang: load(lang) for lang in ["ru", "en"]}
    assert len(raw["events"]) == 7
    assert len(raw["deferred"]) == 6

    for lang, doc in docs.items():
        events = {event["id"]: event for event in doc["events"]}
        arcs = {arc["id"]: arc for arc in doc["arcs"]}
        checks = {claim["id"]: claim for claim in doc["claimChecks"]}
        assert doc["meta"]["version"] == "0.39"
        assert (len(doc["events"]), len(doc["claims"]), len(doc["claimChecks"]), len(doc["arcs"]), len(doc["edges"])) == (394, 73, 32, 26, 941)
        assert EVENT_IDS <= events.keys()
        assert len({source["url"] for source in doc["sourceIndex"]}) == len(doc["sourceIndex"]) == 583
        assert doc["referenceIntegrity"]["valid"]
        assert doc["arcHierarchy"]["role_counts"]["mechanism"] == 13
        assert sum(arc["display_role"] == "mechanism" for arc in doc["arcs"]) == 13

        maven = events["SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE"]
        assert maven["date"] == "2026-05-07"
        assert maven["numbers"]["campaign_targets_reported"] == 13000
        assert "autonom" in maven["safe_wording_en"].lower()
        assert maven["story_primary_arc_id"] == "ARC_PALANTIR_DECISION_OS"

        odin = events["SIG_2026_USMC_ODIN_AUTHORITATIVE_REPORTING"]
        assert odin["date"] == "2026-07-07"
        assert odin["normative_force"] == "binding"
        assert odin["implementation_stage"] == "effective"

        avengers = events["SIG_2026_UKRAINE_AVENGERS_LABS_LICENSED_CORPUS"]
        assert avengers["numbers"] == {
            "annotated_frames": 5000000,
            "monthly_video_streams_more_than": 100000,
            "reported_target_detection_percent": 70,
        }
        assert avengers["normative_force"] == "contractual"

        partnership = events["SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP"]
        assert partnership["normative_force"] == "advisory"
        assert "not legally binding" in partnership["caveat_en"]

        talon = events["SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT"]
        assert talon["implementation_stage"] == "announced"
        assert "do not confirm launch" in talon["caveat_en"]

        gtg27005 = events["SIG_2026_ANTHROPIC_GTG27005_DRONE_SWARM_DEVELOPMENT"]
        assert gtg27005["delegated_authority"] == "evaluated"
        assert gtg27005["numbers"]["reported_maturity"] == "TRL 3-4"
        assert "state entity" in gtg27005["caveat_en"]

        gtg30005 = events["SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE"]
        assert gtg30005["delegated_authority"] == "observed"
        assert gtg30005["cyber_role_ids"] == ["AI_ROLE_ATTACK_ENABLER"]

        assert "SIG_2026_US_MAVEN_EPIC_FURY_OPERATIONAL_USE" in arcs["ARC_PALANTIR_DECISION_OS"]["key_nodes"]
        assert "SIG_2026_UK_UKRAINE_AVENGERS_AI_PARTNERSHIP" in arcs["ARC_WAR_DATA_FLYWHEEL"]["key_nodes"]
        assert "SIG_2026_US_UAE_TALON_SYNAPSE_ANNOUNCEMENT" in checks["CLM_003_GULF_PROTECTORATE"]["supporting_evidence"]
        assert checks["CLM_024_WAR_DATA_FLYWHEEL"]["confidence"] == "A/B"
        assert len(doc["migrationAudit"]["v039_added_edge_ids"]) == 46
        assert doc["factcheckAudit"]["v039_war_ai_operations"]["autonomous_field_action_inferred"] is False

    ru, en = docs["ru"], docs["en"]
    assert [(edge["id"], edge["source"], edge["target"], edge["relation"]) for edge in ru["edges"]] == [
        (edge["id"], edge["source"], edge["target"], edge["relation"]) for edge in en["edges"]
    ]
    assert [(event["id"], event["date"], event["story_primary_arc_id"]) for event in ru["events"] if event["id"] in EVENT_IDS] == [
        (event["id"], event["date"], event["story_primary_arc_id"]) for event in en["events"] if event["id"] in EVENT_IDS
    ]
    print("war AI operations checks passed", len(EVENT_IDS), "events", 46, "edges")


if __name__ == "__main__":
    main()
