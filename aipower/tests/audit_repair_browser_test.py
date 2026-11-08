#!/usr/bin/env python3
"""Regression checks for audit repairs and expanded recent-year chronology."""
import argparse
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review/audit-repair-2026-11-08'


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(chromium):
    OUT.mkdir(exist_ok=True, parents=True)
    report = {'passed': False, 'checks': [], 'errors': []}

    def ok(label, value):
        if not value:
            raise AssertionError(label)
        report['checks'].append(label)

    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium, headless=True)
            context = browser.new_context()
            context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(base + '/') else route.abort())
            for lang, filename in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
                data = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
                url = base + '/' + filename
                catalog = 'catalog' if lang == 'ru' else 'facts'
                page = context.new_page()
                page.on('pageerror', lambda error: report['errors'].append(str(error)))
                page.set_viewport_size({'width': 1440, 'height': 1100})
                page.goto(url + '#tab=timeline')
                aliases = data.get('record_aliases', {})
                ok(lang + ': aliases excluded from event counts', page.evaluate('EV.length') == len(data['events']) - len(aliases))
                for old_id, canonical_id in aliases.items():
                    page.goto(url + '#tab=timeline&kind=event&id=' + old_id)
                    ok(lang + ': old event permalink resolves to canonical record', page.evaluate('currentDetail.id') == canonical_id)
                    ok(lang + ': alias provenance visible', page.locator('#detail .alias-provenance').count() == 1)
                    page.keyboard.press('Escape')
                for arc in data['arcs']:
                    if not arc.get('context_nodes'):
                        continue
                    page.evaluate("id=>openDetail('arc',id)", arc['id'])
                    ok(lang + ': historical context separately linked', all(page.locator('#detail .historical-context [data-id="' + node + '"]').count() == 1 for node in arc['context_nodes']))
                    ok(lang + ': historical context excluded from in-period markers', page.evaluate("id=>factsForArc(byArc[id]).every(e=>!byArc[id].context_nodes.includes(e.id))", arc['id']))
                    page.keyboard.press('Escape')
                ok(lang + ': timeline has four latest-year quarter labels', page.locator('#timeline-svg .time-label').count() >= 4)
                ok(lang + ': updates never render blank headings', page.locator('#state-observations h3').evaluate_all("ns=>ns.every(n=>n.textContent.trim().length>20&&!n.textContent.includes('undefined'))"))
                dates = page.locator('#state-observations time').all_text_contents()
                ok(lang + ': updates newest first', dates == sorted(dates, reverse=True))
                ok(lang + ': October updates visible', any(date.startswith('2026-10') for date in dates))
                news_dates = page.locator('#recent-events time').all_text_contents()
                ok(lang + ': latest events newest first', news_dates == sorted(news_dates, reverse=True) and news_dates[0] == max(e['date'] for e in data['events']))
                before = page.locator('.chronology-row').count()
                page.locator('#recent-more').click()
                ok(lang + ': news pagination', page.locator('.chronology-row').count() > before)
                for width in [1440, 390]:
                    page.set_viewport_size({'width': width, 'height': 1100 if width == 1440 else 844})
                    page.goto(url + '#tab=timeline')
                    collision = page.locator('#timeline-svg').evaluate("""svg=>{const p=[...svg.querySelectorAll('circle')];for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++){const a=p[i],b=p[j];if(a.dataset.lane!==b.dataset.lane)continue;const d=Math.hypot(+a.getAttribute('cx')-b.getAttribute('cx'),+a.getAttribute('cy')-b.getAttribute('cy'));if(d < +a.getAttribute('r') + +b.getAttribute('r'))return [a.dataset.id,b.dataset.id];}return null;}""")
                    ok(f'{lang}/{width}: timeline has no overlapping targets', collision is None)
                    ok(f'{lang}/{width}: no page-wide overflow', page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                    page.screenshot(path=str(OUT / f'{lang}-timeline-{width}.png'), full_page=True)
                    page.evaluate('window.scrollTo(0,0)')
                    page.screenshot(path=str(OUT / f'{lang}-timeline-viewport-{width}.png'))
                    page.goto(url + '#tab=story&g.arc=ARC_QUIET_ACCESS_CONTROL')
                    collision = page.locator('#story-svg').evaluate("""svg=>{const p=[...svg.querySelectorAll('.event-dot')];for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++){const a=p[i],b=p[j];if(a.dataset.arc!==b.dataset.arc)continue;if(Math.hypot(+a.getAttribute('cx')-b.getAttribute('cx'),+a.getAttribute('cy')-b.getAttribute('cy'))<10)return[a.dataset.id,b.dataset.id];}return null;}""")
                    ok(f'{lang}/{width}: story has no overlapping targets', collision is None)
                    target = 'SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE'
                    page.locator('#story-svg .event-dot[data-id="' + target + '"]').click()
                    ok(f'{lang}/{width}: marker opens its own event', page.evaluate('currentDetail.id') == target)
                    page.keyboard.press('Escape')
                    page.screenshot(path=str(OUT / f'{lang}-story-{width}.png'), full_page=True)
                page.set_viewport_size({'width': 1440, 'height': 1100})
                for claim in data['claimChecks']:
                    if not claim.get('qualifying_evidence'):
                        continue
                    page.goto(url + '#tab=claims&kind=check&id=' + claim['id'])
                    ids = page.locator('#detail .qualifying_evidence [data-id]').evaluate_all('ns=>ns.map(n=>n.dataset.id)')
                    ok(lang + ': qualifier links ' + claim['id'], set(ids) == set(claim['qualifying_evidence']))
                page.goto(url + '#tab=sources')
                got = set(page.locator('#source-list a').evaluate_all('ns=>ns.map(n=>n.href)'))
                expected = {s['url'] for group in data['sourceGroups'] for s in group['sources'] if s.get('url')}
                ok(lang + ': every source reachable', got == expected)
                ok(lang + ': source expansion available', page.locator('#source-list details').count() > 0)
                page.goto(url + '#tab=' + catalog + '&f.actorType=public_official')
                rows = page.locator('#catalog-list .row' if lang == 'ru' else '#fact-list .row')
                ok(lang + ': reviewed public official is filterable', rows.count() == 1 and rows.get_attribute('data-id') == 'SIG_2026_TEXAS_ELECTION_DC_PAUSE_PLEDGE')
                page.goto(url + '#tab=' + catalog + '&f.actor=Lund%20University')
                rows = page.locator('#catalog-list .row' if lang == 'ru' else '#fact-list .row')
                ok(lang + ': reviewed research institution is filterable', rows.count() > 0)
                page.evaluate("openDetail('event','SIG_2026_MASAI_INTERVAL_CANCER')")
                detail = page.locator('#detail').inner_text()
                ok(lang + ': canonical actor visible in research card', 'Lund University' in detail)
                ok(lang + ': resolved actor has no outstanding type warning', page.locator('#detail .actor-review').count() == 0)
                ok(lang + ': research card has no governance boilerplate', 'Карточка отделяет обязательное предписание' not in detail and 'The record separates a binding directive' not in detail)
                page.keyboard.press('Escape')
                page.goto(url + '#tab=' + catalog)
                total = page.evaluate('EV.length')
                page.goto(url + '#tab=' + catalog + '&f.actor=NVIDIA')
                page.go_back()
                ok(lang + ': browser Back clears absent filter', page.evaluate('activeFacts().actor') == '')
                ok(lang + ': browser Back restores complete catalog', page.locator('#catalog-list .row' if lang == 'ru' else '#fact-list .row').count() == total)
                page.locator('#nav [data-tab="stack"]').click()
                page.go_back()
                ok(lang + ': tab navigation creates browser history', page.locator('.view.active').get_attribute('id') == 'view-' + catalog)
                field = 'lane' if lang == 'ru' else 'layer'
                page.goto(url + '#tab=' + catalog + '&f.' + field + '=model_weights')
                href = page.locator('a[data-language-link]').first.get_attribute('href')
                page.goto(base + '/' + href)
                ok(lang + ': language switch preserves layer', page.evaluate("activeFacts()[ATLAS_RU?'lane':'layer']") == 'model_weights')
                if lang == 'en':
                    page.goto(url + '#tab=story')
                    page.locator('[data-recipe="VIEW_01_TIMELINE_LANES"]').click()
                    story = page.locator('#story-svg [data-kind="arc"]').count()
                    page.locator('#nav [data-tab="overview"]').click()
                    ok('en: Overview reflects recipe without reload', page.locator('#overview-svg [data-kind="arc"]').count() == story)
                page.close()
            ok('no JavaScript errors', not report['errors'])
            browser.close()
        report['passed'] = True
    finally:
        server.shutdown()
        server.server_close()
        (OUT / 'browser-tests.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': len(report['checks'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium', default='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    run(parser.parse_args().chromium)
