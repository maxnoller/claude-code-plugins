# context-files

Claude Code plugin for optimizing AI context files (CLAUDE.md, AGENTS.md) and reviewing sessions for friction.

## Commands

### `/context-files:review`

Audits your CLAUDE.md, AGENTS.md, and `.claude/rules/` files using the minimal-context principle: **only keep what prevents consistent mistakes**. Classifies each line as KEEP, REMOVE, or MOVE, shows projected line reduction, and applies changes only after your approval.

### `/context-files:session-review`

Reviews your current session for friction, repeated corrections, wrong assumptions, and workflow gaps. Classifies findings as: fix in codebase, add tooling, add to context file, or one-off. Biased toward fixing root causes over patching instructions.

## Background

Research shows developer-written context files improve task success by only ~4% while increasing compute cost by 20%+. Agents explore codebases well independently. CLAUDE.md and AGENTS.md should contain only rules and gotchas that prevent real mistakes — not project documentation.

The skill in this plugin auto-activates when you're discussing CLAUDE.md, AGENTS.md, or context file design.
