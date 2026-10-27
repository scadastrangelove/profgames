#!/usr/bin/env python3
"""Replay v0.48; check preservation, deduplication, bounded claims and chronology."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lab_incidents_test import baseline as v046_baseline
import migrate_lab_incidents as prior
import migrate_knowledge_gatekeeping as release
from validate import references


def baseline(lang):
    doc = prior.migrate(v046_baseline(lang))
    doc["migrationAudit"]["v047_base_sha256"] = prior.BASE_HASH[lang]
    payload = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode()
    assert hashlib.sha256(payload).hexdigest() == release.BASE_HASH[lang], "Pinned baseline changed"
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
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        expected = release.migrate(copy.deepcopy(old))
        expected["migrationAudit"]["v048_base_sha256"] = release.BASE_HASH[lang]
        docs[lang] = doc
        ok(lang+": deterministic migration replay", expected == doc)
        ev = {e["id"]: e for e in doc["events"]}
        newids = {r["id"] for r in release.RECORDS}
        ok(lang+": 14 new unique records", len(newids)==14 and len(ev)==460 and set(ev)-{e["id"] for e in old["events"]}==newids)
        ok(lang+": all 446 old event bodies unchanged", len(old["events"])==446 and all(content(e)==content(ev[e["id"]]) for e in old["events"]))
        ok(lang+": all 1125 old edges unchanged", len(old["edges"])==1125 and all(e in doc["edges"] for e in old["edges"]))
        for collection in ["claims", "claimChecks", "gaps", "counterarguments", "thesisNodes"]:
            byid = {x["id"]:x for x in doc[collection]}
            ok(lang+": preserve old " + collection, all(content(x)==content(byid[x["id"]]) for x in old[collection]))
        ok(lang+": all old source IDs retained", {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]})
        sources = [s for s in doc["sourceIndex"] if s["id"] not in {x["id"] for x in old["sourceIndex"]}]
        oldurls = {urlkey(s["url"]) for s in old["sourceIndex"]}
        ok(lang+": 16 new distinct URLs", len(sources)==16 and len({urlkey(s["url"]) for s in sources})==16 and not oldurls & {urlkey(s["url"]) for s in sources})
        ok(lang+": no new top-level arc", [x["id"] for x in old["arcs"]]==[x["id"] for x in doc["arcs"]])
        ok(lang+": connectivity counts all 26 arcs", doc["connectivity"]["computed_arc_count"]==len(doc["arcs"])==26 and set(doc["connectivity"]["computed_arc_to_thesis_counts"])=={a["id"] for a in doc["arcs"]})
        thesis_ids = {t["id"] for t in old["thesisNodes"]}
        prior_missing = [a["id"] for a in old["arcs"] if not any(e["source"]==a["id"] and e["target"] in thesis_ids for e in old["edges"])]
        ok(lang+": no new arc loses a direct thesis link", doc["connectivity"]["computed_hanging_arcs"]==prior_missing==["ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL"])
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V048_")]
        signature = lambda e: (e["source"], e["target"], e["relation"], e["arc_id"])
        ok(lang+": 44 new links, no duplicates", len(edges)==44 and len({signature(e) for e in edges})==44 and not {signature(e) for e in edges}&{signature(e) for e in old["edges"]})
        ok(lang+": 23 thematic memberships", sum(e["relation"]=="part_of_arc" and e["relationship_class"]=="thematic" for e in edges)==23)
        ok(lang+": SP connection editorial not replication", all(e["relationship_class"]=="editorial_relationship" and e["relation"]=="context_for" for e in edges if e["target"]==release.SP))
        ok(lang+": TLS has no invented causal support", all(e["relation"] in {"qualifies", "context_for", "part_of_arc"} for e in edges if e["source"] in {"SIG_2022_RUSSIAN_DOMAIN_TLS_FRAGMENTATION_STUDY", "SIG_2026_SFR_BROWSER_CERTIFICATE_GUIDANCE"}))
        for r in release.RECORDS:
            e = ev[r["id"]]
            ok(lang+": localized record " + e["id"], all(e[k]==e[k+"_"+lang] and e[k+"_ru"] and e[k+"_en"] for k in ["title", "summary", "safe_wording", "caveat", "scope"]))
            ok(lang+": localized observation period " + e["id"], e["observation_period"]==e["observation_period_"+lang])
            ok(lang+": source URLs indexed " + e["id"], all(s["url"] in {x["url"] for x in doc["sourceIndex"]} for s in e["sources"]))
            ok(lang+": dates not ingestion time " + e["id"], e["date"]<release.DATE and e["date_basis"] and e["date_precision"]==("month" if len(e["date"])==7 else "day"))
            ok(lang+": no incident or independent replication " + e["id"], e["artifact_kind"]!="incident" and not e["classification_review"]["independent_replication"] and not e["behavioral_status"])
            ok(lang+": vocabulary valid " + e["id"], set(e["evidence_context"])<={x["id"] for x in doc["cyberFramework"]["evidence_contexts"]} and e["artifact_kind"] in {x["id"] for x in doc["cyberFramework"]["artifact_kinds"]})
            ok(lang+": existing arc assignment " + e["id"], e["story_primary_arc_id"]==release.DATA and set(e["arcIds"])<=set(x["id"] for x in doc["arcs"]))
        ok(lang+": four relevant cyber entries", sum(bool(ev[i]["primary_domain_id"]) for i in newids)==4)
        ok(lang+": one new core cyber entry", sum(bool(ev[i]["primary_domain_id"]) and ev[i]["editorial_priority"]==1 for i in newids)==1)
        claim = next(c for c in doc["claims"] if c["id"]==release.CLAIM)
        ok(lang+": scoped partial claim with counterevidence", claim["status"]=="partially_verified" and len(claim["qualifying_evidence"])==4)
        ok(lang+": TLS gap remains open", next(g for g in doc["gaps"] if g["id"]==release.GAP)["status"]=="open")
        ok(lang+": unknown SFR publication date retained", ev["SIG_2026_SFR_BROWSER_CERTIFICATE_GUIDANCE"]["source_date"]=="" and "publication_date_unknown" in ev["SIG_2026_SFR_BROWSER_CERTIFICATE_GUIDANCE"]["date_basis"])
        ok(lang+": IMC day not invented", ev["SIG_2022_RUSSIAN_DOMAIN_TLS_FRAGMENTATION_STUDY"]["date"]=="2022-10")
        ok(lang+": rollout distinguished from announcement", ev["SIG_2026_GOOGLE_AI_SEARCH_OPTOUT_GLOBAL_ROLLOUT"]["date"]=="2026-08-31" and ev["SIG_2026_GOOGLE_AI_SEARCH_OPTOUT_GLOBAL_ROLLOUT"]["source_date"]=="2026-06-03")
        ok(lang+": Pew sample and endpoint explicit", ev["SIG_2025_PEW_AI_SUMMARY_CLICK_OBSERVATION"]["numbers"]["participants"]==900 and "random" in ev["SIG_2025_PEW_AI_SUMMARY_CLICK_OBSERVATION"]["caveat_en"])
        for arc in doc["arcs"]:
            oldarc = next(a for a in old["arcs"] if a["id"]==arc["id"])
            ok(lang+": old checkpoints retained " + arc["id"], set(oldarc["key_nodes"])<=set(arc["key_nodes"]))
            if arc["id"] in {release.DATA, release.COG, release.ACCESS}:
                dates = [ev[n]["date"] for n in arc["key_nodes"] if n in ev]
                ok(lang+": checkpoints chronological " + arc["id"], dates==sorted(dates))
        ok(lang+": references resolve", references(doc)==doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', (ROOT/htmlname).read_text(), re.S)
        ok(lang+": HTML embeds exact JSON", bool(embedded) and json.loads(embedded.group(1))==doc)
        try:
            release.migrate(copy.deepcopy(doc))
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang+": repeat migration rejected", rejected)
    for collection in ["events", "claims", "arcs", "edges", "sourceIndex", "gaps"]:
        ok("RU/EN identities " + collection, [x["id"] for x in docs["ru"][collection]]==[x["id"] for x in docs["en"][collection]])
    report.update(passed=True, assertions=len(report["checks"]))
    (release.PACKET/"tests-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__ == "__main__":
    main()
