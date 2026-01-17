---
name: add-agents-md
description: Generate an AGENTS.md file for the current project to help Jules understand your codebase.
allowed-tools: Read, Glob, Grep, Write, Bash, AskUserQuestion
---

# Add AGENTS.md

Generate an AGENTS.md file tailored to the current project. Jules reads this file to understand how to build, test, and work with your codebase.

## Process

### 1. Check for Existing AGENTS.md

First check if AGENTS.md already exists at the project root:
- If it exists, ask the user if they want to overwrite or enhance it
- If not, proceed with generation

### 2. Analyze the Project

Detect project characteristics by examining:

**Package/Config Files:**
- `package.json` → Node.js/JavaScript/TypeScript
- `pyproject.toml`, `setup.py`, `requirements.txt` → Python
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pom.xml`, `build.gradle` → Java
- `Gemfile` → Ruby

**Build/Test Commands:**
- Extract scripts from package.json, Makefile, pyproject.toml, etc.
- Identify test frameworks (jest, pytest, cargo test, go test)
- Find lint/format commands (eslint, ruff, prettier, black)

**Project Structure:**
- Identify src/, lib/, app/, tests/ directories
- Detect monorepo patterns (workspaces, packages/)
- Find configuration files (.env.example, docker-compose.yml)

**Existing Documentation:**
- Read README.md for context
- Check for CONTRIBUTING.md, CLAUDE.md, or similar

### 3. Generate AGENTS.md

Create a concise file (~100-150 lines max) with these sections:

```markdown
# AGENTS.md

## Overview
[1-2 sentences: what this project does]

## Build & Test
[Exact commands wrapped in backticks]

## Architecture
[One paragraph: major modules and data flow]

## Code Style
[Language conventions, lint rules, patterns to follow]

## Git Workflow
[Branch naming, commit format, PR requirements]

## Important Constraints
[Security concerns, files to never modify, boundaries]
```

### 4. Validation

After writing AGENTS.md:
- Verify all listed commands are valid by checking they exist in config files
- Ensure paths referenced actually exist
- Keep it concise - link to detailed docs rather than duplicating

## Guidelines

- **Be specific**: "Run `pnpm test`" not "run tests"
- **Be concise**: Target ~100-150 lines, agents process brevity better
- **Be actionable**: Include exact commands agents can execute
- **Avoid duplication**: Link to README/docs for detailed explanations
- **Include constraints**: What agents should NOT do is as important as what they should do
