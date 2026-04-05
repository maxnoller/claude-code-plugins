<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Todo {
		id: number;
		text: string;
		done: boolean;
	}

	interface Props {
		initial?: Todo[];
		row?: Snippet<[{ todo: Todo; toggle: () => void }]>;
	}

	let { initial = [], row }: Props = $props();

	let todos: Todo[] = $state(initial);
	let newText = $state('');
	let nextId = $state(initial.length ? Math.max(...initial.map((t) => t.id)) + 1 : 1);

	let remaining = $derived(todos.filter((t) => !t.done).length);

	function addTodo() {
		const trimmed = newText.trim();
		if (!trimmed) return;
		todos.push({ id: nextId++, text: trimmed, done: false });
		newText = '';
	}

	function toggle(id: number) {
		const todo = todos.find((t) => t.id === id);
		if (todo) todo.done = !todo.done;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') addTodo();
	}
</script>

<div class="todo-list">
	<div class="input-row">
		<input
			type="text"
			placeholder="Add a todo..."
			bind:value={newText}
			onkeydown={handleKeydown}
		/>
		<button onclick={addTodo}>Add</button>
	</div>

	<p class="remaining">{remaining} item{remaining === 1 ? '' : 's'} remaining</p>

	<ul>
		{#each todos as todo (todo.id)}
			<li>
				{#if row}
					{@render row({ todo, toggle: () => toggle(todo.id) })}
				{:else}
					<label>
						<input
							type="checkbox"
							checked={todo.done}
							onchange={() => toggle(todo.id)}
						/>
						<span class:done={todo.done}>{todo.text}</span>
					</label>
				{/if}
			</li>
		{/each}
	</ul>
</div>

<style>
	.todo-list {
		max-width: 28rem;
		font-family: system-ui, sans-serif;
	}

	.input-row {
		display: flex;
		gap: 0.5rem;
	}

	.input-row input {
		flex: 1;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	.input-row button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		background: #4a90d9;
		color: white;
		cursor: pointer;
	}

	.remaining {
		font-size: 0.875rem;
		color: #666;
		margin: 0.5rem 0;
	}

	ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	li {
		padding: 0.375rem 0;
		border-bottom: 1px solid #eee;
	}

	label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.done {
		text-decoration: line-through;
		opacity: 0.5;
	}
</style>
