# RQ2 double-coding artifacts (review functions)

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
| `adjudication_log.csv` | all 79 arbitrated disagreements (unit, stratum, both labels, arbitrated final) |

Full-sample agreement (Cohen's kappa), as quoted in Section 3:

| stratum | kappa | n |
|---|---|---|
| same-system inline comments | 0.82 | 364 |
| cross-system inline comments | 0.94 | 357 |
| same-system summaries | 0.93 | 275 |
| cross-system summaries | 0.88 | 348 |

Reproduce with `python3 scripts/rq2/coding_agreement.py` (prints the pilot,
remaining and full-sample figures next to the released values and rewrites
`../rq2_kappa_redrawn_samples.json`).

