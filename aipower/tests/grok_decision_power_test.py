#!/usr/bin/env python3
"""Reproduce v0.43 and check preservation, dates, sources and semantic boundaries."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_agent_boundaries import migrate as boundaries
from migrate_grok_decision_power import CHAT, COURT, MERIDIAN, RECORDS, migrate
from validate import references


def main():
    report = {"version": "0.43", "checks": []}
    def ok(label, condition):
        if not condition:
            raise AssertionError(label)
        report["checks"].append(label)
    packet = json.loads((ROOT / "review/agent-boundaries-september-2026/candidates.json").read_text())
    docs = {}
    for lang, filename in [("ru", "ai-power-atlas-ru.html"), ("en", "ai-power-atlas.html")]:
        raw = subprocess.check_output(["git", "show", f"{packet['meta']['atlas_commit_reviewed']}:aipower/ai_power_storygraph_{lang}.json"], cwd=ROOT)
        ok(lang + ": pinned v0.41 baseline", hashlib.sha256(raw).hexdigest() == packet["meta"]["base_sha256"][lang])
        previous = boundaries(json.loads(raw), packet)
        expected = migrate(copy.deepcopy(previous))
        expected["migrationAudit"]["v043_base_sha256"] = hashlib.sha256((json.dumps(previous, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()
        doc = json.loads((ROOT / f"ai_power_storygraph_{lang}.json").read_text())
        docs[lang] = doc
        ok(lang + ": full deterministic reproduction", doc == expected)
        ev = {e["id"]: e for e in doc["events"]}
        links = {"edgeIds", "arcIds", "arcFamilyIds", "relationTypes"}
        ok(lang + ": every prior event preserved", all({k:v for k,v in e.items() if k not in links} == {k:v for k,v in ev[e['id']].items() if k not in links} for e in previous["events"]))
        ok(lang + ": every prior edge preserved", all(e in doc["edges"] for e in previous["edges"]))
        ok(lang + ": exactly three new events", set(ev) - {e['id'] for e in previous['events']} == {CHAT, COURT, MERIDIAN})
        ok(lang + ": no claims lost or modified", doc["claims"] == previous["claims"] and doc["claimChecks"] == previous["claimChecks"])
        ok(lang + ": no new arcs", [a['id'] for a in doc['arcs']] == [a['id'] for a in previous['arcs']])
        ok(lang + ": all graph references resolve", references(doc) == doc["referenceIntegrity"] and doc["referenceIntegrity"]["valid"])
        ok(lang + ": exact month without invented day", ev[CHAT]["date"] == "2025-12" and ev[CHAT]["date_precision"] == "month" and ev[CHAT]["disclosed_at"] == "2026-10-01")
        ok(lang + ": eyewitness is not confirmed causation", ev[CHAT]["confidence"] == "C" and ev[CHAT]["status"] == "reported_unnamed_eyewitness" and ev[CHAT]["delegated_authority"] == "not_established")
        ok(lang + ": court filing not autonomous military action", ev[COURT]["artifact_kind"] == "memorandum" and ev[COURT]["delegated_authority"] == "not_applicable" and ev[COURT]["normative_force"] == "not_applicable" and ev[COURT]["operational_event_date"] is None)
        ok(lang + ": Meridian is only an announced study", ev[MERIDIAN]["implementation_stage"] == "announced" and ev[MERIDIAN]["numbers"] == {"study_deadline_days":120,"co_leads":3} and ev[MERIDIAN]["cyber_role_ids"] == [])
        for r in RECORDS:
            e = ev[r['id']]
            ok(lang + ": no unsupported cyber role " + e['id'], e['cyber_role_ids'] == [])
            ok(lang + ": bilingual fields " + e['id'], all(e[k] == e[k+'_'+lang] and e[k+'_ru'] and e[k+'_en'] for k in ['title','summary','caveat','safe_wording','editorial_rationale']))
            ok(lang + ": critical-decision navigation " + e['id'], e['id'] in doc['criticalDecisionUse']['military_state_security'])
            ok(lang + ": no fabricated causal edge " + e['id'], not any(x['source']==e['id'] and x['relation'] in ['causes','accelerates_governance'] for x in doc['edges']))
        for aid in {a for r in RECORDS for a in r['arcs']}:
            arc = next(a for a in doc['arcs'] if a['id']==aid)
            dates = [ev[i]['date'] for i in arc['key_nodes'] if i in ev]
            ok(lang + ": chronological arc " + aid, dates == sorted(dates))
        html = (ROOT / filename).read_text()
        embedded = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S)
        ok(lang + ": HTML parity", embedded is not None and json.loads(embedded.group(1)) == doc)
        try:
            migrate(copy.deepcopy(doc))
        except ValueError:
            rejected = True
        else:
            rejected = False
        ok(lang + ": repeat migration rejected", rejected)
    for collection in ['events','edges','sourceIndex']:
        ok('bilingual IDs: '+collection, [x['id'] for x in docs['ru'][collection]] == [x['id'] for x in docs['en'][collection]])
    report.update(passed=True, assertions=len(report['checks']))
    (ROOT / 'review/grok-decision-power-tests.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"Passed {report['assertions']} targeted checks")


if __name__ == '__main__':
    main()
