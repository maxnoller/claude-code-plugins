# Testing — Full Reference

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

## Locator Hierarchy

Always prefer semantic queries in this order:

```ts
// 1. Roles (best - accessible)
page.getByRole('button', { name: 'Submit' });
page.getByRole('textbox', { name: 'Email' });

// 2. Labels (forms)
page.getByLabel('Email address');

// 3. Text content
page.getByText('Welcome back');
page.getByText(/error/i);

// 4. Test IDs (last resort)
page.getByTestId('submit-button');
```

### Handling Multiple Elements

Vitest Browser Mode is strict — multiple matches throw errors:

```ts
page.getByRole('listitem').first();
page.getByRole('listitem').nth(2);
page.getByRole('listitem').last();
page.getByRole('listitem', { name: /important/i });
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
  });
});
```

### Testing with FormData

```ts
describe('ContactForm', () => {
  it('collects form data correctly', async () => {
    let submittedData: FormData | null = null;

    render(ContactForm, {
      props: { onsubmit: (data: FormData) => submittedData = data }
    });

    await page.getByLabel('Name').fill('John Doe');
    await page.getByLabel('Message').fill('Hello world');
    await page.getByRole('button', { name: 'Send' }).click();

    expect(submittedData?.get('name')).toBe('John Doe');
  });
});
```

## Async Testing

### Testing Loading States

```ts
describe('AsyncComponent', () => {
  it('shows loading then content', async () => {
    render(AsyncComponent);
    await expect.element(page.getByText('Loading...')).toBeVisible();
    await expect.element(page.getByText('Data loaded')).toBeVisible();
    await expect.element(page.getByText('Loading...')).not.toBeInTheDocument();
  });
});
```

### Mocking Fetch

```ts
import { vi, beforeEach, afterEach } from 'vitest';

describe('DataFetcher', () => {
  beforeEach(() => { vi.stubGlobal('fetch', vi.fn()); });
  afterEach(() => { vi.unstubAllGlobals(); });

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

For load functions and server code, use the Node test project:

```ts
// src/routes/api/users.test.ts (note: not .svelte.test.ts)
import { describe, expect, it } from 'vitest';
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

## Running Tests

```bash
pnpm test              # Run all tests
pnpm test --watch      # Watch mode
pnpm vitest src/lib/components/Button.svelte.test.ts  # Specific file
pnpm vitest --ui       # With UI
```

## Key Principles

1. **Use real browsers** — `vitest-browser-svelte` over jsdom
2. **Prefer semantic queries** — roles > labels > text > test IDs
3. **Test behavior, not implementation** — what users see and do
4. **Use `flushSync`** — when testing runes outside components
5. **Use `untrack`** — to read `$state` values without tracking
6. **Separate client/server tests** — different file extensions
