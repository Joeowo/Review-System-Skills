---
name: grill-me
description: Relentlessly interview the user about research plans or designs to achieve shared understanding, resolve decision branches, and maintain CONTEXT.md with terminology as decisions crystallise. Use when stress-testing plans, getting grilled on designs, or user mentions "grill me".
---

# Grill Me

## What This Does

I will interview you relentlessly about every aspect of your plan until we reach a shared understanding. I'll walk down each branch of your design tree, resolving dependencies between decisions one-by-one. For each question, I'll suggest my recommended answer.

## How It Works

1. **One question at a time** - No information overload
2. **Exploration first** - If a question can be answered by exploring code or documents, I'll explore instead
3. **Recommendations provided** - For each question, I'll suggest my recommended answer
4. **No assumptions** - Every branch gets explored
5. **Inline CONTEXT updates** - When terms are resolved, I'll update CONTEXT.md immediately

## Context and Terminology

### Check for existing CONTEXT.md

Before starting, I'll check if CONTEXT.md exists in the project. If it does, I'll use it to:
- Challenge you when your language conflicts with defined terms
- Identify when you're using terms that have alternatives listed to avoid
- Ensure consistency with previous decisions

### Challenge ambiguous language

When you use vague or overloaded terms, I'll propose a precise canonical term. Example:
> You're saying "account" — do you mean the Customer or the User? Those are different things.

### Update CONTEXT.md inline

When a term is resolved, I'll update CONTEXT.md right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](../CONTEXT-FORMAT.md).

## When to Use

- Before starting major research phases
- When designs feel unclear or incomplete
- When you want to stress-test your plan
- When you say "grill me"

## Example Session

```
You: I want to study the impact of remote work on productivity.

Me: Great. Let's start at the root: What's your specific research question?
     Is it about:
     a) Individual productivity metrics
     b) Team-level coordination efficiency
     c) Organizational outcomes
     d) Something else?

You: Probably a), but I'm not sure how to measure it.

Me: That's a branch we need to resolve. Measurement could be:
     a) Self-reported surveys
     b) Manager evaluations
     c) Objective output metrics
     d) A combination approach [RECOMMENDED]

     My recommendation is d) - combine subjective and objective to capture
     the full picture. What do you think?

You: I like d). Let's call it "Productivity Index".

Me: Got it. I'll add **Productivity Index** to CONTEXT.md as "A combined
     measure of subjective and objective productivity metrics."

     Next question: What time period are you measuring?
```

## Your Turn

Tell me your plan or design, and I'll start grilling you.