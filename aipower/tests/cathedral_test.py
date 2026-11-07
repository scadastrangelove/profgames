#!/usr/bin/env python3
"""Replay the release; check preservation, attribution and relationship semantics."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from october_access_test import baseline as v048_baseline
import migrate_october_access as prior
import migrate_cathedral as release
from validate import references


def baseline(lang):
    doc = prior.migrate(v048_baseline(lang))
    doc["migrationAudit"]["v049_base_sha256"] = prior.BASE_HASH[lang]
    payload = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode()
    assert hashlib.sha256(payload).hexdigest() == release.BASE_HASH[lang]
    return doc


def main():
    report = dict(version=release.VERSION, passed=False, checks=[])
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
        expected["migrationAudit"]["v050_base_sha256"] = release.BASE_HASH[lang]
        docs[lang] = doc
        ok(lang+": exact deterministic migration replay", expected==doc)
        ev = {e["id"]:e for e in doc["events"]}
        newids = {r["id"] for r in release.RECORDS}
        ok(lang+": two new unique records", len(ev)==469 and len(doc["events"])==len(ev) and set(ev)-{e["id"] for e in old["events"]}==newids)
        ok(lang+": all 467 old event bodies retained", len(old["events"])==467 and all(content(e)==content(ev[e["id"]]) for e in old["events"]))
        ok(lang+": all 1189 old edges retained exactly", len(old["edges"])==1189 and all(e in doc["edges"] for e in old["edges"]))
        for collection in ["claims", "gaps", "counterarguments", "thesisNodes"]:
            byid = {x["id"]:x for x in doc[collection]}
            ok(lang+": preserve "+collection, all(content(x)==content(byid[x["id"]]) for x in old[collection]))
        checks = {x["id"]:x for x in doc["claimChecks"]}
        ok(lang+": other claim checks unchanged", all(content(x)==content(checks[x["id"]]) for x in old["claimChecks"] if x["id"]!=release.CLAIM))
        before = next(x for x in old["claimChecks"] if x["id"]==release.CLAIM)
        after = checks[release.CLAIM]
        ok(lang+": authority claim only gains scoped support", set(before["supporting_evidence"])|{release.SI_FORCE}==set(after["supporting_evidence"]) and all(after[k]==v for k,v in content(before).items() if k not in {"supporting_evidence","sources"}))
        oldsourceids = {s["id"] for s in old["sourceIndex"]}
        ok(lang+": all old source IDs and URLs retained", {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]})
        oldurls = {urlkey(s["url"]) for s in old["sourceIndex"]}
        newsources = [s for s in doc["sourceIndex"] if s["id"] not in oldsourceids]
        ok(lang+": six distinct new URLs", len(doc["sourceIndex"])==680 and len(newsources)==6 and len({urlkey(s["url"]) for s in newsources})==6 and not oldurls & {urlkey(s["url"]) for s in newsources})
        ok(lang+": no new top-level arc", [a["id"] for a in old["arcs"]]==[a["id"] for a in doc["arcs"]])
        ok(lang+": no lost arc connectivity", doc["connectivity"]["computed_hanging_arcs"]==old["connectivity"]["computed_hanging_arcs"])
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V050_")]
        signature = lambda e:(e["source"],e["target"],e["relation"],e["arc_id"])
        ok(lang+": eight distinct new links", len(edges)==8 and len({signature(e) for e in edges})==8 and not {signature(e) for e in edges}&{signature(e) for e in old["edges"]})
        ok(lang+": five memberships are thematic only", sum(e["relation"]=="part_of_arc" and e["relationship_class"]=="thematic" for e in edges)==5)
        link = next(e for e in edges if e["source"]==release.CATHEDRAL and e["target"]==release.SI_FORCE)
        ok(lang+": no causal link between incidents", link["relation"]=="context_for" and link["relationship_class"]=="editorial_relationship")
        vocab = doc["cyberFramework"]
        for raw in release.RECORDS:
            e = ev[raw["id"]]
            ok(lang+": localized "+e["id"], all(e[k]==e[k+"_"+lang] and e[k+"_ru"] and e[k+"_en"] for k in ["title","summary","caveat","safe_wording","scope"]))
            ok(lang+": sources indexed "+e["id"], all(s["url"] in {s["url"] for s in doc["sourceIndex"]} for s in e["sources"]))
            ok(lang+": real publication date "+e["id"], e["date"]==raw["date"] and e["date"]<release.DATE and e["date_basis"]==raw["date_basis"])
            ok(lang+": not treated as lab escape "+e["id"], not e["behavioral_status"] and not e["behavioral_mechanism_ids"] and not e["classification_review"]["independent_replication"] and e["behavior_origin"]=="not_applicable")
            ok(lang+": classifier vocabulary "+e["id"], e["artifact_kind"] in {x["id"] for x in vocab["artifact_kinds"]} and e["normative_force"] in {x["id"] for x in vocab["normative_forces"]} and set(e["evidence_context"])<={x["id"] for x in vocab["evidence_contexts"]})
            ok(lang+": existing reading route "+e["id"], e["story_primary_arc_id"]==raw["arcs"][0] and set(e["arcIds"])<={a["id"] for a in doc["arcs"]})
        cat, force = ev[release.CATHEDRAL], ev[release.SI_FORCE]
        ok(lang+": disclosure not fabricated incident date", cat["artifact_kind"]=="disclosure" and cat["incident_date"] is None and cat["incident_date_precision"]=="unknown" and cat["autonomy_status"]=="not_established")
        ok(lang+": asserted obligation not binding-law label", force["artifact_kind"]=="supervisory_communication" and force["normative_force"]=="undetermined" and force["implementation_stage"]=="reported" and force["date"]<cat["date"])
        ok(lang+": public attribution limitations retained", "not independent" in cat["caveat_en"] and "specific permissions are unknown" in cat["caveat_en"] and "denied payment are not established" in cat["caveat_en"])
        ok(lang+": existing disclosure and Georgia correction unchanged", content(ev[release.DISCLOSURE])==content(next(e for e in old["events"] if e["id"]==release.DISCLOSURE)))
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
        ok(lang+": repeat migration rejected", rejected)
        duplicate = copy.deepcopy(old)
        duplicate["events"].append(cat)
        try:
            release.migrate(duplicate)
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang+": existing ID rejected", rejected)
    for collection in ["events","claims","arcs","edges","sourceIndex","gaps"]:
        ok("RU/EN identity parity "+collection,[x["id"] for x in docs["ru"][collection]]==[x["id"] for x in docs["en"][collection]])
    report.update(passed=True,assertions=len(report["checks"]))
    (release.PACKET/"tests-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__=="__main__":
    main()
