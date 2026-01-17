# Rune Gotchas and Common Mistakes

## $state Gotchas

### Wrapping class instances has no effect

```ts
// WRONG: $state doesn't make class instances reactive
let user = $state(new User());

// CORRECT: Define $state inside the class
class User {
  name = $state('');
  email = $state('');
}
```

### Reassignment vs mutation

```ts
let items = $state([1, 2, 3]);

// These both trigger reactivity:
items.push(4);        // Mutation - works because of Proxy
items = [...items, 4]; // Reassignment - also works
```

## $derived Gotchas

### Never mutate state inside $derived

```ts
// WRONG: Causes infinite loop
let doubled = $derived(() => {
  count++; // NEVER do this!
  return count * 2;
});

// CORRECT: Keep derived pure
let doubled = $derived(count * 2);
```

### Dependencies are tracked at runtime

```ts
let includeBonus = $state(false);
let salary = $state(50000);
let bonus = $state(10000);

// Only tracks `salary` when includeBonus is false
let total = $derived(
  includeBonus ? salary + bonus : salary
);
```

## $effect Gotchas

### Reading and writing same state = infinite loop

```ts
// WRONG: Infinite loop
$effect(() => {
  count = count + 1;
});

// CORRECT: Use separate state or event handlers
```

### Always return cleanup for resources

```ts
// WRONG: Memory leak
$effect(() => {
  const id = setInterval(tick, 1000);
});

// CORRECT: Cleanup on re-run or unmount
$effect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
});
```

### Don't use $effect when $derived works

```ts
// WRONG: Using effect for computation
let doubled;
$effect(() => {
  doubled = count * 2;
});

// CORRECT: Use derived
let doubled = $derived(count * 2);
```

## $props Gotchas

### Props are not reactive by default in functions

```ts
let { value } = $props();

function logValue() {
  // This captures the value at function creation time
  console.log(value); // Might be stale!
}

// Use getter or pass explicitly
function logValue(currentValue) {
  console.log(currentValue);
}
```

## Scope Rules

### Runes must be at top level

```ts
// WRONG: Runes inside functions
function createCounter() {
  let count = $state(0); // Error!
}

// CORRECT: Use .svelte.ts files for runes outside components
// counter.svelte.ts
export function createCounter() {
  let count = $state(0);
  return { get count() { return count } };
}
```

### Runes don't work in regular .ts files

Only these files support runes:
- `.svelte` - Components
- `.svelte.ts` / `.svelte.js` - Modules with runes
