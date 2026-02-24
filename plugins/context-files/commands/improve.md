---
description: Review recent sessions and suggest improvements to the project's Claude Code setup (CLAUDE.md, hooks, skills, MCP, settings)
argument-hint: "[number-of-sessions]"
allowed-tools: ["Task", "Read", "Write", "Edit", "Glob", "Grep", "Bash", "AskUserQuestion"]
---

# Improve Claude Code Setup

Review recent conversations for this project, identify recurring friction, and propose concrete changes to the Claude Code configuration.

## Arguments

`$ARGUMENTS` — number of recent sessions to review (default: 5).

## Step 1 — Discover Project Sessions

Find the current project's session directory:

```
~/.claude/projects/**/${CLAUDE_SESSION_ID}.jsonl
```

Take the parent directory. List all `*.jsonl` files, sort by modification time (use `ls -t`), and take the N most recent (excluding the current session).

## Step 2 — Explore Sessions

Use the **Task** tool to spawn the `context-files:session-explorer` agent with a prompt like:

```
Analyze these session files for recurring patterns:

Directory: [path from step 1]
Files (most recent first):
- [file1.jsonl]
- [file2.jsonl]
- ...

For each file, use Grep to extract lines containing "type":"user" that have text content, and "type":"assistant" with "type":"text". Focus on what went wrong or was awkward — skip tool calls.

Return findings using the output format from your instructions.
```

## Step 3 — Read Current Setup

Read the project's current Claude Code configuration:

- `CLAUDE.md`, `CLAUDE.local.md`
- `.claude/settings.json`, `.claude/settings.local.json`
- `.claude/rules/*.md`
- `.claude/skills/*/SKILL.md`
- `.claude/agents/*.md`
- `.mcp.json`
- `AGENTS.md`

Note what already exists and what's absent.

## Step 4 — Map Findings to Improvements

For each finding from the explorer, propose a concrete improvement using this mapping:

| Finding Type | Likely Fix |
|---|---|
| Repeated mistakes about conventions | Add targeted line to `CLAUDE.md` or `.claude/rules/` |
| Repeated mistakes about code structure | Fix the code (better types, naming, docs) |
| Workflow friction (manual steps) | Create a hook (`PostToolUse`, `Stop`) or script |
| Workflow friction (repetitive commands) | Create a skill or command |
| Wrong assumptions about the project | Add to `CLAUDE.md` if not inferable from code |
| Missing knowledge about external tools | Add an MCP server or skill with reference docs |
| Token waste from unclear code | Improve code clarity (types, naming) |
| Token waste from missing context | Add targeted `CLAUDE.md` entry or subdirectory `CLAUDE.md` |

For each improvement, provide:
- **What**: The exact change (specific line, file to create, hook JSON)
- **Why**: Which sessions and what pattern triggered this
- **Impact**: High / Medium / Low

## Step 5 — Present and Apply

Group by type, highest impact first:

1. **CLAUDE.md changes** — lines to add or remove
2. **New hooks** — hook configurations to add
3. **New skills/commands** — skill files to create
4. **MCP servers** — servers to configure
5. **Code improvements** — report only, don't apply
6. **Settings changes** — `.claude/settings.json` modifications

Ask the user which improvements to apply. Apply approved changes. Verify the result reads cleanly.

## Principles

- Prefer fixing root causes over adding context. Better types/naming > CLAUDE.md lines.
- Only add to CLAUDE.md what can't be fixed in the codebase — keep it under 50 lines.
- Hooks > manual workflows — if the agent keeps doing something manually, automate it.
- A pattern in 1 session is noise. 3+ sessions is a system problem — fix the system.
- Be specific. "Add to CLAUDE.md: `Run moon check after editing moon.yml`" — not "consider adding a reminder."
