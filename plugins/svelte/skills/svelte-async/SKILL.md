---
name: Svelte 5 Async Patterns
description: This skill should be used when the user asks to "use await in a component", "async derived", "fetch data in $derived", "async SSR", "svelte:boundary pending", "use getAbortSignal", "use fork()", "use settled()", "async rendering", "$effect.pending", or works with await expressions, async data fetching, suspense-like patterns, or the experimental async mode in Svelte 5. Covers await expressions (Svelte 5.36+), fork() (5.42+), and async SSR.
---

# Svelte 5 Async Patterns

Svelte 5.36+ adds `await` expressions directly in components. Experimental — will stabilize in Svelte 6.

## Setup

```js
// svelte.config.js
export default {
  compilerOptions: {
    experimental: { async: true }
  }
};
```

Caveat: when enabled, block effects (`{#if}`, `{#each}`) run before `$effect.pre` in the same component.

## Where await Works

### Top-level script

```svelte
<script>
  const user = await fetch('/api/user').then(r => r.json());
</script>
```

### Inside $derived (reactive async)

```svelte
<script>
  let city = $state('New York');
  const weather = $derived(await getWeather(city));
</script>
```

Refetches automatically when `city` changes. Old values display until the new result arrives.

### In markup

```svelte
<p>{a} + {b} = {await add(a, b)}</p>
```

`await` is NOT allowed in `use:`, `transition:`, `animate:`, attachments, or bindings.

## svelte:boundary

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

`pending` renders only during **initial** load. For update indicators, use `$effect.pending()` which returns the count of pending promises in the current boundary.

Error boundaries catch rendering and effect errors, not event handler or setTimeout errors.

## Consistency Guarantee

Async expressions block dependent UI updates until resolved — values always display consistently. Exception: focused `<input>` elements update immediately.

## Parallel Execution & Waterfall Avoidance

Independent await expressions in markup run in parallel automatically.

Sequential `$derived` chains create waterfalls. Fix by separating promise creation from awaiting:

```ts
// Waterfall:
let a = $derived(await one(x));  // blocks
let b = $derived(await two(y));  // waits for a

// Parallel:
let aP = $derived(one(x));
let bP = $derived(two(y));
let a = $derived(await aP);
let b = $derived(await bP);
```

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

## fork() — Speculative State (5.42+)

Evaluate state changes without applying to DOM. Primary use: preloading on hover.

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
>Open menu</button>
```

Returns `{ commit(): Promise<void>, discard(): void }`. Cannot create inside effects or when state changes are pending.

## settled() vs tick()

```ts
import { tick, settled } from 'svelte';
await tick();      // DOM updated, async deriveds may still be pending
await settled();   // DOM updated AND all async work resolved
```

## {#await} vs Inline await

| | `{#await}` block | Inline `await` |
|---|---|---|
| Experimental flag | No | Yes |
| Reactive | Manual | Automatic via `$derived` |
| Loading state | Per-promise `{:then}/{:catch}` | `<svelte:boundary>` |
| Parallel | Manual | Automatic in markup |
| Consistency | No | Yes |

Use `{#await}` for one-off promises and lazy imports. Use inline `await` for reactive data and coordinated updates.

## SSR

`await render(App)` resolves async work outside `pending` boundaries before returning. Content in `<svelte:boundary>` with `pending` renders the pending state during SSR. Streaming SSR planned but not yet implemented.

## Additional Resources

- **`references/error-reference.md`** — Compiler/runtime errors and warnings for async
- **`references/remote-functions-integration.md`** — Using await with remote functions
- **`examples/async-search.svelte`** — Reactive search with abort and pending indicator
- **`examples/data-preload.svelte`** — fork() hover preloading
