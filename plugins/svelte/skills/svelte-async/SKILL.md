---
name: Svelte 5 Async Patterns
description: This skill should be used when the user asks to "use await in a component", "async derived", "fetch data in $derived", "async SSR", "svelte:boundary pending", "use getAbortSignal", "use fork()", "use settled()", "async rendering", "$effect.pending", or works with await expressions, async data fetching, suspense-like patterns, or the experimental async mode in Svelte 5. Covers await expressions (Svelte 5.36+), fork() (5.42+), and async SSR.
---

# Svelte 5 Async Patterns

Svelte 5.36+ introduces `await` expressions directly in components — reactive async state, coordinated updates, and suspense-like boundaries.

**Status:** Experimental (will stabilize in Svelte 6)

## Setup

```js
// svelte.config.js
export default {
  compilerOptions: {
    experimental: { async: true }
  }
};
```

**Caveat:** When enabled, block effects (`{#if}`, `{#each}`) run before `$effect.pre` in the same component.

## Three Places Where await Works

### 1. Top-level script

```svelte
<script>
  const user = await fetch('/api/user').then(r => r.json());
</script>

<h1>{user.name}</h1>
```

### 2. Inside $derived (reactive async)

```svelte
<script>
  let city = $state('New York');
  const weather = $derived(await getWeather(city));
</script>

<p>{weather.temp}°</p>
```

When `city` changes, `weather` automatically refetches. The UI stays consistent — old values display until the new result arrives.

### 3. In markup expressions

```svelte
<p>{a} + {b} = {await add(a, b)}</p>
```

**Restriction:** `await` is NOT allowed in `use:`, `transition:`, `animate:`, attachments, or bindings.

## svelte:boundary with pending

Wrap async content in a boundary to show loading state:

```svelte
<svelte:boundary>
  <UserProfile id={userId} />

  {#snippet pending()}
    <p>Loading...</p>
  {/snippet}

  {#snippet failed(error, reset)}
    <p>Error: {error.message}</p>
    <button onclick={reset}>Retry</button>
  {/snippet}
</svelte:boundary>
```

**Key behaviors:**
- `pending` renders only during **initial** load — subsequent updates keep showing the old value
- Use `$effect.pending()` for update indicators after initial load
- Error boundaries catch rendering errors and effect errors, NOT event handler or setTimeout errors

## $effect.pending()

Returns the count of pending promises in the current boundary:

```svelte
<p>{a} + {b} = {await add(a, b)}</p>

{#if $effect.pending()}
  <span class="spinner">Updating...</span>
{/if}
```

Only callable inside an effect or derived — errors outside reactive context.

## Synchronized Updates (Consistency Guarantee)

Async expressions block dependent UI updates until resolved:

```svelte
<script>
  let a = $state(1);
  let b = $state(2);
</script>

<p>{a} + {b} = {await add(a, b)}</p>
```

The values `a`, `b`, and the result always display consistently — never "2 + 2 = 2". Exception: focused `<input>` elements update immediately.

## Parallel Execution

Independent await expressions in markup run simultaneously:

```svelte
<!-- These fetch in parallel, not sequentially -->
<li>Apples: {await getPrice('apple')}</li>
<li>Bananas: {await getPrice('banana')}</li>
```

### Avoiding Waterfall in $derived

**Problem — sequential:**
```ts
let a = $derived(await one(x));  // blocks
let b = $derived(await two(y));  // waits for a
```

**Solution — create promises first, then await:**
```ts
let aPromise = $derived(one(x));
let bPromise = $derived(two(y));

let a = $derived(await aPromise);  // parallel
let b = $derived(await bPromise);  // parallel
```

The compiler warns with `await_waterfall` when a derived is not read immediately after resolving.

## getAbortSignal()

Auto-abort when a derived/effect re-runs or is destroyed:

```svelte
<script>
  import { getAbortSignal } from 'svelte';

  let id = $state(1);
  const data = $derived(await fetch(`/items/${id}`, {
    signal: getAbortSignal()
  }).then(r => r.json()));
</script>
```

Must be called inside an effect or derived.

## fork() — Speculative State (Svelte 5.42+)

Create state changes evaluated but not applied to DOM. Primary use: preloading data on hover:

```svelte
<script>
  import { fork } from 'svelte';

  let open = $state(false);
  let pending: ReturnType<typeof fork> | null = null;

  function preload() {
    pending ??= fork(() => { open = true; });
  }
</script>

<button
  onpointerenter={preload}
  onpointerleave={() => { pending?.discard(); pending = null; }}
  onclick={() => { pending?.commit(); pending = null; open = true; }}
>
  Open menu
</button>

{#if open}
  <Menu onclose={() => open = false} />
{/if}
```

**API:** `fork(fn)` returns `{ commit(): Promise<void>, discard(): void }`. Cannot create inside an effect or when state changes are pending.

## settled() and tick()

```ts
import { tick, settled } from 'svelte';

async function handleClick() {
  color = 'blue';
  await tick();      // DOM updated, but async deriveds may still be pending
  await settled();   // DOM updated AND all async work resolved
}
```

## {#await} Block vs Inline await

| Feature | `{#await}` block | Inline `await` |
|---|---|---|
| Requires experimental flag | No | Yes |
| Reactive (re-runs on state change) | Manual | Automatic with `$derived` |
| Loading state | Per-promise `{:then}` / `{:catch}` | `<svelte:boundary>` + `pending` |
| Parallel execution | Manual | Automatic in markup |
| Consistency guarantee | No | Yes (synchronized updates) |
| SSR | Renders pending branch | Resolves before render (or pending boundary) |

**Use `{#await}` for:** One-off promises, lazy-loaded components, explicit per-promise loading states.
**Use inline `await` for:** Reactive data, coordinated UI updates, component-level data loading.

## SSR Behavior

- `await render(App)` resolves all async work outside `pending` boundaries before returning
- Content inside `<svelte:boundary>` with `pending` snippet renders the pending state during SSR
- Error boundaries work on server since Svelte 5.53.0
- Streaming SSR planned but not yet implemented

## Critical Rules

1. **Always wrap async components in `<svelte:boundary>`** with a `pending` snippet
2. **Use `getAbortSignal()`** for fetch calls in `$derived` to prevent stale responses
3. **Avoid waterfall** — split promise creation from awaiting in sequential `$derived` chains
4. **`$effect.pending()` only in reactive context** — errors if called outside effect/derived
5. **`fork()` cannot nest** — cannot create inside effects or when state changes are pending
6. **`await` not allowed in directives** — no `use:`, `transition:`, `animate:`, attachments, or bindings

## Additional Resources

### Reference Files
- **`references/error-reference.md`** — Compiler and runtime error/warning reference for async patterns
- **`references/remote-functions-integration.md`** — Using async await with remote functions

### Example Files
- **`examples/async-search.svelte`** — Reactive search with abort and pending indicator
- **`examples/data-preload.svelte`** — fork() pattern for hover preloading
