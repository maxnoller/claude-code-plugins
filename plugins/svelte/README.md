# Svelte Plugin for Claude Code

Modern Svelte 5 and SvelteKit development assistant with deep knowledge of runes, attachments, async patterns, remote functions, testing, performance optimization, and accessibility.

## Features

### Skills (Auto-activate based on context)
- **svelte-5** — Unified Svelte 5 + SvelteKit skill covering runes, attachments, async Svelte, component patterns, server-side (load functions, form actions, hooks, API routes), remote functions, testing with vitest-browser-svelte, performance optimization, and accessibility
- **svelte-ui-stack** — Build production UIs with shadcn-svelte, bits-ui, and Tailwind CSS v4

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
