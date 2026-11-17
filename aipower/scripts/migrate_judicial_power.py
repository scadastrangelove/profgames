#!/usr/bin/env python3
"""Deterministic v0.59 -> v0.60 judicial-power release."""
import argparse
import copy
import gzip
import hashlib
import json

from judicial_power_packet import ROOT, PACKET, DATE, RECORDS, SOURCES, EXISTING, RELATIONS
from migrate_frontier_pacing import event_record, pair
from migrate_audit_repair import check_document, date_bounds, write_documents
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq
from validate import references


def read_baseline(lang):
    manifest = json.loads((PACKET / 'baseline-manifest.json').read_text())
    raw = gzip.decompress((PACKET / manifest[lang]['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest[lang]['sha256']
    return json.loads(raw)


def migrate(before):
    assert before['meta']['version'] == '0.59'
    doc, lang = copy.deepcopy(before), before['language']
    events = {e['id']: e for e in doc['events']}
    arcs = {a['id']: a for a in doc['arcs']}
    doc['cyberFramework']['artifact_kinds'].append(dict(id='court_filing',
        label_ru='Судебное обращение', label_en='Court filing'))
    for r in RECORDS:
        assert r['id'] not in events and set(r['arcs']) <= arcs.keys()
        domains = ['CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE', 'CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE'] if r['cyber'] else []
        # Lawsuits concern governance of risk, not observed attacker/defender roles.
        raw = dict(r, date_basis='court_event_date', date_status='source_backed',
            confidence='A', status='verified_as_reported',
            stack_layers=['governance_law', 'model_weights', 'data_telemetry'] + (['cyber_security_patch'] if r['cyber'] else []),
            structures=['security', 'production', 'knowledge'], research_questions=[], numbers={},
            contexts=['governance_document'], method='primary_source_review', domains=domains,
            roles=[], primary_domain=domains[0] if domains else None, priority=2,
            force='binding' if r['artifact'] == 'judgment' else 'not_applicable',
            stage='published', delegation='not_applicable', safe_ru=r['summary_ru'], safe_en=r['summary_en'])
        e = event_record(raw, lang, SOURCES, doc)
        e.update(date_precision='day', story_primary_arc_id=r['arcs'][0],
            story_secondary_arc_ids=r['arcs'][1:], route_eligible_arc_ids=r['arcs'], context_arc_ids=[],
            legal_topics=r['legal_topics'], legal_proceeding=copy.deepcopy(r['legal_proceeding']),
            actor_jurisdictions=[], geographic_scopes=['National'], geographic_scope_basis='court_jurisdiction_not_actor_nationality',
            research_updates=[PACKET.name], behavioral_status=[],
            research_evidence_kind='litigation_filing' if r['artifact']=='court_filing' else 'judicial_record',
            research_review_status='primary_document_reviewed_not_full_docket_audit',
            research_provenance=dict(packet=str(PACKET.relative_to(ROOT))),
            classification_review=dict(date=DATE, source_account_reviewed=True, independent_replication=False),
            governance_scale='court_jurisdiction_and_case_scope', event_or_forecast='event')
        for field in ('notes', 'corroboration_needed', 'claim_challenged', 'role_basis'):
            pair(e, field, '', '', lang)
        for field in ('mechanism', 'editorial_rationale'):
            pair(e, field, r['mechanism_ru'], r['mechanism_en'], lang)
        pair(e, 'scope', r['title_ru'], r['title_en'], lang)
        if r['legal_proceeding']['phase'] == 'first_instance_nonfinal':
            e['normative_force'] = 'undetermined'
        events[e['id']] = e
        doc['events'].append(e)
    for eid, topics in EXISTING.items():
        e = events[eid]
        outcome = ('Суд разделил fair-use обучение и хранение пиратских копий.',
                   'The court separated fair-use training from retention of pirated copies.') if 'BARTZ' in eid else (
                   'Предварительный запрет отменён 4 августа 2026 года; дело возвращено на рассмотрение.',
                   'The preliminary injunction was vacated on 4 August 2026 and the case remanded.')
        e['legal_topics'] = topics
        e['legal_proceeding'] = dict(status_as_of=DATE, case_number='', court='',
            phase='historical_ruling' if 'BARTZ' in eid else 'historical_order_vacated' if 'AUTHORIZATION' in eid else 'appellate_ruling',
            relief_requested_ru='Предмет спора изложен в исходной карточке.',
            relief_requested_en='The dispute is described in the existing record.',
            outcome_ru=outcome[0], outcome_en=outcome[1],
            implementation_evidence='not_independently_established')

    added = []
    signatures = {(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']}
    def link(src, target, aid, relation, ru, en, target_kind='evidence'):
        signature = (src, target, relation, aid)
        assert signature not in signatures
        signatures.add(signature)
        edge = dict(id=f'EDGE_V060_{len(added)+1:03d}', kind='edge', source=src, target=target,
            source_kind='evidence', target_kind=target_kind, relation=relation, arc_id=aid,
            arc_family_id=arcs[aid]['family_id'], strength='moderate', evidence_level='A',
            visual_lane='governance_law', is_auto=False, style='dashed',
            relationship_class='thematic' if relation=='part_of_arc' else 'editorial_relationship')
        pair(edge, 'summary', ru, en, lang)
        added.append(edge)
    for r in RECORDS:
        for aid in r['arcs']:
            link(r['id'], aid, aid, 'part_of_arc', 'Тематическая принадлежность; не подтверждение всех выводов арки.',
                 'Thematic membership, not support for every conclusion of the arc.', 'arc')
            arcs[aid]['key_nodes'] = uniq(arcs[aid]['key_nodes'] + [r['id']])
    for src, target, aid, rel, ru, en in RELATIONS:
        link(src, target, aid, rel, ru, en)
    doc['edges'].extend(added)
    attach_edge_links(doc, {e['id'] for e in added})
    for arc in doc['arcs']:
        nodes = [n for n in arc['key_nodes'] if n in events]
        ordered = iter(sorted(nodes, key=lambda n:(events[n]['date'], n)))
        arc['key_nodes'] = [next(ordered) if n in events else n for n in arc['key_nodes']]
        bounds = [date_bounds(events[n]['date']) for n in nodes]
        if bounds:
            arc['start_date'] = min([arc['start_date']] + [b[0] for b in bounds])
            arc['end_date'] = max([arc['end_date']] + [b[1] for b in bounds])
    doc['crosscuttingViews'] = json.loads((ROOT / 'src/lenses.json').read_text())
    doc['meta'].update(version='0.60', updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version='0.60', date=DATE, added_evidence=len(RECORDS),
        added_claims=0, added_story_arcs=0, added_story_edges=len(added),
        description='Judicial power: separate filings, rulings and implementation; curated bilingual court lens.'))
    doc['presentation'].update(editorial_version='0.60', release_notes=[dict(
        title='Суды и границы власти в ИИ' if lang=='ru' else 'Courts and the Limits of AI Power',
        text='Испытания, конкуренция, закупки, знания и доступ агентов.' if lang=='ru' else
             'Testing, competition, procurement, knowledge and agent access.')])
    refresh(doc)
    doc['connectivity']['last_recomputed'] = DATE
    doc['auditRepair']['presentation_counts'].update(events=sum(not e.get('exclude_from_presentation') for e in doc['events']), stored_events=len(doc['events']))
    doc['migrationAudit']['v060_judicial_power'] = dict(date=DATE,
        added_event_ids=[r['id'] for r in RECORDS], annotated_event_ids=list(EXISTING),
        added_edge_ids=[e['id'] for e in added],
        added_source_urls=sorted({s['url'] for s in doc['sourceIndex']} - {s['url'] for s in before['sourceIndex']}))
    doc['referenceIntegrity'] = references(doc)
    check_document(doc)
    assert all(e in doc['edges'] for e in before['edges'])
    return doc


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    paths = {l:ROOT / f'ai_power_storygraph_{l}.json' for l in ('ru','en')}
    raw = {l:p.read_bytes() for l,p in paths.items()}
    manifest_path = PACKET / 'baseline-manifest.json'
    before = {l:read_baseline(l) if manifest_path.exists() else json.loads(raw[l]) for l in paths}
    after = {l:migrate(before[l]) for l in paths}
    for l in paths:
        if json.loads(raw[l]) not in (before[l], after[l]):
            raise ValueError('Unreviewed concurrent changes: '+l)
    if args.apply:
        PACKET.mkdir(parents=True, exist_ok=True)
        if not manifest_path.exists():
            manifest = {}
            for l in paths:
                name = f'baseline-{l}.json.gz'
                (PACKET/name).write_bytes(gzip.compress(raw[l], mtime=0))
                manifest[l] = dict(path=name, sha256=hashlib.sha256(raw[l]).hexdigest())
            manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        (PACKET/'reviewed-records.json').write_text(json.dumps(dict(events=RECORDS,sources=SOURCES,relations=RELATIONS),ensure_ascii=False,indent=2)+'\n')
        (PACKET/'migration-audit.json').write_text(json.dumps({l:after[l]['migrationAudit']['v060_judicial_power'] for l in paths},ensure_ascii=False,indent=2)+'\n')
        write_documents(ROOT, raw, after)
    print(json.dumps(dict(applied=args.apply,counts={l:{k:len(after[l][k]) for k in ('events','claims','arcs','edges','sourceIndex')} for l in paths})))


if __name__ == '__main__':
    main()
