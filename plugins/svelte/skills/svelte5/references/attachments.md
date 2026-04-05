# Attachments — Full Reference

Attachments (`{@attach}`) were introduced in Svelte 5.29 as the successor to `use:action`. They're functions that receive a DOM element, run inside an effect (so they're inherently reactive), and can be used on both DOM elements and components.

## Basic Attachment

```ts
// tooltip.svelte.ts
export function tooltip(text: string) {
  return (node: HTMLElement) => {
    const tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.textContent = text;

    function show() {
      document.body.appendChild(tip);
      const rect = node.getBoundingClientRect();
      tip.style.left = `${rect.left + rect.width / 2}px`;
      tip.style.top = `${rect.top - 8}px`;
    }

    function hide() {
      tip.remove();
    }

    node.addEventListener('mouseenter', show);
    node.addEventListener('mouseleave', hide);

    // Cleanup — runs on re-run or destroy
    return () => {
      node.removeEventListener('mouseenter', show);
      node.removeEventListener('mouseleave', hide);
      tip.remove();
    };
  };
}
```

Usage:

```svelte
<script>
  import { tooltip } from '$lib/tooltip.svelte';
</script>

<button {@attach tooltip('Save changes')}>Save</button>
```

## Reactivity

Because attachments run inside an effect, they automatically re-run when dependencies change:

```ts
export function highlight(color: string) {
  return (node: HTMLElement) => {
    node.style.backgroundColor = color; // Re-runs when color changes
    return () => {
      node.style.backgroundColor = '';
    };
  };
}
```

```svelte
<script>
  let color = $state('yellow');
</script>

<!-- Automatically updates when color changes -->
<div {@attach highlight(color)}>Highlighted</div>
```

## Click Outside Pattern

```ts
// click-outside.svelte.ts
export function clickOutside(callback: () => void) {
  return (node: HTMLElement) => {
    function handler(event: MouseEvent) {
      if (!node.contains(event.target as Node)) {
        callback();
      }
    }

    document.addEventListener('click', handler, true);
    return () => document.removeEventListener('click', handler, true);
  };
}
```

```svelte
<div {@attach clickOutside(() => open = false)}>
  Dropdown content
</div>
```

## Multiple Attachments

Multiple attachments can be applied to the same element:

```svelte
<button
  {@attach tooltip('Save')}
  {@attach trackClick('save-button')}
>
  Save
</button>
```

## Attachments on Components

Unlike `use:action`, attachments work on components. The attachment is applied to the component's root element:

```svelte
<MyButton {@attach tooltip('Click me')}>Save</MyButton>
```

## createAttachmentKey — Typed Attachment Props

For components that accept attachments as props:

```ts
// focus-trap.svelte.ts
import { createAttachmentKey } from 'svelte/attachments';

export const focusTrap = createAttachmentKey<{ enabled: boolean }>();
```

```svelte
<!-- Modal.svelte -->
<script>
  import { focusTrap } from '$lib/focus-trap.svelte';
</script>

<div {@attach focusTrap({ enabled: true })}>
  <!-- modal content -->
</div>
```

## fromAction — Migrate Existing Actions

Wrap an existing `use:action` as an attachment:

```ts
import { fromAction } from 'svelte/attachments';
import { myAction } from '$lib/old-actions';

const myAttachment = fromAction(myAction);
```

```svelte
<!-- Before: <div use:myAction={params}> -->
<!-- After: -->
<div {@attach myAttachment(params)}>
```

## Inline Attachments

For simple one-off cases:

```svelte
<input {@attach (node) => {
  node.focus();
  return () => {};
}} />
```

## Key Differences from use:action

| Feature | `use:action` | `{@attach}` |
|---------|-------------|-------------|
| Reactivity | Manual `update()` method | Automatic (runs in effect) |
| Components | DOM elements only | DOM elements + components |
| Cleanup | `destroy()` method | Return function |
| Multiple | Multiple `use:` directives | Multiple `{@attach}` |
| TypeScript | Loose typing | Strong typing with `createAttachmentKey` |
