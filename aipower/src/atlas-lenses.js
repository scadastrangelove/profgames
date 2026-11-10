/* Cross-cutting views reuse canonical evidence and explicit arc memberships. */
var lensState={active:'cyber',view:'knowledge',period:'recent',geo:'',context:'',track:'',bucket:'',q:'',page:'1'};
var lensPageSize=18;
function lensViews(){return alist((D.crosscuttingViews||{}).views);}
function lensDefinition(){return lensViews().find(function(v){return v.id===lensState.view;})||lensViews()[0];}
function lensTrackMatches(e,t){
 var ids=alist(e.arcIds);
 return alist(t.arc_ids).some(function(id){return ids.includes(id);})&&alist(t.required_arc_ids).every(function(id){return ids.includes(id);})&&(!alist(t.outcome_stages).length||t.outcome_stages.includes(e.research_outcome_stage));
}
function lensTracks(e,v){return v.tracks.filter(function(t){return lensTrackMatches(e,t);});}
function lensAllEvents(v){return EV.filter(function(e){return lensTracks(e,v).length;});}
function lensQuarter(e){var m=/^(\d{4})-(\d{2})/.exec(e.date||'');return m?m[1]+'-Q'+Math.ceil(Number(m[2])/3):'';}
function lensBuckets(v){
 var years=Array.from(new Set(lensAllEvents(v).map(function(e){return String(e.date||'').slice(0,4);}))).filter(function(y){return /^\d{4}$/.test(y);}).sort();
 var latest=String(D.meta.updated_at).slice(0,4),previous=String(Number(latest)-1),out=[];
 if(lensState.period==='all')years.filter(function(y){return y<previous;}).forEach(function(y){out.push(y);});
 if(lensState.period!=='latest'&&years.includes(previous))out.push(previous);
 [1,2,3,4].forEach(function(q){out.push(latest+'-Q'+q);});
 if(lensState.period==='all')years.filter(function(y){return y>latest;}).forEach(function(y){out.push(y);});
 return out;
}
function lensBucketContains(e,b){return b.includes('-Q')?lensQuarter(e)===b:String(e.date||'').startsWith(b);}
function lensGeos(e){return Array.from(new Set(alist(e.jurisdictions).concat(alist(e.regions),alist(e.geographic_scopes).filter(function(x){return x==='Global';}))));}
function lensContextLabel(id){
 var labels={governance_document:['Документ управления','Governance document'],ecosystem_measurement:['Исследование экосистемы','Ecosystem measurement'],internal_deployment:['Внутреннее внедрение','Internal deployment'],production:['Рабочая эксплуатация','Production'],training:['Обучение модели','Model training'],benchmark:['Испытание на бенчмарке','Benchmark'],evaluation:['Оценка в испытании','Evaluation'],controlled_evaluation:['Контролируемое испытание','Controlled evaluation'],'nine-country sample':['Выборка из девяти стран','Nine-country sample']};
 var value=labels[id];return value?tx(value[0],value[1]):atlasEvidenceContextLabel(id);
}
function lensFiltered(v,selection){
 var buckets=lensBuckets(v),query=lensState.q.trim().toLocaleLowerCase();
 return lensAllEvents(v).filter(function(e){
  return buckets.some(function(b){return lensBucketContains(e,b);})&&(!lensState.geo||lensGeos(e).includes(lensState.geo))&&
   (!lensState.context||alist(e.evidence_context).includes(lensState.context))&&
   (!query||[e.title,lf(e,'summary'),alist(e.actor_entities).join(' ')].join(' ').toLocaleLowerCase().includes(query))&&
   (!selection||!lensState.track||lensTracks(e,v).some(function(t){return t.id===lensState.track;}))&&
   (!selection||!lensState.bucket||lensBucketContains(e,lensState.bucket));
 }).sort(function(a,b){return String(b.date).localeCompare(String(a.date))||a.id.localeCompare(b.id);});
}
function lensExplicitEdges(events){
 var ids=new Set(events.map(function(e){return e.id;}));
 return EDGES.filter(function(edge){return !edge.is_auto&&ids.has(edge.source)&&ids.has(edge.target)&&edge.relation!=='part_of_arc';});
}
function lensOptions(values,label){return '<option value="">'+esc(label)+'</option>'+values.map(function(x){return '<option value="'+esc(x[0])+'">'+esc(x[1])+'</option>';}).join('');}
function initLenses(){
 if(!lensViews().length)return;
 var nav=document.querySelector('#nav [data-tab="cyber"]');
 nav.textContent=tx('Сквозные срезы','Cross-cutting views');
 nav.onclick=function(){var select=document.getElementById('lens-switch');switchTab(select.value==='cyber'?'cyber':'lenses');};
 var picker=document.createElement('label');picker.className='lens-picker';picker.innerHTML='<span>'+tx('Срез','View')+'</span><select id="lens-switch"><option value="cyber">'+tx('Киберустойчивость ИИ','AI Cyber Resilience')+'</option>'+lensViews().map(function(v){return '<option value="'+esc(v.id)+'">'+esc(lf(v,'label'))+'</option>';}).join('')+'</select>';
 document.getElementById('nav').after(picker);
 picker.querySelector('select').onchange=function(){
  if(this.value==='cyber'){switchTab('cyber');return;}
  Object.assign(lensState,{view:this.value,track:'',bucket:'',page:'1'});renderLens();switchTab('lenses');
 };
 var section=document.createElement('section');section.id='view-lenses';section.className='view lens-view';
 section.innerHTML='<header class="lens-heading"><h2 id="lens-title"></h2><p id="lens-question"></p></header>'+
 '<div class="lens-filters"><label>'+tx('Период','Period')+'<select id="lens-period"><option value="recent">'+tx('Последние два года','Latest two years')+'</option><option value="latest">'+tx('Последний год','Latest year')+'</option><option value="all">'+tx('Вся хронология','Full chronology')+'</option></select></label>'+
 '<label>'+tx('География события','Event geography')+'<select id="lens-geo"></select></label><label>'+tx('Свидетельство','Evidence')+'<select id="lens-context"></select></label>'+
 '<label>'+tx('Поиск','Search')+'<input id="lens-query" type="search"></label><button id="lens-reset" type="button">'+tx('Сбросить','Reset')+'</button></div>'+
 '<div id="lens-totals" class="lens-totals" aria-live="polite"></div><div id="lens-map" class="lens-map"></div>'+
 '<div class="lens-results-heading"><h3 id="lens-selection"></h3><button id="lens-clear" type="button">'+tx('Все темы и даты','All themes and dates')+'</button></div>'+
 '<div id="lens-records" class="lens-records"></div><div id="lens-pagination" class="lens-pagination"></div>'+
 '<details class="lens-relations"><summary id="lens-relations-title"></summary><div id="lens-relations"></div></details>';
 var main=document.querySelector('main'),footer=main.querySelector('#footer');if(footer)main.insertBefore(section,footer);else main.append(section);
 ['period','geo','context'].forEach(function(k){document.getElementById('lens-'+k).onchange=function(){lensState[k]=this.value;if(k==='period')lensState.bucket='';lensState.page='1';renderLens();writeAtlasHash();};});
 document.getElementById('lens-query').oninput=function(){lensState.q=this.value;lensState.page='1';renderLens();writeAtlasHash('replace');};
 document.getElementById('lens-reset').onclick=function(){Object.assign(lensState,{period:'recent',geo:'',context:'',track:'',bucket:'',q:'',page:'1'});renderLens();writeAtlasHash();};
 document.getElementById('lens-clear').onclick=function(){lensState.track='';lensState.bucket='';lensState.page='1';renderLens();writeAtlasHash();};
 renderLens();
}
function syncLensNavigation(tab){
 var select=document.getElementById('lens-switch');if(!select)return;
 if(tab==='cyber'||tab==='lenses')lensState.active=tab;
 if(!['cyber','lenses'].includes(lensState.active))lensState.active='cyber';
 if(!lensViews().some(function(v){return v.id===lensState.view;}))lensState.view=lensViews()[0].id;
 select.value=lensState.active==='lenses'?lensState.view:'cyber';
 if(tab==='lenses'){document.querySelector('#nav [data-tab="cyber"]').classList.add('active');renderLens();}
}
function renderLensMap(v,events,buckets){
 var map=document.getElementById('lens-map');
 map.innerHTML='<table class="lens-matrix"><caption>'+tx('События по темам и времени','Events by theme and date')+'</caption><thead><tr><th scope="col">'+tx('Тема','Theme')+'</th>'+buckets.map(function(b){return '<th scope="col">'+esc(b.replace('-Q',tx(' · кв. ',' · Q')))+'</th>';}).join('')+'</tr></thead><tbody>'+v.tracks.map(function(t){return '<tr><th scope="row"><button data-lens-track="'+esc(t.id)+'" style="--track-color:'+t.color+'" aria-pressed="'+(lensState.track===t.id&&!lensState.bucket)+'">'+esc(lf(t,'label'))+'</button></th>'+buckets.map(function(b){var n=events.filter(function(e){return lensTrackMatches(e,t)&&lensBucketContains(e,b);}).length,selected=lensState.track===t.id&&lensState.bucket===b;return '<td><button data-lens-track="'+esc(t.id)+'" data-lens-bucket="'+b+'" aria-label="'+esc(lf(t,'label')+' · '+b+' · '+n)+'" aria-pressed="'+selected+'" '+(!n?'disabled':'')+' style="--track-color:'+t.color+';--fill:'+Math.min(88,12+n*6)+'%"><b>'+n+'</b></button></td>';}).join('')+'</tr>';}).join('')+'</tbody></table>';
 map.querySelectorAll('[data-lens-track]').forEach(function(button){button.onclick=function(){var track=this.dataset.lensTrack,bucket=this.dataset.lensBucket||'';var same=lensState.track===track&&lensState.bucket===bucket;lensState.track=same?'':track;lensState.bucket=same?'':bucket;lensState.page='1';renderLens();writeAtlasHash();};});
 map.querySelectorAll('[data-lens-bucket]').forEach(function(button){button.dataset.periodLabel=button.dataset.lensBucket.replace('-Q',tx(' · К',' · Q'));});
}
function lensOutcomeLabel(e){
 var labels={
  worker_productivity:['Производительность работников','Worker productivity'],public_research_resource:['Открытый исследовательский ресурс','Public research resource'],research_tool_access:['Доступ к инструменту','Research tool access'],mathematical_benchmark:['Математическое испытание','Mathematical benchmark'],reported_operational_result:['Заявленный операционный результат','Reported operational result'],physical_validation:['Физическая проверка','Physical validation'],research_workflow:['Исследовательский процесс','Research workflow'],institutional_practice:['Институциональная практика','Institutional practice'],clinical_screening_endpoint:['Клинический скрининг','Clinical screening endpoint'],patient_vascular_outcome:['Сосудистые исходы пациентов','Patient vascular outcomes'],early_clinical_translation:['Ранняя клиническая проверка','Early clinical translation'],care_access:['Доступ к помощи','Care access'],patient_outcome_null:['Нулевой эффект на исходы','Null patient-outcome effect'],patient_experience:['Опыт пациентов','Patient experience'],clinical_workflow:['Клинический процесс','Clinical workflow'],patient_reported_symptoms:['Симптомы со слов пациентов','Patient-reported symptoms'],employment_hiring_distribution:['Занятость и найм','Employment and hiring'],earnings_hours_null:['Нулевой эффект на заработок и часы','Null earnings and hours effect'],team_task_performance:['Результаты командной задачи','Team task performance'],exposure_not_realized_effect:['Оценка подверженности','Estimated exposure'],reported_firm_effects_and_expectations:['Опрос: эффекты и ожидания','Survey: effects and expectations'],statistical_validation:['Статистическая проверка','Statistical validation'],candidate_catalog_not_confirmed_discoveries:['Каталог кандидатов','Candidate catalogue'],expert_reviewed_catalog_with_candidate_classes:['Каталог с экспертной проверкой','Expert-reviewed catalogue'],expert_assistance_evaluation:['Оценка помощи экспертам','Expert-assistance evaluation'],physical_source_text_recovery:['Чтение физического источника','Physical source-text recovery'],probabilistic_historical_dating:['Вероятностная датировка','Probabilistic historical dating'],historical_text_reconstruction:['Реконструкция текста','Text reconstruction'],field_validated_discovery:['Проверка в полевых условиях','Field-validated discovery'],operational_service:['Действующий сервис','Operational service'],research_validation:['Исследовательская проверка','Research validation'],forecast_validation_and_operational_service:['Прогноз и действующий сервис','Forecast validation and service'],reported_large_scale_deployment:['Заявленное масштабное внедрение','Reported large-scale deployment'],physical_lab_validation:['Лабораторный эксперимент','Physical lab validation'],experimental_control:['Экспериментальное управление','Experimental control'],computational_validation:['Вычислительная проверка','Computational validation'],computational_discovery_with_subset_lab_validation:['Поиск и частичная лабораторная проверка','Discovery and subset lab validation'],computational_validation_against_field_inventories:['Сверка с полевыми измерениями','Validation against field inventories'],retrospective_signal_detection:['Ретроспективное обнаружение','Retrospective detection'],measured_learning_outcomes:['Измеренные результаты обучения','Measured learning outcomes'],bibliometric_association:['Библиометрическая связь','Bibliometric association'],engineering_workflow:['Инженерный процесс','Engineering workflow'],reported_workload_equivalent:['Заявленный эквивалент нагрузки','Reported workload equivalent']
 };
 Object.assign(labels,{
  reported_realized_cash_flows_and_debt_stock:['Денежные потоки и долг','Cash flows and debt'],
  tariff_approval_and_reported_effectiveness:['Тариф и условия подключения','Tariff and connection terms'],
  self_reported_firm_performance:['Показатели бизнеса со слов участников','Self-reported business outcomes'],
  job_posting_demand_not_employment:['Спрос на задания','Demand for posted tasks'],
  completed_development_tasks:['Выполненные задачи разработки','Completed development tasks'],
  application_time_and_task_activity:['Время в приложениях и задачи','Application time and tasks'],
  expert_scored_solutions_not_formal_verification:['Экспертная оценка решений','Expert-scored solutions'],
  realized_revenue_not_marketwide_sustainability:['Выручка сервиса','Service revenue'],
  estimated_referral_effect_not_revenue_loss:['Оценка поисковых переходов','Estimated search referrals'],
  historical_answer_and_attribution_quality:['Качество ответов и источников','Answer and sourcing quality'],
  released_artifacts_and_budget_matched_evaluation:['Открытые материалы и испытание','Open artifacts and evaluation'],
  reported_physical_testing_with_disputed_structure_and_novelty:['Испытание; новизна оспаривается','Testing; novelty disputed']
 });
 var value=labels[e.research_outcome_stage];return value?tx(value[0],value[1]):'';
}
function lensCard(e,v){
 var tracks=lensTracks(e,v),stage=lensOutcomeLabel(e),contexts=alist(e.evidence_context).map(lensContextLabel).join(' · ');
 var geo=lensGeos(e).join(' · '),caveat=lf(e,'caveat')||alist(lf(e,'caveats')).join(' ');
 return '<article class="lens-record" style="--track-color:'+tracks[0].color+'"><div class="lens-record-meta"><time>'+esc(e.date)+'</time><span>'+esc(geo||tx('География не указана','Geography unspecified'))+'</span></div>'+
 '<h4><button type="button" data-kind="event" data-id="'+esc(e.id)+'">'+esc(e.title)+'</button></h4><p>'+esc(lf(e,'safe_wording')||lf(e,'summary'))+'</p>'+
 '<div class="lens-evidence">'+esc(stage||contexts||tx('Тип не указан','Type unspecified'))+' · '+esc(atlasStatusLabel(e.status))+'</div>'+
 (caveat?'<details><summary>'+tx('Границы результата','Scope and limitations')+'</summary><p>'+esc(caveat)+'</p></details>':'')+
 '<div class="lens-record-footer"><span>'+esc(tracks.map(function(t){return lf(t,'label');}).join(' · '))+'</span><span>'+alist(e.sources).length+' '+tx('ист.','sources')+'</span></div></article>';
}
function renderLens(){
 var root=document.getElementById('view-lenses'),v=lensDefinition();if(!root||!v)return;
 lensState.view=v.id;
 if(!v.tracks.some(function(t){return t.id===lensState.track;}))lensState.track='';
 if(!['all','recent','latest'].includes(lensState.period))lensState.period='recent';
 var buckets=lensBuckets(v);if(!buckets.includes(lensState.bucket))lensState.bucket='';
 var all=lensViews().flatMap(lensAllEvents),geos=Array.from(new Set(all.flatMap(lensGeos))).sort(),contexts=Array.from(new Set(all.flatMap(function(e){return alist(e.evidence_context);}))).sort();
 if(lensState.geo&&!geos.includes(lensState.geo))lensState.geo='';
 if(lensState.context&&!contexts.includes(lensState.context))lensState.context='';
 document.getElementById('lens-geo').innerHTML=lensOptions(geos.map(function(g){return[g,g];}),tx('Все территории','All territories'));
 document.getElementById('lens-context').innerHTML=lensOptions(contexts.map(function(c){return[c,lensContextLabel(c)];}),tx('Все свидетельства','All evidence'));
 ['period','geo','context'].forEach(function(k){document.getElementById('lens-'+k).value=lensState[k];});
 document.getElementById('lens-query').value=lensState.q;
 document.getElementById('lens-title').textContent=lf(v,'label');document.getElementById('lens-question').textContent=lf(v,'question');
 var events=lensFiltered(v,false),selected=lensFiltered(v,true),sources=new Set(events.flatMap(function(e){return alist(e.sources).map(function(s){return s.url;}).filter(Boolean);}));
 document.getElementById('lens-totals').textContent=events.length+' '+tx('уникальных событий','unique events')+' · '+sources.size+' '+tx('URL источников','source URLs')+' · '+buckets[0]+' – '+buckets[buckets.length-1];
 renderLensMap(v,events,buckets);
 var track=v.tracks.find(function(t){return t.id===lensState.track;});
 document.getElementById('lens-selection').textContent=(track?lf(track,'label'):tx('Все темы','All themes'))+(lensState.bucket?' · '+lensState.bucket:'')+' · '+selected.length;
 document.getElementById('lens-clear').hidden=!lensState.track&&!lensState.bucket;
 var pages=Math.max(1,Math.ceil(selected.length/lensPageSize)),page=Math.min(pages,Math.max(1,parseInt(lensState.page,10)||1));lensState.page=String(page);
 var records=document.getElementById('lens-records');records.innerHTML=selected.slice((page-1)*lensPageSize,page*lensPageSize).map(function(e){return lensCard(e,v);}).join('')||'<p class="lens-empty">'+tx('Нет событий для выбранных условий.','No events match these filters.')+'</p>';bindAtlasCards(records);
 var pagination=document.getElementById('lens-pagination');pagination.innerHTML='<button type="button" data-lens-page="'+(page-1)+'" '+(page===1?'disabled':'')+'>'+tx('Предыдущие','Previous')+'</button><span>'+page+' / '+pages+'</span><button type="button" data-lens-page="'+(page+1)+'" '+(page===pages?'disabled':'')+'>'+tx('Следующие','Next')+'</button>';
 pagination.querySelectorAll('button').forEach(function(b){b.onclick=function(){lensState.page=this.dataset.lensPage;renderLens();writeAtlasHash();document.getElementById('lens-selection').scrollIntoView({block:'start'});};});
 var edges=lensExplicitEdges(selected);document.getElementById('lens-relations-title').textContent=tx('Явные связи между событиями','Explicit inter-event relationships')+' · '+edges.length;
 var links=document.getElementById('lens-relations');links.innerHTML=edges.map(function(edge){return '<article class="lens-relation"><button data-kind="event" data-id="'+esc(edge.source)+'">'+esc(byEvent[edge.source].title)+'</button><span>'+esc(relationLabel(edge.relation))+'</span><button data-kind="event" data-id="'+esc(edge.target)+'">'+esc(byEvent[edge.target].title)+'</button><p>'+esc(lf(edge,'summary'))+'</p></article>';}).join('')||'<p>'+tx('В выбранной группе нет явных связей между событиями.','This selection has no explicit inter-event relationships.')+'</p>';bindAtlasCards(links);
}
