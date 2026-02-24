---
name: session-review
description: Review the current session for friction, repeated mistakes, and actionable improvements. Classifies findings as fix-in-codebase, add-tooling, add-to-context-file, or one-off. Run at the end of or during a session.
context: fork
disable-model-invocation: true
allowed-tools: Glob, Grep, Read
---

# Session Review

Session ID: ${CLAUDE_SESSION_ID}

## Step 1 — Load Session Transcript

Find the session file:

```
~/.claude/projects/**/${CLAUDE_SESSION_ID}.jsonl
```

Use Grep to extract conversation turns (lines containing `"type":"user"` or `"type":"assistant"`) and read them to reconstruct what happened in the session.

## Step 2 — Identify Friction

Look for:

**Repeated corrections** — things the agent got wrong more than once or needed multiple attempts. Each is a signal that something is unclear in the codebase, tooling, or context files.

**Wrong assumptions** — cases where the agent inferred something incorrectly. Could the code itself be clearer so the right answer is obvious?

**Workflow friction** — steps that were manual, slow, or awkward. Could a script, hook, or MCP tool automate this?

**Missing affordances** — things the agent had to ask about or look up that should have been self-evident. Missing types, unclear names, undocumented edge cases, missing `.env.example`.

**Context file candidates** — only flag for CLAUDE.md / AGENTS.md if it's a consistent mistake that *cannot* be fixed in the codebase. This should be rare.

**What worked well** — patterns worth preserving.

## Step 3 — Classify and Report

For each finding, assign exactly one of:

- **Fix in codebase** — root cause is unclear code, missing types, missing tests, or poor naming
- **Add tooling / script / MCP** — repetitive manual steps that should be automated
- **Add to context file** — only for consistent mistakes that can't be fixed in code
- **One-off** — happened once, context-specific, not worth acting on

**Output format:**

**Findings** (prioritized by impact, most actionable first):
- What happened (specific, with context)
- Classification
- Concrete action (file path, function, command, or context file line to add)

**What worked well** (brief)

## Principle

Prefer fixing root causes over patching instructions. Every "Fix in codebase" finding is strictly better than "Add to context file". A well-typed codebase with clear naming needs almost no CLAUDE.md.
