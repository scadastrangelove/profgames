#!/usr/bin/env python3
"""Run full UI regression and targeted platform-exit checks without external requests."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_test import run as full_regression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_platform_exit import UK, NATO, PAL, PACKET, SOURCES, UK_TEXT, NATO_TEXT


def run(executable):
    PACKET.mkdir(parents=True, exist_ok=True)
    # Keep older release screenshots intact while running the shared regression.
    with tempfile.TemporaryDirectory(prefix="atlas-v046-browser-") as tmp:
        root = Path(tmp)
        (root / "review").mkdir()
        for filename in ["ai-power-atlas-ru.html", "ai-power-atlas.html"]:
            (root / filename).symlink_to(ROOT / filename)
        full_regression(root, executable)
        (PACKET / "full-browser-tests.json").write_bytes((root / "review/browser-results.json").read_bytes())
    report = {"version": "0.46", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True)
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            context = browser.new_context(viewport={"width":1440,"height":1100})
            page, fresh = context.new_page(), context.new_page()
            errors, requests = [], []
            for tab in [page, fresh]:
                tab.on("pageerror", lambda e, es=errors: es.append(str(e)))
                tab.on("request", lambda r, rs=requests: rs.append(r.url))
            html = (ROOT / filename).read_text()
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber')")
            for eid, wording, source_ids in [(UK, UK_TEXT, ["signed","notice","original"]), (NATO, NATO_TEXT, ["nato"])]:
                card = page.locator(f'.cyber-event[data-id="{eid}"]')
                ok(lang + ": core card " + eid, card.count()==1)
                card.click()
                ok(lang + ": correct record " + eid, page.evaluate("currentDetail.id")==eid)
                detail = page.locator("#detail")
                ok(lang + ": localized title " + eid, wording["title_"+lang] in detail.inner_text())
                ok(lang + ": localized caveat " + eid, wording["caveat_"+lang] in detail.inner_text())
                ok(lang + ": scope does not repeat caveat " + eid, wording["caveat_"+lang] not in detail.locator('.governance-card').inner_text())
                if lang=="ru":
                    label = "дата подписания договора" if eid==UK else "дата эксплуатационной вехи"
                    ok(lang + ": date basis localized " + eid, label in detail.inner_text())
                for sid in source_ids:
                    ok(lang + ": primary link " + sid, detail.locator('a[href="'+SOURCES[sid]["url"]+'"]').count()>0)
                for width,height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: detail fits {width} {eid}", page.evaluate("document.documentElement.scrollWidth")<=width and detail.evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid==NATO:
                        page.screenshot(path=str(PACKET/f"{lang}-nato-{width}.png"))
                fresh.goto("about:blank")
                fresh.evaluate("h=>history.replaceState(null,'',h)",page.evaluate("location.hash"))
                fresh.set_content(html,wait_until="load")
                ok(lang + ": fresh permalink " + eid, fresh.evaluate("currentDetail.id")==eid)
                page.locator(f'#detail [data-id="{PAL}"]').first.click()
                ok(lang + ": related arc " + eid,page.evaluate("currentDetail.id")==PAL)
                ok(lang + ": arc links new NATO milestone "+eid,page.locator(f'#detail [data-id="{NATO}"]').count()>0)
                page.keyboard.press("Escape")
                ok(lang + ": Escape "+eid,page.locator("#modal").get_attribute("aria-hidden")=="true")
                page.set_viewport_size({"width":1440,"height":1100})
            page.evaluate("switchTab('"+("catalog" if lang=="ru" else "facts")+"')")
            root = "#catalog-list" if lang=="ru" else "#fact-list"
            for eid in [UK,NATO]:
                page.locator("#search").fill(eid)
                ok(lang + ": search returns one event " + eid,page.locator(root+f' [data-id="{eid}"]').count()==1)
            ok(lang + ": no JS errors", not errors)
            ok(lang + ": no external requests", not requests)
            context.close()
        browser.close()
    report.update(passed=True,assertions=len(report["checks"]))
    (PACKET / "browser-tests.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted browser checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
