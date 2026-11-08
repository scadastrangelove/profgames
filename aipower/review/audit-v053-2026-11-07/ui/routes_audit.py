from pathlib import Path
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT=Path('/Users/serg/Documents/zhet/build/profgames-aipower-frontier-pacing/aipower')
OUT=Path('/tmp/aipower-v053-independent-visual-audit')
results=[]
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}'
def add(lang,scenario,observed):
    item=dict(language=lang,scenario=scenario,observed=observed);results.append(item)
    print(json.dumps(item,ensure_ascii=False),flush=True)
def state(p):
    return p.evaluate('''()=>({hash:location.hash,detail:currentDetail,history:detailHistory,
        view:document.querySelector('.view.active')?.id,actor:activeFacts().actor,
        rows:document.querySelectorAll(ATLAS_RU?'#catalog-list .row':'#fact-list .row').length})''')
try:
  with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
    ctx=b.new_context(viewport={'width':1440,'height':1100})
    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base+'/') else r.abort())
    def sized_page(width,height):
        p=ctx.new_page();p.set_viewport_size({'width':width,'height':height});return p
    for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
      url=base+'/'+name;data=json.loads((ROOT/f'ai_power_storygraph_{lang}.json').read_text())
      p=ctx.new_page();p.goto(url+'#tab='+('catalog' if lang=='ru' else 'facts'))
      unfiltered=p.url
      p.goto(url+'#tab='+('catalog' if lang=='ru' else 'facts')+'&f.actor=NVIDIA')
      filtered=p.url
      p.go_back();back=state(p);p.go_forward();forward=state(p)
      add(lang,'browser_history_restores_prior_unfiltered_URL',{'unfiltered':unfiltered,'filtered':filtered,'back':back,'forward':forward})
      p.close()

      for width,height in [(1440,1100),(390,844)]:
        p=sized_page(width,height)
        p.goto(url+'#tab=story&g.arc=ARC_QUIET_ACCESS_CONTROL')
        candidate='SIG_2026_ANTHROPIC_GTG30005_NAVAL_RECONNAISSANCE'
        selector='#story-svg .event-dot[data-id="'+candidate+'"]'
        dot=p.locator(selector);dot.scroll_into_view_if_needed()
        hit=dot.evaluate('''n=>{let b=n.getBoundingClientRect();let x=b.x+b.width/2,y=b.y+b.height/2;
          let same=[...n.parentNode.querySelectorAll('.event-dot')].filter(q=>q.getAttribute('cx')===n.getAttribute('cx')&&q.getAttribute('cy')===n.getAttribute('cy'));
          return {box:{x,y,width:b.width,height:b.height},same:same.map(q=>({id:q.dataset.id,date:q.dataset.date,r:q.getAttribute('r')})),
          top:document.elementFromPoint(x,y)?.closest('[data-id]')?.dataset.id};}''')
        p.mouse.click(hit['box']['x'],hit['box']['y'])
        add(lang,'same_date_story_pointer_'+str(width),{'candidate':candidate,'hitTest':hit,'opened':state(p)['detail']})
        p.screenshot(path=str(OUT/f'{lang}-story-collision-{width}.png'))
        p.close()

      p=ctx.new_page();p.goto(url+'#tab=story&g.arc=ARC_KNOWLEDGE_PRODUCTION_VALIDATION')
      knowledge=p.evaluate('''()=>({arc:byArc.ARC_KNOWLEDGE_PRODUCTION_VALIDATION.id,
        datedFacts:factsForArc(byArc.ARC_KNOWLEDGE_PRODUCTION_VALIDATION).length,
        renderedDots:document.querySelectorAll('#story-svg .event-dot').length,
        dateBounds:storyBounds(),allDateXWithinBounds:EV.every(e=>{let b=storyBounds(),x=storyDateX(e.date,b.min,b.max,480,1000);return x>=480&&x<=1000}),
        dotLabelsMatch: [...document.querySelectorAll('#story-svg .event-dot')].every(n=>n.dataset.date===byEvent[n.dataset.id].date)})''')
      p.locator('#story-svg [data-kind="arc"][data-id="ARC_KNOWLEDGE_PRODUCTION_VALIDATION"]').click()
      knowledge['linkedFacts']=p.locator('#detail [data-kind="event"]').count()
      knowledge['technicalEdges']=p.locator('#detail [data-kind="edge"]').count()
      knowledge['allEdges']=sum(1 for e in data['edges'] if e.get('arc_id')=='ARC_KNOWLEDGE_PRODUCTION_VALIDATION')
      add(lang,'knowledge_growth_and_dates',knowledge);p.close()

      check=next(c for c in data['claimChecks'] if c.get('supporting_evidence') and any(e['id']==c['supporting_evidence'][0] and e.get('story_primary_arc_id') for e in data['events']))
      eid=check['supporting_evidence'][0]
      event=next(e for e in data['events'] if e['id']==eid);aid=event['story_primary_arc_id']
      for width,height in [(1440,1100),(390,844)]:
        p=sized_page(width,height);p.goto(url+'#tab=claims')
        p.locator('.view.active [data-id="'+check['id']+'"]').click()
        chain=[state(p)['detail']]
        p.locator('#detail [data-kind="event"][data-id="'+eid+'"]').click();chain.append(state(p)['detail'])
        sourceLinks=p.locator('#detail a[href]').evaluate_all('xs=>xs.map(x=>x.getAttribute("href"))')
        p.locator('#detail [data-kind="arc"][data-id="'+aid+'"]').first.click();chain.append(state(p)['detail'])
        p.locator('#detail-back').click();chain.append(state(p)['detail'])
        p.locator('#detail-back').click();chain.append(state(p)['detail'])
        fit=p.locator('#detail').evaluate('e=>({scrollWidth:e.scrollWidth,clientWidth:e.clientWidth})')
        p.keyboard.press('Escape')
        add(lang,'claimcheck_event_arc_back_'+str(width),{'chain':chain,'sourceLinks':sourceLinks,'fit':fit,'closed':p.locator('#modal').get_attribute('aria-hidden')})
        p.close()

      p=ctx.new_page();p.goto(url+'#tab=stack')
      add(lang,'heatmap_matches_counts',p.evaluate('''()=>[...document.querySelectorAll('#stack-table tbody tr')].map(row=>{
        let expected=EV.filter(e=>(e.stack_layer||[]).includes(row.dataset.id)).length;
        let cells=[...row.querySelectorAll('td')].slice(1).map(c=>Number(c.textContent));
        return {layer:row.dataset.id,expected,total:cells.at(-1),sum:cells.slice(0,-1).reduce((a,b)=>a+b,0),match:cells.at(-1)===expected&&cells.slice(0,-1).reduce((a,b)=>a+b,0)===expected};})'''));p.close()

      for kind,collection in [('counterargument','counterarguments'),('gap','gaps'),('claim','claims')]:
        obj=data[collection][0];p=sized_page(390,844)
        p.goto(url+'#tab=sources&kind='+kind+'&id='+obj['id'])
        first=state(p);title=p.locator('#detail h2').inner_text();p.reload();restored=state(p)
        p.keyboard.press('Escape')
        add(lang,kind+'_cold_reload_mobile',{'id':obj['id'],'title':title,'before':first,'restored':restored,'closed':p.locator('#modal').get_attribute('aria-hidden')})
        p.close()

      p=ctx.new_page();p.goto(url+'#tab=story&kind=event&id='+eid)
      p.goto(url+'#tab=story&kind=event&id=DOES_NOT_EXIST')
      add(lang,'invalid_detail_id_after_valid',{'requested':'DOES_NOT_EXIST','actual':state(p),'title':p.locator('#detail h2').inner_text()});p.close()

      p=ctx.new_page();p.goto(url+'#tab=story&g.preset=VIEW_06_RUSSIA_SELECTIVE_SOVEREIGNTY')
      if lang=='ru':p.locator('details').filter(has=p.locator('#recipe-list')).locator('summary').click()
      add(lang,'recipe_URL_active_visual',{'preset':p.evaluate('graphState.preset'),'active':p.locator('#recipe-list .active').count(),'arcs':p.locator('#story-svg [data-kind="arc"]').count()})
      p.screenshot(path=str(OUT/f'{lang}-recipe-restored.png'));p.close()
    b.close()
finally:
  server.shutdown();server.server_close();thread.join()
  (OUT/'routes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
