#!/usr/bin/env python3
"""Run the full UI suite plus bilingual November-record HTTP/mobile regression."""
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from migrate_stack_refresh import RECORDS, PACKET, VERSION

class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def run(executable):
 report=dict(version=VERSION,passed=False,checks=[],mode='temporary localhost plus offline regression; no external model calls')
 def ok(label,condition):
  if not condition:raise AssertionError(label)
  report['checks'].append(label)
 with tempfile.TemporaryDirectory(prefix='atlas-v051-browser-') as tmp:
  root=Path(tmp);(root/'review').mkdir()
  for name in ['ai-power-atlas-ru.html','ai-power-atlas.html']:(root/name).symlink_to(ROOT/name)
  full_regression(root,executable)
  (PACKET/'full-browser-tests.json').write_bytes((root/'review/browser-results.json').read_bytes())
  for name in ['ru-story-hierarchy.png','en-story-hierarchy.png','ru-cyber-390.png','en-cyber-390.png']:
   (PACKET/name).write_bytes((root/'review'/name).read_bytes())
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=executable,headless=True)
   for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
    page=browser.new_page(viewport={'width':1440,'height':1100});errors=[]
    page.on('pageerror',lambda e,es=errors:es.append(str(e)))
    url=f'http://127.0.0.1:{server.server_port}/{name}'
    page.goto(url);doc=json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text());ev={e['id']:e for e in doc['events']}
    page.locator('nav [data-tab="'+('catalog' if lang=='ru' else 'facts')+'"]').click()
    listing='#catalog-list' if lang=='ru' else '#fact-list'
    for r in RECORDS:
     eid=r['id'];page.locator('#search').fill(eid)
     row=page.locator(listing+f' [data-id="{eid}"]');row.wait_for(state='visible')
     ok(lang+': unique search '+eid,row.count()==1);row.click()
     detail=page.locator('#detail');text=detail.inner_text()
     ok(lang+': exact detail '+eid,ev[eid]['summary'] in text and ev[eid]['caveat'] in text)
     hrefs=detail.locator('a').evaluate_all('xs=>xs.map(x=>x.href)')
     ok(lang+': all sources clickable '+eid,all(s['url'] in hrefs for s in ev[eid]['sources']))
     for width,height in [(1440,1100),(390,844)]:
      page.set_viewport_size({'width':width,'height':height})
      ok(f'{lang}: detail fits {width} '+eid,page.evaluate('document.documentElement.scrollWidth')<=width and detail.evaluate('e=>e.scrollWidth<=e.clientWidth'))
      if r['key']=='JAIS3_OPEN_ARABIC_AGENTS':page.screenshot(path=str(PACKET/f'{lang}-jais-{width}.png'))
     page.locator(f'#detail [data-id="{r["arcs"][0]}"]').first.click()
     ok(lang+': arc navigation '+eid,page.evaluate('currentDetail.id')==r['arcs'][0] and page.locator(f'#detail [data-id="{eid}"]').count()>0)
     page.locator('#detail-back').click();ok(lang+': Back '+eid,page.evaluate('currentDetail.id')==eid)
     page.keyboard.press('Escape');ok(lang+': Escape '+eid,page.locator('#modal').get_attribute('aria-hidden')=='true')
     page.set_viewport_size({'width':1440,'height':1100})
    page.locator('#search').fill('');page.locator('nav [data-tab="cyber"]').click()
    for mode in ['all','core']:
     page.evaluate("m=>{cyberState.mode=m;renderCyber()}",mode)
     for r in RECORDS:
      present=bool(r['domains']) and (mode=='all' or r['priority']==1)
      ok(lang+': cyber selection '+mode+' '+r['id'],page.locator(f'.cyber-event[data-id="{r["id"]}"]').count()==int(present))
    page.goto(url+'#tab=cyber&kind=event&id=SIG_2026_DEBIAN_DSA6602_KERNEL_PATCH_BATCH')
    ok(lang+': HTTP permalink',page.evaluate('currentDetail.id')=='SIG_2026_DEBIAN_DSA6602_KERNEL_PATCH_BATCH')
    page.reload();ok(lang+': reload preserves detail',page.evaluate('currentDetail.id')=='SIG_2026_DEBIAN_DSA6602_KERNEL_PATCH_BATCH')
    ok(lang+': no JavaScript exceptions',not errors);page.close()
   browser.close()
 finally:
  server.shutdown();server.server_close();thread.join()
 report.update(passed=True,assertions=len(report['checks']),temporary_server_stopped=True)
 (PACKET/'browser-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed',report['assertions'],'November UI checks; temporary server stopped')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--chromium',required=True);run(parser.parse_args().chromium)
