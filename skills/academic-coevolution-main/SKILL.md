---
name: academic-coevolution-main
description: Core controller for AI-human collaborative academic writing workflow. Use when starting academic writing, coordinating multiple skills, or managing the full research-to-paper pipeline.
---

# Academic Coevolution - Main Controller

## Quick Start

Start any academic writing task by initializing the coevolution workflow:

```
/academic-coevolution-main
```

This will:
1. Load the coevolution methodology (see [core_methodology.md](../core_methodology.md))
2. Configure the skill set for the current stage
3. Guide you through the appropriate workflow

## Core Philosophy

**Human-AI Coevolution**: This is not about AI doing the writing for you. It's about:
- You design rules and constraints
- AI executes within those constraints
- Both iterate to optimize the paradigm

**Roles**:
- **Human**: Core arguments, key reasoning, paragraph structure, final decisions
- **AI**: Academic expression, logical flow, language refinement, information gathering

## Workflow Stages

### Stage 1: Clarification (grill-me + grill-you)
- `/grill-me` - Get grilled on your research plan
- `/grill-you` - Ask AI clarifying questions to refine context
- Goal: Shared understanding before execution

### Stage 2: Research (auto-research + auto-evaluate)
- `/auto-research` - Gather academic sources with deterministic tools
- `/auto-evaluate` - Verify information accuracy and relevance
- Goal: High-quality, validated foundation

### Stage 3: Writing (academic-writing-assist)
- `/academic-writing-assist` - Human-led, AI-supported writing
- Goal: Co-created content with human ownership

## Usage Patterns

**New Paper**: Run through all stages sequentially
**Existing Work**: Jump to specific stage as needed
**Iteration**: Re-enter any stage to refine

## See Also

- [core_methodology.md](../core_methodology.md) - Full methodology documentation