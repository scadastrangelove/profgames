#!/usr/bin/env python3
"""Normalize the four research packets without ingesting candidate evidence."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/crosscutting-views-2026-11-09'


def urlkey(url):
    p = urlsplit(url.strip())
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), p.query, ''))


def review():
    doc = json.loads((ROOT / 'ai_power_storygraph_en.json').read_text())
    arcs = {a['id'] for a in doc['arcs']}
    events = {e['id'] for e in doc['events']}
    old_urls = {urlkey(s['url']) for s in doc['sourceIndex']}
    manifest = dict(date='2026-11-09', status='research_candidates_not_integrated',
                    canonical_event_count=len(events), packets=[], candidates=[])
    seen = set()
    for name in ('knowledge-research', 'knowledge-access', 'economy-infrastructure', 'economy-work'):
        path = PACKET / (name + '.json')
        raw = path.read_bytes()
        packet = json.loads(raw)
        source_map = {s['id']: s for s in packet.get('sources', [])}
        candidates = packet['candidates']
        manifest['packets'].append(dict(file=path.name, sha256=hashlib.sha256(raw).hexdigest(), candidates=len(candidates)))
        for c in candidates:
            eid = c['proposed_id']
            assert eid not in seen and eid not in events, eid
            seen.add(eid)
            for field in ('title_ru', 'title_en', 'summary_ru', 'summary_en', 'caveat_ru', 'caveat_en', 'date_basis', 'dedup', 'evidence_stage'):
                assert c.get(field), (eid, field)
            date = c.get('event_date', c.get('date'))
            assert date and date <= manifest['date'], (eid, date)
            refs = c.get('relevant_existing_arc_ids', c.get('arc_ids', c.get('proposed_arc_ids')))
            assert refs and set(refs) <= arcs, (eid, refs)
            sources = c.get('sources') or [source_map[s] for s in c['source_ids']]
            urls = [s['url'] for s in sources]
            assert urls and all(urlsplit(u).scheme == 'https' for u in urls), eid
            manifest['candidates'].append(dict(id=eid, packet=path.name, date=date,
                date_basis=c['date_basis'], title_ru=c['title_ru'], title_en=c['title_en'],
                arc_ids=refs, source_urls=urls,
                existing_source_urls=[u for u in urls if urlkey(u) in old_urls],
                dedup_verdict=c['dedup']['verdict'],
                action=c.get('action', c.get('recommendation', 'candidate_for_editorial_review'))))
    manifest['candidate_count'] = len(seen)
    manifest['passed'] = True
    return manifest


if __name__ == '__main__':
    manifest = review()
    (PACKET / 'research-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: manifest[k] for k in ('status', 'candidate_count', 'passed')}, indent=2))
