#!/usr/bin/env python3
"""Apply the reviewed v0.55 -> v0.56 research packet with a reversible journal."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

from migrate_audit_repair import field_changes, write_documents
from migrate_frontier_pacing import event_record, pair, add_source
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/crosscutting-expansion-2026-11-10'
VERSION, DATE = '0.56', '2026-11-10'


def baseline(lang):
    manifest = json.loads((PACKET / 'baseline-manifest.json').read_text())
    raw = gzip.decompress((PACKET / manifest['files'][lang]['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest['files'][lang]['sha256']
    return json.loads(raw)


def migrate(before, package, framework):
    if before['meta']['version'] != '0.55':
        raise ValueError('Expected the reviewed v0.55 baseline')
    doc, lang = copy.deepcopy(before), before['language']
    doc['cyberFramework']['artifact_kinds'].append(dict(
        id='judgment', label_ru='Судебное решение', label_en='Court judgment'))
    events, arcs = {e['id']: e for e in doc['events']}, {a['id']: a for a in doc['arcs']}
    sources = copy.deepcopy(package['sources'])
    for source in sources.values():
        source.update(checked_at=DATE, verification_method='primary_source_review_not_independent_replication')
    added, updated, edges = [], [], []
    for record in package['events']:
        if record['id'] in events:
            raise ValueError('Duplicate event: ' + record['id'])
        if not record['arcs'] or not set(record['arcs']) <= set(arcs):
            raise ValueError('Unknown arc: ' + record['id'])
        raw = dict(record, date_status='source_backed', confidence='B',
            status=record.get('status', 'verified_as_reported'),
            stack_layers=record['layers'], structures=record.get('structures', ['knowledge', 'production']),
            research_questions=[], numbers=record.get('numbers', {}),
            domains=[], roles=[], primary_domain=None, priority=2,
            safe_ru=record['summary_ru'], safe_en=record['summary_en'])
        raw.setdefault('actor_types', ['research'])
        raw.setdefault('contexts', ['ecosystem_measurement'])
        raw.setdefault('method', 'primary_source_review')
        raw.setdefault('artifact', 'research')
        raw.setdefault('force', 'not_applicable')
        raw.setdefault('stage', 'published')
        raw.setdefault('delegation', 'not_applicable')
        if not set(raw['actor_types']) <= set(doc['actorTypeLabels']):
            raise ValueError('Unknown actor type: ' + record['id'])
        for key, vocabulary in [('artifact', 'artifact_kinds'), ('force', 'normative_forces'),
                                ('stage', 'implementation_stages'), ('delegation', 'delegated_authority_states')]:
            if raw[key] not in {v['id'] for v in doc['cyberFramework'][vocabulary]}:
                raise ValueError('Unknown '+key+': '+record['id'])
        if not set(raw['contexts']) <= {v['id'] for v in doc['cyberFramework']['evidence_contexts']}:
            raise ValueError('Unknown evidence context: '+record['id'])
        event = event_record(raw, lang, sources, doc)
        event.update(story_primary_arc_id=record['arcs'][0], story_secondary_arc_ids=record['arcs'][1:],
            route_eligible_arc_ids=record['arcs'], research_updates=['crosscutting-expansion-2026-11-10'],
            geographic_scopes=record.get('geographic_scopes', []),
            actor_jurisdictions=record.get('actor_jurisdictions', []),
            geographic_scope_basis=record.get('geographic_scope_basis', 'source_reported_scope'),
            governance_scale=record.get('governance_scale', 'not_applicable'), behavioral_status=[],
            classification_review=dict(date=DATE, source_account_reviewed=True, independent_replication=False),
            research_evidence_kind=record['evidence_kind'],
            research_review_status='source_reviewed_not_independently_replicated',
            research_provenance=copy.deepcopy(record))
        if record.get('outcome_stage'):
            event['research_outcome_stage'] = record['outcome_stage']
        for field in ('notes', 'corroboration_needed', 'claim_challenged', 'role_basis'):
            pair(event, field, '', '', lang)
        pair(event, 'scope', record['title_ru'], record['title_en'], lang)
        pair(event, 'mechanism', record['mechanism_ru'], record['mechanism_en'], lang)
        pair(event, 'editorial_rationale', record['mechanism_ru'], record['mechanism_en'], lang)
        doc['events'].append(event)
        events[event['id']] = event
        added.append(event['id'])
    for update in package.get('updates', []):
        event = events[update['event_id']]
        if event['id'] in added:
            raise ValueError('Updates must target an existing record')
        changed_keys = set(update.get('fields', {}))
        for field in update.get('bilingual_fields', []):
            changed_keys.update((field, field+'_ru', field+'_en'))
        event.setdefault('editorial_history', []).append(dict(as_of=DATE, release='0.55',
            fields={key: copy.deepcopy(event.get(key)) for key in sorted(changed_keys)}))
        event.update(copy.deepcopy(update.get('fields', {})))
        for field in update.get('bilingual_fields', []):
            pair(event, field, update[field+'_ru'], update[field+'_en'], lang)
        for source_id in update.get('source_ids', []):
            add_source(event, sources[source_id])
        event['research_updates'] = uniq(event.get('research_updates', []) + ['crosscutting-expansion-2026-11-10'])
        updated.append(event['id'])
    signatures = {(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']}

    def add_edge(source, target, arc, relation, ru, en, target_kind='arc'):
        signature = (source, target, relation, arc)
        if signature in signatures:
            raise ValueError('Duplicate edge: ' + repr(signature))
        signatures.add(signature)
        edge = dict(id=f'EDGE_V056_RESEARCH_{len(edges)+1:03d}', kind='edge', source=source, target=target,
            source_kind='evidence', target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]['family_id'], strength='moderate', evidence_level='B',
            visual_lane=events[source]['stack_layers'][0], is_auto=False, style='dashed',
            relationship_class='thematic' if relation == 'part_of_arc' else 'editorial_relationship')
        pair(edge, 'summary', ru, en, lang)
        edges.append(edge)

    for record in package['events']:
        for aid in record['arcs']:
            add_edge(record['id'], aid, aid, 'part_of_arc',
                'Тематическая принадлежность; сама по себе не подтверждает тезис арки.',
                'Thematic membership; it does not by itself substantiate the arc thesis.')
            arcs[aid]['key_nodes'] = uniq(arcs[aid]['key_nodes'] + [record['id']])
    for relation in package.get('relations', []):
        if relation['target'] not in events or relation['source'] not in events:
            raise ValueError('Unresolved event relation')
        add_edge(relation['source'], relation['target'], relation['arc_id'], relation['relation'],
            relation['summary_ru'], relation['summary_en'], 'evidence')
    doc['edges'].extend(edges)
    attach_edge_links(doc, {e['id'] for e in edges})
    for aid in {a for record in package['events'] for a in record['arcs']}:
        arc = arcs[aid]
        ordered = iter(sorted((n for n in arc['key_nodes'] if n in events), key=lambda n: (events[n]['date'], n)))
        arc['key_nodes'] = [next(ordered) if n in events else n for n in arc['key_nodes']]
        dates = [events[n]['date'] for n in arc['key_nodes'] if n in events]
        arc.update(start_date=min([arc['start_date']] + dates), end_date=max([arc['end_date']] + dates))
    doc['crosscuttingViews'] = copy.deepcopy(framework)
    doc['meta'].update(version=VERSION, updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(added),
        updated_evidence=len(updated), added_story_edges=len(edges), added_claims=0, added_story_arcs=0,
        description='Sovereignty/exit and decision-delegation views; reviewed research packet integration.'))
    doc['presentation'].update(editorial_version=VERSION, release_notes=[dict(
        title='Суверенитет и решения' if lang == 'ru' else 'Sovereignty and decisions',
        text='Два новых среза и проверенные исследовательские дополнения. Результаты, ограничения доступа и полномочия разделены.' if lang == 'ru' else
             'Two new views and reviewed research additions. Outcomes, access conditions and authority remain distinct.')])
    refresh(doc)
    doc['connectivity']['last_recomputed'] = DATE
    doc['summary']['total_arcs'] = doc['summary']['total_story_arcs'] = len(doc['arcs'])
    doc['migrationAudit']['v056_crosscutting_expansion'] = dict(date=DATE, added_event_ids=added,
        updated_event_ids=updated, added_edge_ids=[e['id'] for e in edges],
        added_source_urls=sorted({s['url'] for s in doc['sourceIndex']} - {s['url'] for s in before['sourceIndex']}),
        packet='review/crosscutting-expansion-2026-11-10/accepted.json',
        decisions=copy.deepcopy(package['decisions']))
    doc['referenceIntegrity'] = references(doc)
    assert doc['referenceIntegrity']['valid'], doc['referenceIntegrity']
    assert all(edge in doc['edges'] for edge in before['edges'])
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    package = json.loads((PACKET / 'accepted.json').read_text())
    framework = json.loads((ROOT / 'src/lenses.json').read_text())
    raw = {lang: (ROOT / f'ai_power_storygraph_{lang}.json').read_bytes() for lang in ('ru', 'en')}
    before = {lang: baseline(lang) for lang in raw}
    after = {lang: migrate(before[lang], package, framework) for lang in raw}
    for lang in raw:
        current = json.loads(raw[lang])
        prior_render = migrate(before[lang], package, current['crosscuttingViews']) if current['meta']['version'] == VERSION else None
        if current != before[lang] and current != after[lang] and current != prior_render:
            raise ValueError('Unreviewed concurrent data changes: ' + lang)
    report = dict(version=VERSION, languages={lang: dict(
        counts={key: len(after[lang][key]) for key in ('events', 'arcs', 'claims', 'edges', 'sourceIndex')},
        changes=field_changes(before[lang], after[lang])) for lang in raw})
    if args.apply:
        (PACKET / 'migration-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        write_documents(ROOT, raw, after)
    print(json.dumps(dict(applied=args.apply, counts={lang: report['languages'][lang]['counts'] for lang in raw})))


if __name__ == '__main__':
    main()
