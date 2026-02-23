---
name: CLAUDE.md Principles
description: Apply when the user is working on CLAUDE.md, discussing context files, agent memory, or AI coding assistant instructions. Teaches the minimal-context approach backed by empirical research.
user-invocable: false
---

# CLAUDE.md Best Practices

## The Research Finding

Developer-written context files improve task success by only ~4% while increasing compute cost and time by **20%+**. LLMs are proficient at exploring codebases independently by reading `package.json`, source files, and schemas. Bloated CLAUDE.md files cause important rules to get buried and ignored.

## The Core Test

For every line in CLAUDE.md, ask: **"Would removing this cause Claude to make mistakes?"**

- **Yes** → keep it
- **No** → cut it

## What Belongs

- Commands Claude cannot infer from `package.json` / `Cargo.toml` — especially verification steps to run after changes
- Coding rules that differ from language/framework defaults
- Non-obvious gotchas that would cause real bugs (wrong URLs, wrong API names, wrong tool)
- Commit format and hook behavior if non-standard
- Files/directories that must NOT be modified

## What Does NOT Belong

| Content | Why to cut |
|---|---|
| Project description / tech stack | Claude reads `package.json` |
| Architecture explanations | Belongs in ADRs / `docs/` |
| Directory structure | Claude explores the filesystem |
| Key file lists | Claude searches the codebase |
| Environment variable templates | Claude reads `.env.example` |
| Database schema docs | Claude reads schema files |
| Deployment / CI pipeline info | Irrelevant during coding |
| Anything discoverable by reading code | Claude will find it |

## Principle: Fix Root Causes

When Claude makes a mistake, prefer fixing the codebase over adding a CLAUDE.md rule:

1. **Fix in codebase** — better types, clearer naming, more tests
2. **Add tooling / script** — automate repetitive steps
3. **Add to CLAUDE.md** — only as a last resort for mistakes that can't be fixed in code

CLAUDE.md is a temporary patch. A well-structured codebase with good types and tests needs almost none of it.

## Size Target

- Under 50 lines is ideal
- Under 100 lines is good
- Over 200 lines is a warning sign — important rules are getting lost
