# Svelte 4 to Svelte 5 Migration Reference

Complete migration patterns from Svelte 4 to Svelte 5 runes.

## State Management

| Svelte 4 | Svelte 5 |
|----------|----------|
| `let count = 0` (auto-reactive in .svelte) | `let count = $state(0)` |
| `export let name` (props) | `let { name } = $props()` |
| `export let value = 'default'` | `let { value = 'default' } = $props()` |

## Reactive Statements

| Svelte 4 | Svelte 5 |
|----------|----------|
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { complex; logic; }` | `let result = $derived.by(() => { complex; logic; return result; })` |
| `$: console.log(count)` | `$effect(() => { console.log(count) })` |

## Event Handling

| Svelte 4 | Svelte 5 |
|----------|----------|
| `on:click={handler}` | `onclick={handler}` |
| `on:click\|preventDefault` | `onclick={(e) => { e.preventDefault(); handler(e) }}` |
| `createEventDispatcher()` | Callback props: `let { onclick } = $props()` |

## Slots to Snippets

| Svelte 4 | Svelte 5 |
|----------|----------|
| `<slot />` | `{@render children()}` |
| `<slot name="header" />` | `{@render header?.()}` |
| `<slot {item} />` (slot props) | `{@render row(item)}` (snippet params) |

## Two-Way Binding

| Svelte 4 | Svelte 5 |
|----------|----------|
| `export let value` + `bind:value` | `let { value = $bindable() } = $props()` |

## Component Lifecycle

| Svelte 4 | Svelte 5 |
|----------|----------|
| `beforeUpdate` | `$effect.pre(() => { ... })` |
| `afterUpdate` | `$effect(() => { ... })` |
| `onMount` | `$effect(() => { ... })` for side effects, or keep `onMount` for one-time setup that shouldn't re-run on state changes |
| `onDestroy` | Return cleanup from `$effect` |

## Actions to Attachments

| Svelte 4 | Svelte 5 (5.29+) |
|----------|----------|
| `use:action` | `{@attach handler}` |
| `use:action={params}` | `{@attach handler(params)}` |
| `action` returns `{ update, destroy }` | Attachment returns cleanup function; re-runs automatically |
| Actions on DOM elements only | Attachments work on DOM elements and components |

To migrate existing actions, use `fromAction()` from `svelte/attachments`:

```ts
import { fromAction } from 'svelte/attachments';
import { myAction } from '$lib/old-actions';

const myAttachment = fromAction(myAction);
// <div {@attach myAttachment(params)}>
```

## Dynamic Components

| Svelte 4 | Svelte 5 |
|----------|----------|
| `<svelte:component this={X} />` | `<X />` — components are dynamic by default |

## Stores to Runes

| Svelte 4 | Svelte 5 |
|----------|----------|
| `import { writable } from 'svelte/store'` | `let x = $state(value)` in `.svelte.ts` |
| `$store` (auto-subscription) | Direct access to `$state` variable |
| `store.set(value)` | Direct assignment |
| `store.subscribe(cb)` | `$effect(() => { /* read state */ })` |

Stores (`svelte/store`) are not formally deprecated yet but are superseded by runes for new code.

## SvelteKit Stores to State

| Svelte 4 | Svelte 5 |
|----------|----------|
| `import { page } from '$app/stores'` | `import { page } from '$app/state'` |
| `$page.url.pathname` | `page.url.pathname` (no $ prefix) |
| `$navigating` | `navigating` from `$app/state` |
| `$updated` | `updated` from `$app/state` |

`$app/stores` is deprecated and will be removed in SvelteKit 3.

## Component Instance Methods

| Svelte 4 | Svelte 5 |
|----------|----------|
| `new Component({ target })` | `mount(Component, { target })` from `svelte` |
| `component.$set({ prop: value })` | Direct prop assignment or `$state` |
| `component.$on('event', handler)` | Callback props |
| `component.$destroy()` | `unmount(component)` from `svelte` |

## Compiler Options

| Svelte 4 | Svelte 5 |
|----------|----------|
| `accessors: true` | No effect in runes mode |
| `immutable: true` | No effect in runes mode — use `$state.raw` for shallow reactivity |
