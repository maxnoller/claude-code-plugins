---
name: session-review
description: Review the current session for friction, repeated mistakes, and actionable improvements. Classifies findings as fix-in-codebase, add-tooling, add-to-CLAUDE.md, or one-off. Run at the end of or during a session.
allowed-tools: Read, Glob, Grep
---

# Session Review

Look back through this conversation from the beginning and identify friction, repeated mistakes, and patterns worth improving. The goal is actionable findings — not observations.

## What to Look For

**Repeated corrections**
Things Claude got wrong more than once, or needed multiple attempts. Each is a signal that something is unclear in the codebase, tooling, or CLAUDE.md.

**Wrong assumptions**
Cases where Claude inferred something incorrectly. Could the code itself be clearer — better types, naming, structure — so the right answer is obvious?

**Workflow friction**
Steps that were manual, slow, or awkward. Could a script, hook, or MCP tool automate this?

**Missing affordances**
Things Claude had to ask about or look up that should have been self-evident from the code. Missing types, unclear function names, undocumented edge cases, missing `.env.example`.

**CLAUDE.md candidates**
Only flag for CLAUDE.md if it's a consistent mistake Claude makes that *cannot* be fixed in the codebase. This should be rare.

**What worked well**
Note smooth patterns worth preserving or repeating.

## Classification

For each finding, assign exactly one of:

- **Fix in codebase** — root cause is unclear code, missing types, missing tests, or poor naming
- **Add tooling / script / MCP** — repetitive manual steps that should be automated
- **Add to CLAUDE.md** — only for consistent mistakes that can't be fixed in code
- **One-off** — happened once, context-specific, not worth acting on

## Output Format

**Findings** (prioritized by impact, most actionable first):

For each finding:
- What happened (specific, with context from the session)
- Classification
- Concrete action to take (file path, function, command, or CLAUDE.md line)

**What worked well** (brief)

## Principle

Prefer fixing root causes over patching instructions. Every finding classified as "Fix in codebase" is strictly better than one classified as "Add to CLAUDE.md". A well-typed, well-tested codebase with clear naming needs almost no CLAUDE.md.
