*Instrument for RQ3 (human replies).*

# Human-reply role coding

A human reply is a later comment in the same thread that GitHub explicitly links
to a review comment and that a human account authors. Each reply receives exactly
one role from the list below.

## The roles

- **decision** — rules on the point at issue, the contribution a maintainer acts
  on when deciding the merge; short, and often committing to an action.
- **code feedback** — evaluates the code or supplies a concrete replacement on a
  specific line; flags a defect, targets an API or type signature, or proposes a
  framework choice.
- **direction to an agent** — instructs the authoring agent to change the code,
  typically addressing it by name; a bare imperative that orders a code change
  counts even without the handle.
- **question** — asks the author or the agent for information, deferring any
  ruling; includes a check request right after an edit.
- **brief remark** — social or procedural content and no decision: a compliment,
  a bare status note, or a link.

## Boundary rules

- A bare agent mention with no instruction is `brief remark`.
- A bare imperative that orders a code change is `direction to an agent`; a
  technical alternative or a rationale about the code is `code feedback`.
- Deferring a decision to someone else is `brief remark`.
- An endorsement carrying a concrete technical improvement is `code feedback`.
- A report of a defect, an implementation constraint or how the code behaves is
  `code feedback`.
- Asking for information, including for a check, is `question`; asking the agent
  to make a change is `direction to an agent`.
- A procedural explanation about the merge is `brief remark`.

## Worked examples

- "We do, this was removed by copilot, I'll add it back" → `decision`
- "Not for now" → `decision`
- "I think PULL_NUMBER is not defined yet" → `code feedback`
- "@copilot apply this feedback please" → `direction to an agent`
- "done, can you please check" → `question`
- "How will we proceed here?" → `question`
- "Nice edit" → `brief remark`
