#!/usr/bin/env python3
"""Exercise every new record through search, links and permalinks offline."""
import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_state_decision_power import SPECS, PACKET


def run(executable):
    report = {"version": "0.44", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            html = (ROOT / filename).read_text()
            records = {e["id"]: e for e in json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())["events"]}
            context = browser.new_context(viewport={"width":1440, "height":1100})
            page = context.new_page()
            fresh = context.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda e, es=errors: es.append(str(e)))
            page.on("request", lambda r, rs=requests: rs.append(r.url))
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('" + ("catalog" if lang == "ru" else "facts") + "')")
            root = "#catalog-list" if lang == "ru" else "#fact-list"
            for spec in SPECS:
                eid = spec["id"]
                page.locator("#search").fill(eid)
                card = page.locator(root + f' [data-id="{eid}"]')
                ok(lang + ": searchable " + eid, card.count() == 1)
                card.click()
                ok(lang + ": opens correct record " + eid, page.evaluate("currentDetail.id") == eid)
                text = page.locator("#detail").inner_text()
                ok(lang + ": title and date " + eid, records[eid]["title"] in text and records[eid]["date"] in text)
                for source in records[eid]["sources"]:
                    ok(lang + ": source " + eid, page.locator("#detail a").evaluate_all("(xs,u)=>xs.some(x=>x.href===u)", source["url"]))
                for width, height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: fits {width} {eid}", page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid == SPECS[1]["id"]:
                        page.screenshot(path=str(PACKET.parent / f"{lang}-consult-{width}.png"))
                fresh.goto("about:blank")
                fresh.evaluate("h=>history.replaceState(null,'',h)", page.evaluate("location.hash"))
                fresh.set_content(html, wait_until="load")
                ok(lang + ": permalink " + eid, fresh.evaluate("currentDetail.id") == eid)
                arc = records[eid]["story_primary_arc_id"]
                page.locator(f'#detail [data-id="{arc}"]').first.click()
                ok(lang + ": related arc " + eid, page.evaluate("currentDetail.id") == arc)
                page.keyboard.press("Escape")
                ok(lang + ": Escape " + eid, page.locator("#modal").get_attribute("aria-hidden") == "true")
                page.set_viewport_size({"width":1440,"height":1100})
                print(lang + ": " + eid, flush=True)
            page.locator("#search").fill("")
            page.select_option("#filter-jurisdiction", "Albania")
            ok(lang + ": Albania classifier", page.locator(root + ' [data-id="SIG_2025_ALBANIA_DIELLA_PM_RESPONSIBILITY"]').count() == 1)
            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": autonomous offline page", not requests)
            context.close()
            print(lang + ": passed", flush=True)
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (PACKET.parent / "browser-tests.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Passed {report['assertions']} browser checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
