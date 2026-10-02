# Double-coding artifacts (RQ2 agreement, RQ3 roles)

The coding instruments live in `../../codebooks/`: the inline and summary
review-function codebooks and the human-reply role codebook.

## RQ2 review-function coding (Section 3, RQ2)

Every coded unit of the four strata is double-coded blind and a third annotator
arbitrated the disagreements; the adjudicated labels are the coding of record
and are applied to the coded samples (`../labeling_full_coded.csv`,
`../cross_inline_sample_coded.csv`, `../rq2_summary_sample_coded.csv`,
`../cross_summary_sample_coded.csv`). The second coding arrived in three waves:
the original pilot (50 units per stratum) and rest waves, and the completion
wave that finished each stratum.

| file | content |
|---|---|
| `same_inline_sample_doublecoding.csv` | 364 same-system inline comments: `pass1`, `pass2`, the double-coding wave (`pilot`/`rest`/`completion`), the adjudicated `final` |
| `cross_inline_sample_doublecoding.csv` | 357 cross-system inline comments, same columns |
| `same_summary_sample_doublecoding.csv` | 275 same-system summaries, same columns |
| `cross_summary_sample_doublecoding.csv` | 348 cross-system summaries, same columns |
| `adjudication_log.csv` | all 79 recorded disagreements (unit, stratum, both labels, the arbitrated final, and a one-line reason per unit) |
| `inline_cross_v2/` | the a-priori re-coding batch that refined the cross-system inline codebook (302 AI-system units, kappa 0.79 on the batch), with its own arbitration log; the instrument it applied is `../../codebooks/review_functions_inline.md` |

Full-sample agreement (Cohen's kappa; observed agreement in parentheses), as
quoted in Section 3:

| stratum | kappa | observed | n |
|---|---|---|---|
| same-system inline comments | 0.82 | 0.91 | 364 |
| cross-system inline comments | 0.94 | 0.99 | 357 |
| same-system summaries | 0.93 | 0.96 | 275 |
| cross-system summaries | 0.88 | 0.92 | 348 |

Reproduce with `python3 scripts/57_rq2_agreement.py` (prints the figures next to
the paper's values and rewrites `../rq2_kappa_redrawn_samples.json`).

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

## RQ3 human roles (Section 4.4)

| file | content |
|---|---|
| `roles_blind.csv` | the pilot 200 human replies (seed 42) with bodies only; the second annotator saw exactly this |
| `roles_pass1.csv` / `roles_pass2.csv` | the two annotators' role labels for the pilot |
| `roles_disagreements.csv` | the pilot units where the two role annotators disagreed, with bodies |
| `roles_final.csv` | the adjudicated pilot role labels |
| `roles_adjudication_log.csv` | arbitrator decisions with one-line reasons |
| `roles_blind_full.csv`, `roles_full_pass1.csv`, `roles_full_pass2.csv`, `roles_full_final.csv`, `roles_full_adjudication_log.csv` | the full coding over the 316 sampled replies: the original wave and the nine-reply completion wave (drawn at seed 20261001, scripts/69; coded and adjudicated by scripts/70) |
| `roles_completion_draw.csv` | the nine completion-wave replies as drawn: ids, PRs, parent reviewers and bodies |

Agreement for the role coding: kappa 0.74 on the pilot (n = 50) and 0.85 on the
remaining replies (n = 266; pooled 0.83 over the 316 coded replies), as quoted
in Section 3. Reproduce with `python3 scripts/58_rq3_roles_pilot_split.py`
(writes `../rq3_kappa_rounds.json`).

The sample holds 316 replies, the size Cochran's rule gives for the 1,787-reply
frame; the pilot set stays fixed at its first draw (seed 20260930) and the
completion wave of nine replies was drawn at seed 20261001.

## Final role distribution (n = 316, adjudicated)

| role | n | share |
|---|---|---|
| code feedback | 88 | 27.8% |
| direction to an agent | 78 | 24.7% |
| decision | 60 | 19.0% |
| brief remark | 50 | 15.8% |
| question | 40 | 12.7% |
