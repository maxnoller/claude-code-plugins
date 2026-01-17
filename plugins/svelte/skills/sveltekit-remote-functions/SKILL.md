---
name: SvelteKit Remote Functions
description: Patterns for SvelteKit remote functions (query, command, form, batch) from $app/server. Use when working with .remote.ts files, server-side data fetching with query(), mutations with command(), form handling with form(), request batching, or when users ask about calling server functions from client code, type-safe RPC, or replacing load functions with remote functions.
---

# SvelteKit Remote Functions

Remote functions allow calling server-side code directly from client components with full type safety. They replace many use cases for load functions and form actions.

**Status:** Experimental (requires configuration)

## Setup

Enable in `svelte.config.js`:

```js
const config = {
  kit: {
    experimental: { remoteFunctions: true }
  },
  compilerOptions: {
    experimental: { async: true }
  }
};

export default config;
```

## Core Functions

### query - Server Data Fetching

Create read-only server queries:

```ts
// src/lib/todos.remote.ts
import { query } from '$app/server';
import { db } from '$lib/db';

export const getTodos = query(async () => {
  return await db.todos.findMany();
});

export const getTodoById = query(async (id: string) => {
  return await db.todos.findUnique({ where: { id } });
});
```

Use in components:

```svelte
<script>
  import { getTodos } from '$lib/todos.remote';

  let todos = $state<Todo[]>([]);

  $effect(() => {
    getTodos().then(data => todos = data);
  });
</script>
```

**How it works:**
- On server: Executes directly
- On client: Automatically wraps in `fetch()` call
- Full TypeScript inference end-to-end

### command - Server Mutations

Create server-side mutations:

```ts
// src/lib/todos.remote.ts
import { command } from '$app/server';
import { db } from '$lib/db';

export const createTodo = command(async (text: string) => {
  return await db.todos.create({ data: { text, done: false } });
});

export const toggleTodo = command(async (id: string) => {
  const todo = await db.todos.findUnique({ where: { id } });
  return await db.todos.update({
    where: { id },
    data: { done: !todo?.done }
  });
});

export const deleteTodo = command(async (id: string) => {
  await db.todos.delete({ where: { id } });
});
```

Use in components:

```svelte
<script>
  import { createTodo, toggleTodo, deleteTodo } from '$lib/todos.remote';

  let newText = $state('');

  async function handleSubmit() {
    await createTodo(newText);
    newText = '';
    // Refetch or invalidate
  }
</script>

<form onsubmit={handleSubmit}>
  <input bind:value={newText} />
  <button>Add</button>
</form>
```

### form - Progressive Enhancement Forms

Create forms that work with and without JavaScript:

```ts
// src/lib/auth.remote.ts
import { form } from '$app/server';
import { fail, redirect } from '@sveltejs/kit';

export const login = form(async ({ request }) => {
  const data = await request.formData();
  const email = data.get('email') as string;
  const password = data.get('password') as string;

  if (!email || !password) {
    return fail(400, { error: 'Email and password required' });
  }

  const user = await authenticate(email, password);
  if (!user) {
    return fail(401, { error: 'Invalid credentials', email });
  }

  redirect(303, '/dashboard');
});
```

Use in components:

```svelte
<script>
  import { login } from '$lib/auth.remote';
</script>

<form {...login.spread()}>
  <input name="email" type="email" />
  <input name="password" type="password" />
  <button>Login</button>
</form>
```

**Progressive enhancement:**
- Without JS: Standard form submission, full page reload
- With JS: AJAX submission, partial update

### batch - Request Batching

Batch multiple queries into a single HTTP request (SvelteKit 2.38+):

```ts
// src/lib/data.remote.ts
import { query } from '$app/server';

export const getUserById = query(async (id: string) => {
  return await db.users.findUnique({ where: { id } });
});

// Enable batching
export const getUserByIdBatched = query.batch(
  async (ids: string[]) => {
    const users = await db.users.findMany({ where: { id: { in: ids } } });
    return (id: string) => users.find(u => u.id === id);
  }
);
```

Use in components:

```svelte
<script>
  import { getUserByIdBatched } from '$lib/data.remote';

  // These calls are batched into one request
  let user1 = getUserByIdBatched('1');
  let user2 = getUserByIdBatched('2');
  let user3 = getUserByIdBatched('3');
</script>

{#await Promise.all([user1, user2, user3])}
  Loading...
{:then [u1, u2, u3]}
  {u1.name}, {u2.name}, {u3.name}
{/await}
```

## Form Handling Patterns

### Validation with Zod

```ts
// src/lib/contact.remote.ts
import { form } from '$app/server';
import { fail } from '@sveltejs/kit';
import { z } from 'zod';

const ContactSchema = z.object({
  name: z.string().min(1, 'Name required'),
  email: z.string().email('Invalid email'),
  message: z.string().min(10, 'Message too short')
});

export const submitContact = form(async ({ request }) => {
  const formData = await request.formData();
  const data = Object.fromEntries(formData);

  const result = ContactSchema.safeParse(data);
  if (!result.success) {
    return fail(400, {
      errors: result.error.flatten().fieldErrors,
      data
    });
  }

  await sendEmail(result.data);
  return { success: true };
});
```

### Form State Management

```svelte
<script>
  import { submitContact } from '$lib/contact.remote';

  let form = $state({
    name: '',
    email: '',
    message: ''
  });
  let errors = $state<Record<string, string[]>>({});
  let submitting = $state(false);

  async function handleSubmit(e: Event) {
    e.preventDefault();
    submitting = true;
    errors = {};

    const formData = new FormData(e.target as HTMLFormElement);
    const result = await submitContact.call(formData);

    if (result?.errors) {
      errors = result.errors;
    }
    submitting = false;
  }
</script>

<form onsubmit={handleSubmit}>
  <input name="name" bind:value={form.name} />
  {#if errors.name}<span class="error">{errors.name[0]}</span>{/if}

  <input name="email" type="email" bind:value={form.email} />
  {#if errors.email}<span class="error">{errors.email[0]}</span>{/if}

  <textarea name="message" bind:value={form.message}></textarea>
  {#if errors.message}<span class="error">{errors.message[0]}</span>{/if}

  <button disabled={submitting}>
    {submitting ? 'Sending...' : 'Send'}
  </button>
</form>
```

## File Organization

Place `.remote.ts` files anywhere in `src/` except `src/lib/server/`:

```
src/
├── lib/
│   ├── todos.remote.ts      # Todo operations
│   ├── auth.remote.ts       # Authentication
│   └── server/              # Server-only (cannot use .remote.ts here)
│       └── db.ts
├── routes/
│   └── api/
│       └── users.remote.ts  # Can colocate with routes
```

## When to Use Remote Functions vs Load Functions

**Use remote functions when:**
- Fetching data on user interaction (not initial page load)
- Component-level data that doesn't need SSR
- Mutations and form submissions
- Data needed by deeply nested components

**Use load functions when:**
- Data needed for initial page render (SEO)
- Data that should be part of SSR HTML
- Page-level data requirements
- Preloading on hover/navigation

## Comparison with tRPC

| Feature | Remote Functions | tRPC |
|---------|-----------------|------|
| Setup | Built-in (config flag) | Separate package |
| Type safety | Full | Full |
| File convention | `.remote.ts` | Routers |
| Batching | Native | Plugin |
| Forms | `form()` helper | Manual |
| Learning curve | Low (SvelteKit native) | Medium |

## Critical Rules

1. **Never put `.remote.ts` in `src/lib/server/`** - It won't work
2. **Always validate on server** - Client can be bypassed
3. **Return serializable data** - No functions, classes, or circular refs
4. **Handle errors gracefully** - Use `fail()` for expected errors
5. **Consider caching** - Remote functions don't cache by default
