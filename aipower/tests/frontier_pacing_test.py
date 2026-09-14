#!/usr/bin/env python3
"""Offline browser checks for the v0.36 frontier-pacing layer."""
from pathlib import Path
import argparse
import json

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EVENT_IDS = [
    "SIG_2026_DOW_AI_STRATEGY_SPEED_WINS",
    "SIG_2026_US_NSPM11_PROVIDER_CONTINUITY_CONTROL",
    "SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL",
    "SIG_2026_FRONTIER_LAB_PACING_ENDORSEMENTS",
    "SIG_2026_TRUMP_REJECTS_FRONTIER_PACING",
]


def run(root: Path, executable: str):
    report = {"mode": "local HTML injection; no network", "checks": [], "languages": {}}

    def ok(name, condition):
        print(name, bool(condition), flush=True)
        if not condition:
            raise AssertionError(name)
        report["checks"].append(name)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.set_default_timeout(12000)
            errors = []
            requests = []
            page.on("pageerror", lambda error, bucket=errors: bucket.append(str(error)))
            page.on("request", lambda request, bucket=requests: bucket.append(request.url))
            page.set_content((root / filename).read_text(), wait_until="load")

            ok(lang + ": v0.36 data loaded", page.evaluate("D.meta.version") == "0.36")
            ok(lang + ": v0.36 counts loaded", page.evaluate("[EV.length,CHECKS.length,ARCS.length,EDGES.length,SOURCES.length]") == [384, 32, 26, 864, 570])
            page.evaluate("switchTab('story')")
            for event_id in EVENT_IDS:
                ok(lang + ": pacing event reaches story graph " + event_id, page.locator(f'.event-dot[data-id="{event_id}"]').count() >= 1)

            page.evaluate("openDetail('arc','ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL')")
            arc_text = page.locator("#detail").inner_text().lower()
            terms = ["темп", "непрерывность"] if lang == "ru" else ["pacing", "continuity"]
            ok(lang + ": pacing arc opens", all(term in arc_text for term in terms))
            page.keyboard.press("Escape")

            claim_kind = "claimCheck" if lang == "ru" else "check"
            page.evaluate("([kind,id])=>openDetail(kind,id)", [claim_kind, "CLM_031_FRONTIER_PACING_AUTHORITY"])
            claim_text = page.locator("#detail").inner_text().lower()
            terms = ["лаборатории", "государство"] if lang == "ru" else ["laboratories", "state"]
            ok(lang + ": scoped pacing claim opens", all(term in claim_text for term in terms))
            page.keyboard.press("Escape")

            page.evaluate("openDetail('event','SIG_2026_AMODEI_PACE_FRONTIER_PROPOSAL')")
            proposal_text = page.locator("#detail").inner_text().lower()
            terms = ["предложение", "6–12"] if lang == "ru" else ["proposal", "six-to-twelve"]
            ok(lang + ": proposal and forecast caveat visible", all(term in proposal_text for term in terms))
            page.keyboard.press("Escape")

            for width, height in [(1440, 1100), (390, 844)]:
                page.set_viewport_size({"width": width, "height": height})
                page.evaluate("switchTab('story')")
                ok(lang + ": no v0.36 page overflow " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width)

            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": no external requests", not requests)
            report["languages"][lang] = {"errors": errors, "external_requests": requests}
            page.close()
        browser.close()

    report.update(passed=True, assertions=len(report["checks"]))
    destination = root / "review/frontier-pacing-september-2026/browser-results.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "checks"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    args = parser.parse_args()
    run(args.root, args.chromium)
