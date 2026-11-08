import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(dir, "../../..");
const pack = JSON.parse(fs.readFileSync(path.join(dir, "candidates.json"), "utf8"));
const checks = [];
const check = (name, ok, details = null) => checks.push({name, ok: Boolean(ok), details});
// After integration, reproduce the collection audit against its pinned baseline.
const sourceBytes = file => pack.meta.merged_into_atlas && /^aipower\/ai_power_storygraph_(ru|en)\.json$/.test(file)
  ? execFileSync("git", ["show", pack.meta.atlas_commit_reviewed+":"+file], {cwd:root,maxBuffer:30*1024*1024})
  : fs.readFileSync(path.join(root,file));
const read = file => {
  const text = sourceBytes(file).toString("utf8");
  return file.endsWith(".jsonl") ? text.trim().split(/\r?\n/).filter(Boolean).map(JSON.parse) : JSON.parse(text);
};
const hash = file => crypto.createHash("sha256").update(sourceBytes(file)).digest("hex");
const records = value => {
  const result = [];
  const walk = x => {
    if (!x || typeof x !== "object") return;
    if (!Array.isArray(x) && typeof x.id === "string") result.push(x);
    Object.values(x).forEach(walk);
  };
  walk(value);
  return result;
};
const urls = value => {
  const result = new Set();
  const walk = x => {
    if (typeof x === "string" && /^https?:\/\//.test(x)) {
      try { result.add(new URL(x).href); } catch {}
    } else if (x && typeof x === "object") Object.values(x).forEach(walk);
  };
  walk(value);
  return [...result];
};
// Known publication aliases only; no fuzzy equivalence between different studies.
const aliases = new Map([
  ["pubmed.ncbi.nlm.nih.gov/39389057", "doi:10.1016/j.cell.2024.09.027"],
  ["hamsabastani.github.io/education_llm.pdf", "doi:10.1073/pnas.2422633122"],
  ["agupubs.onlinelibrary.wiley.com/doi/10.1029/2025jb031348", "doi:10.1029/2025jb031348"],
  ["pubmed.ncbi.nlm.nih.gov/41620232", "doi:10.1016/s0140-6736(25)02464-x"],
  ["pubmed.ncbi.nlm.nih.gov/41862204", "bmj.com/content/392/bmj-2025-085810"],
  ["wfhresearch.com/wp-content/uploads/2026/03/firm-data-on-ai-16-february-2026.pdf", "nber.org/papers/w34836"],
  ["nber.org/system/files/working_papers/w34836/w34836.pdf", "nber.org/papers/w34836"]
]);
function canonical(raw) {
  const u = new URL(raw);
  const host = u.hostname.toLowerCase().replace(/^www\./, "");
  let pathname = decodeURIComponent(u.pathname).replace(/\/+$/, "");
  if (host === "doi.org" || host === "dx.doi.org") return "doi:" + pathname.slice(1).toLowerCase();
  if (host === "nature.com" && pathname.startsWith("/articles/")) return "doi:10.1038/" + pathname.slice(10).replace(/\.pdf$/, "").toLowerCase();
  if (host === "jamanetwork.com") pathname = pathname.replace("/article-abstract/", "/fullarticle/");
  if (host === "arxiv.org") pathname = pathname.replace(/v\d+$/, "");
  if (host === "journals.plos.org" && u.searchParams.get("id")) return "doi:" + u.searchParams.get("id").toLowerCase();
  const key = (host + pathname).toLowerCase();
  return aliases.get(key) ?? key;
}
function reviewFiles(directory) {
  return fs.readdirSync(directory, {withFileTypes:true}).flatMap(entry => {
    const full = path.join(directory, entry.name);
    if (full === dir) return [];
    if (entry.isDirectory()) return reviewFiles(full);
    return entry.name === "candidates.json" ? [path.relative(root,full)] : [];
  });
}
const masters = ["aipower/ai_power_storygraph_ru.json","aipower/ai_power_storygraph_en.json"];
const companions = [
  "profgames_ai_signals.jsonl", "factcheck.json",
  "aimind/aimind_signals.jsonl", "aimind/atlas.json", "aimind/aimind_factcheck.json"
].filter(file => fs.existsSync(path.join(root,file)));
const files = [...masters, ...companions, ...reviewFiles(path.join(root,"aipower/review"))];
const loaded = new Map(files.map(file => [file,read(file)]));
const byFileId = new Map(files.map(file=>[file,new Map(records(loaded.get(file)).map(r=>[r.id,r]))]));
const baseline = masters.map(file=>{
  const d=loaded.get(file), actual=hash(file);
  check("review baseline matches: "+file, actual===pack.meta.master_sha256[file], {actual,commit:pack.meta.atlas_commit_reviewed});
  return {file,sha256:actual,events:d.events.length,claims:d.claims.length,arcs:d.arcs.length,edges:d.edges.length};
});
const atlas=loaded.get(masters[0]);
const arcIds=new Set(atlas.arcs.map(x=>x.id));
const eventIds=new Set(atlas.events.map(x=>x.id));
const layerIds=new Set(atlas.events.flatMap(x=>Array.isArray(x.stack_layer)?x.stack_layer:[x.stack_layer]).filter(Boolean));
const candidateIds=new Set(pack.candidates.map(x=>x.id));
check("unique candidate IDs",candidateIds.size===pack.candidates.length);
const allMasterIds=new Set(masters.flatMap(f=>[...byFileId.get(f).keys()]));
const refCheck=ref=>{
  const match=byFileId.get(ref.file)?.has(ref.id);
  check("reference: "+ref.file+"#"+ref.id,match);
};
for(const c of pack.candidates){
  check("new candidate ID: "+c.id,!allMasterIds.has(c.id));
  for(const field of ["title_ru","title_en","summary_ru","summary_en","caveat_ru","caveat_en","mechanism_ru","mechanism_en"]){
    check(c.id+"."+field,typeof c[field]==="string"&&c[field].trim().length>0);
  }
  check(c.id+" date shape",c.date_precision==="day"?/^\d{4}-\d{2}-\d{2}$/.test(c.date):/^\d{4}-\d{2}$/.test(c.date));
  check(c.id+" date not retrieval substitution", c.date <= pack.meta.reviewed_at && c.date_kind.length>0);
  check(c.id+" valid arcs",c.proposed_arc_ids.every(id=>arcIds.has(id)));
  check(c.id+" valid stack layers",c.stack_layers.every(id=>layerIds.has(id)),c.stack_layers);
  check(c.id+" valid related events",c.related_existing_event_ids.every(id=>eventIds.has(id)));
  if (c.related_candidate_ids) check(c.id+" valid related candidates",c.related_candidate_ids.every(id=>candidateIds.has(id)));
  check(c.id+" primary sources",c.sources.length>0&&c.sources.every(s=>s.type==="primary"&&new URL(s.url).protocol==="https:"));
  if (c.geo_roles) {
    for (const field of ["developer_organizations", "data_inputs", "upstream_models"]) {
      check(c.id+" geo "+field, Array.isArray(c.geo_roles[field]) && c.geo_roles[field].length > 0 && c.geo_roles[field].every(x=>typeof x === "string" && x.trim()));
    }
    for (const field of ["developer_country_codes", "validation_country_codes"]) {
      const values = c.geo_roles[field];
      check(c.id+" geo "+field, Array.isArray(values) && values.every(x=>/^[A-Z]{2}$/.test(x)) && new Set(values).size === values.length);
    }
    for (const field of ["access_notes_ru", "access_notes_en", "interpretation_limit_ru", "interpretation_limit_en"]) {
      check(c.id+" geo "+field, typeof c.geo_roles[field] === "string" && c.geo_roles[field].trim().length > 0);
    }
    check(c.id+" sources disclose access", c.sources.every(s=>typeof s.access === "string" && s.access.length > 0));
  }
  c.prior_record_refs.forEach(refCheck);
}
pack.reuse_candidates.forEach(refCheck);
for(const q of pack.correction_queue){
 q.refs.forEach(refCheck);
 if(q.candidate_id)check(q.id+" candidate",candidateIds.has(q.candidate_id));
}
const collisionReport=pack.candidates.map(c=>{
  const wanted=new Set(c.sources.map(s=>canonical(s.url)));
  const matches=[];
  for(const [file,data] of loaded){
    for(const record of records(data)){
      const overlap=urls(record.sources ?? record).filter(url=>wanted.has(canonical(url)));
      if(overlap.length)matches.push({file,id:record.id,urls:[...new Set(overlap)]});
    }
  }
  return {candidate_id:c.id,declared_prior_records:c.prior_record_refs,matches};
});
const internalCollisions=[];
for (const collision of collisionReport) {
  const declared = new Set(collision.declared_prior_records.map(r=>r.file+"#"+r.id));
  check(collision.candidate_id+" source duplicates declared", collision.matches.every(m=>declared.has(m.file+"#"+m.id)), collision.matches);
}
for(let i=0;i<pack.candidates.length;i++){
 const a=pack.candidates[i],au=new Set(a.sources.map(s=>canonical(s.url)));
 for(const b of pack.candidates.slice(i+1)){
  const overlap=b.sources.filter(s=>au.has(canonical(s.url))).map(s=>s.url);
  if(overlap.length)internalCollisions.push({a:a.id,b:b.id,urls:overlap});
 }
}
check("no undeclared shared primary sources within new candidates",internalCollisions.length===0,internalCollisions);
const result={
 status:checks.every(x=>x.ok)?"pass":"fail",
 checked_at:pack.meta.reviewed_at,
 scope:"Structural integrity, exact-source aliases and master preservation; not automated fact verification or exhaustive semantic dedup.",
 counts:{candidates:pack.candidates.length,science:pack.candidates.filter(x=>x.track==="science").length,medicine:pack.candidates.filter(x=>x.track==="medicine").length,work:pack.candidates.filter(x=>x.track==="work").length,education:pack.candidates.filter(x=>x.track==="education").length,geo_profiled:pack.candidates.filter(x=>x.geo_roles).length,astronomy:pack.candidates.filter(x=>x.subdomain==="astronomy").length,history_archaeology:pack.candidates.filter(x=>x.subdomain==="history_archaeology").length,reused_prior_candidates:pack.reuse_candidates.length,corrections:pack.correction_queue.length,checks:checks.length,passed:checks.filter(x=>x.ok).length},
 baseline,files_scanned:files,checks,source_collisions:collisionReport.filter(x=>x.matches.length),internal_source_collisions:internalCollisions
};
if(process.argv.includes("--write"))fs.writeFileSync(path.join(dir,"audit-results.json"),JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify({status:result.status,counts:result.counts,failures:checks.filter(x=>!x.ok),source_collisions:result.source_collisions},null,2));
if(result.status!=="pass")process.exitCode=1;
