---
name: Svelte Performance Optimization
description: Performance optimization techniques for Svelte 5 and SvelteKit applications. Use when users ask about performance, optimization, slow rendering, bundle size, memory leaks, profiling, lazy loading, code splitting, or when diagnosing performance issues in Svelte applications.
---

# Svelte Performance Optimization

Svelte 5's fine-grained reactivity provides excellent performance by default, but understanding optimization patterns helps build fast applications at scale.

## Reactivity Performance

### Fine-Grained Updates

Svelte 5 runes enable granular reactivity—only affected DOM nodes update:

```svelte
<script>
  let items = $state([
    { id: 1, name: 'Item 1', count: 0 },
    { id: 2, name: 'Item 2', count: 0 }
  ]);

  function increment(item) {
    // Only this item's count triggers updates
    item.count++;
  }
</script>

{#each items as item (item.id)}
  <div>
    {item.name}: {item.count}
    <button onclick={() => increment(item)}>+</button>
  </div>
{/each}
```

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

### Use $derived for Expensive Computations

```svelte
<script>
  let items = $state([]);
  let filter = $state('');

  // Memoized - only recalculates when items or filter change
  let filteredItems = $derived(
    items.filter(item =>
      item.name.toLowerCase().includes(filter.toLowerCase())
    )
  );
</script>
```

## Memory Management

### Clean Up Effects

Always return cleanup functions:

```svelte
<script>
  let count = $state(0);

  // BAD: Memory leak
  $effect(() => {
    const id = setInterval(() => count++, 1000);
    // No cleanup!
  });

  // GOOD: Proper cleanup
  $effect(() => {
    const id = setInterval(() => count++, 1000);
    return () => clearInterval(id);
  });
</script>
```

### Clean Up Event Listeners

```svelte
<script>
  import { onMount } from 'svelte';

  onMount(() => {
    const handler = (e) => console.log(e);
    window.addEventListener('resize', handler);

    return () => {
      window.removeEventListener('resize', handler);
    };
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

  // GOOD: Manual with cleanup
  import { onDestroy } from 'svelte';
  const unsubscribe = myStore.subscribe(v => value = v);
  onDestroy(unsubscribe);
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

### Route-Based Code Splitting

SvelteKit automatically splits by route. Enhance with:

```ts
// src/routes/admin/+page.ts
export const load = async () => {
  // Only loads when visiting /admin
  const { AdminDashboard } = await import('$lib/admin');
  return { AdminDashboard };
};
```

### Tree-Shake Imports

```ts
// BAD: Imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 300);

// GOOD: Import specific function
import debounce from 'lodash/debounce';
const result = debounce(fn, 300);

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
# Build with stats
npx vite build --mode production

# Visualize bundle
npx vite-bundle-visualizer
```

## Rendering Performance

### Use Keyed Each Blocks

```svelte
<!-- BAD: No key, DOM recreated on reorder -->
{#each items as item}
  <Item {item} />
{/each}

<!-- GOOD: Keyed, DOM moves efficiently -->
{#each items as item (item.id)}
  <Item {item} />
{/each}
```

### Avoid Expensive Renders in Loops

```svelte
<script>
  let items = $state([]);

  // BAD: Recalculated for every item on any change
  function getExpensiveData(item) {
    return heavyComputation(item);
  }
</script>

<!-- BAD -->
{#each items as item}
  <div>{getExpensiveData(item)}</div>
{/each}

<!-- GOOD: Precompute or memoize -->
<script>
  let processedItems = $derived(
    items.map(item => ({
      ...item,
      computed: heavyComputation(item)
    }))
  );
</script>

{#each processedItems as item (item.id)}
  <div>{item.computed}</div>
{/each}
```

### Virtualize Long Lists

For lists with 100+ items, use virtualization:

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

### Streaming with defer

Return promises for non-critical data:

```ts
// +page.server.ts
export const load = async () => {
  return {
    // Critical: blocks render
    user: await getUser(),
    // Non-critical: streams after initial render
    recommendations: getRecommendations() // Note: no await
  };
};
```

```svelte
<script>
  let { data } = $props();
</script>

<h1>Welcome, {data.user.name}</h1>

{#await data.recommendations}
  <p>Loading recommendations...</p>
{:then recs}
  {#each recs as rec}
    <div>{rec.title}</div>
  {/each}
{/await}
```

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
  setHeaders({
    'cache-control': 'max-age=60'
  });

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

Or use `srcset` manually:

```svelte
<img
  src="/images/photo-800.jpg"
  srcset="
    /images/photo-400.jpg 400w,
    /images/photo-800.jpg 800w,
    /images/photo-1200.jpg 1200w
  "
  sizes="(max-width: 600px) 400px, 800px"
  loading="lazy"
  alt="Photo"
/>
```

## Profiling

### Browser DevTools

1. Open DevTools → Performance tab
2. Click Record
3. Interact with your app
4. Stop recording
5. Analyze flame graph for long tasks

### Svelte DevTools

Install the Svelte DevTools browser extension:
- Inspect component hierarchy
- View `$state` and `$derived` values
- Track component updates

### Lighthouse

```bash
# Run Lighthouse audit
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
