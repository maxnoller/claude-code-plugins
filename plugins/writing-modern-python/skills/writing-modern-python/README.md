# writing-modern-python skill

## Skill pattern: Living Styleguide

This skill follows the **Living Styleguide** pattern — an opinionated, evolving collection of preferences that grows from real sources (articles, experience, discoveries) into a compiled reference an AI agent applies automatically.

### What makes a Living Styleguide

- **Opinionated, not comprehensive.** It captures *your* choices, not general best practices. "Use yappi" is a styleguide entry. "Here are 12 profilers and their tradeoffs" is a reference guide.
- **Source-driven.** Each pattern originates from something concrete — a blog post, a painful debugging session, a library you discovered. The source gives the pattern credibility and context.
- **Accumulative.** Starts minimal (1-2 patterns) and grows over time. New entries are cheap to add — one reference file, one SKILL.md section.
- **Compiled.** The SKILL.md body is a compiled overview — one example per pattern, enough for the agent to apply the preference without reading deeper. The reference files are the full source material.
- **Self-maintaining.** Patterns are independent. Adding one never requires changing another. Removing a stale pattern is deleting one file and one SKILL.md section.

### Progressive disclosure

1. **Frontmatter description** (~100 words, always in context) — triggers broadly so the styleguide is consulted on any relevant task
2. **SKILL.md body** (loaded on trigger) — compiled overview with one concrete example per pattern. Enough for most tasks. Cap at 500 lines.
3. **references/** (on demand) — one file per pattern with full rationale, examples, and when/when-not. Agent reads only what it needs.

### How to add a pattern

1. **Write the reference file** — create `references/topic-name.md` following the template below
2. **Add a section to SKILL.md** — a heading, 2-3 sentence summary, one key code example, and a `See references/...` pointer

### Reference file template

```markdown
# Pattern Name

## Why
What problem this solves and why this tool/approach wins over alternatives.
Keep it to 2-3 sentences — explain the reasoning, not the history.

## The pattern
Core usage with code examples. Lead with the most common case.

## When to use
Concrete scenarios where this applies.

## When NOT to use
When something else is a better fit, and what that something else is.
```

### Design principles

- **One example beats ten rules.** Each pattern in SKILL.md leads with a concrete code example, not abstract guidance.
- **Explain why, not just what.** So the agent can handle edge cases the pattern doesn't cover explicitly.
- **Don't duplicate upstream docs.** Reference files capture your preferences and the key APIs you actually use, not full library documentation.
- **Patterns are independent.** Each reference file stands alone. No cross-references unless patterns genuinely interact.
- **Keep it current.** A stale pattern is worse than no pattern. Remove rather than leave outdated.
