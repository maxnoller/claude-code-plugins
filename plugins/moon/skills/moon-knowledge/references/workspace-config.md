# Workspace Configuration Reference

Complete reference for `.moon/workspace.yml` options.

## Full Example

```yaml
# Inherit from another workspace config
extends: 'https://raw.githubusercontent.com/org/repo/master/.moon/workspace.yml'

# Project discovery
projects:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'
  # Or explicit mapping:
  # web: 'apps/web'
  # api: 'apps/api'

# Version control system
vcs:
  manager: 'git'
  defaultBranch: 'main'
  provider: 'github'  # github, gitlab, bitbucket, other
  remoteCandidates:
    - 'origin'
    - 'upstream'
  hooks:
    pre-commit:
      - 'moon run :lint :format --affected --status=staged'
    commit-msg:
      - 'moon run commitlint -- $ARG1'
  hookFormat: 'bash'  # native, bash
  syncHooks: true     # Auto-sync hooks for all contributors

# Pipeline configuration
pipeline:
  concurrency: 8           # Max parallel tasks
  timeout: 3600            # Global timeout in seconds
  batchEverything: false   # Batch all targets
  inheritColorsForPipedTasks: true

# Generator settings
generator:
  templates:
    - './templates'

# Remote caching (unstable)
unstable_remote:
  host: 'https://cache.example.com'
  auth:
    token: '${MOON_CACHE_TOKEN}'
  cache:
    compression: true
    verifyIntegrity: true

# Constraints for project boundaries
constraints:
  enforceProjectTypeRelationships: true
  tagRelationships:
    app: ['lib', 'util']
    lib: ['util']

# Code owners generation
codeowners:
  orderBy: 'project-name'  # file-source, project-name
  syncOnRun: true

# Extensions (WASM plugins)
extensions:
  example:
    plugin: 'https://example.com/plugin.wasm'
```

## Key Sections

### projects

Define how projects are discovered:

```yaml
# Glob patterns (recommended)
projects:
  - 'apps/*'
  - 'packages/*'
  - '!packages/deprecated-*'  # Exclude pattern

# Explicit mapping
projects:
  web: 'apps/web'
  api: 'apps/api'
  shared: 'packages/shared'

# Sources with globs
projects:
  globs:
    - 'apps/*'
  sources:
    legacy: 'old/legacy-app'
```

### vcs.hooks

Git hooks with moon commands:

```yaml
vcs:
  hooks:
    # Pre-commit: lint and format staged files
    pre-commit:
      - 'moon run :lint :format --affected --status=staged --no-bail'

    # Commit message validation
    commit-msg:
      - 'moon run commitlint -- $ARG1'

    # Pre-push: run tests
    pre-push:
      - 'moon run :test --affected'
```

Hook arguments are available as `$ARG1`, `$ARG2`, etc.

### constraints

Enforce project boundaries:

```yaml
constraints:
  # Enforce type relationships
  enforceProjectTypeRelationships: true

  # Tag-based constraints
  tagRelationships:
    # Projects tagged 'app' can only depend on 'lib' or 'util' tagged projects
    app: ['lib', 'util']
    # Projects tagged 'lib' can only depend on 'util' tagged projects
    lib: ['util']
    # 'util' projects cannot depend on anything
```

### pipeline

Task execution settings:

```yaml
pipeline:
  # Maximum concurrent tasks
  concurrency: 8

  # Global timeout (seconds)
  timeout: 3600

  # Batch all targets into a single action
  batchEverything: false

  # Inherit terminal colors for piped output
  inheritColorsForPipedTasks: true
```
