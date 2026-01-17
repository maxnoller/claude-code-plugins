# Migration Guide: Turborepo to Moon

## Overview

Turborepo and moon have similar concepts but different configuration approaches.

## Key Differences

| Turborepo | Moon |
|-----------|------|
| `turbo.json` | `.moon/workspace.yml` + `moon.yml` |
| `pipeline` | `tasks` |
| `dependsOn: ["^build"]` | `deps: ["^:build"]` |
| `outputs: ["dist/**"]` | `outputs: ["dist"]` |
| `inputs: ["src/**"]` | `inputs: ["src/**/*"]` |
| `cache: false` | `options: { cache: false }` |
| `persistent: true` | `preset: 'server'` |

## Configuration Migration

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"],
      "inputs": ["src/**", "package.json"]
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### .moon/tasks.yml

```yaml
tasks:
  build:
    command: 'npm run build'  # Or direct command
    deps:
      - '^:build'
    outputs:
      - 'dist'
      - '.next'
    inputs:
      - 'src/**/*'
      - 'package.json'

  lint:
    command: 'eslint src'
    inputs:
      - 'src/**/*'
    # No outputs = no caching of outputs (but command is still cached)

  test:
    command: 'vitest run'
    deps:
      - '~:build'
    inputs:
      - 'src/**/*'

  dev:
    command: 'npm run dev'
    preset: 'server'
```

## Dependency Syntax

```
# Turborepo → Moon
"^build"       → "^:build"      # All dependencies
"build"        → "~:build"      # Same project
"lib#build"    → "lib:build"    # Specific project
```

## Filter Syntax

```bash
# Turborepo
turbo run build --filter=web
turbo run build --filter=...web  # With dependencies
turbo run build --filter=web...  # With dependents

# Moon
moon run web:build
moon run :build --query "project=web"
moon run web:build --dependents
```

## Affected/Changed

```bash
# Turborepo
turbo run build --filter=[origin/main]

# Moon
moon run :build --affected
moon ci  # Automatic in CI
```

## Environment Variables

### turbo.json

```json
{
  "pipeline": {
    "build": {
      "env": ["NODE_ENV", "API_URL"],
      "passThroughEnv": ["CI"]
    }
  },
  "globalEnv": ["GLOBAL_VAR"]
}
```

### moon.yml

```yaml
tasks:
  build:
    command: 'build'
    env:
      NODE_ENV: '${NODE_ENV}'
      API_URL: '${API_URL}'
    inputs:
      - '$NODE_ENV'
      - '$API_URL'
```

## Remote Caching

### Turborepo

```bash
# Vercel Remote Cache
turbo run build --team=myteam --token=$TURBO_TOKEN
```

### Moon

```yaml
# .moon/workspace.yml
unstable_remote:
  host: 'https://your-cache-server.com'
  auth:
    token: '${MOON_CACHE_TOKEN}'
```

## CI Migration

### Turborepo (GitHub Actions)

```yaml
- uses: actions/cache@v3
  with:
    path: .turbo
    key: turbo-${{ github.sha }}
    restore-keys: turbo-

- run: turbo run build test lint
```

### Moon (GitHub Actions)

```yaml
- uses: moonrepo/setup-toolchain@v0
- run: moon ci
```

## Tips

1. **moon is more explicit** - Define inputs/outputs per task
2. **moon has better affected detection** - Uses VCS diff
3. **moon handles toolchain** - No need for separate Node setup
4. **moon uses project-level config** - moon.yml per project vs global turbo.json
