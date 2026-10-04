#!/usr/bin/env python3
"""Offline desktop/mobile interaction checks for the v0.42 additions."""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_agent_boundaries import CLAIM, DECEPTION, INJECTION, MEDICARE, PREPRINT, RESPONSE, TRACK


def run(executable):
    package = ROOT / "review/agent-boundaries-september-2026"
    packet = json.loads((package / "candidates.json").read_text())
    report = {"version": "0.42", "mode": "offline HTML injection", "checks": [], "languages": {}}

    def ok(name, condition):
        if not condition:
            raise AssertionError(name)
        report["checks"].append(name)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, name in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.set_default_timeout(10000)
            errors, requests = [], []
            page.on("pageerror", lambda e, es=errors: es.append(str(e)))
            page.on("request", lambda r, rs=requests: rs.append(r.url))
            html = (ROOT / name).read_text()
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
            for candidate in packet["events"]:
                id = candidate["id"]
                card = page.locator(f'.cyber-event[data-id="{id}"]')
                ok(lang + ": event reachable in cyber map " + id, card.count() == 1)
                card.click()
                ok(lang + ": matching drawer " + id, page.evaluate("currentDetail.id") == id)
                ok(lang + ": localized title " + id, candidate["title_" + lang] in page.locator("#detail").inner_text())
                for width, height in [(1440, 1100), (390, 844)]:
                    page.set_viewport_size({"width": width, "height": height})
                    ok(lang + ": drawer fits " + id + " " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if id == DECEPTION:
                        page.screenshot(path=str(package / f"{lang}-compaction-{width}.png"))
                if id == MEDICARE:
                    ok(lang + ": contested qualification visible", "The Record" in page.locator("#detail").inner_text())
                if id == DECEPTION:
                    edge_id = page.evaluate("([s,t])=>D.edges.find(e=>e.source===s&&e.target===t).id", [id, CLAIM])
                    page.locator(f'#detail [data-id="{edge_id}"]').click()
                    page.locator(f'#detail [data-id="{CLAIM}"]').click()
                    ok(lang + ": claim reachable through edge", page.evaluate("currentDetail.id") == CLAIM)
                    ok(lang + ": claim interpretation visible", "Selective Permeability" in page.locator("#detail").inner_text())
                page.keyboard.press("Escape")
                ok(lang + ": Escape closes drawer " + id, page.locator("#modal").get_attribute("aria-hidden") == "true")
                page.set_viewport_size({"width": 1440, "height": 1100})
            page.locator(f'[data-behavior-track="{TRACK}"]').click()
            ok(lang + ": both compaction records in continuity track", all(page.locator(f'.behavior-evidence-card[data-id="{id}"]').count() == 1 for id in [DECEPTION, INJECTION]))
            page.locator(f'.behavior-evidence-card[data-id="{INJECTION}"]').click()
            saved = page.evaluate("location.hash")
            fresh = browser.new_page()
            fresh.on("pageerror", lambda e, es=errors: es.append(str(e)))
            fresh.evaluate("h=>history.replaceState(null,'',h)", saved)
            fresh.set_content(html, wait_until="load")
            ok(lang + ": permalink restores track and record", fresh.evaluate("currentDetail.id") == INJECTION and fresh.evaluate("behaviorState.track") == TRACK)
            fresh.close()
            page.keyboard.press("Escape")
            page.evaluate("behaviorState.track='';resilienceState.open=true;resilienceState.track='RES_TRACK_INCIDENT_LEARNING';renderCyber()")
            ok(lang + ": government response in incident-learning layer", page.locator(f'.resilience-evidence-card[data-id="{RESPONSE}"]').count() == 1)
            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": no network requests", not requests)
            report["languages"][lang] = {"errors": errors, "requests": requests}
            page.close()
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (package / "browser-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
