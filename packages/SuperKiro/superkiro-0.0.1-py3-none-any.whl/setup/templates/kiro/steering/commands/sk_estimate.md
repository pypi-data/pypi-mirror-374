---
inclusion: manual
---

Note (Kiro): Use `.kiro/steering/commands/sk_estimate.md <target> [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]`. In responses, state: `Consulted .kiro/steering/commands/sk_estimate.md`.

---
name: estimate
description: "Provide development estimates for tasks, features, or projects with intelligent analysis"
category: special
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, performance, project-manager]
---

# #sk_estimate - Development Estimation

## Triggers
- Development planning requiring time, effort, or complexity estimates
- Project scoping and resource allocation decisions
- Feature breakdown needing systematic estimation methodology
- Risk assessment and confidence interval analysis requirements

## Usage
```
#sk_estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```

## Behavioral Flow
1. **Analyze**: Examine scope, complexity factors, dependencies, and framework patterns
2. **Calculate**: Apply estimation methodology with historical benchmarks and complexity scoring
3. **Validate**: Cross-reference estimates with project patterns and domain expertise
4. **Present**: Provide detailed breakdown with confidence intervals and risk assessment
5. **Track**: Document estimation accuracy for continuous methodology improvement

Key behaviors:
- Multi-persona coordination (architect, performance, project-manager) based on estimation scope
- Sequential MCP integration for systematic analysis and complexity assessment
- Context7 MCP integration for framework-specific patterns and historical benchmarks
- Intelligent breakdown analysis with confidence intervals and risk factors
