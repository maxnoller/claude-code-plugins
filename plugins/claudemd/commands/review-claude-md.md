---
name: review-claude-md
description: Review and optimize CLAUDE.md files in the current project. Classifies each line as KEEP, REMOVE, or MOVE using the core test — would removing this cause Claude to make mistakes?
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Review CLAUDE.md

Audit the CLAUDE.md file(s) in this project and recommend cuts. Apply the minimal-context principles — CLAUDE.md should only contain what prevents consistent mistakes, not document the project.

## Core Test

For every line: **"Would removing this cause Claude to make mistakes?"** If no — cut it.

## Process

### 1. Find and Read All CLAUDE.md Files

Use Glob to find all CLAUDE.md and CLAUDE.local.md files:

```
CLAUDE.md, CLAUDE.local.md, .claude/CLAUDE.md, **/CLAUDE.md (excluding node_modules)
```

Read each one in full.

### 2. Classify Every Section

For each section or line, assign one of:

- **KEEP** — directly prevents a mistake Claude would otherwise make (wrong command, wrong URL, non-obvious coding rule, files not to touch)
- **REMOVE** — Claude can figure this out by reading `package.json`, source files, or the filesystem
- **MOVE** — belongs in `docs/`, an ADR, `.claude/rules/` with path scoping, or a subdirectory CLAUDE.md

Apply these rules:

| Content type | Classification |
|---|---|
| Verification commands to run after changes | KEEP |
| Coding rules differing from framework defaults | KEEP |
| Non-obvious gotchas / footguns | KEEP |
| Commit format + hook behavior | KEEP |
| Files/dirs to never modify | KEEP |
| Project description / tech stack overview | REMOVE (reads package.json) |
| Directory structure / file tree | REMOVE (explores filesystem) |
| Key file lists | REMOVE (searches codebase) |
| Architecture diagrams or explanations | MOVE (ADR or docs/) |
| Environment variable templates | REMOVE (reads .env.example) |
| Database schema documentation | REMOVE (reads schema files) |
| Deployment / CI pipeline info | REMOVE (irrelevant during coding) |
| Auth/discord/feature-specific flows | MOVE (docs/ or subdirectory CLAUDE.md) |

### 3. Present Recommendations

Show a summary table:

| Section | Lines | Classification | Reason |
|---|---|---|---|
| ... | ... | KEEP / REMOVE / MOVE | ... |

Show: current line count → projected line count after cuts.

### 4. Ask for Approval

Do NOT apply changes yet. Ask the user which recommendations to apply.

### 5. Apply Approved Changes

After approval, edit the CLAUDE.md file(s) to apply the agreed cuts. Verify the result reads cleanly.

## Principles

- Under 50 lines is ideal. Over 200 is a warning sign.
- Architectural decisions belong in `docs/decisions/` (ADRs), not CLAUDE.md.
- Feature-specific content belongs in subdirectory CLAUDE.md files, only loaded when Claude works in that subtree.
- If a rule is being ignored, the file is probably too long — prune rather than emphasize.
