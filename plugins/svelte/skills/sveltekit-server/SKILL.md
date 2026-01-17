---
name: SvelteKit Server Patterns
description: Server-side SvelteKit patterns including load functions, form actions, hooks, and API routes. Use when working with +page.server.ts, +layout.server.ts, +server.ts, hooks.server.ts, load functions, form actions, handle/handleFetch/handleError hooks, or when users ask about server-side data loading, authentication, authorization, or API endpoints in SvelteKit.
---

# SvelteKit Server Patterns

SvelteKit provides multiple server-side patterns for data loading, mutations, and request handling.

## Load Functions

### Page Server Load (+page.server.ts)

Server-only data loading—code never reaches the client:

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, locals }) => {
  if (!locals.user) {
    error(401, 'Unauthorized');
  }

  const stats = await db.stats.findUnique({
    where: { userId: locals.user.id }
  });

  return {
    stats,
    user: locals.user
  };
};
```

### Layout Server Load (+layout.server.ts)

Share data across child routes:

```ts
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  return {
    user: locals.user
  };
};
```

### Universal Load (+page.ts)

Runs on both server and client—avoid secrets:

```ts
// src/routes/posts/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  // Use SvelteKit's fetch for cookie forwarding
  const posts = await fetch('/api/posts').then(r => r.json());
  return { posts };
};
```

**When to use which:**
| Use case | File |
|----------|------|
| Database queries | `+page.server.ts` |
| API keys/secrets | `+page.server.ts` |
| Shared auth state | `+layout.server.ts` |
| Client-side caching | `+page.ts` |
| Public API calls | `+page.ts` |

### Parallel Loading

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

### Using Parent Data

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

## Form Actions

Handle form submissions with progressive enhancement:

```ts
// src/routes/login/+page.server.ts
import type { Actions, PageServerLoad } from './$types';
import { fail, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.user) redirect(303, '/dashboard');
};

export const actions: Actions = {
  default: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    const password = data.get('password') as string;

    // Validate
    if (!email) {
      return fail(400, { email, missing: true });
    }

    // Authenticate
    const user = await authenticate(email, password);
    if (!user) {
      return fail(400, { email, incorrect: true });
    }

    // Set session
    cookies.set('session', user.sessionId, { path: '/' });
    redirect(303, '/dashboard');
  }
};
```

### Named Actions

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
<form method="POST" action="?/login">
  <!-- login form -->
</form>

<form method="POST" action="?/register">
  <!-- register form -->
</form>

<form method="POST" action="?/logout">
  <button>Logout</button>
</form>
```

### Progressive Enhancement

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

## API Routes (+server.ts)

Create REST API endpoints:

```ts
// src/routes/api/posts/+server.ts
import type { RequestHandler } from './$types';
import { json, error } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url, locals }) => {
  const limit = Number(url.searchParams.get('limit')) || 10;
  const posts = await db.posts.findMany({ take: limit });
  return json(posts);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) {
    error(401, 'Unauthorized');
  }

  const { title, content } = await request.json();
  const post = await db.posts.create({
    data: { title, content, authorId: locals.user.id }
  });

  return json(post, { status: 201 });
};
```

### Dynamic API Routes

```ts
// src/routes/api/posts/[id]/+server.ts
export const GET: RequestHandler = async ({ params }) => {
  const post = await db.posts.findUnique({
    where: { id: params.id }
  });

  if (!post) error(404, 'Post not found');
  return json(post);
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
  if (!locals.user) error(401);

  await db.posts.delete({ where: { id: params.id } });
  return new Response(null, { status: 204 });
};
```

## Hooks (hooks.server.ts)

### handle - Request Middleware

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  // Before route handling
  const session = event.cookies.get('session');
  if (session) {
    event.locals.user = await getUserFromSession(session);
  }

  // Resolve the request
  const response = await resolve(event);

  // After route handling
  response.headers.set('X-Custom-Header', 'value');

  return response;
};
```

### Sequence Multiple Handles

```ts
import { sequence } from '@sveltejs/kit/hooks';

const auth: Handle = async ({ event, resolve }) => {
  // Auth logic
  return resolve(event);
};

const logger: Handle = async ({ event, resolve }) => {
  console.log(`${event.request.method} ${event.url.pathname}`);
  return resolve(event);
};

export const handle = sequence(auth, logger);
```

### handleFetch - Modify Server Fetches

```ts
export const handleFetch: HandleFetch = async ({ request, fetch }) => {
  // Add auth to internal API calls
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

### handleError - Error Handling

```ts
export const handleError: HandleServerError = async ({ error, event }) => {
  const id = crypto.randomUUID();

  // Log to error tracking service
  console.error(`Error ${id}:`, error);

  // Return safe message to client
  return {
    message: 'An error occurred',
    id
  };
};
```

**Note:** `handleError` only catches *unexpected* errors, not errors thrown with `error()`.

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

## Common Antipatterns

**Don't use load for authorization:**
```ts
// WRONG: Load runs on client too
export const load = async ({ locals }) => {
  if (!locals.user) redirect(303, '/login');
};

// CORRECT: Use hooks for auth
export const handle: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith('/admin')) {
    if (!event.locals.user?.isAdmin) {
      return new Response('Forbidden', { status: 403 });
    }
  }
  return resolve(event);
};
```

**Don't return excess data:**
```ts
// WRONG: Returns entire user record
return { user: await db.users.findUnique({ where: { id } }) };

// CORRECT: Return only needed fields
const user = await db.users.findUnique({ where: { id } });
return { user: { id: user.id, name: user.name } };
```

**Don't forget error boundaries:**
```svelte
<!-- src/routes/+error.svelte -->
<script>
  import { page } from '$app/stores';
</script>

<h1>{$page.status}</h1>
<p>{$page.error?.message}</p>
```
