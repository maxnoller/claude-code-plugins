# Project Configuration Reference

Complete reference for `moon.yml` (project-level configuration).

## Full Example

```yaml
# Project metadata
project:
  name: 'My Web App'
  description: 'Main web application'
  channel: '#web-team'
  owner: '@web-team'
  maintainers: ['@alice', '@bob']
  metadata:
    deprecated: false
    priority: 'high'

# Project classification
language: 'typescript'
type: 'application'        # application, library, tool, scaffolding, configuration, automation
stack: 'frontend'          # frontend, backend, infrastructure, systems

# Tags for categorization and constraints
tags:
  - 'react'
  - 'vite'
  - 'app'

# Explicit project dependencies
dependsOn:
  - 'shared-ui'
  - 'api-client'
  - id: 'design-system'
    scope: 'peer'          # production, development, build, peer

# Platform for tasks (auto-detected if not set)
platform: 'node'           # node, deno, bun, rust, system

# Project-level toolchain overrides
toolchain:
  node:
    version: '20.10.0'
  typescript:
    syncProjectReferences: true

# File groups (project-specific)
fileGroups:
  sources:
    - 'src/**/*'
  tests:
    - 'src/**/*.test.ts'
    - 'tests/**/*'
  assets:
    - 'public/**/*'

# Tasks
tasks:
  build:
    command: 'vite build'
    inputs:
      - '@group(sources)'
      - 'vite.config.ts'
    outputs:
      - 'dist'
    deps:
      - '^:build'

  dev:
    command: 'vite dev'
    preset: 'server'

  test:
    command: 'vitest run'
    inputs:
      - '@group(sources)'
      - '@group(tests)'
```

## Project Metadata

```yaml
project:
  name: 'Human Readable Name'
  description: 'What this project does'
  channel: '#slack-channel'
  owner: '@team-name'
  maintainers: ['@user1', '@user2']
  metadata:
    # Any custom key-value pairs
    deprecated: false
```

## Project Classification

```yaml
# Programming language
language: 'typescript'  # javascript, typescript, rust, go, python, etc.

# Project type
type: 'application'
# Options: application, library, tool, scaffolding, configuration, automation

# Technology stack
stack: 'frontend'
# Options: frontend, backend, infrastructure, systems
```

## Dependencies

```yaml
# Simple dependencies
dependsOn:
  - 'shared'
  - 'utils'

# With scopes
dependsOn:
  - id: 'api-client'
    scope: 'production'    # Runtime dependency
  - id: 'test-utils'
    scope: 'development'   # Dev-only dependency
  - id: 'codegen'
    scope: 'build'         # Build-time dependency
  - id: 'types'
    scope: 'peer'          # Peer dependency
```

## Task Configuration

See `task-config.md` for detailed task options.

## Toolchain Overrides

Override workspace toolchain settings per-project:

```yaml
toolchain:
  node:
    version: '18.19.0'     # Different Node version
  typescript:
    syncProjectReferences: false
    includeProjectReferenceSources: true
```
