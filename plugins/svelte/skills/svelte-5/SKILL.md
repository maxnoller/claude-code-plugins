---
name: Svelte 5
description: Comprehensive Svelte 5 and SvelteKit development patterns — runes ($state, $derived, $effect, $props, $bindable), component architecture (snippets, compound components, headless UI), SvelteKit server (load functions, form actions, hooks, API routes), remote functions (query, command, form, batch), testing with vitest-browser-svelte, performance optimization, and accessibility. Use this skill whenever writing, reviewing, or modifying Svelte or SvelteKit code, working with .svelte/.svelte.ts files, asking about Svelte 5 reactivity or migration from Svelte 4, building components, setting up tests, optimizing performance, implementing accessibility, or using any SvelteKit server-side pattern. Even if the user doesn't say "Svelte" explicitly, use this skill if the context involves .svelte files, runes, SvelteKit routes, or any of the patterns above.
---

# Svelte 5

Svelte 5 uses runes — compiler-driven reactivity primitives that replace Svelte 4's implicit reactivity. This skill covers the full Svelte 5 + SvelteKit stack.

## Runes

### $state — Reactive State

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
</script>
<button onclick={() => count++}>{count}</button>
```

- Primitives are reactive by value; objects/arrays become deep reactive proxies
- Class instances are NOT made reactive — define `$state` fields inside the class:

```ts
// WRONG: let instance = $state(new MyClass());
// CORRECT:
class MyClass {
  value = $state(0);
}
```

### $derived — Computed Values

```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
  let expensive = $derived.by(() => heavyCalculation(count));
</script>
```

Must be pure — no side effects, no mutating `$state`. Use `$derived.by()` for multi-statement computations.

### $effect — Side Effects

```ts
$effect(() => {
  console.log('Count changed:', count);
  return () => console.log('Cleanup'); // Always return cleanup for resources
});
```

Use for DOM manipulation, subscriptions, logging, browser APIs. Never read and write the same state (infinite loop). Prefer `$derived` over `$effect` when computing values.

`$effect.pre()` runs before DOM updates (replaces `beforeUpdate`).

### $props — Component Props

```svelte
<script lang="ts">
  interface Props {
    name: string;
    age?: number;
    onclick?: () => void;
  }
  let { name, age = 18, onclick }: Props = $props();
</script>
```

Rest props: `let { class: className, ...rest } = $props();`

### $bindable — Two-Way Binding

```svelte
<!-- Child.svelte -->
<script>
  let { value = $bindable() } = $props();
</script>
<input bind:value />

<!-- Parent: <Child bind:value={text} /> -->
```

### $inspect — Dev Debugging

```ts
$inspect(count); // Logs on change, stripped in production
$inspect(count).with((type, value) => { if (type === 'update') debugger; });
```

### Runes in .svelte.ts Files

Use runes outside components in `.svelte.ts` files. Only rename to `.svelte.ts` when the file directly declares runes — files that merely import rune-using functions stay as `.ts`.

```ts
// counter.svelte.ts
export function createCounter(initial = 0) {
  let count = $state(initial);
  return {
    get count() { return count },
    increment: () => count++,
  };
}
```

### Critical Rune Rules

1. Runes are top-level only — not inside functions or conditionals (except `.svelte.ts` files)
2. `$effect` doesn't run during SSR — use load functions for server data
3. Global `$state` is shared across SSR requests — avoid global mutable state on server
4. `$derived` tracks dependencies at runtime, not compile time
5. Always return cleanup from `$effect` for intervals, listeners, subscriptions

> **Deep dive:** Read `references/gotchas.md` for common mistakes. Read `references/migration.md` for Svelte 4 to 5 migration patterns.

---

## Components

### Snippets (Replacing Slots)

```svelte
<!-- Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  interface Props {
    header?: Snippet;
    children: Snippet;
  }
  let { header, children }: Props = $props();
</script>

<div class="card">
  {#if header}<div class="card-header">{@render header()}</div>{/if}
  <div class="card-body">{@render children()}</div>
</div>
```

**With parameters** (like slot props):

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  interface Props<T> {
    items: T[];
    row: Snippet<[item: T, index: number]>;
  }
  let { items, row }: Props<any> = $props();
</script>

{#each items as item, index (item.id)}
  {@render row(item, index)}
{/each}
```

Always use optional chaining for optional snippets: `{@render icon?.()}`

### Compound Components

Related components share state via context:

```svelte
<!-- Accordion.svelte -->
<script lang="ts" module>
  import { getContext, setContext } from 'svelte';
  const KEY = Symbol('accordion');
  export function getAccordionCtx() { return getContext(KEY); }
</script>

<script lang="ts">
  let { multiple = false, children }: Props = $props();
  let activeItems = $state(new Set<string>());
  // toggle, isOpen functions...
  setContext(KEY, { get activeItems() { return activeItems }, toggle, isOpen });
</script>
{@render children()}
```

### Headless Components

Provide behavior without UI by passing state/actions through snippet parameters:

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { tabs, children }: { tabs: Tab[]; children: Snippet<[{activeTab, setActiveTab, isActive}]> } = $props();
  let activeTab = $state(tabs[0]?.id);
</script>
{@render children({ activeTab, setActiveTab: (id) => activeTab = id, isActive: (id) => activeTab === id })}
```

### Polymorphic Components

```svelte
<svelte:element this={as} class="btn btn-{variant}" {...rest}>
  {@render children()}
</svelte:element>
```

> **Deep dive:** Read `references/components.md` for full compound component, controlled/uncontrolled, and forwarding patterns with examples.

---

## SvelteKit Server

### Load Functions

```ts
// +page.server.ts — server-only, safe for secrets/DB
export const load: PageServerLoad = async ({ params, locals }) => {
  if (!locals.user) error(401, 'Unauthorized');
  return { stats: await db.stats.find({ userId: locals.user.id }) };
};
```

Use `+page.server.ts` for DB/secrets, `+layout.server.ts` for shared data, `+page.ts` for client-cacheable/public API calls. Always parallelize independent fetches with `Promise.all`.

### Form Actions

```ts
export const actions: Actions = {
  login: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    if (!email) return fail(400, { email, missing: true });
    const user = await authenticate(email, data.get('password') as string);
    if (!user) return fail(400, { email, incorrect: true });
    cookies.set('session', user.sessionId, { path: '/' });
    redirect(303, '/dashboard');
  }
};
```

Progressive enhancement: `<form method="POST" action="?/login" use:enhance>`

### Hooks (hooks.server.ts)

```ts
export const handle: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');
  if (session) event.locals.user = await getUserFromSession(session);
  return resolve(event);
};
```

Use `sequence()` to compose multiple handles. Use `handleFetch` to add auth headers to internal API calls. Use `handleError` for error tracking (only catches unexpected errors).

### API Routes (+server.ts)

```ts
export const GET: RequestHandler = async ({ url, locals }) => {
  return json(await db.posts.findMany({ take: Number(url.searchParams.get('limit')) || 10 }));
};
```

> **Deep dive:** Read `references/server-patterns.md` for complete hooks, streaming, locals typing, and antipattern examples.

---

## Remote Functions (Experimental)

Enable with `kit.experimental.remoteFunctions: true` and `compilerOptions.experimental.async: true`.

```ts
// src/lib/todos.remote.ts
import { query, command } from '$app/server';

export const getTodos = query(async () => await db.todos.findMany());
export const createTodo = command(async (text: string) => {
  return await db.todos.create({ data: { text, done: false } });
});
```

- `query()` — read-only server data fetching
- `command()` — server mutations
- `form()` — progressive enhancement forms (works with/without JS)
- `query.batch()` — batch multiple queries into one HTTP request

Place `.remote.ts` files anywhere in `src/` except `src/lib/server/`. Use remote functions for interaction-triggered data; use load functions for SSR/SEO-critical data.

> **Deep dive:** Read `references/remote-functions.md` for form handling with Zod, batch patterns, and comparison with load functions.

---

## Testing

Use `vitest-browser-svelte` for real browser testing (not jsdom):

```bash
pnpm install -D @vitest/browser-playwright vitest-browser-svelte playwright
```

### Component Tests

```ts
import { render } from 'vitest-browser-svelte';
import { page } from 'vitest/browser';

it('handles click', async () => {
  let clicked = false;
  render(Button, { props: { label: 'Click', onclick: () => clicked = true } });
  await page.getByRole('button').click();
  expect(clicked).toBe(true);
});
```

Prefer semantic queries: `getByRole` > `getByLabel` > `getByText` > `getByTestId`.

### Testing Runes in .svelte.ts

```ts
import { flushSync, untrack } from 'svelte';

it('increments', () => {
  const counter = createCounter(0);
  expect(untrack(() => counter.count)).toBe(0);
  counter.increment();
  flushSync();
  expect(untrack(() => counter.count)).toBe(1);
});
```

### File Naming

- Browser tests: `*.svelte.test.ts` (include pattern: `src/**/*.svelte.{test,spec}.ts`)
- Server/node tests: `*.test.ts` (include pattern: `src/**/*.{test,spec}.ts`)

> **Deep dive:** Read `references/testing.md` for full setup config, form testing, async testing, snippet testing, and mocking patterns.

---

## Performance

Svelte 5's fine-grained reactivity is fast by default. Key optimizations:

- **Keyed each blocks:** `{#each items as item (item.id)}` — enables efficient DOM reuse
- **Memoize with $derived:** Use `$derived` for filtered/computed lists instead of recalculating in templates
- **Split reactive dependencies:** Narrow dependency scope to avoid over-reactivity
- **Always clean up effects:** Return cleanup for intervals, listeners, subscriptions
- **Virtualize long lists:** Use `svelte-virtual-list` for 100+ items
- **Debounce user input:** Use `$effect` with `setTimeout` + cleanup for search inputs
- **Lazy load components:** Dynamic `import()` for heavy components
- **Stream non-critical data:** Return promises (no `await`) from load functions for streaming
- **Use `preloadData`:** `import { preloadData } from '$app/navigation'` on hover for fast navigation

> **Deep dive:** Read `references/performance.md` for bundle analysis, image optimization, profiling, and the full performance checklist.

---

## Accessibility

Svelte has built-in a11y compiler warnings. Key practices:

- **Semantic HTML:** Use `<button>` not `<div onclick>`, `<a>` not `<span onclick>`
- **Labels:** Every input needs a `<label>` (explicit `for=` preferred)
- **Error messages:** Use `aria-describedby`, `aria-invalid`, and `role="alert"` for form errors
- **Focus management:** Trap focus in modals, restore focus on close, use skip links
- **Keyboard navigation:** Support Arrow keys, Home/End, Escape for custom widgets
- **Live regions:** `aria-live="polite"` for dynamic content announcements
- **Reduced motion:** Respect `prefers-reduced-motion` with CSS media query
- **Contrast:** 4.5:1 for normal text, 3:1 for large text and UI components

> **Deep dive:** Read `references/a11y.md` for complete ARIA patterns (tabs, accordion, dialogs), focus trap implementation, and testing with axe-core.

---

## Svelte 4 Migration Quick Reference

| Svelte 4 | Svelte 5 |
|----------|----------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { sideEffect() }` | `$effect(() => { sideEffect() })` |
| `export let name` | `let { name } = $props()` |
| `on:click={handler}` | `onclick={handler}` |
| `<slot />` | `{@render children()}` |
| `<slot name="x" />` | `{@render x?.()}` |
| `createEventDispatcher()` | Callback props |
| `export let value` + `bind:value` | `let { value = $bindable() } = $props()` |

> **Full migration guide:** Read `references/migration.md`
