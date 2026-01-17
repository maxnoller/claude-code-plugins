# Svelte 4 to Svelte 5 Migration Reference

Quick migration patterns from Svelte 4 to Svelte 5 runes.

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
| `onMount` | `$effect(() => { ... })` (for side effects) |
| `onDestroy` | Return cleanup from `$effect` |
