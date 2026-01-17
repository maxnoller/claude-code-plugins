---
description: Add a new project to the moon workspace
argument-hint: "<project-name> [path]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion"]
---

# Add Project to Moon Workspace

Add a new project to the moon workspace with proper configuration.

## Arguments

The user provided: `$ARGUMENTS`

## Process

### 1. Parse Arguments

Parse `$ARGUMENTS` to extract:
- `project-name`: Name/identifier for the project (required, first argument)
- `path`: Where to create the project (optional second argument, defaults to reasonable location)

### 2. Detect Workspace Structure

Read `.moon/workspace.yml` to understand:
- Existing project patterns (e.g., `apps/*`, `packages/*`)
- Workspace conventions

If path not specified, determine appropriate location based on:
- Project type (app vs library)
- Existing patterns

### 3. Gather Project Details

If not clear from arguments, ask user:

```
What type of project is this?
- application (standalone app)
- library (shared package)
- tool (internal tooling)
```

```
What language/stack?
- TypeScript/JavaScript
- Python
- Rust
- Other
```

### 4. Create Project Structure

Create the project directory with:

#### moon.yml

```yaml
# Project metadata
project:
  name: 'Human Readable Name'
  description: 'Project description'

# Classification
language: 'typescript'
type: 'library'  # or application, tool
stack: 'frontend'  # or backend, infrastructure

# Tags for constraints
tags:
  - 'lib'

# Dependencies on other workspace projects
dependsOn: []

# Project-specific tasks (inherits from .moon/tasks.yml)
tasks:
  # Add project-specific tasks here
  # build:
  #   command: 'tsc'
  #   outputs: ['dist']
```

#### Basic project files

Based on language:

**TypeScript/JavaScript:**
- `package.json` with name and basic scripts
- `tsconfig.json` if TypeScript
- `src/index.ts` placeholder

**Python:**
- `pyproject.toml`
- `src/` or package directory

### 5. Update Workspace (if needed)

If the project path doesn't match existing glob patterns in workspace.yml, offer to add it:

```yaml
projects:
  - 'apps/*'
  - 'packages/*'
  - 'tools/new-project'  # Added explicit path
```

### 6. Verify Setup

Run `moon project <project-name>` to verify the project is discovered.

## Output

- Created project directory
- moon.yml configuration
- Basic project structure
- Updated workspace.yml (if needed)

## Examples

- `/moon:add-project shared-utils` - Add a project named shared-utils
- `/moon:add-project web-app apps/web` - Add web-app at apps/web
- `/moon:add-project api-client packages/api` - Add api-client package
