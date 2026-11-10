'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const test=require('node:test');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'src/atlas-lenses.js'),'utf8');
function context(doc){
 const c=vm.createContext({D:doc,EV:doc.events.filter(e=>!e.exclude_from_presentation),EDGES:doc.edges,alist:x=>Array.isArray(x)?x:x==null?[]:[x],lf:(x,k)=>x[k+'_en']||x[k]||''});vm.runInContext(source,c);return c;
}
for(const lang of ['ru','en']){
 const d=JSON.parse(fs.readFileSync(path.join(root,`ai_power_storygraph_${lang}.json`),'utf8'));
 test(lang+' views resolve all references and preserve shared membership',()=>{
  const c=context(d),arcs=new Set(d.arcs.map(x=>x.id));
  for(const v of c.lensViews()){
   assert.ok(v.label_ru&&v.label_en);
   assert.equal(new Set(v.tracks.map(t=>t.id)).size,v.tracks.length);
   for(const t of v.tracks){assert.ok(t.label_ru&&t.label_en);for(const id of [...t.arc_ids,...t.required_arc_ids||[]])assert.ok(arcs.has(id),id);}
   const all=c.lensAllEvents(v);assert.ok(all.length>0);assert.equal(new Set(all.map(e=>e.id)).size,all.length);
   c.lensState.view=v.id;const recent=c.lensFiltered(v,true);
   assert.ok(recent.every(e=>Number(e.date.slice(0,4))>=Number(d.meta.updated_at.slice(0,4))-1));
   for(const t of v.tracks){c.lensState.track=t.id;assert.ok(c.lensFiltered(v,true).every(e=>c.lensTrackMatches(e,t)));}
   c.lensState.track='';c.lensState.q='zz-no-such-evidence';assert.equal(c.lensFiltered(v,true).length,0);c.lensState.q='';
  }
 });
 test(lang+' required-arc gate excludes mere cyber access records',()=>{
  const c=context(d),t=c.lensViews()[0].tracks.find(t=>t.id==='research_access');
  assert.equal(c.lensTrackMatches({arcIds:t.arc_ids},t),false);
  assert.equal(c.lensTrackMatches({arcIds:[...t.arc_ids,...t.required_arc_ids]},t),true);
 });
 test(lang+' delegation gates outcomes without classifying by title',()=>{
  const c=context(d),view=c.lensViews().find(v=>v.id==='delegation'),t=view.tracks.find(t=>t.id==='human_verification');
  for(const outcome of ['physical_lab_validation','employment_hiring_distribution','job_posting_demand_not_employment','exposure_not_realized_effect']){
   assert.equal(c.lensTrackMatches({arcIds:t.arc_ids,research_outcome_stage:outcome,title:'human verification'},t),false);
  }
  for(const outcome of ['clinical_workflow','measured_learning_outcomes','engineering_workflow']){
   assert.equal(c.lensTrackMatches({arcIds:t.arc_ids,research_outcome_stage:outcome,title:'unrelated title'},t),true);
  }
  assert.ok(!c.lensAllEvents(view).some(e=>e.id==='SIG_2025_GENERATIVE_ANTIBIOTICS_PRECLINICAL_VALIDATION'));
 });
 test(lang+' matrix buckets partition filtered events',()=>{
  const c=context(d);
  for(const v of c.lensViews())for(const period of ['all','recent','latest']){
   c.lensState.period=period;const buckets=c.lensBuckets(v);
   for(const e of c.lensFiltered(v,false))assert.equal(buckets.filter(b=>c.lensBucketContains(e,b)).length,1,e.id);
  }
 });
 test(lang+' relationships never invent adjacency or use hidden endpoints',()=>{
  const c=context(d);c.EDGES=[{source:'a',target:'b',relation:'context_for'},{source:'a',target:'c',relation:'context_for'},{source:'a',target:'b',relation:'part_of_arc'},{source:'a',target:'b',relation:'supports',is_auto:true}];
  const edges=c.lensExplicitEdges([{id:'a'},{id:'b'}]);assert.equal(edges.length,1);assert.equal(edges[0].relation,'context_for');
 });
 test(lang+' inactive-route picker restores the last cross-cutting selection',()=>{
  const c=context(d),select={value:'cyber'};
  c.document={getElementById:()=>select,querySelector:()=>({classList:{add(){}}})};c.renderLens=()=>{};
  c.lensState.view='economy';c.syncLensNavigation('lenses');c.syncLensNavigation('story');
  assert.equal(select.value,'economy');assert.equal(c.lensState.active,'lenses');
  select.value='cyber';c.syncLensNavigation('timeline');assert.equal(select.value,'economy');
  c.syncLensNavigation('cyber');select.value='economy';c.syncLensNavigation('story');
  assert.equal(select.value,'cyber');assert.equal(c.lensState.view,'economy');
 });
}
test('future-effective records cannot move the recent window',()=>{
 const c=context({meta:{updated_at:'2026-11-09'},events:[{date:'2027-01-01',arcIds:['ARC']}],edges:[]});
 assert.equal(c.lensBuckets({tracks:[{arc_ids:['ARC']}]}).join(','),'2026-Q1,2026-Q2,2026-Q3,2026-Q4');
});
test('RU/EN view schemas are identical',()=>{
 const data=lang=>JSON.parse(fs.readFileSync(path.join(root,`ai_power_storygraph_${lang}.json`),'utf8'));
 assert.deepEqual(data('ru').crosscuttingViews,data('en').crosscuttingViews);
});
