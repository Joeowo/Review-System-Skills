---
name: grill-you
description: Guide users to ask clarifying questions to the agent, promoting deep thinking and maintaining high-quality context with CONTEXT.md terminology consistency. Use alongside grill-me for bidirectional clarification, or when user needs help structuring inquiries.
---

# Grill You

## What This Does

I'll guide you to ask ME questions that clarify your research context. This isn't about answering— it's about helping you formulate the right inquiries to deepen your thinking and maintain high-quality conversation context.

## Why This Matters

When you work with AI over multiple sessions, context quality degrades without explicit clarification. Grill-you helps:
- Surface unstated assumptions
- Reveal gaps in your thinking
- Build shared mental models
- Maintain context across iterations

## How It Works

I'll suggest question categories you should ask ME. You don't have to ask them all— pick what matters. After you ask, I'll answer, then suggest more.

## Context and Terminology

### Check for existing CONTEXT.md

When guiding your questions, I'll reference CONTEXT.md if it exists:
- Point out terms you should clarify based on existing definitions
- Identify when you're asking about concepts that have been previously defined
- Ensure your questions use consistent terminology

### Flagging conflicts

If your question uses language that conflicts with CONTEXT.md, I'll surface it:
> Your CONTEXT.md defines "cancellation" as X, but you seem to be asking about Y — which is it?

### Updating CONTEXT.md

When our discussion resolves terminology, I'll update CONTEXT.md immediately. Use the format in [CONTEXT-FORMAT.md](../CONTEXT-FORMAT.md).

## Core Question Categories

### 1. Boundary Questions
"What's the scope you're assuming for this task?"
"What are you NOT considering?"
"What constraints am I imposing without stating?"

### 2. Method Questions
"What approach would you take if [alternative condition]?"
"Why do you recommend X over Y here?"
"What's the risk of this approach?"

### 3. Context Questions
"What information am I missing that would help?"
"What context from previous sessions might be relevant?"
"What would you need to know to give better suggestions?"

### 4. Terminology Questions
"When you say [term], what exactly do you mean?"
"Is there a specific definition I should use for [concept]?"
"What terms should I avoid using here?"

### 5. Counterfactual Questions
"How would your answer change if [factor] were different?"
"What's the opposite viewpoint?"

## Parallel Use with Grill-Me

```
Grill-Me   →  AI challenges YOUR understanding + maintains CONTEXT.md
Grill-You  →  AI helps YOU challenge AI's understanding + maintains CONTEXT.md

Recommended: Run both at major decision points for bidirectional clarity.
```

## Quick Start

Tell me what you're working on, and I'll start suggesting questions to ask me.

Example:
```
You: I'm analyzing remote work productivity data.

Me: Great. Here are questions you should ask me to clarify our context:
     1. "What assumptions are you making about the data structure?"
     2. "What variables should I prioritize vs ignore?"
     3. "What methodological biases should I be aware of?"
     4. "What terminology should I use when referring to productivity?"

     Pick one to start, or tell me your own concerns.
```