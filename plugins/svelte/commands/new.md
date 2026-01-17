---
name: new
description: Scaffold a new SvelteKit + Svelte 5 + shadcn-svelte project with optional testing and remote functions setup
argument-hint: "[project-name]"
allowed-tools:
  - Bash
  - Write
  - Edit
  - Read
  - AskUserQuestion
---

# Create New Svelte 5 Project

Create a new SvelteKit project with Svelte 5, shadcn-svelte, and optional modern tooling.

## Arguments

The user provided: `$ARGUMENTS`

## Workflow

### 1. Gather Project Information

Parse `$ARGUMENTS` as the project name. If empty or not provided, ask for one.

Then ask the user which features to include:

**Required (always included):**
- SvelteKit with Svelte 5
- TypeScript
- TailwindCSS
- shadcn-svelte component library

**Optional features to offer:**
- **Sveltest** - Modern testing with vitest-browser-svelte
- **Remote Functions** - Enable experimental remote functions ($app/server)
- **Svelte MCP** - Recommend official Svelte MCP server setup

### 2. Create the Project

Run the SvelteKit CLI to create the project:

```bash
pnpm dlx sv create PROJECT_NAME --template minimal --types ts --add tailwindcss
```

Or for npm:
```bash
npx sv create PROJECT_NAME --template minimal --types ts --add tailwindcss
```

### 3. Initialize shadcn-svelte

```bash
cd PROJECT_NAME
pnpm dlx shadcn-svelte@latest init
```

When prompted:
- Base color: Let user choose or default to Slate
- CSS file: `src/app.css`
- Import aliases: Use defaults ($lib, $lib/components, etc.)

### 4. Add Requested Features

#### If Sveltest selected:

Install testing dependencies:
```bash
pnpm add -D @vitest/browser-playwright vitest-browser-svelte playwright
```

Update `vite.config.ts` to include test configuration:

```ts
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { playwright } from '@vitest/browser-playwright';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  test: {
    projects: [
      {
        name: 'client',
        test: {
          testTimeout: 2000,
          browser: {
            enabled: true,
            provider: playwright(),
            instances: [{ browser: 'chromium' }],
          },
          include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
        },
      },
      {
        name: 'server',
        test: {
          environment: 'node',
          include: ['src/**/*.{test,spec}.{js,ts}'],
        },
      },
    ],
  },
});
```

Create `src/vitest-setup-client.ts`:
```ts
/// <reference types="vitest/browser" />
/// <reference types="@vitest/browser-playwright" />
```

Add test scripts to `package.json`:
```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest run"
  }
}
```

#### If Remote Functions selected:

Update `svelte.config.js` to enable remote functions:

```js
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    experimental: {
      remoteFunctions: true
    }
  },
  compilerOptions: {
    experimental: {
      async: true
    }
  }
};

export default config;
```

Create an example remote function at `src/lib/example.remote.ts`:

```ts
import { query, command } from '$app/server';

export const getServerTime = query(async () => {
  return new Date().toISOString();
});

export const echo = command(async (message: string) => {
  return { received: message, timestamp: new Date().toISOString() };
});
```

#### If Svelte MCP selected:

Show the user how to add the official Svelte MCP:

```
To add the official Svelte MCP server for enhanced AI assistance:

claude mcp add svelte https://mcp.svelte.dev/mcp

This provides:
- Svelte/SvelteKit documentation retrieval
- Static code analysis via svelte-autofixer
- Playground link generation
```

### 5. Add Some Default shadcn Components

Add commonly used components:
```bash
pnpm dlx shadcn-svelte@latest add button card input label
```

### 6. Final Summary

After creation, provide a summary:

```
✅ Project created: PROJECT_NAME

Included:
- SvelteKit with Svelte 5
- TypeScript
- TailwindCSS
- shadcn-svelte (button, card, input, label)
[If selected:]
- Sveltest with vitest-browser-svelte
- Remote Functions enabled
- Svelte MCP recommendation

Next steps:
1. cd PROJECT_NAME
2. pnpm install (if not already done)
3. pnpm dev

[If MCP selected:]
4. claude mcp add svelte https://mcp.svelte.dev/mcp
```

## Important Notes

- Always use the user's preferred package manager (pnpm, npm, yarn, bun)
- If `sv` command fails, suggest installing it: `npm install -g sv`
- Handle errors gracefully and report issues clearly
- The project should be immediately runnable after creation
