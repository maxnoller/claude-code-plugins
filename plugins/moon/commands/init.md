---
description: Initialize moon in a project with toolchain, workspace, and CI configuration
argument-hint: "[project-path]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion"]
---

# Moon Initialization

Initialize moon in a project. This command sets up:
- `.moon/` directory structure
- `workspace.yml` configuration
- `toolchain.yml` with proto integration
- `.prototools` version pinning
- CI configuration (GitHub Actions or GitLab CI)
- VCS hooks for pre-commit

## Arguments

The user may provide: `$ARGUMENTS`

Parse this as the optional project path. If empty or not provided, use the current directory.

## Process

### 1. Detect Project Structure

First, analyze the existing project:

- Check for existing `.moon/` directory
- Detect package manager (`package.json`, `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`)
- Detect languages (TypeScript, Python, Rust, Go, etc.)
- Find existing projects/packages (monorepo structure)
- Check for existing task runners (package.json scripts, Makefile, turbo.json)
- Detect CI configuration (`.github/workflows/`, `.gitlab-ci.yml`)

### 2. Determine Configuration

Based on detection, determine:

- **Projects**: Glob patterns for project discovery
- **Toolchain**: Languages and versions to configure
- **VCS**: Git settings, default branch

If anything is ambiguous, ask the user using AskUserQuestion:
- Which package manager to use (if multiple detected)
- Which CI provider (GitHub Actions vs GitLab CI)
- Whether to set up VCS hooks
- Project discovery patterns (if complex structure)

### 3. Create Configuration

Create the following files:

#### .moon/workspace.yml

```yaml
projects:
  - 'apps/*'
  - 'packages/*'
  # Adjust based on detected structure

vcs:
  manager: 'git'
  defaultBranch: 'main'
  hooks:
    pre-commit:
      - 'moon run :lint :format --affected --status=staged'
  syncHooks: true
```

#### .moon/toolchain.yml

```yaml
# Configure based on detected languages
node:
  version: 'inherit'  # From .prototools
  packageManager: 'pnpm'  # Or detected package manager
  pnpm:
    version: 'inherit'
```

#### .prototools

```toml
# Pin tool versions
node = "20.10.0"
pnpm = "8.15.0"
# Add other detected tools
```

#### .moon/tasks.yml (optional)

If common tasks are detected, create inherited tasks:

```yaml
fileGroups:
  sources:
    - 'src/**/*'
  tests:
    - '**/*.test.{ts,tsx}'
  configs:
    - '*.config.{js,ts}'

tasks:
  lint:
    command: 'eslint src'
    inputs:
      - '@group(sources)'
  # ... other common tasks
```

### 4. Create CI Configuration

Based on user preference:

#### GitHub Actions (.github/workflows/ci.yml)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: moonrepo/setup-toolchain@v0
        with:
          auto-install: true
      - run: moon ci
```

#### GitLab CI (.gitlab-ci.yml)

```yaml
stages:
  - ci

variables:
  GIT_DEPTH: 0

moon:
  stage: ci
  image: node:20
  before_script:
    - curl -fsSL https://moonrepo.dev/install/moon.sh | bash
    - export PATH="$HOME/.moon/bin:$PATH"
  script:
    - moon ci
```

### 5. Provide Next Steps

After initialization, tell the user:

1. Run `moon sync hooks` to set up git hooks
2. Run `moon check` to validate configuration
3. Add `moon.yml` to individual projects for project-specific tasks
4. Consider running `/moon:migrate` if migrating from another task runner

## Arguments

- `project-path` (optional): Path to initialize. Defaults to current directory.

## Examples

- `/moon:init` - Initialize in current directory
- `/moon:init ./my-project` - Initialize in specific directory
