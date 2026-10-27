#!/usr/bin/env python3
"""Offline bilingual navigation and correction visibility, desktop and mobile."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_test import run as full_regression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_october_access import RECORDS, PACKET, IDS, DNS, ANTHROPIC, VERSION


def run(executable):
    (PACKET/"browser-tests.json").write_text(json.dumps(dict(version=VERSION,passed=False,status="running"))+"\n")
    with tempfile.TemporaryDirectory(prefix="atlas-v049-browser-") as tmp:
        root = Path(tmp)
        (root/"review").mkdir()
        for name in ["ai-power-atlas-ru.html","ai-power-atlas.html"]:
            (root/name).symlink_to(ROOT/name)
        full_regression(root,executable)
        (PACKET/"full-browser-tests.json").write_bytes((root/"review/browser-results.json").read_bytes())
        for name in ["ru-story-hierarchy.png","en-story-hierarchy.png"]:
            (PACKET/name).write_bytes((root/"review"/name).read_bytes())
    report = dict(version=VERSION,checks=[],mode="offline HTML injection; deployment checked separately")
    def ok(label,condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable,headless=True)
        for lang,name in [("ru","ai-power-atlas-ru.html"),("en","ai-power-atlas.html")]:
            context = browser.new_context(viewport={"width":1440,"height":1100})
            page,fresh = context.new_page(),context.new_page()
            errors,requests = [],[]
            for tab in [page,fresh]:
                tab.on("pageerror",lambda e,es=errors:es.append(str(e)))
                tab.on("request",lambda r,rs=requests:rs.append(r.url))
            html = (ROOT/name).read_text()
            doc = json.loads((ROOT/f"ai_power_storygraph_{lang}.json").read_text())
            events = {e["id"]:e for e in doc["events"]}
            page.set_content(html,wait_until="load")
            page.evaluate("switchTab('"+("catalog" if lang=="ru" else "facts")+"')")
            listing = "#catalog-list" if lang=="ru" else "#fact-list"
            for raw in RECORDS:
                eid = raw["id"]
                page.locator("#search").fill(eid)
                row = page.locator(listing+f' [data-id="{eid}"]')
                ok(lang+": search returns one "+eid,row.count()==1)
                row.click()
                detail = page.locator("#detail")
                ok(lang+": correct detail "+eid,page.evaluate("currentDetail.id")==eid)
                text = detail.inner_text()
                ok(lang+": summary and caveat visible "+eid,events[eid]["summary"] in text and events[eid]["caveat"] in text)
                hrefs = detail.locator("a").evaluate_all("xs=>xs.map(x=>x.href)")
                ok(lang+": every source clickable "+eid,all(s["url"] in hrefs for s in events[eid]["sources"]))
                fresh.goto("about:blank")
                fresh.evaluate("h=>history.replaceState(null,'',h)",page.evaluate("location.hash"))
                fresh.set_content(html,wait_until="load")
                ok(lang+": permalink restores "+eid,fresh.evaluate("currentDetail.id")==eid)
                for width,height in [(1440,1100),(390,844)]:
                    page.set_viewport_size({"width":width,"height":height})
                    ok(f"{lang}: detail fits {width} {eid}",page.evaluate("document.documentElement.scrollWidth")<=width and detail.evaluate("e=>e.scrollWidth<=e.clientWidth"))
                    if eid==IDS["georgia"]:
                        page.screenshot(path=str(PACKET/f"{lang}-georgia-correction-{width}.png"))
                aid = raw["arcs"][0]
                page.locator(f'#detail [data-id="{aid}"]').first.click()
                ok(lang+": primary arc opens "+eid,page.evaluate("currentDetail.id")==aid)
                ok(lang+": arc links back to event "+eid,page.locator(f'#detail [data-id="{eid}"]').count()>0)
                page.locator("#detail-back").click()
                ok(lang+": Back restores "+eid,page.evaluate("currentDetail.id")==eid)
                page.keyboard.press("Escape")
                ok(lang+": Escape closes "+eid,page.locator("#modal").get_attribute("aria-hidden")=="true")
                page.set_viewport_size({"width":1440,"height":1100})
            page.locator("#search").fill("")
            page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
            for raw in RECORDS:
                count = page.locator(f'.cyber-event[data-id="{raw["id"]}"]').count()
                ok(lang+": correct cyber inclusion "+raw["id"],count==(1 if raw["domains"] else 0))
            for eid in [DNS,ANTHROPIC]:
                page.evaluate("id=>openDetail('event',id)",eid)
                text = page.locator("#detail").inner_text()
                ok(lang+": existing record shows current clarification "+eid,events[eid]["current_state"] in text)
                heading = "Последнее уточнение" if lang=="ru" else "Latest clarification"
                ok(lang+": clarification precedes historical account "+eid,heading in text and text.index(heading)<text.index(events[eid]["claim_supported"]))
                page.keyboard.press("Escape")
            correction = next(e for e in doc["edges"] if e["source"]==IDS["georgia"] and e["target"]==ANTHROPIC)
            page.evaluate("id=>openDetail('edge',id)",correction["id"])
            ok(lang+": qualifying edge wording visible",correction["summary"] in page.locator("#detail").inner_text())
            page.locator(f'#detail [data-id="{ANTHROPIC}"]').click()
            ok(lang+": corrected disclosure reachable",page.evaluate("currentDetail.id")==ANTHROPIC)
            ok(lang+": no JavaScript errors",not errors)
            ok(lang+": no external requests",not requests)
            context.close()
        browser.close()
    report.update(passed=True,assertions=len(report["checks"]))
    (PACKET/"browser-tests.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"Passed {report['assertions']} targeted browser checks")


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium",required=True)
    run(parser.parse_args().chromium)
