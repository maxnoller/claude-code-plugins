# Async Error & Warning Reference

## Compiler Errors

### experimental_async
```
Cannot use `await` ... unless `experimental.async` is `true`
```
Add `compilerOptions: { experimental: { async: true } }` to `svelte.config.js`.

### legacy_await_invalid
```
Cannot use `await` ... unless in runes mode
```
Async expressions require runes mode. Remove `svelte:options` legacy flag or ensure the file uses runes.

### illegal_await_expression
```
`use:`, `transition:`, `animate:` directives ... do not support await
```
Move async logic out of directives. Use `$derived` to await data, then pass the resolved value.

## Runtime Errors

### async_derived_orphan
```
Cannot create `$derived(...)` with `await` outside effect tree
```
Async deriveds must be created within a component or inside an effect scope. Cannot create at module top-level.

### await_invalid (server)
```
Encountered asynchronous work while rendering synchronously
```
SSR: Use `await render(App)` (async) instead of synchronous render. Or ensure async work is inside a `<svelte:boundary>` with `pending` snippet.

### effect_pending_outside_reaction
```
`$effect.pending()` can only be called inside an effect or derived
```
Move `$effect.pending()` into a reactive context — inside `$derived`, `$effect`, or template expressions.

### fork_discarded
```
Cannot commit a fork that was already discarded
```
Track fork state and don't call `commit()` after `discard()`.

### fork_timing
```
Cannot create a fork inside an effect or when state changes are pending
```
Call `fork()` from event handlers, not from effects or during reactive updates.

## Runtime Warnings

### await_waterfall
```
An async derived `%name%` was not read immediately after it resolved
```
Indicates sequential async deriveds creating a waterfall. Split promise creation from awaiting:

```ts
// Waterfall (triggers warning):
let a = $derived(await fetchA());
let b = $derived(await fetchB());

// Fixed (parallel):
let aP = $derived(fetchA());
let bP = $derived(fetchB());
let a = $derived(await aP);
let b = $derived(await bP);
```
