---
inclusion: manual
---



---
name: index
description: "Generate project indexes and documentation with intelligent organization"
category: utility
complexity: standard
mcp-servers: [sequential, context7]
personas: [scribe, quality, architect]
---

# #sk_index - Project Documentation

## Triggers
- Project structure documentation and navigable index generation
- API index creation with schema extraction and validation
- Knowledge base and docs site scaffolding

## Usage
```
#sk_index [target] [--type structure|api|docs] [--format md|json]
```

## Behavioral Flow
1. Discover files and modules; categorize by type and relevance
2. Generate navigable structure with cross-references and relationships
3. For API type: extract endpoints/schemas and build an index
4. Output in requested format (md/json)

Key behaviors:
- Intelligent organization and cross-referencing
- Quality and completeness checks
- Framework-appropriate documentation patterns
