#!/usr/bin/env python3
"""Reproduce the institutional evidence merge and test preservation and deduplication."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_state_decision_power import BASE, PACKET, SPECS, canonical_url, migrate
from validate import references


def main():
    report = {"version": "0.44", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    packet = json.loads(PACKET.read_text())
    docs = {}
    ids = {s["id"] for s in SPECS}
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        raw = subprocess.check_output(["git", "show", f"{BASE}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        old = json.loads(raw)
        expected = migrate(copy.deepcopy(old), packet)
        expected["migrationAudit"]["v044_base_sha256"] = hashlib.sha256(raw).hexdigest()
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        docs[lang] = doc
        ok(lang + ": deterministic reproduction", doc == expected)
        ev = {e["id"]: e for e in doc["events"]}
        ok(lang + ": unique events and exactly ten additions", len(ev) == len(doc["events"]) and set(ev) - {e["id"] for e in old["events"]} == ids)
        derived = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        for e in old["events"]:
            ok(lang + ": preserved event " + e["id"], {k:v for k,v in e.items() if k not in derived} == {k:v for k,v in ev[e["id"]].items() if k not in derived})
        ok(lang + ": old edges unchanged", all(e in doc["edges"] for e in old["edges"]))
        for collection in ["claims", "claimChecks", "counterarguments", "gaps"]:
            ok(lang + ": preserved " + collection, doc[collection] == old[collection])
        ok(lang + ": no new arcs", [a["id"] for a in doc["arcs"]] == [a["id"] for a in old["arcs"]])
        ok(lang + ": old source IDs preserved", {(s["id"],s["url"]) for s in old["sourceIndex"]} <= {(s["id"],s["url"]) for s in doc["sourceIndex"]})
        ok(lang + ": eleven additional sources", len(doc["sourceIndex"]) - len(old["sourceIndex"]) == 11)
        old_urls = {canonical_url(s["url"]) for s in old["sourceIndex"]}
        new_edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V044_STATE_")]
        ok(lang + ": 33 edges, 18 thematic", len(new_edges) == 33 and sum(e["relation"] == "part_of_arc" for e in new_edges) == 18)
        ok(lang + ": no causal shortcuts", not any(e["relation"] in ["causes", "accelerates_governance"] for e in new_edges))
        for eid in ids:
            event = ev[eid]
            ok(lang + ": new source " + eid, all(canonical_url(s["url"]) not in old_urls for s in event["sources"]))
            ok(lang + ": bilingual wording " + eid, all(event[k] == event[k+"_"+lang] and event[k+"_ru"] and event[k+"_en"] for k in ["title", "summary", "caveat", "safe_wording"]))
            ok(lang + ": no unsupported AI operational role " + eid, event["cyber_role_ids"] == [] and event["behavioral_status"] == [])
        consult = ev["SIG_2025_UK_CONSULT_PUBLIC_POLICY_PILOT"]
        ok(lang + ": disclosure is not incident date", consult["incident_date"] is None and consult["date"] == "2025-05-14" and consult["supplier_identification_published_at"] == "2025-07-21")
        arena = ev["SIG_2025_UK_DEFENCE_AI_MODEL_ARENA"]
        ok(lang + ": planned launch not deployed result", arena["planned_launch_month"] == "2026-03" and arena["operational_launch_verified"] is False)
        ok(lang + ": Model Arena qualifies dependence", any(e["source"] == arena["id"] and e["relation"] == "qualifies" for e in new_edges))
        ok(lang + ": Genesis separate dated stages", [ev[s["id"]]["date"] for s in SPECS if "GENESIS" in s["id"]] == ["2025-11-24", "2025-12-18", "2026-02-09"])
        ok(lang + ": Diella is not a commercial actor", "company" not in ev["SIG_2025_ALBANIA_DIELLA_PM_RESPONSIBILITY"]["actor_types"])
        for aid in {a for eid in ids for a in ev[eid]["arcIds"]}:
            arc = next(a for a in doc["arcs"] if a["id"] == aid)
            dates = [ev[i]["date"] for i in arc["key_nodes"] if i in ev]
            ok(lang + ": chronological arc " + aid, dates == sorted(dates))
        ok(lang + ": references resolve", references(doc) == doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', (ROOT / filename).read_text(), re.S)
        ok(lang + ": HTML data parity", embedded is not None and json.loads(embedded.group(1)) == doc)
        try:
            migrate(copy.deepcopy(doc), packet)
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang + ": repeat merge rejected", rejected)
    for collection in ["events", "edges", "sourceIndex"]:
        ok("bilingual IDs " + collection, [x["id"] for x in docs["ru"][collection]] == [x["id"] for x in docs["en"][collection]])
    report.update(passed=True, assertions=len(report["checks"]), dedup=docs["en"]["researchAudit"]["state_decision_power"])
    (PACKET.parent / "tests-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__ == "__main__":
    main()
