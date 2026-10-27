#!/usr/bin/env python3
"""Full offline UI regression plus new evidence, attribution and permalink checks."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_test import run as full_regression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_lab_incidents import RECORDS, UPDATED, PACKET, CYBER, COG, RES


def run(executable):
    PACKET.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="atlas-v047-browser-") as tmp:
        root = Path(tmp)
        (root / "review").mkdir()
        for filename in ["ai-power-atlas-ru.html", "ai-power-atlas.html"]:
            (root / filename).symlink_to(ROOT / filename)
        full_regression(root, executable)
        (PACKET / "full-browser-tests.json").write_bytes((root / "review/browser-results.json").read_bytes())
        for name in ["ru-story-hierarchy.png", "en-story-hierarchy.png"]:
            (PACKET / name).write_bytes((root / "review" / name).read_bytes())
    report = dict(version="0.47", checks=[])
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    screenshot_id = "SIG_2026_BOCSAR_INVESTIGATION_NO_BREACH"
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
            doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
            events = {e["id"]:e for e in doc["events"]}
            page.set_content(html, wait_until="load")
            page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
            ok(lang+": all 220 cyber records", page.evaluate("cyberRenderedEvents.length")==220)
            for eid in [r["id"] for r in RECORDS] + UPDATED:
                card = page.locator(f'.cyber-event[data-id="{eid}"]')
                ok(lang+": exactly one visible card " + eid, card.count()==1)
                card.click()
                detail = page.locator("#detail")
                ok(lang+": record opens " + eid, page.evaluate("currentDetail.id")==eid)
                text = detail.inner_text()
                ok(lang+": localized summary " + eid, events[eid]["summary_"+lang] in text)
                ok(lang+": localized caveat " + eid, events[eid]["caveat_"+lang] in text)
                if events[eid].get("attribution_summary_"+lang):
                    ok(lang+": attribution visible " + eid, events[eid]["attribution_summary_"+lang] in text)
                if len(events[eid]["date"])==7:
                    ok(lang+": month precision visible " + eid, events[eid]["date"] in text and ("месяц" in text if lang=="ru" else "month" in text))
                for width,height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: detail fits {width} {eid}", page.evaluate("document.documentElement.scrollWidth")<=width and detail.evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid==screenshot_id:
                        page.screenshot(path=str(PACKET/f"{lang}-bocsar-{width}.png"))
                if eid in {screenshot_id,"SIG_2026_ANTHROPIC_SELF_REPLICATION_CONTROLLED_STUDY"}:
                    fresh.goto("about:blank")
                    fresh.evaluate("h=>history.replaceState(null,'',h)",page.evaluate("location.hash"))
                    fresh.set_content(html,wait_until="load")
                    ok(lang+": fresh permalink " + eid, fresh.evaluate("currentDetail.id")==eid)
                    target = events[eid]["story_primary_arc_id"]
                    page.locator(f'#detail [data-id="{target}"]').first.click()
                    ok(lang+": related story " + eid, page.evaluate("currentDetail.id")==target)
                    ok(lang+": return link " + eid, page.locator(f'#detail [data-id="{eid}"]').count()>0)
                page.keyboard.press("Escape")
                ok(lang+": Escape closes " + eid, page.locator("#modal").get_attribute("aria-hidden")=="true")
                page.set_viewport_size({"width":1440,"height":1100})
            for aid in [CYBER,COG,RES]:
                page.evaluate("id=>openDetail('arc',id)",aid)
                ok(lang+": updated arc wording " + aid, next(a for a in doc["arcs"] if a["id"]==aid)["thesis_"+lang] in page.locator("#detail").inner_text())
                page.keyboard.press("Escape")
            page.evaluate("switchTab('"+("catalog" if lang=="ru" else "facts")+"')")
            root = "#catalog-list" if lang=="ru" else "#fact-list"
            for raw in RECORDS:
                page.locator("#search").fill(raw["id"])
                ok(lang+": search finds unique record " + raw["id"], page.locator(root+f' [data-id="{raw["id"]}"]').count()==1)
            ok(lang+": no JS errors", not errors)
            ok(lang+": no external requests", not requests)
            context.close()
        browser.close()
    report.update(passed=True,assertions=len(report["checks"]))
    (PACKET / "browser-tests.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted browser checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
