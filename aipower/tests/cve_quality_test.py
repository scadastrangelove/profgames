#!/usr/bin/env python3
"""CVE/NVD provenance, conservative integration and offline UI regressions."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_cve_quality import ARC, CISA, CLAIM, NIST, TRACK, migrate


def run(root, executable):
    package = root / "review/cve-quality-era"
    raw = json.loads((package / "candidates.json").read_text())
    base = raw["meta"]["atlas_commit_reviewed"]
    report = {"version": "0.40", "base_commit": base, "checks": [], "languages": {}}

    def ok(name, condition):
        if not condition:
            raise AssertionError(name)
        report["checks"].append(name)

    originals = {}
    for lang in ["ru", "en"]:
        filename = f"ai_power_storygraph_{lang}.json"
        old_bytes = subprocess.check_output(["git", "show", f"{base}:aipower/{filename}"], cwd=root)
        originals[lang] = old_bytes
        old = json.loads(old_bytes)
        doc = json.loads((root / filename).read_text())
        ok(lang + ": pinned baseline", hashlib.sha256(old_bytes).hexdigest() == raw["meta"]["base_sha256"][lang])
        ok(lang + ": reproducible migration", migrate(copy.deepcopy(old), raw) == doc)
        events = {e["id"]: e for e in doc["events"]}
        ok(lang + ": exactly two new events", events.keys() - {e["id"] for e in old["events"]} == {CISA, NIST})
        ok(lang + ": all old dates preserved", all(events[e["id"]]["date"] == e["date"] for e in old["events"]))
        link_fields = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        ok(lang + ": all old event content preserved", all(
            {k: v for k, v in e.items() if k not in link_fields}
            == {k: v for k, v in events[e["id"]].items() if k not in link_fields}
            for e in old["events"]))
        ok(lang + ": all old edges preserved", all(e in doc["edges"] for e in old["edges"]) and len(doc["edges"]) == len(old["edges"]) + 7)
        old_sources = {s["url"]: s["id"] for s in old["sourceIndex"]}
        sources = {s["url"]: s["id"] for s in doc["sourceIndex"]}
        ok(lang + ": sources and identifiers preserved", all(sources[url] == id for url, id in old_sources.items()) and len(sources) == len(old_sources) + 3)
        for collection in ["claims", "arcs", "claimChecks"]:
            ok(lang + ": no new or lost " + collection, {x["id"] for x in old[collection]} == {x["id"] for x in doc[collection]})
        ok(lang + ": original claims preserved", old["claims"] == doc["claims"])
        old_claim = next(c for c in old["claims"] if c["id"] == "CLM_VALID_FINDINGS_MAINTENANCE_CAPACITY")
        claim = next(c for c in doc["claims"] if c["id"] == old_claim["id"])
        ok(lang + ": no CVE-volume inference added to AI-findings claim", claim == old_claim)
        cisa, nist = events[CISA], events[NIST]
        ok(lang + ": publication date distinct from snapshot", cisa["date"] == "2026-09-22" and cisa["reported_metrics"][0]["as_of"] == "2026-09-18")
        ok(lang + ": forecast distinct from observation", cisa["reported_metrics"][1]["kind"] == "forecast_not_observation")
        ok(lang + ": NVD change retains April date", nist["date"] == "2026-04-15")
        ok(lang + ": Q1 rate is approximate", nist["reported_metrics"][1]["exact_percentage_published"] is False)
        ok(lang + ": different policy forces", cisa["normative_force"] == "advisory" and nist["normative_force"] == "not_applicable")
        ok(lang + ": no fabricated AI role or sequential funnel", all(not e["cyber_role_ids"] and "pipeline_semantics" not in e for e in [cisa, nist]))
        arc = next(a for a in doc["arcs"] if a["id"] == ARC)
        dates = [events[id]["date"] for id in arc["key_nodes"] if id in events]
        ok(lang + ": arc chronology", dates == sorted(dates) and arc["end_date"] == "2026-09-22")
        ok(lang + ": all typed references valid", doc["referenceIntegrity"]["valid"])

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        inputs, output = temp / "input", temp / "output"
        inputs.mkdir()
        for lang, data in originals.items():
            (inputs / f"ai_power_storygraph_{lang}.json").write_bytes(data + (b" " if lang == "en" else b""))
        command = [sys.executable, str(root / "scripts/migrate_cve_quality.py"), "--root", str(inputs), "--output", str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        ok("changed second input rejected before either output", result.returncode != 0 and not output.exists() and "en: expected pinned" in result.stderr)
        result = subprocess.run(command[:-4] + ["--root", str(root), "--output", str(output)], capture_output=True, text=True)
        ok("already migrated pair rejected", result.returncode != 0 and not output.exists())

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.set_default_timeout(12000)
            errors, requests = [], []
            page.on("pageerror", lambda error, es=errors: es.append(str(error)))
            page.on("request", lambda request, rs=requests: rs.append(request.url))
            html = (root / filename).read_text()
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber');cyberState.mode='core';resilienceState.open=true;resilienceState.track='RES_TRACK_SHARED_REPAIR';renderCyber()")
            for id in [CISA, NIST]:
                card = page.locator(f'.resilience-evidence-card[data-id="{id}"]')
                ok(lang + ": new core card " + id, card.count() == 1)
                card.click()
                ok(lang + ": click opens correct event " + id, page.evaluate("currentDetail.id") == id)
                ok(lang + ": typed policy metadata " + id, page.locator("#detail .governance-card").count() == 1)
                ok(lang + ": metric cards " + id, page.locator("#detail .resilience-metric").count() == (2 if id == CISA else 3))
                ok(lang + ": no unrelated denominator " + id, "91.4%" not in page.locator("#detail .resilience-metadata").inner_text())
                ok(lang + ": canonical source link " + id, page.locator('#detail a[href*="' + ("cisa.gov/" if id == CISA else "nist.gov/") + '"]').count() >= 1)
                for width, height in [(1440, 1100), (390, 844)]:
                    page.set_viewport_size({"width": width, "height": height})
                    ok(lang + ": no drawer/page overflow " + id + str(width), page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("el=>el.scrollWidth<=el.clientWidth"))
                    if id == CISA:
                        page.screenshot(path=str(package / f"{lang}-cisa-{width}.png"))
                page.set_viewport_size({"width": 1440, "height": 1100})
                edge_id = page.evaluate("([source,target])=>D.edges.find(e=>e.source===source&&e.target===target).id", [id, CLAIM])
                page.locator(f'#detail [data-id="{edge_id}"]').click()
                ok(lang + ": evidence edge opens " + id, page.evaluate("currentDetail.id") == edge_id)
                page.locator(f'#detail [data-id="{CLAIM}"]').click()
                ok(lang + ": scoped supporting claim reachable " + id, page.evaluate("currentDetail.id") == CLAIM)
                page.keyboard.press("Escape")
                ok(lang + ": Escape clears selected event " + id, "event=" not in page.url)
            for width in [1440, 390]:
                page.set_viewport_size({"width": width, "height": 1100})
                page.locator("#resilience-section").scroll_into_view_if_needed()
                ok(lang + ": track no overflow " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width)
            page.evaluate("openDetail('event','SIG_2026_CISA_CVE_QUALITY_ERA_FRAMEWORK')")
            saved = page.evaluate("location.hash")
            fresh = browser.new_page()
            fresh.on("pageerror", lambda error, es=errors: es.append(str(error)))
            fresh.evaluate("hash=>history.replaceState(null,'',hash)", saved)
            fresh.set_content(html, wait_until="load")
            ok(lang + ": permalink restores event and track", fresh.evaluate("currentDetail.id") == CISA and fresh.evaluate("resilienceState.track") == TRACK)
            ok(lang + ": no browser errors", not errors)
            ok(lang + ": offline operation", not requests)
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
    args = parser.parse_args()
    run(args.root, args.chromium)
