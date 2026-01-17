---
name: Moon Knowledge
description: Provides comprehensive knowledge about moonrepo/moon for monorepo management and task running. Use when user asks about moon configuration, workspace setup, task definitions, CI/CD integration, proto toolchain, caching, optimization, or migration from other tools. Triggers on "moon", "moonrepo", "monorepo with moon", ".moon/", "moon.yml", "workspace.yml", "proto toolchain", "moon task", "moon ci".
---

# Moon - Monorepo Management and Task Runner

Moon is a build system and task runner for monorepos (and single projects) written in Rust. It emphasizes developer experience, performance through smart caching, and CI/CD optimization.

## Core Concepts

### Workspace Structure

The workspace root is denoted by the `.moon` directory:

```
project-root/
├── .moon/                    # Workspace root marker
│   ├── workspace.yml         # Workspace configuration
│   ├── toolchain.yml         # Toolchain/proto configuration
│   └── tasks.yml             # Inherited tasks for all projects (optional)
│   └── tasks/                # Language/type-specific inherited tasks
│       ├── node.yml
│       └── python.yml
├── .prototools               # Proto version pinning (optional)
├── apps/
│   └── web/
│       └── moon.yml          # Project-specific config
└── packages/
    └── shared/
        └── moon.yml
```

### Configuration Files

**`.moon/workspace.yml`** - Workspace-wide settings:
- Project discovery (`projects` globs)
- VCS configuration (git hooks, default branch)
- Pipeline settings (concurrency, retries)
- Remote caching
- Constraints and tag relationships

**`.moon/toolchain.yml`** - Language toolchains via proto:
- Node.js version and package manager
- Python, Rust, Go, Deno, Bun versions
- Proto integration settings

**`.moon/tasks.yml`** - Inherited tasks for ALL projects:
- File groups (sources, tests, configs)
- Common tasks (lint, format, typecheck, test)

**`moon.yml`** - Project-specific configuration:
- Project metadata (name, type, language, tags)
- Project dependencies (`dependsOn`)
- Project-specific tasks
- Task overrides

### Task Configuration

Tasks are defined with these key properties:

```yaml
tasks:
  build:
    command: 'vite build'
    inputs:
      - 'src/**/*'
      - 'package.json'
      - 'vite.config.ts'
    outputs:
      - 'dist'
    deps:
      - '^:build'          # All dependencies' build tasks
      - 'shared:codegen'   # Specific project task
    options:
      cache: true          # Enable caching (default)
      runInCI: true        # Run in CI (default)
      persistent: false    # For long-running tasks like dev servers
```

**Inputs** - Files that affect the task hash:
- Source files, configs, dependencies
- Use globs: `src/**/*.ts`, `!**/*.test.ts`

**Outputs** - Files created by the task:
- Build artifacts: `dist`, `build`
- Required for caching and hydration

**Dependencies** - Tasks that must run first:
- `^:taskname` - Same task in all project dependencies
- `~:taskname` - Same task in the current project
- `project:taskname` - Specific project's task

### Task Presets

Use presets for common task patterns:

```yaml
tasks:
  dev:
    command: 'vite dev'
    preset: 'server'    # Disables cache, streams output, persistent

  watch:
    command: 'vitest --watch'
    preset: 'watcher'   # Similar to server preset
```

### File Groups

Define reusable file patterns in `.moon/tasks.yml`:

```yaml
fileGroups:
  sources:
    - 'src/**/*'
  tests:
    - 'tests/**/*'
    - '**/*.test.ts'
  configs:
    - '*.config.{js,ts}'
    - 'package.json'
```

Use in tasks:
```yaml
tasks:
  test:
    command: 'vitest'
    inputs:
      - '@group(sources)'
      - '@group(tests)'
```

## Proto Toolchain Integration

Moon uses proto for toolchain management. Configure in `.moon/toolchain.yml`:

```yaml
# Node.js with pnpm
node:
  version: '20.10.0'
  packageManager: 'pnpm'
  pnpm:
    version: '8.15.0'

# Or use .prototools versions
node:
  version: 'inherit'
```

Create `.prototools` at workspace root:
```toml
node = "20.10.0"
pnpm = "8.15.0"
python = "3.12.0"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0    # Required for affected detection
      - uses: moonrepo/setup-toolchain@v0
        with:
          auto-install: true
      - run: moon ci
```

**Parallelization with matrix:**
```yaml
jobs:
  ci:
    strategy:
      matrix:
        index: [0, 1, 2, 3]
    steps:
      # ... setup ...
      - run: moon ci --job ${{ matrix.index }} --jobTotal 4
```

**Split by target type:**
```yaml
jobs:
  build:
    steps:
      - run: moon ci :build
  test:
    steps:
      - run: moon ci :test :lint
```

### GitLab CI

```yaml
stages:
  - ci

moon:
  stage: ci
  image: node:20
  before_script:
    - curl -fsSL https://moonrepo.dev/install/moon.sh | bash
  script:
    - moon ci
```

## VCS Hooks

Configure git hooks in `.moon/workspace.yml`:

```yaml
vcs:
  manager: git
  defaultBranch: main
  hooks:
    pre-commit:
      - 'moon run :lint :format --affected --status=staged'
    commit-msg:
      - 'moon run :commitlint -- $ARG1'
  syncHooks: true    # Auto-sync hooks for all contributors
```

Sync hooks manually: `moon sync hooks`
Clean hooks: `moon sync hooks --clean`

## Performance Optimization

### Caching Strategy

1. **Define precise inputs** - Only files that affect the task
2. **Define outputs** - Required for cache hydration
3. **Use file groups** - Consistent patterns across projects
4. **Remote caching** - Share cache across CI and developers

### Task Dependencies

- Use `^:task` for dependency graph traversal
- Avoid circular dependencies
- Use `optional: true` for soft dependencies

### Affected Detection

Moon only runs tasks for projects affected by changes:
```bash
moon run :test --affected              # Affected since default branch
moon run :test --affected --status=staged  # Only staged files
moon ci                                # Automatic affected detection
```

## Common Commands

```bash
# Run tasks
moon run project:task
moon run :task              # All projects with this task
moon run project:task1 project:task2

# Check workspace
moon check                  # Validate configs
moon project project-name   # Show project info
moon project-graph          # Visualize project graph
moon task-graph             # Visualize task graph

# CI
moon ci                     # Run affected tasks
moon ci :build :test        # Specific task types

# Sync
moon sync                   # Sync all
moon sync hooks             # Sync VCS hooks
```

## References

For detailed configuration options:
- See `references/workspace-config.md` for workspace.yml options
- See `references/project-config.md` for moon.yml options
- See `references/task-config.md` for task configuration details
- See `references/ci-examples.md` for CI/CD configurations

For migration guides:
- See `references/migration-npm.md` for npm scripts migration
- See `references/migration-turbo.md` for Turborepo migration
