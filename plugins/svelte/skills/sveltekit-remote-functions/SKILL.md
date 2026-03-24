---
name: SvelteKit Remote Functions
description: This skill should be used when the user asks to "create a remote function", "use query()", "use command()", "use form()", "use prerender()", "batch queries", "server RPC", "type-safe API", "call server from client", or works with .remote.ts files, $app/server imports, single-flight mutations, remote form validation, or server-side data fetching in SvelteKit. Covers the full remote functions API (query, command, form, prerender, batch) as of SvelteKit 2.54.
---

# SvelteKit Remote Functions

Type-safe server calls from client components. Experimental (SvelteKit 2.27+, iterated through 2.54).

## Setup

```js
// svelte.config.js
const config = {
  kit: { experimental: { remoteFunctions: true } },
  compilerOptions: { experimental: { async: true } }
};
```

Files use `.remote.ts` extension. Place anywhere in `src/` **except** `src/lib/server/`.

## query

```ts
import { query } from '$app/server';
import * as v from 'valibot';

export const getPosts = query(async () => {
  return await db.sql`SELECT title, slug FROM post ORDER BY published_at DESC`;
});

export const getPost = query(v.string(), async (slug) => {
  const [post] = await db.sql`SELECT * FROM post WHERE slug = ${slug}`;
  if (!post) error(404, 'Not found');
  return post;
});
```

```svelte
{#each await getPosts() as { title, slug }}
  <a href="/blog/{slug}">{title}</a>
{/each}
```

Properties: `.loading`, `.error`, `.current`, `.refresh()`. Queries are cached per page.

Validation uses **Standard Schema** (Valibot, Zod, ArkType). Pass `'unchecked'` to skip.

## query.batch

Solves N+1 — batches calls within the same macrotask (2.35+):

```ts
export const getWeather = query.batch(v.string(), async (cityIds) => {
  const weather = await db.sql`SELECT * FROM weather WHERE city_id = ANY(${cityIds})`;
  const lookup = new Map(weather.map(w => [w.city_id, w]));
  return (cityId) => lookup.get(cityId);
});
```

Callback receives an **array** of all arguments, returns a resolver `(input, index) => Output`.

## command

```ts
export const addLike = command(v.string(), async (id) => {
  await db.sql`UPDATE item SET likes = likes + 1 WHERE id = ${id}`;
  await getLikes(id).refresh();  // single-flight mutation
});
```

Cannot call during render. `redirect()` doesn't work — return an object instead. `command.pending` tracks active count.

## form

Type-safe progressive enhancement forms:

```ts
export const createPost = form(
  v.object({
    title: v.pipe(v.string(), v.nonEmpty()),
    content: v.pipe(v.string(), v.nonEmpty())
  }),
  async ({ title, content }) => {
    await db.sql`INSERT INTO post ...`;
    redirect(303, `/blog/${slug}`);
  }
);
```

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

Field `.as()` types: `'text'`, `'number'`, `'password'`, `'email'`, `'file'`, `'checkbox'`, `'radio'`, `'submit'`, `'select'`, `'select multiple'`. Prefix sensitive fields with underscore (`_password`) to prevent repopulation.

See `references/form-patterns.md` for field methods, `enhance()`, multiple instances, file uploads, and `invalid()`.

## prerender

Build-time data with optional runtime fallback:

```ts
export const getPost = prerender(v.string(), async (slug) => {
  const [post] = await db.sql`SELECT * FROM post WHERE slug = ${slug}`;
  if (!post) error(404, 'Not found');
  return post;
}, {
  inputs: () => ['first-post', 'second-post'],
  dynamic: true
});
```

## Single-Flight Mutations

Piggyback data refresh on mutation responses:

```ts
// Server-side (inside command/form handler)
await getPosts().refresh();
await getPost(id).set(updatedPost);

// Client-side
await addLike(id).updates(getLikes(id));
await addLike(id).updates(getLikes(id).withOverride((n) => n + 1));
```

## Request Context

```ts
import { query, getRequestEvent } from '$app/server';

export const getProfile = query(async () => {
  const { cookies, locals } = getRequestEvent();
  if (!locals.user) redirect(303, '/login');
  return await db.getProfile(locals.user.id);
});
```

Limitations: cannot set response headers (except cookies in form/command). `route`/`params`/`url` relate to the calling page. Never use `getRequestEvent()` to authorize page access.

## Remote Functions vs Load Functions

| Use Case | Remote Functions | Load Functions |
|---|---|---|
| Initial page render / SEO | No | Yes |
| User-triggered data fetching | Yes | No |
| Mutations / forms | Yes | Form actions |
| Component-level data | Yes | Awkward |
| Preloading on hover | No | Yes |
| Static sites | No | Yes |

## Additional Resources

- **`references/form-patterns.md`** — Field methods, enhance(), multiple instances, file uploads, invalid()
- **`references/version-history.md`** — API changes across SvelteKit versions (2.27–2.54)
- **`examples/todos.remote.ts`** — CRUD with query/command
- **`examples/auth-form.remote.ts`** — Login form with progressive enhancement
