---
name: Svelte UI Stack
description: This skill should be used when the user asks to "build a page", "add a component", "create a form", "add a dialog", "set up shadcn-svelte", "add dark mode", "style with tailwind", "create a dashboard", "add a data table", or works with any UI in Svelte 5. Also trigger when the user mentions shadcn-svelte, bits-ui, Tailwind CSS, formsnap, superforms, tailwind-variants, mode-watcher, or component architecture. Even if the user doesn't explicitly mention UI libraries, use this skill whenever building visual interfaces in SvelteKit — it prevents common mistakes like using Svelte 4 syntax, wrong Tailwind v4 patterns, and poor component architecture.
---

# Svelte UI Stack

Build production UIs in Svelte 5 using shadcn-svelte, bits-ui, and Tailwind CSS v4. This skill covers component selection, architecture, and the ecosystem glue that ties everything together.

## Core Principles

### 1. Always Use shadcn-svelte First

Before building any UI element, check if shadcn-svelte has it. The library covers: Accordion, Alert, Avatar, Badge, Button, Calendar, Card, Checkbox, Collapsible, Command, Dialog, Drawer, Dropdown Menu, Form, Input, Label, Pagination, Popover, Progress, Radio Group, ScrollArea, Select, Separator, Sheet, Skeleton, Slider, Sonner (toasts), Spinner, Switch, Table, Tabs, Textarea, Toggle, Tooltip.

```bash
# Install what you need
pnpm dlx shadcn-svelte@latest add button dialog form input
```

When shadcn-svelte has the component: use it, customize variants if needed.
When it doesn't: build with bits-ui primitives + Tailwind, following the same patterns.

### 2. Separate Logic from UI

Components should be thin UI shells. Extract reactive logic into colocated `.svelte.ts` files.

**The 200-line guideline:** When a component approaches ~200 lines, extract business logic into a colocated `.svelte.ts` module. The same runes (`$state`, `$derived`, `$effect`) work identically in both `.svelte` and `.svelte.ts` files — no refactoring needed.

```
routes/dashboard/
├── +page.svelte              # Thin: imports state, renders UI
├── +page.server.ts           # Load function
├── dashboard-state.svelte.ts # Fat: all reactive logic
├── DashboardChart.svelte     # Route-specific component
└── DashboardFilters.svelte
```

The factory function pattern is the standard way to externalize logic:

```ts
// dashboard-state.svelte.ts
export function createDashboardState(initialData: DashboardData) {
  let data = $state(initialData);
  let sortField = $state<'date' | 'amount'>('date');
  let sorted = $derived(
    data.items.toSorted((a, b) => a[sortField] > b[sortField] ? 1 : -1)
  );

  return {
    get sorted() { return sorted; },
    get sortField() { return sortField; },
    set sortField(v) { sortField = v; },
    async refresh() { /* ... */ },
  };
}
```

```svelte
<!-- +page.svelte — thin shell -->
<script lang="ts">
  import { createDashboardState } from './dashboard-state.svelte';
  let { data } = $props();
  const dashboard = createDashboardState(data);
</script>
```

**Never destructure reactive return values** — `const { count } = createCounter()` breaks reactivity. Always access through the object: `counter.count`.

For the full architecture guide (reactive classes, context API, feature folders, decision matrix), see `references/component-architecture.md`.

### 3. Svelte 5 Patterns Only

Every component must use these patterns — never the Svelte 4 equivalents:

| Pattern | Correct (Svelte 5) | Wrong (Svelte 4) |
|---|---|---|
| Props | `let { x } = $props()` | `export let x` |
| Rest props | `let { ...rest } = $props()` | `$$restProps` |
| Children | `{@render children?.()}` | `<slot />` |
| Named slots | `{@render header?.()}` | `<slot name="header" />` |
| Events | `onclick={handler}` | `on:click={handler}` |
| Dispatch | Callback props | `createEventDispatcher` |
| Bindable | `$bindable()` | Just `export let` |
| Ref | `ref = $bindable(null)` | `bind:this` from parent |

### 4. Tailwind v4 — CSS-First Config

No `tailwind.config.ts`. No PostCSS. Configuration lives in CSS:

```ts
// vite.config.ts — use the Vite plugin
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
});
```

```css
/* app.css — all config here */
@import "tailwindcss";
@import "tw-animate-css";
@custom-variant dark (&:is(.dark *));

:root {
  --primary: oklch(0.205 0 0);        /* OKLCH, not HSL */
  --primary-foreground: oklch(0.985 0 0);
  /* ... */
}

@theme inline {
  --color-primary: var(--primary);     /* Maps CSS vars to Tailwind classes */
  --color-primary-foreground: var(--primary-foreground);
}
```

For the full Tailwind v4 setup, theming, and animation patterns, see `references/tailwind-v4.md`.

## Component Anatomy

shadcn-svelte components follow a consistent structure. Replicate this when extending or creating new components:

```svelte
<script lang="ts" module>
  import { tv, type VariantProps } from "tailwind-variants";
  // Module-level: variants + exported types
  export const myVariants = tv({
    base: "...",
    variants: { size: { sm: "...", md: "..." } },
    defaultVariants: { size: "md" },
  });
</script>

<script lang="ts">
  import { cn } from "$lib/utils.js";
  // Instance-level: props via $props()
  let {
    class: className,
    size = "md",
    ref = $bindable(null),
    children,
    ...restProps
  }: Props = $props();
</script>

<div
  bind:this={ref}
  data-slot="my-component"
  class={cn(myVariants({ size }), className)}
  {...restProps}
>
  {@render children?.()}
</div>
```

**Key conventions:**
- `tailwind-variants` (`tv()`) for variants — not `cva`
- `cn()` for class merging (`clsx` + `tailwind-merge`)
- `data-slot="..."` attribute for styling hooks
- `$bindable(null)` for ref forwarding
- `{...restProps}` spread for extensibility (enables attachments to pass through)

## bits-ui (Headless Layer)

shadcn-svelte wraps bits-ui. When customizing deeply, understand the primitive:

```svelte
<!-- Compound component pattern -->
<Dialog.Root bind:open>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>Title</Dialog.Title>
    </Dialog.Header>
  </Dialog.Content>
</Dialog.Root>
```

**Child snippet for render delegation** — override the rendered element:

```svelte
<Dialog.Trigger>
  {#snippet child({ props })}
    <Button {...props} variant="outline">Custom trigger</Button>
  {/snippet}
</Dialog.Trigger>
```

For floating components (Popover, Tooltip, Select), the child snippet receives `wrapperProps` too — always spread both.

## Ecosystem Integrations

### Forms: Formsnap + Superforms

For validated forms, use the shadcn-svelte Form component with superforms:

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

Use `zod4` / `zod4Client` adapters (current versions). See `references/forms-and-tables.md` for full setup.

### Data Tables: TanStack Table

Use `createSvelteTable` from shadcn-svelte's data-table utilities with `renderComponent` and `renderSnippet` helpers. See `references/forms-and-tables.md`.

### Dark Mode: mode-watcher

```svelte
<!-- +layout.svelte -->
<script>
  import { ModeWatcher } from "mode-watcher";
</script>
<ModeWatcher />
{@render children?.()}
```

Toggle with `toggleMode()`, `setMode('light' | 'dark')`, `resetMode()` from `mode-watcher`.

### Icons: @lucide/svelte

Deep imports only: `import Check from "@lucide/svelte/icons/check"` — never barrel imports.

## Key Dependencies

| Package | Purpose |
|---|---|
| `bits-ui` | Headless accessible primitives |
| `tailwind-variants` | Variant API (replaces cva) |
| `tailwind-merge` + `clsx` | Class merging via `cn()` |
| `tw-animate-css` | Animation utilities (replaces tailwindcss-animate) |
| `mode-watcher` | Dark mode |
| `@lucide/svelte` | Icons |
| `formsnap` + `sveltekit-superforms` | Form validation |
| `svelte-sonner` | Toasts |
| `runed` | Utility runes |

## Critical Rules

1. **Never use Svelte 4 syntax** — no `<slot>`, `export let`, `on:click`, `$$restProps`, `createEventDispatcher`
2. **No `tailwind.config.ts`** — all Tailwind config in CSS `@theme inline`
3. **Colors in OKLCH** — never hex or HSL in theme variables
4. **`tw-animate-css`** — never `tailwindcss-animate`
5. **`tailwind-variants` (`tv()`)** — never `cva` (class-variance-authority)
6. **`@lucide/svelte` deep imports** — never `lucide-svelte`
7. **Always spread `{...restProps}`** on the outermost element — required for bits-ui and attachments
8. **Extract logic at ~200 lines** — use colocated `.svelte.ts` factory functions
9. **Never destructure reactive objects** — access through the returned object
10. **Use `createContext` for SSR-safe shared state** — never module-level `$state` for user-specific data

## Additional Resources

### Reference Files
- **`references/component-architecture.md`** — Full architecture guide: .svelte.ts patterns, factory functions, reactive classes, context API, feature folders, decision matrix
- **`references/tailwind-v4.md`** — Complete Tailwind v4 setup: Vite plugin, CSS config, OKLCH theming, dark mode, custom variants, animation
- **`references/shadcn-components.md`** — Component catalog: Dialog, Sheet, Command, Select, Accordion, Toast patterns with code
- **`references/forms-and-tables.md`** — Formsnap + Superforms setup, TanStack Table integration, complete working examples
