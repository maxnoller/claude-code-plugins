<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Todo {
		id: number;
		text: string;
		done: boolean;
	}

	interface Props {
		row?: Snippet<[todo: Todo, toggle: (id: number) => void]>;
	}

	let { row }: Props = $props();

	let todos = $state<Todo[]>([]);
	let newText = $state('');
	let nextId = $state(1);

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

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			addTodo();
		}
	}
</script>

<div class="todo-list">
	<div class="todo-input">
		<label for="new-todo">New todo</label>
		<input
			id="new-todo"
			type="text"
			placeholder="What needs to be done?"
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
					{@render row(todo, toggle)}
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
		font-family: system-ui, -apple-system, sans-serif;
	}

	.todo-input {
		display: flex;
		gap: 0.5rem;
		align-items: end;
		margin-bottom: 0.75rem;
	}

	.todo-input label {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
	}

	.todo-input input {
		flex: 1;
		padding: 0.5rem;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 0.875rem;
	}

	.todo-input button {
		padding: 0.5rem 1rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.875rem;
	}

	.todo-input button:hover {
		background: #2563eb;
	}

	.remaining {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0 0 0.5rem;
	}

	ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	li {
		padding: 0.375rem 0;
		border-bottom: 1px solid #f3f4f6;
	}

	li label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.done {
		text-decoration: line-through;
		color: #9ca3af;
	}
</style>
