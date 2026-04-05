<script lang="ts">
	import TodoList from './TodoList.svelte';
</script>

<h1>Todo App</h1>

<h2>Default rendering</h2>
<TodoList
	initial={[
		{ id: 1, text: 'Buy groceries', done: false },
		{ id: 2, text: 'Walk the dog', done: true }
	]}
/>

<h2>Custom row via snippet</h2>
<TodoList
	initial={[
		{ id: 1, text: 'Read a book', done: false },
		{ id: 2, text: 'Write some code', done: false }
	]}
>
	{#snippet row({ todo, toggle })}
		<div class="custom-row">
			<button onclick={toggle}>
				{todo.done ? '✅' : '⬜'}
			</button>
			<span class:struck={todo.done}>{todo.text}</span>
		</div>
	{/snippet}
</TodoList>

<style>
	h1 {
		font-family: system-ui, sans-serif;
	}

	h2 {
		font-family: system-ui, sans-serif;
		font-size: 1.1rem;
		margin-top: 2rem;
	}

	.custom-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.custom-row button {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 1.2rem;
		padding: 0;
	}

	.struck {
		text-decoration: line-through;
		color: #999;
	}
</style>
