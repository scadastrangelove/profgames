#!/usr/bin/env python3
"""Rebuild in isolation and verify exact release bytes and local index links."""
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build
from finalize_audit_release import finalize

report = {'passed': False, 'files': {}, 'local_index_links': 0}
with tempfile.TemporaryDirectory(prefix='atlas-audit-build-') as temp:
    root = Path(temp)
    shutil.copytree(ROOT / 'src', root / 'src')
    (root / 'review').mkdir()
    for lang in ('ru', 'en'):
        name = f'ai_power_storygraph_{lang}.json'
        shutil.copy2(ROOT / name, root / name)
        doc = json.loads((ROOT / name).read_text())
        assert finalize(json.loads(json.dumps(doc)), lang) == doc, 'release finalizer must be idempotent'
    build(root)
    for name in ('ai-power-atlas-ru.html', 'ai-power-atlas.html', 'review/compiled-ru.js', 'review/compiled-en.js'):
        before, rebuilt = (ROOT / name).read_bytes(), (root / name).read_bytes()
        assert before == rebuilt, name
        report['files'][name] = hashlib.sha256(before).hexdigest()
for href in re.findall(r'href="([^"]+)"', (ROOT / 'index.html').read_text()):
    url = urlsplit(href)
    if not url.scheme and url.path:
        assert (ROOT / unquote(url.path)).exists(), href
        report['local_index_links'] += 1
report['passed'] = True
(ROOT / 'review/audit-repair-2026-11-08/build-parity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
