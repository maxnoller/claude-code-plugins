# Migration Guide: pre-commit to Moon Tasks

## Overview

Convert pre-commit hooks to moon tasks that can be run as VCS hooks. This gives you:
- Caching of hook results
- Consistent behavior in CI and locally
- Affected file detection
- Parallel execution

## Basic Migration

### Before (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]

  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: eslint --fix
        language: node
        types: [javascript, typescript]
```

### After

#### .moon/tasks.yml (inherited tasks)

```yaml
tasks:
  # File checks
  check-files:
    command: 'bash'
    args:
      - '-c'
      - |
        # Check for trailing whitespace
        git diff --cached --name-only | xargs -I {} sh -c 'sed -i "s/[[:space:]]*$//" "{}"'
        # Ensure files end with newline
        git diff --cached --name-only | xargs -I {} sh -c '[ -n "$(tail -c1 "{}")" ] && echo >> "{}"'
    options:
      cache: false

  # YAML validation
  check-yaml:
    command: 'python3'
    args: ['-c', 'import yaml, sys; yaml.safe_load(open(sys.argv[1]))', '*.yaml', '*.yml']
    inputs:
      - '**/*.yaml'
      - '**/*.yml'

  # JSON validation
  check-json:
    command: 'python3'
    args: ['-c', 'import json, sys; json.load(open(sys.argv[1]))', '*.json']
    inputs:
      - '**/*.json'

  # Python formatting
  format-python:
    command: 'black'
    args: ['.']
    inputs:
      - '**/*.py'

  # Python linting
  lint-python:
    command: 'ruff'
    args: ['check', '--fix', '.']
    inputs:
      - '**/*.py'

  # JavaScript/TypeScript linting
  lint-js:
    command: 'eslint'
    args: ['--fix', 'src']
    inputs:
      - 'src/**/*.{js,ts,jsx,tsx}'
```

#### .moon/workspace.yml (VCS hooks)

```yaml
vcs:
  manager: 'git'
  defaultBranch: 'main'
  hooks:
    pre-commit:
      # Run formatting and linting on staged files only
      - 'moon run :format-python :lint-python :lint-js --affected --status=staged'
  syncHooks: true
```

## Staged Files Only

Pre-commit runs on staged files. Moon can do this too:

```yaml
vcs:
  hooks:
    pre-commit:
      - 'moon run :lint :format --affected --status=staged --no-bail'
```

The `--status=staged` flag filters to only staged files.

## Running Specific Tools

### Pre-commit with file types

```yaml
# .pre-commit-config.yaml
- id: black
  types: [python]
```

### Moon equivalent

Use language-specific task files:

```yaml
# .moon/tasks/python.yml
tasks:
  format:
    command: 'black'
    args: ['.']
    inputs:
      - '**/*.py'

  lint:
    command: 'ruff check --fix .'
    inputs:
      - '**/*.py'
```

Then in workspace:

```yaml
vcs:
  hooks:
    pre-commit:
      - 'moon run :format :lint --affected --status=staged'
```

## Custom Hooks

### Pre-commit local hook

```yaml
- repo: local
  hooks:
    - id: custom-check
      name: Custom Check
      entry: ./scripts/check.sh
      language: script
```

### Moon equivalent

```yaml
tasks:
  custom-check:
    command: './scripts/check.sh'
    inputs:
      - 'src/**/*'
    options:
      cache: false
```

## Commit Message Validation

### Pre-commit

```yaml
- repo: https://github.com/commitizen-tools/commitizen
  hooks:
    - id: commitizen
      stages: [commit-msg]
```

### Moon

```yaml
# .moon/tasks.yml
tasks:
  commitlint:
    command: 'npx'
    args: ['commitlint', '--edit']
    options:
      cache: false

# .moon/workspace.yml
vcs:
  hooks:
    commit-msg:
      - 'moon run :commitlint -- $ARG1'
```

## Parallel Execution

Pre-commit runs hooks sequentially by default. Moon runs tasks in parallel:

```yaml
vcs:
  hooks:
    pre-commit:
      # These run in parallel automatically
      - 'moon run :lint-js :lint-python :format --affected --status=staged'
```

## Fallback: Keep pre-commit

If you have complex pre-commit setup, you can keep it and run via moon:

```yaml
vcs:
  hooks:
    pre-commit:
      - 'pre-commit run --from-ref HEAD~1 --to-ref HEAD'
      # Or run moon tasks after
      - 'moon run :typecheck --affected'
```

## Tips

1. **Use `--no-bail`** - Continue running other checks even if one fails
2. **Use `--status=staged`** - Only check staged files
3. **Use `--affected`** - Only run tasks for changed projects
4. **Install tools via toolchain** - Ensure consistent versions
5. **Keep hooks fast** - Use caching and affected detection
