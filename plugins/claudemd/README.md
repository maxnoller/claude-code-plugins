# claudemd

Claude Code plugin for optimizing CLAUDE.md files and reviewing sessions for friction.

## Commands

### `/claudemd:review-claude-md`

Audits your CLAUDE.md file(s) using the minimal-context principle: **only keep what prevents consistent mistakes**. Classifies each line as KEEP, REMOVE, or MOVE, shows projected line reduction, and applies changes only after your approval.

### `/claudemd:session-review`

Reviews your current session for friction, repeated corrections, wrong assumptions, and workflow friction. Classifies findings as: fix in codebase, add tooling, add to CLAUDE.md, or one-off. Biased toward fixing root causes over patching instructions.

## Background

Research shows developer-written context files improve task success by only ~4% while increasing compute cost by 20%+. Claude is good at exploring codebases independently. CLAUDE.md should contain only rules and gotchas that prevent real mistakes — not project documentation.

The skill in this plugin auto-activates when you're discussing CLAUDE.md or context file design.
