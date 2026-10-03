# RQ2 double-coding artifacts (review functions, Section 3.2)

The coding instruments live in `../../../codebooks/`: the inline and summary
review-function codebooks.

Every coded unit of the four strata is double-coded blind and a third annotator
arbitrated the disagreements; the adjudicated labels are the coding of record
and are applied to the coded samples (`../same_system_inline_coded.csv`,
`../cross_system_inline_coded.csv`, `../same_system_summary_coded.csv`,
`../cross_system_summary_coded.csv`). The second coding arrived in three waves,
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

Reproduce with `python3 scripts/rq2/coding_agreement.py` (prints the pilot,
remaining and full-sample figures next to the released values and rewrites
`../rq2_kappa_redrawn_samples.json`).

### Decision rules at the contested boundaries

The adjudication log records a rule-based reason for every executed decision.
The recurring boundaries and the rules applied are:

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
