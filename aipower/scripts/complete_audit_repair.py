#!/usr/bin/env python3
"""Apply source-reviewed actor identities and remove mismatched research boilerplate."""
import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from migrate_audit_repair import field_changes, write_documents, require, unique
from finalize_audit_release import finalize

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path('review/audit-repair-2026-11-08')
KEY = 'audit_completion_2026_11_08'
PREFIXES = {
    'ru': 'Карточка отделяет обязательное предписание, предложение, публичное обещание или риторику от данных об исполнении. ',
    'en': 'The record separates a binding directive, proposal, public commitment or rhetoric from implementation evidence. ',
}


def load_resolutions(root=ROOT):
    return [r for name in ('science-actor-resolution.json', 'named-actor-resolution.json')
            for r in json.loads((root / PACKET / name).read_text())['records']]


def source_family(url):
    return urlsplit(url).hostname.removeprefix('www.')


def add_actor_source(doc, event, check):
    url = check['url']
    require(url.startswith('https://'), 'Expected a primary-source HTTPS URL')
    if not any(s.get('url') == url for s in event['sources']):
        event['sources'].append({
            'url': url, 'title': check['title'], 'name': check['publisher'],
            'date': '', 'type': 'Primary source', 'source_class': 'actor_identity_primary',
            'primary_or_secondary': 'primary', 'checked_at': '2026-11-08',
            'verification_method': 'actor_identity_only; scientific_outcome_not_reassessed',
        })
    indexed = next((s for s in doc['sourceIndex'] if s['url'] == url), None)
    reference = {'id': event['id'], 'kind': 'event'}
    if indexed is None:
        number = max(int(s['id'].split('-')[-1]) for s in doc['sourceIndex']) + 1
        citation = next(s for s in event['sources'] if s['url'] == url)
        indexed = dict(citation, id=f'src-{number}', used_by=[])
        doc['sourceIndex'].append(indexed)
    if reference not in indexed['used_by']:
        indexed['used_by'].append(reference)
    group = next((g for g in doc['sourceGroups'] if any(s['url'] == url for s in g['sources'])), None)
    if group is None:
        family = source_family(url)
        group = next((g for g in doc['sourceGroups'] if g['family'] == family), None)
        if group is None:
            number = max(int(g['id'].split('-')[-1]) for g in doc['sourceGroups']) + 1
            group = {'id': f'source-group-{number}', 'family': family, 'sources': [], 'used_by': [], 'types': []}
            doc['sourceGroups'].append(group)
        group['sources'].append(copy.deepcopy(indexed))
    else:
        grouped = next(s for s in group['sources'] if s['url'] == url)
        if reference not in grouped['used_by']:
            grouped['used_by'].append(reference)
    if reference not in group['used_by']:
        group['used_by'].append(reference)
    group['types'] = unique(group['types'] + [indexed['type']])


def complete(doc, records, lang):
    require(doc.get('auditRepair'), 'The first audit repair must precede completion')
    events = {e['id']: e for e in doc['events']}
    labels = doc['classifierTaxonomy']['actors']['type_labels']
    public = {'label_ru': 'Политик / должностное лицо', 'label_en': 'Politician / public official'}
    labels['public_official'] = public
    doc['actorTypeLabels']['public_official'] = copy.deepcopy(public)
    registry = {a['actor']: a for a in doc['entityRegistry']['audit_actor_type_entries']}
    updated = []
    added_urls = set(doc.get('auditCompletion', {}).get('added_source_urls', []))
    existing_urls = {s['url'] for s in doc['sourceIndex']}
    for record in records:
        event = events[record['event_id']]
        require(not record.get('unresolved'), f"Unresolved identity: {event['id']}")
        checks = {s['url']: s for s in record['source_checks']}
        actor_provenance = []
        for actor in record['actors']:
            name = actor['name']
            require(actor['types'] and set(actor['types']) <= set(labels), f'Unknown actor type for {name}')
            require(actor['source_urls'] and set(actor['source_urls']) <= set(checks), f'Unreviewed source for {name}')
            require(actor.get('basis'), f'Missing identity basis for {name}')
            event['actor_entities'] = unique(event['actor_entities'] + [name])
            event['actor_facets'] = unique(event['actor_facets'] + [name])
            event['actor_types'] = unique(event['actor_types'] + actor['types'])
            event['actor_jurisdictions'] = unique(event['actor_jurisdictions'] + actor['jurisdictions'])
            entry = registry.setdefault(name, {'actor': name, 'actor_types': [], 'evidence_event_ids': [], 'source_urls': []})
            entry['actor_types'] = unique(entry['actor_types'] + actor['types'])
            entry['evidence_event_ids'] = unique(entry['evidence_event_ids'] + [event['id']])
            entry['source_urls'] = unique(entry['source_urls'] + actor['source_urls'])
            entry['basis'] = 'primary_source_identity_review_2026_11_08'
            actor_provenance.append(copy.deepcopy(actor))
            for url in actor['source_urls']:
                add_actor_source(doc, event, checks[url])
                if url not in existing_urls:
                    added_urls.add(url)
        old = event.get('audit_actor_types', {})
        names = [a['name'] for a in record['actors']]
        unresolved = [a for a in old.get('unresolved_entities', []) if a not in names]
        require(not unresolved, f"Incomplete actor review: {event['id']}")
        event['audit_actor_types'] = {
            'registry_field': 'entityRegistry.audit_actor_type_entries',
            'resolved_entities': unique(old.get('resolved_entities', []) + names),
            'unresolved_entities': [], 'status': 'resolved', 'reason': 'primary_source_identity_review',
        }
        event['actor_identity_review'] = {'date': '2026-11-08', 'actors': actor_provenance,
            'scope': 'Named lead institutions or programme participants; not a complete affiliation list. Raw input retained.'}
        updated.append(event['id'])
    edited = []
    for event in doc['events']:
        if not event.get('research_evidence_kind'):
            continue
        # Only replace the known mismatched template, retaining authored scientific text.
        changed = False
        for language, prefix in PREFIXES.items():
            key = 'editorial_rationale_' + language
            if event.get(key, '').startswith(prefix):
                event[key] = event['mechanism_' + language]
                changed = True
        if changed:
            event['editorial_rationale'] = event['editorial_rationale_' + lang]
            if not event.get('cyber_role_ids') and not event.get('behavioral_status'):
                for key in ('role_basis', 'role_basis_ru', 'role_basis_en'):
                    event[key] = ''
            edited.append(event['id'])
    # Keep the original completion set stable on repeated application.
    edited = unique(doc.get('auditCompletion', {}).get('research_editorial_ids', []) + edited)
    doc['entityRegistry']['audit_actor_type_entries'] = sorted(registry.values(), key=lambda a: a['actor'].casefold())
    for key, field in (('actors', 'actor_entities'), ('actor_entities', 'actor_entities'), ('actor_types', 'actor_types'), ('actor_jurisdictions', 'actor_jurisdictions')):
        doc['counts'][key] = dict(Counter(v for e in doc['events'] for v in e.get(field, [])))
    doc['entityRegistry']['actors'] = sorted(doc['counts']['actor_entities'], key=str.casefold)
    doc['summary']['source_count'] = len(doc['sourceIndex'])
    doc['auditRepair']['actor_type_review_queue'] = [
        {'event_id': e['id'], **e['audit_actor_types']} for e in doc['events']
        if e.get('audit_actor_types', {}).get('status') in {'partial', 'review_required'}]
    doc['auditCompletion'] = {
        'id': KEY, 'date': '2026-11-08', 'actor_event_ids': unique(updated),
        'research_editorial_ids': edited, 'added_source_urls': sorted(added_urls),
        'raw_actor_fields_preserved': True, 'scientific_results_reassessed': False,
    }
    return finalize(doc, lang)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {lang: (ROOT / f'ai_power_storygraph_{lang}.json').read_bytes() for lang in ('ru', 'en')}
    before = {lang: json.loads(payload) for lang, payload in raw.items()}
    records = load_resolutions()
    after = {lang: complete(copy.deepcopy(doc), records, lang) for lang, doc in before.items()}
    require(all(complete(copy.deepcopy(doc), records, lang) == doc for lang, doc in after.items()), 'Completion must be idempotent')
    changed = before != after
    if changed and args.apply:
        journal = ROOT / PACKET / 'completion-audit.json'
        require(not journal.exists(), 'Refusing to overwrite completion journal')
        journal.write_text(json.dumps({'languages': {lang: {'changes': field_changes(before[lang], after[lang])} for lang in before}}, ensure_ascii=False, indent=2) + '\n')
        write_documents(ROOT, raw, after)
    print(json.dumps({'applied': args.apply and changed, 'changed': changed,
        'languages': {lang: doc['auditCompletion'] for lang, doc in after.items()}}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
