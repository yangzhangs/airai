#!/usr/bin/env python3
"""Recompute the prevalence statistics of RQ1 (Sec. 3.1) from this package alone
and check each recomputed figure against the value the paper reports.

The counts come from data/common/curated_pr_metadata.csv (the curated AIDev
subset), data/common/pr_review_profile.csv (one row per reviewed PR with its
review configuration) and data/common/review_events_final.csv (the review
events); the account record behind the AI-reviewer identification is
data/rq1/ai_reviewer_accounts.csv. Chi-square tests are computed on the
contingency tables the text describes, with Cramer's V from the same tables
and the task-type comparisons restricted to the ten substantive task types
(other and revert fall outside them throughout the paper).

Run from the package root:  python3 scripts/rq1/prevalence_statistics.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

DATA = Path(__file__).resolve().parents[2] / 'data'

meta = pd.read_csv(DATA / 'common' / 'curated_pr_metadata.csv', low_memory=False)
prof = pd.read_csv(DATA / 'common' / 'pr_review_profile.csv', low_memory=False)
prof['task_type'] = prof.pr_id.map(meta.set_index('id').task_type)
ev = pd.read_csv(DATA / 'common' / 'review_events_final.csv', low_memory=False)
acc = pd.read_csv(DATA / 'rq1' / 'ai_reviewer_accounts.csv', comment='#')

TASKS = [t for t in meta.task_type.dropna().unique() if t not in ('other', 'revert')]

FAILS = []


def check(name, paper, got, fmt='{:g}'):
    """Print a paper vs recomputed line; record any mismatch."""
    ok = fmt.format(got) == fmt.format(paper)
    print(f'{name:44s} paper {fmt.format(paper):>14s} | recomputed {fmt.format(got):>14s}'
          + ('' if ok else '   <-- MISMATCH'))
    if not ok:
        FAILS.append(name)


def cramers_v(chi2, n, table):
    return np.sqrt(chi2 / (n * (min(table.shape) - 1)))


# ---- corpus ---------------------------------------------------------------
print('== Corpus')
check('curated PRs', 33596, len(meta), '{:,}')
check('curated repositories', 2807, meta.repo_name.nunique(), '{:,}')
check('reviewed PRs', 8047, len(prof), '{:,}')
check('reviewed repositories', 1410, ev.repo_name.nunique(), '{:,}')
check('review events', 28714, len(ev), '{:,}')

# ---- Table 1: the curated subset and its review activity, by agent --------
print('\n== Table 1 (by authoring agent)')
sm_tab = pd.read_csv(DATA / 'common' / 'review_summary_meta.csv', low_memory=False)
cm_tab = pd.read_csv(DATA / 'common' / 'review_comments_final.csv', low_memory=False)
EV = ev.merge(sm_tab, on='id')
CM = cm_tab.assign(authoring_agent=cm_tab.pr_id.map(meta.set_index('id').agent))
n_pr = meta.groupby('agent').size()
n_rev = prof.groupby('authoring_agent').size()
n_events = EV.groupby('authoring_agent').size()
n_summ = EV[EV.has_summary].groupby('authoring_agent').size()
n_cm = CM.groupby('authoring_agent').size()
TABLE1 = {
    'Copilot':      (4970, 2705, 54.4, 16209, 2170, 15220),
    'Cursor':       (1541, 727, 47.2, 1727, 967, 1336),
    'Devin':        (4827, 2089, 43.3, 5581, 1657, 4821),
    'Claude_Code':  (459, 189, 41.2, 652, 300, 1159),
    'OpenAI_Codex': (21799, 2337, 10.7, 4545, 2686, 3907),
}
for a, (prs, revd, pct, revs, sums, cms) in TABLE1.items():
    check(f'{a}: PRs', prs, int(n_pr[a]), '{:,}')
    check(f'{a}: reviewed PRs', revd, int(n_rev[a]), '{:,}')
    check(f'{a}: reviewed share (%)', pct, round(n_rev[a] / n_pr[a] * 100, 1))
    check(f'{a}: reviews', revs, int(n_events[a]), '{:,}')
    check(f'{a}: summaries', sums, int(n_summ[a]), '{:,}')
    check(f'{a}: inline comments', cms, int(n_cm[a]), '{:,}')
check('table totals: PRs', 33596, int(n_pr.sum()), '{:,}')
check('table totals: reviewed PRs', 8047, int(n_rev.sum()), '{:,}')
check('table totals: reviews', 28714, int(n_events.sum()), '{:,}')
check('table totals: summaries', 7780, int(n_summ.sum()), '{:,}')
check('table totals: inline comments', 26443, int(n_cm.sum()), '{:,}')

# ---- reviewed PRs by configuration ---------------------------------------
print('\n== Reviewed PRs (configurations)')
conf = np.where(prof.review_config.isin(['same', 'cross', 'same+cross']), 'only AI',
                np.where(prof.review_config == 'human', 'only human', 'both'))
prof = prof.assign(conf=conf)
n = len(prof)
counts = prof.conf.value_counts()
check('humans alone', 3661, counts['only human'], '{:,}')
check('humans and AI together', 2403, counts['both'], '{:,}')
check('AI alone', 1983, counts['only AI'], '{:,}')
check('with at least one AI review', 4386, int(prof.conf.isin(['only AI', 'both']).sum()), '{:,}')
check('AI-only share (%)', 24.6, round(counts['only AI'] / n * 100, 1))
check('at-least-one-AI share (%)', 54.5, round(prof.conf.isin(['only AI', 'both']).mean() * 100, 1))

tab = pd.crosstab(prof.authoring_agent, prof.conf)
chi2, p, dof, _ = chi2_contingency(tab)
check('configuration x agent chi2', 3063.2, round(chi2, 1), '{:,.1f}')
check('configuration x agent df', 8, dof)
check("configuration x agent V", 0.44, round(cramers_v(chi2, n, tab), 2))
agents = prof.groupby('authoring_agent').conf.value_counts(normalize=True).unstack(fill_value=0) * 100
check('AI-only share, Copilot (%)', 3.8, round(agents.loc['Copilot', 'only AI'], 1))
check('AI-only share, Codex (%)', 49.6, round(agents.loc['OpenAI_Codex', 'only AI'], 1))
check('human-only share, Devin (%)', 73.9, round(agents.loc['Devin', 'only human'], 1))
ai_any = prof.assign(ai=prof.conf.isin(['only AI', 'both'])).groupby('authoring_agent').ai.mean() * 100
others = ai_any.drop('Devin')
check('AI-on-AI share, min among four (%)', 61.4, round(others.min(), 1))
check('AI-on-AI share, max among four (%)', 65.9, round(others.max(), 1))
check('AI-on-AI share, Devin (%)', 26.1, round(ai_any['Devin'], 1))
check('with-humans share, Copilot (%)', 60.1, round(agents.loc['Copilot', 'both'], 1))

sub = prof[prof.task_type.isin(TASKS)]
tab = pd.crosstab(sub.task_type, sub.conf)
chi2, p, dof, _ = chi2_contingency(tab)
check('configuration x task chi2', 115.5, round(chi2, 1), '{:,.1f}')
check('configuration x task df', 18, dof)
check('configuration x task V', 0.08, round(cramers_v(chi2, len(sub), tab), 2))
tasks = sub.groupby('task_type').conf.value_counts(normalize=True).unstack(fill_value=0) * 100
for t, v in [('ci', 13.6), ('refactor', 18.3), ('chore', 19.1), ('test', 29.1), ('feat', 28.6), ('docs', 25.8)]:
    check(f'AI-only share, {t} (%)', v, round(tasks.loc[t, 'only AI'], 1))
check('human-only share, build (%)', 40.9, round(tasks.loc['build', 'only human'], 1))
check('human-only share, ci (%)', 63.6, round(tasks.loc['ci', 'only human'], 1))

# ---- AI-on-AI review events ----------------------------------------------
print('\n== AI-on-AI review types')
ai_ev = ev[ev.actor.isin(['same-system', 'cross-system'])]
check('AI-on-AI events', 11693, len(ai_ev), '{:,}')
check('AI-on-AI share of events (%)', 40.7, round(len(ai_ev) / len(ev) * 100, 1))
check('same-system events', 7292, int((ev.actor == 'same-system').sum()), '{:,}')
check('cross-system events', 4401, int((ev.actor == 'cross-system').sum()), '{:,}')
check('same-system share of AI-on-AI (%)', 62.4, round((ev.actor == 'same-system').sum() / len(ai_ev) * 100, 1))

tab = pd.crosstab(ai_ev.authoring_agent, ai_ev.actor)
chi2, p, dof, _ = chi2_contingency(tab)
check('type x agent chi2', 10480.3, round(chi2, 1), '{:,.1f}')
check('type x agent df', 4, dof)
check('type x agent V', 0.95, round(cramers_v(chi2, len(ai_ev), tab), 2))
shares = ai_ev.groupby('authoring_agent').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
check('same-system share, Copilot (%)', 99.2, round(shares.loc['Copilot', 'same-system'], 1))
check('same-system share, Cursor (%)', 45.7, round(shares.loc['Cursor', 'same-system'], 1))
check('same-system share, Claude (%)', 0.4, round(shares.loc['Claude_Code', 'same-system'], 1))
allrev = ev.groupby('authoring_agent').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
check('human share of Devin PR reviews (%)', 79.2, round(allrev.loc['Devin', 'human'], 1))
check('cross share of Codex PR reviews (%)', 53.7, round(allrev.loc['OpenAI_Codex', 'cross-system'], 1))

tab = pd.crosstab(ai_ev[ai_ev.task_type.isin(TASKS)].task_type, ai_ev[ai_ev.task_type.isin(TASKS)].actor)
chi2, p, dof, _ = chi2_contingency(tab)
check('type x task chi2', 247.2, round(chi2, 1), '{:,.1f}')
check('type x task df', 9, dof)
check('type x task V', 0.15, round(cramers_v(chi2, tab.values.sum(), tab), 2))
tshares = ai_ev[ai_ev.task_type.isin(TASKS)].groupby('task_type').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
for t, v in [('chore', 30.3), ('ci', 80.4), ('feat', 60.7), ('test', 60.2), ('fix', 66.1), ('docs', 68.1)]:
    check(f'same-system share, {t} (%)', v, round(tshares.loc[t, 'same-system'], 1))

# ---- pairings ------------------------------------------------------------
print('\n== Review pairings')
same = ev[ev.actor == 'same-system']
pairs = same.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
check('Copilot-to-Copilot events', 6867, int(pairs.get(('Copilot', 'Copilot'), 0)), '{:,}')
check('Cursor-to-Cursor events', 424, int(pairs.get(('Cursor', 'Cursor'), 0)), '{:,}')
check('Claude-to-Claude events', 1, int(pairs.get(('Claude Code', 'Claude_Code'), 0)))
check('Copilot share of same-system (%)', 94.2, round(pairs.get(('Copilot', 'Copilot'), 0) / len(same) * 100, 1))
check('Copilot-to-Copilot share of all AI-on-AI (%)', 58.7, round(pairs.get(('Copilot', 'Copilot'), 0) / len(ai_ev) * 100, 1))
check('Claude Code events as reviewer', 55, int((ev.reviewer_system == 'Claude Code').sum()))
cross = ev[ev.actor == 'cross-system']
check('reviewing systems in cross-system', 30, cross.reviewer_system.nunique())
cpairs = cross.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
check('cross-system pairings', 67, len(cpairs))
top = {('Copilot', 'OpenAI_Codex'): 898, ('CodeRabbit', 'OpenAI_Codex'): 752,
       ('Cursor', 'Devin'): 519, ('Gemini Code Assist', 'OpenAI_Codex'): 259}
for (r, a), v in top.items():
    check(f'{r.split()[0]} on {a} events', v, int(cpairs.get((r, a), 0)), '{:,}')
check('six largest pairings share (%)', 62.9, round(cpairs.head(6).sum() / len(cross) * 100, 1))
check('singleton pairings (of the tail)', 15, int((cpairs.iloc[6:] == 1).sum()))
check('tail pairings', 61, len(cpairs) - 6)
check('Copilot share of cross-system (%)', 27.0, round((cross.reviewer_system == 'Copilot').sum() / len(cross) * 100, 1))
check('CodeRabbit share of cross-system (%)', 23.4, round((cross.reviewer_system == 'CodeRabbit').sum() / len(cross) * 100, 1))
cside = cross.authoring_agent.value_counts(normalize=True) * 100
for a, v in [('OpenAI_Codex', 55.4), ('Devin', 26.4), ('Cursor', 11.4), ('Copilot', 1.2)]:
    check(f'cross-system on {a} (%)', v, round(cside[a], 1))

# ---- account identification ----------------------------------------------
print('\n== AI-reviewer accounts')
check('candidates from the platform bot flag', 40, int((acc.source == 'bot flag').sum()))
check('candidates kept as AI reviewers', 31, int(((acc.source == 'bot flag') & (acc.role == 'AI reviewer')).sum()))
check('candidates excluded as automation', 9, int((acc.role == 'excluded automation').sum()))
check('accounts added by name inspection', 1, int((acc.source == 'name inspection').sum()))
check('AI accounts in total', 32, int((acc.role == 'AI reviewer').sum()))

print()
if FAILS:
    print('MISMATCHES:', ', '.join(FAILS))
    sys.exit(1)
print('all RQ1 prevalence figures match the paper.')
