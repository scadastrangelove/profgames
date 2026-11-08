const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
let checks = 0;
function ok(value, label) { assert.ok(value, label); checks++; }
for (const lang of ['ru', 'en']) {
  const d = JSON.parse(fs.readFileSync(path.join(root, `ai_power_storygraph_${lang}.json`)));
  const context = { ATLAS_RU: lang === 'ru', D: d, esc: s => String(s ?? ''), host: u => new URL(u).hostname };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(root, 'src/atlas-common.js'), 'utf8'), context);
  context.EV = [
    {id:'current',canonical_event_id:'current',alias_event_ids:['legacy'],sources:[{url:'https://example.org/one'}],caveats:['current caveat'],edgeIds:['one']},
    {id:'legacy',canonical_event_id:'current',exclude_from_presentation:true,sources:[{url:'https://example.org/two'}],caveats:['legacy caveat'],edgeIds:['two']}
  ];
  context.byEvent = Object.fromEntries(context.EV.map(e => [e.id,e]));
  context.EDGES = [{id:'two',source:'legacy',target:'thesis'}];
  context.initCanonicalPresentation();
  ok(context.EV.length === 1 && context.canonicalEventId('legacy') === 'current', 'alias presents once and still resolves');
  ok(context.EV[0].sources.length === 2 && context.EV[0].caveats.length === 2 && context.EV[0].edgeIds.length === 2, 'alias provenance is merged');
  ok(context.EDGES[0].source === 'current', 'alias edge presentation resolves');
  const axis = context.atlasTimeAxis(2015, 2026, 480, 1000);
  ok(axis.segments.length === 8, 'compressed history and four quarter segments');
  ok(axis.x('2027-01-01') - axis.x('2026-01-01') > 0.65 * 520, 'latest year receives most of the axis');
  let last = -Infinity;
  for (let time = Date.UTC(2015, 0, 1); time < Date.UTC(2027, 0, 1); time += 86400000) {
    const x = axis.x(new Date(time).toISOString().slice(0, 10));
    assert.ok(x >= last && x >= 480 && x <= 1000, 'monotonic bounded date mapping');
    last = x;
  }
  checks++;
  for (const segment of axis.segments) {
    const mid = new Date((segment.start + segment.end) / 2).toISOString().slice(0, 10);
    ok(Math.abs(axis.x(mid) - (segment.x0 + segment.x1) / 2) < 1, 'linear time within each segment');
  }
  const facts = d.events.concat(Array.from({length: 40}, (_, i) => ({ id: `collision-${i}`, date: '2026-09-10' })));
  const packed = context.packDatedFacts(facts, axis, 12);
  ok(packed.points.length === facts.length, 'every event gets a point');
  for (let a = 0; a < packed.points.length; a++) {
    for (let b = a + 1; b < packed.points.length; b++) {
      const p = packed.points[a], q = packed.points[b];
      assert.ok(p.level !== q.level || Math.abs(p.x - q.x) >= 12, 'no point overlap within a lane');
    }
  }
  checks++;
  const observations = d.events.filter(e => e.current_state).map(e => context.stateObservation(e));
  ok(observations.every(s => s && s.date && s.title && s.summary), 'all historical state formats yield complete updates');
  ok(observations.some(s => s.date.startsWith('2026-10')), 'October updates are not lost');
  for (const claim of d.claimChecks.filter(c => c.qualifying_evidence?.length)) {
    const html = context.claimEvidenceSections(claim, id => `[${id}]`);
    ok(claim.qualifying_evidence.every(id => html.includes(id)), 'all qualifying evidence is rendered');
  }
  for (const group of d.sourceGroups) {
    const html = context.sourceGroupLinks(group);
    assert.ok(group.sources.every(source => !source.url || html.includes(source.url)), 'every grouped source remains accessible');
  }
  checks++;
}
console.log(JSON.stringify({ passed: true, checks }));
