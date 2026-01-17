# Moon Plugin for Claude Code

Comprehensive moonrepo/moon knowledge for monorepo management, task running, and CI/CD integration.

## Features

### Skill: moon-knowledge
Deep knowledge about moon configuration, tasks, workspace setup, CI/CD integration, optimization, and proto toolchain integration.

### Commands

| Command | Description |
|---------|-------------|
| `/moon:init` | Initialize moon in a project (toolchain, CI, workspace setup) |
| `/moon:add-project` | Add a new project to the workspace |
| `/moon:add-task` | Add a new task to a project |
| `/moon:migrate` | Migrate from other task runners (npm, turbo, Make, pre-commit) |
| `/moon:optimize` | Analyze and optimize moon performance |
| `/moon:diagnose` | Troubleshoot and fix moon issues |

### Agents

| Agent | Trigger |
|-------|---------|
| `moon-config-reviewer` | Proactively reviews moon config files after edits |
| `moon-workspace-architect` | Helps design workspace structure and organization |

### Scripts

- `verify-config.sh` - Validate moon configuration files (YAML syntax, schema, moon check)

## Installation

```bash
# Test locally
claude --plugin-dir /path/to/moon

# Or add to your project's .claude-plugin directory
```

## Usage

### Skill Triggers

The moon-knowledge skill activates automatically when you mention:
- "moon", "moonrepo"
- "monorepo with moon"
- ".moon/", "moon.yml", "workspace.yml"
- "proto toolchain"
- "moon task", "moon ci"

### Commands

Commands are available via slash syntax:
```
/moon:init                      # Initialize moon in current project
/moon:add-project my-service    # Add a new project
/moon:add-task build            # Add a task to current project
/moon:migrate                   # Migrate from npm/turbo/Make/pre-commit
/moon:optimize                  # Analyze and optimize performance
/moon:diagnose                  # Troubleshoot issues
```

### Agents

**moon-config-reviewer** triggers automatically after editing:
- `moon.yml`
- `.moon/workspace.yml`
- `.moon/toolchain.yml`
- `.moon/tasks.yml`
- `.prototools`

**moon-workspace-architect** is invoked when discussing:
- Monorepo structure design
- Project organization
- Dependency planning

### Verification Script

Run the verification script to validate moon configuration:
```bash
./scripts/verify-config.sh /path/to/workspace
```

## Knowledge Coverage

The plugin provides comprehensive knowledge about:

- **Configuration**: workspace.yml, toolchain.yml, tasks.yml, moon.yml
- **Tasks**: inputs, outputs, dependencies, caching, presets
- **CI/CD**: GitHub Actions, GitLab CI integration
- **Proto**: Toolchain version management
- **VCS Hooks**: Git hooks, pre-commit integration
- **Migration**: From npm scripts, Turborepo, Makefile, pre-commit
- **Optimization**: Caching strategies, affected detection, parallelization
