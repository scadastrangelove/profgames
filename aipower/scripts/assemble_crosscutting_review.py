#!/usr/bin/env python3
"""Materialize only explicitly selected and edited research candidates."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/crosscutting-expansion-2026-11-10'


def assemble():
    editorial = json.loads((PACKET / 'editorial-decisions.json').read_text())
    result = dict(version='0.56', date='2026-11-10', events=[], updates=[], sources={}, relations=[], decisions=[])
    for selection in editorial['selections']:
        source = json.loads((PACKET / selection['packet']).read_text())
        candidates = source.get(selection.get('collection', 'events'), [])
        candidate = selection.get('record') or next(r for r in candidates if r['id'] == selection['id'])
        if candidate['id'] != selection['id']:
            raise ValueError('Selection ID differs from record')
        record = copy.deepcopy(candidate)
        record.update(selection.get('overrides', {}))
        for sid in record['source_ids']:
            metadata = copy.deepcopy(source['sources'][sid])
            metadata.update(editorial.get('source_overrides', {}).get(sid, {}))
            if sid in result['sources'] and result['sources'][sid] != metadata:
                raise ValueError('Conflicting source ID: ' + sid)
            result['sources'][sid] = metadata
        result['events'].append(record)
        result['decisions'].append({k: v for k, v in selection.items() if k not in ('overrides', 'record')})
    for update in editorial.get('updates', []):
        source = json.loads((PACKET / update['packet']).read_text())
        record = copy.deepcopy(update.get('record') or source['updates'][update['update_index']])
        record.update(update.get('overrides', {}))
        record.setdefault('fields', {}).update(update.get('fields_overrides', {}))
        result['updates'].append(record)
        for sid in record.get('source_ids', []):
            result['sources'][sid] = copy.deepcopy(source['sources'][sid])
        result['decisions'].append({k: v for k, v in update.items() if k not in ('overrides', 'record', 'fields_overrides')})
    result['decisions'].extend(editorial.get('deferred_or_rejected', []))
    result['relations'] = editorial.get('relations', [])
    ids = [e['id'] for e in result['events']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate selected event')
    (PACKET / 'accepted.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'events': len(ids), 'updates': len(result['updates']), 'decisions': len(result['decisions'])}))


if __name__ == '__main__':
    assemble()
