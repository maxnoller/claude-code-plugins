// src/lib/todos.remote.ts
// Full CRUD with query, command, query.batch, and Valibot validation
// Requires: kit.experimental.remoteFunctions = true

import { query, command, getRequestEvent } from '$app/server';
import { error } from '@sveltejs/kit';
import * as v from 'valibot';
import { db } from '$lib/server/database';

// --- Auth helper ---

function requireUser() {
	const { locals } = getRequestEvent();
	if (!locals.user) error(401, 'Unauthorized');
	return locals.user;
}

// --- Queries ---

export const getTodos = query(async () => {
	const user = requireUser();
	return await db.sql`
		SELECT id, text, done, created_at
		FROM todos
		WHERE user_id = ${user.id}
		ORDER BY created_at DESC
	`;
});

export const getTodoById = query(v.string(), async (id) => {
	const user = requireUser();
	const [todo] = await db.sql`
		SELECT * FROM todos WHERE id = ${id} AND user_id = ${user.id}
	`;
	if (!todo) error(404, 'Todo not found');
	return todo;
});

// --- Batched query (solves N+1 for lists) ---

export const getTodosByIds = query.batch(v.string(), async (ids) => {
	const user = requireUser();
	const todos = await db.sql`
		SELECT * FROM todos
		WHERE id = ANY(${ids}) AND user_id = ${user.id}
	`;
	const lookup = new Map(todos.map((t: { id: string }) => [t.id, t]));
	return (id: string) => lookup.get(id) ?? null;
});

// --- Commands ---

const CreateTodoSchema = v.object({
	text: v.pipe(v.string(), v.minLength(1, 'Todo text is required'))
});

export const createTodo = command(CreateTodoSchema, async ({ text }) => {
	const user = requireUser();
	const [todo] = await db.sql`
		INSERT INTO todos (text, done, user_id)
		VALUES (${text}, false, ${user.id})
		RETURNING *
	`;
	// Single-flight: refresh the list in the same response
	await getTodos().refresh();
	return todo;
});

export const toggleTodo = command(v.string(), async (id) => {
	const user = requireUser();
	const [todo] = await db.sql`
		UPDATE todos SET done = NOT done
		WHERE id = ${id} AND user_id = ${user.id}
		RETURNING *
	`;
	if (!todo) error(404, 'Todo not found');
	// Update the specific todo cache without refetching
	await getTodoById(id).set(todo);
	return todo;
});

export const deleteTodo = command(v.string(), async (id) => {
	const user = requireUser();
	await db.sql`
		DELETE FROM todos WHERE id = ${id} AND user_id = ${user.id}
	`;
	await getTodos().refresh();
});
