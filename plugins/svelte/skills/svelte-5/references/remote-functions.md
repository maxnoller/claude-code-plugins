# Remote Functions — Full Reference

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

## Form Handling with Zod Validation

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

### Form State Management in Components

```svelte
<script>
  import { submitContact } from '$lib/contact.remote';

  let form = $state({ name: '', email: '', message: '' });
  let errors = $state<Record<string, string[]>>({});
  let submitting = $state(false);

  async function handleSubmit(e: Event) {
    e.preventDefault();
    submitting = true;
    errors = {};

    const formData = new FormData(e.target as HTMLFormElement);
    const result = await submitContact.call(formData);

    if (result?.errors) errors = result.errors;
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

## Batch Pattern

Batch multiple queries into a single HTTP request (SvelteKit 2.38+):

```ts
// src/lib/data.remote.ts
import { query } from '$app/server';

export const getUserByIdBatched = query.batch(
  async (ids: string[]) => {
    const users = await db.users.findMany({ where: { id: { in: ids } } });
    return (id: string) => users.find(u => u.id === id);
  }
);
```

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

1. **Never put `.remote.ts` in `src/lib/server/`** — it won't work
2. **Always validate on server** — client can be bypassed
3. **Return serializable data** — no functions, classes, or circular refs
4. **Handle errors gracefully** — use `fail()` for expected errors
5. **Consider caching** — remote functions don't cache by default
