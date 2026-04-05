---
name: svelte-5
description: This skill should be used when the user asks to "write a Svelte component", "add $state", "use $derived", "create a SvelteKit page", "add form actions", "set up remote functions", "test Svelte components", "fix Svelte antipatterns", "migrate from Svelte 4", "use attachments", "add async await to Svelte", "review .svelte files", or works with any .svelte/.svelte.ts files, runes, SvelteKit routes, or Svelte 5 patterns. This skill should also be triggered when the context involves Svelte or SvelteKit code even if the user doesn't explicitly say "Svelte" — for example when editing files with .svelte extensions or working in a SvelteKit project structure.
---

# Svelte 5

Svelte 5 uses runes — compiler-driven reactivity primitives replacing Svelte 4's implicit reactivity.

## Runes

### $state

Only apply `$state` to variables that drive UI updates. Objects/arrays become deep reactive proxies (performance overhead — prefer `$state.raw` for large data). Class instances are NOT made reactive — define `$state` fields inside the class.

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
  let API_URL = 'https://api.example.com'; // Not reactive — no $state needed
</script>
```

- **`$state.raw(data)`** — only reassignment triggers updates (no proxy). Use for large datasets, immutable data, or external library values.
- **`$state.snapshot(proxy)`** — convert deep reactive proxy to plain object for serialization or external APIs.

### $derived

```ts
let doubled = $derived(count * 2);
let expensive = $derived.by(() => heavyCalculation(count));
```

Keep pure — no side effects, no mutating `$state`. `$derived` values are writable but re-evaluate when dependencies change.

### $effect (Escape Hatch)

Treat effects as a last resort. Prefer these alternatives:
- Computing values → `$derived`
- Syncing to external DOM → `{@attach ...}`
- User interaction → event handlers
- Debug logging → `$inspect` / `$inspect.trace()`
- External state → `createSubscriber` from `svelte/reactivity`

```ts
$effect(() => {
  console.log('Count changed:', count);
  return () => console.log('Cleanup');
});
```

Never read and write the same state (infinite loop). Effects don't run during SSR — no `if (browser)` wrapper needed.

**Antipattern — `$effect` for data fetching:** Replace `$effect` + `.then()` + cancelled flag with async `$derived` + `getAbortSignal()` + `<svelte:boundary>`. See `references/gotchas.md` for the full before/after pattern.

**Variants:** `$effect.pre()` (before DOM update), `$effect.tracking()` (check tracking context), `$effect.root()` (manual scope).

### $props

```svelte
<script lang="ts">
  interface Props { name: string; age?: number; onclick?: () => void; }
  let { name, age = 18, onclick }: Props = $props();
</script>
```

Rest props: `let { class: className, ...rest } = $props();`

Assume props will change — always derive computed values from props with `$derived`:

```ts
let { type } = $props();
let color = $derived(type === 'danger' ? 'red' : 'green');
```

### Other Runes

- **`$bindable()`** — allow parent `bind:` on a prop: `let { value = $bindable() } = $props()`
- **`$inspect(value)`** — log changes in dev (stripped in production). Add `$inspect.trace(label)` as first line in `$effect`/`$derived.by` to debug which dependencies triggered re-evaluation.

### Runes in .svelte.ts Files

Runes work outside components in `.svelte.ts` files. Only rename to `.svelte.ts` when the file directly declares runes.

```ts
// counter.svelte.ts
export function createCounter(initial = 0) {
  let count = $state(initial);
  return { get count() { return count }, increment: () => count++ };
}
```

### Critical Rules

1. Runes are top-level only (except in `.svelte.ts` files)
2. `$effect` doesn't run during SSR — use load functions for server data
3. Global `$state` is shared across SSR requests — avoid module-level mutable state
4. `$derived` tracks dependencies at runtime, not compile time
5. Always return cleanup from `$effect`

> **When to read references:** Encountering `$state` wrapping class instances, `$derived` infinite loops, `$effect` stale closures, or `$effect` data fetching → `references/gotchas.md`. Migrating Svelte 4 syntax (`$:`, `export let`, `on:click`, `<slot>`) → `references/migration.md`.

---

## Attachments ({@attach}) — 5.29+

Replacements for `use:action`. Run inside an effect (inherently reactive), work on both DOM elements and components:

```svelte
<button {@attach tooltip('Hello!')}>Hover me</button>
```

```ts
// tooltip.svelte.ts
export function tooltip(text: string) {
  return (node: HTMLElement) => {
    node.title = text;
    return () => { node.title = ''; }; // Cleanup
  };
}
```

Wrap existing actions with `fromAction()` from `svelte/attachments`. Use `createAttachmentKey()` for typed attachment props.

> **When to read references:** Migrating `use:action` code, click-outside handlers, typed attachment props → `references/attachments.md`.

---

## Async Svelte (Experimental) — 5.36+

Enable with `compilerOptions.experimental.async: true`. Allows `await` directly in `$derived` and `<script>`:

```svelte
<script>
  import { getAbortSignal } from 'svelte';
  let { id } = $props();
  let user = $derived(await fetch(`/api/users/${id}`, { signal: getAbortSignal() }).then(r => r.json()));
</script>
```

### svelte:boundary

```svelte
<svelte:boundary>
  <AsyncComponent />
  {#snippet pending()}<p>Loading...</p>{/snippet}
  {#snippet failed(error, reset)}<p>{error.message}</p><button onclick={reset}>Retry</button>{/snippet}
</svelte:boundary>
```

**Key APIs:** `$effect.pending()` (pending count), `getAbortSignal()` (auto-cancel stale fetches), `$state.eager()` (immediate UI update), `fork()` (offscreen preloading), `settled()` (wait for all async).

> **When to read references:** Nested boundaries, async SSR errors, `fork()`/`settled()` → `references/async.md`.

---

## Reactive Built-ins (svelte/reactivity)

**Do NOT wrap with `$state()`** — already reactive:

```ts
import { MediaQuery, SvelteMap, SvelteSet, SvelteURL, SvelteDate } from 'svelte/reactivity';
const isMobile = new MediaQuery('(max-width: 768px)');
const selected = new SvelteSet<string>();
const cache = new SvelteMap<string, Data>();
```

---

## Components

### Snippets (Replacing Slots)

```svelte
<!-- Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { header, children }: { header?: Snippet; children: Snippet } = $props();
</script>
<div class="card">
  {#if header}{@render header()}{/if}
  {@render children()}
</div>
```

With parameters: `row: Snippet<[item: T, index: number]>` → `{@render row(item, index)}`. Always use `{@render icon?.()}` for optional snippets.

### Compound Components — createContext (5.40+)

Type-safe `[get, set]` tuple for sharing state between related components:

```ts
// In <script module>
import { createContext } from 'svelte';
const [getCtx, setCtx] = createContext<AccordionContext>();
```

Prefer `createContext` over manual `setContext`/`getContext` with Symbol keys.

### Context Over Module State

Module state is shared across SSR requests — leaks data between users. Scope state with context instead.

> **When to read references:** Compound components, controlled/uncontrolled inputs, prop forwarding → `references/components.md`. Events, styling, CSS custom properties, class arrays → `references/patterns.md`.

---

## SvelteKit Server

### $app/state (Replacing $app/stores)

```svelte
<script>
  import { page, navigating, updated } from '$app/state';
</script>
<p>Current path: {page.url.pathname}</p>
```

### Load Functions

```ts
export const load: PageServerLoad = async ({ params, locals }) => {
  if (!locals.user) error(401, 'Unauthorized');
  return { stats: await db.stats.find({ userId: locals.user.id }) };
};
```

Use `+page.server.ts` for DB/secrets, `+layout.server.ts` for shared data, `+page.ts` for public API calls. Parallelize with `Promise.all`.

### getRequestEvent()

Access `RequestEvent` inside any server function without passing it down:

```ts
import { getRequestEvent } from '$app/server';
export async function getCurrentUser() {
  return getRequestEvent().locals.user;
}
```

### Form Actions

```ts
export const actions: Actions = {
  login: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    if (!email) return fail(400, { email, missing: true });
    cookies.set('session', (await authenticate(email, data.get('password') as string)).sessionId, { path: '/' });
    redirect(303, '/dashboard');
  }
};
```

Progressive enhancement: `<form method="POST" action="?/login" use:enhance>`

### Hooks, API Routes, Shallow Routing

- **Hooks:** `handle` for auth middleware, `sequence()` to compose, `handleFetch` for internal API auth, `handleError` for tracking
- **API routes:** `GET`/`POST`/etc. in `+server.ts`
- **Shallow routing:** `pushState`/`replaceState` from `$app/navigation` for URL state without full nav

> **When to read references:** Composing hooks, streaming deferred data, typing `event.locals`, shallow routing details → `references/server-patterns.md`.

---

## Remote Functions (Experimental)

Enable with `kit.experimental.remoteFunctions: true` and `compilerOptions.experimental.async: true`.

```ts
import { query, command } from '$app/server';
export const getTodos = query(async () => await db.todos.findMany());
export const createTodo = command(async (text: string) => {
  return await db.todos.create({ data: { text, done: false } });
});
```

**Core functions:** `query()` (reads), `command()` (mutations), `form()` (progressive enhancement), `query.batch()` (batching), `prerender()` (build-time).

### Request Context

Access auth/locals inside remote functions with `getRequestEvent()`:

```ts
export const getTodos = query(async () => {
  const { locals } = getRequestEvent();
  if (!locals.user) throw new Error('Unauthorized');
  return await db.todos.findMany({ where: { userId: locals.user.id } });
});
```

### Input Validation

Validate inputs with [valibot](https://valibot.dev) (lighter) or [zod](https://zod.dev):

```ts
import * as v from 'valibot';
const Schema = v.object({ text: v.pipe(v.string(), v.minLength(1), v.maxLength(200)) });

export const createTodo = command(async (input: unknown) => {
  const result = v.safeParse(Schema, input);
  if (!result.success) return invalid(400, { issues: result.issues });
  return await db.todos.create({ data: { text: result.output.text, done: false } });
});
```

Place `.remote.ts` anywhere in `src/` except `src/lib/server/`.

> **When to read references:** Form field API, batching, `.enhance()`, streaming uploads → `references/remote-functions.md`.

---

## Testing

Use `vitest-browser-svelte` for real browser testing (not jsdom):

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

Prefer semantic queries: `getByRole` > `getByLabel` > `getByText` > `getByTestId`. Test runes in `.svelte.ts` with `flushSync()` + `untrack()`. Browser tests: `*.svelte.test.ts`, server tests: `*.test.ts`.

> **When to read references:** Vitest setup, form/async/snippet testing, mocking fetch → `references/testing.md`.

---

## Performance

Fast by default. Key optimizations: `$state.raw` for large data, keyed `{#each}` blocks (never index keys), `$derived` for memoization, `getAbortSignal()` for fetch cancellation, virtualization for 100+ items, debounced input via `$effect` + `setTimeout` cleanup, dynamic `import()` for lazy loading, streaming non-critical data from load functions, `preloadData` on hover.

> **When to read references:** Bundle analysis, image optimization, profiling, pre-deploy checklist → `references/performance.md`.

---

## Accessibility

Svelte has built-in a11y compiler warnings. Key practices: semantic HTML (`<button>` not `<div onclick>`), `<label>` on every input, `aria-describedby`/`aria-invalid`/`role="alert"` for form errors, focus traps in modals, keyboard navigation (Arrow/Home/End/Escape), `aria-live="polite"` for dynamic content, `prefers-reduced-motion` respect, 4.5:1 contrast ratio.

> **When to read references:** ARIA patterns (tabs, accordion, dialogs), focus traps, axe-core testing → `references/a11y.md`.

---

## Deprecated Patterns

| Deprecated | Replacement |
|-----------|-------------|
| `<svelte:component this={X}>` | `<X>` — dynamic by default |
| `use:action` | `{@attach handler}` |
| `createEventDispatcher()` | Callback props |
| `<slot />` / `<slot name="x">` | `{@render children()}` / `{@render x?.()}` |
| `$app/stores` | `$app/state` |
| `export let` | `$props()` |
| `$:` reactive statements | `$derived` / `$effect` |
| `beforeUpdate` / `afterUpdate` | `$effect.pre()` / `$effect()` |
| `class:name={cond}` | `class={[..., cond && 'name']}` |

> **Full table with all deprecated patterns:** `references/migration.md`
