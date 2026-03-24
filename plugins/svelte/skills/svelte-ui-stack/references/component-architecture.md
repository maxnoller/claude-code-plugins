# Component Architecture

## File Types

| Extension | When to use | Example |
|---|---|---|
| `.svelte` | UI components | `Button.svelte` |
| `.svelte.ts` | Modules that **directly declare runes** (`$state`, `$derived`, `$effect`) | `use-pagination.svelte.ts` |
| `.ts` | Everything else (types, utils, API clients, constants, schemas) | `types.ts` |

Only use `.svelte.ts` when the file directly declares runes. Files that merely import rune-using functions stay `.ts`.

## Project Structure

```
src/
├── lib/
│   ├── components/ui/       # shadcn-svelte primitives
│   ├── components/           # Shared app components
│   ├── hooks/               # Reusable reactive logic (.svelte.ts)
│   ├── server/              # Server-only code
│   └── utils/               # Pure utilities
├── routes/
│   ├── dashboard/
│   │   ├── +page.svelte
│   │   ├── +page.server.ts
│   │   └── DashboardChart.svelte  # Route-colocated component
```

**Colocate first, extract when shared.** Keep components next to the route that uses them. Move to `$lib/` only when genuinely used by multiple routes.

## State Management

### The Svelte Philosophy

State lives in components. The `.svelte` file format exists so state, logic, and markup colocate — that colocation is the feature. A 350-line component with 200 lines of script and 150 lines of template is normal and healthy in Svelte.

### When to Extract State to .svelte.ts

Use `.svelte.ts` factory functions for **reusable reactive logic** — patterns used across multiple components:

```ts
// use-pagination.svelte.ts — reusable across many list views
export function usePagination(getTotal: () => number, pageSize = 20) {
  let page = $state(0);
  let totalPages = $derived(Math.ceil(getTotal() / pageSize));
  let hasNext = $derived(page < totalPages - 1);

  return {
    get page() { return page; },
    get totalPages() { return totalPages; },
    get hasNext() { return hasNext; },
    next() { if (hasNext) page++; },
    prev() { if (page > 0) page--; },
  };
}
```

Pass reactive values as getter functions (`() => count`) for primitives, since reactivity persists through property access. Object `$state` proxies can be passed directly because property access on proxies is tracked.

**Don't destructure the return value** — `const { page } = usePagination()` breaks reactivity. Access through the object.

### When NOT to Extract

Don't extract page-local state into a factory just to make the component shorter. If the state is only used by one component, it belongs in that component. A large `<script>` block is fine — extract **visual sub-components** instead.

### State Patterns Quick Reference

| Scenario | Approach |
|---|---|
| Component-local state | `$state` / `$derived` inline in the component |
| Reusable reactive logic | Factory function in `.svelte.ts` |
| Complex domain model with private state | Reactive class with `$state` fields |
| Global app config | Exported `$state` object in `.svelte.ts` |
| Per-user state in SSR | `createContext` (Svelte 5.40+) |

### Reactive Classes

For domain models that benefit from encapsulation:

```ts
export class CanvasState {
  width = $state(800);
  height = $state(600);
  area = $derived(this.width * this.height);
  #history: string[] = [];  // Non-reactive private field

  resize(w: number, h: number) {
    this.#history.push(`${this.width}x${this.height}`);
    this.width = w;
    this.height = h;
  }
}
```

Class `$state` fields become getter/setter pairs on the prototype. `$state.snapshot()` cannot access private fields.

### Context API (SSR-safe)

```ts
import { createContext } from 'svelte';
export const [getUser, setUser] = createContext<User>();
```

Use for subtree-scoped state or any user-specific data in SSR apps. Never use module-level `$state` for user-specific data — it leaks between requests.

## Component Extraction

When a component grows unwieldy, extract **visual sub-components with narrow props**:

```svelte
<!-- +page.svelte stays the owner of all state -->
<script lang="ts">
  let services = $state(data.services);
  let searchTerm = $state('');
  let deleteTarget = $state<string | null>(null);
  // ... all state lives here
</script>

<!-- Sub-components receive only what they need -->
<FilterBar bind:searchTerm {statusOptions} />
<ServiceGrid {filteredServices} onSelect={(s) => goto(s.href)} />
<DeleteConfirm
  bind:open={deleteTarget !== null}
  serviceName={deleteTarget}
  onConfirm={() => handleDelete(deleteTarget)}
/>
```

Each sub-component has a clear, narrow interface. The page component owns the state and coordinates between children.

### Extraction Guidelines

Extract a template block into a sub-component when it:
- Is reused in multiple places
- Has its own imports (icons, libraries, UI primitives)
- Represents a self-contained concern (a filter bar, a dialog, an empty state)

Keep inline when it's just a simple conditional or loop body with no independent logic.

## Extending shadcn-svelte Components

Add variants directly in the component file:

```svelte
<script lang="ts" module>
  export const buttonVariants = tv({
    variants: {
      variant: {
        default: "...",
        brand: "bg-brand text-brand-foreground hover:bg-brand/90",  // custom
      },
    },
  });
</script>
```

Wrap with additional behavior by composing:

```svelte
<script lang="ts">
  import { Button } from "$lib/components/ui/button/index.js";
  import * as Dialog from "$lib/components/ui/dialog/index.js";

  let { children, onConfirm, message = "Are you sure?", ...rest } = $props();
  let open = $state(false);
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    {#snippet child({ props })}
      <Button {...props} {...rest}>{@render children?.()}</Button>
    {/snippet}
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header><Dialog.Title>Confirm</Dialog.Title></Dialog.Header>
    <Dialog.Footer>
      <Button variant="outline" onclick={() => open = false}>Cancel</Button>
      <Button onclick={() => { onConfirm(); open = false; }}>Confirm</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
```
