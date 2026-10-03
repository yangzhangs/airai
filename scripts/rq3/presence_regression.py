#!/usr/bin/env python3
"""Logistic regression of human presence on the AI-on-AI reviewed PRs (Table 3):
review type + authoring agent + task type + log(stars) + calendar month, with
repository-clustered standard errors.

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

TABLE = [
    ('(Intercept)', 'Intercept'),
    ('Same-system review', 'any_same[T.True]'),
    ('Cross-system review', 'any_cross[T.True]'),
    ('Copilot', 'C(agent)[T.Copilot]'),
    ('Cursor', 'C(agent)[T.Cursor]'),
    ('Devin', 'C(agent)[T.Devin]'),
    ('Claude Code', 'C(agent)[T.Claude_Code]'),
    ('Log stars', 'logstars'),
    ('Calendar month', 'month'),
    ('chore', 'C(task_type)[T.chore]'),
    ('ci', 'C(task_type)[T.ci]'),
    ('docs', 'C(task_type)[T.docs]'),
    ('feat', 'C(task_type)[T.feat]'),
    ('fix', 'C(task_type)[T.fix]'),
    ('perf', 'C(task_type)[T.perf]'),
    ('refactor', 'C(task_type)[T.refactor]'),
    ('style', 'C(task_type)[T.style]'),
    ('test', 'C(task_type)[T.test]'),
]

print(f"N = {int(m.nobs)} PRs from {d.repo_name.nunique()} repositories")
print(f"pseudo R2 = {m.prsquared:.2f}   LLR = {2 * (m.llf - m.llnull):,.1f}   df = {int(m.df_model)}")
print(f"{'Predictor':22s} {'OR':>7s} {'95% CI':>16s} {'SE':>5s} {'z':>6s} {'p':>8s}")
for name, key in TABLE:
    or_ = float(np.exp(m.params[key]))
    lo, hi = (float(np.exp(v)) for v in m.conf_int().loc[key])
    print(f"{name:22s} {or_:7.2f} [{lo:5.2f}, {hi:5.2f}] {m.bse[key]:5.2f} {m.tvalues[key]:6.2f} {m.pvalues[key]:8.3f}")

terms = [x for x in m.params.index if x.startswith('C(task_type)')]
R = np.zeros((len(terms), len(m.params)))
idx = list(m.params.index)
for i, x in enumerate(terms):
    R[i, idx.index(x)] = 1
w = m.wald_test(R, scalar=False)
print(f"task controls, joint: chi2({len(terms)}) = {float(np.asarray(w.statistic).squeeze()):.1f}, "
      f"p = {float(np.asarray(w.pvalue).squeeze()):.3f}")
