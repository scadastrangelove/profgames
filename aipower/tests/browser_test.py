#!/usr/bin/env python3
"""Browser regression tests. Uses local document injection: no external requests or API calls.
Install playwright and Chromium; use --chromium to select an executable.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def run(root,executable,only=None):
 report={'mode':'local HTML injection; fresh-document URL-hash restoration; no HTTP deployment test','languages':{},'checks':[]}
 def ok(name,cond):
  if not cond:raise AssertionError(name)
  report['checks'].append(name)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])
  for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
   if only and lang!=only:continue
   print('Testing',lang,flush=True)
   html=(root/name).read_text();pg=b.new_page(viewport={'width':1440,'height':1100});errs=[];requests=[]
   pg.on('pageerror',lambda e,errors=errs:errors.append(str(e)));pg.on('request',lambda r,rs=requests:rs.append(r.url));pg.set_content(html,wait_until='load')
   tabs=pg.locator('nav button').evaluate_all('(xs)=>xs.map(x=>x.dataset.tab)')
   ok(lang+': eight views',len(tabs)==8)
   widths={};heights={}
   for width,height in [(1440,1100),(390,844)]:
    pg.set_viewport_size({'width':width,'height':height})
    for tab in tabs:
     pg.evaluate('(t)=>switchTab(t)',tab);pg.wait_for_timeout(40)
     ok(lang+': active view '+tab+' '+str(width),pg.locator('.view.active').get_attribute('id')=='view-'+tab)
     actual=pg.evaluate('document.documentElement.scrollWidth');widths[f'{tab}:{width}']=actual
     ok(lang+': no page overflow '+tab+' '+str(width),actual<=width)
    pg.evaluate("switchTab('cyber')");pg.wait_for_timeout(80)
    heights['cyber_first_card_'+str(width)]=pg.locator('.cyber-event').first.bounding_box()['y']
    heights['behavior_section_'+str(width)]=pg.locator('.behavior-section').bounding_box()['y']
    pg.screenshot(path=str(root/'review'/f'{lang}-cyber-{width}.png'))
    if width==390:pg.locator('.behavior-section').screenshot(path=str(root/'review'/f'{lang}-behavior-390.png'))
   ok(lang+': mobile behavior layer starts within 850px',heights['behavior_section_390']<850)
   pg.set_viewport_size({'width':1440,'height':1100});pg.evaluate("switchTab('"+('story' if lang=='ru' else 'overview')+"');window.scrollTo(0,0)")
   svg='#story-svg' if lang=='ru' else '#overview-svg';heights['map_top']=pg.locator(svg).bounding_box()['y'];ok(lang+': map above 900px',heights['map_top']<900);pg.screenshot(path=str(root/'review'/f'{lang}-overview.png'))
   pg.evaluate("switchTab('cyber');cyberState.mode='all';cyberState.role='AI_ROLE_DEFENSIVE_TOOL';renderCyber()")
   ok(lang+': Mozilla in defence',pg.locator('.cyber-event[data-id="SIG_2026_MYTHOS_FIREFOX_271"]').count()==1)
   pg.evaluate("cyberState.role='AI_ROLE_ATTACK_ENABLER';renderCyber()")
   ok(lang+': GTG in attack',pg.locator('.cyber-event[data-id="SIG_2025_CLAUDE_ORCHESTRATED_ESPIONAGE"]').count()==1)
   pg.evaluate("cyberState.role='';cyberState.force='binding';renderCyber()")
   ok(lang+': only binding cards',pg.evaluate("cyberRenderedEvents.every(e=>e.normative_force==='binding')"))
   ok(lang+': SB53 binding',pg.locator('.cyber-event[data-id="SIG_2026_CA_SB53_EFFECTIVE"]').count()==1)
   pg.evaluate("cyberState.force='';cyberState.mode='core';renderCyber()")
   ok(lang+': curated Mozilla and SB53',pg.evaluate("['SIG_2026_MYTHOS_FIREFOX_271','SIG_2026_CA_SB53_EFFECTIVE'].every(id=>cyberCoreIds(cyberFocusEvents()).has(id))"))
   ok(lang+': five behavior dependency stages',pg.locator('.behavior-stage').count()==5)
   pg.locator('.behavior-section').screenshot(path=str(root/'review'/f'{lang}-behavior-1440.png'))
   pg.locator('[data-behavior-track="BEH_TRACK_CONCEALMENT_PERSISTENCE"]').click()
   ok(lang+': concealment view has four authored stages',pg.locator('.behavior-stage').count()==4)
   ok(lang+': concealment view selects 20 classified records',pg.evaluate('behaviorEvents(cyberRenderedEvents).length')==20)
   ok(lang+': Astra controllability card is visible',pg.locator('.behavior-evidence-card[data-id="SIG_2026_ASTRA_COT_CONTROLLABILITY_MONITORABILITY"]').count()==1)
   ok(lang+': Astra prompted-evasion card is visible',pg.locator('.behavior-evidence-card[data-id="SIG_2026_ASTRA_PROMPTED_MONITOR_EVASION"]').count()==1)
   ok(lang+': concealment track reaches permalink','b.track=BEH_TRACK_CONCEALMENT_PERSISTENCE' in pg.url)
   pg.locator('.behavior-section').screenshot(path=str(root/'review'/f'{lang}-concealment-track-1440.png'))
   pg.set_viewport_size({'width':390,'height':844})
   ok(lang+': concealment track remains four stages on mobile',pg.locator('.behavior-stage').count()==4)
   ok(lang+': concealment track has no mobile page overflow',pg.evaluate('document.documentElement.scrollWidth')<=390)
   pg.locator('.behavior-section').screenshot(path=str(root/'review'/f'{lang}-concealment-track-390.png'))
   pg.set_viewport_size({'width':1440,'height':1100})
   pg.locator('[data-behavior-mechanism="BEH_POLICY_CONTINUITY"]').click()
   ok(lang+': successor-state mechanism exposes Opus future note',pg.locator('.behavior-evidence-card[data-id="SIG_2025_APOLLO_OPUS4_FUTURE_INSTANCE_NOTES"]').count()==1)
   pg.locator('.behavior-evidence-card[data-id="SIG_2025_APOLLO_OPUS4_FUTURE_INSTANCE_NOTES"]').click()
   detail=pg.locator('#detail').inner_text()
   ok(lang+': concealment metadata visible','external artifact' in detail.lower() if lang=='en' else 'внешний артефакт' in detail.lower())
   pg.keyboard.press('Escape')
   pg.evaluate("behaviorState.track='';behaviorState.mechanism='';renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents())")
   pg.locator('[data-behavior-subdomain="CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"]').click()
   pg.locator('[data-behavior-mechanism="BEH_EXTERNALIZED_STATE"]').click()
   ok(lang+': external-state mechanism exposes wiki incident',pg.locator('.behavior-evidence-card[data-id="SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE"]').count()==1)
   ok(lang+': behavior state reaches permalink','b.mechanism=BEH_EXTERNALIZED_STATE' in pg.url)
   pg.locator('.behavior-evidence-card[data-id="SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE"]').click()
   ok(lang+': behavior metadata drawer',pg.locator('#detail .behavior-metadata').count()==1)
   pg.keyboard.press('Escape')
   pg.locator('[data-behavior-subdomain="CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"]').click()
   ok(lang+': structural-autonomy scale has records',pg.locator('.behavior-evidence-card').count()>0)
   pg.evaluate("behaviorState.subdomain='all';behaviorState.track='';behaviorState.mechanism='';renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents())")
   for country in ['Armenia','Pakistan']:ok(lang+': country facet '+country,pg.locator('#filter-jurisdiction option[value="'+country+'"]').count()==1)
   ok(lang+': Cloudflare facet',pg.locator('#filter-actor option[value="Cloudflare"]').count()==1)
   ok(lang+': NVIDIA alias collapsed',pg.locator('#filter-actor option[value="NVIDIA"]').count()==1 and pg.locator('#filter-actor option[value="Nvidia"]').count()==0)
   ok(lang+': US DOJ alias collapsed',pg.locator('#filter-actor option[value="US Department of Justice"]').count()==1 and pg.locator('#filter-actor option[value="US DOJ"]').count()==0)
   pg.evaluate("switchTab('"+('catalog' if lang=='ru' else 'facts')+"')")
   pg.select_option('#filter-actor','__unresolved__')
   ok(lang+': unresolved filter returns 16',pg.evaluate('EV.filter('+('eventPasses' if lang=='ru' else 'eventPass')+').length')==16)
   pg.select_option('#filter-actor','');pg.select_option('#filter-jurisdiction','Armenia')
   ok(lang+': Armenia records present',pg.evaluate('EV.filter('+('eventPasses' if lang=='ru' else 'eventPass')+').length')>=2)
   pg.select_option('#filter-jurisdiction','');pg.select_option('#filter-actor','Cloudflare')
   ok(lang+': Cloudflare record present',pg.evaluate('EV.filter('+('eventPasses' if lang=='ru' else 'eventPass')+').length')>=1)
   pg.evaluate("switchTab('cyber');cyberState.mode='all';cyberState.force='binding';renderCyber();openDetail('event','SIG_2026_CA_SB53_EFFECTIVE')")
   ok(lang+': typed governance block',pg.locator('.governance-card').count()==1)
   ok(lang+': permalink contains event', 'event=SIG_2026_CA_SB53_EFFECTIVE' in pg.url)
   pg.screenshot(path=str(root/'review'/f'{lang}-binding-record.png'))
   saved=pg.evaluate('location.hash')
   # Fresh document emulates opening a share link without a web server.
   fresh=b.new_page(viewport={'width':1440,'height':1100});fresherrs=[];fresh.on('pageerror',lambda e,es=fresherrs:es.append(str(e)))
   fresh.evaluate('(h)=>history.replaceState(null,"",h)',saved);fresh.set_content(html)
   ok(lang+': fresh permalink opens correct record',fresh.evaluate('currentDetail&&currentDetail.id')=='SIG_2026_CA_SB53_EFFECTIVE')
   ok(lang+': fresh permalink restores filters',fresh.evaluate("cyberState.force==='binding'&&cyberState.mode==='all'"))
   ok(lang+': fresh permalink restores active view',fresh.locator('.view.active').get_attribute('id')=='view-cyber')
   fresh.keyboard.press('Escape');ok(lang+': Escape removes event hash', 'event=' not in fresh.url)
   fresh.close();ok(lang+': no fresh document errors',not fresherrs)
   pg.evaluate("openDetail('event','SIG_2026_KIMI_K3_OPEN_WEIGHT_ANNOUNCEMENT')")
   ok(lang+': Kimi observation visible',pg.locator('.state-card').last.count()>=1 and '2026-09-05' in pg.locator('#detail').inner_text() and '2026-07-16' in pg.locator('#detail').inner_text())
   pg.evaluate('closeDetail()')
   for kind,var in [('counterargument','COUNTERS'),('gap','GAPS')]:
    pg.evaluate('(pair)=>openDetail(pair[0],window[pair[1]][0].id)',[kind,var]);ok(lang+': '+kind+' opens',pg.locator('#detail').inner_text().strip()!='');pg.evaluate('closeDetail()')
   # Render every reviewed card, checking that shared metadata stays total.
   pg.evaluate("cyberFocusEvents().forEach(e=>{openDetail('event',e.id,{replace:true});if(!document.querySelector('#detail .governance-card'))throw new Error('missing governance '+e.id)});closeDetail()")
   ok(lang+': all 133 governance drawers render',not errs)
   ok(lang+': no external requests',not requests)
   ok(lang+': no page errors',not errs)
   report['languages'][lang]={'tabs':tabs,'errors':errs,'external_requests':requests,'positions':heights,'page_widths':widths,'fresh_permalink_errors':fresherrs}
   pg.close()
  b.close()
 report['passed']=True;report['assertions']=len(report['checks']);(root/('review/browser-results-'+only+'.json' if only else 'review/browser-results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--chromium',default='/usr/bin/chromium');a.add_argument('--language',choices=['ru','en']);args=a.parse_args();run(args.root,args.chromium,args.language)
