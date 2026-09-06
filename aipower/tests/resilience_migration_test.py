#!/usr/bin/env python3
"""Offline migration regression. Requires a pinned v0.33 baseline directory."""
from pathlib import Path
import argparse
import tempfile, subprocess, json, hashlib, shutil, sys
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);args=ap.parse_args()
B=args.baseline.resolve();P=R/'review/resilience-throughput'
checks=[]
def ok(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
script=R/'scripts/migrate_resilience_throughput.py'
with tempfile.TemporaryDirectory() as tmp:
 T=Path(tmp);out=T/'replica';cmd=[sys.executable,str(script),'--root',str(B),'--output',str(out)]
 run=subprocess.run(cmd,capture_output=True,text=True);ok('Pinned pair migrates successfully',run.returncode==0)
 for lang in ['ru','en']:ok('Byte-exact deterministic '+lang,sha(out/f'ai_power_storygraph_{lang}.json')==sha(R/f'ai_power_storygraph_{lang}.json'))
 bad=T/'bad';bad.mkdir()
 for lang in ['ru','en']:shutil.copy2(B/f'ai_power_storygraph_{lang}.json',bad/f'ai_power_storygraph_{lang}.json')
 with (bad/'ai_power_storygraph_en.json').open('ab') as f:f.write(b' ')
 target=T/'refused';test=subprocess.run([sys.executable,str(script),'--root',str(bad),'--output',str(target)],capture_output=True,text=True)
 ok('Modified English input rejected',test.returncode!=0)
 ok('English rejection does not write Russian output',not target.exists() or not list(target.iterdir()))
 before={lang:sha(out/f'ai_power_storygraph_{lang}.json') for lang in ['ru','en']}
 test=subprocess.run([sys.executable,str(script),'--root',str(out),'--output',str(out)],capture_output=True,text=True)
 ok('Already migrated input refused',test.returncode!=0)
 ok('Refused rerun leaves both outputs unchanged',all(sha(out/f'ai_power_storygraph_{lang}.json')==digest for lang,digest in before.items()))
expected={'ru':'8b3211b4efa5c2505787db99b785343b163a28e3','en':'dc4a912c9027b1364a6ea9d8e89977454e21819e'}
for lang,expected_hash in expected.items():
 content=(B/f'ai_power_storygraph_{lang}.json').read_bytes();blob=hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()
 ok('Base snapshot matches GitHub blob '+lang,blob==expected_hash)
report={'passed':True,'assertions':len(checks),'checks':checks,'base_commit':'c1d15d3eb057732d07de5b10329bd412c10958e0'}
(P/'reproduction-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
