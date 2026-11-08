from pathlib import Path
import functools
import hashlib
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/serg/Documents/zhet/build/profgames-aipower-frontier-pacing/aipower')
OUT = Path('/tmp/aipower-v053-independent-visual-audit')
OUT.mkdir(exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
report = {'build': {}, 'scenarios': [], 'errors': [], 'external_requests': []}
files = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts]
before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def result(lang, name, value):
    item = {'language': lang, 'scenario': name, 'observed': value}
    report['scenarios'].append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)

for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
    common = (ROOT / 'src/atlas-common.js').read_text()
    runtime = (ROOT / f'src/atlas-{lang}.js').read_text().replace('/* COMMON_RUNTIME */', common)
    data = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = (ROOT / f'src/template-{lang}.html').read_text().replace('/* REVIEW_STYLES */', (ROOT / 'src/review.css').read_text())
    template = template.replace('&lt;!-- ATLAS_DATA --&gt;', '<!-- ATLAS_DATA -->').replace('&lt;!-- ATLAS_RUNTIME --&gt;', '<!-- ATLAS_RUNTIME -->')
    expected = template.replace('<!-- ATLAS_DATA -->', '<script id="DATA" type="application/json">' + payload + '</script>').replace('<!-- ATLAS_RUNTIME -->', '<script>\n' + runtime + '\n</script>')
    actual = (ROOT / name).read_text()
    report['build'][lang] = {'full_html_matches_in_memory_build': actual == expected, 'runtime_exactly_embedded': runtime in actual, 'sha256': before[name], 'version': data['meta']['version']}

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'

def state(p):
    return p.evaluate('''() => ({url:location.hash,view:document.querySelector('.view.active')?.id,
      detail:currentDetail,history:detailHistory,graph:{...graphState},facts:{...activeFacts()},
      rows:document.querySelectorAll(ATLAS_RU?'#catalog-list .row':'#fact-list .row').length,
      recipeActive:document.querySelector('#recipe-list .active')?.dataset||null,
      storyArcs:document.querySelectorAll('#story-svg .arc-row[data-kind="arc"]').length,
      overviewArcs:document.querySelectorAll('#overview-svg .arc-row').length})''')

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, headless=True)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 1100})
        def route(r):
            if r.request.url.startswith(base + '/'):
                r.continue_()
            else:
                report['external_requests'].append(r.request.url)
                r.abort()
        ctx.route('**/*', route)
        def fresh(url):
            p = ctx.new_page()
            p.on('pageerror', lambda e: report['errors'].append(str(e)))
            p.goto(url)
            p.wait_for_function('window.atlasReady === true && !atlasRestoring')
            return p
        for lang, name in [('ru', 'ai-power-atlas-ru.html'), ('en', 'ai-power-atlas.html')]:
            url = base + '/' + name
            facts = 'catalog' if lang == 'ru' else 'facts'
            data = json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text())
            p = fresh(url + '#tab=' + facts + '&f.actor=NVIDIA')
            initial = state(p)
            p.goto(url + '#tab=' + facts)
            p.wait_for_function('!atlasRestoring')
            warm = state(p)
            q = fresh(url + '#tab=' + facts)
            result(lang, 'missing_filter_in_same_document_url', {'filtered':initial, 'warm_bare_hash':warm, 'cold_bare_hash':state(q)})
            q.close(); p.close()

            p = fresh(url + '#tab=' + facts + '&f.q=OpenAI')
            query_url = state(p)
            p.locator('#search').fill('OpenAI')
            result(lang, 'URL_query_case', {'from_url': query_url, 'same_text_typed': state(p)})
            p.close()

            p = ctx.new_page(); p.goto(base + '/README.md'); p.goto(url)
            p.wait_for_function('window.atlasReady === true && !atlasRestoring')
            p.locator('nav [data-tab="'+facts+'"]').click()
            p.locator('nav [data-tab="stack"]').click()
            before_back = state(p)
            p.go_back()
            back_url = p.url
            p.go_forward()
            result(lang, 'browser_back_forward_after_UI_tabs', {'before_back':before_back, 'back_url':back_url, 'forward_url':p.url})
            p.close()

            recipe = data['recipes'][0]['id']
            p = fresh(url + '#tab=story&g.preset=' + recipe)
            result(lang, 'recipe_restored_from_URL', {'recipe': data['recipes'][0], 'state':state(p), 'rendered_title':p.locator('#recipe-list h3, #recipe-list b').first.inner_text()})
            p.close()
            p = fresh(url + '#tab=story')
            p.locator('#recipe-list').evaluate('(e)=>e.closest("details").open=true') if lang == 'ru' else None
            selector = '[data-preset]' if lang == 'ru' else '[data-recipe]'
            p.locator('#recipe-list ' + selector).first.click()
            chosen = state(p)
            if lang == 'en':
                p.locator('nav [data-tab="overview"]').click()
                result(lang, 'recipe_then_overview', {'chosen':chosen,'overview':state(p)})
                p.screenshot(path=str(OUT / 'en-overview-stale-recipe.png'))
            else:
                result(lang, 'recipe_by_click', chosen)
            p.close()

            layer = 'model_weights'
            p = fresh(url + '#tab=stack')
            row = p.locator('#stack-table tr[data-id="'+layer+'"]')
            row.click()
            opened = state(p)
            p.locator('#detail [data-filter-layer]').click()
            filtered = state(p)
            p.locator('a[data-language-link]').click()
            p.wait_for_function('window.atlasReady === true && !atlasRestoring')
            result(lang, 'stack_layer_filter_then_language', {'layer':layer,'opened':opened,'filtered':filtered,'other_language':state(p)})
            p.close()

            p = fresh(url + '#tab=timeline')
            collisions = p.locator('#timeline-svg .timeline-dot').evaluate_all('''nodes=>{
              let groups={}; for(let n of nodes){let key=[n.getAttribute('cx'),n.getAttribute('cy'),n.dataset.lane].join('|');(groups[key]??=[]).push(n.dataset.id)}
              return Object.entries(groups).filter(([k,v])=>v.length>1).map(([position,ids])=>({position,ids}));}''')
            result(lang,'timeline_exact_coordinate_collisions',collisions)
            if collisions:
                ids=collisions[0]['ids']; target=p.locator('#timeline-svg [data-id="'+ids[0]+'"][data-lane="'+collisions[0]['position'].split('|')[-1]+'"]')
                target.scroll_into_view_if_needed(); box=target.bounding_box()
                p.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
                result(lang,'timeline_collision_click',{'intended_id':ids[0],'overlapping_ids':ids,'opened':state(p)['detail']})
                p.keyboard.press('Escape')
            p.screenshot(path=str(OUT / (lang+'-timeline-desktop.png')))
            p.set_viewport_size({'width':390,'height':844})
            p.screenshot(path=str(OUT / (lang+'-timeline-mobile.png')))
            p.close()

            p = fresh(url + '#tab=story&g.scope=all')
            result(lang,'expanded_story_geometry',p.evaluate('''() => {
              let svg=document.getElementById('story-svg'),r=svg.getBoundingClientRect();
              let groups={}; for(let n of svg.querySelectorAll('.event-dot')){let key=[n.getAttribute('cx'),n.getAttribute('cy'),n.dataset.arc].join('|');(groups[key]??=[]).push(n.dataset.id)}
              return {viewBox:svg.getAttribute('viewBox'),bounds:{x:r.x,y:r.y,width:r.width,height:r.height},
              arcRows:svg.querySelectorAll('.arc-row[data-kind="arc"]').length,thesisNodes:svg.querySelectorAll('[data-kind="thesis"]').length,
              exactCollisions:Object.entries(groups).filter(([k,v])=>v.length>1).slice(0,12),
              dotCount:svg.querySelectorAll('.event-dot').length,
              dates:Array.from(svg.querySelectorAll('.event-dot')).slice(-10).map(n=>({date:n.dataset.date,x:n.getAttribute('cx')}))};}'''))
            p.set_viewport_size({'width':390,'height':844})
            result(lang,'expanded_story_mobile',p.locator('#story-svg').evaluate('''svg=>({width:svg.getBoundingClientRect().width,height:svg.getBoundingClientRect().height,
              scrollWidth:svg.parentElement.scrollWidth,clientWidth:svg.parentElement.clientWidth})'''))
            p.screenshot(path=str(OUT / (lang+'-expanded-mobile.png')))
            p.close()

            p = fresh(url + '#tab=sources')
            result(lang,'source_and_gap_discoverability',p.evaluate('''() => ({
              totalSources:SOURCES.length, sourceLinks:document.querySelectorAll('#source-list a').length,
              groups:SOURCE_GROUPS.length,truncatedGroups:SOURCE_GROUPS.filter(g=>g.sources.length>(ATLAS_RU?4:5)).map(g=>({family:g.family,count:g.sources.length})),
              gaps:GAPS.length,gapEntries:document.querySelectorAll('.view [data-kind="gap"]').length,
              counters:COUNTERS.length,counterEntries:document.querySelectorAll('.view [data-kind="counterargument"]').length})'''))
            p.close()

            if lang == 'ru':
                p = fresh(url + '#tab=actors')
                p.locator('#country-cards [data-kind="country"]').first.click()
                country = {'detail':state(p),'title':p.locator('#detail h2').inner_text()}
                p.locator('a[data-language-link]').evaluate('(e)=>location.href=e.href')
                p.wait_for_function('window.atlasReady === true && !atlasRestoring')
                result(lang,'country_detail_language_link',{'before':country,'after':state(p),'detail_text':p.locator('#detail').inner_text()})
                p.close()
        browser.close()
finally:
    server.shutdown();server.server_close();thread.join()
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}
    report['repository_files_changed_during_run'] = [k for k,v in before.items() if after.get(k)!=v]
    (OUT / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print('REPORT',OUT / 'results.json',flush=True)
