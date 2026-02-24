---
name: sessions-review
description: Review recent sessions for the current project to identify recurring patterns, systemic issues, and improvements across multiple sessions.
context: fork
disable-model-invocation: true
allowed-tools: Glob, Grep, Read
---

# Sessions Review

Session ID: ${CLAUDE_SESSION_ID}

## Step 1 — Find Project Sessions

Use Glob to locate the current session file:

```
~/.claude/projects/**/${CLAUDE_SESSION_ID}.jsonl
```

Take its parent directory and glob all `*.jsonl` files there — these are all sessions for this project. Sort by modification time and take the 10 most recent (excluding the current session).

## Step 2 — Read Each Session

For each session file, use Grep to extract conversation turns (`"type":"user"` and `"type":"assistant"` lines) to reconstruct what happened. Note the timestamp and approximate length of each session.

## Step 3 — Identify Cross-Session Patterns

Look for patterns that appear across multiple sessions — single-session issues belong in a regular `/session-review`. Focus on:

**Recurring mistakes** — the same wrong assumption or error appearing in 2+ sessions. Strong signal that something needs fixing in the codebase, tooling, or context file.

**Persistent friction** — the same awkward workflow showing up repeatedly. A script or hook could likely automate it.

**Knowledge gaps** — things the agent keeps having to look up or ask about that should be self-evident from the code.

**Drift** — something that worked well in early sessions but degraded later, or vice versa.

**What's consistently smooth** — patterns worth preserving.

## Step 4 — Classify and Report

For each finding, assign exactly one of:

- **Fix in codebase** — recurring wrong assumption that better types, naming, or structure would prevent
- **Add tooling / script / MCP** — repeated manual steps across sessions
- **Add to context file** — consistent mistake that cannot be fixed in code (rare)
- **One-off** — appears in only one session, not a systemic issue

**Output format:**

Sessions analyzed: N (date range)

**Recurring findings** (seen in 2+ sessions, prioritized by frequency and impact):
- Pattern (sessions affected, e.g. "3/5 sessions")
- Classification
- Concrete action

**What's consistently smooth** (brief)

## Principle

A pattern appearing once is noise. Appearing twice is a coincidence. Appearing three times is a system problem — fix the system, not the symptoms.
