#!/usr/bin/env python3
"""Desktop/mobile regression for institutional scientific access records."""
import argparse
import functools
import json
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright
from browser_test import run as full_regression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from migrate_scientific_access import RECORDS, PACKET, VERSION, ROSALIND, CVP, ACCESS


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(executable):
    report = dict(version=VERSION, passed=False, checks=[])
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report['checks'].append(label)
    with tempfile.TemporaryDirectory(prefix='atlas-v053-browser-') as tmp:
        root = Path(tmp)
        (root / 'review').mkdir()
        for name in ['ai-power-atlas-ru.html', 'ai-power-atlas.html']:
            (root / name).symlink_to(ROOT / name)
        full_regression(root, executable)
        (PACKET / 'full-browser-tests.json').write_bytes((root / 'review/browser-results.json').read_bytes())
        for name in ['ru-story-hierarchy.png', 'en-story-hierarchy.png', 'ru-cyber-390.png', 'en-cyber-390.png']:
            (PACKET / name).write_bytes((root / 'review' / name).read_bytes())
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=executable, headless=True)
            for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
                page = browser.new_page(viewport={'width': 1440, 'height': 1100})
                errors = []
                page.on('pageerror', lambda e, es=errors: es.append(str(e)))
                url = f'http://127.0.0.1:{server.server_port}/{name}'
                page.goto(url)
                doc = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
                events = {e['id']: e for e in doc['events']}
                page.locator('nav [data-tab="' + ('catalog' if lang == 'ru' else 'facts') + '"]').click()
                listing = '#catalog-list' if lang == 'ru' else '#fact-list'
                for candidate in RECORDS:
                    eid = candidate['id']
                    page.locator('#search').fill(eid)
                    row = page.locator(listing + f' [data-id="{eid}"]')
                    row.wait_for(state='visible')
                    ok(lang + ': unique search ' + eid, row.count() == 1)
                    row.click()
                    detail = page.locator('#detail')
                    text = detail.inner_text()
                    ok(lang + ': exact summary and caveat ' + eid, events[eid]['summary'] in text and events[eid]['caveat'] in text)
                    if lang == 'ru':
                        ok(lang + ': localized date basis ' + eid, candidate['date_basis'].replace('_', ' ') not in text)
                    hrefs = detail.locator('a').evaluate_all('xs=>xs.map(x=>x.href)')
                    ok(lang + ': every source linked ' + eid, all(s['url'] in hrefs for s in events[eid]['sources']))
                    if eid != CVP:
                        ok(lang + ': research metadata ' + eid, detail.locator('.research-metadata').is_visible())
                    if eid == ROSALIND:
                        ok(lang + ': access terms have observation date', events[eid]['current_state']['summary'] in text and '2026-11-07' in text and '2026-10-30' in text)
                        ok(lang + ': no serialized object in drawer', '[object Object]' not in text)
                    for width, height in [(1440, 1100), (390, 844)]:
                        page.set_viewport_size({'width': width, 'height': height})
                        ok(f'{lang}: fits {width} ' + eid, page.evaluate('document.documentElement.scrollWidth') <= width and detail.evaluate('e=>e.scrollWidth<=e.clientWidth'))
                        if eid == ROSALIND:
                            page.screenshot(path=str(PACKET / f'{lang}-rosalind-{width}.png'))
                    aid = events[eid]['story_primary_arc_id']
                    detail.locator(f'[data-id="{aid}"]').first.click()
                    ok(lang + ': linked arc ' + eid, page.evaluate('currentDetail.id') == aid and detail.locator(f'[data-id="{eid}"]').count() > 0)
                    page.locator('#detail-back').click()
                    ok(lang + ': Back ' + eid, page.evaluate('currentDetail.id') == eid)
                    page.keyboard.press('Escape')
                    ok(lang + ': Escape ' + eid, page.locator('#modal').get_attribute('aria-hidden') == 'true')
                    page.set_viewport_size({'width': 1440, 'height': 1100})
                page.locator('#search').fill('')
                page.evaluate("switchTab('cyber');cyberState.mode='all';renderCyber()")
                cyber_ids = page.evaluate('cyberRenderedEvents.map(e=>e.id)')
                ok(lang + ': CVP included; pure biology excluded from cyber', CVP in cyber_ids and not ({r['id'] for r in RECORDS if r['id'] != CVP} & set(cyber_ids)))
                page.evaluate("cyberState.mode='core';renderCyber()")
                ok(lang + ': CVP in curated cyber map', page.locator(f'.cyber-event[data-id="{CVP}"]').count() == 1)
                page.goto(url + '#tab=story&kind=event&id=' + ROSALIND)
                ok(lang + ': record permalink', page.evaluate('currentDetail.id') == ROSALIND)
                page.reload()
                ok(lang + ': record survives reload', page.evaluate('currentDetail.id') == ROSALIND)
                page.goto(url + '#tab=story&kind=arc&id=' + ACCESS)
                ok(lang + ': updated arc text visible', next(a['thesis'] for a in doc['arcs'] if a['id'] == ACCESS) in page.locator('#detail').inner_text())
                page.screenshot(path=str(PACKET / f'{lang}-access-arc.png'))
                ok(lang + ': no JavaScript errors', not errors)
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    report.update(passed=True, assertions=len(report['checks']), temporary_server_stopped=True)
    (PACKET / 'browser-tests.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Passed', report['assertions'], 'scientific access UI checks; temporary server stopped')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium', required=True)
    run(parser.parse_args().chromium)
