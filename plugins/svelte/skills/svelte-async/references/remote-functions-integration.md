# Async + Remote Functions Integration

Remote functions and async await work together to enable reactive server data fetching directly in components.

## Configuration

Both features need to be enabled:

```js
// svelte.config.js
export default {
  kit: {
    experimental: { remoteFunctions: true }
  },
  compilerOptions: {
    experimental: { async: true }
  }
};
```

## Basic Pattern

```svelte
<script>
  import { getPosts } from '$lib/data.remote';
</script>

<svelte:boundary>
  {#each await getPosts() as post}
    <article>
      <h2>{post.title}</h2>
      <p>{post.excerpt}</p>
    </article>
  {/each}

  {#snippet pending()}
    <p>Loading posts...</p>
  {/snippet}
</svelte:boundary>
```

## Reactive Queries

```svelte
<script>
  import { getPostsByTag } from '$lib/data.remote';

  let tag = $state('svelte');
  const posts = $derived(await getPostsByTag(tag));
</script>

<select bind:value={tag}>
  <option>svelte</option>
  <option>javascript</option>
</select>

<svelte:boundary>
  {#each posts as post}
    <article>{post.title}</article>
  {/each}

  {#snippet pending()}
    <p>Loading...</p>
  {/snippet}
</svelte:boundary>

{#if $effect.pending()}
  <p class="update-indicator">Fetching new posts...</p>
{/if}
```

## Query Properties

Remote `query()` returns objects with useful properties:

```ts
const result = getPosts();

result.loading;    // boolean — currently fetching
result.error;      // error if failed
result.current;    // last resolved value
result.refresh();  // re-fetch from server
```

## Mutations with Single-Flight Updates

After a command, piggyback the data refresh on the response:

```svelte
<script>
  import { getPosts, createPost } from '$lib/data.remote';

  async function handleCreate(title: string) {
    // Single-flight: createPost response includes refreshed getPosts data
    await createPost({ title }).updates(getPosts());
  }
</script>
```

## Parallel Queries (Avoiding Waterfall)

```svelte
<script>
  import { getUser, getPosts, getNotifications } from '$lib/data.remote';

  // Create promises (parallel)
  let userP = $derived(getUser());
  let postsP = $derived(getPosts());
  let notificationsP = $derived(getNotifications());

  // Await results (still parallel)
  let user = $derived(await userP);
  let posts = $derived(await postsP);
  let notifications = $derived(await notificationsP);
</script>
```

## Batched Queries

`query.batch` combines multiple calls into a single HTTP request:

```svelte
<script>
  import { getUserById } from '$lib/data.remote';
</script>

<!-- These three calls are batched into one HTTP request -->
<svelte:boundary>
  <p>{(await getUserById('1')).name}</p>
  <p>{(await getUserById('2')).name}</p>
  <p>{(await getUserById('3')).name}</p>

  {#snippet pending()}
    <p>Loading users...</p>
  {/snippet}
</svelte:boundary>
```
