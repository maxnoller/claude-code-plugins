#!/usr/bin/env bash
# Run all 20 skill quality checks in parallel using claude -p
# Each check runs with the writing-modern-python skill loaded

set -euo pipefail

ITER_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_FILE="/home/max/projects/claude-code-plugins/plugins/writing-modern-python/skills/writing-modern-python/SKILL.md"
MAX_PARALLEL=5
PIDS=()

run_single() {
    local check_dir="$1"
    local check_name="$(basename "$check_dir")"
    local metadata="$check_dir/metadata.json"
    local output_dir="$check_dir/with_skill/outputs"
    local timing_file="$check_dir/with_skill/timing.json"

    # Extract prompt from metadata
    local prompt
    prompt=$(python3 -c "import json; print(json.load(open('$check_dir/eval_metadata.json'))['prompt'])")

    # Build system prompt file with skill content
    local sys_prompt_file="$check_dir/system_prompt.txt"
    {
        echo "You are a Python expert. The user is asking you a Python development question. Answer it directly with code and explanation."
        echo ""
        echo "Apply these patterns when generating your response:"
        echo ""
        cat "$SKILL_FILE"
        echo ""
        echo "IMPORTANT: Output your response as if you are directly answering the user. Include code blocks and explanations."
    } > "$sys_prompt_file"

    echo "[START] $check_name"
    local start_time
    start_time=$(date +%s%3N)

    # Run claude -p with the skill as system prompt
    local output
    output=$(claude -p "$prompt" \
        --append-system-prompt "$(cat "$sys_prompt_file")" \
        --output-format text \
        --model sonnet 2>&1) || true

    local end_time
    end_time=$(date +%s%3N)
    local duration_ms=$((end_time - start_time))
    local duration_s=$(python3 -c "print(round($duration_ms / 1000, 1))")

    # Save output
    echo "$output" > "$output_dir/response.md"

    # Save timing
    cat > "$timing_file" << TIMING_EOF
{"total_tokens": 0, "duration_ms": $duration_ms, "total_duration_seconds": $duration_s}
TIMING_EOF

    echo "[DONE] $check_name (${duration_s}s)"
}

export -f run_single

echo "=== Running 20 checks with max $MAX_PARALLEL parallel ==="
echo ""

# Get all check directories sorted
check_dirs=()
for d in "$ITER_DIR"/*/eval_metadata.json; do
    check_dirs+=("$(dirname "$d")")
done

# Run in parallel batches
running=0
for check_dir in "${check_dirs[@]}"; do
    run_single "$check_dir" &
    PIDS+=($!)
    running=$((running + 1))

    if [ $running -ge $MAX_PARALLEL ]; then
        # Wait for any one to finish
        wait -n "${PIDS[@]}" 2>/dev/null || true
        # Clean up finished PIDs
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

# Wait for remaining
for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
done

echo ""
echo "=== All checks complete ==="
