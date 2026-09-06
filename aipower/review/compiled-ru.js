var ATLAS_RU=true;

var D = JSON.parse(document.getElementById('DATA').textContent);
var EV = D.events || [];
var ARCS = D.arcs || [];
var FAMILIES = D.arcFamilies || [];
var EDGES = D.edges || [];
var CLAIMS = D.claims || [];
var CHECKS = D.claimChecks || [];
var THESIS = D.thesisNodes || [];
var COUNTRIES = D.countries || [];
var COUNTERS = D.counterarguments || [];
var GAPS = D.gaps || [];
var SOURCES = D.sourceIndex || [];
var SOURCE_GROUPS = D.sourceGroups || [];
var CYBER_FRAMEWORK = D.cyberFramework || {};
var byEvent = Object.fromEntries(EV.map(function(item){ return [item.id, item]; }));
var byArc = Object.fromEntries(ARCS.map(function(item){ return [item.id, item]; }));
var byFamily = Object.fromEntries(FAMILIES.map(function(item){ return [item.id, item]; }));
var byEdge = Object.fromEntries(EDGES.map(function(item){ return [item.id, item]; }));
var byClaim = Object.fromEntries(CLAIMS.map(function(item){ return [item.id, item]; }));
var byCheck = Object.fromEntries(CHECKS.map(function(item){ return [item.id, item]; }));
var byThesis = Object.fromEntries(THESIS.map(function(item){ return [item.id, item]; }));
var byCounter = Object.fromEntries(COUNTERS.map(function(item){ return [item.id, item]; }));
var byGap = Object.fromEntries(GAPS.map(function(item){ return [item.id, item]; }));
var palette = ['#365f9d','#107052','#a66f13','#6b4aa2','#a1412b','#24727a','#a34869','#46535f','#2f7161','#8b5f20','#5164a3','#8d4f75','#5c6974'];
var relationColors = {
  supports:'#107052', supports_with_scope:'#24727a', supports_but_limits:'#a66f13',
  supports_counterargument:'#6b4aa2', challenges:'#a1412b', challenges_overclaim:'#a1412b',
  walks_back:'#a66f13', updates:'#365f9d', sets_up:'#46535f', develops_into:'#365f9d',
  escalates:'#a34869', countermove:'#6b4aa2', routes_around:'#24727a', mitigates:'#107052',
  limits:'#a66f13', qualifies:'#a66f13', refines:'#365f9d', parallel:'#46535f',
  generalizes:'#365f9d', institutionalizes:'#107052', reframes:'#6b4aa2', supports_arc:'#107052',
  key_node:'#46535f',part_of_arc:'#747c85',weakens:'#a66f13'
};
var graphState = { showAuto:false, preset:'', family:'', arc:'', relation:'' };
var catalogState = {
  q:'', jurisdiction:'', actor:'', family:'', lane:'', arc:'', relation:'', confidence:'', status:'',
  region:'', location:'', institution:'', geoContext:'', geoScope:'', actorType:'', actorJurisdiction:'', source:''
};
var cyberState = { mode:'core', role:'', jurisdiction:'', principalOnly:false, showLinks:true };
var cyberRenderedEvents = [];
var cyberThreadArcIds = [
  'ARC_CYBER_CLAIM_TO_CAVEAT',
  'ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK',
  'ARC_COGSEC_LAB_TO_WILD_TO_STATE',
  'ARC_QUIET_ACCESS_CONTROL',
  'ARC_FINANCE_GOVERNED_SHUTDOWN',
  'ARC_RUSSIA_SELECTIVE_SOVEREIGNTY'
];
var detailHistory = [];
var currentDetail = null;

function esc(value){
  return String(value == null ? '' : value).replace(/[&<>"]/g, function(char){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[char];
  });
}
function host(url){
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch (error) { return url || ''; }
}
function fmt(value){
  if (typeof value === 'number') return value.toLocaleString('ru-RU');
  return value == null ? '' : String(value);
}
function truncate(value, length){
  var text = String(value == null ? '' : value);
  return text.length > length ? text.slice(0, length - 1) + '…' : text;
}
function uniq(values){
  return Array.from(new Set((values || []).filter(Boolean)));
}
function tag(value, cls){
  if (!value) return '';
  return '<span class="tag ' + esc(cls || '') + '">' + esc(value) + '</span>';
}
function tags(values, cls){
  return (values || []).filter(Boolean).map(function(value){ return tag(value, cls); }).join('');
}
function itemTitle(id){
  return (byEvent[id] && byEvent[id].title) ||
    (byArc[id] && arcTitleRu(byArc[id])) ||
    (byEdge[id] && byEdge[id].summary_ru) ||
    (byClaim[id] && byClaim[id].title) ||
    (byCheck[id] && byCheck[id].title) ||
    (byThesis[id] && thesisLabelRu(byThesis[id])) ||
    (byCounter[id] && (byCounter[id].objection || byCounter[id].title)) ||
    (byGap[id] && (byGap[id].topic || byGap[id].title)) ||
    id;
}
function itemKind(id){
  if (byEvent[id]) return 'event';
  if (byArc[id]) return 'arc';
  if (byEdge[id]) return 'edge';
  if (byClaim[id]) return 'claim';
  if (byCheck[id]) return 'claimCheck';
  if (byThesis[id]) return 'thesis';
  if (byCounter[id]) return 'counterargument';
  if (byGap[id]) return 'gap';
  return '';
}
function detailLink(id){
  var kind = itemKind(id);
  if (!kind) return '<span class="tag">' + esc(id) + '</span>';
  return '<button class="ghost-btn" type="button" data-kind="' + esc(kind) + '" data-id="' + esc(id) + '">' + esc(kindLabel(kind) + ': ' + truncate(itemTitle(id), 54)) + '</button>';
}

function statusLabelRu(value){
  return ({
    verified:'Подтверждено',
    verified_as_reported:'Подтверждено как сообщение источника',
    verified_adopted_future_application:'Принято, применение впереди',
    verified_as_announcement:'Подтверждено как анонс',
    verified_as_reported_indictment_allegation:'Подтверждено как обвинение в indictment',
    verified_as_reported_not_primary_order:'Подтверждено по сообщениям, не по primary order',
    verified_as_reported_with_redacted_forensics:'Подтверждено по редактированной форензике',
    verified_as_speech_not_as_fact:'Подтверждена публичная формулировка, не сам claim',
    verified_controlled_evaluation:'Подтверждено в controlled evaluation',
    verified_current_rule:'Подтверждено как действующее правило',
    verified_announcement_implementation_pending:'Анонс подтверждён, реализация впереди',
    verified_announcement_details_pending:'Анонс подтверждён, детали и возможности не проверены',
    verified_mou_not_deployment:'Меморандум подтверждён, внедрение не установлено',
    verified_policy_decision_technical_detail_reported:'Решение подтверждено, технические детали частично по сообщениям',
    reported_findings_independent_validation_pending:'Результаты проекта опубликованы, независимая проверка впереди',
    verified_first_party_disclosure_independent_forensics_pending:'Сообщение пострадавшей стороны подтверждено, независимая форензика не опубликована',
    verified_first_party_operational_account:'Операционный отчёт самой организации подтверждён, подробные журналы не опубликованы',
    verified_preview_license_pending:'Технический отчёт и предварительная версия подтверждены; лицензия не завершена',
    proposal_not_enacted:'Проект, не действующее правило',
    verified_vendor_announcement:'Подтверждено как заявление поставщика',
    verified_report_with_older_data_vintage:'Доклад подтверждён, данные более раннего года',
    verified_public_exposure_not_compromise:'Публичная экспозиция, не компрометация',
    verified_program_not_outcome:'Программа подтверждена, итог не заявлен',
    verified_primary_binding_effective:'Действующее обязательное правило',
    verified_primary_binding_effective_scoped:'Действующее обязательное правило с ограниченной сферой',
    verified_primary_binding_with_grace_period:'Действует с переходным периодом',
    verified_primary_enacted_future_effective:'Принято, вступление в действие впереди',
    verified_primary_enacted_future_effective_at_cutoff:'Принято, на дату отсечения ещё не действует',
    verified_primary_consultation_voluntary:'Официальная консультация для добровольной методики',
    verified_primary_government_guidance_voluntary:'Добровольное государственное руководство',
    verified_primary_standards_initiative:'Официальная инициатива стандартизации',
    verified_primary_joint_guidance_nonbinding:'Совместное необязательное руководство',
    verified_primary_government_policy:'Официальная государственная политика',
    verified_primary_supervisory_signal_no_new_rule:'Надзорный сигнал без новых требований',
    verified_primary_government_guidance_scoped:'Государственное руководство с ограниченной сферой',
    verified_primary_government_blueprint_implementation_pending:'Государственный проект, реализация впереди',
    verified_primary_normative_government_guideline_scoped:'Нормативное руководство для ограниченной сферы',
    verified_primary_regulatory_risk_assessment:'Официальная оценка риска регулятора',
    verified_primary_regulatory_warning_nonbinding:'Необязательное предупреждение регулятора',
    verified_primary_final_guidance_voluntary:'Итоговое добровольное руководство',
    verified_primary_standard_projects_not_final:'Проекты стандартов, не итоговые правила',
    verified_primary_supervisory_requirement:'Конкретное надзорное требование',
    verified_primary_government_program_launched:'Государственная программа запущена',
    verified_primary_binding_effective_with_future_duties:'Правило действует, часть обязанностей впереди',
    verified_primary_draft_open_for_comment:'Официальный проект для обсуждения',
    verified_primary_supervisory_coordination_signal:'Сигнал координации надзора',
    verified_primary_government_program_directed:'Создание государственной программы поручено',
    verified_primary_multilateral_policy_warning:'Многостороннее политическое предупреждение',
    verified_primary_government_security_baseline_conditional:'Государственная baseline, обязательность зависит от применения',
    verified_primary_government_incident_report_controlled_evaluation:'Государственный отчёт об инциденте в контролируемой оценке',
    verified_primary_government_guidance_interim_nonbinding:'Промежуточная необязательная государственная методика',
    verified_primary_binding_enforcement_with_interpretive_guidance:'Действующие полномочия с официальным толкованием',
    verified_mixed_legal_force_and_implementation:'Подтверждено, юридическая сила и стадия различаются',
    verified_malicious_registry_artifacts_no_victim_prevalence:'Подтверждены malicious artifacts, не prevalence жертв',
    verified_preprint:'Подтверждено как preprint',
    needs_correction:'Нужна корректировка',
    partially_verified:'Частично подтверждено',
    partially_verified_contested:'Частично подтверждено, оспаривается',
    partially_verified_compliance_contested:'Частично подтверждено, compliance спорный',
    partially_verified_material_update:'Частично подтверждено, новые данные существенно меняют оценку',
    controlled_real_world_and_internal_red_team_no_wild_campaign:'Controlled и internal red team, без wild campaign',
    controlled_real_world_validation_no_wild_campaign:'Controlled validation, без wild campaign',
    reproducible_poc_no_wild_exploitation:'Воспроизводимый PoC, без wild exploitation',
    lab_verified_no_wild_exploitation:'Лабораторно подтверждено, без wild exploitation',
    reproducible_self_authored_preprint_synthetic:'Self-authored reproducible preprint, synthetic',
    advertisement_verified_implementation_unverified:'Реклама подтверждена, реализация не проверена',
    reported_unconfirmed:'Сообщается, не подтверждено',
    needs_primary_confirmation:'Нужен первичный источник',
    context_only:'Только контекст',
    disputed_capability_claim:'Спорное capability claim',
    disputed_specific_claim_valid_general_mechanism:'Частный claim спорен, механизм валиден'
  })[value] || relationLabel(value);
}
function statusShortRu(value){
  if (value === 'proposal_not_enacted') return 'Проект';
  if (value === 'verified_announcement_implementation_pending') return 'Анонс';
  if (value === 'verified_preview_license_pending') return 'Предв. версия';
  if (value === 'verified_public_exposure_not_compromise') return 'Экспозиция';
  if (value === 'verified_report_with_older_data_vintage') return 'Доклад';
  if (value === 'reported_findings_independent_validation_pending') return 'Результаты проекта';
  if (String(value).indexOf('verified') === 0) return 'Подтверждено';
  if (String(value).indexOf('partially_verified') === 0) return 'Частично';
  if (String(value).indexOf('controlled_') === 0) return 'Контролируемая проверка';
  if (value === 'reproducible_poc_no_wild_exploitation') return 'PoC';
  if (value === 'lab_verified_no_wild_exploitation') return 'Лабораторная проверка';
  if (value === 'reproducible_self_authored_preprint_synthetic') return 'Авторский препринт';
  if (value === 'advertisement_verified_implementation_unverified') return 'Реклама';
  if (String(value).indexOf('disputed') === 0) return 'Спорно';
  if (value === 'reported_unconfirmed') return 'Сообщается, не подтверждено';
  return relationLabel(value);
}
function dateBasisLabelRu(value){
  return ({
    public_disclosure_date:'дата публичного раскрытия',
    public_disclosure_date_incident_date_not_disclosed:'дата публичного раскрытия; дата инцидента не названа',
    public_beta_start_date:'начало публичного бета-тестирования',
    final_model_and_model_card_release_date:'финальный выпуск модели и её карточки',
    product_launch_date:'запуск продукта',
    license_announcement_date:'анонс лицензии',
    law_enactment_date:'принятие закона',
    official_report_release_date:'публикация официального доклада',
    final_rule_effective_date:'вступление окончательного правила в силу',
    commission_proposal_publication_date:'публикация проекта Еврокомиссии',
    commission_action_plan_publication_date:'публикация плана действий Еврокомиссии',
    framework_contract_award_month:'месяц заключения рамочного контракта',
    european_parliament_report_adoption_date:'принятие доклада Европарламентом',
    vendor_general_availability_announcement_date:'анонс общей доступности поставщиком',
    commission_program_status_update_date:'обновление статуса программы Еврокомиссией',
    qualification_framework_release_date:'публикация квалификационных требований',
    alliance_strategy_publication_date:'публикация стратегии альянса',
    preprint_publication_date:'публикация препринта',
    internet_measurement_snapshot_date:'дата снимка измерений в интернете',
    security_vendor_report_publication_date:'публикация отчёта ИБ-поставщика',
    program_announcement_date:'анонс программы',
    law_adoption_and_promulgation_date:'принятие и обнародование закона',
    technical_preview_launch_date:'запуск технической предварительной версии',
    service_announcement_date:'анонс сервиса',
    waitlist_removal_date:'отмена очереди на доступ',
    agency_complaint_date:'подача жалобы регулятором',
    public_event_date:'дата публичного события',
    intergovernmental_agreement_signing_date:'дата подписания межправительственного соглашения',
    head_of_state_speech_and_pledge_date:'дата выступления и обещаний главы государства',
    model_preview_announcement_date:'дата анонса предварительной версии модели',
    ministerial_policy_briefing_date:'дата брифинга министерства',
    government_mou_announcement_date:'дата правительственного анонса меморандума',
    phase_one_evaluation_announcement_date:'дата объявления итогов первого этапа',
    mou_signing_date:'дата подписания меморандума',
    first_results_announcement_date:'дата публикации первых результатов',
    statutory_effective_date:'дата вступления закона в силу',
    nist_public_announcement_date:'дата публикации NIST',
    framework_launch_date:'дата запуска рамки',
    initiative_launch_date:'дата запуска инициативы',
    order_effective_date:'дата вступления приказа в силу',
    chapter_amendment_signing_date:'дата подписания поправки',
    joint_guidance_publication_date:'дата публикации совместного руководства',
    policy_opinions_publication_date:'дата публикации государственной политики',
    joint_statement_publication_date:'дата совместного заявления',
    guide_publication_date:'дата публикации руководства',
    gchq_director_announcement_date_reported_by_ncsc:'дата анонса директора GCHQ по версии NCSC',
    guideline_approval_date:'дата утверждения руководства',
    report_month:'месяц публикации доклада',
    warning_adoption_date:'дата принятия предупреждения',
    practice_guide_publication_date:'дата публикации практического руководства',
    mandatory_standard_project_assignment_date:'дата назначения проекта обязательного стандарта',
    supervisory_letter_date:'дата надзорного письма',
    white_house_launch_date:'дата запуска Белым домом',
    regulation_entry_into_force_date:'дата вступления регламента в силу',
    initial_public_draft_date:'дата первичного публичного проекта',
    joint_statement_date:'дата совместного заявления',
    governor_program_announcement_date:'дата анонса программы губернатором',
    fsb_chair_letter_date:'дата письма председателя FSB',
    ism_september_release_publication_date:'дата сентябрьского выпуска ISM',
    statutory_reporting_effective_date:'дата начала обязательной отчётности',
    incident_detection_date:'дата обнаружения инцидента',
    interim_guidance_publication_date:'дата публикации промежуточной методики',
    statutory_enforcement_application_date:'дата начала правоприменения'
  })[value] || relationLabel(value);
}
function dateStatusLabelRu(value){
  if (String(value).indexOf('scheduled_as_of_') === 0) return 'запланировано на ' + String(value).replace('scheduled_as_of_', '');
  if (value === 'future_effective_at_research_cutoff') return 'ещё не действует на дату отсечения';
  return relationLabel(value);
}
function moneyStatusLabelRu(value){
  return ({ contract_ceiling:'потолок рамочного контракта' })[value] || relationLabel(value);
}
function evidenceContextLabelRu(value){
  return ({
    community_registries:'Каталоги сообщества',
    controlled_real_world_targets:'Контролируемые реальные цели',
    laboratory:'Лаборатория',
    'nine-country sample':'Выборка из девяти стран',
    public_registries:'Публичные реестры',
    synthetic_evaluation:'Синтетическая оценка',
    underground_market:'Теневой рынок',
    undisclosed_red_team_client:'Нераскрытый заказчик проверки',
    undisclosed_victim:'Нераскрытая жертва',
    undisclosed_victims:'Нераскрытые жертвы'
  })[value] || relationLabel(value);
}
function confidenceClass(value){
  return String(value || '').slice(0,1).toUpperCase();
}
function confidenceLabelRu(value){
  return value === 'D_for_capability_claim_B_for_speech_event' ? 'D для capability claim / B для speech event' : relationLabel(value);
}
function dateValue(value){
  return value || 'undated';
}
function edgeIsDefault(edge){
  return !edge.is_auto && edge.style !== 'thin' && !String(edge.id).startsWith('AUTO_');
}
function strengthRank(value){
  return { low:1, medium:2, high:3 }[value] || 0;
}
function graphEdges(){
  var preset = (D.recipes || []).find(function(item){ return item.id === graphState.preset; });
  var allowedArcs = preset && preset.recommended_arc_ids ? preset.recommended_arc_ids : null;
  var allowedRelations = preset && preset.recommended_relations ? preset.recommended_relations : null;
  var filters = (preset && preset.recommended_filters) || {};
  var allowedStyles = filters.edge_styles || null;
  var hiddenArcs = filters.hide_arc_ids || [];
  var minStrength = filters.min_strength ? strengthRank(filters.min_strength) : 0;
  return EDGES.filter(function(edge){
    if (!graphState.showAuto && !edgeIsDefault(edge)) return false;
    if (!graphState.preset && !graphState.family && !graphState.arc && byArc[edge.arc_id] && byArc[edge.arc_id].arc_kind === 'phase') return false;
    if (graphState.family && edge.arc_family_id !== graphState.family) return false;
    if (graphState.arc && edge.arc_id !== graphState.arc) return false;
    if (graphState.relation && edge.relation !== graphState.relation) return false;
    if (allowedArcs && allowedArcs.indexOf(edge.arc_id) === -1) return false;
    if (allowedRelations && allowedRelations.indexOf(edge.relation) === -1) return false;
    if (allowedStyles && allowedStyles.indexOf(edge.style) === -1) return false;
    if (hiddenArcs.indexOf(edge.arc_id) !== -1) return false;
    if (minStrength && strengthRank(edge.strength) < minStrength) return false;
    return true;
  });
}
function graphArcs(){
  var preset = (D.recipes || []).find(function(item){ return item.id === graphState.preset; });
  var allowedArcs = preset && preset.recommended_arc_ids ? preset.recommended_arc_ids : null;
  var hiddenArcs = (preset && preset.recommended_filters && preset.recommended_filters.hide_arc_ids) || [];
  return ARCS.filter(function(arc){
    if (!graphState.preset && !graphState.family && !graphState.arc && arc.arc_kind === 'phase') return false;
    if (graphState.family && arc.family_id !== graphState.family) return false;
    if (graphState.arc && arc.id !== graphState.arc) return false;
    if (allowedArcs && allowedArcs.indexOf(arc.id) === -1) return false;
    if (hiddenArcs.indexOf(arc.id) !== -1) return false;
    return true;
  });
}
function eventSearchText(event){
  return [
    event.id,event.title,event.date,event.actor,event.source_name,event.source_type,event.status,event.confidence,
    event.claim_supported,event.claim_challenged,event.notes,event.corroboration_needed,
    (event.geography_raw || []).join(' '),(event.jurisdictions || []).join(' '),(event.regions || []).join(' '),(event.locations || []).join(' '),
    (event.institutional_scopes || []).join(' '),(event.geo_context || []).join(' '),(event.geographic_scopes || []).join(' '),
    (event.evidence_context || []).join(' '),(event.actors_raw || []).join(' '),(event.actors || []).join(' '),(event.actor_entities || []).join(' '),
    (event.actor_types || []).join(' '),(event.actor_jurisdictions || []).join(' '),
    (event.stack_layer || []).join(' '),(event.strange_structure || []).join(' '),
    (event.arcIds || []).join(' '),(event.arcFamilyIds || []).join(' '),(event.relationTypes || []).join(' ')
  ].join(' ').toLowerCase();
}
function eventPasses(event){
  if (catalogState.q && eventSearchText(event).indexOf(catalogState.q) === -1) return false;
  if (catalogState.jurisdiction && (event.jurisdictions || []).indexOf(catalogState.jurisdiction) === -1) return false;
  if(catalogState.actor && (catalogState.actor==='__unresolved__' ? event.actor_classification_status!=='review_required' : (event.actor_entities||[]).indexOf(catalogState.actor)===-1))return false;
  if (catalogState.family && (event.arcFamilyIds || []).indexOf(catalogState.family) === -1) return false;
  if (catalogState.lane && (event.stack_layer || []).indexOf(catalogState.lane) === -1) return false;
  if (catalogState.arc && (event.arcIds || []).indexOf(catalogState.arc) === -1) return false;
  if (catalogState.relation && (event.relationTypes || []).indexOf(catalogState.relation) === -1) return false;
  if (catalogState.confidence && event.confidence !== catalogState.confidence) return false;
  if (catalogState.status && event.status !== catalogState.status) return false;
  if (catalogState.region && (event.regions || []).indexOf(catalogState.region) === -1) return false;
  if (catalogState.location && (event.locations || []).indexOf(catalogState.location) === -1) return false;
  if (catalogState.institution && (event.institutional_scopes || []).indexOf(catalogState.institution) === -1) return false;
  if (catalogState.geoContext && (event.geo_context || []).indexOf(catalogState.geoContext) === -1) return false;
  if (catalogState.geoScope && (event.geographic_scopes || []).indexOf(catalogState.geoScope) === -1) return false;
  if (catalogState.actorType && (event.actor_types || []).indexOf(catalogState.actorType) === -1) return false;
  if (catalogState.actorJurisdiction && (event.actor_jurisdictions || []).indexOf(catalogState.actorJurisdiction) === -1) return false;
  if (catalogState.source && event.source_type !== catalogState.source) return false;
  return true;
}
function countEdgesForArc(arcId){
  return graphEdges().filter(function(edge){ return edge.arc_id === arcId; }).length;
}
function countCoreEdgesForArc(arcId){
  return EDGES.filter(function(edge){ return edge.arc_id === arcId && edgeIsDefault(edge); }).length;
}
function factsForArc(arc){
  var ids = new Set((arc.key_nodes || []).filter(function(id){ return Boolean(byEvent[id]); }));
  EDGES.forEach(function(edge){
    if (edge.arc_id !== arc.id) return;
    if (byEvent[edge.source]) ids.add(edge.source);
    if (byEvent[edge.target]) ids.add(edge.target);
  });
  return Array.from(ids).map(function(id){ return byEvent[id]; }).sort(function(a, b){
    return String(a.date || '').localeCompare(String(b.date || '')) || a.id.localeCompare(b.id);
  });
}
function storyBounds(){
  var years = (D.summary.years || []).map(Number).filter(Number.isFinite);
  if (!years.length) years = EV.map(function(event){ return Number(String(event.date || '').slice(0, 4)); }).filter(Number.isFinite);
  return { min:Math.min.apply(null, years), max:Math.max.apply(null, years) };
}
function storyDateX(date, minYear, maxYear, startX, endX){
  var value = String(date || '');
  var year = Number(value.slice(0, 4)) || minYear;
  var month = Number(value.slice(5, 7)) || 1;
  var day = Number(value.slice(8, 10)) || 1;
  var start = Date.UTC(minYear, 0, 1);
  var end = Date.UTC(maxYear + 1, 0, 1);
  var current = Date.UTC(year, month - 1, day);
  return startX + ((current - start) / Math.max(1, end - start)) * (endX - startX);
}
function edgeTouchesThesis(edge){
  return edge.target_kind === 'synthetic_thesis' || edge.source_kind === 'synthetic_thesis' || byThesis[edge.target] || byThesis[edge.source];
}
function edgeTouchesStoryArc(edge){
  return edge.source_kind === 'story_arc' || edge.target_kind === 'story_arc' || byArc[edge.source] || byArc[edge.target];
}
function edgeArcOrder(edge){
  var index = ARCS.findIndex(function(arc){ return arc.id === edge.arc_id || arc.id === edge.source || arc.id === edge.target; });
  return index < 0 ? 9999 : index;
}
function edgePriority(edge){
  var relationScore = {
    supports: 8,
    supports_with_scope: 7,
    supports_but_limits: 7,
    challenges_overclaim: 6,
    walks_back: 6,
    refines: 5,
    qualifies: 5
  }[edge.relation] || 3;
  return (edgeTouchesStoryArc(edge) ? 100 : 0) + strengthRank(edge.strength) * 10 + relationScore - (edge.is_auto ? 20 : 0);
}
function displayedThesisEdges(visibleEdges){
  var byPair = new Map();
  visibleEdges
    .filter(function(edge){ return edgeTouchesThesis(edge) && edgeTouchesStoryArc(edge); })
    .sort(function(a, b){ return edgePriority(b) - edgePriority(a) || edgeArcOrder(a) - edgeArcOrder(b); })
    .forEach(function(edge){
      var thesisId = byThesis[edge.target] ? edge.target : edge.source;
      var pair = edgeArcId(edge) + '|' + thesisId;
      if (!byPair.has(pair)) byPair.set(pair, edge);
    });
  return Array.from(byPair.values()).sort(function(a, b){
    return edgeArcOrder(a) - edgeArcOrder(b) || edgePriority(b) - edgePriority(a);
  });
}
function arcColor(arcId){
  var index = ARCS.findIndex(function(arc){ return arc.id === arcId; });
  return palette[((index % palette.length) + palette.length) % palette.length];
}
function relationColor(relation){
  return relationColors[relation] || '#46535f';
}
function ruPlural(count, one, few, many){
  var n = Math.abs(Number(count)) % 100;
  var n1 = n % 10;
  if (n > 10 && n < 20) return many;
  if (n1 > 1 && n1 < 5) return few;
  if (n1 === 1) return one;
  return many;
}
function edgeArcId(edge){
  if (byArc[edge.arc_id]) return edge.arc_id;
  if (byArc[edge.source]) return edge.source;
  if (byArc[edge.target]) return edge.target;
  return '';
}
function edgeArcColor(edge){
  var arcId = edgeArcId(edge);
  return arcId ? arcColor(arcId) : relationColor(edge.relation);
}
function edgeTitleRu(edge){
  return [
    arcTitleRu(edgeArcId(edge)),
    relationLabel(edge.relation),
    edge.summary_ru || edge.summary
  ].filter(Boolean).join(' · ');
}
function headlineFindingRu(){
  return D.meta.subtitle_ru || 'Карта фактов о том, как вычисления, облака, модели, данные, кибер и капитал превращаются в среду по умолчанию: доступ дозируется, зависимость закрепляется, рента собирается.';
}
function kindLabel(kind){
  return {
    event:'факт',
    arc:'дуга',
    edge:'связь',
    claim:'тезис',
    claimCheck:'проверка',
    thesis:'опорный узел',
    layer:'слой',
    counterargument:'контраргумент',
    gap:'пробел'
  }[kind] || 'элемент';
}
function thesisLabelRu(nodeOrId){return lf(typeof nodeOrId==='string'?byThesis[nodeOrId]:nodeOrId,'label');}
function thesisSummaryRu(nodeOrId){return lf(typeof nodeOrId==='string'?byThesis[nodeOrId]:nodeOrId,'summary');}
function arcTitleRu(arcOrId){return lf(typeof arcOrId==='string'?byArc[arcOrId]:arcOrId,'title');}
function familyTitleRu(familyOrId){
  var family = typeof familyOrId === 'string' ? byFamily[familyOrId] : familyOrId;
  var id = typeof familyOrId === 'string' ? familyOrId : family?.id;
  return family?.label_ru || id || '';
}
function actorTypeLabelRu(value){
  return (D.actorTypeLabels && D.actorTypeLabels[value] && D.actorTypeLabels[value].label_ru) || relationLabel(value);
}
function structureLabelRu(value){
  return ({security:'безопасность',production:'производство',finance:'финансы',knowledge:'знание'})[value] || value;
}
function laneLabelRu(laneOrId){
  var lane = typeof laneOrId === 'string' ? (D.visualLanes || []).find(function(item){ return item.id === laneOrId; }) : laneOrId;
  var id = typeof laneOrId === 'string' ? laneOrId : lane?.id;
  var labels = {
    energy_compute_chips: 'Энергия, вычисления и чипы',
    cloud_inference: 'Облако и инференс',
    model_weights: 'Модели, веса и контроль доступа',
    data_telemetry: 'Данные и телеметрия',
    cyber_security_patch: 'Кибербезопасность и патчи',
    decision_support_cognition: 'Поддержка решений и когнитивный слой',
    governance_law: 'Управление и право',
    finance_rent: 'Финансы и рента'
  };
  return labels[id] || lane?.label_ru || id || '';
}
function stackTags(values){
  return (values || []).filter(Boolean).map(function(value){ return tag(laneLabelRu(value)); }).join('');
}
function recipeTitleRu(recipe){
  var titles = {
    VIEW_01_TIMELINE_LANES: 'Хронология по дорожкам',
    VIEW_02_WALKBACKS_ONLY: 'Только откаты и оговорки',
    VIEW_03_CONTROL_ESCALATION: 'Эскалация контроля',
    VIEW_04_COUNTERSTACKS: 'Контр-стеки и обходы',
    VIEW_05_DECISION_SOVEREIGNTY: 'Суверенность решений'
  };
  return titles[recipe.id] || recipe.label_ru || recipe.id;
}
function recipeDescriptionRu(recipe){
  var descriptions = {
    VIEW_01_TIMELINE_LANES: 'Разложить дуги от собственных вычислений 2016 года до права, чипов, моделей, киберслоя и поддержки решений 2026-го.',
    VIEW_02_WALKBACKS_ONLY: 'Показать, где рамка уточнялась: откат AI Diffusion, завышенная трактовка Mythos, вопрос владения данными Palantir, энергия и утечки.',
    VIEW_03_CONTROL_ESCALATION: 'От собственных ускорителей и дозируемого доступа к государственным институтам, контролю чипов, облачным закупкам, оценке моделей и поддержке решений.',
    VIEW_04_COUNTERSTACKS: 'Ответные ходы: редкоземельные ограничения, китайские чипы и открытые веса, транзитные обходы, российский селективный контур и европейские требования суверенности.',
    VIEW_05_DECISION_SOVEREIGNTY: 'Связать Palantir, военный и финансовый ИИ, сбои доверенного контекста, оценку моделей, уровни допуска в облачных закупках и архитектуру снижения зависимости.',
    VIEW_06_RUSSIA_SELECTIVE_SOVEREIGNTY: 'Показать российский контур от локализации данных и управляемой сети до статуса моделей, совместных вычислительных мощностей и поддержки решений, вместе с зависимостью от Nvidia, китайских чипов, открытых весов и импортной периферийной электроники.'
  };
  return descriptions[recipe.id] || recipe.description_ru || '';
}
function ruSafeWording(kind,id,text){return text||'';}
function correctionRailRu(){return alist(D.presentation.corrections);}

function initHeader(){
  var keyFinding = headlineFindingRu();
  var titleNode = document.getElementById('page-title');
  if (titleNode) titleNode.textContent = D.meta.display_title_ru || 'ИИ-стек: четыре структуры власти на одном КПП';
  document.getElementById('subtitle').textContent = keyFinding;
  document.getElementById('meta').innerHTML = [
    'v' + (D.meta.version || 'n/a'),
    D.meta.updated_at || D.meta.created_at || '',
    D.summary.total_events + ' фактов',
    D.summary.total_claims + ' ' + ruPlural(D.summary.total_claims, 'тезис', 'тезиса', 'тезисов'),
    D.summary.total_edges + ' ' + ruPlural(D.summary.total_edges, 'связь', 'связи', 'связей')
  ].filter(Boolean).map(function(item){ return '<span class="pill">' + esc(item) + '</span>'; }).join('');
  document.getElementById('edge-hint').textContent = 'Точки — датированные факты. Линии справа — связи дуг с опорными тезисами; автоматические и тонкие связи включаются отдельно.';
  document.getElementById('story-lede').textContent =
    'Точки — факты, расположенные на общей шкале по дате события. Цветная полоса показывает временной охват дуги, линии справа — её связи с опорными тезисами. Claims, caveats и служебные связи не изображаются как события.';
}

function initNav(){
  var tabs = [
    ['story','Карта'],
    ['cyber','Киберконтур 2025–2026'],
    ['timeline','Хронология'],
    ['catalog','Факты'],
    ['stack','Стек'],
    ['actors','Акторы'],
    ['claims','Тезисы'],
    ['sources','Источники']
  ];
  document.getElementById('nav').innerHTML = tabs.map(function(tab, index){
    return '<button type="button" class="' + (index ? '' : 'active') + '" data-tab="' + tab[0] + '">' + esc(tab[1]) + '</button>';
  }).join('');
  document.querySelectorAll('#nav button').forEach(function(button){
    button.addEventListener('click', function(){
      switchTab(button.dataset.tab);
    });
  });
}

function cyberArray(value){
  return Array.isArray(value) ? value : (value ? [value] : []);
}



function cyberDomainMeta(id){
  return cyberDomains().find(function(item){ return item.id === id; }) || {id:id,label_ru:id,short_ru:''};
}
function cyberRoleMeta(id){
  return cyberArray(CYBER_FRAMEWORK.roles).find(function(item){ return item.id === id; }) || {id:id,short_ru:id};
}

function cyberRoleClass(id){
  if (id === 'AI_ROLE_PROTECTED_SYSTEM') return 'protected';
  if (id === 'AI_ROLE_DEFENSIVE_TOOL') return 'defence';
  return 'attack';
}
function cyberPeriod(event){
  var date = String(event.date || '');
  if (date.slice(0, 4) === '2025') return 'y2025';
  var month = Number(date.slice(5, 7)) || 1;
  return month <= 6 ? 'h1' : 'h2';
}
function cyberDirectEdges(events){
  var ids = new Set((events || []).map(function(event){ return event.id; }));
  return EDGES.filter(function(edge){
    return byEvent[edge.source] && byEvent[edge.target] && ids.has(edge.source) && ids.has(edge.target) && !edge.is_auto && !String(edge.id || '').startsWith('AUTO_');
  });
}



function cyberJurisdictionLabel(value){
  return value || 'Без юрисдикции';
}



function renderCyberThreads(events){
  var rows = cyberThreadArcIds.map(function(arcId){
    var items = events.filter(function(event){ return cyberArray(event.arcIds).indexOf(arcId) !== -1; })
      .sort(function(a, b){ return String(a.date || '').localeCompare(String(b.date || '')); });
    return {arcId:arcId,items:items};
  }).filter(function(row){ return row.items.length > 1 && byArc[row.arcId]; });
  var root = document.getElementById('cyber-threads');
  root.innerHTML = rows.length ? rows.map(function(row){
    var track = row.items.map(function(event, index){
      return (index ? '<span class="cyber-thread-arrow">→</span>' : '') + '<button type="button" class="cyber-thread-event" data-kind="event" data-id="' + esc(event.id) + '"><time>' + esc(dateValue(event.date)) + '</time><span>' + esc(truncate(event.title, 68)) + '</span></button>';
    }).join('');
    return '<div class="cyber-thread"><div class="cyber-thread-title"><b>' + esc(arcTitleRu(row.arcId)) + '</b><span>' + row.items.length + ' фактов · общая арка, не доказанная причинная цепь</span></div><div class="cyber-thread-track">' + track + '</div></div>';
  }).join('') : '<div class="cyber-empty">В текущем срезе нет общей арки минимум для двух фактов.</div>';
  bindClickable(root);
}
function renderCyberEdgeList(events){
  var edges = cyberDirectEdges(events);
  var root = document.getElementById('cyber-edge-list');
  root.innerHTML = edges.length ? edges.map(function(edge){
    return '<article class="cyber-edge-item" data-kind="edge" data-id="' + esc(edge.id) + '"><div class="id">' + esc(edge.relation) + ' · ' + esc(edge.id) + '</div><div class="cyber-edge-path"><span>' + esc(truncate(itemTitle(edge.source), 54)) + '</span><i>→</i><span>' + esc(truncate(itemTitle(edge.target), 54)) + '</span></div><p class="small" style="margin-top:7px">' + esc(edge.summary_ru || edge.summary || '') + '</p></article>';
  }).join('') : '<div class="cyber-empty">В текущем срезе нет явных event-to-event рёбер. Общие механизмы показаны выше отдельно.</div>';
  bindClickable(root);
}
function drawCyberLinks(){
  var svg = document.getElementById('cyber-links');
  var board = document.getElementById('cyber-board');
  if (!svg || !board) return;
  if (!cyberState.showLinks){ svg.innerHTML = ''; return; }
  var boardRect = board.getBoundingClientRect();
  if (!boardRect.width || !boardRect.height) return;
  var cards = Array.from(board.querySelectorAll('.cyber-event'));
  var cardById = {};
  cards.forEach(function(card){ cardById[card.dataset.id] = card; });
  var edges = cyberDirectEdges(cyberRenderedEvents).filter(function(edge){ return cardById[edge.source] && cardById[edge.target]; });
  svg.setAttribute('viewBox', '0 0 ' + boardRect.width + ' ' + boardRect.height);
  svg.setAttribute('width', boardRect.width);
  svg.setAttribute('height', boardRect.height);
  svg.innerHTML = edges.map(function(edge){
    var sourceRect = cardById[edge.source].getBoundingClientRect();
    var targetRect = cardById[edge.target].getBoundingClientRect();
    var sx = sourceRect.left - boardRect.left + sourceRect.width / 2;
    var sy = sourceRect.top - boardRect.top + sourceRect.height / 2;
    var tx = targetRect.left - boardRect.left + targetRect.width / 2;
    var ty = targetRect.top - boardRect.top + targetRect.height / 2;
    var bend = Math.max(34, Math.abs(tx - sx) * .45);
    var c1x = sx + (tx >= sx ? bend : -bend);
    var c2x = tx - (tx >= sx ? bend : -bend);
    return '<path class="cyber-link" data-edge-id="' + esc(edge.id) + '" d="M' + sx.toFixed(1) + ',' + sy.toFixed(1) + ' C' + c1x.toFixed(1) + ',' + sy.toFixed(1) + ' ' + c2x.toFixed(1) + ',' + ty.toFixed(1) + ' ' + tx.toFixed(1) + ',' + ty.toFixed(1) + '" stroke="' + esc(relationColor(edge.relation)) + '"' + (edge.style === 'dashed' ? ' stroke-dasharray="6 5"' : '') + '/>';
  }).join('');
}
function bindCyberHover(root, edges){
  var cards = Array.from(root.querySelectorAll('.cyber-event'));
  cards.forEach(function(card){
    card.addEventListener('mouseenter', function(){
      var related = edges.filter(function(edge){ return edge.source === card.dataset.id || edge.target === card.dataset.id; });
      var connected = new Set();
      related.forEach(function(edge){ connected.add(edge.source); connected.add(edge.target); });
      cards.forEach(function(item){
        item.classList.toggle('is-active', item === card);
        item.classList.toggle('is-connected', item !== card && connected.has(item.dataset.id));
        item.classList.toggle('is-dimmed', related.length > 0 && !connected.has(item.dataset.id));
      });
      document.querySelectorAll('#cyber-links [data-edge-id]').forEach(function(path){
        var active = related.some(function(edge){ return edge.id === path.dataset.edgeId; });
        path.classList.toggle('is-active', active);
        path.classList.toggle('is-dimmed', related.length > 0 && !active);
      });
    });
    card.addEventListener('mouseleave', function(){
      cards.forEach(function(item){ item.classList.remove('is-active','is-connected','is-dimmed'); });
      document.querySelectorAll('#cyber-links [data-edge-id]').forEach(function(path){ path.classList.remove('is-active','is-dimmed'); });
    });
  });
}



function renderCapitalMix(){
  var node = document.getElementById('capital-mix');
  var mix = D.summary.capital_mix || [];
  var ledger = D.summary.capital_ledger || {};
  if (!node) return;
  if (!mix.length && !ledger.spent_rows) {
    node.innerHTML = '';
    node.style.display = 'none';
    return;
  }
  node.style.display = '';
  node.innerHTML = '<h3>Капитал: не один рейтинг, а разные режимы денег</h3>' + (mix.length ? '<div class="capital-mix-grid">' +
    mix.map(function(item){
      var source = item.url
        ? '<a href="' + esc(item.url) + '" target="_blank" rel="noreferrer">' + esc(item.source_name || host(item.url)) + '</a>'
        : esc(item.source_name || '');
      return '<article class="capital-item" data-kind="source" data-id="' + esc(item.url || item.source_name || '') + '">' +
        '<b>' + esc(capitalAmountRu(item)) + '</b>' +
        '<span>' + esc(capitalLabelRu(item)) + '</span>' +
        '<div class="mode">' + esc([capitalModeRu(item), capitalPeriodRu(item)].filter(Boolean).join(' · ')) + '</div>' +
        '<span>' + esc(capitalCaveatRu(item)) + '</span>' +
        '<span>' + source + '</span>' +
      '</article>';
    }).join('') +
    '</div>' : '') + renderCapitalLedger(ledger) +
    '<p class="capital-note">Смысл блока — не сложить суммы, а отделить годовые потоки, частные инвестиции, капитальные затраты, накопительные госфонды, мобилизационные программы, суверенные структуры и обещанные объёмы.</p>';
}

function capitalLabelRu(item){
  var raw = item.label_ru || item.label || item.label_en || '';
  var labels = {
    'Мир: annual corporate AI investment': 'Мир: годовые корпоративные ИИ-инвестиции',
    'Мир: годовые корпоративные AI-инвестиции': 'Мир: годовые корпоративные ИИ-инвестиции',
    'Мир: годовые корпоративные ИИ-инвестиции': 'Мир: годовые корпоративные ИИ-инвестиции',
    'США: private AI investment': 'США: частные ИИ-инвестиции',
    'США: частные AI-инвестиции': 'США: частные ИИ-инвестиции',
    'Китай: private AI investment': 'Китай: частные ИИ-инвестиции',
    'Китай: частные AI-инвестиции': 'Китай: частные ИИ-инвестиции',
    'Китай: AI guidance funds': 'Китай: госфонды в ИИ-компании',
    'Китай: госфонды в AI-компании': 'Китай: госфонды в ИИ-компании',
    'Китай: госфонды в ИИ-компании': 'Китай: госфонды в ИИ-компании',
    'Остальной мир: private implied': 'Остальной мир: частные инвестиции, оценка',
    'Gulf state vehicles': 'Залив: суверенные инвестиционные структуры',
    'США: Stargate pledge': 'США: Stargate, объявленный объём',
    'США: Stargate, объявленный объём': 'США: Stargate, объявленный объём',
    'Китай: новые госанонсы': 'Китай: новые госанонсы',
    'Залив: included AI announcements': 'Залив: включённые ИИ-анонсы',
    'Залив: включённые AI-анонсы': 'Залив: включённые ИИ-анонсы',
    'Европа: included AI announcements': 'Европа: включённые ИИ-анонсы',
    'Европа: включённые AI-анонсы': 'Европа: включённые ИИ-анонсы',
    'Прочие: national AI commitments': 'Прочие: национальные ИИ-программы',
    'Прочие: национальные AI-программы': 'Прочие: национальные ИИ-программы'
  };
  return labels[raw] || raw;
}
function capitalAmountRu(item){
  var raw = item.amount || '';
  var amounts = {
    '$100B+ / ~$40B reported': '$100B+ / ~$40B по сообщениям'
  };
  return amounts[raw] || raw;
}
function capitalModeRu(item){
  var raw = item.mode_ru || item.mode || item.mode_en || '';
  var modes = {
    'mobilization / pledge': 'мобилизация капитала / объявленное обязательство',
    'sovereign vehicle / reported fund': 'суверенная структура / заявленный фонд'
  };
  return modes[raw] || raw;
}
function capitalPeriodRu(item){
  var raw = item.period || '';
  var periods = {
    '2000–2023 cumulative': '2000–2023, накопительно',
    'announced 2025': 'объявлено в 2025'
  };
  return periods[raw] || raw;
}
function capitalCaveatRu(item){
  var raw = item.caveat_ru || item.caveat || item.caveat_en || '';
  var caveats = {
    'Годовой private-investment показатель; не равен государственным программам или capex.': 'Годовой показатель частных инвестиций; не равен государственным программам или капитальным затратам.',
    'Частная цифра занижает общую картину, потому что не включает guidance-funds.': 'Частная цифра занижает общую картину, потому что не включает государственно-направляемые фонды.',
    'Накопительная оценка, не сравнивать напрямую с годовым private investment.': 'Накопительная оценка; её нельзя напрямую сравнивать с годовым показателем частных инвестиций.',
    'Грубая разница между global private $344.7B, US $285.9B и China $12.4B.': 'Грубая разница между глобальными частными инвестициями $344.7B, США $285.9B и Китаем $12.4B.',
    'Мобилизация public-private капитала, не deployed spend.': 'Мобилизация государственного и частного капитала, а не уже развёрнутые расходы.',
    'MGX target/AUM и Saudi reported fund нельзя складывать с annual private investment.': 'Целевые активы MGX и сообщения о саудовском фонде нельзя складывать с годовым показателем частных инвестиций.'
  };
  return caveats[raw] || raw;
}

function renderCapitalLedger(ledger){
  if (!ledger || (!ledger.spent_rows && !ledger.announcement_rows)) return '';
  var totals = ledger.announcement_totals_usd_billion || {};
  var totalKeys = Object.keys(totals).filter(function(key){ return key !== 'Total'; });
  var totalCards = totalKeys.map(function(key){
    return '<div class="capital-total"><b>' + esc(moneyB(totals[key])) + '</b><span>' + esc(capitalRegionRu(key)) + '</span></div>';
  }).join('');
  var spent = selectCapitalSpentRows(ledger.spent_rows || []);
  var announced = (ledger.announcement_rows || []).filter(function(row){ return row.include_in_total; }).slice(0, 8);
  return '<div class="capital-ledger">' +
    '<div class="capital-ledger-head"><b>Потрачено / анонсы</b><span>EUR/USD ' + esc(ledger.exchange_rate_eur_usd || '') + ' · включённый итог ' + esc(moneyB(totals.Total || 0)) + '</span></div>' +
    (totalCards ? '<div class="capital-ledger-totals">' + totalCards + '</div>' : '') +
    '<table class="capital-ledger-table"><thead><tr><th>режим</th><th>строка</th><th>период</th><th>$B</th></tr></thead><tbody>' +
    spent.map(function(row){
      return '<tr><td>потрачено</td><td>' + esc(row.metric_ru || row.metric_en) + '<br><span class="id">' + esc(row.region_ru || row.region_en) + '</span></td><td>' + esc(row.period || '') + '</td><td>' + esc(moneyNumber(row.amount_usd_billion)) + '</td></tr>';
    }).join('') +
    announced.map(function(row){
      return '<tr><td>анонс</td><td>' + esc(row.initiative_ru || row.initiative_en) + '<br><span class="id">' + esc(statusLabelRu(row.status || '')) + '</span></td><td>' + esc(row.horizon_ru || row.horizon_en || '') + '</td><td>' + esc(moneyNumber(row.amount_usd_billion)) + '</td></tr>';
    }).join('') +
    '</tbody></table><p class="capital-ledger-warn">' + esc(ledger.non_additivity_ru || ledger.non_additivity_en || '') + '</p></div>';
}

function moneyB(value){
  var n = Number(value || 0);
  if (!n) return '$0B';
  if (n >= 1000) return '$' + (n / 1000).toFixed(n % 1000 ? 2 : 0) + 'T';
  return '$' + moneyNumber(n) + 'B';
}

function moneyNumber(value){
  var n = Number(value || 0);
  if (!Number.isFinite(n)) return '';
  if (n >= 100) return String(Math.round(n));
  if (n >= 10) return n.toFixed(1).replace(/.0$/, '');
  return n.toFixed(2).replace(/0$/, '').replace(/.0$/, '');
}

function selectCapitalSpentRows(rows){
  var wanted = [
    ['Global', 'Global corporate AI investment', '2025'],
    ['Global', 'Private AI investment subset', '2025'],
    ['US', 'Private AI investment', '2025'],
    ['China', 'Private AI investment', '2025'],
    ['China', 'Government venture funds into AI companies, cumulative', '2000-2023'],
    ['US', 'Google AI infrastructure capex', '2025']
  ];
  return wanted.map(function(match){
    return rows.find(function(row){
      return row.region_en === match[0] && row.metric_en === match[1] && row.period === match[2];
    });
  }).filter(Boolean);
}

function capitalRegionRu(key){
  return ({
    US: 'США',
    China: 'Китай',
    Gulf: 'Залив',
    Europe: 'Европа',
    Other: 'Прочие',
    Total: 'Итого'
  })[key] || key;
}

function optionList(values, label, selected, format){
  return '<option value="">' + esc(label) + '</option>' + values.map(function(value){
    var text = format ? format(value) : value;
    return '<option value="' + esc(value) + '"' + (selected === value ? ' selected' : '') + '>' + esc(text) + '</option>';
  }).join('');
}

function initGraphControls(){
  document.getElementById('family-select').innerHTML = optionList(FAMILIES.map(function(family){ return family.id; }), 'Семейство: все', '', familyTitleRu);
  document.getElementById('arc-select').innerHTML = '<option value="">Дуга: все</option>' + ARCS.map(function(arc){
    return '<option value="' + esc(arc.id) + '">' + esc(truncate(familyTitleRu(arc.family_id) + ' · ' + arcTitleRu(arc), 72)) + '</option>';
  }).join('');
  document.getElementById('relation-select').innerHTML = optionList(Object.keys(D.relationTypes || {}).sort(), 'Тип связи: все', '', relationLabel);
  document.getElementById('toggle-auto').addEventListener('click', function(){
    graphState.showAuto = !graphState.showAuto;
    this.classList.toggle('active', graphState.showAuto);
    this.textContent = graphState.showAuto ? 'Скрыть авто-связи' : 'Показать авто-связи';
    renderStoryMap();
  });
  document.getElementById('family-select').addEventListener('change', function(){ graphState.preset = ''; graphState.family = this.value; graphState.arc = ''; document.getElementById('arc-select').value = ''; renderStoryMap(); renderRecipes(); });
  document.getElementById('arc-select').addEventListener('change', function(){ graphState.preset = ''; graphState.arc = this.value; if (this.value) { graphState.family = byArc[this.value]?.family_id || ''; document.getElementById('family-select').value = graphState.family; } renderStoryMap(); renderRecipes(); });
  document.getElementById('relation-select').addEventListener('change', function(){ graphState.preset = ''; graphState.relation = this.value; renderStoryMap(); renderRecipes(); });
}

function renderStoryMap(){
  var svg = document.getElementById('story-svg');
  var rowH = 72;
  var top = 92;
  var labelX = 28;
  var bandStartX = 480;
  var bandEndX = 1000;
  var pathStartX = 1022;
  var thesisX = 1138;
  var widthAll = 1400;
  var visibleArcs = graphArcs();
  var thesisBottom = THESIS.length ? 150 + (THESIS.length - 1) * 124 + 58 : 0;
  var height = Math.max(620, top + visibleArcs.length * rowH + 76, thesisBottom);
  var visibleEdges = graphEdges();
  var thesisEdges = displayedThesisEdges(visibleEdges);
  var bounds = storyBounds();
  document.getElementById('edge-count').textContent = 'дуга→тезис: ' + thesisEdges.length + ' · граф: ' + visibleEdges.length + ' / ' + EDGES.length;
  var thesisY = {};
  THESIS.forEach(function(node, index){
    thesisY[node.id] = 150 + index * 124;
  });
  svg.setAttribute('viewBox', '0 0 ' + widthAll + ' ' + height);
  var out = '<rect width="' + widthAll + '" height="' + height + '" fill="transparent"/>';
  out += '<text x="' + labelX + '" y="30" class="svg-label">сюжетные дуги</text><text x="' + bandStartX + '" y="30" class="svg-label">факты по дате события</text><text x="' + thesisX + '" y="30" class="svg-label">опорные тезисы</text>';
  for (var year = bounds.min; year <= bounds.max; year += 1) {
    var yearX = storyDateX(String(year) + '-01-01', bounds.min, bounds.max, bandStartX, bandEndX);
    out += '<line class="story-grid" x1="' + yearX.toFixed(1) + '" y1="48" x2="' + yearX.toFixed(1) + '" y2="' + (height - 36) + '"/>';
    out += '<text class="story-year" x="' + (yearX + 4).toFixed(1) + '" y="44">' + year + '</text>';
  }
  out += '<line class="story-grid" x1="' + bandEndX + '" y1="48" x2="' + bandEndX + '" y2="' + (height - 36) + '"/>';
  visibleArcs.forEach(function(arc, index){
    var y = top + index * rowH;
    var facts = factsForArc(arc);
    var firstFact = facts[0];
    var lastFact = facts[facts.length - 1];
    var firstX = firstFact ? storyDateX(firstFact.date, bounds.min, bounds.max, bandStartX, bandEndX) : bandStartX;
    var lastX = lastFact ? storyDateX(lastFact.date, bounds.min, bounds.max, bandStartX, bandEndX) : bandStartX;
    var range = firstFact && lastFact ? String(firstFact.date).slice(0, 4) + '–' + String(lastFact.date).slice(0, 4) : 'без даты';
    var color = arcColor(arc.id);
    out += '<g class="arc-row" data-kind="arc" data-id="' + esc(arc.id) + '">';
    out += '<rect x="18" y="' + (y - 30) + '" width="' + (widthAll - 42) + '" height="58" rx="8" fill="' + (index % 2 ? 'rgba(255,255,255,.26)' : 'rgba(255,255,255,.48)') + '"/>';
    out += '<text x="' + labelX + '" y="' + (y - 7) + '" class="arc-title">' + esc(truncate(arcTitleRu(arc), 50)) + '</text>';
    out += '<text x="' + labelX + '" y="' + (y + 13) + '" class="arc-sub">' + esc(familyTitleRu(arc.family_id)) + ' · ' + facts.length + ' ' + ruPlural(facts.length, 'факт', 'факта', 'фактов') + ' · ' + range + '</text>';
    if (facts.length) out += '<rect class="arc-band" x="' + firstX.toFixed(1) + '" y="' + (y - 20) + '" width="' + Math.max(8, lastX - firstX).toFixed(1) + '" height="40" rx="8" fill="' + color + '" opacity=".14"/>';
    out += '</g>';
    var levelEnds = [-Infinity, -Infinity, -Infinity, -Infinity, -Infinity];
    var levelOffsets = [-14, -7, 0, 7, 14];
    facts.forEach(function(event){
      var dotX = storyDateX(event.date, bounds.min, bounds.max, bandStartX, bandEndX);
      var level = levelEnds.findIndex(function(previousX){ return dotX - previousX >= 10; });
      if (level < 0) level = levelEnds.indexOf(Math.min.apply(null, levelEnds));
      levelEnds[level] = dotX;
      var dotY = y + levelOffsets[level];
      var confidence = confidenceClass(event.confidence);
      out += '<circle class="event-dot ' + esc(confidence) + '" data-kind="event" data-id="' + esc(event.id) + '" data-arc="' + esc(arc.id) + '" data-date="' + esc(event.date) + '" cx="' + dotX.toFixed(1) + '" cy="' + dotY + '" r="4.7"><title>' + esc(event.date + ' · ' + event.title) + '</title></circle>';
    });
  });
  THESIS.forEach(function(node){
    var y = thesisY[node.id];
    out += '<g data-kind="thesis" data-id="' + esc(node.id) + '" class="arc-row">';
    out += '<rect x="' + (thesisX - 18) + '" y="' + (y - 32) + '" width="230" height="66" rx="10" fill="#fffefa" stroke="rgba(28,32,38,.18)"/>';
    out += '<text x="' + (thesisX - 2) + '" y="' + (y - 8) + '" class="arc-title">' + esc(truncate(thesisLabelRu(node), 28)) + '</text>';
    out += '<text x="' + (thesisX - 2) + '" y="' + (y + 12) + '" class="arc-sub">' + esc(node.id) + '</text>';
    out += '</g>';
  });
  thesisEdges.forEach(function(edge){
    var arcIndex = visibleArcs.findIndex(function(arc){ return arc.id === edge.arc_id; });
    if (arcIndex < 0) return;
    var y1 = top + arcIndex * rowH - 8;
    var thesisId = byThesis[edge.target] ? edge.target : edge.source;
    var y2 = thesisY[thesisId] || 120;
    var color = edgeArcColor(edge);
    var cls = 'edge-path ' + esc(edge.style || '') + (edge.is_auto ? ' thin' : '');
    out += '<path class="' + cls + '" data-kind="edge" data-id="' + esc(edge.id) + '" data-arc="' + esc(edgeArcId(edge)) + '" d="M' + pathStartX + ',' + y1 + ' C980,' + y1 + ' 986,' + y2 + ' ' + (thesisX - 22) + ',' + y2 + '" stroke="' + color + '" opacity="' + (edge.is_auto ? '.22' : '.5') + '"><title>' + esc(edgeTitleRu(edge)) + '</title></path>';
  });
  svg.innerHTML = out;
  bindClickable(svg);
  bindSvgTooltips(svg);
}

function renderRecipes(){
  document.getElementById('recipe-list').innerHTML = (D.recipes || []).map(function(recipe){
    return '<button type="button" class="recipe-row ' + (graphState.preset === recipe.id ? 'active' : '') + '" data-preset="' + esc(recipe.id) + '">' +
      '<code>' + esc(recipe.id) + '</code><b>' + esc(recipeTitleRu(recipe)) + '</b><span class="small">' + esc(recipeDescriptionRu(recipe)) + '</span></button>';
  }).join('');
  document.querySelectorAll('.recipe-row').forEach(function(row){
    row.addEventListener('click', function(){
      graphState.preset = graphState.preset === row.dataset.preset ? '' : row.dataset.preset;
      graphState.family = '';
      graphState.arc = '';
      graphState.relation = '';
      document.getElementById('family-select').value = '';
      document.getElementById('arc-select').value = '';
      document.getElementById('relation-select').value = '';
      renderStoryMap();
      renderRecipes();
    });
  });
}

function renderTimeline(){
  var svg = document.getElementById('timeline-svg');
  var lanes = D.visualLanes && D.visualLanes.length ? D.visualLanes : [
    { id:'governance_law', label_ru:'Управление и право' },
    { id:'energy_compute_chips', label_ru:'Энергия, вычисления и чипы' },
    { id:'model_weights', label_ru:'Модели, веса и доступ' },
    { id:'decision_support_cognition', label_ru:'Поддержка решений и когнитивный слой' }
  ];
  var years = D.summary.years && D.summary.years.length ? D.summary.years : [2022,2026];
  var minY = Math.min.apply(null, years);
  var maxY = Math.max.apply(null, years);
  var rowH = 70;
  var top = 68;
  var left = 238;
  var width = 1180;
  var height = Math.max(720, top + lanes.length * rowH + 72);
  svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
  function xFor(date){
    var y = Number(String(date || '').slice(0,4)) || minY;
    var m = Number(String(date || '').slice(5,7)) || 1;
    var d = Number(String(date || '').slice(8,10)) || 1;
    var start = Date.UTC(minY,0,1);
    var end = Date.UTC(maxY + 1,0,1);
    var current = Date.UTC(y,m - 1,d);
    return left + ((current - start) / (end - start)) * (width - left - 54);
  }
  function lanesFor(event){
    var hits = lanes.filter(function(lane){ return (event.stack_layer || []).indexOf(lane.id) !== -1; }).map(function(lane){ return lane.id; });
    return hits.length ? hits : [lanes[0].id];
  }
  var laneIndex = Object.fromEntries(lanes.map(function(lane, index){ return [lane.id, index]; }));
  var out = '<rect width="' + width + '" height="' + height + '" fill="transparent"/>';
  for (var year = minY; year <= maxY + 1; year += 1) {
    var xx = left + ((Date.UTC(year,0,1) - Date.UTC(minY,0,1)) / (Date.UTC(maxY + 1,0,1) - Date.UTC(minY,0,1))) * (width - left - 54);
    out += '<line class="axis" x1="' + xx + '" y1="28" x2="' + xx + '" y2="' + (height - 42) + '"/>';
    if (year <= maxY) out += '<text class="svg-id" x="' + (xx + 5) + '" y="22">' + year + '</text>';
  }
  lanes.forEach(function(lane, index){
    var y = top + index * rowH;
    out += '<line class="axis" x1="' + left + '" y1="' + y + '" x2="' + (width - 54) + '" y2="' + y + '"/>';
    out += '<text class="svg-label" x="24" y="' + (y - 6) + '">' + esc(truncate(laneLabelRu(lane), 30)) + '</text>';
    out += '<text class="svg-id" x="24" y="' + (y + 13) + '">' + esc(lane.id) + '</text>';
  });
  var offsets = {};
  EV.slice().sort(function(a,b){ return String(a.date).localeCompare(String(b.date)); }).forEach(function(event){
    lanesFor(event).forEach(function(lane){
      var index = laneIndex[lane] || 0;
      var key = lane + '-' + event.date;
      offsets[key] = (offsets[key] || 0) + 1;
      var x = xFor(event.date);
      var y = top + index * rowH - 8 + Math.min(offsets[key], 7) * 7;
      var c = confidenceClass(event.confidence);
      var r = c === 'A' ? 6 : c === 'B' ? 5.4 : 4.8;
      out += '<circle class="timeline-dot ' + esc(c) + '" data-kind="event" data-id="' + esc(event.id) + '" data-lane="' + esc(lane) + '" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + r + '"><title>' + esc(laneLabelRu(lane) + ': ' + event.title) + '</title></circle>';
    });
  });
  svg.innerHTML = out;
  bindClickable(svg);
  bindSvgTooltips(svg);
}

function initCatalogFilters(){
  document.getElementById('filter-jurisdiction').innerHTML = optionList(Object.keys(D.counts.jurisdictions || {}).sort(), 'Юрисдикция: все', '');
  document.getElementById('filter-actor').innerHTML = optionList(Object.entries(D.counts.actor_entities || {}).map(function(entry){ return entry[0]; }).sort(), 'Актор: все', '');
  document.getElementById('filter-family').innerHTML = optionList(FAMILIES.map(function(family){ return family.id; }), 'Сюжетное семейство: все', '', familyTitleRu);
  document.getElementById('filter-lane').innerHTML = optionList(Object.keys(D.counts.stack_layers || {}).sort(), 'Слой: все', '', laneLabelRu);
  document.getElementById('filter-arc').innerHTML = '<option value="">Точная дуга: все</option>' + ARCS.map(function(arc){ return '<option value="' + esc(arc.id) + '">' + esc(truncate(familyTitleRu(arc.family_id) + ' · ' + arcTitleRu(arc), 72)) + '</option>'; }).join('');
  document.getElementById('filter-relation').innerHTML = optionList(Object.keys(D.counts.relation_types || {}).sort(), 'Тип связи: все', '', relationLabel);
  document.getElementById('filter-confidence').innerHTML = optionList(Object.keys(D.summary.by_confidence || {}).sort(), 'Уверенность: все', '', confidenceLabelRu);
  document.getElementById('filter-status').innerHTML = optionList(Object.keys(D.summary.by_status || {}).sort(), 'Статус: все', '', statusLabelRu);
  document.getElementById('filter-region').innerHTML = optionList(Object.keys(D.counts.regions || {}).sort(), 'Регион: все', '');
  document.getElementById('filter-location').innerHTML = optionList(Object.keys(D.counts.locations || {}).sort(), 'Место / территория: все', '');
  document.getElementById('filter-institution').innerHTML = optionList(Object.keys(D.counts.institutional_scopes || {}).sort(), 'Институциональный контур: все', '');
  document.getElementById('filter-geo-context').innerHTML = optionList(Object.keys(D.counts.geo_context || {}).sort(), 'Контекстный тег: все', '');
  document.getElementById('filter-geo-scope').innerHTML = optionList(Object.keys(D.counts.geographic_scopes || {}).sort(), 'Масштаб: все', '');
  document.getElementById('filter-actor-type').innerHTML = optionList(Object.keys(D.counts.actor_types || {}).sort(), 'Тип актора: все', '', actorTypeLabelRu);
  document.getElementById('filter-actor-jurisdiction').innerHTML = optionList(Object.keys(D.counts.actor_jurisdictions || {}).sort(), 'Юрисдикция актора: все', '');
  document.getElementById('filter-source').innerHTML = optionList(Object.keys(D.counts.source_types || {}).sort(), 'Источник: все', '');
  var map = {
    'filter-jurisdiction':'jurisdiction','filter-actor':'actor','filter-family':'family',
    'filter-lane':'lane','filter-arc':'arc','filter-relation':'relation','filter-confidence':'confidence',
    'filter-status':'status','filter-region':'region','filter-location':'location','filter-institution':'institution',
    'filter-geo-context':'geoContext','filter-geo-scope':'geoScope','filter-actor-type':'actorType',
    'filter-actor-jurisdiction':'actorJurisdiction','filter-source':'source'
  };
  Object.keys(map).forEach(function(id){
    document.getElementById(id).addEventListener('change', function(){
      catalogState[map[id]] = this.value;
      renderCatalog();
    });
  });
  document.getElementById('search').addEventListener('input', function(){
    catalogState.q = this.value.trim().toLowerCase();
    renderCatalog();
  });
  document.getElementById('reset-filters').addEventListener('click', function(){
    Object.keys(catalogState).forEach(function(key){ catalogState[key] = ''; });
    document.getElementById('search').value = '';
    Object.keys(map).forEach(function(id){ document.getElementById(id).value = ''; });
    renderCatalog();
  });
}

function eventRow(event){
  return '<article class="row" data-kind="event" data-id="' + esc(event.id) + '">' +
    '<div class="date">' + esc(dateValue(event.date)) + '<br>' + esc(confidenceLabelRu(event.confidence)) + ' · ' + esc(statusShortRu(event.status)) + '</div>' +
    '<div><div class="row-title">' + esc(event.title) + '</div><div class="tags">' +
    tag(event.source_type) + stackTags((event.stack_layer || []).slice(0,3)) + tags((event.jurisdictions || []).slice(0,3)) +
    '</div></div><div class="badge">дуг: ' + esc((event.arcIds || []).length) + ' · связей: ' + esc((event.edgeIds || []).length) + '</div></article>';
}

function renderCatalog(){
  var list = EV.filter(eventPasses).sort(function(a,b){ return String(b.date).localeCompare(String(a.date)); });
  document.getElementById('catalog-count').textContent = list.length + ' из ' + EV.length + ' фактов';
  document.getElementById('catalog-list').innerHTML = list.map(eventRow).join('') || '<p class="small">Ничего не найдено.</p>';
  bindClickable(document.getElementById('catalog-list'));
}

function renderStack(){
  var years = D.summary.years || [];
  var layers = Object.keys(D.counts.stack_layers || {}).sort();
  var heat = function(count){ return count === 0 ? 0 : count === 1 ? 1 : count <= 3 ? 2 : count <= 6 ? 3 : count <= 10 ? 4 : 5; };
  var html = '<thead><tr><th>Слой</th>' + years.map(function(year){ return '<th>' + year + '</th>'; }).join('') + '<th>Σ</th></tr></thead><tbody>';
  layers.forEach(function(layer){
    var layerEvents = EV.filter(function(event){ return (event.stack_layer || []).indexOf(layer) !== -1; });
    html += '<tr class="clickable-row" data-kind="layer" data-id="' + esc(layer) + '"><td><b>' + esc(laneLabelRu(layer)) + '</b><br><span class="id">' + esc(layer) + '</span></td>';
    years.forEach(function(year){
      var count = layerEvents.filter(function(event){ return event.year === year; }).length;
      html += '<td class="heat' + heat(count) + '"><b>' + count + '</b></td>';
    });
    html += '<td><b>' + layerEvents.length + '</b></td></tr>';
  });
  document.getElementById('stack-table').innerHTML = html + '</tbody>';
  document.getElementById('layer-cards').innerHTML = layers.map(function(layer){
    var layerEvents = EV.filter(function(event){ return (event.stack_layer || []).indexOf(layer) !== -1; });
    var lane = (D.visualLanes || []).find(function(item){ return item.id === layer; });
    return '<article class="card clickable accent-blue" data-kind="layer" data-id="' + esc(layer) + '"><div class="id">' + esc(layer) + '</div><h3>' + esc(laneLabelRu(lane || layer)) + '</h3>' +
      '<p class="small">' + esc((lane && lane.notes_ru) || '') + '</p><div class="tags">' + tag(layerEvents.length + ' фактов') +
      tags(uniq(layerEvents.flatMap(function(event){ return event.strange_structure || []; })).slice(0,4)) + '</div></article>';
  }).join('');
  bindClickable(document.getElementById('stack-table'));
  bindClickable(document.getElementById('layer-cards'));
}

function renderActors(){
  var actors = Object.entries(D.counts.actor_entities || {}).filter(function(entry){ return entry[1] >= 2; }).slice(0, 36);
  document.getElementById('actor-cards').innerHTML = actors.map(function(entry){
    var actor = entry[0];
    var count = entry[1];
    var topEvents = EV.filter(function(event){ return (event.actor_entities || []).indexOf(actor) !== -1; }).slice(0, 3);
    return '<article class="card accent-green"><h3>' + esc(actor) + '</h3><div class="tags">' + tag(count + ' фактов') + '</div>' +
      '<div class="block"><h4>Связанные факты</h4>' + topEvents.map(function(event){ return '<p class="small">' + detailLink(event.id) + '</p>'; }).join('') + '</div></article>';
  }).join('');
  document.getElementById('country-cards').innerHTML = COUNTRIES.map(function(country, index){
    return '<article class="card accent-amber" data-kind="country" data-id="' + index + '"><h3>' + esc(country.geography) + '</h3>' +
      '<p class="small"><b>' + esc(country.tier_position || '') + '</b></p>' +
      '<div class="block"><h4>Контролируемые слои</h4><p class="small">' + esc((country.controlled_layers || []).join(', ')) + '</p></div>' +
      '<div class="block"><h4>Зависимости</h4><p class="small">' + esc((country.key_dependencies || []).join(', ')) + '</p></div>' +
      '<div class="tags">' + tag(country.confidence) + '</div></article>';
  }).join('');
  bindClickable(document.getElementById('country-cards'));
}

function renderClaims(){
  document.getElementById('claim-check-cards').innerHTML = CHECKS.map(function(claim){
    return '<article class="card clickable accent-violet" data-kind="claimCheck" data-id="' + esc(claim.id) + '">' +
      '<div class="id">' + esc(claim.id) + '</div><h3>' + esc(claim.claim) + '</h3>' +
      '<div class="tags">' + tag(statusLabelRu(claim.status), 'status-' + claim.status) + tag(confidenceLabelRu(claim.confidence), confidenceClass(claim.confidence)) + tag((claim.supporting_evidence || []).length + ' фактов') + '</div>' +
      '<div class="block quote"><h4>Осторожная формулировка</h4><p class="small">' + esc(claim.safe_wording_ru || '') + '</p></div></article>';
  }).join('');
  document.getElementById('claim-cards').innerHTML = CLAIMS.map(function(claim){
    return '<article class="card clickable accent-blue" data-kind="claim" data-id="' + esc(claim.id) + '">' +
      '<div class="id">' + esc(claim.id) + '</div><h3>' + esc(claim.claim || claim.title) + '</h3>' +
      '<div class="tags">' + tag(statusLabelRu(claim.status), 'status-' + claim.status) + tag(confidenceLabelRu(claim.evidence_level), confidenceClass(claim.evidence_level)) + stackTags((claim.stack_layer || []).slice(0,2)) + '</div>' +
      '<p class="small">' + esc(claim.recommended_phrasing_ru || claim.recommended_phrasing || '') + '</p></article>';
  }).join('');
  bindClickable(document.getElementById('claim-check-cards'));
  bindClickable(document.getElementById('claim-cards'));
}

function recommendationItem(text){
  var raw = String(text || '');
  var match = raw.match(/^([a-z]+-[0-9]+)(?:\s*\/\s*([a-z]+-[0-9]+))?/i);
  if (!match) return esc(raw);
  var ids = [match[1], match[2]].filter(Boolean);
  var rest = raw.slice(match[0].length).trim();
  return ids.map(detailLink).join(' ') + (rest ? ' <span>' + esc(rest) + '</span>' : '');
}
function recommendationCard(key, title, description, items, accent){
  items = items || [];
  var preview = items.slice(0, key === 'ready_to_publish' ? 18 : 9);
  return '<article class="card ' + esc(accent) + '"><div class="id">' + esc(key) + '</div><h3>' + esc(title) + '</h3>' +
    '<p class="small">' + esc(description) + '</p><div class="tags">' + tag(items.length + ' пунктов') + '</div>' +
    '<ul class="recommendation-list">' + preview.map(function(item){ return '<li>' + recommendationItem(item) + '</li>'; }).join('') +
    (items.length > preview.length ? '<li>+' + esc(items.length - preview.length) + ' ещё в исходном JSON</li>' : '') + '</ul></article>';
}
function renderSources(){
  var rec = D.recommendations || {};
  var recCards = [
    recommendationCard('ready_to_publish', 'Готово к публикации', 'Тезисы с достаточной опорой и безопасной формулировкой.', rec.ready_to_publish, 'accent-green'),
    recommendationCard('needs_correction', 'Править формулировку', 'Тезисы можно использовать, но нужно уточнить деньги, статус, источник или степень уверенности.', rec.needs_correction, 'accent-amber'),
    recommendationCard('downgrade_or_remove', 'Только как спорное или убрать', 'Эти пункты нельзя подавать как установленный факт без явной оговорки.', rec.downgrade_or_remove, 'accent-red')
  ].join('');
  document.getElementById('gap-cards').innerHTML = recCards + GAPS.map(function(gap){
    return '<article class="card clickable accent-amber" data-kind="gap" data-id="' + esc(gap.id) + '"><div class="id">' + esc(gap.id + ' · ' + (gap.priority || '')) + '</div>' +
      '<h3>' + esc(gap.topic || gap.title) + '</h3><p class="small">' + esc(gap.why || '') + '</p></article>';
  }).join('');
  document.getElementById('source-list').innerHTML = (SOURCE_GROUPS.length ? SOURCE_GROUPS : SOURCES.map(function(source){
    return { family: source.name || source.title || host(source.url), sources:[source], used_by:source.used_by || [], types:[source.type || 'источник'] };
  })).map(function(group){
    var topSources = (group.sources || []).slice(0, 4);
    var links = topSources.map(function(source){
      var label = source.name || source.title || host(source.url);
      return source.url ? '<a href="' + esc(source.url) + '" target="_blank" rel="noopener">' + esc(truncate(label, 82)) + '</a>' : esc(truncate(label, 82));
    }).join('');
    return '<div class="source-item"><b>' + esc(group.family) + '</b><br><span class="small">' +
      esc((group.types || []).slice(0, 3).join(', ') || 'источник') + ' · материалов: ' + esc((group.sources || []).length) +
      ' · использований: ' + esc((group.used_by || []).length) + '</span><div class="source-links">' + links + '</div></div>';
  }).join('');
  bindClickable(document.getElementById('gap-cards'));
}

function sourceBlock(item){
  var sources = item.sources || [];
  if (!sources.length && item.url) sources = [{ name:item.source_name || host(item.url), url:item.url, type:item.source_type || '', date:item.source_date || item.date || '' }];
  if (!sources.length) return '';
  return '<div class="block"><h4>Источники</h4>' + sources.map(function(source){
    var label = source.name || source.title || source.url;
    return '<p class="small">' + (source.url ? '<a href="' + esc(source.url) + '" target="_blank" rel="noopener">' + esc(label) + '</a>' : esc(label)) +
      ' ' + tag(source.type) + ' ' + tag(source.date) + '</p>';
  }).join('') + '</div>';
}
function numberBlock(numbers){
  var entries = Object.entries(numbers || {});
  if (!entries.length) return '';
  return '<div class="block"><h4>Числа</h4><div class="tags">' + entries.map(function(entry){ return tag(entry[0] + ': ' + fmt(entry[1])); }).join('') + '</div></div>';
}
function edgeList(ids){
  if (!ids || !ids.length) return '';
  return '<div class="block"><h4>Связанные ребра</h4>' + ids.slice(0, 18).map(function(id){ return detailLink(id); }).join(' ') + '</div>';
}
function arcList(ids){
  if (!ids || !ids.length) return '';
  return '<div class="block"><h4>Сюжетные дуги</h4>' + ids.map(function(id){ return detailLink(id); }).join(' ') + '</div>';
}
function distinctDetailBlock(seen, value, title, cls){
  var text = String(value || '').trim();
  if (!text || seen.indexOf(text) !== -1) return '';
  seen.push(text);
  return '<div class="block ' + esc(cls || '') + '"><h4>' + esc(title) + '</h4><p>' + esc(text) + '</p></div>';
}
function taxonomyTagBlock(title, values, format){
  values = values || [];
  if (!values.length) return '';
  return '<div class="block"><h4>' + esc(title) + '</h4><div class="tags">' + values.map(function(value){ return tag(format ? format(value) : value); }).join('') + '</div></div>';
}
function renderEventDetail(event){
  var seen = [];
  return '<h2 id="detail-title">' + esc(event.title) + '</h2><div class="id">' + esc(event.id) + '</div>' +
    '<div class="tags">' + tag(event.date) + (event.date_basis ? tag(dateBasisLabelRu(event.date_basis)) : '') + (event.date_status ? tag(dateStatusLabelRu(event.date_status)) : '') + (event.status_update_date ? tag('обновлено: ' + event.status_update_date) : '') + (event.current_legal_status ? tag(event.current_legal_status) : '') + (event.money_status ? tag(moneyStatusLabelRu(event.money_status)) : '') + tag(confidenceLabelRu(event.confidence), confidenceClass(event.confidence)) + tag(statusLabelRu(event.status), 'status-' + event.status) + tag(event.source_type) + tags(event.jurisdictions) + '</div>' +
    distinctDetailBlock(seen, event.legal_update_ru || event.independent_review_summary_ru, event.status_update_date ? 'Обновление статуса · ' + event.status_update_date : 'Обновление статуса', 'quote') +
    distinctDetailBlock(seen, event.claim_supported, 'Что поддерживает', 'quote') +
    distinctDetailBlock(seen, event.claim_challenged, 'Что ограничивает или оспаривает', 'caveat') +
    distinctDetailBlock(seen, event.corroboration_needed, 'Что нужно добрать', 'caveat') +
    distinctDetailBlock(seen, event.safe_wording, 'Осторожная формулировка', 'caveat') +
    distinctDetailBlock(seen, event.notes, 'Заметки', '') +
    ((event.caveats || []).length ? '<div class="block caveat"><h4>Ограничения доказательной базы</h4><ul class="recommendation-list">' + event.caveats.map(function(item){ return '<li>' + esc(item) + '</li>'; }).join('') + '</ul></div>' : '') +
    (event.exact_quote_short ? '<div class="block quote"><h4>Короткая цитата</h4><p>' + esc(event.exact_quote_short) + '</p></div>' : '') +
    ((event.evidence_context || []).length ? '<div class="block"><h4>Контекст доказательства</h4><div class="tags">' + (event.evidence_context || []).map(function(value){ return tag(evidenceContextLabelRu(value)); }).join('') + '</div></div>' : '') +
    taxonomyTagBlock('Регион', event.regions) + taxonomyTagBlock('Место / территория', event.locations) +
    taxonomyTagBlock('Институциональный контур', event.institutional_scopes) + taxonomyTagBlock('Контекстные геотеги', event.geo_context) +
    taxonomyTagBlock('Масштаб', event.geographic_scopes) +
    '<div class="block"><h4>Акторы</h4><div class="tags">' + tags(event.actor_entities) + tags((event.actor_types || []).map(actorTypeLabelRu)) + '</div></div>' +
    '<div class="block"><h4>Стек и структуры</h4><div class="tags">' + stackTags(event.stack_layer) + tags((event.strange_structure || []).map(structureLabelRu)) + tags(event.research_question) + '</div></div>' +
    numberBlock(event.numbers) + arcList(event.arcIds) + edgeList(event.edgeIds) + sourceBlock(event);
}
function renderArcDetail(arc){
  var arcEdges = EDGES.filter(function(edge){ return edge.arc_id === arc.id; });
  var facts = factsForArc(arc);
  return '<h2 id="detail-title">' + esc(arcTitleRu(arc)) + '</h2><div class="id">' + esc(arc.id) + '</div>' +
    '<div class="tags">' + tag(familyTitleRu(arc.family_id)) + tag(arc.arc_kind) + tag(arc.arc_type) + tag(arc.status) + tag(arc.start_date) + tag(arc.end_date) + tags(arc.visual_lanes) + '</div>' +
    '<div class="block quote"><h4>Тезис дуги</h4><p>' + esc(arc.thesis_ru || '') + '</p></div>' +
    (arc.safe_wording_ru ? '<div class="block caveat"><h4>Границы вывода</h4><p>' + esc(ruSafeWording('arc', arc.id, arc.safe_wording_ru)) + '</p></div>' : '') +
    '<div class="block"><h4>Факты дуги по времени</h4>' + facts.map(function(event){ return detailLink(event.id); }).join(' ') + '</div>' +
    '<div class="block"><h4>Что не следует из данных</h4><p class="small">' + esc((arc.counterpoints || []).join(' · ')) + '</p></div>' +
    '<details class="block"><summary>Технические связи графа (' + arcEdges.length + ')</summary><div class="block">' + arcEdges.slice(0, 36).map(function(edge){ return detailLink(edge.id); }).join(' ') + '</div></details>';
}
function renderEdgeDetail(edge){
  return '<h2 id="detail-title">' + esc(edge.summary_ru || edge.id) + '</h2><div class="id">' + esc(edge.id) + '</div>' +
    '<div class="tags">' + tag(familyTitleRu(edge.arc_family_id)) + tag(edge.relation) + tag(edge.strength) + tag(edge.evidence_level) + tag(edge.visual_lane) + tag(edge.style) + (edge.is_auto ? tag('авто') : tag('основная')) + '</div>' +
    '<div class="block quote"><h4>Смысл связи</h4><p>' + esc(edge.summary_ru || '') + '</p></div>' +
    '<div class="two-col"><div class="block"><h4>Откуда</h4>' + detailLink(edge.source) + '<p class="small">' + esc(edge.source_kind || '') + '</p></div>' +
    '<div class="block"><h4>Куда</h4>' + detailLink(edge.target) + '<p class="small">' + esc(edge.target_kind || '') + '</p></div></div>' +
    '<div class="block"><h4>Сюжетная дуга</h4>' + detailLink(edge.arc_id) + '</div>' +
    '<div class="block"><h4>Тип связи</h4><p class="small">' + esc(D.relationTypes[edge.relation] || '') + '</p></div>';
}
function renderClaimDetail(claim){
  return '<h2 id="detail-title">' + esc(claim.claim || claim.title) + '</h2><div class="id">' + esc(claim.id) + '</div>' +
    '<div class="tags">' + tag(statusLabelRu(claim.status), 'status-' + claim.status) + tag(confidenceLabelRu(claim.evidence_level || claim.confidence), confidenceClass(claim.evidence_level || claim.confidence)) + stackTags(claim.stack_layer) + tags(claim.geography) + '</div>' +
    (claim.legal_update_ru ? '<div class="block quote"><h4>Обновление статуса' + (claim.status_update_date ? ' · ' + esc(claim.status_update_date) : '') + '</h4><p>' + esc(claim.legal_update_ru) + '</p>' + (claim.legal_update_caveat_ru ? '<p class="small">' + esc(claim.legal_update_caveat_ru) + '</p>' : '') + '</div>' : '') +
    (claim.recommended_phrasing_ru ? '<div class="block quote"><h4>Рекомендуемая формулировка</h4><p>' + esc(claim.recommended_phrasing_ru) + '</p></div>' : '') +
    (claim.recommended_phrasing ? '<div class="block"><h4>Формулировка на английском</h4><p>' + esc(claim.recommended_phrasing) + '</p></div>' : '') +
    (claim.caveats && claim.caveats.length ? '<div class="block caveat"><h4>Ограничения</h4><p>' + esc(claim.caveats.join(' · ')) + '</p></div>' : '') +
    sourceBlock(claim);
}
function renderClaimCheckDetail(claim){
  return '<h2 id="detail-title">' + esc(claim.claim) + '</h2><div class="id">' + esc(claim.id) + '</div>' +
    '<div class="tags">' + tag(statusLabelRu(claim.status), 'status-' + claim.status) + tag(confidenceLabelRu(claim.confidence), confidenceClass(claim.confidence)) + '</div>' +
    '<div class="block quote"><h4>Осторожная формулировка</h4><p>' + esc(claim.safe_wording_ru || '') + '</p></div>' +
    '<div class="block caveat"><h4>Что может сломать тезис</h4><p>' + esc(claim.what_could_break_it || '') + '</p></div>' +
    '<div class="block"><h4>Поддерживающие факты</h4>' + (claim.supporting_evidence || []).map(detailLink).join(' ') + '</div>';
}
function renderThesisDetail(node){
  var related = EDGES.filter(function(edge){ return edge.source === node.id || edge.target === node.id; });
  return '<h2 id="detail-title">' + esc(thesisLabelRu(node)) + '</h2><div class="id">' + esc(node.id) + '</div>' +
    '<div class="block quote"><h4>Смысл узла</h4><p>' + esc(thesisSummaryRu(node)) + '</p></div>' +
    '<div class="block"><h4>Связанные ребра</h4>' + related.slice(0, 40).map(function(edge){ return detailLink(edge.id); }).join(' ') + '</div>';
}
function renderLayerDetail(layer){
  var lane = (D.visualLanes || []).find(function(item){ return item.id === layer; }) || {};
  var layerEvents = EV.filter(function(event){ return (event.stack_layer || []).indexOf(layer) !== -1; });
  var layerClaims = CLAIMS.filter(function(claim){ return (claim.stack_layer || []).indexOf(layer) !== -1; });
  var layerArcs = ARCS.filter(function(arc){
    return (arc.visual_lanes || []).indexOf(layer) !== -1 ||
      EDGES.some(function(edge){ return edge.arc_id === arc.id && layerEvents.some(function(event){ return event.id === edge.source || event.id === edge.target; }); });
  });
  var geographies = uniq(layerEvents.flatMap(function(event){ return event.geography || []; })).slice(0, 10);
  var actors = uniq(layerEvents.flatMap(function(event){ return event.actor_entities || []; })).slice(0, 10);
  return '<h2 id="detail-title">' + esc(laneLabelRu(lane || layer)) + '</h2><div class="id">' + esc(layer) + '</div>' +
    '<div class="tags">' + tag(layerEvents.length + ' фактов') + tag(layerClaims.length + ' тезисов') + tag(layerArcs.length + ' дуг') + tags(geographies.slice(0,4)) + '</div>' +
    (lane.notes_ru ? '<div class="block quote"><h4>Роль слоя</h4><p>' + esc(lane.notes_ru) + '</p></div>' : '') +
    '<div class="block"><button class="ghost-btn" type="button" data-filter-layer="' + esc(layer) + '">Показать факты слоя в каталоге</button></div>' +
    '<div class="block"><h4>Ключевые факты</h4>' + layerEvents.slice(0, 14).map(function(event){ return detailLink(event.id); }).join(' ') + '</div>' +
    '<div class="block"><h4>Связанные дуги</h4>' + layerArcs.slice(0, 12).map(function(arc){ return detailLink(arc.id); }).join(' ') + '</div>' +
    '<div class="block"><h4>Связанные тезисы</h4>' + layerClaims.slice(0, 14).map(function(claim){ return detailLink(claim.id); }).join(' ') + '</div>' +
    '<div class="block"><h4>Акторы</h4><div class="tags">' + tags(actors) + '</div></div>';
}
function renderCountryDetail(index){
  var country = COUNTRIES[Number(index)] || {};
  return '<h2 id="detail-title">' + esc(country.geography || 'Страна') + '</h2><div class="tags">' + tag(country.tier_position) + tag(country.confidence) + '</div>' +
    '<div class="block"><h4>Контролируемые слои</h4><p>' + esc((country.controlled_layers || []).join(', ')) + '</p></div>' +
    '<div class="block"><h4>Арендуемые или внешние слои</h4><p>' + esc((country.rented_or_external_layers || []).join(', ')) + '</p></div>' +
    '<div class="block"><h4>Главные рычаги</h4><p>' + esc((country.key_levers || []).join(', ')) + '</p></div>' +
    '<div class="block"><h4>Поддерживающие факты</h4>' + (country.strongest_supporting_evidence || []).map(detailLink).join(' ') + '</div>' +
    '<div class="block caveat"><h4>Контрфакты</h4><p>' + esc((country.strongest_counter_evidence || []).join(' · ')) + '</p></div>';
}
function renderGapDetail(gap){
  return '<h2 id="detail-title">' + esc(gap.topic || gap.title) + '</h2><div class="id">' + esc(gap.id) + '</div><div class="tags">' + tag(gap.priority) + tag(gap.status) + '</div>' +
    '<div class="block quote"><h4>Почему важно</h4><p>' + esc(gap.why || '') + '</p></div>' +
    '<div class="block"><h4>Что закроет пробел</h4><p>' + esc(gap.what_would_close || '') + '</p></div>' +
    (gap.resolution ? '<div class="block"><h4>Решение</h4><p>' + esc(gap.resolution) + '</p></div>' : '');
}
function renderCounterargumentDetail(item){
  return '<h2 id="detail-title">' + esc(item.objection || item.title) + '</h2><div class="id">' + esc(item.id) + '</div>' +
    '<div class="tags">' + tag(item.evidence_status) + '</div>' +
    (item.steelman ? '<div class="block quote"><h4>Сильная версия возражения</h4><p>' + esc(item.steelman) + '</p></div>' : '') +
    (item.how_to_handle ? '<div class="block"><h4>Как учитывать</h4><p>' + esc(item.how_to_handle) + '</p></div>' : '') +
    ((item.evidence || []).length ? '<div class="block"><h4>Связанные факты</h4>' + item.evidence.map(detailLink).join(' ') + '</div>' : '');
}
function setBackButton(){
  var back = document.getElementById('detail-back');
  back.disabled = detailHistory.length === 0;
  back.textContent = detailHistory.length ? '← Назад: ' + kindLabel(detailHistory[detailHistory.length - 1].kind) : '← Назад';
}
function _legacyOpenDetail(kind, id, options){
  options = options || {};
  if (!options.replace && currentDetail && (currentDetail.kind !== kind || currentDetail.id !== id)) {
    detailHistory.push(currentDetail);
  }
  var html = '';
  if (kind === 'event') html = renderEventDetail(byEvent[id]);
  if (kind === 'arc') html = renderArcDetail(byArc[id]);
  if (kind === 'edge') html = renderEdgeDetail(byEdge[id]);
  if (kind === 'claim') html = renderClaimDetail(byClaim[id]);
  if (kind === 'claimCheck') html = renderClaimCheckDetail(byCheck[id]);
  if (kind === 'thesis') html = renderThesisDetail(byThesis[id]);
  if (kind === 'layer') html = renderLayerDetail(id);
  if (kind === 'country') html = renderCountryDetail(id);
  if (kind === 'counterargument') html = renderCounterargumentDetail(byCounter[id]);
  if (kind === 'gap') html = renderGapDetail(byGap[id]);
  if (!html) return;
  currentDetail = { kind: kind, id: id };
  document.getElementById('detail').innerHTML = html;
  bindClickable(document.getElementById('detail'));
  bindDetailActions(document.getElementById('detail'));
  setBackButton();
  document.getElementById('modal').classList.add('show');
  document.getElementById('modal').setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}
function goBackDetail(){
  var previous = detailHistory.pop();
  if (!previous) return;
  openDetail(previous.kind, previous.id, { replace:true });
}
function _legacyCloseDetail(){
  document.getElementById('modal').classList.remove('show');
  document.getElementById('modal').setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  detailHistory = [];
  currentDetail = null;
  setBackButton();
}

function _legacySwitchTab(tabId){
  if (!document.getElementById('view-' + tabId)) return;
  document.querySelectorAll('#nav button').forEach(function(item){ item.classList.toggle('active', item.dataset.tab === tabId); });
  document.querySelectorAll('.view').forEach(function(item){ item.classList.toggle('active', item.id === 'view-' + tabId); });
  if (tabId === 'cyber') renderCyber();
}
function bindDetailActions(root){
  root.querySelectorAll('[data-filter-layer]').forEach(function(button){
    button.addEventListener('click', function(event){
      event.stopPropagation();
      catalogState.lane = button.dataset.filterLayer;
      var select = document.getElementById('filter-lane');
      if (select) select.value = catalogState.lane;
      renderCatalog();
      closeDetail();
      switchTab('catalog');
    });
  });
}
function bindSvgTooltips(root){
  root.querySelectorAll('[data-kind][data-id]').forEach(function(node){
    if (node.dataset.kind === 'arc') return;
    node.addEventListener('mousemove', function(event){
      var kind = node.dataset.kind;
      var id = node.dataset.id;
      showTip(event, '<b>' + esc(kindLabel(kind) + ': ' + truncate(itemTitle(id), 72)) + '</b><span class="small">' + esc(id) + '</span>');
    });
    node.addEventListener('mouseleave', hideTip);
  });
}
function showTip(event, html){
  var tip = document.getElementById('tooltip');
  tip.innerHTML = html;
  tip.style.left = Math.min(event.clientX + 14, window.innerWidth - 360) + 'px';
  tip.style.top = Math.min(event.clientY + 14, window.innerHeight - 160) + 'px';
  tip.classList.add('show');
}
function hideTip(){
  document.getElementById('tooltip').classList.remove('show');
}

/* v0.33 shared presentation and navigation. No semantic overrides of the JSON. */
var atlasRestoring = true;
var atlasReturnFocus = null;
var atlasReady = false;
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
 var reset=document.getElementById('cyber-reset');if(reset)reset.onclick=function(){Object.assign(cyberState,{mode:'core',role:'',jurisdiction:'',domain:'',force:'',stage:'',authority:'',principalOnly:false,showLinks:true});Object.assign(behaviorState,{subdomain:'all',track:'',mechanism:''});renderCyber();};
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
 var future=String(e.date||'')>'2026-09-05';
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
 var periods=[{id:'y2025',label:'2025'},{id:'h1',label:tx('2026 · январь–июнь','2026 · January–June')},{id:'h2',label:tx('2026 · июль–5 сентября / будущие сроки','2026 · July–5 September / future deadlines')}];
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
 bindAtlasCards(grid);bindCyberHover(grid,edges);renderBehaviorLayer(events,all);renderCyberThreads(events);renderCyberEdgeList(events);requestAnimationFrame(drawCyberLinks);writeAtlasHash();
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
 if(e.current_state){var s=e.current_state;html+='<section class="block state-card"><h3>'+tx('Наблюдение состояния · ','State observed · ')+esc(s.observed_at)+'</h3><p>'+esc(lf(s,'summary'))+'</p><p class="small">'+tx('Дата анонса: ','Announcement date: ')+esc(e.date)+'. '+tx('Дата первого выпуска весов не установлена. Наблюдение не переносится на июльскую точку.','First weight-release date is not established. This observation does not backdate availability to July.')+'</p></section>';}
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
 [['c.',cyberState],['b.',behaviorState],['f.',activeFacts()],['g.',graphState]].forEach(function(pair){Object.keys(pair[1]).sort().forEach(function(k){var v=pair[1][k];if(v!==''&&v!=null)p.set(pair[0]+k,String(v));});});
 if(currentDetail){p.set('kind',currentDetail.kind||currentDetail.k);p.set('id',currentDetail.id);if((currentDetail.kind||currentDetail.k)==='event')p.set('event',currentDetail.id);}
 var hash='#'+p.toString();if(location.hash!==hash){try{history.replaceState(null,'',hash);}catch(e){/* embedding sandboxes may prohibit history */}}
 document.querySelectorAll('a[data-language-link]').forEach(function(a){a.hash=hash;});
}
function restoreAtlasHash(){
 atlasRestoring=true;
 var raw=location.hash.slice(1),p=new URLSearchParams(raw.includes('=')?raw:''),tab=p.get('tab')||(raw&&!raw.includes('=')?raw:'');
 [['c.',cyberState],['b.',behaviorState],['f.',activeFacts()],['g.',graphState]].forEach(function(pair){Object.keys(pair[1]).forEach(function(k){if(!p.has(pair[0]+k))return;var v=p.get(pair[0]+k);pair[1][k]=typeof pair[1][k]==='boolean'?v==='true':v;});});
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

document.getElementById('modal').addEventListener('click', function(event){
  if (event.target.dataset.close) closeDetail();
});
document.getElementById('detail-back').addEventListener('click', goBackDetail);
document.addEventListener('keydown', function(event){
  if (event.key === 'Escape') closeDetail();
});
var footerArcCount = D.connectivity.computed_arc_count || D.summary.total_arcs;
document.getElementById('footer').innerHTML = '<b>' + esc(D.meta.display_title_ru || D.meta.title) + '</b><br>' +
  'Собрано из <code>' + esc(D.meta.source_pack) + '</code>. ' +
  'Связность: ' + esc(footerArcCount) + ' ' + ruPlural(footerArcCount, 'дуга', 'дуги', 'дуг') + ', висящих: ' + esc((D.connectivity.computed_hanging_arcs || []).length) + '. ' +
  'Целостность ссылок: проверено ' + esc(D.referenceIntegrity.checked_references) + ', неразрешённых: ' + esc(D.referenceIntegrity.unresolved_count) + '.<br>' +
  'В набор входят атомарные факты, проверяемые тезисы, сюжетные связи и ограничения формулировок.';

initHeader();
initNav();
renderDashboard();
initGraphControls();
renderStoryMap();
renderRecipes();
renderTimeline();
initCyberControls();
renderCyber();
initCatalogFilters();
renderCatalog();
renderStack();
renderActors();
renderClaims();
renderSources();
bindClickable(document.getElementById('thesis-grid'));
initAtlasReview();
