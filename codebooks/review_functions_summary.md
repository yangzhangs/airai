*Instrument for RQ2 (review summaries).*

# Review-summary coding

This instrument codes the summaries of AI reviews on AI-authored pull requests.
Each summary receives exactly one label from the list below; the labels are
lowercase as in the released data.

## The labels

- `findings digest` — aggregates what the review turned up (defects, action
  items), often opening with a count of its own.
- `change overview` — recounts the change under a standing heading
  ("Pull Request Overview ... This PR fixes ...").
- `explanation` — explains why the code is the way it is (no defect claimed, no
  proposal, no question).
- `improvement suggestion` — proposes a concrete alternative or specific
  improvement.
- `verification report` — relays the outcome of a check the reviewer itself ran
  (test/build output).
- `approval verdict` — the short form that closes a review stating its outcome
  ("found no bugs"; bare "Actionable comments posted: 0").
- `response to feedback` — reports what was done about a point a review
  previously raised.
- `agent instruction` — instructs the authoring agent to do something.
- `clarification` — asks for information.
- `platform notice` — content about the reviewing service (plan, trial,
  pricing).
- `review unavailable` — the review produced no content (e.g., "wasn't able to
  review any files").
- `other` — no review substance or fits none of the above.

## Boundary rules

- A count header "Actionable comments posted: N" with N ≥ 1 is `findings
  digest`; the bare N = 0 header is `approval verdict`.
- A "Pull Request Overview" or "## Code Review" heading that recounts the change
  is `change overview` even if it lists housekeeping items.
- A summary that relays the outcome of a check the reviewer itself ran is
  `verification report`, not `improvement suggestion`.

## Worked examples

- "Actionable comments posted: 2" → `findings digest`
- "Pull Request Overview ... This PR fixes a typo in the README ..." → `change overview`
- "BugBot reviewed your changes and found no bugs!" → `approval verdict`
- "Here are the comprehensive test results for single-file builds ..." → `verification report`
- "Bugbot free trial expires on August 7, 2025" → `platform notice`
- "Copilot wasn't able to review any files in this pull request" → `review unavailable`
