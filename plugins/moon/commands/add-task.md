---
description: Add a new task to a moon project
argument-hint: "<task-name> [project]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion"]
---

# Add Task to Moon Project

Add a new task to a specific project or to inherited tasks.

## Arguments

The user provided: `$ARGUMENTS`

## Process

### 1. Parse Arguments

Parse `$ARGUMENTS` to extract:
- `task-name`: Name of the task (required, first argument)
- `project`: Project to add task to (optional second argument)

If project not specified:
- If in a project directory (has moon.yml), use current project
- Otherwise, ask if adding to inherited tasks (.moon/tasks.yml) or specific project

### 2. Determine Task Type

Ask or detect what kind of task:

```
What does this task do?
- build (compile/bundle code)
- test (run tests)
- lint (check code quality)
- format (format code)
- dev (development server)
- deploy (deployment)
- custom (other)
```

### 3. Gather Task Details

Ask for or detect:

- **Command**: What command to run
- **Inputs**: Files that affect the task (for caching)
- **Outputs**: Files created by the task
- **Dependencies**: Other tasks that must run first

For common task types, suggest sensible defaults:

**build:**
```yaml
command: 'tsc'  # or vite build, webpack, etc.
inputs:
  - 'src/**/*'
  - 'tsconfig.json'
outputs:
  - 'dist'
deps:
  - '^:build'
```

**test:**
```yaml
command: 'vitest run'
inputs:
  - 'src/**/*'
  - 'tests/**/*'
deps:
  - '~:build'
```

**lint:**
```yaml
command: 'eslint src'
inputs:
  - 'src/**/*'
  - '.eslintrc.*'
```

**dev:**
```yaml
command: 'vite dev'
preset: 'server'
```

### 4. Add Task Configuration

Edit the appropriate file:

**Project-specific task (moon.yml):**
```yaml
tasks:
  new-task:
    command: 'command here'
    inputs:
      - 'src/**/*'
    outputs:
      - 'dist'
```

**Inherited task (.moon/tasks.yml):**
```yaml
tasks:
  new-task:
    command: 'command here'
    inputs:
      - '@group(sources)'
```

### 5. Verify Task

Run `moon task <project>:<task-name>` to verify the task is configured correctly.

## Advanced Options

If the user wants advanced configuration, ask about:

- **cache**: Enable/disable caching
- **runInCI**: Should this run in CI?
- **platform**: node, system, etc.
- **env**: Environment variables
- **options**: retryCount, timeout, priority, etc.

## Output

- Updated moon.yml or .moon/tasks.yml
- Task configuration with sensible defaults
- Verification that task is recognized

## Examples

- `/moon:add-task build` - Add build task to current project
- `/moon:add-task test api` - Add test task to api project
- `/moon:add-task lint` - Add lint task (asks for project or inherited)
