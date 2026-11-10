#!/usr/bin/env python3
"""Append the reviewed Astra observation to v0.56; preserve a pinned baseline."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

from migrate_audit_repair import check_document, field_changes, write_documents
from migrate_frontier_pacing import event_record, pair
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/astra-underperformance-2026-11-10'
VERSION, DATE = '0.57', '2026-11-10'


def baseline(lang):
    manifest = json.loads((PACKET / 'baseline-manifest.json').read_text())
    raw = gzip.decompress((PACKET / manifest[lang]['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest[lang]['sha256']
    return json.loads(raw)


def journal_document(doc):
    # Keyed collections keep a one-record update from copying entire arrays.
    return {key: {item['id']: item for item in value}
            if isinstance(value, list) and value and all(isinstance(item, dict) and 'id' in item for item in value)
            else value for key, value in doc.items()}


def migrate(before, package):
    if before['meta']['version'] != '0.56':
        raise ValueError('Expected v0.56')
    doc, lang = copy.deepcopy(before), before['language']
    raw = copy.deepcopy(package['event'])
    if any(e['id'] == raw['id'] for e in doc['events']):
        raise ValueError('Duplicate event ID')
    if any(s['url'] == package['sources']['OPENAI_COVERT_UNDERPERFORMANCE']['url'] for s in doc['sourceIndex']):
        raise ValueError('Study already indexed; review for duplication first')
    raw.update(safe_ru=raw['summary_ru'], safe_en=raw['summary_en'])
    event = event_record(raw, lang, package['sources'], doc)
    event.update(raw['behavior'])
    for field, vocabulary in [('cyber_subdomain_ids', 'subdomains'), ('behavioral_mechanism_ids', 'behavioral_mechanisms'),
                              ('behavioral_status', 'behavioral_statuses'), ('evidence_context', 'evidence_contexts'),
                              ('oversight_target', 'oversight_targets'), ('concealment_targets', 'concealment_targets')]:
        if not set(event[field]) <= {v['id'] for v in doc['cyberFramework'][vocabulary]}:
            raise ValueError('Unknown classifier in '+field)
    event.update(story_primary_arc_id=raw['arcs'][0], story_secondary_arc_ids=raw['arcs'][1:],
        route_eligible_arc_ids=raw['arcs'], research_updates=[PACKET.name],
        geographic_scopes=[], governance_scale='not_applicable',
        research_evidence_kind='provider_internal_observation_and_paired_evaluation',
        research_review_status='source_reviewed_not_independently_replicated',
        research_provenance=copy.deepcopy(raw),
        classification_review=dict(date=DATE, source_account_reviewed=True, independent_replication=False,
            independent_source_reverification=False),
        current_state=dict(observed_at=raw['dates']['report_updated'],
            date_basis='report_updated_date_not_new_incident', sources=[package['sources']['OPENAI_COVERT_UNDERPERFORMANCE']]))
    for field in ('notes', 'corroboration_needed', 'claim_challenged'):
        pair(event, field, '', '', lang)
    for field in ('mechanism', 'editorial_rationale'):
        pair(event, field, raw['mechanism_ru'], raw['mechanism_en'], lang)
    pair(event, 'scope', 'Внутренние исследовательские задачи OpenAI и парное испытание.',
        'OpenAI internal research work and a paired evaluation.', lang)
    pair(event, 'role_basis', 'ИИ помогает исследованию безопасности и сам является объектом проверки.',
        'AI assists safety research and is itself the subject of evaluation.', lang)
    for field in ('title', 'summary'):
        pair(event['current_state'], field, raw['state_'+field+'_ru'], raw['state_'+field+'_en'], lang)
    doc['events'].append(event)
    arcs, events = {a['id']: a for a in doc['arcs']}, {e['id']: e for e in doc['events']}
    edges = []
    for index, aid in enumerate(raw['arcs'], 1):
        arc = arcs[aid]
        edge = dict(id=f'EDGE_V057_ASTRA_{index:03d}', kind='edge', source=event['id'], target=aid,
            source_kind='evidence', target_kind='arc', relation='part_of_arc', arc_id=aid,
            arc_family_id=arc['family_id'], strength='moderate', evidence_level='B',
            visual_lane=raw['stack_layers'][0], is_auto=False, style='dashed', relationship_class='thematic')
        pair(edge, 'summary', 'Тематическая принадлежность; не доказательство намеренной политики поставщика.',
            'Thematic membership, not evidence of a deliberate provider policy.', lang)
        edges.append(edge)
        arc['key_nodes'] = uniq(arc['key_nodes'] + [event['id']])
        ordered = iter(sorted((n for n in arc['key_nodes'] if n in events), key=lambda n: (events[n]['date'], n)))
        arc['key_nodes'] = [next(ordered) if n in events else n for n in arc['key_nodes']]
        arc['start_date'] = min(arc['start_date'], event['date'])
        arc['end_date'] = max(arc['end_date'], event['date'])
    doc['edges'].extend(edges)
    attach_edge_links(doc, {e['id'] for e in edges})
    doc['meta'].update(version=VERSION, updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version=VERSION, date=DATE, added_evidence=1,
        added_story_edges=len(edges), added_claims=0, added_story_arcs=0,
        description='Astra covert safety-research underperformance; internal observation distinct from prompted evasion.'))
    doc['presentation'].update(editorial_version=VERSION, release_notes=[dict(
        title='Исследовательская помощь и надзор' if lang == 'ru' else 'Research assistance and oversight',
        text=raw['title_'+lang])])
    refresh(doc)
    doc['connectivity']['last_recomputed'] = DATE
    doc['migrationAudit']['v057_astra_underperformance'] = dict(date=DATE, added_event_ids=[event['id']],
        added_edge_ids=[e['id'] for e in edges],
        added_source_urls=sorted({s['url'] for s in doc['sourceIndex']} - {s['url'] for s in before['sourceIndex']}),
        packet=str(PACKET.relative_to(ROOT) / 'accepted.json'))
    doc['referenceIntegrity'] = references(doc)
    check_document(doc)
    assert doc['referenceIntegrity']['valid']
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    package = json.loads((PACKET / 'accepted.json').read_text())
    paths = {lang: ROOT / f'ai_power_storygraph_{lang}.json' for lang in ('ru', 'en')}
    raw = {lang: path.read_bytes() for lang, path in paths.items()}
    manifest_path = PACKET / 'baseline-manifest.json'
    if manifest_path.exists():
        before = {lang: baseline(lang) for lang in paths}
    else:
        before = {lang: json.loads(value) for lang, value in raw.items()}
        if any(d['meta']['version'] != '0.56' for d in before.values()):
            raise ValueError('Baseline creation requires v0.56 in both languages')
    after = {lang: migrate(doc, package) for lang, doc in before.items()}
    for lang in raw:
        if json.loads(raw[lang]) not in (before[lang], after[lang]):
            raise ValueError('Unreviewed concurrent edits: ' + lang)
    report = dict(version=VERSION, collection_addressing='top_level_id_maps; order retained in pinned baseline', languages={lang: dict(
        counts={key: len(after[lang][key]) for key in ('events', 'arcs', 'claims', 'edges', 'sourceIndex')},
        changes=field_changes(journal_document(before[lang]), journal_document(after[lang]))) for lang in paths})
    if args.apply:
        if not manifest_path.exists():
            manifest = {}
            for lang in paths:
                name = f'baseline-{lang}.json.gz'
                (PACKET / name).write_bytes(gzip.compress(raw[lang], mtime=0))
                manifest[lang] = dict(path=name, sha256=hashlib.sha256(raw[lang]).hexdigest())
            manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        (PACKET / 'migration-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        write_documents(ROOT, raw, after)
    print(json.dumps(dict(applied=args.apply, counts={lang: report['languages'][lang]['counts'] for lang in paths})))


if __name__ == '__main__':
    main()
