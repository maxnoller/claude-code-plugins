# Claude Code Architecture & Design Patterns (Early 2026)

> A comprehensive analysis of the design patterns and extensibility architectures used in Anthropic's Claude Code, based on official documentation, GitHub sources, and community research. Last updated: February 2026.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Skills System](#1-skills-system)
3. [Subagents (Custom Agents)](#2-subagents-custom-agents)
4. [Agent Teams (Multi-Session Orchestration)](#3-agent-teams-multi-session-orchestration)
5. [Hooks System](#4-hooks-system)
6. [Plugins](#5-plugins)
7. [Memory & Configuration Hierarchy](#6-memory--configuration-hierarchy)
8. [MCP (Model Context Protocol) Integration](#7-mcp-model-context-protocol-integration)
9. [Permission & Security Model](#8-permission--security-model)
10. [Key Design Patterns Summary](#key-design-patterns-summary)

---

## Architecture Overview

Claude Code (GA May 2025) is Anthropic's terminal-native AI coding agent. By early 2026 it has evolved into a **full agent platform** with a layered extensibility architecture:

```
┌───────────────────────────────────────────────────────┐
│                    Agent Teams                         │
│         (Multi-session orchestration via tmux)         │
├──────────┬──────────┬──────────┬──────────────────────┤
│ Subagent │ Subagent │ Subagent │   Lead Agent          │
│ (Explore)│ (Plan)   │ (Custom) │   (Main Session)      │
├──────────┴──────────┴──────────┴──────────────────────┤
│                     Skills Layer                       │
│          (SKILL.md + progressive disclosure)           │
├───────────────────────────────────────────────────────┤
│                     Hooks Engine                       │
│    (17 lifecycle events × 3 handler types)             │
├───────────────────────────────────────────────────────┤
│                     Plugins                            │
│  (Composable bundles: skills + agents + hooks + MCP)   │
├───────────────────────────────────────────────────────┤
│          MCP Servers │ LSP Servers │ Tools              │
├───────────────────────────────────────────────────────┤
│         Permission & Security Layer                    │
│   (Tiered permissions, sandboxing, settings cascade)   │
├───────────────────────────────────────────────────────┤
│              CLAUDE.md / Memory                        │
│       (Project context, conventions, rules)            │
└───────────────────────────────────────────────────────┘
```

### Core Design Philosophy

| Principle | Description |
|---|---|
| **Progressive Disclosure** | Only load what's needed — skill names/descriptions (~50-100 tokens) pre-loaded, full instructions loaded on demand |
| **Convention over Configuration** | File-system conventions (folder structure, naming) replace complex config APIs |
| **Composability** | Small, focused components (skills, hooks, agents) compose into larger systems (plugins, teams) |
| **Hierarchical Scope** | Everything cascades: managed → user → project → local → CLI args |
| **Security by Default** | Read-only default, explicit permission escalation at every layer |

---

## 1. Skills System

**Pattern: Filesystem-as-API with Progressive Disclosure**

Skills are the fundamental unit of extensibility — structured folders of instructions, scripts, and resources that extend Claude's capabilities for specialized tasks.

### Architecture

```
skills/
└── <skill-name>/
    ├── SKILL.md           # Required — instructions + YAML frontmatter
    ├── reference.md       # Optional — detailed docs, loaded on demand
    ├── examples/
    │   └── sample.md      # Optional — example outputs
    ├── templates/
    │   └── template.md    # Optional — templates for Claude to fill in
    └── scripts/
        └── helper.sh      # Optional — executable utilities
```

### SKILL.md Frontmatter Schema

```yaml
---
name: my-skill                    # Identifier, also defines /slash-command
description: What this skill does # Used for auto-invocation matching
argument-hint: "[issue-number]"   # Hint shown in UI
disable-model-invocation: true    # Only user can invoke (not Claude)
user-invocable: false             # Only Claude can invoke (not user)
allowed-tools: Read, Grep, Glob   # Restrict tool access
model: haiku                      # Override model for this skill
context: fork                     # Run in isolated subagent context
agent: Explore                    # Which agent profile to use
hooks:                            # Lifecycle hooks specific to this skill
  PostToolUse: [...]
---
```

### Key Design Patterns

#### a) Progressive Disclosure Pattern

Claude pre-loads only skill `name` and `description` (~50-100 tokens per skill) into its system prompt. Full `SKILL.md` content is loaded only when the skill is relevant to the current task. Supporting files (`reference.md`, `examples/`) are loaded only when Claude navigates to them via markdown links.

```
Pre-loaded:     name + description    (~50 tokens)
On invocation:  SKILL.md body         (~500-2000 tokens)
On demand:      reference.md, etc.    (loaded via links)
```

#### b) Invocation Control Pattern

Two independent flags control who can trigger a skill:

| Flag | User Can Invoke | Claude Can Invoke | Use Case |
|---|---|---|---|
| (default) | ✅ via `/name` | ✅ automatically | General-purpose skills |
| `disable-model-invocation: true` | ✅ via `/name` | ❌ | Dangerous ops: `/deploy`, `/commit` |
| `user-invocable: false` | ❌ | ✅ automatically | Background knowledge, context-only |

#### c) Dynamic Context Injection Pattern

Skills can embed shell command output directly at load time using the `!` prefix:

```markdown
---
name: pr-summary
description: Summarize a PR
context: fork
agent: Explore
---
## PR Context  
- PR diff: !`gh pr diff`
- Comments: !`gh pr view --comments`  
- Files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

The `!command` syntax executes immediately before Claude processes the prompt. Output replaces the placeholder inline.

#### d) Scope Hierarchy Pattern

Skills resolve from multiple directories in priority order:

| Scope | Location | Shared? |
|---|---|---|
| **Managed** | System-wide (set by IT) | Organization-wide |
| **User** | `~/.claude/skills/<name>/` | Personal, all projects |
| **Project** | `.claude/skills/<name>/` | Team via VCS |
| **Plugin** | `<plugin>/skills/<name>/` | Via plugin distribution |
| **Nested Discovery** | `packages/*/skills/<name>/` | Auto-discovered in monorepos |

---

## 2. Subagents (Custom Agents)

**Pattern: Isolated Execution Contexts with Declarative Configuration**

Subagents are specialized AI instances that run in isolated context windows with their own model, tools, permissions, and memory.

### Built-in Subagents

| Agent | Model | Tools | Purpose |
|---|---|---|---|
| **Explore** | Haiku (fast) | Read-only | File discovery, codebase exploration |
| **Plan** | Inherited | Read-only | Codebase research for planning |
| **General-purpose** | Inherited | All tools | Complex research, code modifications |

### Custom Agent File Structure

```
.claude/agents/<agent-name>.md    # Project scope
~/.claude/agents/<agent-name>.md  # User scope
<plugin>/agents/<agent-name>.md   # Plugin scope
```

### Agent Frontmatter Schema

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep, Bash           # Allowed tools
disallowedTools: Write, Edit             # Explicitly denied tools
model: sonnet                            # Model override (sonnet/opus/haiku/inherit)
permissionMode: default                  # default|acceptEdits|dontAsk|bypassPermissions|plan
maxTurns: 50                             # Max conversation turns
skills:                                  # Pre-loaded skills
  - api-conventions
  - error-handling-patterns
mcpServers: ["slack"]                    # MCP server access
hooks:                                   # Per-agent lifecycle hooks
  PreToolUse: [...]
memory: user                             # Persistent memory (user|project|local)
background: true                         # Run as background task
isolation: worktree                      # Git worktree isolation
---
You are a code reviewer. Focus on quality, security, and best practices.
```

### Key Design Patterns

#### a) Context Isolation Pattern

Each subagent operates with a completely fresh context window. This prevents context pollution from the main conversation and allows enforcing different constraints per agent.

```
Main Conversation ──→ Spawn Subagent ──→ Fresh Context
                         │                   │
                         ├── Own model        │
                         ├── Own tools        │
                         ├── Own permissions  │
                         └── Own memory       │
                                             ├── Execute task
                                             └── Return summary ──→ Main Conversation
```

#### b) Agent Composition Pattern

Agents can restrict which _other_ agents they spawn using the `Task(agent_type)` tool specification:

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Task(worker, researcher), Read, Bash
---
```

This creates a hierarchical delegation chain where a coordinator agent can only spawn `worker` and `researcher` subagents.

#### c) Persistent Memory Pattern

Agents can maintain memory across sessions at three scopes:

| Scope | Location | Use Case |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project preferences |
| `project` | `.claude/agent-memory/<name>/` | Project-specific patterns |
| `local` | `.claude/agent-memory-local/<name>/` | Personal, uncommitted |

The agent's system prompt automatically includes the first 200 lines of `MEMORY.md` from the memory directory. The agent curates this file as it works, accumulating knowledge over time.

#### d) Foreground/Background Execution Pattern

| Mode | Behavior | Permission Handling |
|---|---|---|
| **Foreground** | Blocks main conversation | Permission prompts passed through to user |
| **Background** | Runs concurrently | Permissions pre-approved at launch; unapproved tools auto-denied |

Background agents can be launched explicitly ("run this in the background") or converted mid-execution with `Ctrl+B`.

---

## 3. Agent Teams (Multi-Session Orchestration)

**Pattern: Lead-Teammate Architecture with Shared Task Queue**

Agent Teams are a **February 2026** feature (research preview) that coordinates multiple full Claude Code sessions running in parallel via tmux.

### Architecture

```
┌───────────────────────────────────────────────┐
│                   Lead Agent                   │
│        (Main session, orchestrates team)       │
│                                                │
│  Tools: message(teammate), broadcast(all),     │
│         assign_task, claim_task                 │
├────────┬────────┬────────┬────────────────────┤
│  tmux  │  tmux  │  tmux  │                    │
│ session│ session│ session│                    │
│        │        │        │                    │
│Teammate│Teammate│Teammate│   Shared State:    │
│   A    │   B    │   C    │   ~/.claude/teams/ │
│        │        │        │   ~/.claude/tasks/ │
└────────┴────────┴────────┴────────────────────┘
```

### Key Differences from Subagents

| Aspect | Subagents | Agent Teams |
|---|---|---|
| **Process model** | Same process, forked context | Separate tmux sessions |
| **Context** | Independent window, returns summary | Independent sessions, message-based comms |
| **Scale** | 1-3 concurrent tasks | 2-8+ parallel teammates |
| **Communication** | Result returned to parent | `message`, `broadcast`, shared task list |
| **Isolation** | Shared filesystem | Can use git worktrees |
| **Token cost** | Shared API session | Each teammate has own session |

### Communication Patterns

- **Message**: Direct 1-to-1 for specific teammate instructions
- **Broadcast**: Send to all teammates (cost scales with team size)
- **Shared Task Queue**: `~/.claude/tasks/<team-name>/` — agents assign and claim tasks
- **Idle Notifications**: Automatic notify when teammate finishes
- **TeammateIdle Hook**: Lead can react programmatically when agents complete

### Use Cases

- **Parallel code review**: Multiple reviewers on different modules simultaneously
- **Competing hypotheses**: Different teammates test different debug theories
- **Cross-layer work**: Frontend/backend/tests each owned by a different teammate
- **New features**: Each teammate owns a separate piece of a feature

---

## 4. Hooks System

**Pattern: Event-Driven Middleware Pipeline**

Hooks are automated handlers that execute at predefined lifecycle points, providing deterministic control over Claude Code's behavior. This is analogous to git hooks or web middleware.

### 17 Lifecycle Events

| Event | Fires When | Typical Use |
|---|---|---|
| `SessionStart` | Session begins or resumes | Environment setup, context injection |
| `SessionEnd` | Session ends | Cleanup, logging |
| `UserPromptSubmit` | User submits a prompt | Prompt validation, rewriting |
| `PreToolUse` | Before a tool call | Security validation, blocking dangerous commands |
| `PostToolUse` | After successful tool call | Auto-formatting, running tests, logging |
| `PostToolUseFailure` | Tool call fails | Error handling, retry logic |
| `PermissionRequest` | Permission dialog would appear | Auto-approve/deny based on policy |
| `Notification` | Claude sends an alert | Custom notification routing |
| `SubagentStart` | Subagent is spawned | Tracking, resource allocation |
| `SubagentStop` | Subagent completes | Result processing |
| `Stop` | Claude finishes responding | Notifications, Git push, CI trigger |
| `TeammateIdle` | Agent team member finishes | Task reassignment |
| `TaskCompleted` | Task marked complete | Status updates, deployment triggers |
| `ConfigChange` | Settings are modified | Config validation |
| `WorktreeCreate` | Git worktree created | Build setup |
| `WorktreeRemove` | Git worktree removed | Cleanup |
| `PreCompact` | Before context compaction | Memory preservation |

### Three Handler Types

Hooks support three execution mechanisms:

#### 1. Command Hooks (Shell Scripts)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool": "Bash" },
        "handler": {
          "type": "command",
          "command": "./scripts/validate-command.sh"
        }
      }
    ]
  }
}
```

- Execute shell commands synchronously or asynchronously
- Receive JSON input via stdin (tool name, input, session context)
- Control flow via exit codes: `0` = allow, `2` = block, `3` = skip remaining hooks
- Can return JSON on stdout to modify tool inputs/outputs

#### 2. Prompt Hooks (LLM Evaluation)

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": {},
        "handler": {
          "type": "prompt",
          "prompt": "Review the changes made. Are they correct and complete? Return {\"decision\": \"allow\"} or {\"decision\": \"block\", \"reason\": \"...\"}"
        }
      }
    ]
  }
}
```

- Uses an LLM call to evaluate the current state
- Receives full hook context (conversation, tool state)
- Returns structured JSON decisions
- Available for: `PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit`, and 4 more events

#### 3. Agent Hooks (Subagent Evaluation)

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "matcher": {},
        "handler": {
          "type": "agent",
          "agent": "quality-checker"
        }
      }
    ]
  }
}
```

- Spawns a full subagent to evaluate and act
- Agent has access to its own tools and context
- Most powerful hook type — can perform multi-step analysis

### Hook Resolution Pipeline

```
Event Fires → Collect All Matching Hooks (from all scopes)
            → Sort by Priority
            → Execute Sequentially
            → First "block" result stops pipeline
            → "allow" continues to next hook
            → All hooks pass → proceeds normally
```

### Async Hooks Pattern

Hooks can run in the background without blocking Claude's workflow:

```json
{
  "handler": {
    "type": "command",
    "command": "npm test",
    "async": true,
    "timeout": 120000
  }
}
```

Background hooks for running tests, linting, or other long processes without interrupting the main agent flow.

---

## 5. Plugins

**Pattern: Composable Extension Bundles**

Plugins are the top-level distribution unit that bundles all other primitives (skills, agents, hooks, MCP servers, LSP servers, settings) into a single, shareable package.

### Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (required)
├── skills/
│   └── code-review/
│       └── SKILL.md         # Plugin skills
├── agents/
│   └── security-reviewer.md # Plugin agents
├── hooks/
│   └── hooks.json           # Plugin hooks
├── .mcp.json                # MCP server configurations
├── .lsp.json                # LSP server configurations
└── settings.json            # Default settings (e.g., default agent)
```

### plugin.json Manifest

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Description of the plugin"
}
```

### Key Design Patterns

#### a) Namespace Isolation Pattern

Plugin skills are automatically namespaced: `/plugin-name:skill-name`. This prevents conflicts when multiple plugins are loaded.

```
Project: /review        → .claude/skills/review/SKILL.md
Plugin:  /my-plugin:review → plugins/my-plugin/skills/review/SKILL.md
```

#### b) Composable Configuration Pattern

Each component inside a plugin follows the same conventions as standalone `.claude/` configurations. Migration between standalone and plugin is straightforward:

| Standalone | Plugin Equivalent |
|---|---|
| `.claude/skills/` | `<plugin>/skills/` |
| `.claude/agents/` | `<plugin>/agents/` |
| `.claude/settings.json` | `<plugin>/settings.json` |
| `.claude/hooks.json` | `<plugin>/hooks/hooks.json` |
| `.mcp.json` | `<plugin>/.mcp.json` |

#### c) Default Agent Pattern

Plugins can ship a default agent via `settings.json`:

```json
{ "agent": "security-reviewer" }
```

When the plugin is active, Claude uses `security-reviewer` (from `agents/`) as the default agent, changing the overall behavior of the session.

---

## 6. Memory & Configuration Hierarchy

**Pattern: Cascading Settings with Scope Precedence**

### CLAUDE.md — Project Memory

`CLAUDE.md` serves as Claude's "persistent memory and rule book" for a project:

```
project-root/
├── CLAUDE.md                    # Main project context
├── packages/
│   └── frontend/
│       └── CLAUDE.md            # Directory-specific overrides
└── .claude/
    ├── settings.json            # Project settings (VCS)
    ├── settings.local.json      # Personal settings (gitignored)
    └── rules/                   # Split rules pattern
        ├── profile.md
        ├── preferences.md
        └── decisions.md
```

Best practices from Anthropic:
- **Keep CLAUDE.md under ~120 lines** — Claude reliably follows ~100-150 custom instructions
- **Use split files** for complex projects — smaller focused files in `.claude/rules/`
- **Pointers, not copies** — CLAUDE.md routes to other docs via links
- **Directory-specific overrides** — subdirectory CLAUDE.md files take precedence

### Settings Cascade

Settings resolve in strict precedence order (highest to lowest):

```
1. Managed Settings     /etc/claude-code/managed-settings.json     (IT/org-wide)
2. User Settings        ~/.claude/settings.json                     (personal)
3. Project Settings     .claude/settings.json                       (team, in VCS)
4. Local Settings       .claude/settings.local.json                 (personal, gitignored)
5. CLI Arguments        --model, --agent, etc.                      (per-session)
```

More specific scopes override broader ones. Managed settings always have highest priority (for compliance/policy).

---

## 7. MCP (Model Context Protocol) Integration

**Pattern: Standardized Tool Protocol**

MCP is an open protocol connecting Claude to external tools and data sources. Claude Code natively supports MCP server configuration.

### Configuration

```json
// .mcp.json (project root or plugin root)
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_TOKEN": "..." }
  },
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": { "DATABASE_URL": "..." }
  }
}
```

### MCP in Subagents

Subagents can have dedicated MCP server access:

```yaml
---
name: data-analyst
description: Analyze data from our databases
mcpServers: ["postgres", "analytics"]
---
```

> **Note**: MCP tools are **not available** in background subagents (due to lifecycle management).

### Key MCP Servers in the Ecosystem (Early 2026)

| Server | Purpose |
|---|---|
| GitHub MCP | Repository management, PRs, issues |
| PostgreSQL MCP | Natural language SQL queries |
| Slack MCP | Conversation summaries, alerts |
| Playwright MCP | Browser testing automation |
| Context7 MCP | Up-to-date API documentation |
| Filesystem MCP | Sandboxed file access |

---

## 8. Permission & Security Model

**Pattern: Defense-in-Depth with Progressive Trust**

### Permission Tiers

```
┌─────────────────────────────────────────┐
│  Managed Policies (IT/Organization)      │  ← Cannot be overridden
├─────────────────────────────────────────┤
│  Permission Rules (settings.json)        │  ← allow/ask/deny rules
│  ┌─────────────────────────────────┐    │
│  │  allow: [Read, Grep, Glob]      │    │
│  │  ask:   [Write, Edit, Bash(*)]  │    │
│  │  deny:  [Bash(rm -rf *)]        │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│  Sandbox (OS-level enforcement)          │  ← Filesystem & network isolation
├─────────────────────────────────────────┤
│  Hooks (PreToolUse validation)           │  ← Custom security logic
└─────────────────────────────────────────┘
```

### Permission Modes

| Mode | Behavior |
|---|---|
| `default` | Ask for approval on write/execute operations |
| `acceptEdits` | Auto-accept file edits, ask for other ops |
| `plan` | Read-only, no execution |
| `dontAsk` | Auto-deny unless pre-approved |
| `bypassPermissions` | Skip all checks (⚠️ controlled environments only) |

### Sandboxing (Late 2025)

OS-level filesystem and network isolation for the `bash` tool:
- Restricts filesystem access to approved directories
- Controls network access
- Isolates prompt injection attempts
- Reduces permission prompt frequency by allowing safe operations within boundaries

### Tool-Level Granularity

Permission rules support glob patterns for fine-grained control:

```
Bash(npm test)       # Allow specific commands
Bash(git *)          # Allow all git operations
Skill(deploy *)      # Control skill invocation
Task(researcher)     # Control subagent spawning
```

---

## Key Design Patterns Summary

### 1. **Filesystem-as-API**
Everything is a file. Skills are folders with `SKILL.md`. Agents are markdown files with YAML frontmatter. Hooks are JSON. No compiled plugins, no SDK — just files the agent can discover and read.

### 2. **Progressive Disclosure**
Information is loaded in layers: metadata first, then full content, then supporting files. This keeps token usage efficient and prevents context pollution.

### 3. **Declarative Configuration with YAML Frontmatter**
Both skills and agents use the same YAML frontmatter + markdown body pattern. Configuration is human-readable and version-controllable.

### 4. **Hierarchical Scope Resolution**
Every primitive (settings, skills, agents, hooks, memory) resolves through a managed → user → project → local → CLI cascade. This enables organization-wide policy enforcement while preserving developer autonomy.

### 5. **Composition over Inheritance**
Plugins compose primitives without creating dependencies between them. A skill can be standalone, part of a project, or part of a plugin — the format is identical.

### 6. **Event-Driven Middleware**
The hooks system applies the middleware/interceptor pattern from web frameworks to AI agent lifecycle. Each hook is a filter in a pipeline that can inspect, modify, or block operations.

### 7. **Isolation by Default**
Subagents get fresh contexts. Background tasks get pre-approved permissions. Agent teams run in separate tmux processes. This prevents unintended cross-contamination of context and state.

### 8. **Convention over Configuration**
Discovery is automatic: drop a `SKILL.md` in the right folder and it works. No registration, no imports, no build step. The agent SDK is "create a markdown file."

### 9. **Agent Skills as an Open Standard**
Published at [agentskills.io](https://agentskills.io), the skill format is designed for portability across AI platforms — not locked to Claude Code. Other tools (Cursor, VS Code agents) can adopt the same format.

### 10. **Lead-Teammate Architecture for Multi-Agent**
Agent teams use a clear hierarchy: one lead orchestrates, teammates execute. Communication is message-based (not shared context), and a shared task queue enables work distribution and load balancing.

---

## Timeline of Key Architectural Releases

| Date | Feature | Significance |
|---|---|---|
| **Feb 2025** | Claude Code research preview | Terminal-native agent launch |
| **May 2025** | Claude Code GA + Claude 4 | General availability |
| **Oct 2025** | Agent Skills introduced | Filesystem-as-API extensibility pattern |
| **Nov 2025** | Sandboxing | OS-level security isolation |
| **Dec 2025** | Skills as open standard | agentskills.io, org-wide deployment |
| **Jan 2026** | Cowork (GUI Claude Code) | Non-developer agent interface |
| **Jan 2026** | Hooks system (15→17 events) | Full lifecycle control with prompt/agent hooks |
| **Feb 2026** | Agent Teams (research preview) | Multi-session parallel orchestration |
| **Feb 2026** | Plugins architecture | Composable extension bundles |
| **Feb 2026** | Claude Opus 4.6 + Agent Teams | Agent teams in research preview |

---

## Sources

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills) (Anthropic, 2026)
- [Claude Code Hooks Reference](https://docs.anthropic.com/en/docs/claude-code/hooks) (Anthropic, 2026)
- [Claude Code Sub-Agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) (Anthropic, 2026)
- [Claude Code Plugins](https://docs.anthropic.com/en/docs/claude-code/plugins) (Anthropic, 2026)
- [Agent Teams Orchestration](https://docs.anthropic.com/en/docs/claude-code/agent-teams) (Anthropic, 2026)
- [Agent Skills Open Standard](https://agentskills.io) (Anthropic, 2025)
- [Claude Code Permissions & Settings](https://docs.anthropic.com/en/docs/claude-code/settings) (Anthropic, 2026)
- Anthropic Blog Posts on Claude Code autonomy metrics (Jan 2026)
- Simon Willison's analysis of Agent Skills (Oct 2025)
- Community research and GitHub ecosystem analysis
