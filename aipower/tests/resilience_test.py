#!/usr/bin/env python3
"""Offline regressions for v0.34 reading tracks, measurement semantics and links."""
from pathlib import Path
import argparse, json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def run(root: Path, executable: str):
    raw=json.loads((root/'review/resilience-throughput/candidates.json').read_text())
    report={'mode':'local HTML injection and fresh-document hash restoration; no model calls or network','checks':[],'languages':{}}
    def ok(name, condition):
        print(name, bool(condition), flush=True)
        if not condition:raise AssertionError(name)
        report['checks'].append(name)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])
        for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
            html=(root/name).read_text();page=browser.new_page(viewport={'width':1440,'height':1100});page.set_default_timeout(12000);errors=[];requests=[]
            page.on('pageerror',lambda e,es=errors:es.append(str(e)))
            page.on('request',lambda q,rs=requests:rs.append(q.url))
            page.set_content(html,wait_until='load')
            page.evaluate("switchTab('cyber');cyberState.mode='all';resilienceState.open=true;renderCyber()")
            ok(lang+': six local track controls',page.locator('[data-resilience-track]').count()==6)
            ok(lang+': all 31 tagged records in layer',page.locator('#resilience-count').inner_text()=='31 / 31')
            ok(lang+': CVD anchor visible',page.locator('.resilience-evidence-card[data-id="SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG"]').count()==1)
            ok(lang+': historical slop comes after core records',page.evaluate("Array.from(document.querySelectorAll('.resilience-evidence-card')).map(x=>x.dataset.id).at(-1)==='SIG_2026_CURL_BOUNTY_CLOSURE'"))
            for t in raw['tracks']:
                page.locator('[data-resilience-track="'+t['id']+'"]').click()
                count=page.evaluate('(id)=>D.cyberFramework.resilience_tracks.find(t=>t.id===id).event_ids.length',t['id'])
                ok(lang+': every track displays all matching records '+t['id'],page.locator('.resilience-evidence-card').count()==count)
                ok(lang+': track persisted '+t['id'],'r.track='+t['id'] in page.url)
            page.locator('[data-resilience-track="RES_TRACK_VERIFIED_REMEDIATION"]').click()
            for width,height in [(1440,1100),(390,844)]:
                page.set_viewport_size({'width':width,'height':height})
                page.locator('#resilience-section').scroll_into_view_if_needed()
                page.evaluate("document.getElementById('resilience-section').scrollIntoView({block:'start',behavior:'instant'});")
                ok(lang+': new layer has no overflow '+str(width),page.evaluate('document.documentElement.scrollWidth')<=width)
                page.screenshot(path=str(root/'review/resilience-throughput'/f'{lang}-tracks-{width}.png'))
            page.set_viewport_size({'width':1440,'height':1100})
            page.evaluate("openDetail('event','SIG_2026_ANTHROPIC_CVD_VALIDATED_BACKLOG')")
            text=page.locator('#detail .resilience-metadata').inner_text()
            ok(lang+': CVD unit-aware five metric cards',page.locator('#detail .resilience-metric').count()==5)
            ok(lang+': CVD no-funnel warning',('Не последовательная воронка' in text if lang=='ru' else 'Not a sequential funnel' in text))
            ok(lang+': CVD reviewed denominator present',('91,4%' in text if lang=='ru' else '91.4%' in text) and '5008' in text and '4576' in text)
            page.locator('#detail .resilience-metadata').screenshot(path=str(root/'review/resilience-throughput'/f'{lang}-cvd-metrics.png'))
            page.keyboard.press('Escape')
            for event in raw['events']:
                page.evaluate('(id)=>openDetail("event",id)',event['id'])
                ok(lang+': new record has governance and resilience metadata '+event['id'],page.locator('#detail .governance-card').count()==1 and page.locator('#detail .resilience-metadata').count()==1)
                page.keyboard.press('Escape')
            page.evaluate("openDetail('event','SIG_2026_RUST_IN_PEACE_AGENT_ASSISTED_DISCLOSURES')")
            state=page.locator('#detail .state-card').inner_text()
            ok(lang+': rust observation not a model-weight note','37' in state and '33' in state and 'weights' not in state.lower() and 'весов' not in state)
            page.keyboard.press('Escape')
            page.evaluate("openDetail('event','SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION')")
            text=page.locator('#detail .resilience-metadata').inner_text()
            ok(lang+': undated sprint explicitly distinguished',('дата наблюдения страницы' in text if lang=='ru' else 'page-observation date' in text))
            page.keyboard.press('Escape')
            ok(lang+': observation not incorrectly future',page.locator('.cyber-event[data-id="SIG_2026_DEFENSE_FACTORY_VERIFIED_REMEDIATION"]').get_attribute('class').find('is-future')==-1)
            page.evaluate("cyberState.force='binding';renderCyber()")
            ok(lang+': reading layer respects global enforceability filter',page.evaluate("Array.from(document.querySelectorAll('.resilience-evidence-card')).every(x=>byEvent[x.dataset.id].normative_force==='binding')"))
            page.evaluate("cyberState.force='';cyberState.mode='core';resilienceState.track='RES_TRACK_MAINTENANCE_CAPACITY';renderCyber()")
            ok(lang+': historical card excluded from core',page.locator('.resilience-evidence-card[data-id="SIG_2026_CURL_BOUNTY_CLOSURE"]').count()==0)
            page.evaluate("resilienceState.track='RES_TRACK_INCIDENT_LEARNING';resilienceState.open=true;renderCyber();openDetail('event','SIG_2026_SAFE_INCIDENT_LEARNING_RFC')")
            permalink=page.url
            ok(lang+': language switch preserves reading state',page.locator('a[data-language-link]').first.get_attribute('href').find('r.track=RES_TRACK_INCIDENT_LEARNING')>=0)
            fresh=browser.new_page();fresh_errors=[];fresh.on('pageerror',lambda e,es=fresh_errors:es.append(str(e)))
            fresh.goto(permalink);fresh.set_content(html,wait_until='load')
            ok(lang+': fresh-document track restore',fresh.evaluate('resilienceState.track')=='RES_TRACK_INCIDENT_LEARNING')
            ok(lang+': fresh-document open restore',fresh.locator('#resilience-section').evaluate('(x)=>x.open') is True)
            ok(lang+': fresh-document selected card restore',fresh.locator('#detail .resilience-metadata').count()==1 and 'SAFE' in fresh.locator('#detail').inner_text())
            ok(lang+': no JS errors',not errors and not fresh_errors)
            ok(lang+': no external requests',not requests)
            report['languages'][lang]={'errors':errors,'fresh_errors':fresh_errors,'external_requests':requests,'tested_new_records':len(raw['events']),'track_count':6}
            fresh.close();page.close()
        browser.close()
    report.update(passed=True,assertions=len(report['checks']))
    (root/'review/resilience-throughput/browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--chromium',default='/usr/bin/chromium');args=ap.parse_args();run(args.root,args.chromium)
