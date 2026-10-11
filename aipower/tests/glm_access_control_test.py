#!/usr/bin/env python3
"""Check deterministic migration, semantic boundaries and preservation of the corpus."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_glm_access_control import BASE, CAISI, CLAUDE, CYBER, GLM, PACKET, SOURCES, SPECS, canonical, migrate
from validate import references


def main():
    report = {"version": "0.45", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    docs = {}
    ids = {s["id"] for s in SPECS}
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        raw = subprocess.check_output(["git", "show", f"{BASE}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        old = json.loads(raw)
        expected = migrate(copy.deepcopy(old))
        expected["migrationAudit"]["v045_base_sha256"] = hashlib.sha256(raw).hexdigest()
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        docs[lang] = doc
        ok(lang + ": deterministic migration", doc == expected)
        events = {e["id"]: e for e in doc["events"]}
        ok(lang + ": exactly three unique additions", len(events) == len(doc["events"]) and set(events) - {e["id"] for e in old["events"]} == ids)
        derived = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        for e in old["events"]:
            ok(lang + ": preserved event " + e["id"], {k:v for k,v in e.items() if k not in derived} == {k:v for k,v in events[e["id"]].items() if k not in derived})
        ok(lang + ": every old edge preserved", all(e in doc["edges"] for e in old["edges"]))
        for collection in ["claims", "claimChecks", "counterarguments", "gaps", "thesisNodes"]:
            current = {x["id"]: x for x in doc[collection]}
            ok(lang + ": original content " + collection, all({k:v for k,v in x.items() if k not in derived} == {k:v for k,v in current[x["id"]].items() if k not in derived} for x in old[collection]))
        ok(lang + ": unchanged arc IDs", [x["id"] for x in doc["arcs"]] == [x["id"] for x in old["arcs"]])
        ok(lang + ": preserved source IDs", {(s["id"],s["url"]) for s in old["sourceIndex"]} <= {(s["id"],s["url"]) for s in doc["sourceIndex"]})
        ok(lang + ": three unique new sources", len(doc["sourceIndex"]) - len(old["sourceIndex"]) == 3 and not {canonical(s["url"]) for s in old["sourceIndex"]} & {canonical(s["url"]) for s in SOURCES.values()})
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V045_GLM_")]
        ok(lang + ": fourteen edges, nine thematic", len(edges) == 14 and sum(e["relation"] == "part_of_arc" for e in edges) == 9)
        ok(lang + ": noncausal comparison", all(e["relationship_class"] == "editorial_relationship" for e in edges if e["relation"] == "context_for"))
        for eid in ids:
            event = events[eid]
            ok(lang + ": cyber primary route " + eid, event["story_primary_arc_id"] == CYBER and event["editorial_priority"] == 1)
            ok(lang + ": bilingual fields " + eid, all(event[k] == event[k+"_"+lang] and event[k+"_ru"] and event[k+"_en"] for k in ["title", "summary", "caveat", "safe_wording"]))
            ok(lang + ": publication not incident date " + eid, event["date"] == event["source_date"] and event["incident_date"] is None)
        ok(lang + ": no fictional law", events[GLM]["normative_force"] == "not_applicable" and events[GLM]["artifact_kind"] == "evaluation")
        ok(lang + ": simulated engagement is explicit", "controlled_simulation" in events[GLM]["evidence_context"] and "simulation, not breaches" in events[GLM]["caveat_en"])
        ok(lang + ": live external effect is separate", "evaluation_with_real_effect" in events[CLAUDE]["evidence_context"] and events[CLAUDE]["date"] == "2026-10-09")
        ok(lang + ": benchmarks not field incidents", events[CAISI]["behavioral_status"] == ["capability_demonstrated"])
        vocab = doc["cyberFramework"]
        for eid in ids:
            event = events[eid]
            for field, key in [("behavioral_status", "behavioral_statuses"), ("evidence_context", "evidence_contexts"), ("behavioral_mechanism_ids", "behavioral_mechanisms"), ("cyber_subdomain_ids", "subdomains")]:
                ok(lang + ": vocabulary " + field + " " + eid, set(event[field]) <= {x["id"] for x in vocab[key]})
        for aid in {a for eid in ids for a in events[eid]["arcIds"]}:
            arc = next(a for a in doc["arcs"] if a["id"] == aid)
            dates = [events[e]["date"] for e in arc["key_nodes"] if e in events]
            ok(lang + ": chronological arc " + aid, dates == sorted(dates))
        ok(lang + ": reference integrity", references(doc) == doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', (ROOT / filename).read_text(), re.S)
        ok(lang + ": HTML parity", embedded is not None and json.loads(embedded.group(1)) == doc)
        try:
            migrate(copy.deepcopy(doc))
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang + ": repeated merge rejected", rejected)
    for collection in ["events", "edges", "sourceIndex"]:
        ok("bilingual IDs " + collection, [x["id"] for x in docs["ru"][collection]] == [x["id"] for x in docs["en"][collection]])
    report.update(passed=True, assertions=len(report["checks"]))
    (PACKET / "tests-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__ == "__main__":
    main()
