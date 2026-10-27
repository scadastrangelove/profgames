#!/usr/bin/env python3
"""Replay the release and test preservation, corrections and bounded interpretation."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from knowledge_gatekeeping_test import baseline as v047_baseline
import migrate_knowledge_gatekeeping as prior
import migrate_october_access as release
from validate import references


def baseline(lang):
    doc = prior.migrate(v047_baseline(lang))
    doc["migrationAudit"]["v048_base_sha256"] = prior.BASE_HASH[lang]
    payload = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode()
    assert hashlib.sha256(payload).hexdigest() == release.BASE_HASH[lang]
    return doc


def main():
    report = dict(version=release.VERSION, checks=[])
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    def content(node):
        return {k:v for k,v in node.items() if k not in {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}}
    def urlkey(url):
        u = urlsplit(url)
        return urlunsplit((u.scheme.lower(), u.netloc.lower(), u.path.rstrip("/"), u.query, ""))
    docs = {}
    for lang, htmlname in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        old = baseline(lang)
        doc = json.loads((ROOT/f"ai_power_storygraph_{lang}.json").read_text())
        expected = release.migrate(copy.deepcopy(old))
        expected["migrationAudit"]["v049_base_sha256"] = release.BASE_HASH[lang]
        docs[lang] = doc
        ok(lang+": exact deterministic migration replay", expected==doc)
        ev = {e["id"]:e for e in doc["events"]}
        newids = {r["id"] for r in release.RECORDS}
        updated = {release.DNS, release.ANTHROPIC}
        ok(lang+": seven new unique records", len(ev)==467 and set(ev)-{e["id"] for e in old["events"]}==newids and len(newids)==7)
        ok(lang+": 458 unchanged old event bodies", all(content(e)==content(ev[e["id"]]) for e in old["events"] if e["id"] not in updated))
        ok(lang+": all old event dates retained", all(e["date"]==ev[e["id"]]["date"] for e in old["events"]))
        ok(lang+": all 1169 old edges retained exactly", len(old["edges"])==1169 and all(e in doc["edges"] for e in old["edges"]))
        for collection in ["claims", "claimChecks", "gaps", "counterarguments", "thesisNodes"]:
            byid = {x["id"]:x for x in doc[collection]}
            ok(lang+": preserve "+collection, all(content(x)==content(byid[x["id"]]) for x in old[collection]))
        ok(lang+": all old source IDs and URLs retained", {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]})
        oldurls = {urlkey(s["url"]) for s in old["sourceIndex"]}
        newsources = [s for s in doc["sourceIndex"] if s["id"] not in {s["id"] for s in old["sourceIndex"]}]
        ok(lang+": nine distinct new URLs", len(newsources)==9 and len({urlkey(s["url"]) for s in newsources})==9 and not oldurls & {urlkey(s["url"]) for s in newsources})
        ok(lang+": no new top-level arc", [a["id"] for a in old["arcs"]]==[a["id"] for a in doc["arcs"]])
        ok(lang+": no lost arc connectivity", doc["connectivity"]["computed_hanging_arcs"]==old["connectivity"]["computed_hanging_arcs"])
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V049_")]
        signature = lambda e:(e["source"],e["target"],e["relation"],e["arc_id"])
        ok(lang+": twenty new links without duplicate signatures", len(edges)==20 and len({signature(e) for e in edges})==20 and not {signature(e) for e in edges}&{signature(e) for e in old["edges"]})
        ok(lang+": fourteen memberships are thematic only", sum(e["relation"]=="part_of_arc" and e["relationship_class"]=="thematic" for e in edges)==14)
        for raw in release.RECORDS:
            e = ev[raw["id"]]
            ok(lang+": localized "+e["id"], all(e[k]==e[k+"_"+lang] and e[k+"_ru"] and e[k+"_en"] for k in ["title","summary","caveat","safe_wording","scope"]))
            ok(lang+": indexed sources "+e["id"], all(s["url"] in {s["url"] for s in doc["sourceIndex"]} for s in e["sources"]))
            ok(lang+": dated event not ingestion "+e["id"], e["date"]<release.DATE and e["date_basis"] and e["date_precision"]=="day")
            ok(lang+": not counted as incident "+e["id"], e["artifact_kind"]!="incident" and not e["behavioral_status"] and not e["classification_review"]["independent_replication"])
            vocab = doc["cyberFramework"]
            ok(lang+": classifier vocabulary "+e["id"], e["artifact_kind"] in {x["id"] for x in vocab["artifact_kinds"]} and set(e["evidence_context"])<={x["id"] for x in vocab["evidence_contexts"]} and set(e.get("cyber_subdomain_ids",[]))<={x["id"] for x in vocab["subdomains"]})
            ok(lang+": existing route "+e["id"], e["story_primary_arc_id"]==raw["arcs"][0] and set(e["arcIds"])<={a["id"] for a in doc["arcs"]})
        for eid in updated:
            before = next(e for e in old["events"] if e["id"]==eid)
            after = ev[eid]
            ok(lang+": historical account retained "+eid, all(before[k]==after[k] for k in ["title","summary","date","source_date"]))
            ok(lang+": correction visible in caveat "+eid, after["current_state"]==after["current_state_"+lang] and after["current_state"] in after["caveat"])
            ok(lang+": prior caveats retained "+eid, all(c in after["caveat"] for c in before.get("caveats",[])))
        ok(lang+": resumption dated separately from disclosure", ev[release.IDS["openai"]]["date"]=="2026-10-01" and ev[release.IDS["openai"]]["source_date"]=="2026-10-23")
        ok(lang+": Swedish institutional scope and channels", ev[release.IDS["svt"]]["artifact_kind"]=="government_order" and "nationwide" in ev[release.IDS["svt"]]["caveat_en"] and "Intric" in ev[release.IDS["svt"]]["summary_en"])
        ok(lang+": Georgia correction not a new breach", ev[release.IDS["georgia"]]["artifact_kind"]=="commentary" and "relayed" in ev[release.IDS["georgia"]]["caveat_en"])
        ok(lang+": SpaceX commitment not closing", ev[release.IDS["spacex"]]["implementation_stage"]=="announced" and ev[release.IDS["spacex"]]["numbers"]["transaction_closed"] is False)
        ok(lang+": IBM position not benchmark", ev[release.IDS["ibm_call"]]["artifact_kind"]=="commentary" and "benchmark" not in ev[release.IDS["ibm_call"]]["evidence_context"])
        ok(lang+": Mozilla observation window retained", "September 1" in ev[release.IDS["mozilla"]]["observation_period_en"])
        ok(lang+": four cyber, two core additions", sum(bool(ev[i].get("primary_domain_id")) for i in newids)==4 and sum(bool(ev[i].get("primary_domain_id")) and ev[i]["editorial_priority"]==1 for i in newids)==2)
        for arc in doc["arcs"]:
            before = next(a for a in old["arcs"] if a["id"]==arc["id"])
            ok(lang+": checkpoints preserved "+arc["id"], set(before["key_nodes"])<=set(arc["key_nodes"]))
            if arc["id"] in {aid for r in release.RECORDS for aid in r["arcs"]}:
                dates = [ev[n]["date"] for n in arc["key_nodes"] if n in ev]
                ok(lang+": chronological "+arc["id"], dates==sorted(dates))
        ok(lang+": all typed references resolve", references(doc)==doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>',(ROOT/htmlname).read_text(),re.S)
        ok(lang+": exact HTML data parity", bool(embedded) and json.loads(embedded.group(1))==doc)
        try:
            release.migrate(copy.deepcopy(doc))
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang+": duplicate migration rejected", rejected)
    for collection in ["events","claims","arcs","edges","sourceIndex","gaps"]:
        ok("RU/EN identity parity "+collection,[x["id"] for x in docs["ru"][collection]]==[x["id"] for x in docs["en"][collection]])
    report.update(passed=True,assertions=len(report["checks"]))
    (release.PACKET/"tests-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__=="__main__":
    main()
