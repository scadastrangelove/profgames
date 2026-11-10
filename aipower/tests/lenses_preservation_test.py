#!/usr/bin/env python3
"""Verify evidence equality to published v0.54 and isolated build reproducibility."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = '89919b6029900446ff81426c2664db71c046d25f'
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build
from configure_lenses import configure
from validate import references

report = {'base': BASE, 'checks': 0, 'files': {}}


def check(condition, message):
    assert condition, message
    report['checks'] += 1


framework = json.loads((ROOT / 'src/lenses.json').read_text())
for lang in ('ru', 'en'):
    name = f'ai_power_storygraph_{lang}.json'
    old = json.loads(subprocess.check_output(['git', 'show', f'{BASE}:aipower/{name}'], cwd=ROOT))
    doc = json.loads((ROOT / name).read_text())
    for key in ('events', 'claims', 'claimChecks', 'arcs', 'edges', 'thesisNodes', 'counterarguments', 'gaps', 'sourceIndex', 'sourceGroups', 'entityRegistry'):
        check(doc[key] == old[key], lang + ': unchanged ' + key)
    check(configure(json.loads(json.dumps(doc)), framework) == doc, 'idempotent configuration')
    configured = configure(json.loads(json.dumps(old)), framework)
    check(configured['referenceIntegrity'] == references(configured), 'migration refreshes typed references')
    check(doc['referenceIntegrity'] == references(doc), 'current reference metadata matches all fields')
    check(doc['summary']['total_arcs'] == len(doc['arcs']), 'current legacy arc count')
with tempfile.TemporaryDirectory(prefix='atlas-lenses-build-') as folder:
    target = Path(folder)
    shutil.copytree(ROOT / 'src', target / 'src')
    (target / 'review').mkdir()
    for lang in ('ru', 'en'):
        shutil.copy2(ROOT / f'ai_power_storygraph_{lang}.json', target)
    build(target)
    for name in ('ai-power-atlas-ru.html', 'ai-power-atlas.html', 'review/compiled-ru.js', 'review/compiled-en.js'):
        content = (ROOT / name).read_bytes()
        check(content == (target / name).read_bytes(), 'reproducible ' + name)
        report['files'][name] = hashlib.sha256(content).hexdigest()
for href in re.findall(r'href="([^"]+)"', (ROOT / 'index.html').read_text()):
    u = urlsplit(href)
    if not u.scheme and u.path:
        check((ROOT / unquote(u.path)).exists(), href)
report['passed'] = True
(ROOT / 'review/crosscutting-views-2026-11-09/preservation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
