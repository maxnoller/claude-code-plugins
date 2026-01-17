---
description: Migrate from other task runners to moon (npm scripts, turbo, Make, pre-commit)
argument-hint: "[source-type]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion"]
---

# Migrate to Moon

Migrate existing task runner configuration to moon tasks.

## Arguments

The user provided: `$ARGUMENTS`

If provided, this specifies the source type to migrate from (e.g., `npm`, `turbo`, `make`, `pre-commit`).

## Supported Sources

- **npm/yarn/pnpm scripts** (package.json)
- **Turborepo** (turbo.json)
- **Makefile**
- **pre-commit** (.pre-commit-config.yaml)
- **Just** (justfile)
- **Gradle** (build.gradle)

## Process

### 1. Detect Source

If source-type not specified, detect automatically:

- Check for `turbo.json` → Turborepo
- Check for `Makefile` → Make
- Check for `.pre-commit-config.yaml` → pre-commit
- Check for `justfile` → Just
- Check for `package.json` with scripts → npm scripts
- Check for `build.gradle` → Gradle

If multiple detected, ask user which to migrate.

### 2. Analyze Existing Configuration

Read the source configuration and extract:

- Task/target names
- Commands
- Dependencies between tasks
- Environment variables
- File patterns (inputs/outputs where detectable)

### 3. Generate Moon Configuration

#### From npm scripts

```json
// package.json
{
  "scripts": {
    "build": "tsc && vite build",
    "test": "vitest run",
    "lint": "eslint src"
  }
}
```

Becomes:

```yaml
# moon.yml
tasks:
  build:
    command: 'tsc && vite build'
    inputs:
      - 'src/**/*'
      - 'tsconfig.json'
    outputs:
      - 'dist'

  test:
    command: 'vitest run'
    inputs:
      - 'src/**/*'

  lint:
    command: 'eslint src'
    inputs:
      - 'src/**/*'
```

#### From Turborepo

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

Becomes:

```yaml
tasks:
  build:
    command: 'npm run build'
    deps:
      - '^:build'
    outputs:
      - 'dist'
```

#### From Makefile

```makefile
build: clean
	npm run build

clean:
	rm -rf dist
```

Becomes:

```yaml
tasks:
  build:
    command: 'npm run build'
    deps:
      - '~:clean'
    outputs:
      - 'dist'

  clean:
    command: 'rm -rf dist'
    options:
      cache: false
```

#### From pre-commit

Convert hooks to moon tasks + VCS hook configuration:

```yaml
# .moon/workspace.yml
vcs:
  hooks:
    pre-commit:
      - 'moon run :lint :format --affected --status=staged'
```

### 4. Handle Special Cases

**Development servers:**
```yaml
tasks:
  dev:
    command: 'vite dev'
    preset: 'server'  # Instead of complex options
```

**Watch mode:**
```yaml
tasks:
  watch:
    command: 'vitest --watch'
    preset: 'watcher'
```

**Scripts with pre/post hooks:**
Convert to explicit dependencies:
```yaml
tasks:
  prebuild:
    command: 'clean'
  build:
    command: 'tsc'
    deps: ['~:prebuild']
```

### 5. Suggest Improvements

After migration, suggest optimizations:

1. **Add inputs** for better caching
2. **Add outputs** for cache hydration
3. **Use file groups** for consistent patterns
4. **Move common tasks** to `.moon/tasks.yml`
5. **Add `^:task` deps** for proper build order

### 6. Clean Up (Optional)

Ask if user wants to:
- Remove old configuration (turbo.json, Makefile)
- Keep as backup
- Keep scripts in package.json for backwards compatibility

## Output

- Generated moon.yml files
- Updated .moon/tasks.yml (if applicable)
- Updated .moon/workspace.yml (for VCS hooks)
- Summary of migrated tasks
- Suggestions for improvements

## Examples

- `/moon:migrate` - Auto-detect and migrate
- `/moon:migrate npm` - Migrate from npm scripts
- `/moon:migrate turbo` - Migrate from Turborepo
- `/moon:migrate pre-commit` - Migrate pre-commit hooks
