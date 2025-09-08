---
inclusion: manual
---

Note (Kiro): Use `.kiro/steering/commands/sk_git.md <operation> [--smart-commit] [--interactive]`. In responses, state: `Consulted .kiro/steering/commands/sk_git.md`.

---
name: git
description: "Git Operations"
category: utility
complexity: basic
mcp-servers: []
personas: []
---

# #sk_git - Git Operations

## Triggers
- Commit message generation and staging assistance
- Branch management, merging, and conflict resolution guidance
- History analysis and blame navigation support
- Release tagging and changelog preparation

## Usage
```
#sk_git [operation] [--smart-commit] [--interactive]
```

## Behavioral Flow
1. Analyze repository state and pending changes
2. Propose clear, conventional commit messages or release notes
3. Guide safe operations (branch, merge, rebase) with recovery steps
4. Summarize results and next recommended actions

Key behaviors:
- Conventional messages and semantic versioning suggestions
- Safety-first conflict handling and rollback advice
- Minimal, auditable command sequences
