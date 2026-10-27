#!/usr/bin/env python3
"""Offline bilingual regression and knowledge-source navigation on desktop/mobile."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_test import run as full_regression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_knowledge_gatekeeping import RECORDS, PACKET, DATA, CLAIM, GAP, SP


def run(executable):
    with tempfile.TemporaryDirectory(prefix="atlas-v048-browser-") as tmp:
        root = Path(tmp)
        (root/"review").mkdir()
        for name in ["ai-power-atlas-ru.html", "ai-power-atlas.html"]:
            (root/name).symlink_to(ROOT/name)
        full_regression(root, executable)
        (PACKET/"full-browser-tests.json").write_bytes((root/"review/browser-results.json").read_bytes())
        for name in ["ru-story-hierarchy.png", "en-story-hierarchy.png"]:
            (PACKET/name).write_bytes((root/"review"/name).read_bytes())
    report = dict(version="0.48", checks=[], mode="offline HTML injection; no HTTP deployment test")
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True)
        for lang, name in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            context = browser.new_context(viewport={"width":1440, "height":1100})
            page, fresh = context.new_page(), context.new_page()
            errors, requests = [], []
            for tab in [page, fresh]:
                tab.on("pageerror", lambda e, es=errors: es.append(str(e)))
                tab.on("request", lambda r, rs=requests: rs.append(r.url))
            html = (ROOT/name).read_text()
            doc = json.loads((ROOT/f"ai_power_storygraph_{lang}.json").read_text())
            events = {e["id"]:e for e in doc["events"]}
            page.set_content(html, wait_until="load")
            if lang=="en":
                ok(lang+": footer direct-link count current", "26 arcs, without a direct thesis link: 1" in page.locator("#footer").inner_text())
            page.evaluate("switchTab('"+("catalog" if lang=="ru" else "facts")+"')")
            listing = "#catalog-list" if lang=="ru" else "#fact-list"
            for raw in RECORDS:
                eid = raw["id"]
                page.locator("#search").fill(eid)
                row = page.locator(listing+f' [data-id="{eid}"]')
                ok(lang+": search finds one record " + eid, row.count()==1)
                row.click()
                detail = page.locator("#detail")
                ok(lang+": search result opens " + eid, page.evaluate("currentDetail.id")==eid)
                text = detail.inner_text()
                ok(lang+": summary and caveat shown " + eid, events[eid]["summary_"+lang] in text and events[eid]["caveat_"+lang] in text)
                if events[eid]["observation_period_"+lang]:
                    ok(lang+": separate observation window " + eid, events[eid]["observation_period_"+lang] in text)
                for source in events[eid]["sources"]:
                    ok(lang+": clickable source " + source["url"], detail.locator('a').evaluate_all('(xs)=>xs.map(x=>x.href)').count(source["url"])>=1)
                for width,height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: detail fits {width} {eid}", page.evaluate("document.documentElement.scrollWidth")<=width and detail.evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid=="SIG_2026_PUBLIC_POSTS_AI_SEARCH_CITATION_EXPERIMENT":
                        page.screenshot(path=str(PACKET/f"{lang}-citation-study-{width}.png"))
                page.locator(f'#detail [data-id="{DATA}"]').first.click()
                ok(lang+": primary arc opens " + eid, page.evaluate("currentDetail.id")==DATA)
                page.locator("#detail-back").click()
                ok(lang+": back restores record " + eid, page.evaluate("currentDetail.id")==eid)
                page.keyboard.press("Escape")
                ok(lang+": Escape closes " + eid, page.locator("#modal").get_attribute("aria-hidden")=="true")
                page.set_viewport_size({"width":1440,"height":1100})
            page.locator("#search").fill("")
            page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
            for raw in RECORDS:
                count = page.locator(f'.cyber-event[data-id="{raw["id"]}"]').count()
                ok(lang+": correct cyber inclusion " + raw["id"], count==(1 if raw["cyber"] else 0))
            for kind,eid in [("arc", DATA), ("claim", CLAIM), ("gap", GAP)]:
                page.evaluate("x=>openDetail(x[0],x[1])", [kind,eid])
                ok(lang+": detail opens " + kind, page.evaluate("currentDetail.id")==eid)
                text = page.locator("#detail").inner_text()
                if kind=="arc":
                    arc = next(a for a in doc["arcs"] if a["id"]==DATA)
                    ok(lang+": new arc title and thesis", arc["title_"+lang] in text and arc["thesis_"+lang] in text)
                    ok(lang+": all new facts reachable from arc", all(page.locator(f'#detail [data-id="{r["id"]}"]').count()>0 for r in RECORDS))
                elif kind=="claim":
                    ok(lang+": scoped claim visible", next(c for c in doc["claims"] if c["id"]==CLAIM)["claim_"+lang] in text)
                else:
                    ok(lang+": gap research protocol visible", next(g for g in doc["gaps"] if g["id"]==GAP)["what_would_close_"+lang] in text)
                fresh.goto("about:blank")
                fresh.evaluate("h=>history.replaceState(null,'',h)", page.evaluate("location.hash"))
                fresh.set_content(html, wait_until="load")
                ok(lang+": permalink restores " + kind, fresh.evaluate("currentDetail.id")==eid)
                for width,height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: {kind} fits {width}", page.evaluate("document.documentElement.scrollWidth")<=width and page.locator("#detail").evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if kind=="arc":
                        page.screenshot(path=str(PACKET/f"{lang}-knowledge-arc-{width}.png"))
                page.keyboard.press("Escape")
            editorial = next(e for e in doc["edges"] if e["source"]==CLAIM and e["target"]==SP)
            page.evaluate("id=>openDetail('edge',id)",editorial["id"])
            ok(lang+": SP editorial limit visible", editorial["summary_"+lang] in page.locator("#detail").inner_text())
            page.locator(f'#detail [data-id="{SP}"]').click()
            ok(lang+": SP existing record reachable",page.evaluate("currentDetail.id")==SP)
            ok(lang+": no JavaScript errors", not errors)
            ok(lang+": no external requests", not requests)
            context.close()
        browser.close()
    report.update(passed=True, assertions=len(report["checks"]))
    (PACKET/"browser-tests.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted browser checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", required=True)
    run(parser.parse_args().chromium)
