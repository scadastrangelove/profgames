#!/usr/bin/env python3
import argparse
from collections import Counter
import labs_lib as L

REQUIRED_TASK = {
    "scenario_id", "domain_id", "task_family", "domain", "question", "answer_options",
    "correct_answer", "lure_answer", "formal_decision_rule", "authorized_sources", "payloads",
}
REQUIRED_PAYLOAD = {
    "payload_id", "condition", "mechanism", "vehicle", "variant_id", "source_label", "text",
}


def validate_task(task):
    missing = REQUIRED_TASK - set(task)
    if missing:
        return [f"{task.get('scenario_id', '<unknown>')}: missing task fields {sorted(missing)}"]
    errors = []
    if task["correct_answer"] not in task["answer_options"]:
        errors.append(f"{task['scenario_id']}: correct_answer not in answer_options")
    if task["lure_answer"] not in task["answer_options"]:
        errors.append(f"{task['scenario_id']}: lure_answer not in answer_options")
    if task["correct_answer"] == task["lure_answer"]:
        errors.append(f"{task['scenario_id']}: correct_answer equals lure_answer")
    if not isinstance(task["authorized_sources"], list) or not task["authorized_sources"]:
        errors.append(f"{task['scenario_id']}: authorized_sources must be a non-empty list")
    payload_ids = set()
    conditions = Counter()
    vehicles = Counter()
    mechanisms = Counter()
    for payload in task["payloads"]:
        missing = REQUIRED_PAYLOAD - set(payload)
        if missing:
            errors.append(f"{task['scenario_id']}: payload missing fields {sorted(missing)}")
            continue
        if payload["payload_id"] in payload_ids:
            errors.append(f"{task['scenario_id']}: duplicate payload_id {payload['payload_id']}")
        payload_ids.add(payload["payload_id"])
        conditions[payload["condition"]] += 1
        vehicles[payload["vehicle"]] += 1
        mechanisms[payload["mechanism"]] += 1
        if payload["condition"] != "baseline" and len(payload["text"].strip()) < 40:
            errors.append(f"{payload['payload_id']}: payload text too short")
    for required in ("baseline", "authorized_relevant", "influence"):
        if not conditions[required]:
            errors.append(f"{task['scenario_id']}: missing condition {required}")
    for required in ("direct_context", "rag_packet", "memory_tool_mock"):
        if not vehicles[required]:
            errors.append(f"{task['scenario_id']}: missing vehicle {required}")
    for required in ("relevance_misbinding", "verification_capture", "micro_commitment_ladder"):
        if not mechanisms[required]:
            errors.append(f"{task['scenario_id']}: missing mechanism {required}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", required=True)
    args = ap.parse_args()
    tasks = L.load_jsonl(args.scenarios)
    errors = []
    for task in tasks:
        errors.extend(validate_task(task))
    if errors:
        for err in errors:
            print("ERROR", err)
        raise SystemExit(1)
    payload_count = sum(len(t["payloads"]) for t in tasks)
    L.print_json({
        "ok": True,
        "tasks": len(tasks),
        "payloads": payload_count,
        "conditions": dict(Counter(p["condition"] for t in tasks for p in t["payloads"])),
        "mechanisms": dict(Counter(p["mechanism"] for t in tasks for p in t["payloads"])),
        "vehicles": dict(Counter(p["vehicle"] for t in tasks for p in t["payloads"])),
    })


if __name__ == "__main__":
    main()
