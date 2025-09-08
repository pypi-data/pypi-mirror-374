---
inclusion: manual
---

Note (Kiro): Use `.kiro/steering/commands/sk_save.md [--type session|learnings|context|all] [--summarize] [--checkpoint]` or `#sk_save …`. State: `Consulted .kiro/steering/commands/sk_save.md`.

# #sk_save - Session Context Persistence

## Triggers
- Session completion and project context persistence needs
- Cross-session memory management and checkpoint creation requests
- Project understanding preservation and discovery archival scenarios
- Session lifecycle management and progress tracking requirements

## Usage
```
#sk_save [--type session|learnings|context|all] [--summarize] [--checkpoint]
```

## Behavioral Flow
1. Analyze: Examine session progress and identify discoveries worth preserving
2. Persist: Save session context and learnings using Serena MCP memory management
3. Checkpoint: Create recovery points for complex sessions and progress tracking
4. Validate: Ensure session data integrity and cross-session compatibility
5. Prepare: Ready session context for seamless continuation in future sessions

Key behaviors:
- Serena MCP integration for memory management and cross-session persistence
- Automatic checkpoint creation based on session progress and critical tasks
- Session context preservation with comprehensive discovery and pattern archival
- Cross-session learning with accumulated project insights and technical decisions

## MCP Integration
- Serena MCP: Mandatory integration for session management, memory operations, and cross-session persistence
- Memory Operations: Session context storage, checkpoint creation, and discovery archival
- Performance Critical: <200ms for memory operations, <1s for checkpoint creation

## Tool Coordination
- write_memory/read_memory: Core session context persistence and retrieval
- think_about_collected_information: Session analysis and discovery identification
- summarize_changes: Session summary generation and progress documentation
- TodoRead: Task completion tracking for automatic checkpoint triggers

## Key Patterns
- Session Preservation: Discovery analysis → memory persistence → checkpoint creation
- Cross-Session Learning: Context accumulation → pattern archival → enhanced project understanding
- Progress Tracking: Task completion → automatic checkpoints → session continuity
- Recovery Planning: State preservation → checkpoint validation → restoration readiness

