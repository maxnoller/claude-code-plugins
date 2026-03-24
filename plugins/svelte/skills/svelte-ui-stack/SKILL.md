---
name: Svelte UI Stack
description: This skill should be used when the user asks to "build a page", "add a component", "create a form", "add a dialog", "set up shadcn-svelte", "add dark mode", "style with tailwind", "create a dashboard", "add a data table", or works with any UI in Svelte 5. Also trigger when the user mentions shadcn-svelte, bits-ui, Tailwind CSS, formsnap, superforms, tailwind-variants, mode-watcher, or component architecture. Even if the user doesn't explicitly mention UI libraries, use this skill whenever building visual interfaces in SvelteKit — it prevents common mistakes like using Svelte 4 syntax, wrong Tailwind v4 patterns, and poor component architecture.
---

# Svelte UI Stack

Build production UIs in Svelte 5 using shadcn-svelte, bits-ui, and Tailwind CSS v4.

## What Claude Doesn't Know (training data gaps)

These are the things that have changed since training cutoff. Everything else (component design, software architecture, state management principles) — Claude already knows.

### Svelte 5 Syntax (never use Svelte 4)

| Correct (Svelte 5) | Wrong (Svelte 4) |
|---|---|
| `let { x } = $props()` | `export let x` |
| `let { ...rest } = $props()` | `$$restProps` |
| `{@render children?.()}` | `<slot />` |
| `{@render header?.()}` | `<slot name="header" />` |
| `onclick={handler}` | `on:click={handler}` |
| Callback props | `createEventDispatcher` |
| `$bindable()` | Just `export let` for two-way |
| `ref = $bindable(null)` | `bind:this` from parent |

### Tailwind CSS v4 (no config file, no PostCSS)

```ts
// vite.config.ts — Vite plugin, not PostCSS
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
});
```

All configuration in CSS. Colors in OKLCH. `tw-animate-css` replaces `tailwindcss-animate`. See `references/tailwind-v4.md` for the full theme setup.

### Package Renames

| Current | Deprecated |
|---|---|
| `tailwind-variants` (`tv()`) | `class-variance-authority` (`cva`) |
| `@lucide/svelte` (deep imports: `@lucide/svelte/icons/check`) | `lucide-svelte` (barrel imports) |
| `tw-animate-css` | `tailwindcss-animate` |
| bits-ui `Command` | `cmdk-sv` |
| `@tanstack/table-core` + `createSvelteTable` | `svelte-headless-table` |
| `zod4` / `zod4Client` (superforms adapters) | `zod` / `zodClient` |

## shadcn-svelte

### Installation & CLI

```bash
pnpm dlx shadcn-svelte@latest init
pnpm dlx shadcn-svelte@latest add button dialog form input
pnpm dlx shadcn-svelte@latest add --all
```

### Component Anatomy

All shadcn-svelte components follow this structure:

```svelte
<script lang="ts" module>
  import { tv } from "tailwind-variants";
  export const myVariants = tv({ base: "...", variants: { ... } });
</script>

<script lang="ts">
  import { cn } from "$lib/utils.js";
  let {
    class: className, variant, ref = $bindable(null),
    children, ...restProps
  }: Props = $props();
</script>

<div bind:this={ref} data-slot="my-component"
  class={cn(myVariants({ variant }), className)} {...restProps}>
  {@render children?.()}
</div>
```

The `cn()` utility merges classes (`clsx` + `tailwind-merge`). `{...restProps}` spread enables attachments and bits-ui features to pass through.

### bits-ui (Headless Layer)

Compound component pattern with dot notation. The `child` snippet overrides rendered elements:

```svelte
<Dialog.Trigger>
  {#snippet child({ props })}
    <Button {...props} variant="outline">Custom trigger</Button>
  {/snippet}
</Dialog.Trigger>
```

For floating components (Popover, Tooltip, Select), the child snippet also receives `wrapperProps` — spread both.

See `references/shadcn-components.md` for Dialog, Sheet, Command, Select, Accordion, Toast, DataTable patterns.

## Architecture

Svelte's value proposition is simplicity. State, logic, and markup live together in `.svelte` files — that colocation is the feature. Don't add abstraction layers Svelte was designed to not need.

### Component Extraction

When a component grows large, **extract visual sub-components with narrow props**. This is the Svelte way — not extracting state into separate files.

```svelte
<!-- Before: 800-line +page.svelte -->
<!-- After: thin page + focused sub-components -->
<PageToolbar {services} onDeploy={handleDeploy} onRestart={handleRestart} />
<ServiceGrid {filteredServices} {statusMap} />
{#if services.length === 0}
  <EmptyState {slug} {env} />
{/if}
<ConfirmDialogs bind:deleteOpen bind:deployOpen {onConfirm} />
```

Each sub-component receives only what it needs — not a god object. The state stays in the page component that owns it.

### When to Use .svelte.ts Files

`.svelte.ts` files enable runes outside components. Use them for **reusable reactive logic shared across multiple components** — not for extracting page-local state.

Good uses: `createPagination()`, `createInfiniteScroll()`, `useAutoRefresh()`, `createFormState()`
Not ideal: extracting a single page's state into a factory just to make the component shorter.

When passing reactive values to `.svelte.ts` functions, use getter functions for primitives (`() => count`) since reactivity persists through property access. Object `$state` proxies can be passed directly.

### Context API

`createContext` (Svelte 5.40+) for SSR-safe, subtree-scoped state:

```ts
import { createContext } from 'svelte';
export const [getUser, setUser] = createContext<User>();
```

Never use module-level `$state` for user-specific data in SSR apps — it leaks between requests.

See `references/component-architecture.md` for the full decision guide on state patterns, file types, and project structure.

## Ecosystem

### Forms: Formsnap + Superforms

```svelte
<form method="POST" use:enhance>
  <Form.Field {form} name="email">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Email</Form.Label>
        <Input {...props} bind:value={$formData.email} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
</form>
```

### Dark Mode: mode-watcher

```svelte
<ModeWatcher />  <!-- in +layout.svelte -->
```

Toggle: `toggleMode()`, `setMode('light' | 'dark')`, `resetMode()`.

### Data Tables: TanStack Table

Use `createSvelteTable` with `renderComponent`/`renderSnippet`. See `references/forms-and-tables.md`.

## Additional Resources

- **`references/component-architecture.md`** — State patterns, .svelte.ts usage, project structure, context API
- **`references/tailwind-v4.md`** — Full CSS theme setup, OKLCH colors, dark mode, custom variants
- **`references/shadcn-components.md`** — Component catalog with code: Dialog, Sheet, Command, Select, Accordion, Toast, DataTable, DropdownMenu
- **`references/forms-and-tables.md`** — Formsnap + Superforms + TanStack Table complete setup
