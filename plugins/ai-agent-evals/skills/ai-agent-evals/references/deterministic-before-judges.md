# Deterministic First, LLM Judges Second

## Why

LLM judges are slow, cost tokens, and return different results across runs. Deterministic checks are instant, free, and perfectly reproducible. Most eval suites overuse LLM judges for things that code can check trivially — parsing, file existence, tool call sequences, schema conformance. This wastes time and introduces flakiness where none is needed.

The rule: if you can check it with code, check it with code. LLM judges are for semantics — meaning, tone, relevance, coherence. Everything else has a deterministic check.

## The layering approach

Build eval checks in this order, stopping when you have enough confidence:

### Layer 1: Structure and format (always)

Did the output arrive in the right shape?

```python
import json
from pydantic import TypeAdapter

# schema conformance
adapter = TypeAdapter(ExpectedOutput)
result = adapter.validate_json(agent_output)

# file existence
assert Path("output/report.md").exists()

# required fields present
assert "summary" in result
assert len(result["items"]) > 0
```

### Layer 2: Tool and process checks (for agents)

Did the agent take the right steps?

```python
# parse JSONL event stream from agent execution
events = parse_agent_events(run_output)

# correct tools called
tool_calls = [e["tool"] for e in events if e["type"] == "tool_call"]
assert "search_docs" in tool_calls
assert "delete_production_db" not in tool_calls

# reasonable efficiency
assert len(tool_calls) < 20, "agent is thrashing"
```

### Layer 3: Content checks (when possible deterministically)

Things you might think need an LLM judge but often don't:

```python
# keyword/phrase presence
assert "order #123" in response.lower()
assert "refund" in response.lower()

# length bounds
assert 50 < len(response.split()) < 500

# regex patterns for specific formats
import re
assert re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", response)  # contains a date

# no hallucinated URLs
urls = re.findall(r"https?://\S+", response)
for url in urls:
    assert url in known_valid_urls
```

### Layer 4: LLM judge (for semantics only)

What's left — meaning, tone, coherence, helpfulness — goes to an LLM judge:

```python
from pydantic_evals.evaluators import LLMJudge

# good: specific, observable criteria
LLMJudge(rubric="Response explains the return policy in plain language without legal jargon")

# bad: vague, subjective
LLMJudge(rubric="Response is good and helpful")
```

## When to skip layers

- Prototyping: start at layer 4, backfill deterministic checks as the eval stabilizes
- One-off checks: an LLM judge is fine if you're running it once to validate a change
- Subjective quality: if the whole point is "does this sound right", there's no deterministic shortcut

## When to add layers

- Flaky evals: if an LLM judge passes/fails inconsistently, find the deterministic check hiding inside it
- Slow eval suites: deterministic checks run in milliseconds, LLM judges take seconds
- Debugging: when an eval fails, deterministic checks point to the exact problem; LLM judges give you a paragraph of explanation that may or may not be right
