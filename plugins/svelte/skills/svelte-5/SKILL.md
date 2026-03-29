---
name: svelte-5
description: Comprehensive Svelte 5 and SvelteKit development patterns — runes ($state, $state.raw, $state.snapshot, $derived, $effect, $props, $bindable, $inspect, $host), attachments ({@attach}), async Svelte (await expressions, svelte:boundary, $effect.pending, getAbortSignal), component architecture (snippets, compound components with createContext, headless UI), svelte/reactivity (MediaQuery, SvelteMap, SvelteSet, SvelteURL), SvelteKit server (load functions, form actions, hooks, API routes, $app/state), remote functions (query, command, form, batch, prerender), testing with vitest-browser-svelte, performance optimization, and accessibility. Use this skill whenever writing, reviewing, or modifying Svelte or SvelteKit code, working with .svelte/.svelte.ts files, asking about Svelte 5 reactivity or migration from Svelte 4, building components, setting up tests, optimizing performance, implementing accessibility, using attachments or actions, async rendering, or any SvelteKit server-side pattern. Even if the user doesn't say "Svelte" explicitly, use this skill if the context involves .svelte files, runes, SvelteKit routes, or any of the patterns above.
---

# Svelte 5

Svelte 5 uses runes — compiler-driven reactivity primitives that replace Svelte 4's implicit reactivity. This skill covers the full Svelte 5 + SvelteKit stack.

## Runes

### $state — Reactive State

Only use `$state` for variables that actually need reactivity (those read by `$derived`, `$effect`, or templates). Regular variables that don't drive UI updates don't need it.

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
  let API_URL = 'https://api.example.com'; // Not reactive — no $state needed
</script>
<button onclick={() => count++}>{count}</button>
```

- Primitives are reactive by value; objects/arrays become deep reactive proxies (has performance overhead — use `$state.raw` for large data that's only reassigned)
- Class instances are NOT made reactive — define `$state` fields inside the class:

```ts
// WRONG: let instance = $state(new MyClass());
// CORRECT:
class MyClass {
  value = $state(0);
}
```

### $state.raw — Shallow Reactive State

Creates state where only reassignment triggers updates (no deep proxy). Use for large datasets, immutable data, or values from external libraries that don't expect proxies:

```ts
let items = $state.raw(hugeArray);        // Only reassignment triggers updates
items = [...items, newItem];              // This triggers
items.push(newItem);                      // This does NOT trigger
```

### $state.snapshot — Convert Proxy to Plain Object

Converts a deep reactive proxy back to a plain object. Use for serialization, logging, or passing to external APIs:

```ts
let user = $state({ name: 'Alice', nested: { age: 30 } });
let plain = $state.snapshot(user); // Plain object, no proxy
console.log(JSON.stringify(plain));
```

### $derived — Computed Values

```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
  let expensive = $derived.by(() => heavyCalculation(count));
</script>
```

Must be pure — no side effects, no mutating `$state`. Use `$derived.by()` for multi-statement computations. Note: `$derived` values are writable (like `$state`), but re-evaluate when their expression's dependencies change.

### $effect — Side Effects (Escape Hatch)

Effects are an escape hatch — avoid them when a better alternative exists:
- Computing values? Use `$derived` instead
- Syncing to external DOM libraries? Use `{@attach ...}` instead
- Responding to user interaction? Put code in event handlers
- Debug logging? Use `$inspect` or `$inspect.trace()`
- Observing external state? Use `createSubscriber` from `svelte/reactivity`

When you do need an effect:

```ts
$effect(() => {
  console.log('Count changed:', count);
  return () => console.log('Cleanup'); // Always return cleanup for resources
});
```

Never read and write the same state (infinite loop). Effects don't run during SSR — no need to wrap contents in `if (browser)`.

**Common antipattern — `$effect` for data fetching.** If you see `$effect` + `.then()` + a cancelled flag to fetch data when inputs change, replace it with async `$derived` + `getAbortSignal()` + `<svelte:boundary>` (requires `experimental.async`):

```svelte
<!-- WRONG: Manual fetch with cancellation boilerplate -->
<script>
  let query = $state('');
  let results = $state([]);
  let loading = $state(false);

  $effect(() => {
    let cancelled = false;
    loading = true;
    fetch(`/api/search?q=${query}`)
      .then(r => r.json())
      .then(data => { if (!cancelled) results = data; })
      .finally(() => { if (!cancelled) loading = false; });
    return () => { cancelled = true; };
  });
</script>

<!-- CORRECT: Async $derived handles cancellation and loading automatically -->
<script>
  import { getAbortSignal } from 'svelte';
  let query = $state('');
  let results = $derived(await fetch(`/api/search?q=${query}`, {
    signal: getAbortSignal()
  }).then(r => r.json()));
</script>

<svelte:boundary>
  {#each results as item (item.id)}
    <div>{item.name}</div>
  {/each}
  {#snippet pending()}<p>Loading...</p>{/snippet}
  {#snippet failed(error, reset)}<p>{error.message}</p><button onclick={reset}>Retry</button>{/snippet}
</svelte:boundary>
```

**Variants:**
- `$effect.pre()` — runs before DOM updates (replaces `beforeUpdate`)
- `$effect.tracking()` — returns `true` if inside a tracking context (useful in libraries)
- `$effect.root()` — creates a manually-managed effect scope; returns a cleanup function

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

**Assume props will change.** Values derived from props should use `$derived`, not plain assignment:

```ts
let { type } = $props();
let color = $derived(type === 'danger' ? 'red' : 'green'); // Updates when type changes
// WRONG: let color = type === 'danger' ? 'red' : 'green'; // Stale after prop change
```

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

`$inspect.trace(label)` — add as the first line in `$effect` or `$derived.by` to identify which dependencies triggered re-evaluation. Essential for debugging unexpected reactivity.

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

> **When to read references:** If you encounter `$state` wrapping class instances, `$derived` causing infinite loops, or `$effect` with stale closures → read `references/gotchas.md`. If migrating a codebase from Svelte 4 syntax (`$:`, `export let`, `on:click`, `<slot>`) → read `references/migration.md`.

---

## Attachments ({@attach}) — Svelte 5.29+

Attachments replace `use:action`. They're functions that receive a DOM element, run inside an effect (inherently reactive), and work on both DOM elements and components:

```svelte
<script>
  import { tooltip } from '$lib/attachments';
</script>

<button {@attach tooltip('Hello!')}>Hover me</button>
```

Writing an attachment:

```ts
// tooltip.svelte.ts
export function tooltip(text: string) {
  return (node: HTMLElement) => {
    // Setup — runs in an effect, so reactive to `text` changes
    const tip = document.createElement('div');
    tip.textContent = text;
    // ... positioning logic ...

    return () => {
      // Cleanup — runs on re-run or destroy
      tip.remove();
    };
  };
}
```

**Key differences from `use:action`:**
- Run inside an effect — automatically re-run when dependencies change
- Work on components (not just DOM elements)
- Return cleanup function directly (no `destroy()` method)
- Use `fromAction()` from `svelte/attachments` to wrap existing actions
- Use `createAttachmentKey()` for typed attachment props

> **When to read references:** If migrating existing `use:action` code, building click-outside handlers, or need typed attachment props → read `references/attachments.md`.

---

## Async Svelte (Experimental) — Svelte 5.36+

Enable with `compilerOptions.experimental.async: true`. Allows `await` directly in `<script>`, `$derived`, and markup:

```svelte
<script>
  let { id } = $props();
  let user = $derived(await fetchUser(id)); // Re-fetches when id changes
</script>

<h1>{user.name}</h1>
```

### svelte:boundary — Error and Loading Boundaries

```svelte
<svelte:boundary>
  <MyAsyncComponent />

  {#snippet pending()}
    <p>Loading...</p>
  {/snippet}

  {#snippet failed(error, reset)}
    <p>Error: {error.message}</p>
    <button onclick={reset}>Retry</button>
  {/snippet}
</svelte:boundary>
```

Works during SSR as of Svelte 5.53+. Use `transformError` in `render()` to sanitize errors for the client.

### Key Async APIs

- **`$effect.pending()`** — returns count of pending async operations in the current boundary
- **`getAbortSignal()`** (5.35+) — returns an `AbortSignal` that aborts when the current `$derived`/`$effect` re-runs or is destroyed. The correct way to cancel stale fetches:

```ts
import { getAbortSignal } from 'svelte';

let data = $derived(await fetch(`/api/items?q=${query}`, {
  signal: getAbortSignal()
}).then(r => r.json()));
```

- **`$state.eager()`** (5.41+) — updates UI immediately during async, before the `await` resolves. Use for instant UI feedback (e.g., active link), not for critical state
- **`fork()`** (5.42+) — runs state changes offscreen to discover async work without committing. Used by SvelteKit for preloading
- **`settled()`** — returns a promise that resolves when all async work in the tree completes

> **When to read references:** If composing nested boundaries, handling async SSR errors, or using `fork()`/`settled()` → read `references/async.md`.

---

## Reactive Built-ins (svelte/reactivity)

Reactive wrappers around native APIs. **Do NOT wrap these with `$state()`** — they're already reactive:

```ts
import { MediaQuery, SvelteMap, SvelteSet, SvelteURL, SvelteDate } from 'svelte/reactivity';

// Responsive design
const isMobile = new MediaQuery('(max-width: 768px)');
// In template: {#if isMobile.current}...{/if}

// Reactive collections
const selected = new SvelteSet<string>();
const cache = new SvelteMap<string, Data>();

// Reactive URL
const url = new SvelteURL('https://example.com');
url.searchParams.set('q', 'svelte'); // Triggers reactivity

// Reactive date
const now = new SvelteDate();
```

Common gotcha: `let map = $state(new SvelteMap())` is redundant — just use `let map = new SvelteMap()`.

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

### Compound Components with createContext (5.40+)

`createContext` is the recommended way to share state between related components. It returns a type-safe `[get, set]` tuple:

```svelte
<!-- Accordion.svelte -->
<script lang="ts" module>
  import { createContext } from 'svelte';

  interface AccordionContext {
    toggle: (id: string) => void;
    isOpen: (id: string) => boolean;
  }

  const [getAccordionCtx, setAccordionCtx] = createContext<AccordionContext>();
  export { getAccordionCtx };
</script>

<script lang="ts">
  let { multiple = false, children }: Props = $props();
  let activeItems = $state(new Set<string>());
  // toggle, isOpen functions...
  setAccordionCtx({ toggle, isOpen });
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

> **When to read references:** If building compound components with shared state, implementing controlled/uncontrolled inputs, or forwarding props with TypeScript → read `references/components.md`.

---

## Events, Styling, and Patterns

### Event Listeners

Any attribute starting with `on` becomes an event listener. Use shorthand and spread:

```svelte
<button onclick={() => count++}>click</button>
<button {onclick}>shorthand</button>
<button {...props}>spread</button>
```

For window/document listeners, use special elements instead of `onMount` or `$effect`:

```svelte
<svelte:window onkeydown={handleKey} />
<svelte:document onvisibilitychange={handleVisibility} />
```

### Each Blocks

Always use keyed each blocks — they enable surgical DOM insertion/removal instead of updating existing elements:

```svelte
{#each items as item (item.id)}
  <Item {item} />
{/each}
```

**Never use array indices as keys.** Avoid destructuring when mutating items (e.g., use `bind:value={item.count}` with the full `item` reference).

### CSS Custom Properties

Pass JS variables into CSS via the `style:` directive:

```svelte
<div style:--columns={columns}>
  <!-- Uses var(--columns) in <style> -->
</div>
```

### Styling Child Components

Use CSS custom properties to control child styles from parent:

```svelte
<!-- Parent -->
<Child --color="red" />

<!-- Child.svelte -->
<h1>Hello</h1>
<style>
  h1 { color: var(--color); }
</style>
```

When you can't use custom properties (e.g., library components), use `:global`:

```svelte
<div>
  <LibraryComponent />
</div>
<style>
  div :global {
    h1 { color: red; }
  }
</style>
```

### Class Attributes

Prefer clsx-style arrays/objects in `class` attributes over the `class:` directive:

```svelte
<div class={['card', isActive && 'active', size === 'lg' && 'card-lg']}>
```

### Context Over Module State

Prefer context (`createContext`) over shared module-level state. Module state is shared across all requests during SSR, which can leak data between users. Context scopes state to the component tree:

```ts
// WRONG: Module-level state — shared across SSR requests
let user = $state(null);

// CORRECT: Use context
const [getUser, setUser] = createContext<User>();
```

---

## SvelteKit Server

### $app/state (Replacing $app/stores)

Use `$app/state` instead of the deprecated `$app/stores`:

```svelte
<script>
  import { page, navigating, updated } from '$app/state';
</script>

<!-- Access directly — no $ prefix needed, these are runes-based -->
<p>Current path: {page.url.pathname}</p>
{#if navigating.to}<p>Navigating...</p>{/if}
```

### Load Functions

```ts
// +page.server.ts — server-only, safe for secrets/DB
export const load: PageServerLoad = async ({ params, locals }) => {
  if (!locals.user) error(401, 'Unauthorized');
  return { stats: await db.stats.find({ userId: locals.user.id }) };
};
```

Use `+page.server.ts` for DB/secrets, `+layout.server.ts` for shared data, `+page.ts` for client-cacheable/public API calls. Always parallelize independent fetches with `Promise.all`.

### getRequestEvent() — SvelteKit 2.20+

Returns the current `RequestEvent` inside server code, eliminating the need to pass it through call chains:

```ts
import { getRequestEvent } from '$app/server';

export async function getCurrentUser() {
  const event = getRequestEvent();
  return event.locals.user;
}
```

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

### Shallow Routing

Update URL state without full navigation using `pushState`/`replaceState`:

```ts
import { pushState } from '$app/navigation';

pushState('/items/1', { selected: item });
```

Access in components via `page.state`.

> **When to read references:** If composing multiple hooks with `sequence()`, streaming deferred data, typing `event.locals` in `app.d.ts`, or implementing shallow routing → read `references/server-patterns.md`.

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
- `form()` — progressive enhancement forms with rich field API (`.as('text')`, `.fields.title.issues()`)
- `query.batch()` — batch multiple queries into one HTTP request
- `prerender()` — generate data at build time

### Form Validation with invalid()

```ts
import { form } from '$app/server';
import { invalid } from '@sveltejs/kit';

export const login = form(async ({ request }) => {
  const data = await request.formData();
  const email = data.get('email') as string;
  if (!email) return invalid(400, { email: 'Required' });
  // ...
});
```

Place `.remote.ts` files anywhere in `src/` except `src/lib/server/`. Use remote functions for interaction-triggered data; use load functions for SSR/SEO-critical data.

### Accessing Request Context in Remote Functions

Use `getRequestEvent()` to access auth, locals, or cookies inside remote functions without passing them as arguments:

```ts
// src/lib/todos.remote.ts
import { query } from '$app/server';
import { getRequestEvent } from '$app/server';

export const getTodos = query(async () => {
  const { locals } = getRequestEvent();
  if (!locals.user) throw new Error('Unauthorized');
  return await db.todos.findMany({ where: { userId: locals.user.id } });
});
```

### Input Validation

Always validate inputs in remote functions and form actions. Use [valibot](https://valibot.dev) (lighter, tree-shakeable) or [zod](https://zod.dev) for schema validation:

```ts
import { command } from '$app/server';
import { invalid } from '@sveltejs/kit';
import * as v from 'valibot';

const CreateTodoSchema = v.object({
  text: v.pipe(v.string(), v.minLength(1, 'Required'), v.maxLength(200)),
});

export const createTodo = command(async (input: unknown) => {
  const result = v.safeParse(CreateTodoSchema, input);
  if (!result.success) return invalid(400, { issues: result.issues });
  return await db.todos.create({ data: { text: result.output.text, done: false } });
});
```

> **When to read references:** If using form field API (`.fields`, `.as()`), request batching, `.enhance()` for custom submission, or comparing remote functions vs load functions → read `references/remote-functions.md`.

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

> **When to read references:** If setting up vitest from scratch, testing forms/async/snippets, mocking fetch, or configuring client vs server test projects → read `references/testing.md`.

---

## Performance

Svelte 5's fine-grained reactivity is fast by default. Key optimizations:

- **`$state.raw` for large data:** Avoid deep proxy overhead on big arrays/immutable data
- **Keyed each blocks:** `{#each items as item (item.id)}` — enables efficient DOM reuse
- **Memoize with $derived:** Use `$derived` for filtered/computed lists instead of recalculating in templates
- **Split reactive dependencies:** Narrow dependency scope to avoid over-reactivity
- **Always clean up effects:** Return cleanup for intervals, listeners, subscriptions
- **`getAbortSignal()`:** Cancel stale fetches in `$derived`/`$effect` automatically
- **Virtualize long lists:** Use `svelte-virtual-list` for 100+ items
- **Debounce user input:** Use `$effect` with `setTimeout` + cleanup for search inputs
- **Lazy load components:** Dynamic `import()` for heavy components
- **Stream non-critical data:** Return promises (no `await`) from load functions for streaming
- **Use `preloadData`:** `import { preloadData } from '$app/navigation'` on hover for fast navigation

> **When to read references:** If analyzing bundle size, optimizing images, profiling with DevTools/Lighthouse, or running through a pre-deploy performance checklist → read `references/performance.md`.

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

> **When to read references:** If implementing ARIA patterns (tabs, accordion, dialogs), building focus traps, or setting up automated a11y testing with axe-core → read `references/a11y.md`.

---

## Deprecated Patterns to Avoid

These Svelte 4 patterns are deprecated or superseded in Svelte 5:

| Deprecated | Replacement |
|-----------|-------------|
| `<svelte:component this={X}>` | `<X>` — components are dynamic by default |
| `use:action` | `{@attach handler}` (5.29+) |
| `createEventDispatcher()` | Callback props: `let { onclick } = $props()` |
| `<slot />` / `<slot name="x">` | `{@render children()}` / `{@render x?.()}` |
| `$app/stores` (`$page`, etc.) | `$app/state` (`page`, `navigating`, `updated`) |
| `export let` | `let { prop } = $props()` |
| `$: x = y * 2` | `let x = $derived(y * 2)` |
| `$: { sideEffect() }` | `$effect(() => { sideEffect() })` |
| `beforeUpdate` / `afterUpdate` | `$effect.pre()` / `$effect()` |
| `component.$set()` / `$on()` / `$destroy()` | `mount()` / `unmount()` from `svelte` |
| `accessors` / `immutable` compiler options | No effect in runes mode |
| Wrapping `SvelteMap`/`SvelteSet`/`MediaQuery` with `$state()` | Use directly — already reactive |
| `$$props` / `$$restProps` | `let { ...rest } = $props()` |
| `<svelte:self>` | `import Self from './Self.svelte'` then `<Self>` |
| `$$slots` | Check snippet props: `{#if header}` |
| `<svelte:fragment>` | Snippets: `{#snippet name()}...{/snippet}` |
| `class:active={isActive}` directive | `class={['base', isActive && 'active']}` |

> **Full migration guide:** Read `references/migration.md`
