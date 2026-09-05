var ATLAS_RU=false;

var D = JSON.parse(document.getElementById('DATA').textContent);
var EV = D.events || [], ARCS = D.arcs || [], FAMILIES = D.arcFamilies || [], EDGES = D.edges || [], CLAIMS = D.claims || [], CHECKS = D.claimChecks || [], THESIS = D.thesisNodes || [], COUNTERS = D.counterarguments || [], GAPS = D.gaps || [], SOURCES = D.sourceIndex || [], SOURCE_GROUPS = D.sourceGroups || [];
var CYBER_FRAMEWORK = D.cyberFramework || {};
var byEvent = Object.fromEntries(EV.map(function(x){ return [x.id,x]; }));
var byArc = Object.fromEntries(ARCS.map(function(x){ return [x.id,x]; }));
var byFamily = Object.fromEntries(FAMILIES.map(function(x){ return [x.id,x]; }));
var byEdge = Object.fromEntries(EDGES.map(function(x){ return [x.id,x]; }));
var byClaim = Object.fromEntries(CLAIMS.map(function(x){ return [x.id,x]; }));
var byCheck = Object.fromEntries(CHECKS.map(function(x){ return [x.id,x]; }));
var byThesis = Object.fromEntries(THESIS.map(function(x){ return [x.id,x]; }));
var byCounter = Object.fromEntries(COUNTERS.map(function(x){ return [x.id,x]; }));
var byGap = Object.fromEntries(GAPS.map(function(x){ return [x.id,x]; }));
var palette = ['#365f9d','#107052','#a66f13','#6b4aa2','#a1412b','#24727a','#a34869','#46535f','#2f7161','#8b5f20','#5164a3','#8d4f75','#5c6974'];
var relationColors = {supports:'#107052',supports_with_scope:'#24727a',supports_but_limits:'#a66f13',supports_counterargument:'#6b4aa2',challenges:'#a1412b',challenges_overclaim:'#a1412b',walks_back:'#a66f13',updates:'#365f9d',sets_up:'#46535f',develops_into:'#365f9d',escalates:'#a34869',countermove:'#6b4aa2',routes_around:'#24727a',mitigates:'#107052',limits:'#a66f13',qualifies:'#a66f13',refines:'#365f9d',parallel:'#46535f',generalizes:'#365f9d',institutionalizes:'#107052',reframes:'#6b4aa2',supports_arc:'#107052',key_node:'#46535f',part_of_arc:'#747c85',weakens:'#a66f13'};
var graphState = { showAuto:false, preset:'', family:'', arc:'', relation:'' };
var factState = { q:'', jurisdiction:'', actor:'', family:'', layer:'', year:'', arc:'', status:'', confidence:'', region:'', location:'', institution:'', geoContext:'', geoScope:'', actorType:'', actorJurisdiction:'', source:'' };
var cyberState = { mode:'core', role:'', jurisdiction:'', principalOnly:false, showLinks:true };
var cyberRenderedEvents = [];
var cyberThreadArcIds = ['ARC_CYBER_CLAIM_TO_CAVEAT','ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK','ARC_COGSEC_LAB_TO_WILD_TO_STATE','ARC_QUIET_ACCESS_CONTROL','ARC_FINANCE_GOVERNED_SHUTDOWN','ARC_RUSSIA_SELECTIVE_SOVEREIGNTY'];
var detailHistory = [];
var currentDetail = null;
function esc(v){ return String(v == null ? '' : v).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }
function arr(v){ return Array.isArray(v) ? v : (v ? [v] : []); }
function uniq(v){ return Array.from(new Set((v || []).filter(Boolean))); }
function trunc(v,n){ var s=String(v||''); return s.length>n?s.slice(0,n-1)+'...':s; }
function tag(v){ return v ? '<span class="tag">'+esc(v)+'</span>' : ''; }
function tags(v){ return arr(v).filter(Boolean).slice(0,5).map(tag).join(''); }
function statusLabel(v){ return ({verified:'Verified',verified_adopted_future_application:'Adopted; future application',verified_as_announcement:'Verified as an announcement',verified_as_reported:'Verified as reported',verified_as_reported_indictment_allegation:'Verified as an indictment allegation',verified_as_reported_not_primary_order:'Verified as reported; primary order unavailable',verified_as_reported_with_redacted_forensics:'Verified from redacted forensics',verified_as_speech_not_as_fact:'Speech verified; underlying claim unverified',verified_controlled_evaluation:'Verified controlled evaluation',verified_current_rule:'Verified current rule',verified_malicious_registry_artifacts_no_victim_prevalence:'Malicious artifacts verified; victim prevalence unknown',verified_preprint:'Verified as a preprint',verified_announcement_implementation_pending:'Announcement verified; implementation pending',verified_announcement_details_pending:'Announcement verified; details and capability pending',verified_mou_not_deployment:'MOU verified; deployment not established',verified_policy_decision_technical_detail_reported:'Policy decision verified; technical detail partly reported',reported_findings_independent_validation_pending:'Project findings reported; independent validation pending',verified_first_party_disclosure_independent_forensics_pending:'First-party victim disclosure verified; independent forensics pending',verified_first_party_operational_account:'First-party operational account verified; detailed logs unavailable',verified_preview_license_pending:'Technical report and preview verified; license pending',proposal_not_enacted:'Proposal; not enacted',verified_vendor_announcement:'Verified vendor announcement',verified_report_with_older_data_vintage:'Report verified; older data vintage',verified_public_exposure_not_compromise:'Public exposure; not compromise',verified_program_not_outcome:'Program verified; outcome not claimed',partially_verified:'Partially verified',partially_verified_contested:'Partially verified; contested',partially_verified_compliance_contested:'Partially verified; compliance contested',partially_verified_material_update:'Partially verified; materially updated',controlled_real_world_and_internal_red_team_no_wild_campaign:'Controlled and internal red team; no wild campaign',controlled_real_world_validation_no_wild_campaign:'Controlled validation; no wild campaign',reproducible_poc_no_wild_exploitation:'Reproducible PoC; no wild exploitation',lab_verified_no_wild_exploitation:'Lab verified; no wild exploitation',reproducible_self_authored_preprint_synthetic:'Self-authored reproducible preprint; synthetic',advertisement_verified_implementation_unverified:'Advertisement verified; implementation unverified',reported_unconfirmed:'Reported; unconfirmed',disputed_capability_claim:'Disputed capability claim',disputed_specific_claim_valid_general_mechanism:'Specific claim disputed; general mechanism valid'})[v] || String(v||'').replace(/_/g,' '); }
function statusShort(v){ if(v==='proposal_not_enacted') return 'Proposal'; if(v==='verified_announcement_implementation_pending'||v==='verified_announcement_details_pending') return 'Announcement'; if(v==='verified_mou_not_deployment') return 'MOU'; if(v==='verified_preview_license_pending') return 'Preview'; if(v==='verified_public_exposure_not_compromise') return 'Exposure'; if(v==='verified_report_with_older_data_vintage') return 'Report'; if(v==='reported_findings_independent_validation_pending') return 'Reported'; if(String(v).indexOf('verified')===0) return 'Verified'; if(String(v).indexOf('partially_verified')===0) return 'Partial'; if(String(v).indexOf('controlled_')===0) return 'Controlled'; if(v==='reproducible_poc_no_wild_exploitation') return 'PoC'; if(v==='lab_verified_no_wild_exploitation') return 'Lab'; if(v==='reproducible_self_authored_preprint_synthetic') return 'Self-authored'; if(v==='advertisement_verified_implementation_unverified') return 'Advertisement'; if(String(v).indexOf('disputed')===0) return 'Disputed'; if(v==='reported_unconfirmed') return 'Reported'; return String(v||'').replace(/_/g,' '); }
function dateBasisLabel(v){ return ({public_disclosure_date:'public disclosure date',public_disclosure_date_incident_date_not_disclosed:'public disclosure date; incident date not disclosed',public_beta_start_date:'public beta start',final_model_and_model_card_release_date:'final model/model-card release',product_launch_date:'product launch',license_announcement_date:'license announcement',law_enactment_date:'law enactment',official_report_release_date:'official report release',final_rule_effective_date:'final rule effective date',commission_proposal_publication_date:'Commission proposal publication',commission_action_plan_publication_date:'Commission action-plan publication',framework_contract_award_month:'framework-contract award month',european_parliament_report_adoption_date:'European Parliament report adoption',vendor_general_availability_announcement_date:'vendor general-availability announcement',commission_program_status_update_date:'Commission program-status update',qualification_framework_release_date:'qualification framework release',alliance_strategy_publication_date:'alliance strategy publication',preprint_publication_date:'preprint publication',internet_measurement_snapshot_date:'internet-measurement snapshot',security_vendor_report_publication_date:'security-vendor report publication',program_announcement_date:'program announcement',law_adoption_and_promulgation_date:'law adoption and promulgation',technical_preview_launch_date:'technical preview launch',service_announcement_date:'service announcement',waitlist_removal_date:'waitlist removal',agency_complaint_date:'agency complaint filing',public_event_date:'public event date',intergovernmental_agreement_signing_date:'intergovernmental agreement signing',head_of_state_speech_and_pledge_date:'head-of-state speech and pledge',model_preview_announcement_date:'model preview announcement',ministerial_policy_briefing_date:'ministerial policy briefing',government_mou_announcement_date:'government MOU announcement',phase_one_evaluation_announcement_date:'phase-one evaluation announcement',mou_signing_date:'MOU signing',first_results_announcement_date:'first-results announcement'})[v] || String(v||'').replace(/_/g,' '); }
function dateStatusLabel(v){ if(String(v).indexOf('scheduled_as_of_')===0) return 'scheduled as of '+String(v).replace('scheduled_as_of_',''); return String(v||'').replace(/_/g,' '); }
function moneyStatusLabel(v){ return ({contract_ceiling:'framework contract ceiling'})[v] || String(v||'').replace(/_/g,' '); }
function evidenceContextLabel(v){ return ({community_registries:'Community registries',controlled_real_world_targets:'Controlled real-world targets',laboratory:'Laboratory','nine-country sample':'Nine-country sample',public_registries:'Public registries',synthetic_evaluation:'Synthetic evaluation',underground_market:'Underground market',undisclosed_red_team_client:'Undisclosed red-team client',undisclosed_victim:'Undisclosed victim',undisclosed_victims:'Undisclosed victims'})[v] || String(v||'').replace(/_/g,' '); }
function confidenceLabel(v){ return v==='D_for_capability_claim_B_for_speech_event' ? 'D for capability claim / B for speech event' : String(v||'').replace(/_/g,' '); }
function host(url){ try { return new URL(url).hostname.replace(/^www\./,''); } catch(e) { return url || ''; } }
function arcTitle(a){ a = typeof a === 'string' ? byArc[a] : a; return (a && (a.title_en || a.title || a.id)) || ''; }
function familyTitle(f){ f = typeof f === 'string' ? byFamily[f] : f; return (f && (f.label_en || f.label || f.id)) || ''; }
function actorTypeLabel(v){ return (D.actorTypeLabels && D.actorTypeLabels[v] && (D.actorTypeLabels[v].label_en || D.actorTypeLabels[v].label)) || String(v||'').replace(/_/g,' '); }
function thesisLabel(t){ t = typeof t === 'string' ? byThesis[t] : t; return (t && (t.label_en || t.label || t.id)) || ''; }
function thesisSummary(t){ t = typeof t === 'string' ? byThesis[t] : t; return (t && (t.summary_en || t.summary || '')) || ''; }
function laneLabel(id){ var lane = (D.visualLanes || []).find(function(x){ return x.id === id; }); return (lane && (lane.label_en || lane.label)) || id; }
function laneNote(id){ var lane = (D.visualLanes || []).find(function(x){ return x.id === id; }); return (lane && (lane.notes_en || lane.notes)) || ''; }
function relationColor(r){ return relationColors[r] || '#46535f'; }
function arcColor(id){ var i=ARCS.findIndex(function(a){return a.id===id;}); return palette[((i%palette.length)+palette.length)%palette.length]; }
function edgeArcId(e){ if(byArc[e.arc_id]) return e.arc_id; if(byArc[e.source]) return e.source; if(byArc[e.target]) return e.target; return ''; }
function edgeArcColor(e){ var id=edgeArcId(e); return id ? arcColor(id) : relationColor(e.relation); }
function edgeTitle(e){ return [arcTitle(edgeArcId(e)), String(e.relation||'').replace(/_/g,' '), e.summary_en||e.summary||e.summary_ru].filter(Boolean).join(' · '); }
function defaultEdge(e){ return !e.is_auto && e.style !== 'thin' && !String(e.id).startsWith('AUTO_'); }
function graphEdges(){
  var preset=(D.recipes||[]).find(function(item){return item.id===graphState.preset;});
  var allowedArcs=preset&&preset.recommended_arc_ids?preset.recommended_arc_ids:null;
  var allowedRelations=preset&&preset.recommended_relations?preset.recommended_relations:null;
  var filters=(preset&&preset.recommended_filters)||{};
  var allowedStyles=filters.edge_styles||null, hiddenArcs=filters.hide_arc_ids||[], minStrength=filters.min_strength?strengthRank(filters.min_strength):0;
  return EDGES.filter(function(e){
    if(!graphState.showAuto && !defaultEdge(e)) return false;
    if(!graphState.preset && !graphState.family && !graphState.arc && byArc[e.arc_id] && byArc[e.arc_id].arc_kind==='phase') return false;
    if(graphState.family && e.arc_family_id!==graphState.family) return false;
    if(graphState.arc && e.arc_id!==graphState.arc) return false;
    if(graphState.relation && e.relation!==graphState.relation) return false;
    if(allowedArcs && allowedArcs.indexOf(e.arc_id)===-1) return false;
    if(allowedRelations && allowedRelations.indexOf(e.relation)===-1) return false;
    if(allowedStyles && allowedStyles.indexOf(e.style)===-1) return false;
    if(hiddenArcs.indexOf(e.arc_id)!==-1) return false;
    if(minStrength && strengthRank(e.strength)<minStrength) return false;
    return true;
  });
}
function graphArcs(){
  var preset=(D.recipes||[]).find(function(item){return item.id===graphState.preset;});
  var allowedArcs=preset&&preset.recommended_arc_ids?preset.recommended_arc_ids:null;
  var hiddenArcs=(preset&&preset.recommended_filters&&preset.recommended_filters.hide_arc_ids)||[];
  return ARCS.filter(function(a){
    if(!graphState.preset && !graphState.family && !graphState.arc && a.arc_kind==='phase') return false;
    if(graphState.family && a.family_id!==graphState.family) return false;
    if(graphState.arc && a.id!==graphState.arc) return false;
    if(allowedArcs && allowedArcs.indexOf(a.id)===-1) return false;
    if(hiddenArcs.indexOf(a.id)!==-1) return false;
    return true;
  });
}
function factsForArc(arc){
  var ids=new Set(arr(arc.key_nodes).filter(function(id){return Boolean(byEvent[id]);}));
  EDGES.forEach(function(e){
    if(e.arc_id!==arc.id) return;
    if(byEvent[e.source]) ids.add(e.source);
    if(byEvent[e.target]) ids.add(e.target);
  });
  return Array.from(ids).map(function(id){return byEvent[id];}).sort(function(a,b){return String(a.date||'').localeCompare(String(b.date||''))||a.id.localeCompare(b.id);});
}
function storyBounds(){
  var years=arr(D.summary.years).map(Number).filter(Number.isFinite);
  if(!years.length) years=EV.map(function(e){return Number(String(e.date||'').slice(0,4));}).filter(Number.isFinite);
  return {min:Math.min.apply(null,years),max:Math.max.apply(null,years)};
}
function storyDateX(date,minYear,maxYear,startX,endX){
  var value=String(date||''),year=Number(value.slice(0,4))||minYear,month=Number(value.slice(5,7))||1,day=Number(value.slice(8,10))||1;
  var start=Date.UTC(minYear,0,1),end=Date.UTC(maxYear+1,0,1),current=Date.UTC(year,month-1,day);
  return startX+((current-start)/Math.max(1,end-start))*(endX-startX);
}
function strengthRank(v){ return {low:1,medium:2,high:3}[v] || 0; }
function edgeTouchesThesis(e){ return e.target_kind === 'synthetic_thesis' || e.source_kind === 'synthetic_thesis' || byThesis[e.target] || byThesis[e.source]; }
function edgeTouchesStoryArc(e){ return e.source_kind === 'story_arc' || e.target_kind === 'story_arc' || byArc[e.source] || byArc[e.target]; }
function edgeArcOrder(e){ var i=ARCS.findIndex(function(a){return a.id===e.arc_id || a.id===e.source || a.id===e.target;}); return i<0?9999:i; }
function edgePriority(e){ var rs={supports:8,supports_with_scope:7,supports_but_limits:7,challenges_overclaim:6,walks_back:6,refines:5,qualifies:5}[e.relation]||3; return (edgeTouchesStoryArc(e)?100:0)+strengthRank(e.strength)*10+rs-(e.is_auto?20:0); }
function displayedThesisEdges(edges){ var byPair=new Map(); edges.filter(function(e){return edgeTouchesThesis(e)&&edgeTouchesStoryArc(e);}).sort(function(a,b){return edgePriority(b)-edgePriority(a)||edgeArcOrder(a)-edgeArcOrder(b);}).forEach(function(e){var thesisId=byThesis[e.target]?e.target:e.source,pair=edgeArcId(e)+'|'+thesisId;if(!byPair.has(pair))byPair.set(pair,e);});return Array.from(byPair.values()).sort(function(a,b){return edgeArcOrder(a)-edgeArcOrder(b)||edgePriority(b)-edgePriority(a);}); }
function kind(id){ if(byEvent[id]) return 'event'; if(byArc[id]) return 'arc'; if(byEdge[id]) return 'edge'; if(byClaim[id]) return 'claim'; if(byCheck[id]) return 'check'; if(byThesis[id]) return 'thesis'; if(byCounter[id]) return 'counterargument'; if(byGap[id]) return 'gap'; return ''; }
function titleOf(id){ return (byEvent[id]&&byEvent[id].title)||(byArc[id]&&arcTitle(id))||(byEdge[id]&&(byEdge[id].summary_en||byEdge[id].summary))||(byClaim[id]&&(byClaim[id].claim||byClaim[id].title))||(byCheck[id]&&byCheck[id].claim)||(byThesis[id]&&thesisLabel(id))||(byCounter[id]&&(byCounter[id].objection||byCounter[id].title))||(byGap[id]&&(byGap[id].topic||byGap[id].title))||id; }
function linkButton(id){ var k=kind(id); return k ? '<button class="btn" data-kind="'+esc(k)+'" data-id="'+esc(id)+'">'+esc(trunc(titleOf(id),58))+'</button>' : tag(id); }
function renderHeader(){
  document.getElementById('subtitle').textContent = D.meta.subtitle || 'A research atlas of AI stack power.';
  document.getElementById('top-pills').innerHTML = ['v'+D.meta.version,D.summary.total_events+' facts',D.summary.total_claims+' claims',D.summary.total_edges+' edges'].map(tag).join('');
  document.getElementById('footer').innerHTML = '<b>'+esc(D.meta.title)+'</b><br>Source pack: <code>'+esc(D.meta.source_pack)+'</code>. Connectivity: '+esc(D.connectivity.computed_arc_count || D.summary.total_arcs)+' arcs, hanging: '+esc((D.connectivity.computed_hanging_arcs || []).length)+'. Reference integrity: '+esc(D.referenceIntegrity.checked_references)+' checked, '+esc(D.referenceIntegrity.unresolved_count)+' unresolved. JSON: <a href="ai_power_storygraph_en.json">ai_power_storygraph_en.json</a>.';
}
function renderNav(){
  var tabs=[['overview','Overview'],['story','Story map'],['cyber','Cyber 2025–26'],['timeline','Timeline'],['stack','Stack'],['facts','Facts'],['claims','Claims'],['sources','Sources']];
  document.getElementById('nav').innerHTML=tabs.map(function(t,i){return '<button type="button" class="'+(i?'':'active')+'" data-tab="'+t[0]+'">'+t[1]+'</button>';}).join('');
  document.querySelectorAll('#nav button').forEach(function(b){ b.onclick=function(){ switchTab(b.dataset.tab); }; });
}



function cyberDomainMeta(id){return cyberDomains().find(function(item){return item.id===id;})||{id:id,label_en:id,short_en:''};}
function cyberRoleMeta(id){return arr(CYBER_FRAMEWORK.roles).find(function(item){return item.id===id;})||{id:id,short_en:id};}

function cyberRoleClass(id){if(id==='AI_ROLE_PROTECTED_SYSTEM')return'protected';if(id==='AI_ROLE_DEFENSIVE_TOOL')return'defence';return'attack';}
function cyberPeriod(event){ var date=String(event.date||''); if(date.slice(0,4)==='2025') return 'y2025'; return (Number(date.slice(5,7))||1)<=6?'h1':'h2'; }
function cyberDirectEdges(events){ var ids=new Set((events||[]).map(function(event){return event.id;})); return EDGES.filter(function(edge){return byEvent[edge.source]&&byEvent[edge.target]&&ids.has(edge.source)&&ids.has(edge.target)&&!edge.is_auto&&!String(edge.id||'').startsWith('AUTO_');}); }






function renderCyberThreads(events){
  var rows=cyberThreadArcIds.map(function(arcId){var items=events.filter(function(event){return arr(event.arcIds).indexOf(arcId)!==-1;}).sort(function(a,b){return String(a.date||'').localeCompare(String(b.date||''));});return {arcId:arcId,items:items};}).filter(function(row){return row.items.length>1&&byArc[row.arcId];}),root=document.getElementById('cyber-threads');
  root.innerHTML=rows.length?rows.map(function(row){var track=row.items.map(function(event,index){return (index?'<span class="cyber-thread-arrow">→</span>':'')+'<button type="button" class="cyber-thread-event" data-kind="event" data-id="'+esc(event.id)+'"><time>'+esc(event.date||'undated')+'</time><span>'+esc(trunc(event.title,68))+'</span></button>';}).join('');return '<div class="cyber-thread"><div class="cyber-thread-title"><b>'+esc(arcTitle(row.arcId))+'</b><span>'+row.items.length+' facts · shared arc, not a proven causal chain</span></div><div class="cyber-thread-track">'+track+'</div></div>';}).join(''):'<div class="cyber-empty">The current slice has no shared arc with at least two facts.</div>';
  bindClicks(root);
}
function renderCyberEdgeList(events){
  var edges=cyberDirectEdges(events),root=document.getElementById('cyber-edge-list');
  root.innerHTML=edges.length?edges.map(function(edge){return '<article class="cyber-edge-item" data-kind="edge" data-id="'+esc(edge.id)+'"><div class="id">'+esc(edge.relation)+' · '+esc(edge.id)+'</div><div class="cyber-edge-path"><span>'+esc(trunc(titleOf(edge.source),54))+'</span><i>→</i><span>'+esc(trunc(titleOf(edge.target),54))+'</span></div><p class="small" style="margin-top:7px">'+esc(edge.summary_en||edge.summary||'')+'</p></article>';}).join(''):'<div class="cyber-empty">The current slice has no explicit event-to-event edge. Shared mechanisms are shown separately above.</div>';
  bindClicks(root);
}
function drawCyberLinks(){
  var svg=document.getElementById('cyber-links'),board=document.getElementById('cyber-board');if(!svg||!board)return;if(!cyberState.showLinks){svg.innerHTML='';return;}var boardRect=board.getBoundingClientRect();if(!boardRect.width||!boardRect.height)return;
  var cards=Array.from(board.querySelectorAll('.cyber-event')),cardById={};cards.forEach(function(card){cardById[card.dataset.id]=card;});var edges=cyberDirectEdges(cyberRenderedEvents).filter(function(edge){return cardById[edge.source]&&cardById[edge.target];});
  svg.setAttribute('viewBox','0 0 '+boardRect.width+' '+boardRect.height);svg.setAttribute('width',boardRect.width);svg.setAttribute('height',boardRect.height);
  svg.innerHTML=edges.map(function(edge){var sourceRect=cardById[edge.source].getBoundingClientRect(),targetRect=cardById[edge.target].getBoundingClientRect(),sx=sourceRect.left-boardRect.left+sourceRect.width/2,sy=sourceRect.top-boardRect.top+sourceRect.height/2,tx=targetRect.left-boardRect.left+targetRect.width/2,ty=targetRect.top-boardRect.top+targetRect.height/2,bend=Math.max(34,Math.abs(tx-sx)*.45),c1x=sx+(tx>=sx?bend:-bend),c2x=tx-(tx>=sx?bend:-bend);return '<path class="cyber-link" data-edge-id="'+esc(edge.id)+'" d="M'+sx.toFixed(1)+','+sy.toFixed(1)+' C'+c1x.toFixed(1)+','+sy.toFixed(1)+' '+c2x.toFixed(1)+','+ty.toFixed(1)+' '+tx.toFixed(1)+','+ty.toFixed(1)+'" stroke="'+esc(relationColor(edge.relation))+'"'+(edge.style==='dashed'?' stroke-dasharray="6 5"':'')+'/>';}).join('');
}
function bindCyberHover(root,edges){
  var cards=Array.from(root.querySelectorAll('.cyber-event'));cards.forEach(function(card){card.onmouseenter=function(){var related=edges.filter(function(edge){return edge.source===card.dataset.id||edge.target===card.dataset.id;}),connected=new Set();related.forEach(function(edge){connected.add(edge.source);connected.add(edge.target);});cards.forEach(function(item){item.classList.toggle('is-active',item===card);item.classList.toggle('is-connected',item!==card&&connected.has(item.dataset.id));item.classList.toggle('is-dimmed',related.length>0&&!connected.has(item.dataset.id));});document.querySelectorAll('#cyber-links [data-edge-id]').forEach(function(path){var active=related.some(function(edge){return edge.id===path.dataset.edgeId;});path.classList.toggle('is-active',active);path.classList.toggle('is-dimmed',related.length>0&&!active);});};card.onmouseleave=function(){cards.forEach(function(item){item.classList.remove('is-active','is-connected','is-dimmed');});document.querySelectorAll('#cyber-links [data-edge-id]').forEach(function(path){path.classList.remove('is-active','is-dimmed');});};});
}
function _legacySwitchTab(id){ if(!document.getElementById('view-'+id)) return; document.querySelectorAll('#nav button').forEach(function(b){ b.classList.toggle('active',b.dataset.tab===id); }); document.querySelectorAll('.view').forEach(function(v){ v.classList.toggle('active',v.id==='view-'+id); });  if(id==='story') renderStory('story-svg'); if(id==='cyber') renderCyber(); if(id==='timeline') renderTimeline(); }

function moneyB(value){ var n=Number(value||0); if(!n) return '$0B'; if(n>=1000) return '$'+(n/1000).toFixed(n%1000?2:0)+'T'; return '$'+(n>=100?Math.round(n):n.toFixed(n>=10?1:2).replace(/0$/,'').replace(/\.0$/,''))+'B'; }
function renderCapitalLedger(){
  var section=document.getElementById('capital-ledger-section'), ledger=D.summary.capital_ledger||{};
  if(!section) return;
  if(!ledger.announcement_rows){ section.style.display='none'; return; }
  var totals=ledger.announcement_totals_usd_billion||{};
  var keys=Object.keys(totals).filter(function(k){return k!=='Total';});
  document.getElementById('capital-totals').innerHTML=keys.concat(['Total']).filter(function(k){return totals[k]!=null;}).map(function(k){return '<div class="stat"><b>'+esc(moneyB(totals[k]))+'</b><span>'+esc(k==='Total'?'included total':k)+'</span></div>';}).join('');
  var wantedSpent=[['Global','Global corporate AI investment','2025'],['Global','Private AI investment subset','2025'],['US','Private AI investment','2025'],['China','Private AI investment','2025'],['China','Government venture funds into AI companies, cumulative','2000-2023'],['US','Google AI infrastructure capex','2025']];
  var spent=wantedSpent.map(function(m){return (ledger.spent_rows||[]).find(function(r){return r.region_en===m[0]&&r.metric_en===m[1]&&r.period===m[2];});}).filter(Boolean);
  var announced=(ledger.announcement_rows||[]).filter(function(r){return r.include_in_total;}).slice(0,10);
  var rows=spent.map(function(r){return '<tr><td>spent</td><td>'+esc(r.region_en||'')+'</td><td>'+esc(r.metric_en||'')+'</td><td>'+esc(r.period||'')+'</td><td><b>'+esc(moneyB(r.amount_usd_billion).replace('$','').replace('B',''))+'</b></td><td>'+esc(statusLabel(r.status||''))+'</td></tr>';}).join('')+
    announced.map(function(r){return '<tr><td>announced</td><td>'+esc(r.region_en||'')+'</td><td>'+esc(r.initiative_en||'')+'</td><td>'+esc(r.horizon_en||'')+'</td><td><b>'+esc(moneyB(r.amount_usd_billion).replace('$','').replace('B',''))+'</b></td><td>'+esc(statusLabel(r.status||''))+'</td></tr>';}).join('');
  document.getElementById('capital-table').innerHTML='<thead><tr><th>Mode</th><th>Region</th><th>Line</th><th>Period</th><th>$B</th><th>Status</th></tr></thead><tbody>'+rows+'</tbody>';
}
function initGraphControls(){
  document.getElementById('family-select').innerHTML='<option value="">Family: all</option>'+FAMILIES.map(function(f){return '<option value="'+esc(f.id)+'">'+esc(familyTitle(f))+'</option>';}).join('');
  document.getElementById('arc-select').innerHTML='<option value="">Exact arc: all</option>'+ARCS.map(function(a){return '<option value="'+esc(a.id)+'">'+esc(trunc(familyTitle(a.family_id)+' · '+arcTitle(a),78))+'</option>';}).join('');
  document.getElementById('relation-select').innerHTML='<option value="">Relation: all</option>'+Object.keys(D.relationTypes||{}).sort().map(function(r){return '<option value="'+esc(r)+'">'+esc(r.replace(/_/g,' '))+'</option>';}).join('');
  document.getElementById('toggle-auto').onclick=function(){ graphState.showAuto=!graphState.showAuto; this.classList.toggle('active',graphState.showAuto); this.textContent=graphState.showAuto?'Hide auto/thin links':'Show auto/thin links'; renderStory('story-svg'); };
  document.getElementById('family-select').onchange=function(){ graphState.preset=''; graphState.family=this.value; graphState.arc=''; document.getElementById('arc-select').value=''; renderStory('story-svg'); renderRecipes(); };
  document.getElementById('arc-select').onchange=function(){ graphState.preset=''; graphState.arc=this.value; if(this.value){ graphState.family=(byArc[this.value]&&byArc[this.value].family_id)||''; document.getElementById('family-select').value=graphState.family; } renderStory('story-svg'); renderRecipes(); };
  document.getElementById('relation-select').onchange=function(){ graphState.preset=''; graphState.relation=this.value; renderStory('story-svg'); renderRecipes(); };
}
function renderStory(id){
  var svg=document.getElementById(id); if(!svg) return;
  var arcs=graphArcs(),rowH=72,top=92,labelX=28,bandStartX=480,bandEndX=1000,pathStartX=1022,thesisX=1138,width=1400,thesisBottom=THESIS.length?150+(THESIS.length-1)*124+58:0,height=Math.max(620,top+arcs.length*rowH+76,thesisBottom),edges=graphEdges(),thesisEdges=displayedThesisEdges(edges),bounds=storyBounds();
  if(document.getElementById('edge-count')) document.getElementById('edge-count').textContent='arc→thesis: '+thesisEdges.length+' · graph: '+edges.length+' / '+EDGES.length;
  var thesisY={}; THESIS.forEach(function(t,i){ thesisY[t.id]=150+i*124; });
  svg.setAttribute('viewBox','0 0 '+width+' '+height);
  var out='<rect width="'+width+'" height="'+height+'" fill="transparent"/><text x="'+labelX+'" y="30" class="svg-label">story arcs</text><text x="'+bandStartX+'" y="30" class="svg-label">facts by event date</text><text x="'+thesisX+'" y="30" class="svg-label">thesis nodes</text>';
  for(var year=bounds.min;year<=bounds.max;year+=1){var yearX=storyDateX(String(year)+'-01-01',bounds.min,bounds.max,bandStartX,bandEndX);out+='<line class="story-grid" x1="'+yearX.toFixed(1)+'" y1="48" x2="'+yearX.toFixed(1)+'" y2="'+(height-36)+'"/><text class="story-year" x="'+(yearX+4).toFixed(1)+'" y="44">'+year+'</text>';}
  out+='<line class="story-grid" x1="'+bandEndX+'" y1="48" x2="'+bandEndX+'" y2="'+(height-36)+'"/>';
  arcs.forEach(function(a,i){
    var y=top+i*rowH,c=arcColor(a.id),facts=factsForArc(a),first=facts[0],last=facts[facts.length-1],firstX=first?storyDateX(first.date,bounds.min,bounds.max,bandStartX,bandEndX):bandStartX,lastX=last?storyDateX(last.date,bounds.min,bounds.max,bandStartX,bandEndX):bandStartX,range=first&&last?String(first.date).slice(0,4)+'-'+String(last.date).slice(0,4):'undated';
    out+='<g class="arc-row" data-kind="arc" data-id="'+esc(a.id)+'"><rect x="16" y="'+(y-30)+'" width="'+(width-38)+'" height="58" rx="8" fill="'+(i%2?'rgba(255,255,255,.26)':'rgba(255,255,255,.48)')+'"/><text x="'+labelX+'" y="'+(y-7)+'" class="arc-title">'+esc(trunc(arcTitle(a),52))+'</text><text x="'+labelX+'" y="'+(y+13)+'" class="arc-sub">'+esc(familyTitle(a.family_id))+' · '+facts.length+' facts · '+range+'</text>'+(facts.length?'<rect class="arc-band" x="'+firstX.toFixed(1)+'" y="'+(y-20)+'" width="'+Math.max(8,lastX-firstX).toFixed(1)+'" height="40" rx="8" fill="'+c+'" opacity=".14"/>':'')+'</g>';
    var levelEnds=[-Infinity,-Infinity,-Infinity,-Infinity,-Infinity],levelOffsets=[-14,-7,0,7,14];
    facts.forEach(function(e){var dotX=storyDateX(e.date,bounds.min,bounds.max,bandStartX,bandEndX),level=levelEnds.findIndex(function(previousX){return dotX-previousX>=10;});if(level<0)level=levelEnds.indexOf(Math.min.apply(null,levelEnds));levelEnds[level]=dotX;var dotY=y+levelOffsets[level],confidence=confidenceClass(e.confidence);out+='<circle class="event-dot '+esc(confidence)+'" data-kind="event" data-id="'+esc(e.id)+'" data-arc="'+esc(a.id)+'" data-date="'+esc(e.date)+'" cx="'+dotX.toFixed(1)+'" cy="'+dotY+'" r="4.7"><title>'+esc(e.date+' · '+e.title)+'</title></circle>';});
  });
  THESIS.forEach(function(t){ var y=thesisY[t.id]; out+='<g data-kind="thesis" data-id="'+esc(t.id)+'"><rect x="'+(thesisX-18)+'" y="'+(y-32)+'" width="238" height="66" rx="10" fill="#fffefa" stroke="rgba(28,32,38,.18)"/><text x="'+(thesisX-2)+'" y="'+(y-8)+'" class="arc-title">'+esc(trunc(thesisLabel(t),30))+'</text><text x="'+(thesisX-2)+'" y="'+(y+12)+'" class="arc-sub">'+esc(t.id)+'</text></g>'; });
  thesisEdges.forEach(function(e){ var ai=arcs.findIndex(function(a){return a.id===edgeArcId(e);});if(ai<0)return;var y1=top+ai*rowH-8,tid=byThesis[e.target]?e.target:e.source,y2=thesisY[tid]||120;out+='<path class="edge-path '+esc(e.style||'')+(e.is_auto?' thin':'')+'" data-kind="edge" data-id="'+esc(e.id)+'" data-arc="'+esc(edgeArcId(e))+'" d="M'+pathStartX+','+y1+' C1070,'+y1+' 1085,'+y2+' '+(thesisX-22)+','+y2+'" stroke="'+edgeArcColor(e)+'" opacity="'+(e.is_auto?'.22':'.5')+'"><title>'+esc(edgeTitle(e))+'</title></path>'; });
  svg.innerHTML=out; bindClicks(svg);
}
function renderRecipes(){
  document.getElementById('recipe-list').innerHTML=(D.recipes||[]).map(function(r){return '<button type="button" class="card recipe-card '+(graphState.preset===r.id?'active':'')+'" data-recipe="'+esc(r.id)+'"><div class="id">'+esc(r.id)+'</div><h3>'+esc(r.title_en||r.title||r.id)+'</h3><p class="small">'+esc(r.description_en||r.description||'')+'</p></button>';}).join('');
  document.querySelectorAll('.recipe-card').forEach(function(card){card.onclick=function(){graphState.preset=graphState.preset===card.dataset.recipe?'':card.dataset.recipe;graphState.family='';graphState.arc='';graphState.relation='';document.getElementById('family-select').value='';document.getElementById('arc-select').value='';document.getElementById('relation-select').value='';renderStory('story-svg');renderRecipes();};});
}
function confidenceClass(v){ return String(v || 'D').slice(0,1).toUpperCase(); }
function renderTimeline(){
  var svg=document.getElementById('timeline-svg'); if(!svg) return;
  var lanes=(D.visualLanes&&D.visualLanes.length)?D.visualLanes:[{id:'governance_law',label:'Governance and law'},{id:'energy_compute_chips',label:'Energy, compute and chips'},{id:'model_weights',label:'Models, weights and access'},{id:'decision_support_cognition',label:'Decision support and cognition'}];
  var years=(D.summary.years&&D.summary.years.length)?D.summary.years:[2022,2026], minY=Math.min.apply(null,years), maxY=Math.max.apply(null,years);
  var rowH=70, top=68, left=250, width=1240, height=Math.max(720,top+lanes.length*rowH+72);
  var laneIds=lanes.map(function(l){return l.id;}), laneIndex=Object.fromEntries(lanes.map(function(l,i){return [l.id,i];}));
  function xFor(date){ var s=String(date||''), y=Number(s.slice(0,4))||minY, m=Number(s.slice(5,7))||1, d=Number(s.slice(8,10))||1, start=Date.UTC(minY,0,1), end=Date.UTC(maxY+1,0,1), cur=Date.UTC(y,m-1,d); return left+((cur-start)/(end-start))*(width-left-54); }
  function lanesFor(e){ var hits=arr(e.stack_layer).filter(function(l){return laneIds.indexOf(l)!==-1;}); return hits.length?hits:[lanes[0].id]; }
  svg.setAttribute('viewBox','0 0 '+width+' '+height);
  var out='<rect width="'+width+'" height="'+height+'" fill="transparent"/>';
  for(var y=minY;y<=maxY+1;y+=1){ var xx=left+((Date.UTC(y,0,1)-Date.UTC(minY,0,1))/(Date.UTC(maxY+1,0,1)-Date.UTC(minY,0,1)))*(width-left-54); out+='<line class="axis" x1="'+xx+'" y1="28" x2="'+xx+'" y2="'+(height-42)+'"/>'; if(y<=maxY) out+='<text class="svg-id" x="'+(xx+5)+'" y="22">'+y+'</text>'; }
  lanes.forEach(function(l,i){ var yy=top+i*rowH; out+='<line class="axis" x1="'+left+'" y1="'+yy+'" x2="'+(width-54)+'" y2="'+yy+'"/><text class="svg-label" x="24" y="'+(yy-6)+'">'+esc(trunc(laneLabel(l.id),34))+'</text><text class="svg-id" x="24" y="'+(yy+13)+'">'+esc(l.id)+'</text>'; });
  var offsets={};
  EV.slice().sort(function(a,b){return String(a.date).localeCompare(String(b.date));}).forEach(function(e){
    lanesFor(e).forEach(function(l){
      var i=laneIndex[l]||0, key=l+'-'+e.date;
      offsets[key]=(offsets[key]||0)+1;
      var c=confidenceClass(e.confidence), r=c==='A'?6:c==='B'?5.4:4.8, xx=xFor(e.date), yy=top+i*rowH-8+Math.min(offsets[key],7)*7;
      out+='<circle class="timeline-dot '+esc(c)+'" data-kind="event" data-id="'+esc(e.id)+'" data-lane="'+esc(l)+'" cx="'+xx.toFixed(1)+'" cy="'+yy.toFixed(1)+'" r="'+r+'"><title>'+esc(laneLabel(l)+': '+e.title)+'</title></circle>';
    });
  });
  svg.innerHTML=out; bindClicks(svg);
}
function renderStack(){
  var years=D.summary.years||[], layers=Object.keys(D.counts.stack_layers||{}).sort(), heat=function(c){return c===0?0:c===1?1:c<=3?2:c<=6?3:c<=10?4:5;};
  var html='<thead><tr><th>Layer</th>'+years.map(function(y){return '<th>'+y+'</th>';}).join('')+'<th>Total</th></tr></thead><tbody>';
  layers.forEach(function(l){ var events=EV.filter(function(e){return arr(e.stack_layer).indexOf(l)!==-1;}); html+='<tr data-kind="layer" data-id="'+esc(l)+'"><td><b>'+esc(laneLabel(l))+'</b><br><span class="id">'+esc(l)+'</span></td>'; years.forEach(function(y){ var c=events.filter(function(e){return e.year===y;}).length; html+='<td class="heat'+heat(c)+'"><b>'+c+'</b></td>'; }); html+='<td><b>'+events.length+'</b></td></tr>'; });
  document.getElementById('stack-table').innerHTML=html+'</tbody>';
  document.getElementById('layer-cards').innerHTML=layers.map(function(l){ var events=EV.filter(function(e){return arr(e.stack_layer).indexOf(l)!==-1;}); return '<article class="card" data-kind="layer" data-id="'+esc(l)+'"><div class="id">'+esc(l)+'</div><h3>'+esc(laneLabel(l))+'</h3><p class="small">'+esc(laneNote(l))+'</p><div>'+tag(events.length+' facts')+'</div></article>'; }).join('');
  bindClicks(document.getElementById('stack-table')); bindClicks(document.getElementById('layer-cards'));
}
function initFilters(){
  function opts(values,label,format){ return '<option value="">'+label+'</option>'+values.map(function(v){return '<option value="'+esc(v)+'">'+esc(format?format(v):v)+'</option>';}).join(''); }
  document.getElementById('filter-jurisdiction').innerHTML=opts(Object.keys(D.counts.jurisdictions||{}).sort(),'Jurisdiction: all');
  document.getElementById('filter-actor').innerHTML=opts(Object.entries(D.counts.actor_entities||{}).map(function(x){return x[0];}).sort(),'Actor: all');
  document.getElementById('filter-family').innerHTML=opts(FAMILIES.map(function(f){return f.id;}),'Story family: all',familyTitle);
  document.getElementById('filter-layer').innerHTML='<option value="">Layer: all</option>'+Object.keys(D.counts.stack_layers||{}).sort().map(function(l){return '<option value="'+esc(l)+'">'+esc(laneLabel(l))+'</option>';}).join('');
  document.getElementById('filter-year').innerHTML=opts((D.summary.years||[]).map(String),'Year: all');
  document.getElementById('filter-arc').innerHTML='<option value="">Exact arc: all</option>'+ARCS.map(function(a){return '<option value="'+esc(a.id)+'">'+esc(trunc(familyTitle(a.family_id)+' · '+arcTitle(a),78))+'</option>';}).join('');
  document.getElementById('filter-status').innerHTML=opts(Object.keys(D.summary.by_status||{}).sort(),'Status: all',statusLabel);
  document.getElementById('filter-confidence').innerHTML=opts(Object.keys(D.summary.by_confidence||{}).sort(),'Confidence: all',confidenceLabel);
  document.getElementById('filter-region').innerHTML=opts(Object.keys(D.counts.regions||{}).sort(),'Region: all');
  document.getElementById('filter-location').innerHTML=opts(Object.keys(D.counts.locations||{}).sort(),'Place / territory: all');
  document.getElementById('filter-institution').innerHTML=opts(Object.keys(D.counts.institutional_scopes||{}).sort(),'Institutional scope: all');
  document.getElementById('filter-geo-context').innerHTML=opts(Object.keys(D.counts.geo_context||{}).sort(),'Context tag: all');
  document.getElementById('filter-geo-scope').innerHTML=opts(Object.keys(D.counts.geographic_scopes||{}).sort(),'Geographic scope: all');
  document.getElementById('filter-actor-type').innerHTML=opts(Object.keys(D.counts.actor_types||{}).sort(),'Actor type: all',actorTypeLabel);
  document.getElementById('filter-actor-jurisdiction').innerHTML=opts(Object.keys(D.counts.actor_jurisdictions||{}).sort(),'Actor jurisdiction: all');
  document.getElementById('filter-source').innerHTML=opts(Object.keys(D.counts.source_types||{}).sort(),'Source: all');
  var map={'filter-jurisdiction':'jurisdiction','filter-actor':'actor','filter-family':'family','filter-layer':'layer','filter-year':'year','filter-arc':'arc','filter-status':'status','filter-confidence':'confidence','filter-region':'region','filter-location':'location','filter-institution':'institution','filter-geo-context':'geoContext','filter-geo-scope':'geoScope','filter-actor-type':'actorType','filter-actor-jurisdiction':'actorJurisdiction','filter-source':'source'};
  Object.keys(map).forEach(function(id){ document.getElementById(id).onchange=function(){ factState[map[id]]=this.value; renderFacts(); }; });
  document.getElementById('search').oninput=function(){ factState.q=this.value.trim().toLowerCase(); renderFacts(); };
  document.getElementById('reset-filters').onclick=function(){ Object.keys(factState).forEach(function(k){factState[k]='';}); document.getElementById('search').value=''; Object.keys(map).forEach(function(id){document.getElementById(id).value='';}); renderFacts(); };
}
function eventText(e){ return [e.id,e.title,e.date,e.actor,e.source_name,e.source_type,e.status,e.confidence,e.claim_supported,e.claim_challenged,arr(e.geography_raw).join(' '),arr(e.jurisdictions).join(' '),arr(e.regions).join(' '),arr(e.locations).join(' '),arr(e.institutional_scopes).join(' '),arr(e.geo_context).join(' '),arr(e.geographic_scopes).join(' '),arr(e.evidence_context).join(' '),arr(e.actors_raw).join(' '),arr(e.actor_entities).join(' '),arr(e.actor_types).join(' '),arr(e.actor_jurisdictions).join(' '),arr(e.stack_layer).join(' '),arr(e.arcIds).join(' '),arr(e.arcFamilyIds).join(' ')].join(' ').toLowerCase(); }
function eventPass(e){ if(factState.q && eventText(e).indexOf(factState.q)===-1) return false; if(factState.jurisdiction && arr(e.jurisdictions).indexOf(factState.jurisdiction)===-1) return false; if(factState.actor && (factState.actor==='__unresolved__'?e.actor_classification_status!=='review_required':arr(e.actor_entities).indexOf(factState.actor)===-1))return false; if(factState.family && arr(e.arcFamilyIds).indexOf(factState.family)===-1) return false; if(factState.layer && arr(e.stack_layer).indexOf(factState.layer)===-1) return false; if(factState.year && String(e.year)!==factState.year) return false; if(factState.arc && arr(e.arcIds).indexOf(factState.arc)===-1) return false; if(factState.status && e.status!==factState.status) return false; if(factState.confidence && e.confidence!==factState.confidence) return false; if(factState.region && arr(e.regions).indexOf(factState.region)===-1) return false; if(factState.location && arr(e.locations).indexOf(factState.location)===-1) return false; if(factState.institution && arr(e.institutional_scopes).indexOf(factState.institution)===-1) return false; if(factState.geoContext && arr(e.geo_context).indexOf(factState.geoContext)===-1) return false; if(factState.geoScope && arr(e.geographic_scopes).indexOf(factState.geoScope)===-1) return false; if(factState.actorType && arr(e.actor_types).indexOf(factState.actorType)===-1) return false; if(factState.actorJurisdiction && arr(e.actor_jurisdictions).indexOf(factState.actorJurisdiction)===-1) return false; if(factState.source && e.source_type!==factState.source) return false; return true; }
function renderFacts(){ var list=EV.filter(eventPass).sort(function(a,b){return String(b.date).localeCompare(String(a.date));}); document.getElementById('fact-count').textContent=list.length+' of '+EV.length+' facts'; document.getElementById('fact-list').innerHTML=list.map(function(e){ return '<article class="row" data-kind="event" data-id="'+esc(e.id)+'"><div class="id">'+esc(e.date)+'<br>'+esc(confidenceLabel(e.confidence))+' · '+esc(statusShort(e.status))+'</div><div><div class="row-title">'+esc(e.title)+'</div><div>'+tag(e.source_type)+arr(e.stack_layer).slice(0,3).map(function(l){return tag(laneLabel(l));}).join('')+tags(e.jurisdictions)+'</div></div><div class="badge">arcs: '+arr(e.arcIds).length+' · edges: '+arr(e.edgeIds).length+'</div></article>'; }).join('') || '<p class="small">No matching facts.</p>'; bindClicks(document.getElementById('fact-list')); }
function renderClaims(){ document.getElementById('check-cards').innerHTML=CHECKS.map(function(c){return '<article class="card" data-kind="check" data-id="'+esc(c.id)+'"><div class="id">'+esc(c.id)+'</div><h3>'+esc(c.claim||c.title)+'</h3><div>'+tag(statusLabel(c.status))+tag(c.confidence)+tag(arr(c.supporting_evidence).length+' facts')+'</div><p class="small">'+esc(c.safe_wording||'')+'</p></article>';}).join(''); document.getElementById('claim-cards').innerHTML=CLAIMS.map(function(c){return '<article class="card" data-kind="claim" data-id="'+esc(c.id)+'"><div class="id">'+esc(c.id)+'</div><h3>'+esc(c.claim||c.title)+'</h3><div>'+tag(statusLabel(c.status))+tag(c.evidence_level||c.confidence)+'</div><p class="small">'+esc(c.recommended_phrasing||'')+'</p></article>';}).join(''); bindClicks(document.getElementById('check-cards')); bindClicks(document.getElementById('claim-cards')); }
function renderSources(){ var groups=SOURCE_GROUPS.length?SOURCE_GROUPS:SOURCES.map(function(s){return {family:s.name||s.title||host(s.url),sources:[s],types:[s.type],used_by:s.used_by||[]};}); document.getElementById('source-list').innerHTML=groups.map(function(g){ var links=arr(g.sources).slice(0,5).map(function(s){ var label=s.name||s.title||host(s.url); return s.url?'<a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(trunc(label,90))+'</a>':esc(label); }).join('<br>'); return '<div class="source-item"><b>'+esc(g.family)+'</b><br><span class="small">'+esc(arr(g.types).slice(0,3).join(', ')||'source')+' · materials: '+arr(g.sources).length+' · uses: '+arr(g.used_by).length+'</span><div class="block">'+links+'</div></div>'; }).join(''); }
function taxonomyDetail(e){ var groups=[['Regions',e.regions],['Places / territories',e.locations],['Institutional scopes',e.institutional_scopes],['Context tags',e.geo_context],['Geographic scope',e.geographic_scopes],['Actors',e.actors],['Actor types',arr(e.actor_types).map(actorTypeLabel)]]; return groups.filter(function(g){return arr(g[1]).length;}).map(function(g){return '<div class="block"><h4>'+esc(g[0])+'</h4>'+tags(g[1])+'</div>';}).join(''); }
function eventMeta(e){ return tag(e.date)+(e.date_basis?tag(dateBasisLabel(e.date_basis)):'')+(e.date_status?tag(dateStatusLabel(e.date_status)):'')+(e.status_update_date?tag('updated: '+e.status_update_date):'')+(e.current_legal_status?tag(e.current_legal_status):'')+(e.money_status?tag(moneyStatusLabel(e.money_status)):'')+tag(confidenceLabel(e.confidence))+tag(statusLabel(e.status))+tag(e.source_type)+tags(e.jurisdictions); }
function detailHtml(k,id){
  if(k==='layer'){
    var ev=EV.filter(function(e){return arr(e.stack_layer).indexOf(id)!==-1;});
    return '<h2>'+esc(laneLabel(id))+'</h2><div class="id">'+esc(id)+'</div><p>'+esc(laneNote(id))+'</p><div>'+tag(ev.length+' facts')+'</div><div class="block"><button class="btn" type="button" data-filter-layer="'+esc(id)+'">Show layer facts in catalog</button></div><div class="block"><h4>Top facts</h4>'+ev.slice(0,14).map(function(e){return linkButton(e.id);}).join(' ')+'</div>';
  }
  if(k==='event'){
    var e=byEvent[id], contexts=arr(e.evidence_context), caveats=arr(e.caveats);
    var cyberBlock=arr(e.cyber_domain_ids).length?'<div class="block"><h4>Cyber framework</h4>'+arr(e.cyber_domain_ids).map(function(value){return tag(cyberDomainMeta(value).label_en||value);}).join('')+arr(e.cyber_role_ids).map(function(value){var meta=cyberRoleMeta(value);return tag(meta.label_en||value);}).join('')+(e.cyber_access_principal?tag((CYBER_FRAMEWORK.access_principal||{}).label_en||'Agent with delegated authority'):'')+'</div>':'';
    var statusUpdate=e.legal_update_en||e.independent_review_summary_en||'';
    var statusBlock=statusUpdate?'<div class="block quote"><h4>Status update'+(e.status_update_date?' · '+esc(e.status_update_date):'')+'</h4><p>'+esc(statusUpdate)+'</p></div>':'';
    return '<h2>'+esc(e.title)+'</h2><div class="id">'+esc(e.id)+'</div><div>'+eventMeta(e)+'</div>'+cyberBlock+statusBlock+'<div class="block"><h4>Supported claim</h4><p>'+esc(e.claim_supported||e.summary||'')+'</p></div>'+(e.claim_challenged||e.caveat?'<div class="quote block"><h4>Caveat</h4><p>'+esc(e.claim_challenged||e.caveat)+'</p></div>':'')+(e.safe_wording?'<div class="quote block"><h4>Safe wording</h4><p>'+esc(e.safe_wording)+'</p></div>':'')+(contexts.length?'<div class="block"><h4>Evidence context</h4>'+contexts.map(function(v){return tag(evidenceContextLabel(v));}).join('')+'</div>':'')+(caveats.length?'<div class="quote block"><h4>Evidence-tier limitations</h4><ul>'+caveats.map(function(v){return '<li>'+esc(v)+'</li>';}).join('')+'</ul></div>':'')+taxonomyDetail(e)+sourceBlock(e)+edgeBlock(e.edgeIds)+arcBlock(e.arcIds);
  }
  if(k==='arc'){
    var a=byArc[id],facts=factsForArc(a),arcEdges=EDGES.filter(function(e){return e.arc_id===a.id;});
    return '<h2>'+esc(arcTitle(a))+'</h2><div class="id">'+esc(a.id)+'</div><div>'+tag(familyTitle(a.family_id))+tag(a.arc_kind)+tag(a.arc_type)+tag(a.status)+tags(a.visual_lanes.map(laneLabel))+'</div><div class="block"><h4>Arc thesis</h4><p>'+esc(a.thesis_en||a.thesis||'')+'</p></div><div class="quote block"><h4>Limits of the inference</h4><p>'+esc(a.safe_wording_en||a.safe_wording||'')+'</p></div><div class="block"><h4>Dated facts</h4>'+facts.map(function(e){return linkButton(e.id);}).join(' ')+'</div><div class="block"><h4>What the evidence does not establish</h4><p>'+esc(arr(a.counterpoints_en||a.counterpoints).join(' · '))+'</p></div><details class="block"><summary>Technical graph links ('+arcEdges.length+')</summary><div class="block">'+arcEdges.slice(0,36).map(function(e){return linkButton(e.id);}).join(' ')+'</div></details>';
  }
  if(k==='edge'){
    var ed=byEdge[id];
    return '<h2>'+esc(ed.summary_en||ed.summary||ed.id)+'</h2><div class="id">'+esc(ed.id)+'</div><div>'+tag(familyTitle(ed.arc_family_id))+tag(ed.relation)+tag(ed.strength)+tag(ed.evidence_level)+'</div><div class="block"><h4>From</h4>'+linkButton(ed.source)+'</div><div class="block"><h4>To</h4>'+linkButton(ed.target)+'</div>';
  }
  if(k==='claim'){
    var c=byClaim[id];
    var legalUpdate=c.legal_update_en?'<div class="block quote"><h4>Status update'+(c.status_update_date?' · '+esc(c.status_update_date):'')+'</h4><p>'+esc(c.legal_update_en)+'</p>'+(c.legal_update_caveat_en?'<p class="small">'+esc(c.legal_update_caveat_en)+'</p>':'')+'</div>':'';
    return '<h2>'+esc(c.claim||c.title)+'</h2><div class="id">'+esc(c.id)+'</div><div>'+tag(statusLabel(c.status))+tag(confidenceLabel(c.evidence_level||c.confidence))+tags(c.geography)+'</div>'+legalUpdate+'<div class="block"><h4>Recommended phrasing</h4><p>'+esc(c.recommended_phrasing||'')+'</p></div>'+sourceBlock(c);
  }
  if(k==='check'){
    var cc=byCheck[id];
    return '<h2>'+esc(cc.claim||cc.title)+'</h2><div class="id">'+esc(cc.id)+'</div><div>'+tag(statusLabel(cc.status))+tag(confidenceLabel(cc.confidence))+'</div><div class="quote block"><h4>Safe wording</h4><p>'+esc(cc.safe_wording||'')+'</p></div><div class="block"><h4>Supporting evidence</h4>'+arr(cc.supporting_evidence).map(linkButton).join(' ')+'</div>';
  }
  if(k==='thesis'){
    var t=byThesis[id];
    return '<h2>'+esc(thesisLabel(t))+'</h2><div class="id">'+esc(t.id)+'</div><p>'+esc(thesisSummary(t))+'</p>';
  }
  if(k==='counterargument'){
    var ca=byCounter[id];
    return '<h2>'+esc(ca.objection||ca.title)+'</h2><div class="id">'+esc(ca.id)+'</div><div>'+tag(ca.evidence_status)+'</div>'+(ca.steelman?'<div class="quote block"><h4>Strongest version of the objection</h4><p>'+esc(ca.steelman)+'</p></div>':'')+(ca.how_to_handle?'<div class="block"><h4>How to handle it</h4><p>'+esc(ca.how_to_handle)+'</p></div>':'')+(arr(ca.evidence).length?'<div class="block"><h4>Related facts</h4>'+arr(ca.evidence).map(linkButton).join(' ')+'</div>':'');
  }
  if(k==='gap'){
    var gap=byGap[id];
    return '<h2>'+esc(gap.topic||gap.title)+'</h2><div class="id">'+esc(gap.id)+'</div><div>'+tag(gap.priority)+tag(gap.status)+'</div>'+(gap.why?'<div class="quote block"><h4>Why it matters</h4><p>'+esc(gap.why)+'</p></div>':'')+(gap.what_would_close?'<div class="block"><h4>What would close the gap</h4><p>'+esc(gap.what_would_close)+'</p></div>':'')+(gap.resolution?'<div class="block"><h4>Resolution</h4><p>'+esc(gap.resolution)+'</p></div>':'');
  }
  return '<p>Not found.</p>';
}
function sourceBlock(x){ var ss=arr(x.sources); if(!ss.length && x.url) ss=[{name:x.source_name||host(x.url),url:x.url,type:x.source_type,date:x.source_date||x.date}]; if(!ss.length) return ''; return '<div class="block"><h4>Sources</h4>'+ss.map(function(s){var label=s.name||s.title||s.url; return '<p class="small">'+(s.url?'<a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(label)+'</a>':esc(label))+' '+tag(s.type)+' '+tag(s.date)+'</p>';}).join('')+'</div>'; }
function edgeBlock(ids){ return arr(ids).length?'<div class="block"><h4>Related edges</h4>'+arr(ids).slice(0,18).map(linkButton).join(' ')+'</div>':''; }
function arcBlock(ids){ return arr(ids).length?'<div class="block"><h4>Story arcs</h4>'+arr(ids).map(linkButton).join(' ')+'</div>':''; }
function updateDetailBack(){ document.getElementById('detail-back').hidden=!detailHistory.length; }
function _legacyCloseDetail(){ document.getElementById('modal').classList.remove('open'); detailHistory=[]; currentDetail=null; updateDetailBack(); }
function _legacyOpenDetail(k,id,options){ options=options||{}; if(currentDetail && !options.replace && (currentDetail.k!==k || currentDetail.id!==id)) detailHistory.push(currentDetail); currentDetail={k:k,id:id}; document.getElementById('detail').innerHTML=detailHtml(k,id); bindClicks(document.getElementById('detail')); bindDetailActions(document.getElementById('detail')); updateDetailBack(); document.getElementById('modal').classList.add('open'); }

function bindDetailActions(root){ if(!root) return; root.querySelectorAll('[data-filter-layer]').forEach(function(button){ button.onclick=function(ev){ ev.stopPropagation(); factState.layer=button.dataset.filterLayer; document.getElementById('filter-layer').value=factState.layer; renderFacts(); closeDetail(); switchTab('facts'); }; }); }

/* COMMON_RUNTIME */
document.getElementById('detail-back').onclick=function(){ var previous=detailHistory.pop(); if(previous) openDetail(previous.k,previous.id,{replace:true}); };
document.getElementById('modal').onclick=function(e){ if(e.target.dataset.close) closeDetail(); };
document.addEventListener('keydown',function(e){ if(e.key==='Escape') closeDetail(); });
renderHeader(); renderNav(); renderOverview(); renderCapitalLedger(); initGraphControls(); renderStory('story-svg'); renderRecipes(); renderTimeline(); initCyberControls(); renderCyber(); renderStack(); initFilters(); renderFacts(); renderClaims(); renderSources(); initAtlasReview();
