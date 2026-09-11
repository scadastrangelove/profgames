#!/usr/bin/env python3
"""Offline browser checks for the v0.35 Anthropic threat-intelligence layer."""
from pathlib import Path
import argparse
import json

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
EVENT_IDS = [
    "SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE",
    "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
    "SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY",
    "SIG_2026_ANTHROPIC_GTG50014_CREDENTIAL_SUPPLY_CHAIN",
    "SIG_2026_ANTHROPIC_STATE_SURVEILLANCE_BUREAUCRACY",
    "SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING",
    "SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE",
]
TRACK_IDS = [
    "SIG_2026_ANTHROPIC_GTG20006_ADAPTIVE_EVASION",
    "SIG_2026_ANTHROPIC_GTG10007_EXPLOIT_FOUNDRY",
    "SIG_2026_ANTHROPIC_INFLUENCE_ATTRIBUTION_LAUNDERING",
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

            ok(lang + ": v0.35 data loaded", page.evaluate("D.meta.version") == "0.35")
            ok(
                lang + ": v0.35 counts loaded",
                page.evaluate("[EV.length,CHECKS.length,EDGES.length,SOURCES.length]") == [379, 31, 829, 562],
            )

            page.evaluate("switchTab('story')")
            ok(
                lang + ": observability event reaches story graph",
                page.locator('.event-dot[data-id="SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE"]').count() >= 1,
            )
            ok(
                lang + ": distillation dispute reaches story graph",
                page.locator('.event-dot[data-id="SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE"]').count() >= 1,
            )

            page.evaluate("switchTab('cyber');cyberState.mode='core';cyberState.principalOnly=false;renderCyber()")
            for event_id in EVENT_IDS:
                ok(lang + ": core cyber card " + event_id, page.locator(f'.cyber-event[data-id="{event_id}"]').count() == 1)

            page.evaluate("openDetail('event','SIG_2026_ANTHROPIC_THREAT_INTEL_OBSERVABILITY_GATE')")
            detail = page.locator("#detail").inner_text().lower()
            expected = ["паноптикум", "чокпойнт"] if lang == "ru" else ["observability", "access gate"]
            ok(lang + ": provider mechanism is explicit", all(term in detail for term in expected))
            ok(
                lang + ": Habr is exposed as a source",
                page.locator('#detail a[href="https://habr.com/ru/articles/1058354/"]').count() == 1,
            )
            page.keyboard.press("Escape")

            page.evaluate("openDetail('event','SIG_2026_ANTHROPIC_DISTILLATION_ABUSE_DISCLOSURE')")
            state = page.locator("#detail .state-card").last.inner_text()
            state_digits = "".join(character for character in state if character.isdigit())
            ok(lang + ": distillation update has separate date and scale", "2026-09-10" in state and "151" in state and "5380" in state_digits)
            page.keyboard.press("Escape")

            page.evaluate("behaviorState.track='BEH_TRACK_CONCEALMENT_PERSISTENCE';behaviorState.subdomain='all';behaviorState.mechanism='';renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents())")
            ok(lang + ": concealment track now has 23 records", page.evaluate("behaviorEvents(cyberRenderedEvents).length") == 23)
            for event_id in TRACK_IDS:
                ok(lang + ": operational behavior card " + event_id, page.locator(f'.behavior-evidence-card[data-id="{event_id}"]').count() == 1)

            claim_kind = "claimCheck" if lang == "ru" else "check"
            page.evaluate("([kind,id])=>openDetail(kind,id)", [claim_kind, "CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE"])
            claim_text = page.locator("#detail").inner_text().lower()
            expected = ["облачной модели", "отзыва доступа"] if lang == "ru" else ["hosted-model", "access revocation"]
            ok(lang + ": scoped panopticon/chokepoint claim opens", all(term in claim_text for term in expected))
            page.keyboard.press("Escape")

            page.evaluate("openDetail('event','SIG_2026_US_CHINA_DISTILLATION_SECURITY_DISPUTE')")
            ok(
                lang + ": both official distillation positions link",
                page.locator('#detail a[href*="nsa.gov/Press-Room"]').count() == 1
                and page.locator('#detail a[href*="mofcom.gov.cn/xwfb"]').count() == 1,
            )
            page.keyboard.press("Escape")

            for width, height in [(1440, 1100), (390, 844)]:
                page.set_viewport_size({"width": width, "height": height})
                page.evaluate("switchTab('cyber')")
                ok(lang + ": no v0.35 page overflow " + str(width), page.evaluate("document.documentElement.scrollWidth") <= width)

            ok(lang + ": no JavaScript errors", not errors)
            ok(lang + ": no external requests", not requests)
            report["languages"][lang] = {"errors": errors, "external_requests": requests}
            page.close()
        browser.close()

    report.update(passed=True, assertions=len(report["checks"]))
    destination = root / "review/anthropic-threat-intel-september-2026/browser-results.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "checks"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    args = parser.parse_args()
    run(args.root, args.chromium)
