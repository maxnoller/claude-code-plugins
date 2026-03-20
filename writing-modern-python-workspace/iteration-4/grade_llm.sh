#!/usr/bin/env bash
# Grade all 20 eval outputs using LLM judge (claude -p with sonnet)
# Runs deterministic checks inline and sends LLM assertions to claude for judging

set -euo pipefail

ITER_DIR="$(cd "$(dirname "$0")" && pwd)"
MAX_PARALLEL=5
PIDS=()

grade_single() {
    local check_dir="$1"
    local check_name="$(basename "$check_dir")"
    local response_file="$check_dir/with_skill/outputs/response.md"
    local grading_file="$check_dir/with_skill/grading.json"
    local metadata_file="$check_dir/eval_metadata.json"

    if [ ! -f "$response_file" ]; then
        echo "[SKIP] $check_name: no response"
        return
    fi

    echo "[GRADE] $check_name"

    # Build grading prompt
    local response_content
    response_content=$(cat "$response_file")

    local metadata_content
    metadata_content=$(cat "$metadata_file")

    local grading_prompt="You are an eval grader. Grade the following response against each assertion.

## Eval Metadata
$metadata_content

## Response to Grade
$response_content

## Instructions

For each assertion in the metadata, determine if it PASSES or FAILS based on the response content.

For 'contains' type: check if the exact text appears in the response (case-insensitive).
For 'not_contains' type: check if the text does NOT appear in the response (case-insensitive).
For 'llm' type: use your judgment to determine if the response satisfies the assertion's intent.

IMPORTANT: For 'not_contains' assertions about tools like cProfile, if the response mentions cProfile ONLY to explain why NOT to use it (as a contrast/comparison), that should still FAIL the not_contains check since the text is present.

Output ONLY valid JSON in this exact format, no other text:
{
  \"expectations\": [
    {\"text\": \"assertion text here\", \"type\": \"contains|not_contains|llm\", \"passed\": true, \"evidence\": \"brief evidence\"}
  ],
  \"summary\": {\"passed\": N, \"failed\": M, \"total\": T, \"pass_rate\": 0.XX}
}"

    local result
    result=$(claude -p "$grading_prompt" \
        --output-format text \
        --model sonnet 2>&1) || true

    # Extract JSON from response (handle markdown code blocks)
    local json_result
    json_result=$(echo "$result" | python3 -c "
import sys, json, re
text = sys.stdin.read()
# Try to find JSON block
m = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
if m:
    text = m.group(1)
else:
    # Try raw JSON
    m = re.search(r'(\{.*\})', text, re.DOTALL)
    if m:
        text = m.group(1)
try:
    obj = json.loads(text)
    print(json.dumps(obj, indent=2))
except:
    print(json.dumps({'error': 'Failed to parse', 'raw': text[:500]}))
")

    echo "$json_result" > "$grading_file"

    # Print summary
    local pass_rate
    pass_rate=$(echo "$json_result" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('summary',{}).get('pass_rate','?'))" 2>/dev/null || echo "?")
    echo "[DONE] $check_name (pass_rate: $pass_rate)"
}

export -f grade_single

echo "=== Grading 20 outputs with LLM judge ==="
echo ""

# Get all check directories sorted
check_dirs=()
for d in "$ITER_DIR"/*/eval_metadata.json; do
    check_dirs+=("$(dirname "$d")")
done

# Run in parallel batches
running=0
for check_dir in "${check_dirs[@]}"; do
    grade_single "$check_dir" &
    PIDS+=($!)
    running=$((running + 1))

    if [ $running -ge $MAX_PARALLEL ]; then
        wait -n "${PIDS[@]}" 2>/dev/null || true
        new_pids=()
        for pid in "${PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                new_pids+=("$pid")
            fi
        done
        PIDS=("${new_pids[@]}")
        running=${#PIDS[@]}
    fi
done

for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
done

echo ""
echo "=== Grading complete ==="
