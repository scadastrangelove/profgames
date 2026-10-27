#!/usr/bin/env python3
"""Check evidence scope, chronology, duplicate handling and bilingual preservation."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_platform_exit import BASE, UK, NATO, PURCHASE, PAL, PARENT, LOCK, ALLIES, MITIGATION, PACKET, SOURCES, migrate
from validate import dates_preserved_or_corrected, references


def main():
    report = {"version": "0.46", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    docs = {}
    derived = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
    def content(item):
        return {k:v for k,v in item.items() if k not in derived}
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        raw = subprocess.check_output(["git", "show", f"{BASE}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        old = json.loads(raw)
        expected = migrate(copy.deepcopy(old))
        expected["migrationAudit"]["v046_base_sha256"] = hashlib.sha256(raw).hexdigest()
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        docs[lang] = doc
        ok(lang + ": deterministic migration", doc == expected)
        events = {e["id"]: e for e in doc["events"]}
        old_events = {e["id"]:e for e in old["events"]}
        ok(lang + ": one unique new event", len(events)==len(doc["events"]) and set(events)-set(old_events)=={NATO})
        ok(lang + ": no old event removed", set(old_events)<=set(events))
        ok(lang + ": only UK event content changed", all(content(e)==content(events[e["id"]]) for e in old["events"] if e["id"]!=UK))
        ok(lang + ": UK original amounts retained", old_events[UK]["numbers"]==events[UK]["numbers"])
        ok(lang + ": UK original sources retained", all(s in events[UK]["sources"] for s in old_events[UK]["sources"]))
        ok(lang + ": old edges unchanged", all(e in doc["edges"] for e in old["edges"]))
        ok(lang + ": old source identities preserved", {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]})
        ok(lang + ": four new source URLs", {s["url"] for s in doc["sourceIndex"]}-{s["url"] for s in old["sourceIndex"]}=={s["url"] for s in SOURCES.values()})
        ok(lang + ": mirror not independent corroboration", SOURCES["original"]["same_document_as"]==SOURCES["notice"]["url"] and doc["researchAudit"]["platform_exit"]["independent_new_documents"]==3)
        for collection in ["claims", "counterarguments", "gaps", "thesisNodes"]:
            current = {x["id"]:x for x in doc[collection]}
            ok(lang + ": preserved content " + collection, all(content(x)==content(current[x["id"]]) for x in old[collection]))
        checks = {x["id"]:x for x in doc["claimChecks"]}
        ok(lang + ": only three claim checks updated", all(content(x)==content(checks[x["id"]]) for x in old["claimChecks"] if x["id"] not in {LOCK,ALLIES,MITIGATION}))
        ok(lang + ": no claim-check status inflation", all((x["status"],x["confidence"])==(checks[x["id"]]["status"],checks[x["id"]]["confidence"]) for x in old["claimChecks"]))
        ok(lang + ": no new arcs", [a["id"] for a in doc["arcs"]]==[a["id"] for a in old["arcs"]])
        ok(lang + ": signing differs from publication", events[UK]["date"]=="2025-12-30" and events[UK]["source_date"]=="2026-02-24" and events[UK]["date_basis"]=="contract_signed_date")
        ok(lang + ": notice and mirror dates distinguished", events[UK]["notice_publication_date"]=="2025-12-17" and events[UK]["notice_mirror_date"]=="2025-12-18")
        ok(lang + ": NATO milestone differs from publication", events[NATO]["date"]=="2026-06-22" and events[NATO]["source_date"]=="2026-08-12")
        ok(lang + ": accreditation not assigned invented date", events[NATO]["security_accreditation_date"] is None)
        ok(lang + ": NATO not a country facet", not events[NATO]["jurisdictions"] and events[NATO]["institutional_scopes"]==["NATO"])
        ok(lang + ": UK not re-added as event", sum(e["id"]==UK for e in doc["events"])==1)
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V046_PLATFORM_")]
        ok(lang + ": eight links, three memberships", len(edges)==8 and sum(e["relation"]=="part_of_arc" for e in edges)==3)
        ok(lang + ": acquisition linked to readiness", any(e["source"]==PURCHASE and e["target"]==NATO and e["relation"]=="updated_by" for e in edges))
        ok(lang + ": UK-NATO comparison noncausal", any(e["source"]==UK and e["target"]==NATO and e["relationship_class"]=="editorial_relationship" and e["relation"]=="context_for" for e in edges))
        ok(lang + ": buyer rationale caveat", "not an independent estimate" in events[UK]["caveat_en"])
        ok(lang + ": model versus platform caveat", "platform replacement" in events[NATO]["caveat_en"] and "every headquarters" in events[NATO]["caveat_en"])
        for eid in [UK,NATO]:
            e = events[eid]
            ok(lang + ": bilingual fields " + eid, all(e[k]==e[k+"_"+lang] and e[k+"_ru"] and e[k+"_en"] for k in ["title","summary","caveat","safe_wording"]))
            ok(lang + ": no autonomous-agency inference " + eid, e["delegated_authority"]=="not_established" and e["artifact_kind"]=="deployment")
        for a in doc["arcs"]:
            if UK in a.get("key_nodes",[]) or NATO in a.get("key_nodes",[]):
                dates = [events[x]["date"] for x in a["key_nodes"] if x in events]
                ok(lang + ": chronological " + a["id"], dates==sorted(dates))
        baseline_dates = {e["id"]:e["date"] for e in old["events"]}
        ok(lang + ": correction audit valid", dates_preserved_or_corrected(doc, baseline_dates))
        bad = copy.deepcopy(doc)
        bad["factcheckAudit"]["v046_platform_exit"]["date_corrections"][0]["basis"]="https://example.invalid/"
        ok(lang + ": unlinked correction source rejected", not dates_preserved_or_corrected(bad, baseline_dates))
        bad = copy.deepcopy(doc)
        bad["events"][0]["date"]="2000-01-01"
        ok(lang + ": unlogged date change rejected", not dates_preserved_or_corrected(bad, baseline_dates))
        ok(lang + ": references valid and current", references(doc)==doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        html = (ROOT / filename).read_text()
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>',html,re.S)
        ok(lang + ": HTML data parity", embedded is not None and json.loads(embedded.group(1))==doc)
        try:
            migrate(copy.deepcopy(doc))
        except ValueError:
            rejected=True
        else:
            rejected=False
        ok(lang + ": replay rejected", rejected)
    for collection in ["events","edges","sourceIndex"]:
        ok("bilingual IDs " + collection,[x["id"] for x in docs["ru"][collection]]==[x["id"] for x in docs["en"][collection]])
    report.update(passed=True,assertions=len(report["checks"]))
    PACKET.mkdir(parents=True,exist_ok=True)
    (PACKET / "tests-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__ == "__main__":
    main()
