#!/usr/bin/env python3
"""Attach the shared, reference-based view definitions without rewriting evidence."""
import json
from pathlib import Path
from validate import references

ROOT = Path(__file__).resolve().parents[1]


def configure(doc, framework):
    if doc['meta']['version'] not in ('0.54', '0.55'):
        raise ValueError('Expected v0.54 or v0.55; future releases require review')
    arcs = {arc['id'] for arc in doc['arcs']}
    for view in framework['views']:
        for track in view['tracks']:
            refs = track['arc_ids'] + track.get('required_arc_ids', [])
            if not set(refs) <= arcs:
                raise ValueError('Unknown arc in view: ' + track['id'])
    doc['crosscuttingViews'] = framework
    doc['summary']['total_arcs'] = len(doc['arcs'])
    doc['summary']['total_story_arcs'] = len(doc['arcs'])
    doc['meta'].update(version='0.55', updated_at='2026-11-09')
    if not any(x['version'] == '0.55' for x in doc['meta']['changelog']):
        doc['meta']['changelog'].insert(0, dict(version='0.55', date='2026-11-09',
            added_evidence=0, added_story_edges=0, added_claims=0, added_story_arcs=0,
            description='Knowledge and Access / AI Economy views; separate source-reviewed research packets, not new canonical events.'))
    doc['presentation']['editorial_version'] = '0.55'
    doc['referenceIntegrity'] = references(doc)
    if not doc['referenceIntegrity']['valid']:
        raise ValueError('Invalid references after configuring views')
    return doc


if __name__ == '__main__':
    framework = json.loads((ROOT / 'src/lenses.json').read_text())
    outputs = []
    for lang in ('ru', 'en'):
        path = ROOT / f'ai_power_storygraph_{lang}.json'
        doc = configure(json.loads(path.read_text()), framework)
        outputs.append((path, json.dumps(doc, ensure_ascii=False, indent=2) + '\n'))
        print(lang, 'configured', len(framework['views']), 'views; evidence unchanged')
    for path, content in outputs:
        path.write_text(content)
