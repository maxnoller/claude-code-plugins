---
description: Troubleshoot and fix moon configuration issues
argument-hint: "[issue-description]"
allowed-tools: ["Task", "Bash"]
---

# Diagnose Moon Issues

## Context Gathering

### 1. Run Moon Check
!`moon check`

## Delegation

### 2. Spawn Config Reviewer

Use the Task tool to spawn the `moon:moon-config-reviewer` agent with:

**Task prompt:**
```
Diagnose the following moon configuration/issue:

User Input: $ARGUMENTS

Context (moon check):
[Insert output from step 1]

Instructions:
1. Analyze the issue or configuration
2. If specific errors are present, explain the root cause
3. Suggest or apply fixes
4. Verify the resolution
```
