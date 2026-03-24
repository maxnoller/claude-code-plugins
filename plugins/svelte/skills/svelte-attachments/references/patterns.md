# Attachment Patterns

## Getter Pattern for Expensive Setup

When an attachment has expensive initialization that should not re-run on every parameter change, accept a getter function instead of a direct value:

```typescript
function chart(getData: () => DataPoint[]): Attachment {
  return (node) => {
    // Expensive: runs once
    const instance = new ChartLibrary(node);

    $effect(() => {
      // Cheap: runs on data changes
      instance.update(getData());
    });

    return () => instance.destroy();
  };
}
```

```svelte
<div {@attach chart(() => data)}>...</div>
```

## Click Outside

```typescript
import type { Attachment } from 'svelte/attachments';

function clickOutside(callback: () => void): Attachment {
  return (node) => {
    function handleClick(event: MouseEvent) {
      if (!node.contains(event.target as Node)) {
        callback();
      }
    }
    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  };
}
```

```svelte
<div {@attach clickOutside(() => open = false)}>
  Dropdown content
</div>
```

## Intersection Observer

```typescript
function intersect(
  callback: (entry: IntersectionObserverEntry) => void,
  options?: IntersectionObserverInit
): Attachment {
  return (node) => {
    const observer = new IntersectionObserver(([entry]) => {
      callback(entry);
    }, options);
    observer.observe(node);
    return () => observer.disconnect();
  };
}
```

```svelte
<script>
  let visible = $state(false);
</script>

<div {@attach intersect((entry) => visible = entry.isIntersecting)}>
  {#if visible}Visible!{/if}
</div>
```

## Focus Trap

```typescript
function trapFocus(): Attachment {
  return (node) => {
    const previous = document.activeElement as HTMLElement;

    function focusable(): HTMLElement[] {
      return Array.from(node.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ));
    }

    function handleKeydown(event: KeyboardEvent) {
      if (event.key !== 'Tab') return;
      const elements = focusable();
      const first = elements.at(0);
      const last = elements.at(-1);
      const current = document.activeElement;

      if (event.shiftKey && current === first) {
        last?.focus();
        event.preventDefault();
      } else if (!event.shiftKey && current === last) {
        first?.focus();
        event.preventDefault();
      }
    }

    focusable()[0]?.focus();
    node.addEventListener('keydown', handleKeydown);

    return () => {
      node.removeEventListener('keydown', handleKeydown);
      previous?.focus();
    };
  };
}
```

```svelte
{#if showModal}
  <div class="modal" {@attach trapFocus()}>
    <input placeholder="Trapped focus" />
    <button onclick={() => showModal = false}>Close</button>
  </div>
{/if}
```

## Resize Observer

```typescript
function resize(
  callback: (entry: ResizeObserverEntry) => void
): Attachment {
  return (node) => {
    const observer = new ResizeObserver(([entry]) => callback(entry));
    observer.observe(node);
    return () => observer.disconnect();
  };
}
```

```svelte
<script>
  let width = $state(0);
  let height = $state(0);
</script>

<div {@attach resize((entry) => {
  width = entry.contentRect.width;
  height = entry.contentRect.height;
})}>
  {width} x {height}
</div>
```

## Drag Handle

```typescript
function draggable(
  onDrag: (dx: number, dy: number) => void
): Attachment {
  return (node) => {
    let startX: number, startY: number;

    function handlePointerDown(e: PointerEvent) {
      startX = e.clientX;
      startY = e.clientY;
      node.setPointerCapture(e.pointerId);
      node.addEventListener('pointermove', handlePointerMove);
      node.addEventListener('pointerup', handlePointerUp);
    }

    function handlePointerMove(e: PointerEvent) {
      onDrag(e.clientX - startX, e.clientY - startY);
      startX = e.clientX;
      startY = e.clientY;
    }

    function handlePointerUp() {
      node.removeEventListener('pointermove', handlePointerMove);
      node.removeEventListener('pointerup', handlePointerUp);
    }

    node.addEventListener('pointerdown', handlePointerDown);
    return () => node.removeEventListener('pointerdown', handlePointerDown);
  };
}
```

## Long Press

```typescript
function longPress(callback: () => void, duration = 500): Attachment {
  return (node) => {
    let timer: ReturnType<typeof setTimeout>;

    function handlePointerDown() {
      timer = setTimeout(callback, duration);
    }

    function handlePointerUp() {
      clearTimeout(timer);
    }

    node.addEventListener('pointerdown', handlePointerDown);
    node.addEventListener('pointerup', handlePointerUp);
    node.addEventListener('pointerleave', handlePointerUp);

    return () => {
      clearTimeout(timer);
      node.removeEventListener('pointerdown', handlePointerDown);
      node.removeEventListener('pointerup', handlePointerUp);
      node.removeEventListener('pointerleave', handlePointerUp);
    };
  };
}
```

## Auto-Resize Textarea

```typescript
function autoResize(): Attachment {
  return (textarea: HTMLTextAreaElement) => {
    function resize() {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }

    resize();
    textarea.addEventListener('input', resize);
    return () => textarea.removeEventListener('input', resize);
  };
}
```

```svelte
<textarea {@attach autoResize()}></textarea>
```
