# Double-coding artifacts (RQ2 agreement, RQ3 roles)

The coding instruments live in `../../codebooks/`: the inline and summary
review-function codebooks and the human-reply role codebook.

## RQ2 review-function coding (Section 3, RQ2)

Every coded unit of the four strata is double-coded blind and a third annotator
arbitrated the disagreements; the adjudicated labels are the coding of record
and are applied to the coded samples (`../labeling_full_coded.csv`,
`../cross_inline_sample_coded.csv`, `../rq2_summary_sample_coded.csv`,
`../cross_summary_sample_coded.csv`). The second coding arrived in three waves,
recorded per unit in the `round` column: `pilot` (the first 50 units drawn per
stratum, which fixed the codebook), `rest`, and a `completion` wave that
finished each stratum.

| file | content |
|---|---|
| `same_inline_sample_doublecoding.csv` | 364 same-system inline comments: `pass1`, `pass2`, the wave (`round`), the adjudicated `final` |
| `cross_inline_sample_doublecoding.csv` | 357 cross-system inline comments, same columns |
| `same_summary_sample_doublecoding.csv` | 275 same-system summaries, same columns |
| `cross_summary_sample_doublecoding.csv` | 348 cross-system summaries, same columns |
| `adjudication_log.csv` | all 79 recorded disagreements (unit, stratum, both labels, the arbitrated final, and a one-line reason per unit) |

Full-sample agreement (Cohen's kappa; observed agreement in parentheses), as
quoted in Section 3:

| stratum | kappa | observed | n |
|---|---|---|---|
| same-system inline comments | 0.82 | 0.91 | 364 |
| cross-system inline comments | 0.94 | 0.99 | 357 |
| same-system summaries | 0.93 | 0.96 | 275 |
| cross-system summaries | 0.88 | 0.92 | 348 |

Reproduce with `python3 scripts/rq2_agreement.py` (prints the pilot, remaining
and full-sample figures next to the paper's values and rewrites
`../rq2_kappa_redrawn_samples.json`).

### Decision rules at the contested boundaries

The adjudication log records a rule-based reason for every executed decision.
The recurring boundaries and the rules applied are:

- **Acknowledgment vs. response.** A reply that explicitly references the
  earlier point ("as requested", "applied your suggestion", "you're correct")
  and reports the action it prompted is `Response to feedback`; a bare report
  of an applied action is `Change acknowledgment`.
- **Defense vs. action.** A unit that only justifies the current state of the
  code is `Explanation`; a unit that reports or commits to an action is a
  disposition of the review point.
- **Count headers (summaries).** `Actionable comments posted: N` with N >= 1
  aggregates the review's findings and is `findings digest`; the bare N = 0
  header reports the review's own outcome and is `approval verdict` (the C.2
  boundary against `verification report`, whose checks run on the code).
- **Standing template headings.** A summary that recounts the change under a
  `Pull Request Overview` / `## Code Review` heading is `change overview`
  regardless of housekeeping lists inside it.
- **Verification runs.** A unit that relays the outcome of a check the reviewer
  itself ran (build, test or script output, including environment failures) is
  `Workflow/verification report`, not a code issue.

## RQ3 human role coding (Section 3.3.2)

| file | content |
|---|---|
| `roles_blind_full.csv` | the 316 sampled replies as the annotators saw them (no labels), with the reply bodies; third-party names in the bodies are replaced by pseudonyms |
| `roles_full_pass1.csv` / `roles_full_pass2.csv` | the two annotators' role labels over the full sample |
| `roles_full_final.csv` | the adjudicated labels of record |
| `roles_full_adjudication_log.csv` | arbitrator decisions with one-line reasons |

The pilot/remaining split lives in `../rq3_roles_pilot.csv` (the first 50
replies drawn, seed 20260930, which fixed the role codebook) and
`../rq3_roles_rest.csv` (the 266 remaining replies). The completion wave of
nine replies that brought the sample from 307 to 316 (drawn from the raw
comment table at seed 20261001) is already folded into the `roles_full_*` files.

Agreement for the role coding: kappa 0.74 on the pilot (n = 50) and 0.85 on the
remaining replies (n = 266; pooled 0.83 over the 316 coded replies), as quoted
in Section 3. Reproduce with `python3 scripts/reply_roles_agreement.py` (writes
`../rq3_kappa_rounds.json`).

The sample holds 316 replies, the size Cochran's rule gives for the 1,787-reply
frame.

## Final role distribution (n = 316, adjudicated)

| role | n | share |
|---|---|---|
| code feedback | 88 | 27.8% |
| direction to an agent | 78 | 24.7% |
| decision | 60 | 19.0% |
| brief remark | 50 | 15.8% |
| question | 40 | 12.7% |
