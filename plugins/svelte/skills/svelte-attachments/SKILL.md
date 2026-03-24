---
name: Svelte 5 Attachments
description: This skill should be used when the user asks to "add an attachment", "use {@attach}", "convert action to attachment", "create a tooltip attachment", "click outside handler", "migrate use:action", "fromAction", "createAttachmentKey", or mentions DOM behavior, element lifecycle, or the {@attach} directive in Svelte 5. Covers attachments (Svelte 5.29+), the modern replacement for use:action.
---

# Svelte 5 Attachments

Attachments (`{@attach}`) are the modern way to add reusable DOM behavior in Svelte 5.29+. They replace `use:action` with a simpler, fully reactive API.

## Core Concept

An attachment is a function that receives a DOM element when mounted and optionally returns a cleanup function:

```svelte
<script lang="ts">
  import type { Attachment } from 'svelte/attachments';

  const highlight: Attachment = (element) => {
    element.style.backgroundColor = 'yellow';
    return () => {
      element.style.backgroundColor = '';
    };
  };
</script>

<div {@attach highlight}>Highlighted</div>
```

Attachments run inside an effect — they automatically re-execute when reactive dependencies change.

## Attachment Factories (Parameterized)

Return an attachment function to accept parameters:

```svelte
<script lang="ts">
  import type { Attachment } from 'svelte/attachments';

  function tooltip(content: string): Attachment {
    return (element) => {
      const tip = tippy(element, { content });
      return tip.destroy;
    };
  }

  let label = $state('Hello!');
</script>

<button {@attach tooltip(label)}>Hover me</button>
```

When `label` changes, the attachment is destroyed and recreated. To avoid expensive re-setup, use the getter pattern — see `references/patterns.md`.

## Inline Attachments

Define attachments directly in markup:

```svelte
<canvas
  {@attach (canvas) => {
    const ctx = canvas.getContext('2d');
    $effect(() => {
      ctx.fillStyle = color;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    });
  }}
/>
```

Nested `$effect` inside an inline attachment enables fine-grained reactivity — the outer function runs once, the inner effect re-runs on changes.

## Conditional & Multiple Attachments

```svelte
<!-- Conditional: falsy values are ignored -->
<div {@attach enabled && clickOutside(() => open = false)}>...</div>

<!-- Multiple attachments on one element -->
<div
  {@attach tooltip('Info')}
  {@attach clickOutside(() => open = false)}
>...</div>
```

## Attachments on Components

Attachments pass through to elements when a component spreads props:

```svelte
<!-- Button.svelte -->
<script lang="ts">
  import type { HTMLButtonAttributes } from 'svelte/elements';
  let { children, ...props }: HTMLButtonAttributes = $props();
</script>

<button {...props}>
  {@render children?.()}
</button>
```

```svelte
<!-- Usage: attachment passes through to the <button> -->
<Button {@attach tooltip('Click me')}>Submit</Button>
```

## Migrating from Actions

### fromAction() utility

Convert existing `use:action` to attachments incrementally:

```svelte
<script>
  import { fromAction } from 'svelte/attachments';
  import { myAction } from '$lib/actions';
</script>

<!-- Before -->
<div use:myAction={param}>...</div>

<!-- After -->
<div {@attach fromAction(myAction, () => param)}>...</div>

<!-- No-param action -->
<div {@attach fromAction(myAction)}>...</div>
```

The second argument must be a **function returning** the parameter, not the parameter itself.

## Attachments vs Actions

| Feature | `use:action` | `{@attach}` |
|---|---|---|
| Reactivity | Manual `update()` | Automatic re-execution |
| Inline | Not supported | `{@attach (el) => {...}}` |
| Conditional | Workarounds needed | `{@attach cond && fn}` |
| Components | DOM elements only | Components + elements |
| Spreading | Not supported | `{...props}` compatible |
| Cleanup | `{ destroy() {} }` object | Return a function |
| Multiple | One per action name | Unlimited `{@attach}` |

**For new code, always prefer attachments.** Use `fromAction()` only for migrating existing action libraries.

## createAttachmentKey() for Libraries

Create symbol keys recognized as attachments when spread onto elements:

```ts
import { createAttachmentKey } from 'svelte/attachments';

const key = createAttachmentKey();

const props = {
  class: 'btn',
  [key]: (node: Element) => {
    // runs when element mounts
    return () => { /* cleanup */ };
  }
};
```

```svelte
<button {...props}>Click</button>
```

## Critical Rules

1. **Use attachments for all new DOM behavior** — `use:action` is legacy
2. **Always return cleanup** for listeners, intervals, third-party libraries
3. **Use getter pattern for expensive setup** — `{@attach foo(() => bar)}` separates setup from reactive updates
4. **`fromAction` second arg is a function** — `() => param`, not `param`
5. **Attachments re-run entirely on dependency changes** — use nested `$effect` for fine-grained control
6. **Component attachments require prop spreading** — `{...props}` on the target element

## Additional Resources

### Reference Files
- **`references/patterns.md`** — Common attachment patterns (click outside, intersection observer, focus trap, drag, resize)

### Example Files
- **`examples/tooltip.svelte`** — Tooltip attachment with tippy.js
- **`examples/click-outside.svelte`** — Click outside handler
