# Eval-Driven Iteration

## Why

Without evals, prompt/skill iteration is vibes. You change something, try a few inputs manually, and ship it hoping nothing broke. With evals, you change something, run the suite, and know exactly what improved and what regressed. The difference compounds — after 10 iterations, the vibe-based approach has drifted in unknowable ways while the eval-based approach has a clear record of what works.

## The cycle

1. **Something breaks** — a user complains, an agent does something surprising, a skill produces wrong output
2. **Capture it as a test case** — the exact input, what happened, what should have happened
3. **Write the eval** — deterministic checks first, LLM judge if needed
4. **Fix the issue** — change the prompt/skill/tool
5. **Run the suite** — the new case passes, old cases still pass
6. **Keep the case forever** — it prevents this regression from ever returning

The test suite only grows. Never delete a passing test case unless the feature it tests no longer exists.

## Building your initial test set

Start with 10-20 cases across four categories:

### Explicit triggers
Direct requests that obviously should invoke the behavior:
```
"Use the code review skill to check this PR"
"Run evals on the latest changes"
```

### Implicit triggers
Realistic requests that should trigger the behavior without naming it:
```
"Can you check if this function handles edge cases properly?"
"I'm worried the refactor broke something"
```

### Edge cases
Unusual but valid inputs that test boundaries:
```
"Review this file but it's 10,000 lines"
"The test output is in a language other than English"
```

### Negative controls
Similar requests that should NOT trigger the behavior:
```
"Write a code review tool from scratch"  # creating, not using
"What's a good eval framework?"          # asking about, not running
```

## From manual validation to automation

### Phase 1: Manual (first 3-5 runs)
Run the agent manually. Watch what it does. Note:
- Did it invoke the right tools?
- Did it skip steps or repeat them?
- Were there hidden assumptions about the environment?

### Phase 2: Scripted (next 10-20 runs)
Automate execution but review results by hand. This is where you discover which checks can be deterministic:
- "It should create a file" → `assert Path(...).exists()`
- "It should call the search tool" → check the event log
- "The summary should be reasonable" → this one needs a judge

### Phase 3: CI (ongoing)
Full automation. Deterministic checks gate the build. LLM judge results get logged and reviewed periodically but don't block.

## Defining success before you start

Before writing the skill/prompt, define what success looks like across four dimensions:

- **Outcome**: did it complete the task? (file created, question answered, bug fixed)
- **Process**: did it take reasonable steps? (right tools, right order, no thrashing)
- **Style**: does the output match conventions? (format, tone, structure)
- **Efficiency**: did it waste resources? (token count, tool call count, time)

Not every eval needs all four. But knowing which dimensions matter prevents eval sprawl — you only write checks for what you actually care about.

## When to add more cases

- A new failure mode appears (always)
- You're about to change the prompt/skill significantly (before the change)
- Confidence is low on a specific category (targeted expansion)
- You're switching models (run the full suite on the new model before committing)

## When NOT to add more cases

- You already have 5+ cases covering the same behavior pattern
- The scenario is speculative ("what if someone asks in Klingon?")
- The check would be so vague it passes everything
