---
inclusion: always
---

# SuperKiro Steering

Lightweight, always-included guides that you target by file path (and optional hashtag triggers).

- Include all files in this folder in the system/context using the `inclusion: always` front matter.
- Primary usage: reference the steering file explicitly in your message.
  - Example: `Use .kiro/steering/commands/sk_document.md src/api --type api --style detailed`
- Hashtag triggers: `#sk_<name>` or `#sk:<name>` at message start selects the corresponding steering file.
  - Example: `#sk_document src/api --type api --style detailed`
  - Mapping: `#sk_<name>` → `.kiro/steering/commands/sk_<name>.md`
  - Tokenization: split on spaces; support quoted segments ("...") for paths with spaces.
  - Behavior: Treat the remainder of the message as arguments to the steering behavior.
- Transparency: Always state consulted file, e.g., `Consulted .kiro/steering/commands/sk_document.md`.
- Flags announcement: If global flags are present (e.g., `--ultrathink`), announce them immediately after the consulted line, e.g., `Applied flags: --ultrathink`.

## Command Files

Command files live under `.kiro/steering/commands/` and are named `sk_<name>.md`.
- Mapping: `<name>` → `.kiro/steering/commands/sk_<name>.md`
- Examples: `sk_document.md`, `sk_analyze.md`, `sk_explain.md`, `sk_improve.md`, etc.

## Global Flags & Rules

Use these flags with any command file under `.kiro/steering/commands/`. Apply definitions exactly as documented; do not infer unspecified behavior.

Analysis Depth
- `--think`: Structured analysis (~4K tokens).
- `--think-hard`: Deep analysis (~10K tokens).
- `--ultrathink`: Maximum depth (~32K tokens).

MCP Control
- `--all-mcp`: Enable all MCP servers.
- `--no-mcp`: Disable all MCP servers (overrides others).
- Individual servers: `--seq` (Sequential), `--c7` (Context7), `--magic` (UI/Magic), `--play` (Playwright), `--morph` (Morphllm), `--serena` (Memory/Symbols).

Safety & Execution
- `--safe-mode`: Maximum validation; auto-enables `--uc` and `--validate`.
- `--validate`: Pre-execution checks and risk assessment.
- `--loop`: Iterative improvement cycles; combine with `--iterations N`.
- `--concurrency N`: Parallel operations (1–15).

Output Optimization
- `--uc` / `--ultracompressed`: 30–50% token reduction with symbol-enhanced communication.

Flag Handling Protocol
- Detect global flags in the message args (e.g., `--think`, `--c7`).
- Announce application: print `Applied flags: <flags>` right after the consulted line.
- Apply behaviors exactly as documented (SuperClaude/Core/FLAGS.md, Docs/User-Guide/flags.md). Do not infer extra effects beyond explicit policy.

Flag Priority Rules
- Safety first: `--safe-mode` > `--validate` > optimization flags.
- Explicit override: User-provided flags take precedence over auto-activation.
- Depth hierarchy: `--ultrathink` > `--think-hard` > `--think`.
- MCP control: `--no-mcp` overrides all individual MCP flags.

Flag Interactions
- Compatible: `--think` + `--c7`; `--magic` + `--play`; `--serena` + `--morph`; `--safe-mode` + `--validate`; `--loop` + `--validate`.
- Conflicts: `--all-mcp` vs individual MCP flags (prefer one); `--no-mcp` vs any MCP flags (no-mcp wins); `--safe` vs `--aggressive`; `--quiet` vs `--verbose`.
- Auto-relationships: Use only those explicitly documented by the framework or command. Do not auto-enable MCP servers from depth flags. If policy states `--safe-mode` implies `--uc` (and/or `--validate`), announce and apply accordingly.

 
