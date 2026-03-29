# SvelteKit Server Patterns — Full Reference

## $app/state (Replacing $app/stores)

Use `$app/state` instead of the deprecated `$app/stores`:

```svelte
<script>
  // OLD (deprecated):
  // import { page, navigating, updated } from '$app/stores';
  // Access via $page, $navigating, $updated

  // NEW:
  import { page, navigating, updated } from '$app/state';
  // Access directly — no $ prefix, these are runes-based
</script>

<p>Current path: {page.url.pathname}</p>
<p>Current user: {page.data.user?.name}</p>
{#if navigating.to}<p>Navigating to {navigating.to.url.pathname}...</p>{/if}
```

`$app/stores` is deprecated and will be removed in SvelteKit 3.

## getRequestEvent() — SvelteKit 2.20+

Returns the current `RequestEvent` inside server hooks, load functions, actions, endpoints, and functions called by them. Eliminates the need to pass the event down call chains:

```ts
import { getRequestEvent } from '$app/server';

// Can be called from any server-side function during a request
export async function getCurrentUser() {
  const event = getRequestEvent();
  return event.locals.user;
}

export async function requireAuth() {
  const event = getRequestEvent();
  if (!event.locals.user) {
    throw error(401, 'Unauthorized');
  }
  return event.locals.user;
}
```

## Load Function Decision Guide

| Use case | File |
|----------|------|
| Database queries | `+page.server.ts` |
| API keys/secrets | `+page.server.ts` |
| Shared auth state | `+layout.server.ts` |
| Client-side caching | `+page.ts` |
| Public API calls | `+page.ts` |

## Parallel Loading

```ts
export const load: PageServerLoad = async ({ fetch }) => {
  // DON'T: Sequential (slow)
  const user = await fetch('/api/user').then(r => r.json());
  const posts = await fetch('/api/posts').then(r => r.json());

  // DO: Parallel (fast)
  const [user, posts] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/posts').then(r => r.json())
  ]);

  return { user, posts };
};
```

## Using Parent Data

```ts
// src/routes/dashboard/settings/+page.server.ts
export const load: PageServerLoad = async ({ parent }) => {
  // Avoid waterfall - fetch your data first
  const settings = await db.settings.find();
  // Then get parent data
  const { user } = await parent();
  return { settings, user };
};
```

## Named Form Actions

```ts
export const actions: Actions = {
  login: async ({ request }) => { /* ... */ },
  register: async ({ request }) => { /* ... */ },
  logout: async ({ cookies }) => {
    cookies.delete('session', { path: '/' });
    redirect(303, '/');
  }
};
```

```svelte
<form method="POST" action="?/login"><!-- login form --></form>
<form method="POST" action="?/register"><!-- register form --></form>
<form method="POST" action="?/logout"><button>Logout</button></form>
```

## Progressive Enhancement

```svelte
<script>
  import { enhance } from '$app/forms';
  let loading = $state(false);
</script>

<form
  method="POST"
  use:enhance={() => {
    loading = true;
    return async ({ update }) => {
      await update();
      loading = false;
    };
  }}
>
  <button disabled={loading}>
    {loading ? 'Submitting...' : 'Submit'}
  </button>
</form>
```

## Hooks

### Sequence Multiple Handles

```ts
import { sequence } from '@sveltejs/kit/hooks';

const auth: Handle = async ({ event, resolve }) => {
  const session = event.cookies.get('session');
  if (session) event.locals.user = await getUserFromSession(session);
  return resolve(event);
};

const logger: Handle = async ({ event, resolve }) => {
  console.log(`${event.request.method} ${event.url.pathname}`);
  return resolve(event);
};

export const handle = sequence(auth, logger);
```

### handleFetch — Modify Server Fetches

```ts
export const handleFetch: HandleFetch = async ({ request, fetch }) => {
  if (request.url.startsWith('https://api.internal/')) {
    request = new Request(request, {
      headers: {
        ...Object.fromEntries(request.headers),
        'Authorization': `Bearer ${API_KEY}`
      }
    });
  }
  return fetch(request);
};
```

### handleError — Error Tracking

```ts
export const handleError: HandleServerError = async ({ error, event }) => {
  const id = crypto.randomUUID();
  console.error(`Error ${id}:`, error);
  return { message: 'An error occurred', id };
};
```

`handleError` only catches *unexpected* errors, not errors thrown with `error()`.

## Locals Type Safety

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user: { id: string; email: string } | null;
    }
    interface PageData {
      user?: { id: string; email: string };
    }
  }
}
export {};
```

## Dynamic API Routes

```ts
// src/routes/api/posts/[id]/+server.ts
export const GET: RequestHandler = async ({ params }) => {
  const post = await db.posts.findUnique({ where: { id: params.id } });
  if (!post) error(404, 'Post not found');
  return json(post);
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
  if (!locals.user) error(401);
  await db.posts.delete({ where: { id: params.id } });
  return new Response(null, { status: 204 });
};
```

## Streaming with Deferred Data

```ts
// +page.server.ts
export const load = async () => {
  return {
    user: await getUser(),                 // Critical: blocks render
    recommendations: getRecommendations()  // Non-critical: streams (no await)
  };
};
```

```svelte
<h1>Welcome, {data.user.name}</h1>

{#await data.recommendations}
  <p>Loading recommendations...</p>
{:then recs}
  {#each recs as rec}
    <div>{rec.title}</div>
  {/each}
{/await}
```

## Common Antipatterns

**Don't use load for route protection — use hooks:**
```ts
// WRONG: Load can run on client
export const load = async ({ locals }) => {
  if (!locals.user) redirect(303, '/login');
};

// CORRECT: Use hooks for auth
export const handle: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith('/admin') && !event.locals.user?.isAdmin) {
    return new Response('Forbidden', { status: 403 });
  }
  return resolve(event);
};
```

**Don't return excess data from load:**
```ts
// WRONG: Entire user record (includes password hash, etc.)
return { user: await db.users.findUnique({ where: { id } }) };

// CORRECT: Select needed fields
const user = await db.users.findUnique({ where: { id } });
return { user: { id: user.id, name: user.name } };
```

## Shallow Routing

Update URL/state without full navigation using `pushState`/`replaceState` from `$app/navigation`:

```ts
import { pushState, replaceState } from '$app/navigation';

// Push new state (adds to history)
pushState('/items/1', { selected: item });

// Replace current state (no history entry)
replaceState('', { modal: 'open' });
```

Access in components via `page.state`:

```svelte
<script>
  import { page } from '$app/state';
</script>

{#if page.state.modal === 'open'}
  <Modal onclose={() => history.back()} />
{/if}
```

Useful for modals, tabs, filters — URL-reflected state that doesn't need a full page load.
