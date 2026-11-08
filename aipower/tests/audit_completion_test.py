#!/usr/bin/env python3
"""Validate the source-backed completion without hiding earlier migration regressions."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from complete_audit_repair import complete, load_resolutions, PREFIXES, PACKET
from migrate_audit_repair import check_document
from validate import references
from audit_data_test import undo_journal


class CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = {lang: json.loads((ROOT / f'ai_power_storygraph_{lang}.json').read_text()) for lang in ('ru', 'en')}
        journal = json.loads((ROOT / PACKET / 'completion-audit.json').read_text())
        cls.before = {lang: undo_journal(d, journal['languages'][lang]['changes']) for lang, d in cls.current.items()}
        cls.records = load_resolutions()

    def test_replay_and_idempotence(self):
        for lang, current in self.current.items():
            self.assertEqual(complete(copy.deepcopy(self.before[lang]), self.records, lang), current)
            self.assertEqual(complete(copy.deepcopy(current), self.records, lang), current)

    def test_all_original_records_edges_and_raw_actor_data_preserved(self):
        for lang, before in self.before.items():
            after = self.current[lang]
            for collection in ('events', 'claims', 'claimChecks', 'arcs', 'edges', 'gaps', 'counterarguments'):
                self.assertEqual([x['id'] for x in before[collection]], [x['id'] for x in after[collection]])
            self.assertEqual(before['edges'], after['edges'])
            for old, new in zip(before['events'], after['events']):
                for field in ('date', 'title', 'summary', 'caveat', 'numbers', 'actor_raw', 'actors_raw', 'actor_facets_legacy', 'geography', 'jurisdictions', 'research_provenance', 'status', 'confidence'):
                    self.assertEqual(old.get(field), new.get(field), (old['id'], field))
                self.assertTrue(all(source in new['sources'] for source in old['sources']))
            self.assertTrue({(s['id'], s['url']) for s in before['sourceIndex']} <= {(s['id'], s['url']) for s in after['sourceIndex']})

    def test_actor_queue_resolved_with_primary_evidence(self):
        for doc in self.current.values():
            self.assertEqual(doc['auditRepair']['actor_type_review_queue'], [])
            self.assertEqual(len(doc['auditCompletion']['actor_event_ids']), 13)
            by_id = {e['id']: e for e in doc['events']}
            for record in self.records:
                event = by_id[record['event_id']]
                urls = {s['url'] for s in event['sources']}
                self.assertEqual(event['audit_actor_types']['status'], 'resolved')
                for actor in record['actors']:
                    self.assertIn(actor['name'], event['actor_entities'])
                    self.assertTrue(set(actor['source_urls']) <= urls)
                    self.assertTrue(set(actor['types']) <= set(event['actor_types']))
            self.assertIn('public_official', by_id['SIG_2026_TEXAS_ELECTION_DC_PAUSE_PLEDGE']['actor_types'])

    def test_scientific_editorial_text_is_specific(self):
        for doc in self.current.values():
            for event in doc['events']:
                if not event.get('research_evidence_kind'):
                    continue
                for lang, prefix in PREFIXES.items():
                    self.assertFalse(event.get('editorial_rationale_' + lang, '').startswith(prefix))
            self.assertGreaterEqual(len(doc['auditCompletion']['research_editorial_ids']), 52)

    def test_graph_and_source_contracts(self):
        for doc in self.current.values():
            check_document(doc)
            self.assertTrue(references(doc)['valid'])
            urls = {s['url'] for s in doc['sourceIndex']}
            self.assertEqual(len(urls), len(doc['sourceIndex']))
            self.assertEqual(len(urls), 824 + len(doc['auditCompletion']['added_source_urls']))
            self.assertTrue({s['url'] for e in doc['events'] for s in e['sources']} <= urls)
            self.assertEqual({s['url'] for g in doc['sourceGroups'] for s in g['sources']}, urls)

    def test_missing_or_invalid_identity_evidence_rejected(self):
        records = copy.deepcopy(self.records)
        records[0]['actors'][0]['source_urls'] = []
        with self.assertRaisesRegex(ValueError, 'Unreviewed source'):
            complete(copy.deepcopy(self.before['ru']), records, 'ru')
        records = copy.deepcopy(self.records)
        records[0]['actors'][0]['types'] = ['guessed_actor_type']
        with self.assertRaisesRegex(ValueError, 'Unknown actor type'):
            complete(copy.deepcopy(self.before['ru']), records, 'ru')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CompletionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT / PACKET / 'completion-tests.json').write_text(json.dumps({'passed': result.wasSuccessful(), 'tests': result.testsRun, 'failures': result.failures, 'errors': result.errors}, default=str, indent=2) + '\n')
    sys.exit(not result.wasSuccessful())
