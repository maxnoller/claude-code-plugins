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

The standard pattern for extracting reactive logic:

```ts
// todo-state.svelte.ts
export function createTodoState() {
  let todos = $state<Todo[]>([]);
  let remaining = $derived(todos.filter(t => !t.done).length);

  return {
    get todos() { return todos; },
    get remaining() { return remaining; },
    add(text: string) { todos.push({ text, done: false }); },
    toggle(i: number) { todos[i].done = !todos[i].done; },
  };
}
```

Use when: logic exceeds ~200 lines, or the same logic pattern is reused across multiple components.

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
