# Migration Guide: npm Scripts to Moon

## Overview

Convert package.json scripts to moon tasks for better caching, dependency tracking, and CI optimization.

## Basic Migration

### Before (package.json)

```json
{
  "scripts": {
    "build": "tsc && vite build",
    "dev": "vite dev",
    "lint": "eslint src",
    "format": "prettier --write src",
    "test": "vitest run",
    "test:watch": "vitest --watch"
  }
}
```

### After (moon.yml)

```yaml
tasks:
  build:
    command: 'tsc && vite build'
    inputs:
      - 'src/**/*'
      - 'package.json'
      - 'tsconfig.json'
      - 'vite.config.ts'
    outputs:
      - 'dist'

  dev:
    command: 'vite dev'
    preset: 'server'

  lint:
    command: 'eslint src'
    inputs:
      - 'src/**/*'
      - '.eslintrc.*'

  format:
    command: 'prettier --write src'
    inputs:
      - 'src/**/*'
      - '.prettierrc*'

  test:
    command: 'vitest run'
    inputs:
      - 'src/**/*'
      - 'vitest.config.*'

  test-watch:
    command: 'vitest --watch'
    preset: 'watcher'
```

## Complex Scripts

### Scripts with Arguments

```json
{
  "scripts": {
    "build:prod": "vite build --mode production",
    "build:dev": "vite build --mode development"
  }
}
```

```yaml
tasks:
  build:
    command: 'vite build'
    args:
      - '--mode'
      - 'production'
    # Or allow overriding:
    # args: ['--mode', '${MODE:-production}']

  build-dev:
    command: 'vite build'
    args: ['--mode', 'development']
```

### Scripts with Environment Variables

```json
{
  "scripts": {
    "build": "NODE_ENV=production webpack"
  }
}
```

```yaml
tasks:
  build:
    command: 'webpack'
    env:
      NODE_ENV: 'production'
```

### Pre/Post Scripts

```json
{
  "scripts": {
    "prebuild": "rm -rf dist",
    "build": "tsc",
    "postbuild": "cp -r assets dist/"
  }
}
```

```yaml
tasks:
  clean:
    command: 'rm -rf dist'
    options:
      cache: false

  build:
    command: 'tsc'
    deps:
      - '~:clean'
    outputs:
      - 'dist'

  build-assets:
    command: 'cp -r assets dist/'
    deps:
      - '~:build'
```

### Chained Scripts

```json
{
  "scripts": {
    "ci": "npm run lint && npm run test && npm run build"
  }
}
```

```yaml
# Don't create a "ci" task - use moon ci command instead
# Individual tasks with proper inputs/outputs will be cached

tasks:
  lint:
    command: 'eslint src'
    inputs: ['src/**/*']

  test:
    command: 'vitest run'
    inputs: ['src/**/*']

  build:
    command: 'vite build'
    inputs: ['src/**/*']
    outputs: ['dist']
```

## Workspaces Migration

### Before (root package.json)

```json
{
  "scripts": {
    "build": "npm run build --workspaces",
    "lint": "npm run lint --workspaces"
  }
}
```

### After (.moon/tasks.yml)

```yaml
# Inherited by all projects
tasks:
  lint:
    command: 'eslint'
    args: ['src']
    inputs:
      - '@group(sources)'
      - '.eslintrc.*'

  build:
    command: 'vite build'
    inputs:
      - '@group(sources)'
      - '@group(configs)'
    outputs:
      - 'dist'
    deps:
      - '^:build'  # Build dependencies first
```

## Script References

If you need to keep npm scripts for backwards compatibility:

```yaml
tasks:
  legacy-build:
    command: 'npm run build'
    # Note: Less efficient, prefer direct commands
```

## Tips

1. **Remove scripts from package.json** once migrated (optional but cleaner)
2. **Use file groups** for consistent input patterns
3. **Add outputs** to enable caching
4. **Use deps** instead of chaining with `&&`
5. **Use presets** for dev servers and watchers
