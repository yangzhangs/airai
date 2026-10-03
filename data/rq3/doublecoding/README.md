# RQ3 double-coding artifacts (human reply roles)

The coding instrument lives in `../../../codebooks/reply_roles.md`.

| file | content |
|---|---|
| `roles_blind_full.csv` | the 316 sampled replies as the annotators saw them (no labels), with the reply bodies; third-party account names in the bodies are replaced by pseudonyms |
| `roles_full_pass1.csv` / `roles_full_pass2.csv` | the two annotators' role labels over the full sample |
| `roles_full_final.csv` | the adjudicated labels of record |
| `roles_full_adjudication_log.csv` | the arbitration record (unit, both labels, arbitrated outcome) |

The pilot/remaining split lives in `../roles_pilot.csv` (the first 50 replies
drawn, seed 20260930, which fixed the role codebook) and `../roles_rest.csv`
(the 266 remaining replies). The completion wave of nine replies that brought
the sample from 307 to 316 (drawn from the raw comment table at seed 20261001)
is already folded into the `roles_full_*` files.

Agreement for the role coding: kappa 0.74 on the pilot (n = 50) and 0.85 on the
remaining replies (n = 266; pooled 0.83 over the 316 coded replies), as quoted
in Section 3. Reproduce with `python3 scripts/rq3/reply_roles_agreement.py`
(writes `../rq3_kappa_rounds.json`).

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
