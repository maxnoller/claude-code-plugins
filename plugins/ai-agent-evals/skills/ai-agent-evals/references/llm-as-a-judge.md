# LLM-as-a-Judge

## Why

Evaluation is easier than generation. When judging, the model has both the question and the answer in front of it — a much narrower task than open-ended generation. Research shows 80%+ agreement between LLM judges and human preferences on many tasks. The same model that generated flawed content can often catch its own errors when asked to evaluate.

This asymmetry is the whole point: you can use a capable model as a judge to validate outputs from cheaper/faster models, or to check qualities that code can't measure — relevance, coherence, tone, hallucination.

## Two types of judge

### Case-specific judges

Rubric tailored per test case. The rubric knows what the right answer should look like for this specific input.

```python
Case(
    name="refund-policy-question",
    inputs="What's your refund policy for digital products?",
    expected_output="Explains 30-day refund window, no questions asked",
    evaluators=[
        LLMJudge(
            rubric="Response correctly states the 30-day refund window and mentions it applies to digital products",
            include_input=True,
            include_expected_output=True,
        )
    ],
)
```

Use for: regression tests, correctness checks, anything where "good" depends on the specific input.

### One-size-fits-all judges

Single rubric applied across every test case in the dataset.

```python
Dataset(
    cases=[...],
    evaluators=[
        LLMJudge(rubric="Response maintains a professional, empathetic tone without being condescending")
    ],
)
```

Use for: tone/style consistency, safety compliance, validating a cheaper model against a capable judge.

### Picking the right one

If the quality you're checking is universal (should apply identically to every case), use one-size-fits-all. If "good" depends on what was asked, use case-specific. When in doubt, case-specific — it's more work but catches more.

## Writing rubrics

Progress from vague to specific:

- **Bad**: "Response is good"
- **Better**: "Response answers the user's question"
- **Best**: "Response acknowledges the specific order number mentioned, expresses empathy for the situation, and provides exactly one clear next step the user can take immediately"

Specify both success AND failure conditions:

```python
LLMJudge(
    rubric=(
        "PASS if the response explains the concept using an analogy and avoids jargon. "
        "FAIL if the response uses technical terms without defining them, "
        "or if the analogy is misleading or inaccurate."
    ),
)
```

Binary pass/fail works best for absolute criteria (policy compliance, factual correctness). Numeric scores work for tracking quality trends over time.

## Context levels

Give the judge the minimum context it needs:

- **Output only**: style checks, format validation, tone
- **Input + output** (`include_input=True`): relevance, completeness, appropriateness
- **Input + output + expected** (`include_expected_output=True`): correctness against a known answer

More context isn't always better — excess context can distract the judge from the actual criteria.

## Always request reasoning

```python
LLMJudge(
    rubric="...",
    assertion={"include_reason": True, "evaluation_name": "tone_check"},
)
```

Without reasoning, you can't tell if the judge passed for the right reasons or failed due to a bad rubric. Reasoning is how you debug your evals — which you will need to do, because rubrics are prompts and prompts need iteration.

## Where LLM judges excel

- **Hallucination detection**: give the judge source material via `include_input=True`, let it verify claims
- **Style and tone**: clear criteria that resist programmatic checking
- **Context-dependent quality**: rules easy to articulate per-case but hard to generalize

## Where NOT to use LLM judges

Use deterministic checks instead for:
- Type/schema validation (Pydantic models)
- Format checks (JSON, regex, length)
- Exact value matching
- Tool call verification
- File existence

These are faster, cheaper, perfectly consistent, and easier to debug.
