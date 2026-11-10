#!/usr/bin/env python3
"""Run existing browser suites without overwriting historical release reports."""
import shutil
import os
import tempfile
from pathlib import Path

import audit_repair_browser_test
import browser_test

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('ATLAS_BROWSER_REPORT_DIR', ROOT / 'review/crosscutting-expansion-2026-11-10')).resolve()
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

audit_repair_browser_test.OUT = OUT / 'legacy-regression'
audit_repair_browser_test.run(CHROME)
with tempfile.TemporaryDirectory(prefix='atlas-v056-browser-') as tmp:
    target = Path(tmp)
    (target / 'review').mkdir()
    for name in ('ai-power-atlas-ru.html', 'ai-power-atlas.html'):
        shutil.copy2(ROOT / name, target / name)
    browser_test.run(target, CHROME)
    shutil.copytree(target / 'review', OUT / 'full-browser', dirs_exist_ok=True)
