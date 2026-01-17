<script lang="ts">
    let searchQuery = $state("");
    let results = $state<string[]>([]);
    let loading = $state(false);

    // $effect with cleanup for fetch cancellation
    $effect(() => {
        if (!searchQuery.trim()) {
            results = [];
            return;
        }

        const controller = new AbortController();
        loading = true;

        fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`, {
            signal: controller.signal,
        })
            .then((r) => r.json())
            .then((data) => {
                results = data;
                loading = false;
            })
            .catch((err) => {
                if (err.name !== "AbortError") {
                    console.error("Search failed:", err);
                    loading = false;
                }
            });

        // Cleanup: abort fetch when query changes or component unmounts
        return () => controller.abort();
    });
</script>

<div>
    <input type="search" placeholder="Search..." bind:value={searchQuery} />

    {#if loading}
        <p>Searching...</p>
    {:else if results.length > 0}
        <ul>
            {#each results as result}
                <li>{result}</li>
            {/each}
        </ul>
    {:else if searchQuery}
        <p>No results found</p>
    {/if}
</div>
