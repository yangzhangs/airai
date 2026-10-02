#!/usr/bin/env python3
"""Fit the logistic regression of human presence behind Table 3 and Table 3's
text (Section 3.3): human presence ~ same-system + cross-system + authoring
agent + task type + log(stars) + calendar month, with repository-clustered
standard errors, on the 4,386 AI-on-AI reviewed PRs (Section 2.4).

Task-type controls are the ten substantive categories: the four PRs carrying
the two rarest labels (other, revert; 0.1% of the curated PRs) are excluded, as
they fall outside the task-type comparisons throughout the paper.

The script prints the rows exactly as the manuscript rounds them and fails if
any value drifts from the table, so the regression is reproducible from the
package alone (statsmodels; the released variables are recomputed from the
event and metadata tables).
Run from the package root:  python3 scripts/62_presence_regression.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA = Path(__file__).resolve().parent.parent / 'data'

prof = pd.read_csv(DATA / 'pr_review_profile.csv')
meta = pd.read_csv(DATA / 'curated_pr_metadata.csv')
ev = pd.read_csv(DATA / 'review_events_final.csv')
meta['created_at'] = pd.to_datetime(meta['created_at'], utc=True, format='mixed')

ai_prs = set(ev.loc[ev.actor.str.contains('system'), 'pr_id'])
d = prof[prof.pr_id.isin(ai_prs)].merge(
    meta[['id', 'task_type', 'stars', 'created_at', 'repo_name']],
    left_on='pr_id', right_on='id')
d = d[~d.task_type.isin(['other', 'revert'])].copy()
d['human'] = d.any_human.astype(int)
d['month'] = d.created_at.dt.month
d['logstars'] = np.log(d.stars.astype(float))
d['agent'] = pd.Categorical(d.authoring_agent,
                            categories=['OpenAI_Codex', 'Copilot', 'Cursor', 'Devin', 'Claude_Code'])

m = smf.logit('human ~ any_same + any_cross + C(agent) + C(task_type) + logstars + month',
              data=d).fit(cov_type='cluster', cov_kwds={'groups': d.repo_name}, disp=0, maxiter=300)
assert m.mle_retvals.get('converged'), 'the model must converge on the released tables'

ROWS = [
    ('Same-system review', 'any_same[T.True]', 1.10, 0.51, 2.34, 0.39, 0.24, 0.812),
    ('Cross-system review', 'any_cross[T.True]', 0.56, 0.24, 1.27, 0.42, -1.39, 0.165),
    ('Copilot', 'C(agent)[T.Copilot]', 23.74, 8.67, 64.94, 0.51, 6.17, None),
    ('Cursor', 'C(agent)[T.Cursor]', 0.74, 0.35, 1.58, 0.39, -0.78, 0.436),
    ('Devin', 'C(agent)[T.Devin]', 2.35, 1.02, 5.45, 0.43, 2.00, 0.045),
    ('Claude Code', 'C(agent)[T.Claude_Code]', 1.49, 0.79, 2.82, 0.33, 1.22, 0.222),
    ('Log stars', 'logstars', 1.07, 0.89, 1.28, 0.09, 0.70, 0.487),
    ('Calendar month', 'month', 1.15, 0.93, 1.42, 0.11, 1.28, 0.201),
]

print(f"N = {int(m.nobs)} PRs from {d.repo_name.nunique()} repositories")
print(f"{'Predictor':22s} {'OR':>7s} {'95% CI':>16s} {'SE':>5s} {'z':>6s} {'p':>8s}   paper")
ok = True
for name, key, or_, lo, hi, se, z, p in ROWS:
    row = (round(float(np.exp(m.params[key])), 2), round(float(np.exp(m.conf_int()[0][key])), 2),
           round(float(np.exp(m.conf_int()[1][key])), 2), round(float(m.bse[key]), 2),
           round(float(m.tvalues[key]), 2), float(m.pvalues[key]))
    bad = (row[0] != or_ or row[1] != lo or row[2] != hi or row[3] != se or row[4] != z
           or (p is not None and round(row[5], 3) != p) or (p is None and row[5] >= 0.001))
    ok &= not bad
    print(f"{name:22s} {row[0]:7.2f} [{row[1]:5.2f}, {row[2]:5.2f}] {row[3]:5.2f} {row[4]:6.2f} "
          f"{row[5]:8.3f}   {'OK' if not bad else 'MISMATCH'}")
print('Table 3 reproduced.' if ok else 'MISMATCH against the manuscript; update the table or the script.')
