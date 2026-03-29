# Async Svelte — Full Reference

Experimental feature (Svelte 5.36+) that enables `await` directly in components. Requires `compilerOptions.experimental.async: true` in `svelte.config.js`.

## Await in $derived

Fetch data reactively — re-fetches when dependencies change:

```svelte
<script>
  import { getAbortSignal } from 'svelte';

  let { userId } = $props();

  let user = $derived(await fetch(`/api/users/${userId}`, {
    signal: getAbortSignal()
  }).then(r => r.json()));
</script>

<h1>{user.name}</h1>
```

When `userId` changes, the previous fetch is automatically aborted via `getAbortSignal()` and a new one starts.

## Await in Script

```svelte
<script>
  let config = await fetch('/api/config').then(r => r.json());
</script>

<p>Theme: {config.theme}</p>
```

## svelte:boundary

Provides error handling and loading states for async children:

```svelte
<svelte:boundary>
  <UserProfile userId={selectedId} />

  {#snippet pending()}
    <div class="skeleton">Loading profile...</div>
  {/snippet}

  {#snippet failed(error, reset)}
    <div class="error">
      <p>Failed to load: {error.message}</p>
      <button onclick={reset}>Retry</button>
    </div>
  {/snippet}
</svelte:boundary>
```

### Nested Boundaries

Boundaries can be nested for granular loading states:

```svelte
<svelte:boundary>
  <Layout>
    <svelte:boundary>
      <Sidebar />
      {#snippet pending()}<SidebarSkeleton />{/snippet}
    </svelte:boundary>

    <svelte:boundary>
      <MainContent />
      {#snippet pending()}<ContentSkeleton />{/snippet}
    </svelte:boundary>
  </Layout>

  {#snippet pending()}<FullPageSpinner />{/snippet}
</svelte:boundary>
```

### Error-Only Boundaries (No Async)

`<svelte:boundary>` also works as a pure error boundary without async:

```svelte
<svelte:boundary onerror={(error) => logError(error)}>
  <RiskyComponent />

  {#snippet failed(error, reset)}
    <p>Something went wrong</p>
    <button onclick={reset}>Try again</button>
  {/snippet}
</svelte:boundary>
```

### SSR Error Boundaries (5.53+)

Error boundaries now work during SSR. Use `transformError` in the `render()` call to sanitize errors before sending to the client:

```ts
// +page.server.ts or entry-server.ts
import { render } from 'svelte/server';

const result = render(App, {
  props: { ... },
  transformError: (error) => {
    // Don't expose internal errors to client
    return new Error('Something went wrong');
  }
});
```

## getAbortSignal() — Svelte 5.35+

Returns an `AbortSignal` that automatically aborts when the current `$derived` or `$effect` re-runs or is destroyed. Essential for preventing race conditions:

```ts
import { getAbortSignal } from 'svelte';

// In $derived — aborts when dependencies change
let data = $derived(await fetchData(query, { signal: getAbortSignal() }));

// In $effect — aborts on re-run or component destroy
$effect(() => {
  fetch(`/api/search?q=${query}`, { signal: getAbortSignal() })
    .then(r => r.json())
    .then(data => results = data);
});
```

## $effect.pending()

Returns the number of pending async operations within the closest `<svelte:boundary>`. Useful for showing progress indicators:

```svelte
<svelte:boundary>
  <Dashboard />

  {#snippet pending()}
    {#if $effect.pending() > 0}
      <ProgressBar pending={$effect.pending()} />
    {/if}
  {/snippet}
</svelte:boundary>
```

## $state.eager() — Svelte 5.41+

Updates the UI immediately during async operations, before the `await` resolves. Use sparingly — only for UI feedback, not critical state:

```svelte
<script>
  let activeTab = $state.eager('home');

  // UI updates immediately to show the new tab as active,
  // even while async content is loading
  let content = $derived(await loadTabContent(activeTab));
</script>

<nav>
  {#each tabs as tab}
    <button
      class:active={activeTab === tab.id}
      onclick={() => activeTab = tab.id}
    >
      {tab.label}
    </button>
  {/each}
</nav>

<svelte:boundary>
  <div>{@html content}</div>
  {#snippet pending()}<Spinner />{/snippet}
</svelte:boundary>
```

## fork() — Svelte 5.42+

Runs state changes "offscreen" to discover async work without committing to the screen. Primarily used by frameworks (SvelteKit uses this for preloading):

```ts
import { fork } from 'svelte';

// Preload data without showing it yet
const result = await fork(() => {
  selectedItem = nextItem; // Triggers async derived values
});
// result contains the resolved async state
```

## settled()

Returns a promise that resolves when all async work in the component tree completes:

```ts
import { settled } from 'svelte';

// Wait for all pending async operations
await settled();
```

Useful in tests and server-side rendering.

## Patterns

### Search with Debounce and Abort

```svelte
<script>
  import { getAbortSignal } from 'svelte';

  let query = $state('');
  let debouncedQuery = $state('');

  $effect(() => {
    const timeout = setTimeout(() => debouncedQuery = query, 300);
    return () => clearTimeout(timeout);
  });

  let results = $derived(
    debouncedQuery.length >= 2
      ? await fetch(`/api/search?q=${debouncedQuery}`, {
          signal: getAbortSignal()
        }).then(r => r.json())
      : []
  );
</script>

<svelte:boundary>
  <input bind:value={query} />
  <ul>
    {#each results as result (result.id)}
      <li>{result.title}</li>
    {/each}
  </ul>

  {#snippet pending()}<p>Searching...</p>{/snippet}
</svelte:boundary>
```

### Parallel Async Data

```svelte
<script>
  import { getAbortSignal } from 'svelte';

  let { userId } = $props();
  const signal = getAbortSignal();

  let [user, posts] = $derived(await Promise.all([
    fetch(`/api/users/${userId}`, { signal }).then(r => r.json()),
    fetch(`/api/users/${userId}/posts`, { signal }).then(r => r.json())
  ]));
</script>
```

## Important Notes

1. Async components are **suspended** until their async work completes — wrap with `<svelte:boundary>` to show loading states
2. `getAbortSignal()` must be called **synchronously** inside `$derived` or `$effect`, not inside a `.then()` callback
3. This feature will become stable in Svelte 6
4. Remote functions (`query()`, `command()`) work seamlessly with async Svelte
