#!/usr/bin/env python3
"""Data-only audit regression tests. No build, browser or release-file writes.

python3 -B tests/audit_data_test.py --report review/audit-repair-2026-11-08/tests-results.json
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import migrate_audit_repair as repair
from validate import references


def undo_journal(document, changes):
    result = copy.deepcopy(document)
    for change in reversed(changes):
        parent = result
        for part in change["path"][:-1]:
            parent = parent[part]
        key = change["path"][-1]
        if change["before_exists"]:
            parent[key] = copy.deepcopy(change["before"])
        else:
            del parent[key]
    return result


class AuditDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = {lang: json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text()) for lang in ("ru", "en")}
        completion = ROOT / repair.REVIEW_DIR / 'completion-audit.json'
        if completion.exists():
            journal = json.loads(completion.read_text())
            # This suite replays the first repair. Completion has its own preservation suite.
            cls.current = {lang: undo_journal(doc, journal['languages'][lang]['changes']) for lang, doc in cls.current.items()}
        report_path = ROOT / repair.REVIEW_DIR / "migration-audit.json"
        cls.report = json.loads(report_path.read_text()) if report_path.exists() else None
        if cls.report and "auditRepair" in cls.current["ru"]:
            cls.before = {lang: undo_journal(doc, cls.report["languages"][lang]["changes"]) for lang, doc in cls.current.items()}
        else:
            cls.before = copy.deepcopy(cls.current)
        cls.after = repair.prepare_documents(cls.before)

    def test_exact_id_counts_and_preservation(self):
        expected = {"events": 567, "claims": 76, "claimChecks": 32, "arcs": 30, "edges": 1411, "sourceIndex": 824}
        for lang in self.before:
            with self.subTest(lang=lang):
                self.assertEqual(repair.manifest(self.before[lang]), repair.manifest(self.after[lang]))
                for col, count in expected.items():
                    self.assertEqual(len(self.after[lang][col]), count)
                    self.assertEqual([n["id"] for n in self.before[lang][col]], [n["id"] for n in self.after[lang][col]])

    def test_all_original_top_level_records_retained(self):
        for lang, before in self.before.items():
            for key, value in before.items():
                if isinstance(value, list) and value and all(isinstance(n, dict) and "id" in n for n in value):
                    self.assertEqual([n["id"] for n in value], [n["id"] for n in self.after[lang][key]], (lang, key))

    def test_event_dates_raw_actors_and_source_indexes_unchanged(self):
        for lang, before in self.before.items():
            for old, new in zip(before["events"], self.after[lang]["events"]):
                for field in ("date", "source_date", "url", "actor_raw", "actors_raw", "actor_facets_legacy", "title", "summary", "caveat", "numbers"):
                    self.assertEqual(old.get(field), new.get(field), (old["id"], field))
            for key in ("sourceIndex", "sourceGroups", "meta", "recommendations", "recipes", "countries"):
                self.assertEqual(before[key], self.after[lang][key], (lang, key))

    def test_idempotence(self):
        self.assertEqual(repair.prepare_documents(self.after), self.after)

    def test_future_release_metadata_is_not_pinned_or_rewritten(self):
        docs = copy.deepcopy(self.after)
        for doc in docs.values():
            doc["meta"]["version"] = "0.54"
            doc["meta"]["updated_at"] = "parent-owned-release-date"
        after = repair.prepare_documents(docs)
        for lang in docs:
            self.assertEqual(after[lang]["meta"], docs[lang]["meta"])

    def test_journal_is_reversible(self):
        for lang in self.before:
            changes = repair.field_changes(self.before[lang], self.after[lang])
            self.assertEqual(undo_journal(self.after[lang], changes), self.before[lang])

    def test_committed_migration_matches_replay(self):
        if not self.report or "auditRepair" not in self.current["ru"]:
            self.skipTest("Pre-apply run; replay is checked after migration")
        for lang in self.current:
            expected_doc = copy.deepcopy(self.after[lang])
            # Reversing the journal intentionally leaves parent release metadata
            # in place; the historical preservation seal still belongs to v0.53.
            expected_doc["migrationAudit"][repair.AUDIT_KEY]["preserved"]["release_metadata_sha256"] = self.report["languages"][lang]["before"]["release_metadata_sha256"]
            self.assertEqual(self.current[lang], expected_doc)
            # Parent-owned release metadata may change after the data repair.
            expected = dict(self.report["languages"][lang]["after"])
            actual = repair.manifest(self.current[lang])
            expected.pop("release_metadata_sha256")
            actual.pop("release_metadata_sha256")
            self.assertEqual(expected, actual)

    def test_polarity_matches_explicit_manual_counterparts(self):
        for lang, doc in self.after.items():
            old = {e["id"]: e for e in self.before[lang]["edges"]}
            edges = {e["id"]: e for e in doc["edges"]}
            corrected = [e for e in doc["edges"] if "audit_original_relation" in e]
            self.assertEqual(len(corrected), 6)
            for edge in corrected:
                self.assertEqual(edge["audit_original_relation"], old[edge["id"]]["relation"])
                for reference in edge["polarity_basis_edge_ids"]:
                    manual = edges[reference]
                    self.assertFalse(manual["is_auto"])
                    self.assertEqual((edge["source"], edge["target"], edge["relation"]), (manual["source"], manual["target"], manual["relation"]))
            self.assertEqual(edges["EDGE_AUTO_SUPPORT_029"]["relation"], "walks_back")
            self.assertEqual(edges["EDGE_AUTO_SUPPORT_062"]["relation"], "walks_back")

    def test_auto_edges_not_blanket_deleted_or_reclassified(self):
        for lang, doc in self.after.items():
            old = {e["id"]: e for e in self.before[lang]["edges"]}
            self.assertEqual(sum(e.get("is_auto", False) for e in doc["edges"]), 83)
            for edge in doc["edges"]:
                self.assertEqual((edge["source"], edge["target"]), (old[edge["id"]]["source"], old[edge["id"]]["target"]))
                if "audit_original_relation" not in edge:
                    self.assertEqual(edge["relation"], old[edge["id"]]["relation"])

    def test_polarity_uses_relation_not_identifier_or_status(self):
        doc = {"language": "en", "claimChecks": [{"id": "claim", "status": "needs_correction", "supporting_evidence": ["counterevidence_named_but_unreviewed"]}], "edges": [
            {"id": "auto", "source": "counterevidence_named_but_unreviewed", "target": "claim", "relation": "supports", "is_auto": True, "arc_id": "AUTO_CLAIMCHECK_SUPPORT"}]}
        repair.repair_polarity(doc)
        self.assertEqual(doc["edges"][0]["relation"], "supports")
        doc["edges"].append({"id": "manual", "source": doc["edges"][0]["source"], "target": "claim", "relation": "qualifies", "is_auto": False})
        repair.repair_polarity(doc)
        self.assertEqual(doc["edges"][0]["relation"], "qualifies")

    def test_conflicting_manual_relations_fail_closed(self):
        doc = copy.deepcopy(self.before["ru"])
        edge = copy.deepcopy(next(e for e in doc["edges"] if e["id"] == "EDGE_CYBER_005"))
        edge.update(id="different-manual-evidence", relation="supports")
        doc["edges"].append(edge)
        with self.assertRaisesRegex(ValueError, "Ambiguous manual polarity"):
            repair.repair_polarity(doc)

    def test_evidence_arrays_are_neutral_complete_and_preserved(self):
        for lang, doc in self.after.items():
            before = {n["id"]: n for n in self.before[lang]["claimChecks"]}
            for check in doc["claimChecks"]:
                self.assertEqual(check["evidence_linkage_semantics"], "neutral_linkage_not_positive_support")
                for field in ("supporting_evidence", "qualifying_evidence"):
                    self.assertEqual(check.get(field), before[check["id"]].get(field))
                refs = set(check.get("supporting_evidence", [])) | set(check.get("qualifying_evidence", []))
                self.assertEqual({e["event_id"] for e in check["evidence_relations"]}, refs)
            for old, new in zip(self.before[lang]["claims"], doc["claims"]):
                self.assertEqual(old.get("qualifying_evidence"), new.get("qualifying_evidence"))

    def test_finance_scope_and_status(self):
        for lang, doc in self.after.items():
            check = next(c for c in doc["claimChecks"] if c["id"] == repair.FINANCE)
            old = next(c for c in self.before[lang]["claimChecks"] if c["id"] == repair.FINANCE)
            self.assertEqual((check["status"], check["confidence"]), (old["status"], old["confidence"]))
            for phrase in ("draft", "implementation is not established", "gathering information", "had not yet been adopted", "not a claim"):
                self.assertIn(phrase, check["safe_wording_en"])

    def test_english_caveats_and_translation_provenance(self):
        for lang, doc in self.after.items():
            for check in doc["claimChecks"]:
                self.assertTrue(check.get("safe_wording_en") or check.get("safe_wording"))
                if check["id"] in repair.TRANSLATIONS:
                    self.assertTrue(check["audit_translation"]["source_text"])
                    self.assertFalse(check["audit_translation"]["independent_factcheck"])
                    self.assertEqual(check["safe_wording_en"], repair.TRANSLATIONS[check["id"]])

    def test_uk_actor_identity_and_counts(self):
        for doc in self.after.values():
            event = next(e for e in doc["events"] if e["id"] == repair.UK_EVENT)
            self.assertNotIn("US Treasury", event["actor_entities"])
            self.assertNotIn("US", event["actor_jurisdictions"])
            self.assertIn("UK Treasury Committee", event["actor_entities"])
            self.assertIn("government", event["actor_types"])
            for field in ("actor_types", "actor_entities", "actor_jurisdictions"):
                self.assertEqual(doc["counts"][field], dict(Counter(v for e in doc["events"] for v in e[field])))

    def test_actor_registry_exact_mapping_and_unresolved_records(self):
        for doc in self.after.values():
            entries = {a["actor"]: a for a in doc["entityRegistry"]["audit_actor_type_entries"]}
            taxonomy = set(doc["classifierTaxonomy"]["actors"]["type_labels"])
            targets = set(doc["migrationAudit"]["v051_added_event_ids"] + doc["migrationAudit"]["v052_added_event_ids"])
            self.assertEqual(len(targets), 93)
            typed, unresolved = 0, 0
            for event in doc["events"]:
                if event["id"] not in targets:
                    continue
                expected = {t for a in event["actor_entities"] if a in entries for t in entries[a]["actor_types"]}
                self.assertEqual(set(event["actor_types"]), expected)
                self.assertLessEqual(expected, taxonomy)
                if expected:
                    typed += 1
                else:
                    unresolved += 1
                    self.assertEqual(event["audit_actor_types"]["status"], "review_required")
            self.assertEqual((typed, unresolved), (82, 11))
            self.assertEqual(len(doc["auditRepair"]["actor_type_review_queue"]), 13)

    def test_actor_mapping_has_no_name_substring_fallback(self):
        doc = copy.deepcopy(self.before["ru"])
        event = next(e for e in doc["events"] if e["id"] == "SIG_2026_OPENAI_KERNEL_PIPELINE")
        event["actor_entities"] = ["Unknown OpenAI-like Research Government Company"]
        repair.repair_actors(doc)
        self.assertEqual(event["actor_types"], [])
        self.assertEqual(event["audit_actor_types"]["status"], "review_required")

    def test_invalid_taxonomy_fails_closed(self):
        doc = copy.deepcopy(self.before["ru"])
        del doc["classifierTaxonomy"]["actors"]["type_labels"]["company"]
        with self.assertRaisesRegex(ValueError, "Unknown actor type"):
            repair.repair_actors(doc)

    def test_backlinks_equal_all_incident_edges(self):
        for doc in self.after.values():
            incident = defaultdict(set)
            for edge in doc["edges"]:
                incident[edge["source"]].add(edge["id"])
                incident[edge["target"]].add(edge["id"])
            for node_id, node in repair.nodes(doc).items():
                self.assertEqual(set(node.get("edgeIds", [])), incident[node_id], node_id)
                self.assertEqual(len(node.get("edgeIds", [])), len(incident[node_id]))
            self.assertEqual(len(repair.nodes(doc)["THESIS_CORE"]["edgeIds"]), 39)

    def test_missing_backlink_is_detected(self):
        doc = copy.deepcopy(self.after["ru"])
        repair.nodes(doc)["THESIS_CORE"]["edgeIds"].pop()
        with self.assertRaisesRegex(ValueError, "backlinks"):
            repair.check_document(doc)

    def test_route_contract_explains_every_association(self):
        for doc in self.after.values():
            arcs = {a["id"] for a in doc["arcs"]}
            for event in doc["events"]:
                ordered = ([event["story_primary_arc_id"]] if event.get("story_primary_arc_id") else []) + event.get("story_secondary_arc_ids", [])
                self.assertEqual(event["route_eligible_arc_ids"], ordered)
                self.assertEqual(len(ordered), len(set(ordered)))
                gap = (set(event.get("arcIds", [])) & arcs) - set(ordered)
                self.assertLessEqual(gap, set(event.get("context_arc_ids", [])))
                self.assertFalse(set(ordered) & set(event.get("context_arc_ids", [])))
            boe = repair.nodes(doc)["SIG_2026_BOE_FRONTIER_AI_HARNESS_ENGINEERING"]
            self.assertNotIn("ARC_WORK_COMPETENCE_DISTRIBUTION", boe["route_eligible_arc_ids"])
            self.assertIn("ARC_WORK_COMPETENCE_DISTRIBUTION", boe["context_arc_ids"])

    def test_relation_association_alone_never_promotes_route(self):
        for relation in ("context_for", "supports_with_scope", "qualifies", "updates", "challenges"):
            doc = {"events": [{"id": "event", "arcIds": ["arc"]}], "arcs": [{"id": "arc", "key_nodes": []}], "edges": [{"id": "edge", "source": "event", "target": "claim", "relation": relation, "arc_id": "arc"}], "arcHierarchy": {}}
            repair.repair_routes(doc)
            self.assertEqual(doc["events"][0]["route_eligible_arc_ids"], [])
            self.assertEqual(doc["events"][0]["context_arc_ids"], ["arc"])
            doc["edges"][0].update(target="arc", relation="part_of_arc")
            repair.repair_routes(doc)
            self.assertEqual(doc["events"][0]["route_eligible_arc_ids"], ["arc"])

    def test_historical_context_overrides_direct_membership(self):
        for doc in self.after.values():
            by_id = repair.nodes(doc)
            arc = by_id[repair.CONTEXT_ARC]
            event = by_id[repair.CONTEXT_EVENT]
            self.assertNotIn(repair.CONTEXT_EVENT, arc["key_nodes"])
            self.assertIn(repair.CONTEXT_EVENT, arc["context_nodes"])
            self.assertNotIn(repair.CONTEXT_ARC, event["route_eligible_arc_ids"])
            self.assertIn("ARC_2021_STATE_INSTITUTIONALIZATION", event["route_eligible_arc_ids"])
            self.assertEqual((arc["start_date"], arc["end_date"]), ("2023-01-26", "2023-12-09"))
            self.assertEqual(arc["context_start_date"], "2021-04-21")

    def test_intervals_include_full_date_precision(self):
        for doc in self.after.values():
            by_id = repair.nodes(doc)
            for arc in doc["arcs"]:
                for node_id in arc["key_nodes"]:
                    if by_id[node_id]["kind"] == "event":
                        low, high = repair.date_bounds(by_id[node_id]["date"])
                        self.assertLessEqual(arc["start_date"], low)
                        self.assertLessEqual(high, arc["end_date"])
        self.assertEqual(repair.date_bounds("2024-02"), ("2024-02-01", "2024-02-29"))
        self.assertEqual(repair.date_bounds("2025"), ("2025-01-01", "2025-12-31"))
        with self.assertRaises(ValueError):
            repair.date_bounds("2025-02-30")

    def test_unreviewed_timeline_expansion_is_rejected(self):
        doc = {"events": [{"id": "event", "date": "2020-01-01"}], "arcs": [{"id": "new-timeline", "key_nodes": ["event"], "display_role": "timeline_lens", "start_date": "2023-01-01", "end_date": "2023-12-31"}]}
        with self.assertRaisesRegex(ValueError, "Unreviewed timeline expansion"):
            repair.repair_intervals(doc)

    def test_alias_contract_and_aggregate_edges(self):
        for doc in self.after.values():
            by_id = repair.nodes(doc)
            alias, canonical = by_id[repair.ALIAS], by_id[repair.CANONICAL]
            self.assertEqual(doc["record_aliases"], {repair.ALIAS: repair.CANONICAL})
            self.assertEqual(alias["canonical_event_id"], canonical["id"])
            self.assertTrue(alias["presentation_hidden"])
            self.assertFalse(canonical["presentation_hidden"])
            self.assertEqual(doc["auditRepair"]["presentation_counts"], {"events": 566, "stored_events": 567, "preserved_aliases": 1})
            incident = {e["id"] for e in doc["edges"] if {e["source"], e["target"]} & {repair.ALIAS, repair.CANONICAL}}
            self.assertEqual(set(canonical["canonical_edge_ids"]), incident)
            for edge in doc["edges"]:
                for endpoint in ("source", "target"):
                    if edge[endpoint] == repair.ALIAS:
                        self.assertEqual(edge["canonical_" + endpoint], repair.CANONICAL)
            self.assertEqual(alias["status"], "verified_as_reported")
            self.assertEqual(canonical["status"], "verified_as_reported")

    def test_duplicate_identity_change_rejected(self):
        doc = copy.deepcopy(self.before["ru"])
        repair.nodes(doc)[repair.ALIAS]["date"] = "2026-06-27"
        with self.assertRaisesRegex(ValueError, "Duplicate event evidence changed"):
            repair.repair_alias(doc)

    def test_typed_endpoints_and_full_reference_integrity(self):
        for doc in self.after.values():
            self.assertEqual(references(doc), doc["referenceIntegrity"])
            self.assertTrue(references(doc)["valid"])
            by_id = repair.nodes(doc)
            for edge in doc["edges"]:
                for endpoint in ("source", "target"):
                    actual = edge[endpoint + "_kind"]
                    actual = repair.KIND_ALIASES.get(actual, actual)
                    expected = by_id[edge[endpoint]]["kind"]
                    expected = repair.KIND_ALIASES.get(expected, expected)
                    self.assertEqual(actual, expected, edge["id"])

    def test_citation_objects_not_just_urls_are_preserved(self):
        for lang, doc in self.after.items():
            old = repair.nodes(self.before[lang])
            for node_id, node in repair.nodes(doc).items():
                self.assertEqual(Counter(repair.encoded(s) for s in repair.citation_records(old[node_id])), Counter(repair.encoded(s) for s in repair.citation_records(node)), node_id)
            sources = repair.nodes(doc)["scale-02"]["sources"]
            self.assertEqual(len(sources), 1)
            self.assertEqual(len(sources[0]["citation_variants"]), 2)
            self.assertNotEqual(sources[0]["citation_variants"][0]["title"], sources[0]["citation_variants"][1]["title"])

    def test_generic_citation_dedup_retains_multiplicity_and_metadata(self):
        doc = {col: [] for col in repair.NODE_COLLECTIONS}
        original = [{"url": "https://example.test/source", "title": "A", "date": "2020"}, {"url": "https://example.test/source", "title": "B", "checked_at": "2021"}, {"url": "https://example.test/source", "title": "B", "checked_at": "2021"}, {"title": "no URL"}]
        doc["events"] = [{"id": "event", "sources": copy.deepcopy(original)}]
        repair.repair_sources(doc)
        self.assertEqual(repair.citation_records(doc["events"][0]), original)
        once = copy.deepcopy(doc)
        repair.repair_sources(doc)
        self.assertEqual(doc, once)

    def test_missing_language_rejected_without_mutating_input(self):
        docs = {"ru": copy.deepcopy(self.before["ru"])}
        unchanged = copy.deepcopy(docs)
        with self.assertRaisesRegex(ValueError, "Both canonical"):
            repair.prepare_documents(docs)
        self.assertEqual(docs, unchanged)

    def test_concurrent_write_guard_preserves_both_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = {lang: json.dumps(doc).encode() for lang, doc in self.before.items()}
            for lang, payload in raw.items():
                (root / f"ai_power_storygraph_{lang}.json").write_bytes(payload)
            en = root / "ai_power_storygraph_en.json"
            en.write_bytes(b"concurrent edit")
            with self.assertRaisesRegex(ValueError, "Concurrent JSON change"):
                repair.write_documents(root, raw, self.after)
            self.assertEqual(en.read_bytes(), b"concurrent edit")
            self.assertEqual((root / "ai_power_storygraph_ru.json").read_bytes(), raw["ru"])

    def test_staging_failure_leaves_both_inputs_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = {lang: json.dumps(doc).encode() for lang, doc in self.before.items()}
            for lang, payload in raw.items():
                (root / f"ai_power_storygraph_{lang}.json").write_bytes(payload)
            with patch.object(repair.tempfile, "mkstemp", side_effect=OSError("disk unavailable")):
                with self.assertRaises(OSError):
                    repair.write_documents(root, raw, self.after)
            for lang in raw:
                self.assertEqual((root / f"ai_power_storygraph_{lang}.json").read_bytes(), raw[lang])

    def test_cli_apply_twice_is_byte_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for lang, doc in self.before.items():
                (root / f"ai_power_storygraph_{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
            command = [sys.executable, "-B", str(ROOT / "scripts/migrate_audit_repair.py"), "--root", str(root), "--apply"]
            first = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(first.stdout)["applied"])
            paths = list(root.glob("*.json")) + [root / repair.REVIEW_DIR / "migration-audit.json"]
            initial = {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths}
            second = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertFalse(json.loads(second.stdout)["changed"])
            self.assertEqual(initial, {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AuditDataTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.report:
        destination = args.report.resolve()
        allowed = (ROOT / repair.REVIEW_DIR).resolve()
        if not destination.is_relative_to(allowed):
            raise SystemExit("Test report must stay in the audit repair review directory")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({"passed": result.wasSuccessful(), "tests_run": result.testsRun,
            "failures": [(str(test), detail) for test, detail in result.failures],
            "errors": [(str(test), detail) for test, detail in result.errors],
            "skipped": [(str(test), reason) for test, reason in result.skipped]}, indent=2) + "\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
