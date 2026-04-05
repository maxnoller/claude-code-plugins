<script lang="ts">
	import TodoList from './TodoList.svelte';
</script>

<main>
	<h1>Todo App</h1>

	<section>
		<h2>Default rendering</h2>
		<TodoList />
	</section>

	<section>
		<h2>Custom row via snippet</h2>
		<TodoList>
			{#snippet row(todo, toggle)}
				<div class="custom-row">
					<button class="toggle-btn" onclick={() => toggle(todo.id)}>
						{todo.done ? '✔' : '○'}
					</button>
					<span class:struck={todo.done}>{todo.text}</span>
					{#if todo.done}
						<span class="badge">done</span>
					{/if}
				</div>
			{/snippet}
		</TodoList>
	</section>
</main>

<style>
	main {
		max-width: 36rem;
		margin: 2rem auto;
		font-family: system-ui, -apple-system, sans-serif;
	}

	section {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 1.5rem;
		margin-bottom: 1.5rem;
	}

	h2 {
		font-size: 1.125rem;
		margin-bottom: 0.75rem;
		color: #374151;
	}

	.custom-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.25rem 0;
	}

	.toggle-btn {
		background: none;
		border: 1px solid #d1d5db;
		border-radius: 50%;
		width: 1.5rem;
		height: 1.5rem;
		cursor: pointer;
		font-size: 0.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.struck {
		text-decoration: line-through;
		opacity: 0.5;
	}

	.badge {
		font-size: 0.625rem;
		text-transform: uppercase;
		background: #d1fae5;
		color: #065f46;
		padding: 0.125rem 0.375rem;
		border-radius: 9999px;
	}
</style>
