# Tailwind CSS v4 for SvelteKit

## Setup

### Vite Plugin (replaces PostCSS)

```ts
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
});
```

No `postcss.config.js` needed. No `tailwind.config.ts` needed.

### CSS Configuration

```css
/* src/app.css */
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

/* Theme variables — OKLCH format only */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.205 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.205 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.205 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.5rem;
  --sidebar-background: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.451 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.205 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
}

/* Map CSS variables to Tailwind theme */
@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-sidebar-background: var(--sidebar-background);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

## Adding Custom Theme Colors

1. Add CSS variables in `:root` and `.dark`:
```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}
.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}
```

2. Register in `@theme inline`:
```css
@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

3. Use as Tailwind classes: `bg-warning text-warning-foreground`

## Dark Mode

Class-based, managed by `mode-watcher`:

```svelte
<!-- +layout.svelte -->
<script>
  import "../app.css";
  import { ModeWatcher } from "mode-watcher";
  let { children } = $props();
</script>

<ModeWatcher />
{@render children?.()}
```

```svelte
<!-- Toggle component -->
<script>
  import { toggleMode, setMode, resetMode } from "mode-watcher";
  import Sun from "@lucide/svelte/icons/sun";
  import Moon from "@lucide/svelte/icons/moon";
</script>

<button onclick={toggleMode} class="...">
  <Sun class="h-4 w-4 rotate-0 scale-100 dark:-rotate-90 dark:scale-0" />
  <Moon class="absolute h-4 w-4 rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
</button>
```

## What Changed from Tailwind v3

| Before (v3) | After (v4) |
|---|---|
| `tailwind.config.ts` | CSS `@theme inline` block |
| PostCSS plugin | `@tailwindcss/vite` Vite plugin |
| HSL color format | OKLCH color format |
| `darkMode: "class"` in config | `@custom-variant dark (&:is(.dark *))` in CSS |
| `tailwindcss-animate` | `tw-animate-css` |
| `content: ["./src/**/*.{svelte,ts}"]` | Automatic content detection |
