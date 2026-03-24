---
name: Svelte 5 Attachments
description: This skill should be used when the user asks to "add an attachment", "use {@attach}", "convert action to attachment", "create a tooltip attachment", "click outside handler", "migrate use:action", "fromAction", "createAttachmentKey", or mentions DOM behavior, element lifecycle, or the {@attach} directive in Svelte 5. Covers attachments (Svelte 5.29+), the modern replacement for use:action.
---

# Svelte 5 Attachments

Attachments (`{@attach}`) replace `use:action` in Svelte 5.29+. For new code, always use attachments.

## Syntax

```svelte
<div {@attach myAttachment}>...</div>
```

An attachment is a function `(element) => cleanup`. It runs inside an effect — re-executes when reactive dependencies change.

## Parameterized (Factory Pattern)

```svelte
<script>
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

When `label` changes, the attachment is destroyed and recreated entirely. To avoid expensive re-setup, pass a getter and use a nested `$effect`:

```ts
function chart(getData: () => Data): Attachment {
  return (node) => {
    const instance = new ChartLib(node);  // expensive, runs once
    $effect(() => instance.update(getData()));  // cheap, re-runs
    return () => instance.destroy();
  };
}
```

Usage: `{@attach chart(() => data)}`

## Inline, Conditional, Multiple

```svelte
<!-- Inline -->
<canvas {@attach (el) => { const ctx = el.getContext('2d'); /* ... */ }} />

<!-- Conditional (falsy = ignored) -->
<div {@attach enabled && clickOutside(() => open = false)}>...</div>

<!-- Multiple on one element -->
<div {@attach tooltip('Info')} {@attach clickOutside(() => open = false)}>...</div>
```

## On Components

Attachments pass through when a component spreads props (`{...restProps}` on the target element):

```svelte
<Button {@attach tooltip('Click me')}>Submit</Button>
```

## Migrating from Actions

```svelte
<!-- Before -->
<div use:myAction={param}>...</div>

<!-- After -->
<div {@attach fromAction(myAction, () => param)}>...</div>
```

Import: `import { fromAction } from 'svelte/attachments'`. The second arg must be a **function returning** the parameter.

## Attachments vs Actions

| Feature | `use:action` | `{@attach}` |
|---|---|---|
| Reactivity | Manual `update()` | Automatic |
| Inline | No | `{@attach (el) => {...}}` |
| Conditional | Workarounds | `{@attach cond && fn}` |
| Components | DOM only | Components + elements |
| Cleanup | `{ destroy() {} }` | Return a function |
| Multiple | One per action | Unlimited |

## createAttachmentKey() (Library Authors)

Create symbol keys recognized as attachments when spread:

```ts
import { createAttachmentKey } from 'svelte/attachments';
const key = createAttachmentKey();
const props = { class: 'btn', [key]: (node) => { /* ... */ } };
```

## Additional Resources

- **`references/patterns.md`** — Click outside, intersection observer, focus trap, drag, resize, long press, auto-resize textarea
- **`examples/tooltip.svelte`** — Tooltip with tippy.js
- **`examples/click-outside.svelte`** — Click outside handler
