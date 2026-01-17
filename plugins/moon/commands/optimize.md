---
description: Analyze and optimize moon configuration for better performance
argument-hint: "[project]"
allowed-tools: ["Task"]
---

# Optimize Moon Performance

## Delegation

### Spawn Config Reviewer

Use the Task tool to spawn the `moon:moon-config-reviewer` agent with:

**Task prompt:**
```
Analyze and optimize the moon configuration for performance.

Target Project: $ARGUMENTS (if empty, analyze entire workspace)

Instructions:
1. Review workspace and project configurations
2. Look for performance bottlenecks (missing caching, parallelization issues)
3. Check for CI optimization opportunities
4. Suggest specific improvements
```
