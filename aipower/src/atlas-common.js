/* v0.34 shared presentation and navigation. No semantic overrides of the JSON. */
var atlasRestoring = true;
var atlasReturnFocus = null;
var atlasReady = false;
var resilienceState = { track:'RES_TRACK_MAINTENANCE_CAPACITY', open:false };
var behaviorState = { subdomain:'all', track:'', mechanism:'' };
function tx(ru,en){ return ATLAS_RU ? ru : en; }
function alist(x){ return Array.isArray(x) ? x : (x == null ? [] : [x]); }
function lf(x,key){ return x && (x[key+'_'+(ATLAS_RU?'ru':'en')] || x[key] || '') || ''; }
function vocab(group,id){ var x=alist(CYBER_FRAMEWORK[group]).find(function(v){return v.id===id;}); return x?lf(x,'label'):String(id||''); }
function relationLabel(id){var label=(D.relationLabels||{})[id];return label?label[ATLAS_RU?'ru':'en']:String(id||'').replace(/_/g,' ');}
function cyberFocusEvents(){ return EV.filter(function(e){return !!e.primary_domain_id && alist(e.cyber_domain_ids).length>0;}).sort(function(a,b){return String(a.date).localeCompare(String(b.date))||a.id.localeCompare(b.id);}); }
function cyberDomains(){return alist(CYBER_FRAMEWORK.domains);}
function cyberDomain(e){return e.primary_domain_id;}
function cyberCoreIds(events){return new Set(events.filter(function(e){return e.editorial_priority===1;}).map(function(e){return e.id;}));}
function bindAtlasCards(root){
 if(!root)return;
 root.querySelectorAll('[data-kind][data-id]').forEach(function(n){
  n.onclick=function(e){e.stopPropagation();openDetail(n.dataset.kind,n.dataset.id);};
  if(!['BUTTON','A'].includes(n.tagName)){
   n.setAttribute('tabindex','0');n.setAttribute('role','button');
   n.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openDetail(n.dataset.kind,n.dataset.id);}};
  }
 });
}
function bindClickable(root){bindAtlasCards(root);}
function bindClicks(root){bindAtlasCards(root);}
function fillSelect(id,values,caption,label){var n=document.getElementById(id);if(!n)return;n.innerHTML='<option value="">'+esc(caption)+'</option>'+values.map(function(v){return'<option value="'+esc(v)+'">'+esc(label?label(v):v)+'</option>';}).join('');}
function initCyberControls(){
 cyberState.domain='';cyberState.force='';cyberState.stage='';cyberState.authority='';
 var events=cyberFocusEvents();
 fillSelect('cyber-jurisdiction',Array.from(new Set(events.flatMap(function(e){return alist(e.jurisdictions);}))).sort(),tx('Все юрисдикции','All jurisdictions'));
 fillSelect('cyber-domain',cyberDomains().map(function(d){return d.id;}),tx('Все домены','All domains'),function(id){return lf(cyberDomainMeta(id),'label');});
 [['force','normative_forces'],['stage','implementation_stages'],['authority','delegated_authority_states']].forEach(function(pair){
  fillSelect('cyber-'+pair[0],alist(CYBER_FRAMEWORK[pair[1]]).map(function(v){return v.id;}),tx({force:'Любая обязательность',stage:'Любая стадия',authority:'Любое делегирование'}[pair[0]],{force:'Any enforceability',stage:'Any stage',authority:'Any delegation'}[pair[0]]),function(id){return vocab(pair[1],id);});
 });
 document.querySelectorAll('[data-cyber-mode]').forEach(function(n){n.onclick=function(){cyberState.mode=n.dataset.cyberMode;renderCyber();};});
 document.querySelectorAll('[data-cyber-role]').forEach(function(n){n.onclick=function(){cyberState.role=n.dataset.cyberRole;renderCyber();};});
 ['jurisdiction','domain','force','stage','authority'].forEach(function(k){document.getElementById('cyber-'+k).onchange=function(){cyberState[k]=this.value;renderCyber();};});
 document.getElementById('cyber-principal-toggle').onclick=function(){cyberState.principalOnly=!cyberState.principalOnly;renderCyber();};
 document.getElementById('cyber-links-toggle').onclick=function(){cyberState.showLinks=!cyberState.showLinks;renderCyber();};
 var reset=document.getElementById('cyber-reset');if(reset)reset.onclick=function(){Object.assign(cyberState,{mode:'core',role:'',jurisdiction:'',domain:'',force:'',stage:'',authority:'',principalOnly:false,showLinks:true});Object.assign(behaviorState,{subdomain:'all',track:'',mechanism:''});Object.assign(resilienceState,{track:'RES_TRACK_MAINTENANCE_CAPACITY',open:false});renderCyber();};
 var note=document.getElementById('cyber-framework-note');if(note)note.textContent=lf(CYBER_FRAMEWORK,'summary');
 var method=document.getElementById('cyber-method');if(method)method.textContent=lf(CYBER_FRAMEWORK,'method_note');
 window.addEventListener('resize',function(){if(document.getElementById('view-cyber').classList.contains('active'))drawCyberLinks();});
}
function syncCyberControls(){
 document.querySelectorAll('[data-cyber-mode]').forEach(function(n){n.classList.toggle('active',n.dataset.cyberMode===cyberState.mode);n.setAttribute('aria-pressed',n.dataset.cyberMode===cyberState.mode);});
 document.querySelectorAll('[data-cyber-role]').forEach(function(n){n.classList.toggle('active',n.dataset.cyberRole===cyberState.role);n.setAttribute('aria-pressed',n.dataset.cyberRole===cyberState.role);});
 ['jurisdiction','domain','force','stage','authority'].forEach(function(k){var n=document.getElementById('cyber-'+k);if(n)n.value=cyberState[k]||'';});
 var p=document.getElementById('cyber-principal-toggle');p.classList.toggle('active',!!cyberState.principalOnly);p.setAttribute('aria-pressed',!!cyberState.principalOnly);p.textContent=tx('Наблюдавшиеся / тестовые полномочия','Observed / tested authority');
 var l=document.getElementById('cyber-links-toggle');l.classList.toggle('active',!!cyberState.showLinks);l.setAttribute('aria-pressed',!!cyberState.showLinks);l.textContent=cyberState.showLinks?tx('Прямые связи','Direct links'):tx('Связи скрыты','Links hidden');
}
function cyberEventCard(e){
 var future=String(e.date||'')>String(D.meta.updated_at||'2026-09-06');
 var roles=alist(e.cyber_role_ids).map(function(id){return'<span class="cyber-role '+cyberRoleClass(id)+'">'+esc(lf(cyberRoleMeta(id),'short')||lf(cyberRoleMeta(id),'label'))+'</span>';}).join('');
 var authority={observed:tx('доступ: наблюдался','access: observed'),evaluated:tx('доступ: тест','access: evaluated'),control_requirement:tx('требования к правам','authority controls')}[e.delegated_authority];
 if(authority)roles+='<span class="cyber-role principal">'+esc(authority)+'</span>';
 alist(e.cyber_subdomain_ids).forEach(function(id){var meta=alist(CYBER_FRAMEWORK.subdomains).find(function(x){return x.id===id;});if(meta)roles+='<span class="cyber-role behavior-domain">'+esc(String(lf(meta,'label')).split('·')[0].trim())+'</span>';});
 return'<article class="cyber-event '+(future?'is-future':'')+'" role="button" tabindex="0" data-kind="event" data-id="'+esc(e.id)+'" data-cyber-domain="'+esc(e.primary_domain_id)+'">'+
 '<div class="cyber-event-head"><time>'+esc(e.date)+'</time><span>'+esc(vocab('artifact_kinds',e.artifact_kind))+'</span></div>'+
 '<div class="cyber-event-title">'+esc(e.title)+'</div><div class="cyber-event-roles">'+roles+'</div>'+
 '<div class="cyber-event-meta"><span class="force-'+esc(e.normative_force)+'">'+esc(vocab('normative_forces',e.normative_force))+'</span></div>'+
 '<div class="cyber-event-meta">'+esc(vocab('implementation_stages',e.implementation_stage))+' · '+esc(alist(e.jurisdictions).slice(0,2).join(' / '))+(future?' · '+tx('будущая дата','future date'):'')+'</div></article>';
}
function behaviorMeta(group,id){return alist(CYBER_FRAMEWORK[group]).find(function(x){return x.id===id;})||null;}
function atlasStatusLabel(id){return ATLAS_RU?statusLabelRu(id):statusLabel(id);}
function atlasEvidenceContextLabel(id){return ATLAS_RU?evidenceContextLabelRu(id):evidenceContextLabel(id);}
function behaviorEvents(events){
 return events.filter(function(e){
  if(!alist(e.behavioral_mechanism_ids).length)return false;
  if(behaviorState.subdomain!=='all'&&!alist(e.cyber_subdomain_ids).includes(behaviorState.subdomain))return false;
  return !behaviorState.track||alist(e.behavior_track_ids).includes(behaviorState.track);
 });
}
function behaviorEvidenceCard(e){
 var statuses=alist(e.behavioral_status).map(function(id){var m=behaviorMeta('behavioral_statuses',id);return'<span class="behavior-evidence-chip status-'+esc(id)+'">'+esc(m?lf(m,'label'):String(id).replace(/_/g,' '))+'</span>';}).join('');
 var contexts=alist(e.evidence_context).map(function(id){var m=behaviorMeta('evidence_contexts',id);return m?lf(m,'label'):atlasEvidenceContextLabel(id);}).filter(Boolean).join(' · ');
 var origin=e.behavior_origin?vocab('behavior_origins',e.behavior_origin):'';
 var media=alist(e.persistence_media).map(function(id){return vocab('persistence_media',id);}).filter(Boolean).join(' · ');
 var facets=[origin,media].filter(Boolean).join(' / ');
 return '<article class="behavior-evidence-card" role="button" tabindex="0" data-kind="event" data-id="'+esc(e.id)+'"><div class="behavior-evidence-head"><time>'+esc(e.date)+'</time><span>'+esc(e.evidence_level||e.confidence||'')+'</span></div><h4>'+esc(e.title)+'</h4><div class="behavior-evidence-tags">'+(statuses||'<span class="behavior-evidence-chip">'+tx('Контекстная запись','Context record')+'</span>')+'</div>'+(contexts?'<p>'+esc(contexts)+'</p>':'')+(facets?'<p class="behavior-evidence-facets">'+esc(facets)+'</p>':'')+'</article>';
}
function renderBehaviorLayer(events,allCyber){
 var root=document.getElementById('behavior-map'),list=document.getElementById('behavior-evidence-list'),controls=document.getElementById('behavior-subdomains'),trackControls=document.getElementById('behavior-tracks');
 if(!root||!list||!controls||!trackControls)return;
 var subdomains=alist(CYBER_FRAMEWORK.subdomains),groups=alist(CYBER_FRAMEWORK.behavior_groups),mechanisms=alist(CYBER_FRAMEWORK.behavioral_mechanisms),tracks=alist(CYBER_FRAMEWORK.behavior_tracks);
 var activeTrack=tracks.find(function(x){return x.id===behaviorState.track;})||null;
 var eligible=behaviorEvents(events),allEligible=behaviorEvents(allCyber);
 controls.innerHTML=[{id:'all',label:tx('5A + 5B','5A + 5B')}].concat(subdomains.map(function(x){return{id:x.id,label:lf(x,'short')};})).map(function(x){return'<button type="button" data-behavior-subdomain="'+esc(x.id)+'" class="'+(behaviorState.subdomain===x.id?'active':'')+'" aria-pressed="'+(behaviorState.subdomain===x.id)+'">'+esc(x.label)+'</button>';}).join('');
 controls.querySelectorAll('[data-behavior-subdomain]').forEach(function(button){button.onclick=function(){behaviorState.subdomain=button.dataset.behaviorSubdomain;behaviorState.mechanism='';renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents());writeAtlasHash();};});
 trackControls.innerHTML=[{id:'',label:tx('Вся модель','Full model')}].concat(tracks.map(function(x){return{id:x.id,label:lf(x,'short')||lf(x,'label')};})).map(function(x){return'<button type="button" data-behavior-track="'+esc(x.id)+'" class="'+(behaviorState.track===x.id?'active':'')+'" aria-pressed="'+(behaviorState.track===x.id)+'">'+esc(x.label)+'</button>';}).join('');
 trackControls.querySelectorAll('[data-behavior-track]').forEach(function(button){button.onclick=function(){behaviorState.track=button.dataset.behaviorTrack;behaviorState.mechanism='';renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents());writeAtlasHash();};});
 var displayGroups=activeTrack?alist(activeTrack.stages):groups;
 root.classList.toggle('is-track',!!activeTrack);
 root.innerHTML=displayGroups.map(function(group,index){
  var groupMechanisms=alist(group.mechanism_ids).map(function(id){return mechanisms.find(function(m){return m.id===id;});}).filter(Boolean).filter(function(m){return behaviorState.subdomain==='all'||alist(m.subdomain_ids).includes(behaviorState.subdomain);});
  var rows=groupMechanisms.map(function(m){var count=eligible.filter(function(e){return alist(e.behavioral_mechanism_ids).includes(m.id);}).length;return'<button type="button" class="behavior-mechanism '+(behaviorState.mechanism===m.id?'active':'')+'" data-behavior-mechanism="'+esc(m.id)+'" '+(count?'':'disabled')+'><span>'+esc(lf(m,'label'))+'</span><b>'+count+'</b></button>';}).join('');
  return'<section class="behavior-stage" data-stage="'+(index+1)+'"><div class="behavior-stage-index">0'+(index+1)+'</div><h3>'+esc(lf(group,'label').replace(/^\d+\s*·\s*/,''))+'</h3><p>'+esc(lf(group,'description'))+'</p><div class="behavior-mechanisms">'+(rows||'<span class="behavior-stage-empty">'+tx('Нет механизмов в масштабе','No mechanisms at this scale')+'</span>')+'</div></section>';
 }).join('');
 root.querySelectorAll('[data-behavior-mechanism]').forEach(function(button){button.onclick=function(){behaviorState.mechanism=behaviorState.mechanism===button.dataset.behaviorMechanism?'':button.dataset.behaviorMechanism;renderBehaviorLayer(cyberRenderedEvents,cyberFocusEvents());writeAtlasHash();};});
 var selected=behaviorState.mechanism?mechanisms.find(function(m){return m.id===behaviorState.mechanism;}):null;
 var shown=eligible.filter(function(e){return!selected||alist(e.behavioral_mechanism_ids).includes(selected.id);}).sort(function(a,b){return(a.editorial_priority||3)-(b.editorial_priority||3)||String(b.date).localeCompare(String(a.date));});
 var limit=selected?20:12,total=shown.length;shown=shown.slice(0,limit);
 var title=document.getElementById('behavior-evidence-title');if(title)title.textContent=selected?lf(selected,'label'):tx('Опорные наблюдения','Anchor evidence');
 var count=document.getElementById('behavior-evidence-count');if(count)count.textContent=total?tx('Показано ','Showing ')+shown.length+tx(' из ',' of ')+total:tx('Нет записей в текущей выборке','No records in the current selection');
 list.innerHTML=shown.length?shown.map(behaviorEvidenceCard).join(''):'<div class="atlas-notice">'+tx('Для этого сочетания фильтров нет размеченных наблюдений.','No classified observations match this combination of filters.')+'</div>';
 bindAtlasCards(list);
 var trackNote=document.getElementById('behavior-track-note');if(trackNote)trackNote.textContent=activeTrack?lf(activeTrack,'description'):tx('Базовый вид связывает пять зон контроля; специализированная дорожка перестраивает карту по одному исследовательскому вопросу.','The base view links five control zones; a specialised track reorganises the map around one research question.');
 var claim=byClaim[CYBER_FRAMEWORK.behavior_claim_id],claimRoot=document.getElementById('behavior-claim');
 if(claimRoot&&claim){claimRoot.dataset.kind='claim';claimRoot.dataset.id=claim.id;claimRoot.innerHTML='<div><span class="behavior-claim-label">'+tx('Калиброванный тезис','Calibrated claim')+'</span><h3>'+esc(lf(claim,'title'))+'</h3><p>'+esc(lf(claim,'claim'))+'</p></div><span class="behavior-claim-status">'+esc(atlasStatusLabel(claim.status))+'</span>';bindAtlasCards(claimRoot);}
 var summary=document.getElementById('behavior-selection-summary');if(summary)summary.textContent=eligible.length+'/'+allEligible.length+' '+tx('размеченных записей в текущей кибервыборке','classified records in the current cyber selection');
}
function renderCyber(){
 var all=cyberFocusEvents(),core=cyberCoreIds(all);
 var events=all.filter(function(e){
  if(cyberState.mode==='core'&&!core.has(e.id))return false;
  if(cyberState.role&&!alist(e.cyber_role_ids).includes(cyberState.role))return false;
  if(cyberState.jurisdiction&&!alist(e.jurisdictions).includes(cyberState.jurisdiction))return false;
  if(cyberState.domain&&!alist(e.cyber_domain_ids).includes(cyberState.domain))return false;
  if(cyberState.force&&e.normative_force!==cyberState.force)return false;
  if(cyberState.stage&&e.implementation_stage!==cyberState.stage)return false;
  if(cyberState.authority&&e.delegated_authority!==cyberState.authority)return false;
  if(cyberState.principalOnly&&!['observed','evaluated'].includes(e.delegated_authority))return false;
  return true;
 });
 cyberRenderedEvents=events;syncCyberControls();
 var periods=[{id:'y2025',label:'2025'},{id:'h1',label:tx('2026 · январь–июнь','2026 · January–June')},{id:'h2',label:tx('2026 · июль–6 сентября / будущие сроки','2026 · July–6 September / future deadlines')}];
 var html='<div class="cyber-period-row"><div class="cyber-corner">'+tx('Основной домен','Primary domain')+'</div>'+periods.map(function(p){return'<div class="cyber-period">'+esc(p.label)+'<small>'+events.filter(function(e){return cyberPeriod(e)===p.id;}).length+' '+tx('записей','records')+'</small></div>';}).join('')+'</div>';
 cyberDomains().forEach(function(d){
  if(events.length && !events.some(function(e){return e.primary_domain_id===d.id;}))return;
  var ref=d.control_reference_url?'<a class="domain-reference" href="'+esc(d.control_reference_url)+'" target="_blank" rel="noopener">'+esc(d.control_reference||'ASAMM')+' · '+tx('независимый draft','independent draft')+'</a>':'';
  html+='<div class="cyber-domain-row"><div class="cyber-domain-label"><b>'+esc(lf(d,'label'))+'</b><details><summary>'+tx('Границы домена','Domain scope')+'</summary><p>'+esc(lf(d,'description'))+'</p>'+ref+'</details></div>';
  periods.forEach(function(p){var cell=events.filter(function(e){return e.primary_domain_id===d.id&&cyberPeriod(e)===p.id;});html+='<div class="cyber-cell" data-period-label="'+esc(p.label)+'"><div class="cyber-event-grid">'+(cell.length?cell.map(cyberEventCard).join(''):'<div class="cyber-empty">'+tx('Нет записей в выборке','No records in selection')+'</div>')+'</div></div>';});html+='</div>';
 });
 if(!events.length)html='<div class="atlas-notice">'+tx('Нет совпадений. Сбросьте часть фильтров или переключитесь на все факты.','No matches. Reset filters or switch to all facts.')+'</div>';
 var grid=document.getElementById('cyber-grid');grid.innerHTML=html;
 var edges=cyberDirectEdges(events);
 document.getElementById('cyber-kpis').innerHTML=[[events.length+'/'+all.length,tx('записей видно','records shown')],[edges.length,tx('явных связей между событиями','explicit event links')]].map(function(x){return'<div class="cyber-kpi"><b>'+esc(x[0])+'</b><span>'+esc(x[1])+'</span></div>';}).join('');
 bindAtlasCards(grid);bindCyberHover(grid,edges);renderBehaviorLayer(events,all);renderResilienceLayer(events,all);renderCyberThreads(events);renderCyberEdgeList(events);requestAnimationFrame(drawCyberLinks);writeAtlasHash();
}
function renderAtlasStats(){
 document.getElementById('stats').innerHTML=[[EV.length,tx('фактов','facts')],[CLAIMS.length,tx('тезисов','claims')],[ARCS.length,tx('сюжетов','story arcs')],[SOURCES.length,tx('URL источников','source URLs')]].map(function(x){return'<div class="stat"><b>'+esc(x[0])+'</b><span>'+esc(x[1])+'</span></div>';}).join('');
 var s=D.summary.claim_status_counts||{};
 var n=document.getElementById('claim-status-summary');if(n)n.textContent=tx('Статусы '+CLAIMS.length+' тезиса: '+(s.verified||0)+' подтверждены · '+(s.partially_verified||0)+' частично · '+(s.disputed||0)+' спорны. Это не показатель точности всех событий.', 'Status of the '+CLAIMS.length+' claims only: '+(s.verified||0)+' verified · '+(s.partially_verified||0)+' partial · '+(s.disputed||0)+' disputed. Not an accuracy score for all events.');
 var rail=document.getElementById('correction-rail');if(rail)rail.innerHTML=alist((D.presentation||{}).corrections).map(function(x){return'<p class="small">'+esc(x)+'</p>';}).join('');
 var r=document.getElementById('release-notes');if(r)r.innerHTML='<div class="release-heading">v'+esc(D.meta.version)+' · '+tx('Что изменилось','What changed')+'</div><div class="release-grid">'+alist((D.presentation||{}).release_notes).map(function(x){return'<div><b>'+esc(x.title)+'</b><p>'+esc(x.text)+'</p></div>';}).join('')+'</div>';
}
function renderDashboard(){
 document.getElementById('core-thesis').textContent=lf(byThesis.THESIS_CORE,'summary');
 document.getElementById('thesis-grid').innerHTML=THESIS.map(function(n){return'<article class="thesis-node" data-kind="thesis" data-id="'+esc(n.id)+'"><h3>'+esc(lf(n,'label'))+'</h3><p>'+esc(lf(n,'summary'))+'</p></article>';}).join('');
 renderAtlasStats();renderCapitalMix();
}
function renderOverview(){
 document.getElementById('core-thesis').textContent=lf(byThesis.THESIS_CORE,'summary');
 document.getElementById('thesis-grid').innerHTML=THESIS.map(function(n){return'<article class="card" data-kind="thesis" data-id="'+esc(n.id)+'"><h3>'+esc(lf(n,'label'))+'</h3><p class="small">'+esc(lf(n,'summary'))+'</p></article>';}).join('');
 renderAtlasStats();renderStory('overview-svg');bindAtlasCards(document.getElementById('thesis-grid'));
}
function metadataBlock(e){
 var html='';
 if(e.primary_domain_id){
  html+='<section class="block governance-card"><h3>'+tx('Тип, сила и область применения','Type, force and scope')+'</h3><dl class="governance-grid">';
  [[tx('Документ / событие','Document / event'),vocab('artifact_kinds',e.artifact_kind)],[tx('Нормативная сила','Normative force'),vocab('normative_forces',e.normative_force)],[tx('Стадия','Stage'),vocab('implementation_stages',e.implementation_stage)],[tx('Основной домен','Primary domain'),lf(cyberDomainMeta(e.primary_domain_id),'label')]].forEach(function(x){html+='<div><dt>'+esc(x[0])+'</dt><dd>'+esc(x[1])+'</dd></div>';});
  html+='</dl><p><b>'+tx('Сфера: ','Scope: ')+'</b>'+esc(lf(e,'scope'))+'</p><p><b>'+tx('Роли ИИ: ','AI roles: ')+'</b>'+esc(alist(e.cyber_role_ids).map(function(id){return lf(cyberRoleMeta(id),'label');}).join(' · ')||tx('Не установлены для контекстной записи','Not established for this context record'))+'</p><p>'+esc(lf(e,'role_basis'))+'</p><p><b>'+tx('Делегирование: ','Delegation: ')+'</b>'+esc(vocab('delegated_authority_states',e.delegated_authority))+'</p>';
  if(e.intended_normative_force)html+='<p class="atlas-notice">'+tx('Предлагаемая сила (не действующая): ','Intended force (not current): ')+esc(vocab('normative_forces',e.intended_normative_force))+'</p>';
  html+='<details><summary>'+tx('Редакционная разметка и отбор','Editorial classification and selection')+'</summary><p>'+esc(lf(e,'editorial_rationale'))+'</p><p class="small">'+tx('Разметка пересмотрена по сохранённым свидетельствам; это не новый независимый фактчек всех первоисточников.','Classification reviewed against stored evidence; this is not a fresh independent fact-check of every source.')+'</p></details></section>';
 }
 if(alist(e.behavioral_mechanism_ids).length){
  var valueLabels=function(group,values){return alist(values).map(function(id){var m=behaviorMeta(group,id);if(m)return lf(m,'label');if(group==='evidence_contexts')return atlasEvidenceContextLabel(id);return String(id||'').replace(/_/g,' ');}).filter(Boolean).join(' · ');};
  var rows=[
   [tx('Масштаб','Scale'),valueLabels('subdomains',e.cyber_subdomain_ids)],
   [tx('Механизмы','Mechanisms'),valueLabels('behavioral_mechanisms',e.behavioral_mechanism_ids)],
   [tx('Что установлено','What is established'),valueLabels('behavioral_statuses',e.behavioral_status)],
   [tx('Контекст','Evidence context'),valueLabels('evidence_contexts',e.evidence_context)],
   [tx('Популяция агентов','Agent population'),valueLabels('agent_population_scopes',e.agent_population_scope)],
   [tx('Общая записываемая среда','Shared writable state'),valueLabels('shared_writable_states',e.shared_writable_state)],
   [tx('Цель контроля','Oversight target'),valueLabels('oversight_targets',e.oversight_target)],
   [tx('Основание вывода о мотивации','Basis for motive inference'),valueLabels('motivation_bases',e.motivation_basis)],
   [tx('Исследовательская дорожка','Research track'),valueLabels('behavior_tracks',e.behavior_track_ids)],
   [tx('Происхождение поведения','Behaviour origin'),valueLabels('behavior_origins',e.behavior_origin)],
   [tx('Перед кем скрывается','Concealment target'),valueLabels('concealment_targets',e.concealment_targets)],
   [tx('Носитель преемственности','Persistence medium'),valueLabels('persistence_media',e.persistence_media)],
   [tx('Источник цели','Objective source'),valueLabels('goal_sources',e.goal_source)]
  ].filter(function(row){return row[1];});
  html+='<section class="block behavior-metadata"><h3>'+tx('Поведение, контроль и автономия','Behaviour, control and autonomy')+'</h3><dl class="behavior-metadata-grid">'+rows.map(function(row){return'<div><dt>'+esc(row[0])+'</dt><dd>'+esc(row[1])+'</dd></div>';}).join('')+'</dl>'+(e.evidence_method?'<p class="small"><b>'+tx('Метод: ','Method: ')+'</b>'+esc(String(e.evidence_method).replace(/_/g,' '))+'</p>':'')+'</section>';
 }
 if(e.current_state){var st=e.current_state;var note=lf(st,'date_note')||(e.id==='SIG_2026_KIMI_K3_OPEN_WEIGHT_ANNOUNCEMENT'?tx('Дата первого выпуска весов не установлена. Наблюдение не переносится на июльскую точку.','First weight-release date is not established. This observation does not backdate availability to July.'):tx('Наблюдение не меняет дату исходного события.','The observation does not change the original event date.'));html+='<section class="block state-card"><h3>'+tx('Наблюдение состояния · ','State observed · ')+esc(st.observed_at)+'</h3><p>'+esc(lf(st,'summary'))+'</p><p class="small">'+tx('Исходная запись: ','Original record: ')+esc(e.date)+'. '+esc(note)+'</p></section>';}
 html+=resilienceMetadata(e);
 if(alist(e.mechanism_effects).length)html+='<section class="block effect-card"><h3>'+tx('Эффект на конкретный механизм','Effect on a specific mechanism')+'</h3>'+e.mechanism_effects.map(function(x){return'<p><b>'+esc(relationLabel(x.direction))+' · '+esc(x.actor)+'</b></p><p>'+esc(lf(x,'interpretation'))+'</p>';}).join('')+'<p class="small">'+tx('Редакционная интерпретация, не измеренный причинный эффект.','Editorial interpretation, not a measured causal effect.')+'</p></section>';
 if(e.actor_classification_status==='review_required')html+='<section class="block atlas-notice"><h3>'+tx('Актор требует уточнения','Actor needs review')+'</h3><p>'+esc(alist(e.actor_unclassified).join(' · '))+'</p><p>'+tx('Исходная метка сохранена и доступна поиском и фильтром «Не разобраны». Организация не угадана автоматически.','The raw label is searchable and included in the unresolved filter. No organisation was guessed.')+'</p></section>';
 return html;
}
function openDetail(k,id,options){
 if(ATLAS_RU&&k==='check')k='claimCheck';if(!ATLAS_RU&&k==='claimCheck')k='check';
 var maps={event:byEvent,arc:byArc,edge:byEdge,claim:byClaim,claimCheck:byCheck,check:byCheck,thesis:byThesis,counterargument:byCounter,gap:byGap};
 if(maps[k]&&!maps[k][id])return;
 if(!currentDetail)atlasReturnFocus=document.activeElement;
 _legacyOpenDetail(k,id,options);
 if(!currentDetail)return;
 var root=document.getElementById('detail'),h=root.querySelector('h2');if(h){h.id='detail-title';if(k==='event')h.insertAdjacentHTML('afterend',metadataBlock(byEvent[id]));}
 var modal=document.getElementById('modal');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';
 var drawer=modal.querySelector('.drawer');drawer.setAttribute('role','dialog');drawer.setAttribute('aria-modal','true');drawer.setAttribute('aria-labelledby','detail-title');drawer.scrollTop=0;
 writeAtlasHash();
 var copy=document.getElementById('copy-record-link');if(copy)copy.disabled=false;
 var focus=modal.querySelector('button[data-close]');if(focus)focus.focus({preventScroll:true});
}
function closeDetail(){var had=!!currentDetail;_legacyCloseDetail();document.body.style.overflow='';document.getElementById('modal').setAttribute('aria-hidden','true');writeAtlasHash();if(had&&atlasReturnFocus&&atlasReturnFocus.isConnected)atlasReturnFocus.focus({preventScroll:true});}
function switchTab(id){if(!document.getElementById('view-'+id))return;_legacySwitchTab(id);writeAtlasHash();}
function filterMap(){return {'filter-jurisdiction':'jurisdiction','filter-actor':'actor','filter-family':'family','filter-lane':'lane','filter-layer':'layer','filter-year':'year','filter-arc':'arc','filter-relation':'relation','filter-status':'status','filter-confidence':'confidence','filter-region':'region','filter-location':'location','filter-institution':'institution','filter-geo-context':'geoContext','filter-geo-scope':'geoScope','filter-actor-type':'actorType','filter-actor-jurisdiction':'actorJurisdiction','filter-source':'source'};}
function activeFacts(){return ATLAS_RU?catalogState:factState;}
function writeAtlasHash(){
 if(atlasRestoring||!atlasReady)return;
 var p=new URLSearchParams(),view=document.querySelector('.view.active');p.set('tab',view?view.id.slice(5):tx('story','overview'));
 [['c.',cyberState],['b.',behaviorState],['r.',resilienceState],['f.',activeFacts()],['g.',graphState]].forEach(function(pair){Object.keys(pair[1]).sort().forEach(function(k){var v=pair[1][k];if(v!==''&&v!=null)p.set(pair[0]+k,String(v));});});
 if(currentDetail){p.set('kind',currentDetail.kind||currentDetail.k);p.set('id',currentDetail.id);if((currentDetail.kind||currentDetail.k)==='event')p.set('event',currentDetail.id);}
 var hash='#'+p.toString();if(location.hash!==hash){try{history.replaceState(null,'',hash);}catch(e){/* embedding sandboxes may prohibit history */}}
 document.querySelectorAll('a[data-language-link]').forEach(function(a){a.setAttribute('href',(a.getAttribute('href')||'').split('#')[0]+hash);});
}
function restoreAtlasHash(){
 atlasRestoring=true;
 var raw=location.hash.slice(1),p=new URLSearchParams(raw.includes('=')?raw:''),tab=p.get('tab')||(raw&&!raw.includes('=')?raw:'');
 [['c.',cyberState],['b.',behaviorState],['r.',resilienceState],['f.',activeFacts()],['g.',graphState]].forEach(function(pair){Object.keys(pair[1]).forEach(function(k){if(!p.has(pair[0]+k))return;var v=p.get(pair[0]+k);pair[1][k]=typeof pair[1][k]==='boolean'?v==='true':v;});});
 var map=filterMap(),f=activeFacts();Object.keys(map).forEach(function(id){var n=document.getElementById(id);if(n)n.value=f[map[id]]||'';});
 var search=document.getElementById('search');if(search)search.value=f.q||'';
 ['family','arc','relation'].forEach(function(k){var n=document.getElementById(k+'-select');if(n)n.value=graphState[k]||'';});
 syncCyberControls();if(ATLAS_RU){renderCatalog();renderStoryMap();}else{renderFacts();renderStory('story-svg');renderStory('overview-svg');}
 renderCyber();
 if(tab==='facts'&&ATLAS_RU)tab='catalog';if(tab==='catalog'&&!ATLAS_RU)tab='facts';if(tab==='overview'&&ATLAS_RU)tab='story';
 if(tab)switchTab(tab);
 var id=p.get('event')||p.get('id'),kind=p.get('event')?'event':p.get('kind');
 if(id&&kind)openDetail(kind,id,{replace:true});else if(currentDetail)closeDetail();
 atlasRestoring=false;writeAtlasHash();
}
function initAtlasReview(){
 var actor=document.getElementById('filter-actor');
 if(actor&&!actor.querySelector('[value="__unresolved__"]'))actor.insertAdjacentHTML('beforeend','<option value="__unresolved__">'+tx('Не разобраны · ','Unresolved · ')+(D.classificationReviewQueue||[]).length+'</option>');
 var notice=document.getElementById('actor-review-notice');if(notice)notice.innerHTML=tx('Неразобранные исходные обозначения: ','Unresolved raw labels: ')+(D.classificationReviewQueue||[]).length+'. '+tx('Они сохранены в поиске и отдельном фильтре, а не исключены из набора.','They remain searchable and have a dedicated filter rather than disappearing.');
 var state=document.getElementById('state-observations');if(state)state.innerHTML=EV.filter(function(e){return e.current_state;}).map(function(e){return'<article class="block state-card" data-kind="event" data-id="'+esc(e.id)+'"><h3>'+esc(e.current_state.observed_at)+' · '+esc(lf(e.current_state,'title'))+'</h3><p>'+esc(lf(e.current_state,'summary'))+'</p><p class="small">'+tx('Отдельное наблюдение состояния. Исходный анонс: ','Separate state observation. Original announcement: ')+esc(e.date)+'</p></article>';}).join('');bindAtlasCards(state);
 var modal=document.getElementById('modal'),tools=modal.querySelector('.drawer-tools');var btn=document.createElement('button');btn.type='button';btn.id='copy-record-link';btn.className=tx('ghost-btn','btn');btn.textContent=tx('Ссылка на запись','Copy record link');btn.onclick=async function(){var u=location.href;try{await navigator.clipboard.writeText(u);btn.textContent=tx('Скопировано','Copied');}catch(e){var box=document.getElementById('permalink-fallback');if(!box){box=document.createElement('input');box.id='permalink-fallback';box.readOnly=true;box.setAttribute('aria-label',tx('Постоянная ссылка','Permalink'));tools.after(box);}box.value=u;box.focus();box.select();}setTimeout(function(){btn.textContent=tx('Ссылка на запись','Copy record link');},1500);};tools.insertBefore(btn,tools.lastElementChild);
 document.querySelectorAll('a[href$="ai-power-atlas.html"],a[href$="ai-power-atlas-ru.html"]').forEach(function(a){a.dataset.languageLink='1';});
 document.addEventListener('change',function(){setTimeout(writeAtlasHash,0);});document.addEventListener('input',function(e){if(e.target.id==='search')setTimeout(writeAtlasHash,0);});document.addEventListener('click',function(e){if(e.target.closest('button'))setTimeout(writeAtlasHash,0);});
 document.addEventListener('keydown',function(e){if(e.key!=='Tab'||!currentDetail)return;var nodes=Array.from(modal.querySelectorAll('button:not([disabled]),a[href],input,[tabindex="0"]')).filter(function(n){return n.getClientRects().length;});if(!nodes.length)return;var first=nodes[0],last=nodes[nodes.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
 window.addEventListener('hashchange',restoreAtlasHash);atlasReady=true;restoreAtlasHash();
}


function resMeta(group,id){return alist(CYBER_FRAMEWORK[group]).find(function(x){return x.id===id;});}
function renderResilienceLayer(events,all){
 var box=document.getElementById('resilience-section');if(!box)return;
 var tracks=alist(CYBER_FRAMEWORK.resilience_tracks);
 if(!tracks.some(function(t){return t.id===resilienceState.track;}))resilienceState.track=tracks.length?tracks[0].id:'';
 var selected=tracks.find(function(t){return t.id===resilienceState.track;});
 var tagged=events.filter(function(e){return alist(e.resilience_track_ids).length;});
 var shown=tagged.filter(function(e){return alist(e.resilience_track_ids).includes(resilienceState.track);}).sort(function(a,b){return (a.editorial_priority||2)-(b.editorial_priority||2)||String(b.date).localeCompare(String(a.date));});
 box.open=!!resilienceState.open;
 var count=document.getElementById('resilience-count');count.textContent=tagged.length+' / '+all.filter(function(e){return alist(e.resilience_track_ids).length;}).length;
 document.getElementById('resilience-note').textContent=lf(CYBER_FRAMEWORK,'resilience_note');
 document.getElementById('resilience-tracks').innerHTML=tracks.map(function(t){var n=tagged.filter(function(e){return alist(e.resilience_track_ids).includes(t.id);}).length;return '<button type="button" class="resilience-track'+(resilienceState.track===t.id?' active':'')+'" data-resilience-track="'+esc(t.id)+'" aria-pressed="'+String(resilienceState.track===t.id)+'"><b>'+esc(lf(t,'label'))+'</b><span>'+n+' '+tx('записей','records')+'</span></button>';}).join('');
 document.getElementById('resilience-tracks').querySelectorAll('[data-resilience-track]').forEach(function(n){n.onclick=function(){resilienceState.track=n.dataset.resilienceTrack;resilienceState.open=true;renderResilienceLayer(cyberRenderedEvents,cyberFocusEvents());writeAtlasHash();};});
 document.getElementById('resilience-description').textContent=selected?lf(selected,'description'):'';
 var claim=CYBER_FRAMEWORK.resilience_claim_id;
 document.getElementById('resilience-claim').innerHTML='<button type="button" class="resilience-claim" data-kind="claim" data-id="'+esc(claim)+'">'+tx('Тезис: поток реальных находок и ёмкость сопровождения','Claim: valid-finding throughput and maintenance capacity')+'</button>';
 var cards=document.getElementById('resilience-events');
 cards.innerHTML=shown.length?shown.map(function(e){var m=resMeta('defense_evidence_kinds',e.defense_evidence_kind);return '<article class="resilience-evidence-card" data-kind="event" data-id="'+esc(e.id)+'"><div class="resilience-card-meta"><time>'+esc(e.date)+'</time><span>'+esc(m?lf(m,'label'):tx('Ранее проверенная запись','Previously reviewed record'))+'</span></div><h4>'+esc(e.title)+'</h4><p>'+esc(lf(e,'summary'))+'</p><small>'+esc(vocab('implementation_stages',e.implementation_stage))+(e.current_state?' · '+tx('обновлено наблюдением ','state observed ')+esc(e.current_state.observed_at):'')+(e.editorial_priority===3?' · '+tx('предыстория','historical context'):'')+(e.date_basis==='observation_date_publication_unknown'?' · '+tx('дата наблюдения','observation date'):'')+'</small></article>';}).join(''):'<p class="atlas-notice">'+tx('В этой дорожке нет совпадений с верхними фильтрами.','This track has no matches under the current filters.')+'</p>';
 box.ontoggle=function(){if(resilienceState.open!==box.open){resilienceState.open=box.open;writeAtlasHash();}};
 bindAtlasCards(cards);bindAtlasCards(document.getElementById('resilience-claim'));
}
function resilienceMetadata(e){
 if(!alist(e.resilience_track_ids).length)return '';
 var tracks=alist(e.resilience_track_ids).map(function(id){var m=resMeta('resilience_tracks',id);return m?lf(m,'label'):id;});
 var m=resMeta('defense_evidence_kinds',e.defense_evidence_kind);
 var h='<section class="block resilience-metadata"><h3>'+tx('Защитный цикл и устойчивость','Defensive lifecycle and resilience')+'</h3><p>'+esc(tracks.join(' · '))+'</p>';
 if(m)h+='<p><b>'+tx('Тип свидетельства: ','Evidence kind: ')+'</b>'+esc(lf(m,'label'))+'</p>';
 if(alist(e.defense_stage_ids).length){h+='<p><b>'+tx('Предмет свидетельства: ','Evidence concerns: ')+'</b>'+esc(e.defense_stage_ids.map(function(id){var st=resMeta('defense_stages',id);return st?lf(st,'label'):id;}).join(' · '))+'</p><p class="small">'+tx('Теги этапов не означают, что все результаты уже достигнуты; читайте стадию, сферу и ограничения.','Stage tags do not mean every outcome has been achieved; read implementation stage, scope and limitations.')+'</p>';}
 if(e.date_basis==='observation_date_publication_unknown')h+='<p class="atlas-notice">'+tx('6 сентября — дата наблюдения страницы. Дата спринта и первой публикации не установлена.','6 September is the page-observation date. The sprint and first-publication dates are not established.')+'</p>';
 if(e.pipeline_semantics&&e.pipeline_semantics.sequential_funnel===false)h+='<p class="atlas-notice">'+tx('Не последовательная воронка: проверенная ветка и прямая передача мейнтейнерам различаются. 91,4% — только проверенный поднабор; ответы мейнтейнеров не равны подтверждениям, upstream не равен установке.','Not a sequential funnel: the reviewed route differs from direct maintainer disclosure. 91.4% applies only to the reviewed subset; replies are not validation, and upstream fixes are not deployment.')+'</p>';
 if(alist(e.pipeline_metrics).length)h+='<div class="resilience-metrics">'+e.pipeline_metrics.map(function(v){return '<div class="resilience-metric"><strong>'+esc(v.value)+'</strong><b>'+esc(lf(v,'label'))+'</b><small>'+esc(v.as_of)+' · '+esc(v.unit)+'</small><p>'+esc(lf(v,'population'))+'</p><a href="'+esc(v.source_url)+'" target="_blank" rel="noopener">'+tx('Источник','Source')+'</a></div>';}).join('')+'</div>';
 h+='<p class="small">'+tx('Проверенная находка ≠ принятый патч ≠ выпуск ≠ установка ≠ восстановленная услуга.','Validated finding ≠ accepted patch ≠ release ≠ deployment ≠ restored service.')+'</p></section>';
 return h;
}
