# RQ3 double-coding artifacts (human reply roles)

The coding instrument lives in `../../../codebooks/reply_roles.md`.

Every sampled reply is double-coded blind and a third annotator arbitrated the
disagreements; the adjudicated labels are the coding of record and are applied
to the released files (`../roles_pilot.csv`, `../roles_rest.csv`,
`roles_full_final.csv`). The pilot is the first 50 replies drawn, which fixed
the role codebook; the remaining replies were labeled under it, with a
completion wave folded into the `roles_full_*` files.

| file | content |
|---|---|
| `roles_blind_full.csv` | the 316 replies as the annotators saw them (no labels), with the reply bodies; third-party account names are replaced by pseudonyms |
| `roles_full_pass1.csv` / `roles_full_pass2.csv` | the two annotators' role labels over the full sample |
| `roles_full_final.csv` | the adjudicated labels of record |
| `roles_full_adjudication_log.csv` | the arbitration record (unit, both labels, arbitrated outcome) |

Agreement (Cohen's kappa), as quoted in the paper:

| round | kappa | n |
|---|---|---|
| pilot | 0.74 | 50 |
| remaining | 0.85 | 266 |
| pooled | 0.83 | 316 |

Reproduce with `python3 scripts/rq3/reply_roles_agreement.py` (prints the
agreement rounds and rewrites `../rq3_kappa_rounds.json`).
