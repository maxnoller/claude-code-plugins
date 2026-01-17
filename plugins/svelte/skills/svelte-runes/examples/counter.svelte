<script lang="ts">
	// Counter with $state - basic reactive state
	let count = $state(0);
	
	// $derived - computed value that auto-updates
	let doubled = $derived(count * 2);
	
	// $derived.by - for multi-statement computations
	let analysis = $derived.by(() => {
		if (count === 0) return 'zero';
		if (count % 2 === 0) return 'even';
		return 'odd';
	});
</script>

<div>
	<p>Count: {count}</p>
	<p>Doubled: {doubled}</p>
	<p>Analysis: {analysis}</p>
	
	<button onclick={() => count++}>Increment</button>
	<button onclick={() => count--}>Decrement</button>
	<button onclick={() => count = 0}>Reset</button>
</div>
