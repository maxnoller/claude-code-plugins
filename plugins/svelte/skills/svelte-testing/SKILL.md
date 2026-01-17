---
name: Svelte Testing with Sveltest
description: Modern testing patterns for Svelte 5 using vitest-browser-svelte and Sveltest methodology. Use when users ask about testing Svelte components, unit tests, integration tests, vitest, vitest-browser-svelte, testing runes, testing $state/$derived/$effect, or setting up a test environment for Svelte 5.
---

# Svelte Testing with Sveltest

Modern Svelte 5 testing uses `vitest-browser-svelte` to run tests in real browsers instead of simulated environments like jsdom. This approach provides accurate testing of runes, reactivity, and DOM behavior.

## Setup

### Install Dependencies

```bash
pnpm install -D @vitest/browser-playwright vitest-browser-svelte playwright

# Remove old testing libraries if present
pnpm remove @testing-library/jest-dom @testing-library/svelte jsdom
```

### Configure Vite

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { playwright } from '@vitest/browser-playwright';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  test: {
    projects: [
      {
        name: 'client',
        test: {
          testTimeout: 2000,
          browser: {
            enabled: true,
            provider: playwright(),
            instances: [{ browser: 'chromium' }],
          },
          include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
        },
      },
      {
        name: 'server',
        test: {
          environment: 'node',
          include: ['src/**/*.{test,spec}.{js,ts}'],
        },
      },
    ],
  },
});
```

### Setup File

```ts
// src/vitest-setup-client.ts
/// <reference types="vitest/browser" />
/// <reference types="@vitest/browser-playwright" />
```

## Core Testing Patterns

### Basic Component Test

```ts
// src/lib/components/Button.svelte.test.ts
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { page } from 'vitest/browser';
import Button from './Button.svelte';

describe('Button', () => {
  it('renders with text', async () => {
    render(Button, { props: { label: 'Click me' } });

    const button = page.getByRole('button', { name: 'Click me' });
    await expect.element(button).toBeVisible();
  });

  it('handles click events', async () => {
    let clicked = false;
    render(Button, {
      props: {
        label: 'Click',
        onclick: () => clicked = true
      }
    });

    await page.getByRole('button').click();
    expect(clicked).toBe(true);
  });
});
```

### Locator Hierarchy

Always prefer semantic queries in this order:

```ts
// 1. Roles (best - accessible)
page.getByRole('button', { name: 'Submit' });
page.getByRole('textbox', { name: 'Email' });
page.getByRole('link', { name: 'Home' });

// 2. Labels (forms)
page.getByLabel('Email address');
page.getByLabel('Password');

// 3. Text content
page.getByText('Welcome back');
page.getByText(/error/i);

// 4. Test IDs (last resort)
page.getByTestId('submit-button');
```

### Handling Multiple Elements

Vitest Browser Mode is strict—multiple matches throw errors:

```ts
// When multiple elements match, be specific
page.getByRole('listitem').first();
page.getByRole('listitem').nth(2);
page.getByRole('listitem').last();

// Or use more specific selectors
page.getByRole('listitem', { name: /important/i });
```

## Testing Svelte 5 Runes

### Testing $state

```ts
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { page } from 'vitest/browser';
import Counter from './Counter.svelte';

describe('Counter with $state', () => {
  it('increments count', async () => {
    render(Counter);

    const button = page.getByRole('button', { name: 'Increment' });
    const count = page.getByTestId('count');

    await expect.element(count).toHaveTextContent('0');
    await button.click();
    await expect.element(count).toHaveTextContent('1');
    await button.click();
    await expect.element(count).toHaveTextContent('2');
  });
});
```

### Testing $derived

```ts
// Component: DoubleCounter.svelte
// let count = $state(0);
// let doubled = $derived(count * 2);

describe('Derived values', () => {
  it('updates derived when state changes', async () => {
    render(DoubleCounter);

    const count = page.getByTestId('count');
    const doubled = page.getByTestId('doubled');
    const button = page.getByRole('button', { name: '+' });

    await expect.element(count).toHaveTextContent('0');
    await expect.element(doubled).toHaveTextContent('0');

    await button.click();

    await expect.element(count).toHaveTextContent('1');
    await expect.element(doubled).toHaveTextContent('2');
  });
});
```

### Testing $effect

```ts
import { vi } from 'vitest';

describe('Effects', () => {
  it('runs effect on state change', async () => {
    const consoleSpy = vi.spyOn(console, 'log');

    render(ComponentWithEffect);

    await page.getByRole('button').click();

    expect(consoleSpy).toHaveBeenCalledWith('Count changed:', 1);

    consoleSpy.mockRestore();
  });
});
```

### Testing Runes in .svelte.ts Files

```ts
// counter.svelte.ts
export function createCounter(initial = 0) {
  let count = $state(initial);
  return {
    get count() { return count },
    increment: () => count++
  };
}

// counter.svelte.test.ts
import { describe, expect, it } from 'vitest';
import { flushSync, untrack } from 'svelte';
import { createCounter } from './counter.svelte';

describe('createCounter', () => {
  it('increments count', () => {
    const counter = createCounter(0);

    expect(untrack(() => counter.count)).toBe(0);

    counter.increment();
    flushSync();

    expect(untrack(() => counter.count)).toBe(1);
  });
});
```

## Form Testing

### Basic Form Test

```ts
describe('LoginForm', () => {
  it('submits with valid data', async () => {
    const handleSubmit = vi.fn();
    render(LoginForm, { props: { onsubmit: handleSubmit } });

    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Login' }).click();

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });

  it('shows validation errors', async () => {
    render(LoginForm);

    await page.getByRole('button', { name: 'Login' }).click();

    await expect.element(page.getByText('Email is required')).toBeVisible();
    await expect.element(page.getByText('Password is required')).toBeVisible();
  });
});
```

### Testing with FormData

```ts
describe('ContactForm', () => {
  it('collects form data correctly', async () => {
    let submittedData: FormData | null = null;

    render(ContactForm, {
      props: {
        onsubmit: (data: FormData) => submittedData = data
      }
    });

    await page.getByLabel('Name').fill('John Doe');
    await page.getByLabel('Message').fill('Hello world');
    await page.getByRole('button', { name: 'Send' }).click();

    expect(submittedData?.get('name')).toBe('John Doe');
    expect(submittedData?.get('message')).toBe('Hello world');
  });
});
```

## Async Testing

### Testing Loading States

```ts
describe('AsyncComponent', () => {
  it('shows loading then content', async () => {
    render(AsyncComponent);

    // Initially shows loading
    await expect.element(page.getByText('Loading...')).toBeVisible();

    // Eventually shows content
    await expect.element(page.getByText('Data loaded')).toBeVisible();
    await expect.element(page.getByText('Loading...')).not.toBeInTheDocument();
  });
});
```

### Mocking Fetch

```ts
import { vi, beforeEach, afterEach } from 'vitest';

describe('DataFetcher', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('displays fetched data', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ name: 'Test User' })
    } as Response);

    render(DataFetcher);

    await expect.element(page.getByText('Test User')).toBeVisible();
  });
});
```

## Testing Snippets and Children

```ts
import { createRawSnippet } from 'svelte';

describe('Card', () => {
  it('renders children', async () => {
    const children = createRawSnippet(() => ({
      render: () => '<p>Card content</p>'
    }));

    render(Card, { props: { children } });

    await expect.element(page.getByText('Card content')).toBeVisible();
  });
});
```

## Server-Side Testing

For load functions and server code, use Node environment:

```ts
// src/routes/api/users.test.ts (note: not .svelte.test.ts)
import { describe, expect, it, vi } from 'vitest';
import { load } from './+page.server';

describe('Users page load', () => {
  it('returns user data', async () => {
    const result = await load({
      params: {},
      locals: { user: { id: '1' } }
    } as any);

    expect(result.users).toBeDefined();
    expect(Array.isArray(result.users)).toBe(true);
  });
});
```

## Running Tests

```bash
# Run all tests
pnpm test

# Watch mode
pnpm test --watch

# Run specific file
pnpm vitest src/lib/components/Button.svelte.test.ts

# Run with UI
pnpm vitest --ui
```

## File Naming Convention

```
src/
├── lib/
│   ├── components/
│   │   ├── Button.svelte
│   │   └── Button.svelte.test.ts    # Browser test
│   └── utils/
│       ├── format.ts
│       └── format.test.ts           # Node test
└── routes/
    └── api/
        ├── +server.ts
        └── api.test.ts              # Node test
```

## Key Principles

1. **Use real browsers** - `vitest-browser-svelte` over jsdom
2. **Prefer semantic queries** - roles > labels > text > test IDs
3. **Test behavior, not implementation** - What users see and do
4. **Use `flushSync`** - When testing runes outside components
5. **Use `untrack`** - To read `$state` values without tracking
6. **Separate client/server tests** - Different file extensions
