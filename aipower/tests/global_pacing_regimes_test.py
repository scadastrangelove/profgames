#!/usr/bin/env python3
"""Offline browser checks that the v0.37 global pacing/access comparison survives v0.40."""
from pathlib import Path
import argparse
import json

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EVENT_IDS = [
    "SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS",
    "SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS",
    "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE",
]
REUSED_IDS = [
    "SIG_2023_CHINA_GENAI_INTERIM_MEASURES",
    "SIG_2026_EU_AI_ACT_GPAI_ENFORCEMENT_AGENT_SCOPE",
    "SIG_2026_KOREA_SOVEREIGN_CYBER_AI_MODEL",
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

            ok(lang + ": v0.40 data loaded", page.evaluate("D.meta.version") == "0.40")
            ok(lang + ": v0.40 counts loaded", page.evaluate("[EV.length,CHECKS.length,ARCS.length,EDGES.length,SOURCES.length]") == [396, 32, 26, 948, 586])
            page.evaluate("switchTab('story')")
            for event_id in EVENT_IDS + REUSED_IDS:
                ok(lang + ": global event reaches story graph " + event_id, page.locator(f'.event-dot[data-id="{event_id}"]').count() >= 1)

            page.evaluate("openDetail('arc','ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL')")
            arc_text = page.locator("#detail").inner_text().lower()
            terms = ["сеул", "британ", "китай", "коре"] if lang == "ru" else ["seoul", "uk aisi", "china", "korea"]
            ok(lang + ": global comparison visible in pacing arc", all(term in arc_text for term in terms))
            page.keyboard.press("Escape")

            expected = {
                "SIG_2024_SEOUL_FRONTIER_SAFETY_COMMITMENTS": ["шестнадцать", "четыре"] if lang == "ru" else ["sixteen", "four more"],
                "SIG_2024_UK_AISI_PREDEPLOYMENT_MODEL_ACCESS": ["дорелизн", "право"] if lang == "ru" else ["pre-deployment", "power"],
                "SIG_2026_CN_GENAI_FILING_IMPLEMENTATION_SCALE": ["868", "530"],
            }
            for event_id, terms in expected.items():
                page.evaluate("id=>openDetail('event',id)", event_id)
                text = page.locator("#detail").inner_text().lower()
                ok(lang + ": scoped event detail " + event_id, all(term in text for term in terms))
                page.keyboard.press("Escape")

            claim_kind = "claimCheck" if lang == "ru" else "check"
            page.evaluate("([kind,id])=>openDetail(kind,id)", [claim_kind, "CLM_031_FRONTIER_PACING_AUTHORITY"])
            claim_text = page.locator("#detail").inner_text().lower()
            terms = ["разных юрисдикциях", "не единый"] if lang == "ru" else ["across jurisdictions", "not one global"]
            ok(lang + ": claim remains comparative and bounded", all(term in claim_text for term in terms))
            page.keyboard.press("Escape")

            for width, height in [(1440, 1100), (390, 844)]:
                page.set_viewport_size({"width": width, "height": height})
                page.evaluate("switchTab('story')")
                ok(lang + ": no v0.40 page overflow " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width)

            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": no external requests", not requests)
            report["languages"][lang] = {"errors": errors, "external_requests": requests}
            page.close()
        browser.close()

    report.update(passed=True, assertions=len(report["checks"]))
    destination = root / "review/global-pacing-access-regimes/browser-results.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "checks"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    args = parser.parse_args()
    run(args.root, args.chromium)
