#!/usr/bin/env python3
"""Export reproducible JSON Patch ledgers and hashes from pinned v0.29 to v0.30."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def ptr(k):return str(k).replace('~','~0').replace('/','~1')
def diff(a,b,path=''):
 if type(a) is not type(b):return [{'op':'replace','path':path,'value':b}]
 if isinstance(a,dict):
  out=[]
  for k in sorted(a.keys()-b.keys()):out.append({'op':'remove','path':path+'/'+ptr(k)})
  for k in sorted(b.keys()-a.keys()):out.append({'op':'add','path':path+'/'+ptr(k),'value':b[k]})
  for k in sorted(a.keys()&b.keys()):out+=diff(a[k],b[k],path+'/'+ptr(k))
  return out
 if isinstance(a,list) and len(a)==len(b):
  out=[]
  for i,(x,y) in enumerate(zip(a,b)):out+=diff(x,y,path+'/'+str(i))
  return out
 return [] if a==b else [{'op':'replace','path':path,'value':b}]
def main():
 for lang in ['ru','en']:
  baseline=ROOT/f'review/baseline_{lang}.json';out=ROOT/f'ai_power_storygraph_{lang}.json';old=json.loads(baseline.read_text());new=json.loads(out.read_text());ops=diff(old,new)
  ledger={'base_commit':'156e39a21b5a523092ccb2975e5aa38f489f52b6','baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'target_canonical_sha256':hashlib.sha256(json.dumps(new,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'operations':ops}
  (ROOT/f'review/migration_{lang}.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
  changes=[]
  for field in ['events','claims','edges','thesisNodes']:
   previous={x['id']:x for x in old[field]}
   for x in new[field]:
    before=previous[x['id']];fields={k:{'before':before.get(k),'after':x.get(k),'before_present':k in before,'after_present':k in x} for k in sorted(set(before)|set(x)) if before.get(k)!=x.get(k) or (k in before)!=(k in x)}
    if fields:changes.append({'collection':field,'id':x['id'],'fields':fields})
  (ROOT/f'review/changes_{lang}.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
  print(lang,len(ops),'JSON Patch operations',len(changes),'changed records')
 d=json.loads((ROOT/'ai_power_storygraph_ru.json').read_text());keys=['artifact_kind','normative_force','implementation_stage','primary_domain_id','cyber_domain_ids','cyber_role_ids','delegated_authority','editorial_priority','scope_ru','scope_en','role_basis_ru','role_basis_en','editorial_rationale_ru','editorial_rationale_en','classification_review']
 (ROOT/'review/cyber-classification-ledger.json').write_text(json.dumps({e['id']:{k:e[k] for k in keys} for e in d['events'] if e.get('primary_domain_id')},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
