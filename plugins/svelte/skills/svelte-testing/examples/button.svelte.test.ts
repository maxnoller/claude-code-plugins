// Button.svelte.test.ts - Testing Svelte 5 components with vitest-browser-svelte
// 
// This example demonstrates browser-based component testing.
// Requires vitest configured with browser mode and @vitest/browser.
//
// vitest.config.ts:
// import { svelte } from 'vitest-browser-svelte';
// export default defineConfig({
//   plugins: [svelte()],
//   test: { browser: { enabled: true, name: 'chromium' } }
// });

import { describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Button from './Button.svelte';

// Note: In actual tests, 'page' comes from '@vitest/browser/context'
// This example shows the pattern without requiring full vitest setup

describe('Button', () => {
    it('renders with text', async () => {
        const { container } = render(Button, { label: 'Click me' });

        const button = container.querySelector('button');
        expect(button).toBeTruthy();
        expect(button?.textContent).toContain('Click me');
    });

    it('handles click events', async () => {
        const handleClick = vi.fn();
        const { container } = render(Button, { label: 'Click', onclick: handleClick });

        const button = container.querySelector('button');
        button?.click();
        expect(handleClick).toHaveBeenCalledOnce();
    });

    it('can be disabled', async () => {
        const { container } = render(Button, { label: 'Submit', disabled: true });

        const button = container.querySelector('button') as HTMLButtonElement;
        expect(button?.disabled).toBe(true);
    });

    it('shows loading state', async () => {
        const { container } = render(Button, { label: 'Save', loading: true });

        const button = container.querySelector('button');
        expect(button?.getAttribute('aria-busy')).toBe('true');
    });
});
