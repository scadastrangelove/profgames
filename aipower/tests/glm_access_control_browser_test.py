#!/usr/bin/env python3
"""Exercise new bilingual cyber cards, cross-links, search and mobile permalinks."""
import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_glm_access_control import CYBER, PACKET, SPECS


def run(executable):
    report = {"version": "0.45", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True)
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            html = (ROOT / filename).read_text()
            context = browser.new_context(viewport={"width":1440, "height":1100})
            page = context.new_page()
            fresh = context.new_page()
            errors, requests = [], []
            for tab in [page, fresh]:
                tab.on("pageerror", lambda e, es=errors: es.append(str(e)))
                tab.on("request", lambda r, rs=requests: rs.append(r.url))
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber')")
            for spec in SPECS:
                eid = spec["id"]
                card = page.locator(f'.cyber-event[data-id="{eid}"]')
                ok(lang + ": core cyber card " + eid, card.count() == 1)
                card.click()
                ok(lang + ": opens " + eid, page.evaluate("currentDetail.id") == eid)
                ok(lang + ": correct language " + eid, spec["title_"+lang] in page.locator("#detail").inner_text())
                for width, height in [(1440,1100), (390,844)]:
                    page.set_viewport_size({"width":width, "height":height})
                    ok(f"{lang}: detail fits {width} {eid}", page.evaluate("document.documentElement.scrollWidth") <= width and page.locator("#detail").evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid == SPECS[1]["id"]:
                        page.screenshot(path=str(PACKET / f"{lang}-glm-{width}.png"))
                fresh.goto("about:blank")
                fresh.evaluate("h=>history.replaceState(null,'',h)", page.evaluate("location.hash"))
                fresh.set_content(html, wait_until="load")
                ok(lang + ": permalink " + eid, fresh.evaluate("currentDetail.id") == eid)
                page.locator(f'#detail [data-id="{CYBER}"]').first.click()
                ok(lang + ": related cyber arc " + eid, page.evaluate("currentDetail.id") == CYBER)
                page.keyboard.press("Escape")
                ok(lang + ": Escape " + eid, page.locator("#modal").get_attribute("aria-hidden") == "true")
                page.set_viewport_size({"width":1440, "height":1100})
            page.evaluate("switchTab('" + ("catalog" if lang == "ru" else "facts") + "')")
            root = "#catalog-list" if lang == "ru" else "#fact-list"
            for spec in SPECS:
                page.locator("#search").fill(spec["id"])
                ok(lang + ": catalog search " + spec["id"], page.locator(root + f' [data-id="{spec["id"]}"]').count() == 1)
            page.locator("#search").fill("")
            page.evaluate("switchTab('cyber')")
            for width, height in [(1440,1100), (390,844)]:
                page.set_viewport_size({"width":width, "height":height})
                ok(f"{lang}: cyber page fits {width}", page.evaluate("document.documentElement.scrollWidth") <= width)
            ok(lang + ": no JS errors", not errors)
            ok(lang + ": offline", not requests)
            context.close()
            print(lang + ": passed", flush=True)
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (PACKET / "browser-tests.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Passed {report['assertions']} browser checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
