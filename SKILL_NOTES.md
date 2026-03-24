# Skill Writing Principles

## 1. Only teach what Claude doesn't know

Claude already knows software engineering, architecture patterns, and best practices. Skills should provide facts Claude can't derive: API changes after training cutoff, package renames, new syntax, specific config formats. Before adding anything, ask: "Does Claude really need this, or does it already know it?"

## 2. Match freedom to fragility

- **High freedom** for context-dependent decisions (architecture, code organization, naming) — give principles and reasoning, let Claude decide
- **Low freedom** for fragile operations (CLI commands, config file formats, exact syntax) — give the specific answer

Most architecture decisions are high-freedom. Don't impose rigid rules on inherently contextual problems.

## 3. No rigid thresholds or mandatory patterns

Rules like "extract at 200 lines" or "always use factory functions" produce mechanical behavior. Claude follows the rule regardless of whether it makes sense. Instead, explain the reasoning: "Svelte's value is colocation — state and markup together." Claude can then judge each situation.

## 4. Explain why, not what

"Use factory functions for reactive logic shared across multiple components — think `usePagination()` or `useAutoRefresh()`" is better than "Always extract state into factory functions." The why lets Claude make contextual decisions.

## 5. Examples shape output

The example in a skill is the strongest signal for what Claude will produce. If the example shows an over-extracted factory pattern, Claude will over-extract. Make sure examples demonstrate the genuinely right use case, not an edge case elevated to a default.

## 6. Smaller is better

More instructions ≠ better output. More instructions = more rigid behavior. The final version of our UI skill was ~150 lines and produced better results than the ~270 line version. Challenge every paragraph for its token cost.

## 7. Test against real code, then honestly review the output

The iteration loop: write skill → run against real codebase → have an agent honestly review "is this actually good code?" → fix the skill. The honest review is the critical step — without it you'll keep refining the wrong approach.

## 8. Don't confuse "followed the skill" with "good output"

An agent can perfectly follow every rule in a skill and still produce bad code. Check the actual output quality, not just compliance with the skill's patterns.
