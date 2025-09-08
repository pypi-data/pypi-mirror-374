---
inclusion: manual
---



# #sk_load - Project Context Loading

## Triggers
- Session initialization and project context loading requests
- Cross-session persistence and memory retrieval needs
- Project activation and context management requirements
- Session lifecycle management and checkpoint loading scenarios

## Usage
```
#sk_load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]
```

## Behavioral Flow
1. Initialize: Establish Serena MCP connection and session context management
2. Discover: Analyze project structure and identify context loading requirements
3. Load: Retrieve project memories, checkpoints, and cross-session persistence data
4. Activate: Establish project context and prepare for development workflow
5. Validate: Ensure loaded context integrity and session readiness

Key behaviors:
- Serena MCP integration for memory management and cross-session persistence
- Project activation with comprehensive context loading and validation
- Performance-critical operation with <500ms initialization target
- Session lifecycle management with checkpoint and memory coordination

## MCP Integration
- Serena MCP: Mandatory integration for project activation, memory retrieval, and session management
- Memory Operations: Cross-session persistence, checkpoint loading, and context restoration
- Performance Critical: <200ms for core operations, <1s for checkpoint creation

## Tool Coordination
- activate_project: Core project activation and context establishment
- list_memories/read_memory: Memory retrieval and session context loading
- Read/Grep/Glob: Project structure analysis and configuration discovery
- Write: Session context documentation and checkpoint creation

## Key Patterns
- Project Activation: Directory analysis → memory retrieval → context establishment
- Session Restoration: Checkpoint loading → context validation → workflow preparation
- Memory Management: Cross-session persistence → context continuity → development efficiency
- Performance Critical: Fast initialization → immediate productivity → session readiness
