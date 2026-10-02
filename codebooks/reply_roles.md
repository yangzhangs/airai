# Codebook — human-reply role coding (five roles)

Scope: the human replies on the AI-on-AI reviewed PRs, where a human reply is a
later comment in the same thread that GitHub explicitly links to a review
comment and that a human account authors (Section 2.4). The released sample
holds 316 coded replies; a pilot of 50 replies fixed the codebook and the rest
were labeled under it. Assign EXACTLY one role to each reply.

## The roles

- **decision** — rules on the point at issue, the contribution a maintainer
  acts on when deciding the merge. Decisions are short, settle a point the
  thread has already raised, and often commit to an action ("We do, this was
  removed by copilot, I'll add it back"; "Not for now"). 60 of 316 replies.
- **code feedback** — evaluates the code or supplies a concrete replacement on
  a specific line; flags an undefined reference ("I think PULL_NUMBER is not
  defined yet"), targets an API or type signature, or proposes a framework
  choice ("Or just use the useSettings hook"). 88 of 316 replies.
- **direction to an agent** — instructs the authoring agent to change the code,
  typically addressing it by name ("@copilot apply this feedback please"); a
  bare imperative that orders a code change counts even without the handle
  ("override the `_split_zone_and_sub` with `BaseProvider`"). 78 of 316 replies.
- **question** — asks the author or the agent for information, deferring any
  ruling; includes a check request right after an edit ("done, can you please
  check"; "How will we proceed here?"). 40 of 316 replies.
- **brief remark** — social or procedural content and no decision: a compliment
  ("Nice edit"), a bare status note ("Removed the try/catch."), or a link. 50 of
  316 replies.

## Boundary rules (decided on the adjudicated cases)

- A bare agent mention with no instruction is `brief remark`, not `direction to an agent`.
- A bare imperative that orders a code change is `direction to an agent`; a
  technical alternative or a rationale about the code is `code feedback`.
- Deferring a decision to someone else is `brief remark`.
- An endorsement carrying a concrete technical improvement is `code feedback`;
  a position without technical content ("Not for now") is `decision`.
- A report of a defect, an implementation constraint or how the code behaves is `code feedback`.
- Asking for information, including for a check, is `question`; asking the
  agent to make a change is `direction to an agent`.
- A procedural explanation about the merge is `brief remark`.

## Agreement

Coding ran in two rounds over the 316 replies, with the pilot set fixed at its
first draw: kappa 0.74 on the pilot (n = 50), 0.85 on the remaining replies
(n = 266), 0.83 pooled (`data/rq3_kappa_rounds.json`; regenerate with
`scripts/58_rq3_roles_pilot_split.py`).

The coded sample is `data/doublecoding/roles_full_final.csv` (316 rows); the
waves and the per-unit adjudication reasons are documented in
`data/doublecoding/README.md` and the `roles_*` files next to it.
