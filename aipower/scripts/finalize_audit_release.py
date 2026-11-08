#!/usr/bin/env python3
"""Set v0.54 presentation metadata after the reversible data repair."""
import json
from pathlib import Path

from validate import references

ROOT = Path(__file__).resolve().parents[1]


def finalize(doc, lang):
    assert doc.get('auditRepair'), 'Apply migrate_audit_repair.py first'
    doc['meta']['version'] = '0.54'
    doc['meta']['updated_at'] = '2026-11-08'
    entry = {
        'version': '0.54', 'date': '2026-11-08', 'added_evidence': 0,
        'added_story_edges': 0, 'added_claims': 0, 'added_story_arcs': 0,
        'description': 'Audit repairs: evidence polarity, routes, aliases and provenance; quarterly recent-year chronology and complete update cards.'
    }
    doc['meta']['changelog'] = [entry] + [x for x in doc['meta']['changelog'] if x['version'] != '0.54']
    note = {
        'ru': {'title': 'Хронология и целостность', 'text': '2026 год показан по кварталам. Последние события и уточнения разделены. Исправлены доказательные связи, маршруты чтения и навигация; исходные записи и источники сохранены.'},
        'en': {'title': 'Chronology and integrity', 'text': '2026 is expanded into quarters. Recent events and later updates are separate. Evidence relations, reading routes and navigation are repaired; original records and sources are retained.'}
    }
    doc['presentation']['release_notes'] = [note[lang]]
    doc['presentation']['editorial_version'] = '0.54'
    doc['referenceIntegrity'] = references(doc)
    assert doc['referenceIntegrity']['valid']
    return doc


if __name__ == '__main__':
    for lang in ('ru', 'en'):
        path = ROOT / f'ai_power_storygraph_{lang}.json'
        doc = finalize(json.loads(path.read_text()), lang)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    print('Finalized v0.54 RU/EN')
