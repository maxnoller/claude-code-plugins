# ai-agent-evals skill

## Skill pattern: Curated Codex

This skill follows the **Curated Codex** pattern — an opinionated, evolving collection of preferences that grows from real sources (articles, experience, failures) into a compiled reference an AI agent applies automatically.

### Progressive disclosure

1. **Frontmatter description** (~100 words, always in context) — triggers on any eval-related task
2. **SKILL.md body** (loaded on trigger) — unified overview with one concrete example per pattern and pointers to reference files. Cap at 500 lines.
3. **references/** (on demand) — one file per pattern with full rationale, all examples, and when/when-not guidance

### How to add a pattern

1. **Write the reference file** — create `references/topic-name.md` with why, the core pattern, when to use, when not to use
2. **Add a section to SKILL.md** — a heading, 2-3 sentence summary, one key code example, and a `See references/...` pointer

### Design principles

- **One example beats ten rules.** Lead with concrete code, not abstract guidance.
- **Explain why, not just what.** So the agent handles edge cases the pattern doesn't cover.
- **Don't duplicate upstream docs.** Capture preferences and key APIs, not full library documentation.
- **Patterns are independent.** Each reference file stands alone.
- **Keep it current.** A stale pattern is worse than no pattern.
