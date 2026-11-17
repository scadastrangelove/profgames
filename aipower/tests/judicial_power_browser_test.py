#!/usr/bin/env python3
"""Judicial lens, legal stages, source links and responsive RU/EN cards."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'review/judicial-power-2026-11-17/browser'
OUT.mkdir(parents=True, exist_ok=True)
report = dict(assertions=0,errors=[],screenshots=[])
def check(condition,label):
    assert condition,label
    report['assertions']+=1

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
    for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
        doc=json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text())
        page=browser.new_page(viewport=dict(width=1440,height=1000))
        page.on('pageerror',lambda error:report['errors'].append(str(error)))
        url=(ROOT/name).as_uri()+'#tab=lenses&s.view=courts'
        page.goto(url)
        check(page.locator('#lens-switch').input_value()=='courts','Court view selected')
        check(page.locator('#lens-records .lens-record').count()==12,'Exactly 12 canonical cards')
        check(page.locator('#lens-map tbody tr').count()==5,'Five tracks')
        check('2026-11-16' in page.locator('#lens-records .lens-record').first.inner_text(),'Chronology starts with newest event')
        for width,height in [(1440,1000),(390,844)]:
            page.set_viewport_size(dict(width=width,height=height))
            check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Page fits')
            page.screenshot(path=str(OUT/f'{lang}-courts-{width}.png'),full_page=False)
            report['screenshots'].append(f'{lang}-courts-{width}.png')
            for e in [e for e in doc['events'] if e.get('legal_topics')]:
                page.goto(url+'&kind=event&id='+e['id'])
                check(page.locator('#modal').is_visible(),'Permalink opens '+e['id'])
                text=page.locator('#detail').inner_text()
                check(e['title'] in text and e['date'] in text,'Localized title and date')
                check(e['legal_proceeding']['outcome_'+lang] in text,'Legal outcome visible')
                check(e['legal_proceeding']['relief_requested_'+lang] in text,'Requested relief separately visible')
                check(page.locator('#detail a[href="'+e['sources'][0]['url']+'"]').count()>0,'Primary source linked')
                check(page.locator('#modal .drawer').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),'Drawer fits')
            page.goto(url+'&s.track=testing&s.bucket=2026-Q4')
            check(page.locator('#lens-records .lens-record').count()==3,'Testing filings filter')
            page.reload()
            check(page.locator('#lens-records .lens-record').count()==3,'Filter survives reload')
            page.locator('#lens-reset').click()
            check(page.locator('#lens-records .lens-record').count()==12,'Reset restores all events')
        page.close()
    browser.close()
check(not report['errors'],'No JavaScript errors')
report['passed']=True
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
