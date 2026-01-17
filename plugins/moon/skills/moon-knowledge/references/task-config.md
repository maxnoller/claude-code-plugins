# Task Configuration Reference

Complete reference for task configuration in moon.

## Task Definition

```yaml
tasks:
  task-name:
    # Required
    command: 'command to run'

    # Optional
    args: ['--flag', 'value']
    env:
      NODE_ENV: 'production'
    inputs:
      - 'src/**/*'
    outputs:
      - 'dist'
    deps:
      - 'other:task'
    platform: 'node'
    preset: 'server'
    local: true
    options:
      cache: true
      # ... more options
```

## Command & Arguments

```yaml
tasks:
  # Simple command
  lint:
    command: 'eslint src'

  # Command with args
  build:
    command: 'vite'
    args:
      - 'build'
      - '--mode'
      - 'production'

  # Script reference (package.json)
  legacy:
    command: 'npm run build'
```

## Inputs

Files that affect the task hash (for caching):

```yaml
tasks:
  build:
    inputs:
      # Literal paths
      - 'src/**/*'
      - 'package.json'
      - 'tsconfig.json'

      # Negation (exclude)
      - '!src/**/*.test.ts'

      # File groups
      - '@group(sources)'
      - '@group(configs)'

      # Environment variables
      - '$NODE_ENV'

      # From other projects
      - 'project://shared'
      - 'project://utils?group=sources'

      # Optional inputs (won't fail if missing)
      - file: 'optional.config.js'
        optional: true

      # Globs with options
      - glob: 'src/**/*.ts'
        optional: false
```

## Outputs

Files created by the task (for caching and hydration):

```yaml
tasks:
  build:
    outputs:
      # Directory
      - 'dist'

      # Glob pattern
      - 'dist/**/*.js'
      - 'dist/**/*.css'

      # Exclude from output
      - '!dist/internal'

      # Optional outputs
      - file: 'dist/sourcemaps'
        optional: true
```

## Dependencies

Tasks that must run before this task:

```yaml
tasks:
  build:
    deps:
      # Specific project task
      - 'shared:build'
      - 'utils:codegen'

      # All dependencies' task (from dependsOn)
      - '^:build'

      # Task in current project
      - '~:codegen'

      # With additional args/env
      - target: 'shared:build'
        args: '--production'
        env:
          DEBUG: 'false'

      # Optional dependency (won't fail if task doesn't exist)
      - target: 'maybe:task'
        optional: true
```

## Task Options

```yaml
tasks:
  example:
    command: '...'
    options:
      # Caching
      cache: true              # true, false, 'local', 'remote'
      cacheKey: 'v2'           # Custom cache key
      cacheLifetime: '1 day'   # Cache expiration

      # CI behavior
      runInCI: true            # true, false, 'always', 'affected', 'only', 'skip'

      # Execution
      retryCount: 3            # Retry on failure
      timeout: 300             # Timeout in seconds
      persistent: true         # Long-running task
      interactive: true        # Needs stdin

      # Parallelization
      runDepsInParallel: true  # Run deps in parallel
      priority: 'high'         # critical, high, normal, low

      # Output
      outputStyle: 'stream'    # buffer, buffer-only-failure, hash, none, stream

      # Environment
      envFile: '.env.local'    # Load env file

      # Platform
      os: 'linux'              # linux, macos, windows, or array
      shell: true              # Run in shell
      unixShell: 'bash'        # bash, zsh, fish, etc.

      # Working directory
      runFromWorkspaceRoot: false

      # Inheritance
      mergeArgs: 'append'      # append, prepend, replace
      mergeDeps: 'append'
      mergeEnv: 'append'
      mergeInputs: 'append'
      mergeOutputs: 'append'

      # Advanced
      mutex: 'resource-name'   # Exclusive lock
      internal: true           # Can't be run directly
      allowFailure: true       # Don't fail pipeline
```

## Presets

Apply common configurations:

```yaml
tasks:
  # Development server
  dev:
    command: 'vite dev'
    preset: 'server'
    # Equivalent to:
    # local: true
    # options:
    #   cache: false
    #   outputStyle: 'stream'
    #   persistent: true
    #   runInCI: false

  # Watch mode
  watch:
    command: 'vitest --watch'
    preset: 'watcher'
```

## Inherited Tasks

In `.moon/tasks.yml` for all projects:

```yaml
# Default options for all inherited tasks
taskOptions:
  retryCount: 2
  outputStyle: 'stream'

# File groups available to all projects
fileGroups:
  sources:
    - 'src/**/*'
  tests:
    - '**/*.test.{ts,tsx}'
  configs:
    - '*.config.{js,ts}'

# Tasks inherited by all projects
tasks:
  lint:
    command: 'eslint'
    args: ['--ext', '.ts,.tsx', 'src']
    inputs:
      - '@group(sources)'
      - '@group(configs)'

  typecheck:
    command: 'tsc'
    args: ['--noEmit']
    inputs:
      - '@group(sources)'
      - 'tsconfig.json'
```

In `.moon/tasks/node.yml` for Node projects:

```yaml
# Only applies to projects with language: javascript/typescript
tasks:
  test:
    command: 'vitest run'
```
