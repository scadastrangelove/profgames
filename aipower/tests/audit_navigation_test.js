'use strict';

// Run with: node --test tests/audit_navigation_test.js
// Exercise source directly; never read or regenerate the shared built HTML.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const common = fs.readFileSync(path.join(root, 'src/atlas-common.js'), 'utf8');
const clone = value => JSON.parse(JSON.stringify(value));

function section(source, start, end) {
  const from = source.indexOf(start);
  const to = source.indexOf(end, from + start.length);
  assert.ok(from >= 0 && to > from, 'source boundaries: ' + start);
  return source.slice(from, to);
}

function harness(ru, initialHash = '') {
  const language = fs.readFileSync(path.join(root, 'src/atlas-' + (ru ? 'ru' : 'en') + '.js'), 'utf8');
  const pending = [], calls = [], warnings = [], renders = [];
  const documentListeners = {}, windowListeners = {}, elements = new Map();
  const document = {
    body: { style: {} },
    activeElement: null,
    getElementById: id => elements.get(id) || null,
    addEventListener(type, handler) { (documentListeners[type] ||= []).push(handler); },
    querySelector(selector) {
      if (selector === '.view.active') return views.find(node => node.classList.contains('active')) || null;
      return null;
    },
    querySelectorAll(selector) {
      if (selector === '.view') return views;
      if (selector === '#nav button') return nav;
      if (selector === 'a[data-language-link]') return links;
      return [];
    }
  };
  function element(id, tagName = 'INPUT') {
    const classes = new Set(), attributes = {}, listeners = {};
    const node = {
      id, tagName, value: '', dataset: {}, isConnected: true, style: {}, innerHTML: '',
      classList: {
        add: value => classes.add(value),
        remove: value => classes.delete(value),
        contains: value => classes.has(value),
        toggle(value, on) { if (on) classes.add(value); else classes.delete(value); }
      },
      setAttribute(key, value) { attributes[key] = String(value); },
      getAttribute: key => attributes[key] ?? null,
      focus() { document.activeElement = node; },
      closest: selector => selector === 'button' && tagName === 'BUTTON' ? node : null,
      querySelector: () => null,
      querySelectorAll: () => [],
      addEventListener(type, handler) { (listeners[type] ||= []).push(handler); },
      listeners
    };
    elements.set(id, node);
    return node;
  }
  const tabs = ['story', 'cyber', 'timeline', 'stack', 'claims', 'sources', ru ? 'catalog' : 'facts'];
  if (!ru) tabs.unshift('overview');
  const views = tabs.map(tab => element('view-' + tab, 'SECTION'));
  views[0].classList.add('active');
  const nav = tabs.map(tab => { const node = element('nav-' + tab, 'BUTTON'); node.dataset.tab = tab; return node; });
  const links = [false, true].map(targetRu => {
    const node = element(targetRu ? 'language-ru' : 'language-en', 'A');
    node.setAttribute('href', targetRu ? 'ai-power-atlas-ru.html' : 'ai-power-atlas.html');
    return node;
  });
  const origin = element('origin', 'BUTTON');
  origin.focus();
  const modal = element('modal', 'DIV'), drawer = element('drawer', 'DIV'), close = element('close', 'BUTTON');
  close.dataset.close = '1';
  modal.querySelector = selector => selector === '.drawer' ? drawer : selector === 'button[data-close]' ? close : null;
  const detail = element('detail', 'DIV');
  const layerAction = element('layer-action', 'BUTTON');
  layerAction.dataset.filterLayer = 'model_weights';
  detail.querySelectorAll = selector => selector === '[data-filter-layer]' ? [layerAction] : [];
  ['detail-back', 'copy-record-link', 'toggle-arc-levels', 'toggle-auto', 'cyber-principal-toggle', 'cyber-links-toggle'].forEach(id => element(id, 'BUTTON'));
  ['search', 'family-select', 'arc-select', 'relation-select', 'cyber-jurisdiction', 'cyber-domain', 'cyber-force', 'cyber-stage', 'cyber-authority'].forEach(id => element(id));

  let index = 0;
  const entries = [{ hash: initialHash, state: { unrelated: 'preserved' } }];
  const location = { hash: initialHash };
  const history = {
    get state() { return entries[index].state; },
    get length() { return entries.length; },
    pushState(state, title, hash) {
      calls.push({ mode: 'push', hash });
      entries.splice(index + 1);
      entries.push({ hash, state: clone(state) });
      index++;
      location.hash = hash;
    },
    replaceState(state, title, hash) {
      calls.push({ mode: 'replace', hash });
      entries[index] = { hash, state: clone(state) };
      location.hash = hash;
    }
  };
  const context = vm.createContext({
    ATLAS_RU: ru, URLSearchParams, document, history, location,
    window: { addEventListener(type, handler) { (windowListeners[type] ||= []).push(handler); } },
    queueMicrotask: callback => pending.push(callback),
    console: { warn: (...args) => warnings.push(args) },
    EV: [{ id: 'EVENT_A' }, { id: 'EVENT_B' }], EDGES: [],
    byEvent: { EVENT_A: { id: 'EVENT_A' }, EVENT_B: { id: 'EVENT_B' } },
    byArc: { ARC_A: { id: 'ARC_A' } }, byEdge: {}, byClaim: {},
    byCheck: { CHECK_A: { id: 'CHECK_A' } }, byThesis: {}, byCounter: {}, byGap: {},
    detailHtml: (kind, id) => '<h2>' + kind + ':' + id + '</h2>',
    renderEventDetail: event => '<h2>' + event.id + '</h2>',
    renderArcDetail: arc => '<h2>' + arc.id + '</h2>',
    renderClaimCheckDetail: check => '<h2>' + check.id + '</h2>',
    renderLayerDetail: id => '<h2>' + id + '</h2>',
    detailLink: id => id, linkButton: id => id,
    kindLabel: kind => kind
  });
  const run = source => vm.runInContext(source, context);
  run(section(language, 'var graphState =', 'function esc('));
  run(common);
  run(fs.readFileSync(path.join(root, 'src/atlas-lenses.js'), 'utf8'));
  if (ru) {
    run(section(language, 'function setBackButton()', 'function bindSvgTooltips('));
  } else {
    run(section(language, 'function _legacySwitchTab(', 'function moneyB('));
    run(section(language, 'function updateDetailBack()', '/* COMMON_RUNTIME */'));
  }
  const afterCommon = language.slice(language.indexOf('/* COMMON_RUNTIME */') + '/* COMMON_RUNTIME */'.length);
  run(afterCommon.slice(0, afterCommon.indexOf(ru ? 'var footerArcCount' : 'renderHeader();')));
  ['renderCatalog', 'renderFacts', 'renderStoryMap', 'renderStory', 'renderRecipes', 'renderTimeline', 'renderLens'].forEach(name => {
    context[name] = () => renders.push(name);
  });
  // renderCyber writes the route, including when called inside switchTab/restore.
  context.renderCyber = () => { renders.push('renderCyber'); context.writeAtlasHash(); };
  Object.assign(context.cyberState, { domain: '', force: '', stage: '', authority: '' });
  Object.keys(context.filterMap()).forEach(id => element(id));

  function flush() {
    let count = 0;
    while (pending.length) { assert.ok(count++ < 100, 'bounded microtasks'); pending.shift()(); }
  }
  function emit(type, target = origin, action = () => {}, bubble = true) {
    let stopped = false;
    const event = { type, target, key: type === 'keydown' ? 'Escape' : undefined,
      stopPropagation() { stopped = true; }, preventDefault() {} };
    action();
    if (target['on' + type]) target['on' + type](event);
    (target.listeners[type] || []).forEach(handler => handler(event));
    if (bubble && !stopped) (documentListeners[type] || []).forEach(handler => handler(event));
    flush();
  }
  function windowEvent(type) {
    (windowListeners[type] || []).forEach(handler => handler({ type }));
    flush();
  }
  function travel(delta) {
    assert.ok(index + delta >= 0 && index + delta < entries.length, 'history destination exists');
    index += delta;
    location.hash = entries[index].hash;
    windowEvent('popstate');
    windowEvent('hashchange');
  }
  function route(hash) {
    history.pushState(null, '', hash);
    windowEvent('hashchange');
  }
  context.initAtlasNavigation();
  flush();
  function snapshot() {
    return clone({
      states: context.atlasStateGroups().map(([prefix, state]) => [prefix, state]),
      tab: document.querySelector('.view.active').id,
      detail: context.currentDetail,
      controls: Object.fromEntries(Object.keys(context.filterMap()).concat(['search', 'family-select', 'arc-select', 'relation-select']).map(id => [id, elements.get(id).value]))
    });
  }
  return { context, document, elements, links, origin, calls, warnings, renders, history, location,
    flush, emit, route, travel, snapshot, facts: context.activeFacts(), run,
    tab: ru ? 'catalog' : 'facts', layer: ru ? 'lane' : 'layer' };
}

for (const ru of [false, true]) {
  const label = ru ? 'RU' : 'EN';
  test(label + ': omitted URL state resets every group to startup defaults', () => {
    const h = harness(ru);
    const defaults = h.snapshot();
    const dirty = new URLSearchParams({ tab: h.tab, event: 'EVENT_A' });
    h.context.atlasStateGroups().forEach(([prefix, state]) => {
      Object.entries(state).forEach(([key, value]) => dirty.set(prefix + key, typeof value === 'boolean' ? String(!value) : 'changed'));
    });
    h.route('#' + dirty);
    h.route('');
    assert.deepEqual(h.snapshot(), defaults);
    assert.equal(h.context.detailHistory.length, 0);
    assert.equal(h.document.body.style.overflow, '');
    assert.equal(h.elements.get('modal').getAttribute('aria-hidden'), 'true');
  });

  test(label + ': cold and warm hashes have identical route semantics', () => {
    const warm = harness(ru);
    const routes = ['', '#stack', '#tab=' + warm.tab, '#f.actor=Example+Org',
      '#tab=missing', '#tab=cyber&c.showLinks=false&c.principalOnly=true&b.track=research&r.open=true&g.scope=all',
      '#tab=story&g.preset=RECIPE_A&g.family=FAMILY_A&g.arc=ARC_A&g.relation=supports',
      '#event=EVENT_B', '#kind=claimCheck&id=CHECK_A', '#event=UNKNOWN', '#kind=event'];
    for (const hash of routes) {
      warm.route('#tab=cyber&f.actor=prior&f.q=old&event=EVENT_A&c.mode=all&g.showAuto=true');
      warm.route(hash);
      const cold = harness(ru, hash);
      assert.deepEqual(warm.snapshot(), cold.snapshot(), hash || '(empty hash)');
      assert.equal(warm.location.hash, cold.location.hash);
    }
  });

  test(label + ': defaults are captured before reading the initial deep link', () => {
    const h = harness(ru, '#tab=cyber&f.actor=Example&c.showLinks=false&r.open=true');
    assert.equal(h.facts.actor, 'Example');
    h.route('#tab=' + h.tab);
    assert.equal(h.facts.actor, '');
    assert.equal(h.context.cyberState.showLinks, true);
    assert.equal(h.context.resilienceState.open, false);
    assert.equal(h.context.cyberState.mode, 'core');
    assert.equal(h.context.graphState.scope, 'core');
  });

  test(label + ': init replaces; tab, select, recipe and toggles push once', () => {
    const h = harness(ru);
    assert.equal(h.history.length, 1);
    assert.ok(h.calls.every(call => call.mode === 'replace'));
    assert.equal(h.history.state.unrelated, 'preserved');
    const initial = h.location.hash;
    h.emit('click', h.elements.get('nav-' + h.tab), () => h.context.switchTab(h.tab));
    const facts = h.location.hash;
    assert.equal(h.history.length, 2);
    h.emit('change', h.elements.get('filter-actor'), () => { h.facts.actor = 'Example'; });
    assert.equal(h.history.length, 3);
    h.travel(-1);
    assert.equal(h.location.hash, facts);
    assert.equal(h.facts.actor, '');
    h.travel(-1);
    assert.equal(h.location.hash, initial);
    h.travel(1);
    h.emit('click', h.elements.get('nav-cyber'), () => h.context.switchTab('cyber'));
    assert.equal(h.history.length, 3, 'nested render write and click are one entry');
    h.emit('click', h.elements.get('toggle-auto'), () => { h.context.graphState.showAuto = true; });
    h.emit('click', h.origin, () => { h.context.graphState.preset = 'RECIPE_A'; });
    assert.equal(h.history.length, 5);
    h.travel(-1);
    assert.equal(h.context.graphState.preset, '');
    assert.equal(h.context.graphState.showAuto, true);
    assert.ok(h.renders.includes('renderRecipes'));
  });

  test(label + ': transient search replaces and no-op writes do not grow history', () => {
    const h = harness(ru, '#tab=' + (ru ? 'catalog' : 'facts'));
    for (const q of ['e', 'ex', 'example']) h.emit('input', h.elements.get('search'), () => { h.facts.q = q; });
    h.emit('change', h.elements.get('search'));
    assert.equal(h.history.length, 1);
    assert.equal(new URLSearchParams(h.location.hash.slice(1)).get('f.q'), 'example');
    const count = h.calls.length;
    h.context.writeAtlasHash();h.flush();
    h.emit('click', h.origin);
    assert.equal(h.calls.length, count);
    h.context.switchTab('stack');h.flush();
    assert.equal(h.history.length, 2);
    h.travel(-1);
    assert.equal(h.facts.q, 'example');
    assert.equal(h.document.querySelector('.view.active').id, 'view-' + h.tab);
  });

  test(label + ': compound drawer layer action pushes only the final route', () => {
    const h = harness(ru, '#tab=stack');
    h.context.openDetail('layer', 'model_weights');h.flush();
    const before = h.history.length;
    h.emit('click', h.elements.get('layer-action'));
    assert.equal(h.history.length, before + 1);
    assert.equal(h.context.currentDetail, null);
    assert.equal(h.facts[h.layer], 'model_weights');
    assert.equal(h.document.querySelector('.view.active').id, 'view-' + h.tab);
    h.travel(-1);
    assert.equal(h.context.currentDetail.id, 'model_weights');
    assert.equal(h.facts[h.layer], '');
    assert.equal(h.document.querySelector('.view.active').id, 'view-stack');
  });

  test(label + ': actual drawer Back and Escape coexist with browser Back/Forward', () => {
    const h = harness(ru);
    for (const [kind, id] of [['check', 'CHECK_A'], ['event', 'EVENT_A'], ['arc', 'ARC_A']]) {
      h.context.openDetail(kind, id);h.flush();
    }
    assert.equal(h.context.detailHistory.length, 2);
    h.travel(-1);
    assert.equal(h.context.currentDetail.id, 'EVENT_A');
    assert.deepEqual(clone(h.context.detailHistory.map(item => item.id)), ['CHECK_A']);
    h.travel(1);
    assert.equal(h.context.currentDetail.id, 'ARC_A');
    assert.deepEqual(clone(h.context.detailHistory.map(item => item.id)), ['CHECK_A', 'EVENT_A']);
    h.emit('click', h.elements.get('detail-back'));
    assert.equal(h.context.currentDetail.id, 'EVENT_A');
    h.emit('click', h.elements.get('detail-back'));
    assert.equal(h.context.currentDetail.id, 'CHECK_A');
    assert.equal(h.context.detailHistory.length, 0);
    h.emit('keydown');
    assert.equal(h.context.currentDetail, null);
    assert.equal(h.document.body.style.overflow, '');
    assert.equal(h.document.activeElement, h.origin);
    assert.equal(new URLSearchParams(h.location.hash.slice(1)).has('id'), false);
    h.travel(-1);
    assert.equal(h.context.currentDetail.id, 'CHECK_A');
    h.travel(1);
    assert.equal(h.context.currentDetail, null);
    const count = h.history.length;
    h.emit('keydown');
    assert.equal(h.history.length, count, 'Escape with no drawer is a no-op');
  });

  test(label + ': URL traversal cancels stale pending writes and restores once', () => {
    const h = harness(ru);
    h.context.switchTab('stack');
    h.facts.actor = 'pending';h.context.writeAtlasHash();
    h.route('#tab=cyber');
    assert.equal(h.facts.actor, '');
    assert.equal(h.history.length, 2);
    const count = h.renders.length;
    h.context.restoreAtlasHash({ type: 'popstate' });h.flush();
    assert.equal(h.renders.length, count, 'duplicate history/hash events do not render twice');
    h.travel(-1);
    assert.equal(h.document.querySelector('.view.active').id, 'view-' + (ru ? 'story' : 'overview'));
  });

  test(label + ': lane/layer aliases map on input and language links in both directions', () => {
    const h = harness(ru);
    const foreign = ru ? 'layer' : 'lane';
    h.route('#tab=' + (ru ? 'facts' : 'catalog') + '&f.' + foreign + '=model_weights&f.actor=Example+%26+Co&kind=check&id=CHECK_A');
    assert.equal(h.facts[h.layer], 'model_weights');
    assert.equal(h.elements.get('filter-' + h.layer).value, 'model_weights');
    assert.equal(h.document.querySelector('.view.active').id, 'view-' + h.tab);
    assert.equal(new URLSearchParams(h.location.hash.slice(1)).has('f.' + foreign), false);
    const targetHash = '#' + h.links[ru ? 0 : 1].getAttribute('href').split('#')[1];
    const other = harness(!ru, targetHash);
    assert.equal(other.facts[other.layer], 'model_weights');
    assert.equal(other.facts.actor, 'Example & Co');
    assert.equal(other.context.currentDetail.id, 'CHECK_A');
    assert.equal(other.context.currentDetail.kind || other.context.currentDetail.k, ru ? 'check' : 'claimCheck');
    const roundTrip = '#' + other.links[ru ? 1 : 0].getAttribute('href').split('#')[1];
    assert.deepEqual(harness(ru, roundTrip).snapshot(), h.snapshot());
  });

  test(label + ': explicit native layer key wins, including an empty value', () => {
    const h = harness(ru);
    const foreign = ru ? 'layer' : 'lane';
    for (const native of ['', 'governance_law']) {
      h.route('#f.' + foreign + '=model_weights&f.' + h.layer + '=' + native);
      assert.equal(h.facts[h.layer], native);
    }
  });

  test(label + ': browser history failure is reported and language links still update', () => {
    const h = harness(ru);
    h.history.pushState = () => { throw new Error('sandbox'); };
    h.context.switchTab('stack');h.flush();
    assert.equal(h.warnings.length, 1);
    assert.match(h.links[0].getAttribute('href'), /#tab=stack/);
    assert.equal(h.context.atlasRestoring, false);
  });
}
