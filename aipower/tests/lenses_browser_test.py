#!/usr/bin/env python3
"""Bilingual view navigation, filtering, history, keyboard and responsive checks."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('ATLAS_BROWSER_REPORT_DIR', ROOT / 'review/crosscutting-expansion-2026-11-10')).resolve() / 'browser'
OUT.mkdir(parents=True, exist_ok=True)
report = {'assertions': 0, 'screenshots': [], 'errors': []}


def check(condition, message):
    assert condition, message
    report['assertions'] += 1


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        url = (ROOT / name).as_uri()
        page.goto(url + '#tab=lenses&s.view=knowledge')
        check(page.locator('#view-lenses').is_visible(), 'knowledge view opens')
        check(page.locator('#lens-switch').input_value() == 'knowledge', 'selector restored')
        check(page.locator('#lens-records article').count() > 0, 'evidence renders')
        check(page.evaluate('!!(document.querySelector("#view-lenses").compareDocumentPosition(document.querySelector("#footer")) & Node.DOCUMENT_POSITION_FOLLOWING)'), 'view precedes footer')
        check(page.locator('#lens-map td button:not([disabled])').count() > 0, 'matrix nonempty')
        page.locator('#lens-map tbody th button').first.click()
        check('s.track=discovery' in page.url, 'track selection has permalink')
        page.locator('#lens-map td button:not([disabled])').first.click()
        check('s.bucket=' in page.url, 'cell selects date')
        page.locator('#lens-records [data-kind="event"]').first.click()
        check(page.locator('#modal').is_visible(), 'record opens')
        page.keyboard.press('Escape')
        check(not page.locator('#modal').is_visible(), 'record closes')
        page.locator('#lens-reset').click()
        page.locator('#lens-query').fill('a-query-without-matches-987')
        check(page.locator('.lens-empty').is_visible(), 'explicit empty state')
        page.locator('#lens-reset').click()
        page.locator('#lens-geo').select_option('US')
        page.locator('#lens-switch').select_option('economy')
        check(page.locator('#lens-geo').input_value() == 'US', 'shared geo preserved')
        check(page.locator('#lens-title').inner_text() == ('Экономика ИИ' if lang == 'ru' else 'AI Economy'), 'economy opens')
        page.go_back()
        check(page.locator('#lens-switch').input_value() == 'knowledge', 'back restores view')
        page.go_forward()
        check(page.locator('#lens-switch').input_value() == 'economy', 'forward restores view')
        page.locator('#lens-reset').click()
        if page.locator('#lens-pagination button').last.is_enabled():
            page.locator('#lens-pagination button').last.click()
            check('s.page=2' in page.url, 'pagination permalink')
            page.reload()
            check(page.locator('#lens-pagination span').inner_text().startswith('2 /'), 'pagination reload')
        page.locator('#lens-switch').select_option('cyber')
        check(page.locator('#view-cyber').is_visible(), 'legacy cyber remains available')
        page.goto(url + '#tab=lenses&s.view=knowledge&s.period=unknown&s.track=unknown&s.bucket=bad&s.page=nan')
        check(page.locator('#lens-period').input_value() == 'recent', 'invalid state normalizes')
        check(page.locator('#lens-records article').count() > 0, 'invalid state still renders')
        for view in ['knowledge', 'economy', 'sovereignty', 'delegation']:
            page.goto(url + '#tab=lenses&s.view=' + view)
            page.locator('#lens-map td button:not([disabled])').first.click()
            check('s.bucket=' in page.url and 's.track=' in page.url, view + ' cell route')
            page.reload()
            check(page.locator('#lens-records article').count() > 0, view + ' filtered reload')
            page.locator('#lens-records [data-kind="event"]').first.click()
            check(page.locator('#modal').is_visible(), view + ' evidence drawer')
            page.keyboard.press('Escape')
            for width, height in [(1440, 1000), (390, 844)]:
                page.set_viewport_size({'width': width, 'height': height})
                page.goto(url + '#tab=lenses&s.view=' + view)
                page.evaluate('window.scrollTo(0, 0)')
                check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'no page overflow')
                check(page.locator('#lens-title').is_visible(), 'heading visible')
                check(page.locator('#lens-switch').input_value() == view, 'view selection restored')
                check(page.locator('#lens-records h4 button').first.is_visible(), 'card visible')
                path = OUT / f'{lang}-{view}-{width}.png'
                page.screenshot(path=str(path), full_page=False)
                report['screenshots'].append(str(path.relative_to(ROOT)))
                if width == 390:
                    page.locator('#lens-map').scroll_into_view_if_needed()
                    path = OUT / f'{lang}-{view}-matrix-{width}.png'
                    page.locator('#lens-map').screenshot(path=str(path))
                    report['screenshots'].append(str(path.relative_to(ROOT)))
        check(page.locator('a[data-language-link]').first.get_attribute('href').find('s.view=delegation') > 0, 'language link preserves view')
        page.close()
    browser.close()
check(not report['errors'], 'no JavaScript exceptions')
report['passed'] = True
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
