# RQ3 double-coding artifacts (human reply roles)

The coding instrument lives in `../../../codebooks/reply_roles.md`.

The sampled replies are double-coded blind and a third annotator arbitrated the
disagreements; the adjudicated `final` is the coding of record and matches the
labels used in the analysis. A disagreement is visible where `pass1` and
`pass2` differ.

| file | content |
|---|---|
| `roles_full_coded.csv` | the 316 replies with their bodies (third-party account names pseudonymized), `pass1`, `pass2`, and the adjudicated `final` |

The `id` column is the reply's comment id in the AIDev data and `pr_id` its pull
request, so the full text of each sampled reply can be looked up in the original
AIDev tables.

Agreement (Cohen's kappa): 0.83 over the 316 coded replies.

Reproduce with `python3 scripts/rq3/reply_roles_agreement.py` (prints the
agreement and rewrites `../rq3_kappa.json`).
