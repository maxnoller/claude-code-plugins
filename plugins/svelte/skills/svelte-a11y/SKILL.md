---
name: Svelte Accessibility (a11y)
description: Accessibility best practices for Svelte 5 applications. Use when users ask about accessibility, a11y, ARIA attributes, screen readers, keyboard navigation, focus management, semantic HTML, or making Svelte apps accessible to users with disabilities.
---

# Svelte Accessibility (a11y)

Svelte has built-in accessibility warnings. This guide covers patterns for building inclusive Svelte applications.

## Svelte A11y Warnings

Svelte compiler warns about common a11y issues:

```svelte
<!-- Warning: A11y: <img> element should have an alt attribute -->
<img src="photo.jpg" />

<!-- Fixed -->
<img src="photo.jpg" alt="A sunset over mountains" />

<!-- Decorative image -->
<img src="decoration.jpg" alt="" />
```

Common warnings:
- Missing `alt` on images
- Missing form labels
- Invalid ARIA attributes
- Non-interactive elements with handlers
- Missing keyboard support

## Semantic HTML

### Use Correct Elements

```svelte
<!-- BAD: div with click handler -->
<div onclick={handleClick}>Click me</div>

<!-- GOOD: button -->
<button onclick={handleClick}>Click me</button>

<!-- BAD: span as link -->
<span onclick={() => goto('/about')}>About</span>

<!-- GOOD: anchor tag -->
<a href="/about">About</a>
```

### Heading Hierarchy

```svelte
<!-- BAD: Skipped heading levels -->
<h1>Page Title</h1>
<h3>Section</h3>

<!-- GOOD: Proper hierarchy -->
<h1>Page Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>
```

### Landmark Regions

```svelte
<header>
  <nav aria-label="Main navigation">
    <!-- navigation -->
  </nav>
</header>

<main>
  <!-- main content -->
</main>

<aside aria-label="Related content">
  <!-- sidebar -->
</aside>

<footer>
  <!-- footer -->
</footer>
```

## Form Accessibility

### Labels

```svelte
<!-- Explicit label (preferred) -->
<label for="email">Email address</label>
<input id="email" type="email" name="email" />

<!-- Implicit label -->
<label>
  Email address
  <input type="email" name="email" />
</label>

<!-- Hidden label for visual design -->
<label for="search" class="sr-only">Search</label>
<input id="search" type="search" placeholder="Search..." />

<style>
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
</style>
```

### Error Messages

```svelte
<script>
  let email = $state('');
  let error = $state('');

  function validate() {
    if (!email.includes('@')) {
      error = 'Please enter a valid email address';
    } else {
      error = '';
    }
  }
</script>

<div>
  <label for="email">Email</label>
  <input
    id="email"
    type="email"
    bind:value={email}
    onblur={validate}
    aria-describedby={error ? 'email-error' : undefined}
    aria-invalid={error ? 'true' : undefined}
  />
  {#if error}
    <p id="email-error" class="error" role="alert">
      {error}
    </p>
  {/if}
</div>
```

### Required Fields

```svelte
<label for="name">
  Name <span aria-hidden="true">*</span>
  <span class="sr-only">(required)</span>
</label>
<input id="name" type="text" required aria-required="true" />
```

### Fieldsets for Groups

```svelte
<fieldset>
  <legend>Shipping Address</legend>

  <label for="street">Street</label>
  <input id="street" type="text" />

  <label for="city">City</label>
  <input id="city" type="text" />
</fieldset>
```

## Keyboard Navigation

### Focus Management

```svelte
<script>
  let inputRef = $state<HTMLInputElement>();

  function focusInput() {
    inputRef?.focus();
  }
</script>

<input bind:this={inputRef} />
<button onclick={focusInput}>Focus Input</button>
```

### Focus Trap for Modals

```svelte
<script>
  let modalRef = $state<HTMLDivElement>();
  let previousFocus: HTMLElement | null = null;

  function openModal() {
    previousFocus = document.activeElement as HTMLElement;
    // Focus first focusable element in modal
  }

  function closeModal() {
    previousFocus?.focus();
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      closeModal();
      return;
    }

    if (e.key === 'Tab') {
      // Trap focus within modal
      const focusable = modalRef?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (!focusable?.length) return;

      const first = focusable[0] as HTMLElement;
      const last = focusable[focusable.length - 1] as HTMLElement;

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }
</script>

<div
  bind:this={modalRef}
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  onkeydown={handleKeydown}
>
  <h2 id="modal-title">Modal Title</h2>
  <!-- content -->
  <button onclick={closeModal}>Close</button>
</div>
```

### Skip Links

```svelte
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<nav><!-- navigation --></nav>

<main id="main-content" tabindex="-1">
  <!-- main content -->
</main>

<style>
  .skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    padding: 8px;
    background: #000;
    color: #fff;
    z-index: 100;
  }

  .skip-link:focus {
    top: 0;
  }
</style>
```

### Custom Keyboard Interactions

```svelte
<script>
  let items = ['Home', 'About', 'Contact'];
  let activeIndex = $state(0);

  function handleKeydown(e: KeyboardEvent) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        break;
      case 'ArrowUp':
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        break;
      case 'Home':
        e.preventDefault();
        activeIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        activeIndex = items.length - 1;
        break;
    }
  }
</script>

<ul role="listbox" onkeydown={handleKeydown}>
  {#each items as item, i}
    <li
      role="option"
      aria-selected={activeIndex === i}
      tabindex={activeIndex === i ? 0 : -1}
    >
      {item}
    </li>
  {/each}
</ul>
```

## ARIA Patterns

### Live Regions

Announce dynamic changes to screen readers:

```svelte
<script>
  let message = $state('');
  let items = $state([]);

  async function addItem() {
    const newItem = await saveItem();
    items = [...items, newItem];
    message = `${newItem.name} added to list`;
  }
</script>

<!-- Polite: Waits for silence -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  {message}
</div>

<!-- Assertive: Interrupts immediately (use sparingly) -->
<div aria-live="assertive" role="alert">
  {#if error}
    {error}
  {/if}
</div>
```

### Expandable Content

```svelte
<script>
  let expanded = $state(false);
</script>

<button
  aria-expanded={expanded}
  aria-controls="content"
  onclick={() => expanded = !expanded}
>
  {expanded ? 'Hide' : 'Show'} Details
</button>

{#if expanded}
  <div id="content">
    Details content here...
  </div>
{/if}
```

### Tabs

```svelte
<script>
  let tabs = ['Tab 1', 'Tab 2', 'Tab 3'];
  let activeTab = $state(0);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'ArrowRight') {
      activeTab = (activeTab + 1) % tabs.length;
    } else if (e.key === 'ArrowLeft') {
      activeTab = (activeTab - 1 + tabs.length) % tabs.length;
    }
  }
</script>

<div role="tablist" onkeydown={handleKeydown}>
  {#each tabs as tab, i}
    <button
      role="tab"
      id="tab-{i}"
      aria-selected={activeTab === i}
      aria-controls="panel-{i}"
      tabindex={activeTab === i ? 0 : -1}
      onclick={() => activeTab = i}
    >
      {tab}
    </button>
  {/each}
</div>

{#each tabs as tab, i}
  <div
    role="tabpanel"
    id="panel-{i}"
    aria-labelledby="tab-{i}"
    hidden={activeTab !== i}
  >
    Content for {tab}
  </div>
{/each}
```

## Loading States

```svelte
<script>
  let loading = $state(false);
</script>

<button
  onclick={handleSubmit}
  disabled={loading}
  aria-busy={loading}
>
  {loading ? 'Submitting...' : 'Submit'}
</button>

<!-- Or with live region -->
<div aria-live="polite" class="sr-only">
  {#if loading}
    Loading, please wait...
  {/if}
</div>
```

## Color and Contrast

### Don't Rely on Color Alone

```svelte
<!-- BAD: Only color indicates error -->
<input class="error" />

<!-- GOOD: Icon + color + text -->
<input aria-invalid="true" aria-describedby="error-msg" />
<span class="error-icon" aria-hidden="true">⚠️</span>
<p id="error-msg">This field is required</p>
```

### Ensure Sufficient Contrast

- Normal text: 4.5:1 minimum
- Large text (18px+ or 14px+ bold): 3:1 minimum
- UI components: 3:1 minimum

## Motion and Animation

### Respect Reduced Motion

```svelte
<style>
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
</style>
```

Or in JavaScript:

```svelte
<script>
  import { onMount } from 'svelte';

  let prefersReducedMotion = $state(false);

  onMount(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    prefersReducedMotion = mq.matches;
    mq.addEventListener('change', (e) => prefersReducedMotion = e.matches);
  });
</script>
```

## Testing Accessibility

### Automated Testing

```bash
# Install axe-core
pnpm add -D @axe-core/playwright

# In tests
import AxeBuilder from '@axe-core/playwright';

test('page should be accessible', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

### Manual Testing Checklist

- [ ] Navigate with keyboard only (Tab, Enter, Escape, Arrows)
- [ ] Test with screen reader (VoiceOver, NVDA)
- [ ] Check color contrast ratios
- [ ] Verify focus indicators are visible
- [ ] Test at 200% zoom
- [ ] Disable CSS and check content order
