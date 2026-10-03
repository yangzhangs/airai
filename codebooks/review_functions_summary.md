*Instrument for RQ2 (review-function coding; Sections 2.3 and 3.2).*

# Codebook — review-summary coding (12 leaf labels, lowercase as in the package)

Use EXACTLY these labels for the `summary` strata:

- `findings digest` — aggregates what the review turned up (defects, action items), often opening with a count of its own.
- `change overview` — recounts the change under a standing heading ("Pull Request Overview ... This PR fixes ...").
- `explanation` — explains why the code is the way it is (no defect claimed, no proposal, no question).
- `improvement suggestion` — proposes a concrete alternative or specific improvement.
- `verification report` — relays the outcome of a check the reviewer itself ran (test/build output).
- `approval verdict` — the short form that closes a review stating its outcome ("found no bugs"; bare "Actionable comments posted: 0").
- `response to feedback` — reports what was done about a point a review previously raised.
- `agent instruction` — instructs the authoring agent to do something.
- `clarification` — asks for information.
- `platform notice` — content about the reviewing service (plan, trial, pricing).
- `review unavailable` — the review produced no content (e.g., "wasn't able to review any files").
- `other` — no review substance or fits none of the above.

Boundary notes: a count header "Actionable comments posted: N" with N>=1 is `findings digest`; the bare N=0 header is `approval verdict`; a "Pull Request Overview"/"## Code Review" heading that recounts the change is `change overview` even if it lists housekeeping items.

## Mapping to the paper's function taxonomy

The paper aggregates these codes into five review functions (Section 3.2.2):
[A] Descriptive groups `findings digest` (A.1), `change overview` (A.2) and
`explanation` (A.3); [B] Code-directed groups `improvement suggestion` (B.1)
and `verification report` (B.3), while the code-issue label (B.2) arises on
inline comments only; [C] Confirmatory groups `approval verdict` (C.2); [D]
Interactive/directive groups `response to feedback` (D.1) and `clarification`
(D.2); [E] Other collects `platform notice`, `review unavailable` and the
residue. `agent instruction` is defined in the instrument, but no unit in the
coded samples carries it, and it is not a leaf of the paper's taxonomy.
