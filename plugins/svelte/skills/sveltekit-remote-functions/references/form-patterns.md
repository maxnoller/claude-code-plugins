# Remote Function Form Patterns

## Field API

### Field Methods

```svelte
<script>
  import { createPost } from '$lib/posts.remote';
</script>

<form {...createPost}>
  <!-- Spread field props with type -->
  <input {...createPost.fields.title.as('text')} />
  <input {...createPost.fields.email.as('email')} />
  <input {...createPost.fields.age.as('number')} />
  <input {...createPost.fields.avatar.as('file')} />
  <textarea {...createPost.fields.content.as('text')}></textarea>
  <select {...createPost.fields.category.as('select')}>
    <option value="news">News</option>
    <option value="blog">Blog</option>
  </select>

  <!-- Radio buttons -->
  <label>
    <input {...createPost.fields.visibility.as('radio', 'public')} /> Public
  </label>
  <label>
    <input {...createPost.fields.visibility.as('radio', 'private')} /> Private
  </label>

  <!-- Checkboxes -->
  <label>
    <input {...createPost.fields.tags.as('checkbox', 'svelte')} /> Svelte
  </label>
  <label>
    <input {...createPost.fields.tags.as('checkbox', 'kit')} /> SvelteKit
  </label>
</form>
```

### Reading and Setting Values

```ts
// Single field
createPost.fields.title.value()        // current value
createPost.fields.title.set('New')     // update value

// All fields
createPost.fields.value()              // { title: '...', content: '...' }
createPost.fields.set({ title: 'X' }) // update multiple

// Validation issues
createPost.fields.title.issues()       // [{ message: 'Required' }]
createPost.fields.allIssues()          // all field issues
```

## Validation

### Client-Side Preflight

Validate before submitting to server:

```ts
// Validate only touched fields
createPost.validate();

// Validate all fields
createPost.validate({ includeUntouched: true });

// Preflight with custom schema
createPost.preflight(v.object({
  title: v.pipe(v.string(), v.minLength(5))
}));
```

### Imperative Server Validation with invalid()

For validation that requires server state (uniqueness checks, stock levels):

```ts
import { form, invalid } from '$app/server';

export const buyHotcakes = form(
  v.object({ qty: v.pipe(v.number(), v.minValue(1)) }),
  async (data, issue) => {
    try {
      await db.buy(data.qty);
    } catch (e) {
      if (e.code === 'OUT_OF_STOCK') {
        invalid(issue.qty("we don't have enough hotcakes"));
      }
    }
  }
);
```

The `issue` parameter is a proxy — `issue.fieldName(message)` creates a validation error for that field.

## Custom Submission with enhance()

Override default form submission behavior:

```svelte
<form {...createPost.enhance(async ({ form, data, submit }) => {
  try {
    const result = await submit();
    form.reset();
    showToast('Published!');
  } catch (error) {
    showToast('Failed to publish');
  }
})}>
  <!-- fields -->
</form>
```

### Single-Flight Mutations via enhance

Piggyback data refresh on the submission response:

```svelte
<form {...createPost.enhance(async ({ submit }) => {
  // Refresh related query after submit
  await submit().updates(getPosts());

  // Or with optimistic update
  await submit().updates(
    getPosts().withOverride((posts) => [newPost, ...posts])
  );
})}>
```

## Multiple Form Instances

Use `form.for(id)` to create isolated instances (e.g., inline editing):

```svelte
{#each todos as todo}
  {@const modify = modifyTodo.for(todo.id)}
  <form {...modify}>
    <input {...modify.fields.text.as('text')} />
    <button disabled={!!modify.pending}>Save</button>
  </form>
{/each}
```

## Multiple Submit Buttons

Use `.as('submit', value)` for different actions:

```svelte
<form {...loginOrRegister}>
  <input {...loginOrRegister.fields.email.as('email')} />
  <input {...loginOrRegister.fields._password.as('password')} />

  <button {...loginOrRegister.fields.action.as('submit', 'login')}>Login</button>
  <button {...loginOrRegister.fields.action.as('submit', 'register')}>Register</button>
</form>
```

Handle in the server function:

```ts
export const loginOrRegister = form(
  v.object({
    email: v.pipe(v.string(), v.email()),
    _password: v.pipe(v.string(), v.minLength(8)),
    action: v.picklist(['login', 'register'])
  }),
  async ({ email, _password, action }) => {
    if (action === 'login') { /* ... */ }
    else { /* ... */ }
  }
);
```

## File Uploads

Streamable as of SvelteKit 2.49:

```ts
export const uploadAvatar = form(
  v.object({
    avatar: v.instance(File),
    caption: v.optional(v.string())
  }),
  async ({ avatar, caption }) => {
    const buffer = await avatar.arrayBuffer();
    await storage.upload(`avatars/${avatar.name}`, buffer);
    return { url: `/avatars/${avatar.name}` };
  }
);
```

```svelte
<form {...uploadAvatar}>
  <input {...uploadAvatar.fields.avatar.as('file')} accept="image/*" />
  <input {...uploadAvatar.fields.caption.as('text')} />
  <button>Upload</button>
</form>
```

## Form Result

Access the return value after submission:

```svelte
{#if createPost.result}
  <p>Post created: {createPost.result.slug}</p>
{/if}

{#if createPost.pending}
  <p>Submitting...</p>
{/if}
```

## Sensitive Fields

Prefix with underscore to prevent the value from being sent back to the client after submission:

```ts
v.object({
  email: v.string(),
  _password: v.string(),  // not repopulated on validation failure
  _secret: v.string()     // not repopulated
})
```
