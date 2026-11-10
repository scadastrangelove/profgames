#!/usr/bin/env python3
"""Exercise the new record and cold-route cross-cutting selection in both languages."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review/astra-underperformance-2026-11-10/record-browser'
OUT.mkdir(parents=True, exist_ok=True)
EVENT = 'SIG_2026_ASTRA_COVERT_SAFETY_UNDERPERFORMANCE'
report = dict(assertions=0, errors=[], screenshots=[])


def check(condition, label):
    assert condition, label
    report['assertions'] += 1


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
        page = browser.new_page(viewport=dict(width=1440, height=1000))
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        url = (ROOT / name).as_uri()
        page.goto(url + '#tab=cyber&kind=event&id=' + EVENT)
        check(page.locator('#modal').is_visible(), 'direct cyber record link')
        text = page.locator('#detail').inner_text()
        check('Astra' in text and '2026-08-20' in text and '2026-11-04' in text, 'dates and title visible')
        check(page.locator('#detail a[href="https://alignment.openai.com/misalignment-reports/covert-underperformance-on-safety-research-tasks/"]').count() > 0, 'primary source clickable')
        for width, height in [(1440, 1000), (390, 844)]:
            page.set_viewport_size(dict(width=width, height=height))
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'page fits viewport')
            check(page.locator('#modal .drawer').evaluate('(e) => e.scrollWidth <= e.clientWidth + 1'), 'drawer fits viewport')
            shot = OUT / f'{lang}-{width}.png'
            page.screenshot(path=str(shot), full_page=False)
            report['screenshots'].append(shot.name)
        page.set_viewport_size(dict(width=1440, height=1000))
        for view, track in [('knowledge', 'research_access'), ('delegation', 'agent_boundaries')]:
            page.goto(url + '#tab=lenses&s.view=' + view + '&s.track=' + track)
            page.locator('#lens-query').fill('Astra')
            record = page.locator('#lens-records [data-id="'+EVENT+'"]')
            check(record.count() == 1, view + ' contains the canonical record once')
            record.click()
            check(page.locator('#modal').is_visible(), view + ' record opens')
            page.keyboard.press('Escape')
        page.goto(url + '#tab=lenses&s.view=economy')
        page.locator('#nav [data-tab="story"]').click()
        page.reload()
        check(page.locator('#lens-switch').input_value() == 'economy', 'picker restored off lens route')
        check('s.active=lenses' in page.url, 'active view mode persisted')
        other_file = 'ai-power-atlas.html' if lang == 'ru' else 'ai-power-atlas-ru.html'
        page.locator('a[data-language-link][href^="'+other_file+'#"]').click()
        check(page.locator('#lens-switch').input_value() == 'economy', 'picker survives language change')
        page.locator('#nav [data-tab="cyber"]').click()
        check(page.locator('#view-lenses').is_visible(), 'cross-cutting navigation returns to economy')
        page.locator('#lens-switch').select_option('cyber')
        page.locator('#nav [data-tab="story"]').click()
        page.reload()
        check(page.locator('#lens-switch').input_value() == 'cyber', 'cyber selection also persists')
        page.goto(url + '#tab=story&s.view=sovereignty')
        check(page.locator('#lens-switch').input_value() == 'sovereignty', 'legacy route restored')
        page.close()
    browser.close()
check(not report['errors'], 'no JavaScript errors')
report['passed'] = True
(OUT / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
