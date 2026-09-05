#!/usr/bin/env python3
"""Deterministic offline build. Python standard library only; canonical JSON is authoritative."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
def build(root:Path=ROOT)->None:
 css=(root/'src/review.css').read_text(encoding='utf-8')
 common=(root/'src/atlas-common.js').read_text(encoding='utf-8')
 for lang,name in [('ru','ai-power-atlas-ru.html'),('en','ai-power-atlas.html')]:
  data=json.loads((root/f'ai_power_storygraph_{lang}.json').read_text(encoding='utf-8'))
  payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
  runtime=(root/f'src/atlas-{lang}.js').read_text(encoding='utf-8')
  assert runtime.count('/* COMMON_RUNTIME */')==1
  runtime=runtime.replace('/* COMMON_RUNTIME */',common)
  template=(root/f'src/template-{lang}.html').read_text(encoding='utf-8')
  template=template.replace('/* REVIEW_STYLES */',css)
  # Template placeholder comments are emitted as literal text by the template preparer.
  template=template.replace('&lt;!-- ATLAS_DATA --&gt;','<!-- ATLAS_DATA -->').replace('&lt;!-- ATLAS_RUNTIME --&gt;','<!-- ATLAS_RUNTIME -->')
  assert template.count('<!-- ATLAS_DATA -->')==1
  assert template.count('<!-- ATLAS_RUNTIME -->')==1
  html=template.replace('<!-- ATLAS_DATA -->','<script id="DATA" type="application/json">'+payload+'</script>').replace('<!-- ATLAS_RUNTIME -->','<script>\n'+runtime+'\n</script>')
  (root/name).write_text(html,encoding='utf-8')
  (root/'review'/f'compiled-{lang}.js').write_text(runtime,encoding='utf-8')
  print(name, len(html.encode()),'bytes')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
