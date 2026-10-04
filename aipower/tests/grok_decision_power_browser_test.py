#!/usr/bin/env python3
"""Offline bilingual interaction checks for the v0.43 records."""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_grok_decision_power import CHAT, COURT, MERIDIAN


def run(executable):
    report = {"version": "0.43", "mode": "offline HTML injection", "checks": []}

    def ok(name, condition):
        if not condition:
            raise AssertionError(name)
        report["checks"].append(name)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            html = (ROOT / filename).read_text()
            data = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
            records = {e["id"]: e for e in data["events"]}
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors, requests = [], []
            page.on("pageerror", lambda e, es=errors: es.append(str(e)))
            page.on("request", lambda r, rs=requests: rs.append(r.url))
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
            for event_id in [CHAT, COURT, MERIDIAN]:
                card = page.locator(f'.cyber-event[data-id="{event_id}"]')
                ok(f"{lang}: map card {event_id}", card.count() == 1)
                card.click()
                ok(f"{lang}: matching record {event_id}", page.evaluate("currentDetail.id") == event_id)
                text = page.locator("#detail").inner_text()
                ok(f"{lang}: title and date {event_id}", records[event_id]["title"] in text and records[event_id]["date"] in text)
                for source in records[event_id]["sources"]:
                    ok(f"{lang}: source link {event_id}", page.locator("#detail a").evaluate_all("(xs,url)=>xs.some(x=>x.href===url)", source["url"]))
                for width, height in [(1440, 1100), (390, 844)]:
                    page.set_viewport_size({"width": width, "height": height})
                    ok(f"{lang}: drawer fits {event_id} {width}", page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if event_id == CHAT:
                        page.screenshot(path=str(ROOT / "review" / f"{lang}-grok-consultation-{width}.png"))
                saved = page.evaluate("location.hash")
                fresh = browser.new_page()
                fresh.on("pageerror", lambda e, es=errors: es.append(str(e)))
                fresh.evaluate("h=>history.replaceState(null,'',h)", saved)
                fresh.set_content(html, wait_until="load")
                ok(f"{lang}: permalink {event_id}", fresh.evaluate("currentDetail.id") == event_id)
                fresh.close()
                arc = records[event_id]["story_primary_arc_id"]
                page.locator(f'#detail [data-id="{arc}"]').first.click()
                ok(f"{lang}: related story {event_id}", page.evaluate("currentDetail.id") == arc)
                page.keyboard.press("Escape")
                ok(f"{lang}: Escape {event_id}", page.locator("#modal").get_attribute("aria-hidden") == "true")
                page.set_viewport_size({"width": 1440, "height": 1100})
            page.evaluate("switchTab('" + ("catalog" if lang == "ru" else "facts") + "')")
            page.select_option("#filter-jurisdiction", "Venezuela")
            predicate = "eventPasses" if lang == "ru" else "eventPass"
            ok(lang + ": Venezuela filter retains consultation", page.evaluate(f"EV.filter({predicate}).some(e=>e.id==='{CHAT}')"))
            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": no external requests", not requests)
            page.close()
            print(lang + ": interaction checks passed", flush=True)
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (ROOT / "review/grok-decision-power-browser-tests.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
