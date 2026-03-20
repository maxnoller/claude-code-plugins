#!/usr/bin/env python3
"""Run deterministic (contains/not_contains) assertions against eval outputs."""

import json
import sys
from pathlib import Path

iter_dir = Path(__file__).parent

results = {}

for eval_dir in sorted(iter_dir.iterdir()):
    metadata_file = eval_dir / "eval_metadata.json"
    if not metadata_file.exists():
        continue

    metadata = json.loads(metadata_file.read_text())
    eval_name = metadata["eval_name"]
    response_file = eval_dir / "with_skill" / "outputs" / "response.md"

    if not response_file.exists():
        print(f"SKIP {eval_name}: no response file")
        continue

    response = response_file.read_text().lower()

    det_results = []
    for assertion in metadata["assertions"]:
        atype = assertion.get("type", "llm")
        text = assertion["text"]

        if atype == "contains":
            passed = text.lower() in response
            det_results.append({
                "text": text,
                "type": "contains",
                "passed": passed,
                "evidence": f"{'Found' if passed else 'NOT found'} in response"
            })
        elif atype == "not_contains":
            passed = text.lower() not in response
            det_results.append({
                "text": text,
                "type": "not_contains",
                "passed": passed,
                "evidence": f"{'Correctly absent' if passed else 'FOUND (should be absent)'} in response"
            })

    results[eval_name] = det_results

# Print summary
total_pass = 0
total_fail = 0
total = 0

print("\n=== Deterministic Assertion Results ===\n")

for eval_name, assertions in results.items():
    if not assertions:
        continue
    passed = sum(1 for a in assertions if a["passed"])
    failed = len(assertions) - passed
    total_pass += passed
    total_fail += failed
    total += len(assertions)

    status = "PASS" if failed == 0 else "FAIL"
    print(f"[{status}] {eval_name}: {passed}/{len(assertions)}")

    for a in assertions:
        marker = "+" if a["passed"] else "X"
        print(f"  [{marker}] {a['type']}: \"{a['text']}\" - {a['evidence']}")

print(f"\n=== Total: {total_pass}/{total} passed ({total_fail} failed) ===")

# Save results
output_file = iter_dir / "deterministic_results.json"
output_file.write_text(json.dumps(results, indent=2))
print(f"\nSaved to {output_file}")
