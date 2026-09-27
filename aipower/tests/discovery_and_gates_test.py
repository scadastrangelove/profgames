#!/usr/bin/env python3
"""Pinned migration, provenance and bilingual offline UI checks for v0.41."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_discovery_and_gates import ARC, PACING, CLAIM, CAPACITY, GATES, VULNCHECK, TRACK, migrate
from validate import references


def run(root, executable, regenerate=False):
    package = root / "review/ai-discovery-gates"
    packet = json.loads((package / "candidates.json").read_text())
    base = packet["meta"]["atlas_commit_reviewed"]
    report = {"version": "0.41", "base_commit": base, "checks": [], "languages": {}}

    def ok(name, condition):
        if not condition:
            raise AssertionError(name)
        report["checks"].append(name)

    originals, docs = {}, {}
    for lang in ["ru", "en"]:
        filename = f"ai_power_storygraph_{lang}.json"
        old_bytes = subprocess.check_output(["git", "show", f"{base}:aipower/{filename}"], cwd=root)
        originals[lang] = old_bytes
        old = json.loads(old_bytes)
        expected = migrate(copy.deepcopy(old), packet)
        if regenerate:
            docs[lang] = expected
            continue
        doc = json.loads((root / filename).read_text())
        docs[lang] = doc
        ok(lang + ": exact reviewed input", hashlib.sha256(old_bytes).hexdigest() == packet["meta"]["base_sha256"][lang])
        ok(lang + ": migration reproduces current JSON", expected == doc)
        events = {e["id"]: e for e in doc["events"]}
        ids = {e["id"] for e in packet["events"]}
        ok(lang + ": exactly eight new events", set(events) - {e["id"] for e in old["events"]} == ids and len(ids) == 8)
        link_fields = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        ok(lang + ": existing event content and dates preserved", all(
            {k: v for k, v in e.items() if k not in link_fields}
            == {k: v for k, v in events[e["id"]].items() if k not in link_fields} for e in old["events"]))
        ok(lang + ": all prior edges preserved", all(e in doc["edges"] for e in old["edges"]))
        ok(lang + ": 33 new edges", len(doc["edges"]) - len(old["edges"]) == 33)
        previous_sources = {s["url"]: s["id"] for s in old["sourceIndex"]}
        sources = {s["url"]: s["id"] for s in doc["sourceIndex"]}
        ok(lang + ": existing source IDs preserved", all(sources[url] == id for url, id in previous_sources.items()))
        ok(lang + ": exactly eleven new unique source URLs", len(sources) == len(doc["sourceIndex"]) == len(previous_sources) + 11)
        for collection in ["claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"]:
            ok(lang + ": no lost " + collection, {e["id"] for e in old[collection]} <= {e["id"] for e in doc[collection]})
        ok(lang + ": no new arcs or claim checks", len(doc["arcs"]) == len(old["arcs"]) and len(doc["claimChecks"]) == len(old["claimChecks"]))
        ok(lang + ": all typed references resolve", references(doc) == doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        for arc_id in [ARC, PACING]:
            arc = next(a for a in doc["arcs"] if a["id"] == arc_id)
            dates = [events[id]["date"] for id in arc["key_nodes"] if id in events]
            ok(lang + ": chronological arc " + arc_id, dates == sorted(dates) and arc["end_date"] == max(dates))
        claim = next(c for c in doc["claims"] if c["id"] == CLAIM)
        ok(lang + ": affirmative claim supported and scoped", claim["status"] == "verified" and len(claim["supporting_evidence"]) == 11 and claim["qualifying_evidence"] == [VULNCHECK])
        capacity = next(c for c in doc["claims"] if c["id"] == CAPACITY)
        ok(lang + ": capacity remains partial and includes scaling counterpoints", capacity["status"] == "partially_verified" and {"SIG_2026_WINDOWS_MDASH_DISCOVERY_CAPACITY", "SIG_2026_CHROME_AI_SECURITY_FIX_THROUGHPUT"} <= set(capacity["qualifying_evidence"]))
        gates = events[GATES]
        ok(lang + ": Gates is speech not policy or casualty forecast", gates["artifact_kind"] == "commentary" and gates["normative_force"] == "not_applicable" and gates["policy_adopted"] is False and gates["numbers"] == {} and gates["date"] == "2026-09-25" and gates["interview_recorded_at"] == "2026-09-23")
        ok(lang + ": Mozilla campaigns stay separate", events["SIG_2026_FIREFOX_CLAUDE_22_CVES"]["date"] == "2026-03-06" and events["SIG_2026_MYTHOS_FIREFOX_271"]["date"] == "2026-04-21")
        ok(lang + ": Chrome metric is security bugs not CVEs", events["SIG_2026_CHROME_AI_SECURITY_FIX_THROUGHPUT"]["pipeline_metrics"][0]["unit"] == "security bugs fixed")
        metr = events["SIG_2026_METR_AI_DISCOVERY_OPENSSL_ATTRIBUTION"]
        ok(lang + ": analysis and observation dates separate", metr["date"] == "2026-08-14" and metr["pipeline_metrics"][0]["as_of"] == "2026-08-05")
        ok(lang + ": no fabricated common funnel", all("pipeline_semantics" not in events[id] for id in ids))
        kind_ids = {x["id"] for x in doc["cyberFramework"]["defense_evidence_kinds"]}
        for candidate in packet["events"]:
            e = events[candidate["id"]]
            ok(lang + ": source provenance " + e["id"], {s["url"] for s in e["sources"]} == {packet["sources"][id]["url"] for id in candidate["source_ids"]})
            if e["id"] != GATES:
                ok(lang + ": defense type and track " + e["id"], e["defense_evidence_kind"] in kind_ids and TRACK in e["resilience_track_ids"])
                ok(lang + ": metrics carry source and population " + e["id"], all(m["source_url"] in sources and m["population_ru"] and m["population_en"] and m["unit"] for m in e["pipeline_metrics"]))
    if regenerate:
        for lang, doc in docs.items():
            (root / f"ai_power_storygraph_{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        print("Rebuilt both JSON files from the pinned v0.40 commit")
        return

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        inputs, output = temp / "input", temp / "output"
        inputs.mkdir()
        for lang, data in originals.items():
            (inputs / f"ai_power_storygraph_{lang}.json").write_bytes(data + (b" " if lang == "en" else b""))
        command = [sys.executable, str(root / "scripts/migrate_discovery_and_gates.py"), "--root", str(inputs), "--output", str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        ok("changed English input produces no outputs", result.returncode != 0 and not output.exists() and "en: expected pinned" in result.stderr)
        command[command.index(str(inputs))] = str(root)
        result = subprocess.run(command, capture_output=True, text=True)
        ok("migration rejects current release", result.returncode != 0 and not output.exists())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.set_default_timeout(12000)
            errors, requests = [], []
            page.on("pageerror", lambda e, es=errors: es.append(str(e)))
            page.on("request", lambda r, rs=requests: rs.append(r.url))
            html = (root / filename).read_text()
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber');cyberState.mode='all';resilienceState.open=true;resilienceState.track='RES_TRACK_MAINTENANCE_CAPACITY';renderCyber()")
            ok(lang + ": both claims visible", page.locator("#resilience-claim button").count() == 2)
            page.locator(f'#resilience-claim [data-id="{CLAIM}"]').click()
            ok(lang + ": new claim opens", page.evaluate("currentDetail.id") == CLAIM)
            page.keyboard.press("Escape")
            for candidate in packet["events"]:
                id = candidate["id"]
                if id == GATES:
                    page.evaluate("id=>openDetail('event',id)", id)
                else:
                    page.locator(f'.resilience-evidence-card[data-id="{id}"]').click()
                ok(lang + ": correct event " + id, page.evaluate("currentDetail.id") == id)
                ok(lang + ": policy metadata " + id, page.locator("#detail .governance-card").count() == 1)
                ok(lang + ": exact metric count " + id, page.locator("#detail .resilience-metric").count() == len(candidate["metrics"]))
                if candidate["metrics"]:
                    units = page.locator("#detail .resilience-metric small").all_text_contents()
                    event = next(e for e in docs[lang]["events"] if e["id"] == id)
                    ok(lang + ": localized metric units " + id, all(m["unit_" + lang] in text for m, text in zip(event["pipeline_metrics"], units)))
                for width, height in [(1440, 1100), (390, 844)]:
                    page.set_viewport_size({"width": width, "height": height})
                    ok(lang + ": no overflow " + id + str(width), page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("el=>el.scrollWidth<=el.clientWidth"))
                    if id in [GATES, "SIG_2026_CHROME_AI_SECURITY_FIX_THROUGHPUT"]:
                        page.screenshot(path=str(package / f'{lang}-{"gates" if id == GATES else "chrome"}-{width}.png'))
                page.set_viewport_size({"width": 1440, "height": 1100})
                target = "CLM_031_FRONTIER_PACING_AUTHORITY" if id == GATES else CLAIM
                edge_id = page.evaluate("([s,t])=>D.edges.find(e=>e.source===s&&e.target===t).id", [id, target])
                page.locator(f'#detail [data-id="{edge_id}"]').click()
                page.locator(f'#detail [data-id="{target}"]').click()
                ok(lang + ": claim reachable through edge " + id, page.evaluate("currentDetail.id") == target)
                page.keyboard.press("Escape")
            for width in [1440, 390]:
                page.set_viewport_size({"width": width, "height": 1100})
                page.locator("#resilience-section").scroll_into_view_if_needed()
                page.evaluate("document.getElementById('resilience-section').scrollIntoView({block:'start',behavior:'instant'})")
                ok(lang + ": reading layer no overflow " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width)
                page.screenshot(path=str(package / f"{lang}-discovery-{width}.png"))
            page.locator(f'#resilience-claim [data-id="{CLAIM}"]').click()
            saved = page.evaluate("location.hash")
            fresh = browser.new_page()
            fresh.on("pageerror", lambda e, es=errors: es.append(str(e)))
            fresh.evaluate("h=>history.replaceState(null,'',h)", saved)
            fresh.set_content(html, wait_until="load")
            ok(lang + ": permalink restores new claim and track", fresh.evaluate("currentDetail.id") == CLAIM and fresh.evaluate("resilienceState.track") == TRACK)
            ok(lang + ": no browser errors", not errors)
            ok(lang + ": no network requests", not requests)
            report["languages"][lang] = {"errors": errors, "requests": requests}
            fresh.close()
            page.close()
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (package / "tests-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    parser.add_argument("--regenerate-from-baseline", action="store_true")
    args = parser.parse_args()
    run(args.root, args.chromium, args.regenerate_from_baseline)
