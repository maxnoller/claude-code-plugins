<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		header?: Snippet;
		footer?: Snippet;
		children: Snippet;
		variant?: 'default' | 'outlined' | 'elevated';
	}

	let { header, footer, children, variant = 'default' }: Props = $props();
</script>

<article class="card card-{variant}">
	{#if header}
		<header class="card-header">
			{@render header()}
		</header>
	{/if}
	
	<div class="card-body">
		{@render children()}
	</div>
	
	{#if footer}
		<footer class="card-footer">
			{@render footer()}
		</footer>
	{/if}
</article>

<style>
	.card {
		border-radius: 8px;
		overflow: hidden;
	}
	
	.card-default {
		background: white;
		border: 1px solid #e5e7eb;
	}
	
	.card-outlined {
		background: transparent;
		border: 2px solid currentColor;
	}
	
	.card-elevated {
		background: white;
		box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
	}
	
	.card-header {
		padding: 1rem;
		border-bottom: 1px solid #e5e7eb;
	}
	
	.card-body {
		padding: 1rem;
	}
	
	.card-footer {
		padding: 1rem;
		border-top: 1px solid #e5e7eb;
	}
</style>
