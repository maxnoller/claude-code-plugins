---
name: jules
description: Guide for using Google Jules, the asynchronous AI coding agent. Use when delegating tasks to Jules, writing Jules prompts, using the `jules` CLI, or when the user mentions "jules", "send to jules", or wants to offload coding work to run in the background. Ideal for well-defined tasks that can run independently (bug fixes, tests, refactoring, docs) or parallelizing work.
---

Jules is Google's asynchronous coding agent that clones your repo into a secure VM, executes tasks, and returns diffs or PRs. It works in the background while you continue other work.

## CLI Quick Reference

```bash
# Launch TUI
jules

# Create session for current repo
jules new "write unit tests for auth module"

# Create session for specific repo
jules new --repo owner/repo "add input validation"

# Parallel sessions (1-5) for same task
jules new --parallel 3 "fix linting errors"

# List sessions and repos
jules remote list --session
jules remote list --repo

# Pull session results
jules remote pull --session 123456
jules remote pull --session 123456 --apply  # Apply patch locally

# Teleport: clone + checkout + apply patch
jules teleport 123456

# Auth
jules login
jules logout
```

## Writing Effective Prompts

**Be specific, not vague.** Treat it like delegating to a developer.

| Bad | Good |
|-----|------|
| "Add authentication" | "Add JWT auth to Express app with login/logout endpoints and middleware for protected routes" |
| "Fix the bug" | "Fix TypeError in components/LoginForm.js when submitting empty email field - add validation" |
| "Write tests" | "Write pytest tests for the parse_config function covering edge cases: empty input, malformed JSON, missing required fields" |

**Include context:**
- Specify files/modules to modify
- Mention frameworks and patterns to follow
- Reference existing code patterns when applicable

**For complex tasks:** Break into smaller, sequential sessions rather than one large request.

## Prompt Categories

**Debugging:** "Help me fix {specific error}", "Trace why this value is undefined", "Add logging to debug {issue}"

**Refactoring:** "Refactor {file} from {pattern X} to {pattern Y}", "Convert callbacks to async/await", "Extract {logic} into a utility function"

**Testing:** "Add integration tests for {endpoint}", "Write pytest fixtures mocking {external API}", "Generate property-based tests for {function}"

**Documentation:** "Add docstrings to {module}", "Write API docs for {endpoint}"

**Maintenance:** "Upgrade {dependency} and fix breaking changes", "Remove unused imports across the codebase"

## Workflow Patterns

**Batch processing from file:**
```bash
cat TODO.md | while IFS= read -r line; do
  jules new "$line"
done
```

**From GitHub issues:**
```bash
gh issue list --assignee @me --limit 1 --json title | jq -r '.[0].title' | jules new
```

**With Gemini for triage:**
```bash
gemini -p "find the most tedious issue:\n$(gh issue list --assignee @me)" | jules new
```

## AGENTS.md Integration

Jules reads `AGENTS.md` from the repo root for context. Use `/add-agents-md` to generate one.

Keep it updated with:
- Build/test commands (exact, copy-pasteable)
- Architecture overview (one paragraph)
- Coding conventions and lint rules
- Important constraints (what NOT to do)

## Session Workflow

1. **Create session** with specific prompt
2. **Jules generates plan** - review for understanding
3. **Approve or refine** the plan
4. **Jules executes** in isolated VM
5. **Review diff/PR** when complete
6. **Apply locally** with `jules remote pull --apply` or `jules teleport`
