# Remote Functions Version History

API changes across SvelteKit versions:

| Version | Change |
|---------|--------|
| v2.27 | Initial release: `query`, `form`, `command`, `prerender` |
| v2.31 | OpenTelemetry tracing for remote functions (`kit.experimental.tracing.server`) |
| v2.35 | `query.batch` added |
| v2.37 | `set()` callable on server queries; `query.refresh()` resolved on server |
| v2.38 | `query.batch` collects within macrotask |
| v2.39 | Lazy discovery of remote functions in `node_modules` |
| v2.42 | Enhanced `form` with schema support, field properties |
| v2.47.3 | `invalid()` function from `@sveltejs/kit` |
| v2.49 | File uploads streamable in form remote functions |
| v2.50 | **Breaking:** `buttonProps` removed; use `.as('submit', value)` instead |
| v2.53.2 | Fixes: deep partial types for `.value()`/`.set()`, optional types, correct URL info |
| v2.54 | Don't wait for non-awaited remote functions in templates |

## Adapter Support

| Adapter | Support | Notes |
|---------|---------|-------|
| adapter-node | Full | |
| adapter-vercel | Full (6.3.1+) | Remote calls traceable under `/_app/remote` |
| adapter-netlify | Full (6.0.4+) | Fixed catch-all function generation |
| adapter-cloudflare | Full | |
| adapter-static | Not supported | No server runtime |

## Security Notes

- Versions 2.44.0–2.49.4 had security vulnerabilities affecting remote functions (patched in 2.49.5+)
- Always update to latest SvelteKit when using remote functions
