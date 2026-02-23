---
name: Context File Principles
description: Apply when the user is working on CLAUDE.md, AGENTS.md, context files, agent memory, or AI coding assistant instructions. Teaches the minimal-context approach backed by empirical research.
user-invocable: false
---

# AI Context File Best Practices

Applies to: **CLAUDE.md** (Claude Code), **AGENTS.md** (Jules / other agents), and any equivalent agent instruction file.

## The Research Finding

Developer-written context files improve task success by only ~4% while increasing compute cost and time by **20%+**. LLMs are proficient at exploring codebases independently by reading `package.json`, source files, and schemas. Bloated context files cause important rules to get buried and ignored.

## The Core Test

For every line, ask: **"Would removing this cause the agent to make mistakes?"**

- **Yes** → keep it
- **No** → cut it

## What Belongs

- Commands the agent cannot infer from `package.json` / `Cargo.toml` — especially verification steps to run after changes
- Coding rules that differ from language/framework defaults
- Non-obvious gotchas that would cause real bugs (wrong URLs, wrong API names, wrong tool)
- Commit format and hook behavior if non-standard
- Files/directories that must NOT be modified

## What Does NOT Belong

| Content | Why to cut |
|---|---|
| Project description / tech stack | Agent reads `package.json` |
| Architecture explanations | Belongs in ADRs / `docs/` |
| Directory structure | Agent explores the filesystem |
| Key file lists | Agent searches the codebase |
| Environment variable templates | Agent reads `.env.example` |
| Database schema docs | Agent reads schema files |
| Deployment / CI pipeline info | Irrelevant during coding |
| Anything discoverable by reading code | Agent will find it |

## Principle: Fix Root Causes

When an agent makes a mistake, prefer fixing the codebase over adding a context file rule:

1. **Fix in codebase** — better types, clearer naming, more tests
2. **Add tooling / script** — automate repetitive steps
3. **Add to context file** — only as a last resort for mistakes that can't be fixed in code

Context files are a temporary patch. A well-structured codebase with good types and tests needs almost none of it.

## Size Targets

- Under 50 lines is ideal
- Under 100 lines is good
- Over 200 lines is a warning sign — important rules are getting lost
