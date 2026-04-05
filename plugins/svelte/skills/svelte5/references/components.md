# Advanced Component Patterns

## Snippets with Parameters

Pass data to snippets (like slot props):

```svelte
<!-- List.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props<T> {
    items: T[];
    row: Snippet<[item: T, index: number]>;
    empty?: Snippet;
  }

  let { items, row, empty }: Props<any> = $props();
</script>

{#if items.length === 0}
  {#if empty}
    {@render empty()}
  {:else}
    <p>No items</p>
  {/if}
{:else}
  <ul>
    {#each items as item, index (item.id)}
      <li>{@render row(item, index)}</li>
    {/each}
  </ul>
{/if}
```

Usage:

```svelte
<List items={users}>
  {#snippet row(user, index)}
    <span>{index + 1}. {user.name}</span>
  {/snippet}

  {#snippet empty()}
    <p>No users found</p>
  {/snippet}
</List>
```

## Compound Components with createContext (5.40+)

`createContext` is the recommended way to share state between related components. It returns a type-safe `[get, set]` tuple with automatic Symbol keys — replacing manual `setContext`/`getContext` with Symbol keys.

### Accordion

```svelte
<!-- Accordion.svelte -->
<script lang="ts" module>
  import { createContext } from 'svelte';

  interface AccordionContext {
    toggle: (id: string) => void;
    isOpen: (id: string) => boolean;
  }

  const [getAccordionCtx, setAccordionCtx] = createContext<AccordionContext>();
  export { getAccordionCtx };
</script>

<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    multiple?: boolean;
    children: Snippet;
  }

  let { multiple = false, children }: Props = $props();
  let activeItems = $state(new Set<string>());

  function toggle(id: string) {
    if (activeItems.has(id)) {
      activeItems.delete(id);
      activeItems = activeItems;
    } else {
      if (!multiple) activeItems.clear();
      activeItems.add(id);
      activeItems = activeItems;
    }
  }

  function isOpen(id: string) {
    return activeItems.has(id);
  }

  setAccordionCtx({ toggle, isOpen });
</script>

<div class="accordion">
  {@render children()}
</div>
```

```svelte
<!-- AccordionItem.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { getAccordionCtx } from './Accordion.svelte';

  interface Props {
    id: string;
    header: Snippet;
    children: Snippet;
  }

  let { id, header, children }: Props = $props();
  const { toggle, isOpen } = getAccordionCtx();

  let open = $derived(isOpen(id));
</script>

<div class="accordion-item">
  <button
    class="accordion-header"
    onclick={() => toggle(id)}
    aria-expanded={open}
  >
    {@render header()}
  </button>

  {#if open}
    <div class="accordion-content">
      {@render children()}
    </div>
  {/if}
</div>
```

> **Note:** The old `setContext`/`getContext` with manual Symbol keys still works but `createContext` is preferred for new code — it's simpler, type-safe, and less boilerplate.

## Polymorphic Components

Components that render as different elements:

```svelte
<!-- Button.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { HTMLButtonAttributes, HTMLAnchorAttributes } from 'svelte/elements';

  type Props = {
    children: Snippet;
    variant?: 'primary' | 'secondary';
  } & (
    | ({ as?: 'button' } & HTMLButtonAttributes)
    | ({ as: 'a' } & HTMLAnchorAttributes)
  );

  let { children, variant = 'primary', as = 'button', ...rest }: Props = $props();
</script>

<svelte:element this={as} class="btn btn-{variant}" {...rest}>
  {@render children()}
</svelte:element>
```

Usage:

```svelte
<Button>Click me</Button>
<Button as="a" href="/about">Go to About</Button>
```

## Forwarding Props

### Rest Props Pattern

```svelte
<script lang="ts">
  import type { HTMLAttributes } from 'svelte/elements';

  interface Props extends HTMLAttributes<HTMLDivElement> {
    title: string;
  }

  let { title, class: className, ...rest }: Props = $props();
</script>

<div class="card {className}" {...rest}>
  <h2>{title}</h2>
</div>
```

## Controlled vs Uncontrolled

```svelte
<!-- Uncontrolled: Component manages state -->
<script>
  let { defaultValue = '' } = $props();
  let value = $state(defaultValue);
</script>
<input bind:value />

<!-- Controlled: Parent manages state -->
<script>
  let { value = $bindable() } = $props();
</script>
<input bind:value />
```

### Hybrid Controlled

```svelte
<script lang="ts">
  interface Props {
    value?: string;
    defaultValue?: string;
    onchange?: (value: string) => void;
  }

  let { value: controlledValue, defaultValue = '', onchange }: Props = $props();
  let internalValue = $state(defaultValue);
  let value = $derived(controlledValue ?? internalValue);

  function handleChange(e: Event) {
    const newValue = (e.target as HTMLInputElement).value;
    internalValue = newValue;
    onchange?.(newValue);
  }
</script>

<input {value} onchange={handleChange} />
```

## Conditional Rendering Patterns

### Show/Hide vs Mount/Unmount

```svelte
<!-- Mount/unmount: Component recreated -->
{#if visible}
  <HeavyComponent />
{/if}

<!-- Show/hide: Component stays mounted -->
<div class:hidden={!visible}>
  <HeavyComponent />
</div>
```

### Keyed Blocks — Force Recreation

```svelte
{#key userId}
  <UserProfile id={userId} />
{/key}
```

## Best Practices

1. **Use snippets over slots** — More flexible, typed, work outside components
2. **Type your props** — Use TypeScript interfaces for all props
3. **Make children optional safely** — Always use `{@render children?.()}`
4. **Prefer composition** — Small, focused components over monolithic ones
5. **Use context sparingly** — Only for deeply nested state sharing
