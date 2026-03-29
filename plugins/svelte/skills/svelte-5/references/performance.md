# Performance Optimization — Full Reference

## Reactivity Performance

### Avoid Over-Reactive Dependencies

```svelte
<script>
  let data = $state({ users: [], settings: {} });

  // BAD: Re-runs when settings change
  let userCount = $derived(data.users.length);

  // GOOD: Only depends on users array
  let users = $derived(data.users);
  let userCount = $derived(users.length);
</script>
```

### Avoid Expensive Renders in Loops

```svelte
<script>
  let items = $state([]);

  // BAD: Recalculated for every item on any change
</script>
{#each items as item}
  <div>{heavyComputation(item)}</div>
{/each}

<!-- GOOD: Precompute -->
<script>
  let processedItems = $derived(
    items.map(item => ({ ...item, computed: heavyComputation(item) }))
  );
</script>
{#each processedItems as item (item.id)}
  <div>{item.computed}</div>
{/each}
```

## Memory Management

### Clean Up Event Listeners

```svelte
<script>
  import { onMount } from 'svelte';

  onMount(() => {
    const handler = (e) => console.log(e);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  });
</script>
```

### Avoid Store Subscription Leaks

```svelte
<script>
  import { myStore } from '$lib/stores';

  // BAD: Manual subscription without cleanup
  let value;
  myStore.subscribe(v => value = v);

  // GOOD: Auto-subscription (auto-cleanup)
  let value = $myStore;
</script>
```

## Bundle Size Optimization

### Code Splitting with Dynamic Imports

```svelte
<script>
  let HeavyComponent = $state(null);

  async function loadComponent() {
    const module = await import('$lib/HeavyComponent.svelte');
    HeavyComponent = module.default;
  }
</script>

<button onclick={loadComponent}>Load Component</button>

{#if HeavyComponent}
  <svelte:component this={HeavyComponent} />
{/if}
```

### Tree-Shake Imports

```ts
// BAD: Imports entire library
import _ from 'lodash';

// GOOD: Import specific function
import debounce from 'lodash/debounce';

// BETTER: Use native or smaller alternatives
function debounce(fn, ms) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), ms);
  };
}
```

### Analyze Bundle Size

```bash
npx vite build --mode production
npx vite-bundle-visualizer
```

## Rendering Performance

### Virtualize Long Lists

For lists with 100+ items:

```svelte
<script>
  import VirtualList from 'svelte-virtual-list';

  let items = $state(Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`
  })));
</script>

<VirtualList {items} let:item>
  <div>{item.name}</div>
</VirtualList>
```

### Debounce Expensive Operations

```svelte
<script>
  let query = $state('');
  let debouncedQuery = $state('');

  $effect(() => {
    const timeout = setTimeout(() => {
      debouncedQuery = query;
    }, 300);
    return () => clearTimeout(timeout);
  });

  let results = $derived.by(async () => {
    if (!debouncedQuery) return [];
    return await search(debouncedQuery);
  });
</script>

<input bind:value={query} placeholder="Search..." />
```

## SvelteKit Performance

### Preload on Hover

```svelte
<script>
  import { preloadData } from '$app/navigation';
</script>

<a
  href="/slow-page"
  onmouseenter={() => preloadData('/slow-page')}
>
  Slow Page
</a>
```

### Cache Headers

```ts
// +page.server.ts
export const load = async ({ setHeaders }) => {
  setHeaders({ 'cache-control': 'max-age=60' });
  return { data: await fetchData() };
};
```

### Image Optimization

```svelte
<script>
  import { enhanced } from '@sveltejs/enhanced-img';
</script>

<enhanced:img src="./photo.jpg" alt="Photo" />
```

Or use `srcset` manually with `loading="lazy"` and appropriate `sizes`.

## Profiling

### Browser DevTools

1. Open DevTools > Performance tab
2. Click Record
3. Interact with your app
4. Stop recording
5. Analyze flame graph for long tasks

### Svelte DevTools

Install the Svelte DevTools browser extension to inspect component hierarchy, view `$state`/`$derived` values, and track component updates.

### Lighthouse

```bash
npx lighthouse http://localhost:5173 --view
```

## Performance Checklist

- [ ] Use `(key)` in `{#each}` blocks
- [ ] Clean up effects, listeners, subscriptions
- [ ] Use `$derived` for computed values
- [ ] Lazy load heavy components
- [ ] Virtualize long lists (100+ items)
- [ ] Debounce user input handlers
- [ ] Use `loading="lazy"` on images
- [ ] Stream non-critical data
- [ ] Analyze bundle with visualizer
- [ ] Test on low-end devices
