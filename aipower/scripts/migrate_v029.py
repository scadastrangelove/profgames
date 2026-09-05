#!/usr/bin/env python3
"""Apply the reviewed patch to an exact, checksum-pinned v0.29 JSON pair.
Usage: python scripts/migrate_v029.py --input review --output /tmp/atlas-migration
Use --baseline-names for the included review/baseline_*.json filenames.
"""
from pathlib import Path
import argparse,hashlib,json,copy
ROOT=Path(__file__).resolve().parents[1]
def apply(doc,operations):
 doc=copy.deepcopy(doc)
 for op in operations:
  path=op['path']
  if path=='':
   if op['op'] not in ('add','replace'):raise ValueError('Unsupported root operation')
   doc=op['value'];continue
  parts=[x.replace('~1','/').replace('~0','~') for x in path.lstrip('/').split('/')];parent=doc
  for key in parts[:-1]:parent=parent[int(key)] if isinstance(parent,list) else parent[key]
  key=int(parts[-1]) if isinstance(parent,list) else parts[-1]
  if op['op']=='remove':del parent[key]
  elif op['op']=='add' and isinstance(parent,list):parent.insert(key,op['value'])
  elif op['op'] in ('add','replace'):parent[key]=op['value']
  else:raise ValueError('Unsupported operation '+op['op'])
 return doc
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline-names',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 for lang in ['ru','en']:
  name=f'baseline_{lang}.json' if a.baseline_names else f'ai_power_storygraph_{lang}.json';raw=(a.input/name).read_bytes();patch=json.loads((ROOT/f'review/migration_{lang}.json').read_text())
  if hashlib.sha256(raw).hexdigest()!=patch['baseline_sha256']:raise SystemExit(f'{name}: base checksum mismatch; refusing to overwrite a different revision')
  output=(json.dumps(apply(json.loads(raw),patch['operations']),ensure_ascii=False,indent=2)+'\n').encode()
  canonical=json.dumps(json.loads(output),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
  if hashlib.sha256(canonical).hexdigest()!=patch['target_canonical_sha256']:raise SystemExit('Target semantic checksum mismatch')
  dest=a.output/f'ai_power_storygraph_{lang}.json';dest.write_bytes(output);print(dest)
