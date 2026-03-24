---
name: SvelteKit Remote Functions
description: This skill should be used when the user asks to "create a remote function", "use query()", "use command()", "use form()", "use prerender()", "batch queries", "server RPC", "type-safe API", "call server from client", or works with .remote.ts files, $app/server imports, single-flight mutations, remote form validation, or server-side data fetching in SvelteKit. Covers the full remote functions API (query, command, form, prerender, batch) as of SvelteKit 2.54.
---

# SvelteKit Remote Functions

Remote functions enable type-safe server calls directly from client components. They replace many use cases for load functions and form actions with a simpler RPC-style API.

**Status:** Experimental (SvelteKit 2.27+, significant iteration through 2.54)

## Setup

```js
// svelte.config.js
const config = {
  kit: {
    experimental: { remoteFunctions: true }
  },
  compilerOptions: {
    experimental: { async: true }  // enables await in components
  }
};
```

## File Convention

Files use `.remote.ts` extension. Place anywhere in `src/` except `src/lib/server/`:

```
src/
├── lib/
│   ├── todos.remote.ts       # CRUD operations
│   ├── auth.remote.ts        # Authentication
│   └── server/               # Server-only (NO .remote.ts here)
│       └── db.ts
├── routes/
│   └── blog/
│       └── data.remote.ts    # Route-colocated
```

## query — Server Data Fetching

Read-only server queries with automatic caching:

```ts
// src/lib/data.remote.ts
import { query } from '$app/server';
import * as v from 'valibot';

// No arguments
export const getPosts = query(async () => {
  return await db.sql`SELECT title, slug FROM post ORDER BY published_at DESC`;
});

// With Standard Schema validation (Valibot, Zod, etc.)
export const getPost = query(v.string(), async (slug) => {
  const [post] = await db.sql`SELECT * FROM post WHERE slug = ${slug}`;
  if (!post) error(404, 'Not found');
  return post;
});
```

In components (with async/await):

```svelte
<script>
  import { getPosts } from '$lib/data.remote';
</script>

{#each await getPosts() as { title, slug }}
  <a href="/blog/{slug}">{title}</a>
{/each}
```

**Query properties:** `.loading`, `.error`, `.current`, `.refresh()`

Queries are **cached per page** — `getPosts() === getPosts()` returns the same promise.

## query.batch — Solving N+1 Problems

Batch calls within the same macrotask into a single request (SvelteKit 2.35+):

```ts
export const getWeather = query.batch(v.string(), async (cityIds) => {
  const weather = await db.sql`SELECT * FROM weather WHERE city_id = ANY(${cityIds})`;
  const lookup = new Map(weather.map(w => [w.city_id, w]));
  return (cityId) => lookup.get(cityId);
});
```

The callback receives an **array** of all arguments and returns a resolver function `(input, index) => Output`.

## command — Server Mutations

Mutations triggered by user interaction:

```ts
export const addLike = command(v.string(), async (id) => {
  await db.sql`UPDATE item SET likes = likes + 1 WHERE id = ${id}`;
  await getLikes(id).refresh();  // single-flight: piggyback on response
});
```

```svelte
<button onclick={() => addLike(item.id)}>Like</button>
```

**Rules:** Cannot call during render. `redirect()` does not work in commands — return an object instead. `command.pending` tracks active count.

## form — Progressive Enhancement Forms

Type-safe forms with validation, working with and without JavaScript:

```ts
import { form } from '$app/server';
import * as v from 'valibot';

export const createPost = form(
  v.object({
    title: v.pipe(v.string(), v.nonEmpty()),
    content: v.pipe(v.string(), v.nonEmpty())
  }),
  async ({ title, content }) => {
    const slug = title.toLowerCase().replace(/ /g, '-');
    await db.sql`INSERT INTO post (slug, title, content) VALUES (${slug}, ${title}, ${content})`;
    redirect(303, `/blog/${slug}`);
  }
);
```

In components — spread form and field props:

```svelte
<form {...createPost}>
  <input {...createPost.fields.title.as('text')} />
  {#each createPost.fields.title.issues() as issue}
    <span class="error">{issue.message}</span>
  {/each}

  <textarea {...createPost.fields.content.as('text')}></textarea>
  <button>Publish</button>
</form>
```

**Field `.as()` types:** `'text'`, `'number'`, `'password'`, `'email'`, `'file'`, `'checkbox'`, `'radio'`, `'submit'`, `'select'`, `'select multiple'`

For detailed form patterns (validation, enhance, multiple instances, file uploads), see `references/form-patterns.md`.

## prerender — Build-Time Data

Pre-compute query results at build time:

```ts
export const getPost = prerender(v.string(), async (slug) => {
  const [post] = await db.sql`SELECT * FROM post WHERE slug = ${slug}`;
  if (!post) error(404, 'Not found');
  return post;
}, {
  inputs: () => ['first-post', 'second-post'],
  dynamic: true  // also available at runtime for unknown args
});
```

Cached via browser Cache API; cleared on new deployment.

## Single-Flight Mutations

Piggyback data refresh on mutation responses to avoid extra round-trips:

```ts
// Server-side: inside command/form handler
await getPosts().refresh();           // re-fetch, include in response
await getPost(id).set(updatedPost);   // set directly without fetching

// Client-side: via enhance or after command
await addLike(id).updates(getLikes(id));
await addLike(id).updates(getLikes(id).withOverride((n) => n + 1));
```

## Request Context & Auth

Access request data via `getRequestEvent()`:

```ts
import { query, getRequestEvent } from '$app/server';

export const getProfile = query(async () => {
  const { cookies, locals } = getRequestEvent();
  if (!locals.user) redirect(303, '/login');
  return await db.getProfile(locals.user.id);
});
```

**Limitations:** Cannot set response headers (except cookies in form/command). `route`, `params`, `url` relate to the calling page, not the endpoint. Never use `getRequestEvent()` to authorize page access.

## Validation

Remote functions use **Standard Schema** (Valibot, Zod, ArkType). To skip validation:

```ts
export const getStuff = query('unchecked', async ({ id }: { id: string }) => {
  // no runtime validation — use only for trusted internal calls
});
```

Handle validation errors globally in `src/hooks.server.js`:

```js
export function handleValidationError({ event, issues }) {
  return { message: 'Invalid request' };
}
```

## When to Use Remote Functions vs Load Functions

| Use Case | Remote Functions | Load Functions |
|---|---|---|
| Initial page render / SEO | No | Yes |
| User-triggered data fetching | Yes | No |
| Mutations / form submissions | Yes | Use form actions |
| Component-level data | Yes | Awkward |
| Preloading on hover | No | Yes |
| Static sites | No | Yes |

## Critical Rules

1. **Never put `.remote.ts` in `src/lib/server/`** — will not work
2. **Always validate with schemas** — client input is untrusted; use `'unchecked'` only for internal calls
3. **Return serializable data** — devalue supports Date, Map, Set, BigInt, RegExp, Error, ArrayBuffer, typed arrays
4. **Prefix sensitive form fields with underscore** — `_password` prevents repopulation
5. **Cannot use on prerendered pages** — requires a running server
6. **Commands cannot call during render** — only in event handlers
7. **Queries are cached per page** — same call returns same promise

## Additional Resources

### Reference Files
- **`references/form-patterns.md`** — Complete form API: field methods, enhance(), multiple instances, file uploads, imperative validation with invalid()
- **`references/version-history.md`** — API changes across SvelteKit versions

### Example Files
- **`examples/todos.remote.ts`** — CRUD with query/command and Valibot validation
- **`examples/auth-form.remote.ts`** — Login form with progressive enhancement
