# RQ2 double-coding artifacts (review functions)

The coding instruments live in `../../../codebooks/`: the inline and summary
review-function codebooks.

Every coded unit is double-coded blind and a third annotator arbitrated the
disagreements; the adjudicated `final` is the coding of record and matches the
labels used in the analysis. A disagreement is visible where `pass1` and
`pass2` differ.

| file | content |
|---|---|
| `same_inline_coded.csv` | 364 same-system inline comments: `pass1`, `pass2`, the adjudicated `final` |
| `cross_inline_coded.csv` | 357 cross-system inline comments, same columns |
| `same_summary_coded.csv` | 275 same-system summaries, same columns |
| `cross_summary_coded.csv` | 348 cross-system summaries, same columns |

The `id` column carries the coded unit's identifier in the AIDev data, the
comment id for inline comments and the review id for summaries, so the full
text of each coded unit can be looked up in the original AIDev tables.

Agreement (Cohen's kappa):

| stratum | kappa | n |
|---|---|---|
| same-system inline comments | 0.82 | 364 |
| cross-system inline comments | 0.94 | 357 |
| same-system summaries | 0.93 | 275 |
| cross-system summaries | 0.88 | 348 |

Reproduce with `python3 scripts/rq2/coding_agreement.py` (prints the
per-stratum kappa and rewrites `../rq2_kappa.json`).
