---
name: Svelte Component Patterns
description: Advanced component patterns for Svelte 5 including snippets, slots, headless components, compound components, and render delegation. Use when users ask about component architecture, reusable components, snippets vs slots, compound components, headless UI, render props, component composition, or building component libraries in Svelte 5.
---

# Svelte 5 Component Patterns

Svelte 5 introduces snippets and changes how components compose. Master these patterns for flexible, reusable component design.

## Snippets (Replacing Slots)

### Basic Snippet

Snippets are reusable template blocks:

```svelte
<script>
  import Card from './Card.svelte';
</script>

<Card>
  {#snippet header()}
    <h2>Card Title</h2>
  {/snippet}

  {#snippet footer()}
    <button>Action</button>
  {/snippet}

  <p>Card content goes here.</p>
</Card>
```

```svelte
<!-- Card.svelte -->
<script>
  import type { Snippet } from 'svelte';

  interface Props {
    header?: Snippet;
    footer?: Snippet;
    children: Snippet;
  }

  let { header, footer, children }: Props = $props();
</script>

<div class="card">
  {#if header}
    <div class="card-header">
      {@render header()}
    </div>
  {/if}

  <div class="card-body">
    {@render children()}
  </div>

  {#if footer}
    <div class="card-footer">
      {@render footer()}
    </div>
  {/if}
</div>
```

### Snippets with Parameters

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

### Optional Snippets

Always use optional chaining for optional snippets:

```svelte
<script>
  let { icon, children } = $props();
</script>

<!-- WRONG: Errors if icon is undefined -->
{@render icon()}

<!-- CORRECT: Safe rendering -->
{@render icon?.()}

<!-- Or with fallback -->
{#if icon}
  {@render icon()}
{:else}
  <DefaultIcon />
{/if}
```

## Children Prop

The `children` snippet captures non-snippet content:

```svelte
<!-- Button.svelte -->
<script>
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
    variant?: 'primary' | 'secondary';
  }

  let { children, variant = 'primary' }: Props = $props();
</script>

<button class={variant}>
  {@render children()}
</button>
```

```svelte
<Button variant="primary">
  Click me
</Button>
```

## Headless Components

Components that provide behavior without UI:

```svelte
<!-- Tabs.svelte (headless) -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Tab {
    id: string;
    label: string;
  }

  interface Props {
    tabs: Tab[];
    defaultTab?: string;
    children: Snippet<[{
      activeTab: string;
      setActiveTab: (id: string) => void;
      isActive: (id: string) => boolean;
    }]>;
  }

  let { tabs, defaultTab, children }: Props = $props();
  let activeTab = $state(defaultTab ?? tabs[0]?.id);

  function setActiveTab(id: string) {
    activeTab = id;
  }

  function isActive(id: string) {
    return activeTab === id;
  }
</script>

{@render children({ activeTab, setActiveTab, isActive })}
```

Usage with custom UI:

```svelte
<Tabs tabs={[
  { id: 'tab1', label: 'First' },
  { id: 'tab2', label: 'Second' }
]}>
  {#snippet children({ activeTab, setActiveTab, isActive })}
    <div class="my-custom-tabs">
      <div class="tab-list" role="tablist">
        {#each tabs as tab}
          <button
            role="tab"
            aria-selected={isActive(tab.id)}
            onclick={() => setActiveTab(tab.id)}
            class:active={isActive(tab.id)}
          >
            {tab.label}
          </button>
        {/each}
      </div>

      <div class="tab-panels">
        {#if activeTab === 'tab1'}
          <div>First panel content</div>
        {:else if activeTab === 'tab2'}
          <div>Second panel content</div>
        {/if}
      </div>
    </div>
  {/snippet}
</Tabs>
```

## Compound Components

Related components that share state:

```svelte
<!-- Accordion.svelte -->
<script lang="ts" module>
  import { getContext, setContext } from 'svelte';

  const ACCORDION_KEY = Symbol('accordion');

  interface AccordionContext {
    activeItems: Set<string>;
    toggle: (id: string) => void;
    isOpen: (id: string) => boolean;
  }

  export function getAccordionContext(): AccordionContext {
    return getContext(ACCORDION_KEY);
  }
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
      activeItems = activeItems; // Trigger reactivity
    } else {
      if (!multiple) {
        activeItems.clear();
      }
      activeItems.add(id);
      activeItems = activeItems;
    }
  }

  function isOpen(id: string) {
    return activeItems.has(id);
  }

  setContext(ACCORDION_KEY, {
    get activeItems() { return activeItems },
    toggle,
    isOpen
  });
</script>

<div class="accordion">
  {@render children()}
</div>
```

```svelte
<!-- AccordionItem.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { getAccordionContext } from './Accordion.svelte';

  interface Props {
    id: string;
    header: Snippet;
    children: Snippet;
  }

  let { id, header, children }: Props = $props();
  const { toggle, isOpen } = getAccordionContext();

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

Usage:

```svelte
<Accordion>
  <AccordionItem id="item1">
    {#snippet header()}Section 1{/snippet}
    Content for section 1
  </AccordionItem>

  <AccordionItem id="item2">
    {#snippet header()}Section 2{/snippet}
    Content for section 2
  </AccordionItem>
</Accordion>
```

## Polymorphic Components

Components that render as different elements:

```svelte
<!-- Button.svelte -->
<script lang="ts">
  import type { Snippet, Component } from 'svelte';
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

### Event Forwarding

```svelte
<script lang="ts">
  interface Props {
    onclick?: (e: MouseEvent) => void;
  }

  let { onclick, ...rest }: Props = $props();
</script>

<button {onclick} {...rest}>
  <slot />
</button>
```

## Conditional Rendering Patterns

### Show/Hide vs Mount/Unmount

```svelte
<script>
  let visible = $state(true);
</script>

<!-- Mount/unmount: Component recreated -->
{#if visible}
  <HeavyComponent />
{/if}

<!-- Show/hide: Component stays mounted -->
<div class:hidden={!visible}>
  <HeavyComponent />
</div>

<style>
  .hidden { display: none; }
</style>
```

### Keyed Blocks

Force component recreation:

```svelte
{#key userId}
  <UserProfile id={userId} />
{/key}
```

## Component State Patterns

### Controlled vs Uncontrolled

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

  // Use controlled value if provided, otherwise manage internally
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

## Best Practices

1. **Use snippets over slots** - More flexible, typed, work outside components
2. **Type your props** - Use TypeScript interfaces for all props
3. **Make children optional safely** - Always use `{@render children?.()}`
4. **Prefer composition** - Small, focused components over monolithic ones
5. **Use context sparingly** - Only for deeply nested state sharing
6. **Document snippet parameters** - Include types and examples
