# Svelte Plugin for Claude Code

Modern Svelte 5 and SvelteKit development assistant with deep knowledge of runes, remote functions, testing patterns, and performance optimization.

## Features

### Skills (Auto-activate based on context)
- **svelte-5** - Unified Svelte 5 + SvelteKit skill covering runes, component patterns, server-side (load functions, form actions, hooks, API routes), remote functions, testing with vitest-browser-svelte, performance optimization, and accessibility

### Commands
- `/svelte:new [name]` - Scaffold a new SvelteKit + Svelte 5 + shadcn-svelte project

### Agents
- **svelte-reviewer** - Proactively reviews `.svelte` files after edits for antipatterns

## Recommended: Official Svelte MCP

This plugin works best alongside the official Svelte MCP server:

```bash
claude mcp add svelte https://mcp.svelte.dev/mcp
```

The MCP provides:
- Documentation retrieval
- Static analysis via `svelte-autofixer`
- Playground link generation

## Installation

```bash
claude --plugin-dir /path/to/svelte
```

Or copy to your project's `.claude-plugin/` directory.
