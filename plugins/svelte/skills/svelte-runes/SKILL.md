---
name: Svelte 5 Runes
description: Deep patterns and best practices for Svelte 5's reactivity system. Use when working with $state, $derived, $effect, $props, $bindable, $inspect, or when users ask about Svelte 5 reactivity, state management, reactive declarations, or migrating from Svelte 4 reactive statements ($:).
---

# Svelte 5 Runes

Svelte 5 introduces runes—compiler-driven reactivity primitives that replace Svelte 4's implicit reactivity. Runes provide fine-grained, predictable reactivity that works in `.svelte` and `.svelte.ts` files.

## Core Runes

### $state - Reactive State

Declare reactive state that triggers updates when changed:

```svelte
<script>
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });
</script>

<button onclick={() => count++}>{count}</button>
```

**Key behaviors:**
- Primitives are reactive by value
- Objects and arrays become deeply reactive proxies
- Class instances are NOT made reactive—define `$state` fields inside the class instead

**Antipattern - wrapping class instances:**
```ts
// WRONG: Has no effect
let instance = $state(new MyClass());

// CORRECT: Define $state inside the class
class MyClass {
  value = $state(0);
}
```

### $derived - Computed Values

Create memoized computations that auto-update:

```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
  let expensive = $derived.by(() => {
    // Complex computation
    return heavyCalculation(count);
  });
</script>
```

**Rules:**
- Expression must be pure—no side effects
- Cannot mutate `$state` inside `$derived` (causes infinite loop)
- Only recalculates when dependencies change
- Use `$derived.by()` for multi-statement computations

**Antipattern - side effects in derived:**
```ts
// WRONG: Causes infinite loop
let computed = $derived(() => { count++; return count * 2 });

// CORRECT: Keep derived pure
let computed = $derived(count * 2);
```

### $effect - Side Effects

Run code in response to state changes:

```svelte
<script>
  let count = $state(0);

  $effect(() => {
    console.log('Count changed:', count);

    // Return cleanup function
    return () => {
      console.log('Cleanup before next run or unmount');
    };
  });
</script>
```

**When to use:**
- DOM manipulation
- External subscriptions
- Logging/analytics
- Browser API interactions

**Always return cleanup** for intervals, listeners, subscriptions:

```ts
$effect(() => {
  const id = setInterval(() => tick(), 1000);
  return () => clearInterval(id);
});
```

**Antipattern - reading and writing same state:**
```ts
// WRONG: Infinite loop
$effect(() => { count += 1; });

// CORRECT: Use event handlers or separate the logic
```

### $effect.pre - Before DOM Updates

Runs before DOM updates (replaces `beforeUpdate`):

```svelte
<script>
  let messages = $state([]);
  let container;

  $effect.pre(() => {
    // Capture scroll position before DOM update
    const wasAtBottom = container.scrollTop + container.clientHeight >= container.scrollHeight;
    return () => {
      if (wasAtBottom) container.scrollTop = container.scrollHeight;
    };
  });
</script>
```

### $props - Component Props

Declare component props with destructuring:

```svelte
<script>
  let { name, age = 18, onclick } = $props();
</script>

<button {onclick}>{name} ({age})</button>
```

**With TypeScript:**
```svelte
<script lang="ts">
  interface Props {
    name: string;
    age?: number;
    onclick?: () => void;
  }
  let { name, age = 18, onclick }: Props = $props();
</script>
```

**Rest props pattern:**
```svelte
<script>
  let { class: className, ...rest } = $props();
</script>

<div class={className} {...rest} />
```

### $bindable - Two-way Binding Props

Allow parent components to bind to a prop:

```svelte
<!-- Child.svelte -->
<script>
  let { value = $bindable() } = $props();
</script>

<input bind:value />

<!-- Parent.svelte -->
<script>
  let text = $state('');
</script>

<Child bind:value={text} />
```

### $inspect - Development Debugging

Log state changes during development:

```svelte
<script>
  let count = $state(0);

  $inspect(count); // Logs on every change

  // Custom handler
  $inspect(count).with((type, value) => {
    if (type === 'update') debugger;
  });
</script>
```

**Note:** `$inspect` is stripped in production builds.

## Runes in .svelte.ts Files

Use runes outside components in `.svelte.ts` files:

```ts
// counter.svelte.ts
export function createCounter(initial = 0) {
  let count = $state(initial);

  return {
    get count() { return count },
    increment: () => count++,
    decrement: () => count--
  };
}
```

**Important:** Only rename files to `.svelte.ts` when they directly declare runes. Files importing rune-using functions stay as `.ts`.

## Common Patterns

### Reactive Class

```ts
// todo.svelte.ts
export class Todo {
  text = $state('');
  done = $state(false);

  constructor(text: string) {
    this.text = text;
  }

  toggle() {
    this.done = !this.done;
  }
}
```

### Derived from Props

```svelte
<script>
  let { items } = $props();
  let total = $derived(items.reduce((sum, i) => sum + i.price, 0));
</script>
```

### Effect with Dependencies

```svelte
<script>
  let query = $state('');
  let results = $state([]);

  $effect(() => {
    const controller = new AbortController();

    fetch(`/api/search?q=${query}`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => results = data);

    return () => controller.abort();
  });
</script>
```

## Critical Rules

1. **Runes are top-level only** - Cannot use inside functions or conditionals
2. **$effect doesn't run during SSR** - Use load functions for server data
3. **Global $state is shared across requests in SSR** - Avoid global mutable state on server
4. **$derived tracks at runtime** - Dependencies detected when code runs, not at compile time
5. **Always cleanup effects** - Return cleanup functions for any resources

## Svelte 4 Migration

| Svelte 4 | Svelte 5 |
|----------|----------|
| `let count = 0` (reactive) | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { console.log(count) }` | `$effect(() => { console.log(count) })` |
| `export let name` | `let { name } = $props()` |
| `on:click={handler}` | `onclick={handler}` |
