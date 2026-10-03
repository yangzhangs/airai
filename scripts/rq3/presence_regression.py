#!/usr/bin/env python3
"""Fit the logistic regression of human presence behind Table 3 and Table 3's
text (Section 3.3): human presence ~ same-system + cross-system + authoring
agent + task type + log(stars) + calendar month, with repository-clustered
standard errors, on the 4,386 AI-on-AI reviewed PRs (Section 2.4).

Task-type controls are the ten substantive categories: the four PRs carrying
the two rarest labels (other, revert; 0.1% of the curated PRs) are excluded, as
they fall outside the task-type comparisons throughout the paper.

The script prints the rows exactly as the manuscript rounds them (including the
intercept; the second panel of the table lists the task-type terms) and checks the joint Wald test of
the task controls quoted in the text, so the regression is reproducible from the
package alone (statsmodels; the released variables are recomputed from the
event and metadata tables).
Run from the package root:  python3 scripts/rq3/presence_regression.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA = Path(__file__).resolve().parents[2] / 'data' / 'common'

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
    ('(Intercept)', 'Intercept', 0.13, 0.01, 1.18, 1.13, -1.81, 0.070),
    ('Same-system review', 'any_same[T.True]', 1.10, 0.51, 2.34, 0.39, 0.24, 0.812),
    ('Cross-system review', 'any_cross[T.True]', 0.56, 0.24, 1.27, 0.42, -1.39, 0.165),
    ('Copilot', 'C(agent)[T.Copilot]', 23.74, 8.67, 64.94, 0.51, 6.17, None),
    ('Cursor', 'C(agent)[T.Cursor]', 0.74, 0.35, 1.58, 0.39, -0.78, 0.436),
    ('Devin', 'C(agent)[T.Devin]', 2.35, 1.02, 5.45, 0.43, 2.00, 0.045),
    ('Claude Code', 'C(agent)[T.Claude_Code]', 1.49, 0.79, 2.82, 0.33, 1.22, 0.222),
    ('Log stars', 'logstars', 1.07, 0.89, 1.28, 0.09, 0.70, 0.487),
    ('Calendar month', 'month', 1.15, 0.93, 1.42, 0.11, 1.28, 0.201),
    ('chore', 'C(task_type)[T.chore]', 2.83, 1.18, 6.81, 0.45, 2.33, 0.020),
    ('ci', 'C(task_type)[T.ci]', 1.20, 0.47, 3.04, 0.47, 0.38, 0.703),
    ('docs', 'C(task_type)[T.docs]', 1.04, 0.54, 2.01, 0.34, 0.12, 0.904),
    ('feat', 'C(task_type)[T.feat]', 1.20, 0.64, 2.24, 0.32, 0.58, 0.564),
    ('fix', 'C(task_type)[T.fix]', 1.34, 0.73, 2.47, 0.31, 0.95, 0.344),
    ('perf', 'C(task_type)[T.perf]', 0.51, 0.16, 1.65, 0.60, -1.13, 0.259),
    ('refactor', 'C(task_type)[T.refactor]', 2.02, 0.97, 4.23, 0.38, 1.87, 0.062),
    ('style', 'C(task_type)[T.style]', 2.23, 0.57, 8.77, 0.70, 1.15, 0.249),
    ('test', 'C(task_type)[T.test]', 0.85, 0.47, 1.52, 0.30, -0.55, 0.579),
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
llr = 2 * (m.llf - m.llnull)
fit_ok = (abs(round(llr, 1) - 2178.1) <= 0.5 and int(m.df_model) == 17
          and abs(round(m.prsquared, 2) - 0.36) <= 0.005)
ok &= fit_ok
print(f"{'model fit vs null':22s} LLR={llr:9.1f} {'':16s} df={int(m.df_model):3d} {'':8s}   "
      f"paper 2,178.1 / 17 / pseudoR2 0.36   {'OK' if fit_ok else 'MISMATCH'}")

terms = [x for x in m.params.index if x.startswith('C(task_type)')]
idx = list(m.params.index)
R = np.zeros((len(terms), len(m.params)))
for i, x in enumerate(terms):
    R[i, idx.index(x)] = 1
w = m.wald_test(R, scalar=False)
cjk = float(np.asarray(w.statistic).squeeze()); pjk = float(np.asarray(w.pvalue).squeeze())
jk_ok = abs(cjk - 18.2) <= 0.3 and abs(pjk - 0.033) <= 0.002
ok &= jk_ok
print(f"{'task controls, joint':22s} {cjk:7.1f} {'':16s} {'':5s} {len(terms):6d} {pjk:8.3f}   "
      f"{'OK' if jk_ok else 'MISMATCH'}")
print('Table 3 reproduced.' if ok else 'MISMATCH against the manuscript; update the table or the script.')
