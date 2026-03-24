# Component Architecture

## File Types

| Extension | Purpose | Example |
|---|---|---|
| `.svelte` | UI components (HTML + CSS + logic) | `Button.svelte` |
| `.svelte.ts` | Modules that **use runes directly** (`$state`, `$derived`, `$effect`) | `counter.svelte.ts` |
| `.ts` | Regular TypeScript (types, utils, API clients, constants) | `types.ts`, `api.ts` |

**Rule:** Only rename to `.svelte.ts` when the file directly declares runes. Files that import rune-using functions stay `.ts`.

## Project Structure

```
src/
├── lib/
│   ├── components/
│   │   └── ui/              # shadcn-svelte primitives (auto-generated)
│   ├── features/            # Feature modules (shared across routes)
│   │   └── invoice/
│   │       ├── invoice-state.svelte.ts
│   │       ├── invoice-api.ts
│   │       ├── invoice-types.ts
│   │       ├── InvoiceList.svelte
│   │       └── index.ts
│   ├── hooks/               # Reusable reactive logic (.svelte.ts)
│   ├── server/              # Server-only code
│   └── utils/               # Pure utilities (.ts)
├── routes/
│   ├── dashboard/
│   │   ├── +page.svelte
│   │   ├── +page.server.ts
│   │   ├── dashboard-state.svelte.ts   # Route-colocated logic
│   │   └── DashboardChart.svelte       # Route-specific component
```

**Colocate first, extract when shared.** Keep components and logic next to the route that uses them. Move to `$lib/` only when genuinely used by multiple routes.

## State Patterns (Decision Guide)

### 1. Inline State (default)

For simple component-local state, keep it inline:

```svelte
<script lang="ts">
  let count = $state(0);
  let doubled = $derived(count * 2);
</script>
```

Use when: component is under ~200 lines, state is only used here.

### 2. Factory Function ("composable")

The standard pattern for extracting reactive logic. Pass reactive props as **getter functions** so the factory tracks changes (endorsed by Rich Harris as "simple, clear, debuggable, composable"):

```ts
// todo-state.svelte.ts
export function createTodoState(getFilter: () => string) {
  let todos = $state<Todo[]>([]);
  let filtered = $derived(
    getFilter() === 'all' ? todos : todos.filter(t => t.status === getFilter())
  );
  let remaining = $derived(filtered.filter(t => !t.done).length);

  return {
    get todos() { return filtered; },
    get remaining() { return remaining; },
    add(text: string) { todos.push({ text, done: false, status: 'active' }); },
    toggle(i: number) { todos[i].done = !todos[i].done; },
  };
}
```

```svelte
<script lang="ts">
  import { createTodoState } from './todo-state.svelte';
  let filter = $state('all');
  const todos = createTodoState(() => filter);
</script>
```

Use when: logic exceeds ~200 lines, or the same logic pattern is reused across multiple components.

**Getter function rule:** Reactivity persists through property access, not value passing. Use `() => prop` for primitives and props that change by reference. For object `$state` proxies, passing directly works because property access is tracked.

**Always expose state via getters/setters** — never return raw `$state` variables. Destructuring (`const { count } = createCounter()`) breaks reactivity.

### 3. Reactive Class (complex domain)

For domain models with mixed reactive and non-reactive state:

```ts
// canvas-state.svelte.ts
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

Use when: need selective reactivity (only some fields tracked), encapsulation with private fields, or modeling a complex domain entity.

**Gotcha:** `$state()` class fields become getter/setter pairs on the prototype. `$state.snapshot()` cannot access private fields.

### 4. Shared Reactive Object (singleton)

For global app config or feature flags:

```ts
// config.svelte.ts
export const config = $state({ theme: 'dark', locale: 'en' });
```

Use when: truly global, non-user-specific state. **Never for user data in SSR** — shared module state leaks between requests.

### 5. Context API (SSR-safe)

For per-request, per-subtree state. Use `createContext` (Svelte 5.40+):

```ts
// src/lib/context/user.ts
import { createContext } from 'svelte';

interface UserState { name: string; email: string; }
export const [getUser, setUser] = createContext<UserState>();
```

```svelte
<!-- +layout.svelte -->
<script>
  import { setUser } from '$lib/context/user';
  let { data, children } = $props();
  let user = $state(data.user);  // Wrap in $state for reactivity
  setUser(user);
</script>
{@render children()}
```

```svelte
<!-- Any descendant -->
<script>
  import { getUser } from '$lib/context/user';
  const user = getUser();  // Typed, throws if missing
</script>
```

Use when: state scoped to a component subtree, or any user-specific data in SSR apps.

### Decision Matrix

| Scenario | Pattern | File |
|---|---|---|
| Simple component state (<200 lines) | Inline `$state` | `.svelte` |
| Extracted component logic | Factory function | `.svelte.ts` colocated |
| Reusable reactive logic | Factory function | `$lib/hooks/*.svelte.ts` |
| Complex domain model | Reactive class | `.svelte.ts` |
| Global app config (no SSR concern) | Shared `$state` object | `$lib/state/*.svelte.ts` |
| User-specific state (SSR) | `createContext` | `$lib/context/*.ts` |
| Pure utilities, types, constants | Regular exports | `.ts` |

## Feature Folder Pattern

For non-trivial features shared across routes:

```
src/lib/features/invoice/
├── invoice-state.svelte.ts     # Reactive state & business logic
├── invoice-api.ts              # API calls (plain fetch, no runes)
├── invoice-types.ts            # TypeScript interfaces
├── invoice-schema.ts           # Zod/Valibot validation schemas
├── InvoiceList.svelte          # UI component
├── InvoiceDetail.svelte        # UI component
├── InvoiceForm.svelte          # UI component
└── index.ts                    # Barrel export
```

**Naming conventions:**
- State files: `kebab-case.svelte.ts` (e.g., `invoice-state.svelte.ts`)
- Components: `PascalCase.svelte` (e.g., `InvoiceList.svelte`)
- Types/utils: `kebab-case.ts` (e.g., `invoice-types.ts`)

## Extending shadcn-svelte Components

To add a variant to an existing component:

```svelte
<!-- src/lib/components/ui/button/button.svelte -->
<script lang="ts" module>
  export const buttonVariants = tv({
    base: "...",
    variants: {
      variant: {
        default: "...",
        // Add your custom variant:
        brand: "bg-brand text-brand-foreground hover:bg-brand/90",
      },
      size: {
        default: "h-10 px-4",
        // Add your custom size:
        xl: "h-14 px-8 text-lg",
      },
    },
  });
</script>
```

To wrap with additional behavior:

```svelte
<!-- src/lib/components/confirm-button.svelte -->
<script lang="ts">
  import { Button, type ButtonProps } from "$lib/components/ui/button/index.js";
  import * as Dialog from "$lib/components/ui/dialog/index.js";

  let { children, onConfirm, message = "Are you sure?", ...rest }: ButtonProps & {
    onConfirm: () => void;
    message?: string;
  } = $props();

  let open = $state(false);
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    {#snippet child({ props })}
      <Button {...props} {...rest}>{@render children?.()}</Button>
    {/snippet}
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>Confirm</Dialog.Title>
      <Dialog.Description>{message}</Dialog.Description>
    </Dialog.Header>
    <Dialog.Footer>
      <Button variant="outline" onclick={() => open = false}>Cancel</Button>
      <Button onclick={() => { onConfirm(); open = false; }}>Confirm</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
```

## Component Decomposition

When to extract a template block into a sub-component vs. keep inline:

| Extract to sub-component | Keep inline |
|---|---|
| Reused in multiple places | Used only once |
| Has its own imports (icons, libraries) | Pure HTML with parent data |
| Would benefit from testing in isolation | Tightly coupled to surrounding template |
| Self-contained behavior (e.g., a filter bar) | Simple conditional or loop body |
| Exceeds ~100 lines with own state/logic | Presentation only, no state |

**Svelte 5 gives two extraction axes:**
1. **Extract logic** → `.svelte.ts` factory function (keeps template in parent)
2. **Extract template** → sub-component `.svelte` file (moves markup out)

Prefer extracting logic first. Only extract template blocks when they have independent concerns (own imports, own state, or reusability).

## Passing State to Child Components

When extracting sub-components from a page, decide how to pass state:

### Single state object (route-colocated components)

For components colocated with a route that won't be reused elsewhere, passing the full state object is acceptable and avoids prop drilling:

```svelte
<!-- +page.svelte -->
<script>
  const state = createPageState(() => data);
</script>

<PageToolbar {state} />
<PageContent {state} />
<PageDialogs {state} />
```

```svelte
<!-- PageToolbar.svelte -->
<script lang="ts">
  import type { PageState } from './page-state.svelte';
  let { state }: { state: PageState } = $props();
</script>
```

### Individual typed props (reusable components)

For shared/reusable components, prefer explicit props for encapsulation:

```svelte
<ServiceCard
  svc={service}
  status={status}
  onRestart={() => restart(service.id)}
/>
```

### Context (deep hierarchies)

For deeply nested component trees where prop drilling becomes unwieldy, use `createContext` (Svelte 5.40+).

## DOM Refs in Extracted State

When a factory function needs access to DOM elements (e.g., for scroll position, canvas, focus management), use a `$state` ref object:

```ts
// editor-state.svelte.ts
export function createEditorState() {
  let canvasEl = $state<HTMLCanvasElement>();

  $effect(() => {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    // setup...
    return () => { /* cleanup */ };
  });

  return {
    get canvasEl() { return canvasEl; },
    set canvasEl(v) { canvasEl = v; },
    // ...
  };
}
```

```svelte
<canvas bind:this={state.canvasEl}></canvas>
```

The getter/setter pair allows `bind:this` to write the element reference into the state, which the factory's `$effect` can then react to. When the element is destroyed (conditional rendering), `bind:this` sets it to `undefined`, triggering effect cleanup.

## Structuring Large State Objects

When a factory returns >20 properties, consider these strategies:

### Split into composable sub-factories

```ts
// page-state.svelte.ts
export function createPageState(getData: () => Data) {
  const filters = createFilterState(getData);
  const zoom = createZoomState();
  const dialogs = createDialogState();

  return { filters, zoom, dialogs, /* page-level concerns */ };
}
```

Access as `state.filters.query`, `state.zoom.level`, `state.dialogs.confirmOpen`.

### Use a reactive class for complex domain state

When the state has private internals, validation in setters, or a large surface area, a class provides better organization than a factory:

```ts
export class EditorState {
  // Public reactive state
  width = $state(800);
  height = $state(600);

  // Private non-reactive state
  #undoStack: Command[] = [];

  // Derived
  area = $derived(this.width * this.height);

  // Methods grouped by concern
  undo() { /* ... */ }
  redo() { /* ... */ }
}
```

### Decision guide

| Return object size | Approach |
|---|---|
| <10 properties | Single factory function |
| 10-25 properties | Single factory, group related actions |
| 25+ properties | Split into sub-factories or use a class |

## Testing After Refactoring

When extracting components or logic:

1. **Run existing tests first** to establish a baseline (some may already be failing)
2. **Preserve `data-testid` attributes** exactly when moving template to sub-components
3. **Run tests after** to verify zero regressions
4. **Consider unit-testing the factory** directly for complex business logic — the factory is a plain function that can be tested without rendering

```ts
// dashboard-state.svelte.test.ts
import { createDashboardState } from './dashboard-state.svelte';

it('sorts by date descending by default', () => {
  const state = createDashboardState(() => mockData);
  expect(state.sorted[0].date).toBe('2024-12-01');
});
```
