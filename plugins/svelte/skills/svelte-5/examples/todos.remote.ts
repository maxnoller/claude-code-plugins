// src/lib/todos.remote.ts
// SvelteKit Remote Functions for Todo CRUD operations
// Requires: kit.experimental.remoteFunctions = true in svelte.config.js

import { query, command } from '$app/server';
import * as v from 'valibot';
import { sql } from '$lib/server/database';

// Query: Read-only server data (no arguments)
export const getTodos = query(async () => {
    const todos = await sql`
		SELECT id, text, done, created_at
		FROM todos
		ORDER BY created_at DESC
	`;
    return todos;
});

// Query with validated argument
export const getTodoById = query(
    v.string(), // Validate that id is a string
    async (id) => {
        const [todo] = await sql`
			SELECT * FROM todos WHERE id = ${id}
		`;
        return todo ?? null;
    }
);

// Command: Mutations (with validated input)
const CreateTodoSchema = v.object({
    text: v.pipe(v.string(), v.minLength(1, 'Todo text is required'))
});

export const createTodo = command(
    CreateTodoSchema,
    async ({ text }) => {
        const [todo] = await sql`
			INSERT INTO todos (text, done)
			VALUES (${text}, false)
			RETURNING *
		`;
        return todo;
    }
);

// Toggle todo completion
export const toggleTodo = command(
    v.string(), // id
    async (id) => {
        const [todo] = await sql`
			UPDATE todos
			SET done = NOT done
			WHERE id = ${id}
			RETURNING *
		`;
        if (!todo) throw new Error('Todo not found');
        return todo;
    }
);

// Delete todo
export const deleteTodo = command(
    v.string(), // id
    async (id) => {
        await sql`DELETE FROM todos WHERE id = ${id}`;
    }
);
