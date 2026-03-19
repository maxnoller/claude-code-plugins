---
name: ai-agent-evals
description: Opinionated patterns for evaluating AI agents and LLM outputs (2026). Use this skill whenever writing, designing, or reviewing evals for AI agents, LLM pipelines, or model outputs. Trigger when the user mentions "evals", "evaluation", "LLM judge", "grading", "rubric", "test cases for AI", "benchmark", "agent testing", "pydantic-evals", "model quality", or asks how to measure whether an agent or LLM output is good. Also trigger when writing pytest tests that assess LLM-generated content, or when the user is iterating on prompts/skills and wants to know if they're improving.
---

# AI Agent Evals (2026)

Evals answer one question: is this getting better or worse? Without them you're guessing. These patterns share a philosophy: start with what you can check deterministically, add LLM judges only for what code can't measure, and let real failures — not speculation — drive what you test.

Every eval should exist because something broke or because you need to prove something works. Don't write evals for imaginary scenarios.

## Deterministic first, LLM judges second

Always reach for deterministic checks before LLM-based grading. Deterministic checks are fast, free, perfectly consistent, and easy to debug. Use them for everything they can cover:

- Did the agent call the right tools in the right order?
- Does the output parse as valid JSON/match a schema?
- Did it create the expected files?
- Is the token count within bounds?
- Does the output contain/exclude specific strings?

LLM judges handle what code can't: tone, relevance, whether an explanation actually makes sense, hallucination detection against source material. But they're slow, expensive, and non-deterministic — so layer them on top of deterministic checks, not instead of them.

```python
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

dataset = Dataset(
    cases=[Case(name="handles refund", inputs="I want a refund for order #123")],
    evaluators=[
        # LLM judge only for what code can't check
        LLMJudge(
            rubric="Response acknowledges the order number, expresses empathy, and provides clear next steps",
            include_input=True,
        )
    ],
)
```

See `references/deterministic-before-judges.md` for the full layering approach and when to use which.

## LLM-as-a-judge

Evaluation is easier than generation — a model that struggles to produce good output can often reliably judge it, because judging with both question and answer visible is a narrower task. Use this asymmetry deliberately.

Two types of judge, and picking the wrong one wastes effort:

- **Case-specific judges**: rubric tailored per test case. Use for regression tests, correctness checks, anything where "good" depends on the specific input.
- **One-size-fits-all judges**: single rubric across all cases. Use for universal qualities — tone, safety, style consistency, or validating a cheaper model against a capable one.

Write rubrics that specify both what success looks like AND what failure looks like. Always request reasoning (`include_reason=True`) so you can debug when the judge disagrees with you.

See `references/llm-as-a-judge.md` for rubric writing, context levels, evaluator selection, and the pydantic-evals implementation.

## Test cases from real failures

Don't invent eval scenarios. Collect them:

- Every user complaint becomes a test case proving the fix works
- Every prompt/skill iteration gets a before/after eval
- Every surprising agent behavior — good or bad — gets captured

Start with 10-20 cases covering: explicit triggers, implicit triggers, edge cases, and negative controls (inputs that should NOT trigger the behavior). Keep test cases permanently — they prevent regressions when models or prompts change.

See `references/eval-driven-iteration.md` for the full workflow from failure to test case to confidence.
