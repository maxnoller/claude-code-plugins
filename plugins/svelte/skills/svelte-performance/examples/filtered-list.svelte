<script lang="ts">
    let items = $state(generateItems(10000));
    let filter = $state("");

    // Memoized filtering - only recalculates when dependencies change
    let filteredItems = $derived(
        items.filter((item) =>
            item.name.toLowerCase().includes(filter.toLowerCase()),
        ),
    );

    // Debounced search input
    let debouncedFilter = $state("");

    $effect(() => {
        const timeout = setTimeout(() => {
            debouncedFilter = filter;
        }, 300);
        return () => clearTimeout(timeout);
    });

    function generateItems(count: number) {
        return Array.from({ length: count }, (_, i) => ({
            id: i,
            name: `Item ${i}`,
            value: Math.random() * 100,
        }));
    }
</script>

<div>
    <input type="search" placeholder="Filter items..." bind:value={filter} />

    <p>{filteredItems.length} items</p>

    <!-- Virtualization recommended for 100+ items -->
    <!-- Using svelte-virtual-list or similar -->
    {#each filteredItems.slice(0, 100) as item (item.id)}
        <div class="item">
            {item.name}: {item.value.toFixed(2)}
        </div>
    {/each}

    {#if filteredItems.length > 100}
        <p>Showing 100 of {filteredItems.length}...</p>
    {/if}
</div>
