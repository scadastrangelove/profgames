#!/usr/bin/env python3
"""Offline preservation, provenance, chronology and bilingual checks for v0.42."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_agent_boundaries import (
    BEHAVIOR, CITATION, CLAIM, COG, CYBER, DECEPTION, DNS, IMAGES, INJECTION, KEYS,
    MEDICARE, PACING, PREPRINT, RESILIENCE, RESPONSE, TRACK, WORKBOOK, migrate,
)
from validate import references


def main():
    package = ROOT / "review/agent-boundaries-september-2026"
    packet = json.loads((package / "candidates.json").read_text())
    base = packet["meta"]["atlas_commit_reviewed"]
    report = {"version": "0.42", "base_commit": base, "checks": []}

    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)

    docs, originals = {}, {}
    regenerate = "--regenerate-from-baseline" in sys.argv
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        name = f"ai_power_storygraph_{lang}.json"
        raw = subprocess.check_output(["git", "show", f"{base}:aipower/{name}"], cwd=ROOT)
        originals[lang] = raw
        old = json.loads(raw)
        if regenerate:
            ok(lang + ": pinned baseline hash", hashlib.sha256(raw).hexdigest() == packet["meta"]["base_sha256"][lang])
            docs[lang] = migrate(copy.deepcopy(old), packet)
            continue
        doc = json.loads((ROOT / name).read_text())
        docs[lang] = doc
        ok(lang + ": pinned baseline hash", hashlib.sha256(raw).hexdigest() == packet["meta"]["base_sha256"][lang])
        ok(lang + ": migration exactly reproduces JSON", migrate(copy.deepcopy(old), packet) == doc)
        ev = {e["id"]: e for e in doc["events"]}
        new_ids = {c["id"] for c in packet["events"]}
        ok(lang + ": nine records across five requested blocks", len(new_ids) == 9 and {c["block"] for c in packet["events"]} == set(range(1, 6)))
        ok(lang + ": only requested records added", set(ev) - {e["id"] for e in old["events"]} == new_ids)
        links = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        ok(lang + ": all existing event content preserved", all(
            {k: v for k, v in e.items() if k not in links} == {k: v for k, v in ev[e["id"]].items() if k not in links}
            for e in old["events"]))
        ok(lang + ": all previous edges unchanged", all(e in doc["edges"] for e in old["edges"]))
        ok(lang + ": thirty-one new explicit edges", len(doc["edges"]) == len(old["edges"]) + 31)
        old_sources = {s["url"]: s["id"] for s in old["sourceIndex"]}
        new_sources = {s["url"]: s["id"] for s in doc["sourceIndex"]}
        ok(lang + ": eleven new unique URLs, stable source IDs", len(new_sources) == len(old_sources) + 11 and all(new_sources.get(url) == id for url, id in old_sources.items()))
        for collection in ["claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"]:
            ok(lang + ": preserved IDs " + collection, {x["id"] for x in old[collection]} <= {x["id"] for x in doc[collection]})
        ok(lang + ": no added arcs", len(doc["arcs"]) == 26)
        ok(lang + ": every typed reference resolves", references(doc) == doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        for arc_id in [COG, CYBER, RESILIENCE, PACING]:
            arc = next(a for a in doc["arcs"] if a["id"] == arc_id)
            dates = [ev[id]["date"] for id in arc["key_nodes"] if id in ev]
            ok(lang + ": chronological arc " + arc_id, dates == sorted(dates) and max(dates) == arc["end_date"])
        framework = doc["cyberFramework"]
        enums = {
            "cyber_domain_ids": "domains", "cyber_subdomain_ids": "subdomains", "cyber_role_ids": "roles",
            "behavioral_mechanism_ids": "behavioral_mechanisms", "behavioral_status": "behavioral_statuses",
            "evidence_context": "evidence_contexts", "behavior_track_ids": "behavior_tracks",
            "concealment_targets": "concealment_targets", "persistence_media": "persistence_media",
        }
        for candidate in packet["events"]:
            e = ev[candidate["id"]]
            ok(lang + ": vocabulary " + e["id"], all(set(e[field]) <= {v["id"] for v in framework[vocab]} for field, vocab in enums.items()))
            ok(lang + ": bilingual title and summary " + e["id"], all(e[field] == e[field + "_" + lang] and e[field + "_ru"] and e[field + "_en"] for field in ["title", "summary", "caveat", "role_basis"]))
            ok(lang + ": sources preserved " + e["id"], {s["url"] for s in e["sources"]} == {packet["sources"][id]["url"] for id in candidate["source_ids"]})
            ok(lang + ": event not dated by migration " + e["id"], e["date"] == candidate["date"] and e["date"] != "2026-09-28")
        ok(lang + ": DNS pause explicitly as-of report", ev[DNS]["date"] == "2026-09-20" and ev[DNS]["status_as_of"] == "2026-09-25")
        ok(lang + ": API misuse and fabrication stay one record", ev[KEYS]["date"] == "2026-05-15" and ev[KEYS]["numbers"]["fabricated_values"] == 9)
        ok(lang + ": compaction dates precede disclosures", ev[DECEPTION]["date"] == "2026-05-30" and ev[INJECTION]["date"] == "2026-07-18" and ev[DECEPTION]["source_date"] == ev[INJECTION]["source_date"] == "2026-09-16")
        ok(lang + ": compaction reduction retained", ev[DECEPTION]["numbers"] == {"sol_flagged_compaction_percent": 2.15, "astra_flagged_compaction_percent": 0.27})
        ok(lang + ": twenty-seven summaries not takeovers", ev[INJECTION]["numbers"] == {"flagged_jailbreak_style_summaries": 27} and ev[INJECTION]["concealment_targets"] == ["none"])
        ok(lang + ": image uploads have no invented incident date", ev[IMAGES]["incident_date"] is None and ev[IMAGES]["date_basis"] == "disclosure_date_incident_dates_unknown" and ev[IMAGES]["primary_or_secondary"] == "secondary")
        ok(lang + ": no guessed mapping of citation/photo dates", ev[CITATION]["date"] == "2026-09-16" and ev[CITATION]["sample_dates"] == ["2025-10-22", "2026-01-24"] and ev[CITATION]["date_status"] == "report_date_known_sample_mapping_unresolved")
        previous_behavior = next(c for c in old["claims"] if c["id"] == BEHAVIOR)
        current_behavior = next(c for c in doc["claims"] if c["id"] == BEHAVIOR)
        ok(lang + ": earlier behaviour synthesis retained", current_behavior["claim"].startswith(previous_behavior["claim"]))
        ok(lang + ": Australian incident and response separated", ev[MEDICARE]["date"] == "2026-06-18" and ev[RESPONSE]["date"] == "2026-09-24" and ev[RESPONSE]["artifact_kind"] == "government_program" and ev[RESPONSE]["normative_force"] == "not_applicable")
        ok(lang + ": Medicare technical attribution contested", ev[MEDICARE]["status"] == "partially_verified_contested" and len(ev[MEDICARE]["sources"]) == 4)
        ok(lang + ": response is not enacted legislation", ev[RESPONSE]["policy_adopted"] is False and ev[RESPONSE]["delegated_authority"] == "not_applicable")
        claim = next(c for c in doc["claims"] if c["id"] == CLAIM)
        ok(lang + ": narrow memory claim remains calibrated", claim["status"] == "partially_verified" and set(claim["supporting_evidence"]) == {DECEPTION, INJECTION})
        sp_edges = [e for e in doc["edges"] if e["source"] == PREPRINT and e["target"] in {DECEPTION, INJECTION}]
        ok(lang + ": Selective Permeability links are interpretation", len(sp_edges) == 2 and all(e["relation"] == "context_for" and e["relationship_class"] == "editorial_relationship" for e in sp_edges))
        incident_track = next(t for t in framework["resilience_tracks"] if t["id"] == "RES_TRACK_INCIDENT_LEARNING")
        ok(lang + ": incident-learning track integrated", {DNS, MEDICARE, RESPONSE} <= set(incident_track["event_ids"]) and all(incident_track["id"] in ev[id]["resilience_track_ids"] for id in [DNS, MEDICARE, RESPONSE]))
        ok(lang + ": four new concealment-track records", all(TRACK in ev[id]["behavior_track_ids"] for id in [KEYS, DECEPTION, INJECTION, WORKBOOK]))
        html = (ROOT / filename).read_text()
        match = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S)
        ok(lang + ": HTML embeds current canonical data", match is not None and json.loads(match.group(1)) == doc)
    if regenerate:
        for lang, doc in docs.items():
            (ROOT / f"ai_power_storygraph_{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        print("Rebuilt bilingual JSON from the pinned v0.41 baseline")
        return
    for collection in ["events", "claims", "edges", "sourceIndex"]:
        ok("bilingual identical IDs: " + collection, [e["id"] for e in docs["ru"][collection]] == [e["id"] for e in docs["en"][collection]])
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        for lang, raw in originals.items():
            (folder / f"ai_power_storygraph_{lang}.json").write_bytes(raw + (b" " if lang == "en" else b""))
        output = folder / "output"
        command = [sys.executable, str(ROOT / "scripts/migrate_agent_boundaries.py"), "--root", str(folder), "--output", str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        ok("changed English input leaves both outputs untouched", result.returncode != 0 and not output.exists() and "en: expected pinned" in result.stderr)
        command[command.index(str(folder))] = str(ROOT)
        result = subprocess.run(command, capture_output=True, text=True)
        ok("repeat migration rejected", result.returncode != 0 and not output.exists())
    report.update(passed=True, assertions=len(report["checks"]))
    (package / "tests-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))


if __name__ == "__main__":
    main()
