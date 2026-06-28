# CONTEXT.md Format

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Term**:
{A concise description of the term}
_Avoid_: term1, term2

**Another Term**:
A description.
_Avoid_: alternate word

## Relationships

- A **Term** has multiple **Another Terms**
- **Another Term** belongs to exactly one **Term**

## Example dialogue

> **User**: "When a **Term** does X, what happens?"
> **Agent**: "A **Term** is only created when Y is confirmed."

## Flagged ambiguities

- "ambiguous word" was used to mean both **Term A** and **Term B** — resolved: these are distinct concepts.
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out in "Flagged ambiguities" with a clear resolution.
- **Keep definitions tight.** One sentence max. Define what it IS, not what it does.
- **Show relationships.** Use bold term names and express cardinality where obvious.
- **Only include terms specific to this session's context.** General concepts don't belong unless they're central to the discussion.
- **Group terms under subheadings** when natural clusters emerge.
- **Write an example dialogue.** A conversation that demonstrates how the terms interact naturally.

## When to update

Update CONTEXT.md **immediately** when:
- A term is defined or clarified during the conversation
- Ambiguous language is resolved
- Relationships between concepts are established
- New domain-specific concepts emerge

Don't batch updates — capture them as they happen.