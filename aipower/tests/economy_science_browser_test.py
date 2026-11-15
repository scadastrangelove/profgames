#!/usr/bin/env python3
"""Check every v0.58 card, evidence link and new claim in both published languages."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review/economy-science-2026-11-15/record-browser'
OUT.mkdir(parents=True, exist_ok=True)
report = dict(assertions=0, errors=[], screenshots=[])


def check(condition, message):
    assert condition, message
    report['assertions'] += 1


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
        doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
        audit = doc['migrationAudit']['v058_economy_science']
        by_id = {e['id']: e for e in doc['events']}
        page = browser.new_page(viewport=dict(width=1440, height=1000))
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        url = (ROOT / name).as_uri()
        for event_id in audit['added_event_ids']:
            event = by_id[event_id]
            page.goto(url + '#tab=lenses&s.view=knowledge&kind=event&id=' + event_id)
            check(page.locator('#modal').is_visible(), event_id + ': permalink opens')
            text = page.locator('#detail').inner_text()
            check(event['title'] in text and event['date'] in text, event_id + ': localized title and date')
            check(event['caveat'] in text, event_id + ': evidence limits visible')
            check(page.locator('#detail a[href="' + event['sources'][0]['url'] + '"]').count() > 0, event_id + ': source link')
            check(page.locator('#detail [data-kind="arc"][data-id="' + event['story_primary_arc_id'] + '"]').count() > 0, event_id + ': arc link')
            check(page.locator('#modal .drawer').evaluate('(e) => e.scrollWidth <= e.clientWidth + 1'), event_id + ': no drawer overflow')
        for claim_id in audit['added_claim_ids']:
            page.goto(url + '#tab=story&kind=claim&id=' + claim_id)
            check(page.locator('#modal').is_visible(), claim_id + ': claim opens')
            claim = next(c for c in doc['claims'] if c['id'] == claim_id)
            for field in ('supporting_evidence', 'qualifying_evidence'):
                check(page.locator('#detail .' + field + ' [data-kind="event"]').count() == len(claim[field]), claim_id + ': ' + field)
            check(claim['caveats'][0] in page.locator('#detail').inner_text(), claim_id + ': limitations visible')
            if lang == 'ru':
                check(claim['recommended_phrasing_en'] in page.locator('#detail').inner_text(), claim_id + ': English phrasing localized correctly')
        for view, event_id in [('economy', audit['added_event_ids'][0]), ('knowledge', 'SIG_2026_MAYA_AGENT_REDISCOVERY_CORRECTION')]:
            page.goto(url + '#tab=lenses&s.view=' + view)
            page.locator('#lens-query').fill(by_id[event_id]['title'])
            check(page.locator('#lens-records [data-id="' + event_id + '"]').count() == 1, view + ': one canonical card')
            for width, height in [(1440, 1000), (390, 844)]:
                page.set_viewport_size(dict(width=width, height=height))
                check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), view + ': page fits')
                shot = OUT / f'{lang}-{view}-{width}.png'
                page.screenshot(path=str(shot), full_page=False)
                report['screenshots'].append(shot.name)
                page.locator('#lens-records [data-id="' + event_id + '"]').click()
                check(page.locator('#modal .drawer').evaluate('(e) => e.scrollWidth <= e.clientWidth + 1'), view + ': responsive drawer')
                page.keyboard.press('Escape')
        page.close()
    browser.close()
check(not report['errors'], 'No JavaScript errors')
report['passed'] = True
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
