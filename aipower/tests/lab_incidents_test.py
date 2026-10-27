#!/usr/bin/env python3
"""Replay the pinned baseline and audit preservation, attribution, scope and chronology."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import migrate_platform_exit as prior
import migrate_lab_incidents as release
from validate import references


def baseline(lang):
    raw = subprocess.check_output(["git", "show", f"{prior.BASE}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
    doc = prior.migrate(json.loads(raw))
    doc["migrationAudit"]["v046_base_sha256"] = hashlib.sha256(raw).hexdigest()
    payload = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode()
    if hashlib.sha256(payload).hexdigest() != release.BASE_HASH[lang]:
        raise AssertionError("Reconstructed baseline differs from reviewed v0.46")
    return doc


def main():
    report = dict(version=release.VERSION, checks=[], duplicate_review=[])
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    derived = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
    def content(item):
        return {k:v for k,v in item.items() if k not in derived}
    def norm_url(url):
        u = urlsplit(url)
        return urlunsplit((u.scheme.lower(), u.netloc.lower(), u.path.rstrip("/"), u.query, ""))
    docs = {}
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        old = baseline(lang)
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        expected = release.migrate(copy.deepcopy(old))
        expected["migrationAudit"]["v047_base_sha256"] = release.BASE_HASH[lang]
        docs[lang] = doc
        ok(lang+": deterministic replay", doc == expected)
        ev = {e["id"]:e for e in doc["events"]}
        old_ev = {e["id"]:e for e in old["events"]}
        new_ids = {r["id"] for r in release.RECORDS}
        ok(lang+": exactly 16 unique new records", len(ev)==len(doc["events"]) and set(ev)-set(old_ev)==new_ids and len(new_ids)==16)
        ok(lang+": all 430 prior events retained", len(old_ev)==430 and set(old_ev)<=set(ev))
        ok(lang+": only five old event bodies changed", all(content(e)==content(ev[e["id"]]) for e in old["events"] if e["id"] not in release.UPDATED))
        ok(lang+": old event dates retained", all(e["date"]==ev[e["id"]]["date"] for e in old["events"]))
        ok(lang+": old numeric evidence retained", all(e.get("numbers")==ev[e["id"]].get("numbers") for e in old["events"]))
        ok(lang+": old event sources retained", all(s in ev[e["id"]].get("sources",[]) for e in old["events"] for s in e.get("sources",[])))
        ok(lang+": all 1079 old edges unchanged", len(old["edges"])==1079 and all(e in doc["edges"] for e in old["edges"]))
        ok(lang+": all old source IDs and URLs retained", {(s["id"],s["url"]) for s in old["sourceIndex"]}<={(s["id"],s["url"]) for s in doc["sourceIndex"]})
        ok(lang+": twenty new URLs", len({s["url"] for s in doc["sourceIndex"]}-{s["url"] for s in old["sourceIndex"]})==20)
        old_urls = {norm_url(s["url"]) for s in old["sourceIndex"]}
        new_sources = [s for s in doc["sourceIndex"] if s["id"] not in {x["id"] for x in old["sourceIndex"]}]
        ok(lang+": new sources do not duplicate normalized old URLs", not ({norm_url(s["url"]) for s in new_sources} & old_urls))
        ok(lang+": new sources unique after URL normalization", len({norm_url(s["url"]) for s in new_sources})==len(new_sources))
        for collection in ["claims", "claimChecks", "counterarguments", "gaps", "thesisNodes"]:
            current = {x["id"]:x for x in doc[collection]}
            ok(lang+": preserve unrelated " + collection, all(content(x)==content(current[x["id"]]) for x in old[collection] if x["id"]!=release.CLAIM))
        claim = next(c for c in doc["claims"] if c["id"]==release.CLAIM)
        ok(lang+": no claim certainty inflation", claim["status"]=="partially_verified" and claim["confidence"]=="B")
        ok(lang+": supporting and qualifying records retained", all(set(next(c for c in old["claims"] if c["id"]==release.CLAIM)[k])<=set(claim[k]) for k in ["supporting_evidence","qualifying_evidence"]))
        ok(lang+": no new top-level arc", [a["id"] for a in doc["arcs"]]==[a["id"] for a in old["arcs"]])
        edges = [e for e in doc["edges"] if e["id"].startswith("EDGE_V047_LAB_")]
        ok(lang+": 46 links with 33 non-evidential memberships", len(edges)==46 and sum(e["relation"]=="part_of_arc" and e["relationship_class"]=="thematic" for e in edges)==33)
        ok(lang+": comparisons do not imply causation", all(e["relationship_class"]=="editorial_relationship" for e in edges if e["relation"] in {"parallel","context_for"}))
        signatures = {(e["source"],e["target"],e["relation"],e.get("arc_id")) for e in old["edges"]}
        ok(lang+": no new duplicate semantic edges", not any((e["source"],e["target"],e["relation"],e.get("arc_id")) in signatures for e in edges))
        for raw in release.RECORDS:
            e = ev[raw["id"]]
            ok(lang+": bilingual record " + e["id"], all(e[k]==e[k+"_"+lang] and e[k+"_ru"] and e[k+"_en"] for k in ["title","summary","caveat","safe_wording","scope"]))
            ok(lang+": source links indexed " + e["id"], all(s["url"] in {x["url"] for x in doc["sourceIndex"]} for s in e["sources"]))
            ok(lang+": date and precision " + e["id"], e["date"]==raw["date"] and e["date_precision"]==("month" if len(raw["date"])==7 else "day"))
            ok(lang+": not independently reproduced " + e["id"], e["classification_review"]["independent_replication"] is False)
            ok(lang+": distinct title/date " + e["id"], not any(x["date"]==e["date"] and x["title"].casefold()==e["title"].casefold() for x in old["events"]))
        a = lambda suffix: ev["SIG_2026_"+suffix]["incident_assessment"]
        ok(lang+": BOCSAR negative finding", a("BOCSAR_INVESTIGATION_NO_BREACH")["outcome"]=="no_vulnerability_or_unauthorized_access_found")
        ok(lang+": BOCSAR not a vulnerability disclosure or observed attack", ev["SIG_2026_BOCSAR_INVESTIGATION_NO_BREACH"]["artifact_kind"]=="risk_report" and not ev["SIG_2026_BOCSAR_INVESTIGATION_NO_BREACH"]["behavioral_status"])
        ok(lang+": AIHW not a breach", a("AIHW_PROBES_NO_COMPROMISE")["outcome"]=="attempts_no_compromise_found")
        ok(lang+": VAHI authorisation remains uncertain", a("OPENAI_VAHI_EXPOSED_KEY_STATISTICS")["outcome"]=="access_reported_authorization_unclear")
        ok(lang+": Ruby attribution not acknowledged", a("RUBYGEMS_RUBYDOC_AGENT_ATTRIBUTION_DISPUTE")["attribution"]=="contested")
        ok(lang+": Canada provider not established", a("CANADA_ARCHIVES_UNSUCCESSFUL_AGENT_PROBES")["attribution"]=="provider_not_established")
        ok(lang+": incomplete public traces do not imply independent repeated agents", ev["SIG_2026_UNM_LIBRARY_UNSUCCESSFUL_AGENT_PROBES"]["agent_population_scope"]=="not_established")
        ok(lang+": Modal application distinct from platform", "Modal customer application" in ev[release.HF]["incident_assessment"]["targets"] and "not compromised" in ev[release.HF]["summary_en"])
        ok(lang+": AISI actions not runs", ev[release.AISI]["numbers"]["unsanctioned_actions"]==19 and ev[release.AISI]["numbers"]["runs_with_unsanctioned_actions"]==10)
        ok(lang+": no unique-victim aggregate", all(e["incident_assessment"]["unique_victim_total"] is None for e in doc["events"] if "incident_assessment" in e))
        study = ev["SIG_2026_ANTHROPIC_SELF_REPLICATION_CONTROLLED_STUDY"]
        ok(lang+": replication is controlled research not incident", study["artifact_kind"]=="research" and study["evidence_context"]==["controlled_simulation"] and "exploitation" in study["caveat_en"])
        sans = ev["SIG_2026_SANS_AI_SECURITY_WORKFORCE_SNAPSHOT"]
        ok(lang+": SANS sample not census or incident", sans["date"]=="2026-09" and sans["source_date"]=="2026-10-19" and sans["workforce_sample"]["census"] is False and sans["artifact_kind"]=="market_observation")
        ok(lang+": only six new core entries", sum(ev[i]["editorial_priority"]==1 for i in new_ids)==6)
        for arc in doc["arcs"]:
            if arc["id"] in {release.CYBER,release.COG,release.RES}:
                dates = [ev[n]["date"] for n in arc["key_nodes"] if n in ev]
                ok(lang+": chronological checkpoints " + arc["id"], dates==sorted(dates))
        ok(lang+": all reference fields resolve", references(doc)==doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        html = (ROOT / filename).read_text()
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>',html,re.S)
        ok(lang+": embedded HTML equals JSON", bool(embedded) and json.loads(embedded.group(1))==doc)
        try:
            release.migrate(copy.deepcopy(doc))
        except ValueError:
            rejected=True
        else:
            rejected=False
        ok(lang+": replay rejected", rejected)
    for collection in ["events","edges","sourceIndex"]:
        ok("bilingual identities " + collection,[x["id"] for x in docs["ru"][collection]]==[x["id"] for x in docs["en"][collection]])
    report["duplicate_review"] = [
        {"existing":release.UPDATED,"decision":"Update in place; retain prior sources and numeric evidence."},
        {"cohorts":"Google / Meta / Anthropic unnamed organisations","decision":"Separate disclosures; no additive victim count."},
        {"pair":[release.MEDICARE,"SIG_2026_OPENAI_GOV_STATISTICS_SECRETS_AUTH_BYPASS"],"decision":"Different disclosed tasks; anonymous target may overlap, not counted as a new unique victim."},
        {"pair":["SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE","SIG_2026_WIKIMEDIA_AGENT_ACTIVITY_INVESTIGATION"],"decision":"Researcher reconstruction versus affected-organisation investigation; not a second independent attack count."},
    ]
    report.update(passed=True,assertions=len(report["checks"]))
    release.PACKET.mkdir(parents=True,exist_ok=True)
    (release.PACKET / "tests-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted data checks")


if __name__ == "__main__":
    main()
