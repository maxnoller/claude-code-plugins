# Events, Styling, and Patterns

## Event Listeners

Any attribute starting with `on` becomes an event listener. Shorthand and spread are supported:

```svelte
<button onclick={() => count++}>click</button>
<button {onclick}>shorthand</button>
<button {...props}>spread</button>
```

For window/document listeners, use special elements instead of `onMount` or `$effect`:

```svelte
<svelte:window onkeydown={handleKey} />
<svelte:document onvisibilitychange={handleVisibility} />
```

## Each Blocks

Always use keyed each blocks — they enable surgical DOM insertion/removal instead of updating existing elements:

```svelte
{#each items as item (item.id)}
  <Item {item} />
{/each}
```

Never use array indices as keys. Avoid destructuring when mutating items (e.g., use `bind:value={item.count}` with the full `item` reference).

## CSS Custom Properties

Pass JS variables into CSS via the `style:` directive:

```svelte
<div style:--columns={columns}>
  <!-- Uses var(--columns) in <style> -->
</div>
```

## Styling Child Components

Use CSS custom properties to control child styles from parent:

```svelte
<!-- Parent -->
<Child --color="red" />

<!-- Child.svelte -->
<h1>Hello</h1>
<style>
  h1 { color: var(--color); }
</style>
```

When custom properties aren't possible (e.g., library components), use `:global`:

```svelte
<div>
  <LibraryComponent />
</div>
<style>
  div :global {
    h1 { color: red; }
  }
</style>
```

## Class Attributes

Prefer clsx-style arrays/objects in `class` attributes over the `class:` directive:

```svelte
<div class={['card', isActive && 'active', size === 'lg' && 'card-lg']}>
```

## Context Over Module State

Prefer context (`createContext`) over shared module-level state. Module state is shared across all requests during SSR, which can leak data between users. Context scopes state to the component tree:

```ts
// WRONG: Module-level state — shared across SSR requests
let user = $state(null);

// CORRECT: Use context
const [getUser, setUser] = createContext<User>();
```
