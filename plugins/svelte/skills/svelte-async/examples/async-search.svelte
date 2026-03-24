<!-- Reactive search with abort signal and pending indicator -->
<script lang="ts">
  import { getAbortSignal } from 'svelte';

  let query = $state('');

  async function search(q: string): Promise<{ title: string; url: string }[]> {
    if (!q.trim()) return [];
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, {
      signal: getAbortSignal()
    });
    if (!res.ok) throw new Error('Search failed');
    return res.json();
  }

  // Re-runs automatically when query changes
  // Previous fetch is aborted via getAbortSignal()
  const results = $derived(await search(query));
</script>

<div class="search">
  <input
    type="search"
    bind:value={query}
    placeholder="Search..."
  />

  {#if $effect.pending()}
    <span class="spinner" aria-label="Searching">...</span>
  {/if}
</div>

<svelte:boundary>
  {#if results.length > 0}
    <ul>
      {#each results as result}
        <li><a href={result.url}>{result.title}</a></li>
      {/each}
    </ul>
  {:else if query.trim()}
    <p>No results for "{query}"</p>
  {/if}

  {#snippet pending()}
    <p>Searching...</p>
  {/snippet}

  {#snippet failed(error, reset)}
    <p>Search error: {error.message}</p>
    <button onclick={reset}>Retry</button>
  {/snippet}
</svelte:boundary>
