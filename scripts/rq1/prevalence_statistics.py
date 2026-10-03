#!/usr/bin/env python3
"""RQ1 prevalence statistics.

Run from the package root:  python3 scripts/rq1/prevalence_statistics.py
"""
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


def show(name, value, fmt='{:g}'):
    print(f'{name:52s} {fmt.format(value):>14s}')


def cramers_v(chi2, n, table):
    return np.sqrt(chi2 / (n * (min(table.shape) - 1)))


# ---- corpus ---------------------------------------------------------------
print('== Corpus')
show('curated PRs', len(meta), '{:,}')
show('curated repositories', meta.repo_name.nunique(), '{:,}')
show('reviewed PRs', len(prof), '{:,}')
show('reviewed repositories', ev.repo_name.nunique(), '{:,}')
show('review events', len(ev), '{:,}')

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
for a in n_pr.sort_values(ascending=False).index:
    show(f'{a}: PRs', int(n_pr[a]), '{:,}')
    show(f'{a}: reviewed PRs', int(n_rev[a]), '{:,}')
    show(f'{a}: reviewed share (%)', round(n_rev[a] / n_pr[a] * 100, 1))
    show(f'{a}: reviews', int(n_events[a]), '{:,}')
    show(f'{a}: summaries', int(n_summ[a]), '{:,}')
    show(f'{a}: inline comments', int(n_cm[a]), '{:,}')
show('table totals: PRs', int(n_pr.sum()), '{:,}')
show('table totals: reviewed PRs', int(n_rev.sum()), '{:,}')
show('table totals: reviewed share (%)', round(n_rev.sum() / n_pr.sum() * 100, 1))
show('table totals: reviews', int(n_events.sum()), '{:,}')
show('table totals: summaries', int(n_summ.sum()), '{:,}')
show('table totals: inline comments', int(n_cm.sum()), '{:,}')

# ---- reviewed PRs by configuration ---------------------------------------
print('\n== Reviewed PRs (configurations)')
conf = np.where(prof.review_config.isin(['same', 'cross', 'same+cross']), 'only AI',
                np.where(prof.review_config == 'human', 'only human', 'both'))
prof = prof.assign(conf=conf)
n = len(prof)
counts = prof.conf.value_counts()
show('humans alone', int(counts['only human']), '{:,}')
show('humans and AI together', int(counts['both']), '{:,}')
show('AI alone', int(counts['only AI']), '{:,}')
show('with at least one AI review', int(prof.conf.isin(['only AI', 'both']).sum()), '{:,}')
show('AI-only share (%)', round(counts['only AI'] / n * 100, 1))
show('humans-alone share (%)', round(counts['only human'] / n * 100, 1))
show('humans-and-AI share (%)', round(counts['both'] / n * 100, 1))
show('at-least-one-AI share (%)', round(prof.conf.isin(['only AI', 'both']).mean() * 100, 1))

tab = pd.crosstab(prof.authoring_agent, prof.conf)
chi2, p, dof, _ = chi2_contingency(tab)
show('configuration x agent chi2', round(chi2, 1), '{:,.1f}')
show('configuration x agent df', dof)
show('configuration x agent V', round(cramers_v(chi2, n, tab), 2))
show('configuration x agent p', p, '{:.1e}')
agents = prof.groupby('authoring_agent').conf.value_counts(normalize=True).unstack(fill_value=0) * 100
show('AI-only share, Copilot (%)', round(agents.loc['Copilot', 'only AI'], 1))
show('AI-only share, Codex (%)', round(agents.loc['OpenAI_Codex', 'only AI'], 1))
show('human-only share, Devin (%)', round(agents.loc['Devin', 'only human'], 1))
ai_any = prof.assign(ai=prof.conf.isin(['only AI', 'both'])).groupby('authoring_agent').ai.mean() * 100
others = ai_any.drop('Devin')
show('AI-on-AI share, min among four (%)', round(others.min(), 1))
show('AI-on-AI share, max among four (%)', round(others.max(), 1))
show('AI-on-AI share, Devin (%)', round(ai_any['Devin'], 1))
show('with-humans share, Copilot (%)', round(agents.loc['Copilot', 'both'], 1))

sub = prof[prof.task_type.isin(TASKS)]
tab = pd.crosstab(sub.task_type, sub.conf)
chi2, p, dof, _ = chi2_contingency(tab)
show('configuration x task chi2', round(chi2, 1), '{:,.1f}')
show('configuration x task df', dof)
show('configuration x task V', round(cramers_v(chi2, len(sub), tab), 2))
show('configuration x task p', p, '{:.1e}')
tasks = sub.groupby('task_type').conf.value_counts(normalize=True).unstack(fill_value=0) * 100
for t in ['ci', 'refactor', 'chore', 'test', 'feat', 'docs']:
    show(f'AI-only share, {t} (%)', round(tasks.loc[t, 'only AI'], 1))
show('human-only share, build (%)', round(tasks.loc['build', 'only human'], 1))
show('human-only share, ci (%)', round(tasks.loc['ci', 'only human'], 1))

# ---- AI-on-AI review events ----------------------------------------------
print('\n== AI-on-AI review types')
ai_ev = ev[ev.actor.isin(['same-system', 'cross-system'])]
show('AI-on-AI events', len(ai_ev), '{:,}')
show('AI-on-AI share of events (%)', round(len(ai_ev) / len(ev) * 100, 1))
show('same-system events', int((ev.actor == 'same-system').sum()), '{:,}')
show('cross-system events', int((ev.actor == 'cross-system').sum()), '{:,}')
show('same-system share of AI-on-AI (%)', round((ev.actor == 'same-system').sum() / len(ai_ev) * 100, 1))
show('cross-system share of AI-on-AI (%)', round((ev.actor == 'cross-system').sum() / len(ai_ev) * 100, 1))

tab = pd.crosstab(ai_ev.authoring_agent, ai_ev.actor)
chi2, p, dof, _ = chi2_contingency(tab)
show('type x agent chi2', round(chi2, 1), '{:,.1f}')
show('type x agent df', dof)
show('type x agent V', round(cramers_v(chi2, len(ai_ev), tab), 2))
show('type x agent p', p, '{:.1e}')
shares = ai_ev.groupby('authoring_agent').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
show('same-system share, Copilot (%)', round(shares.loc['Copilot', 'same-system'], 1))
show('same-system share, Cursor (%)', round(shares.loc['Cursor', 'same-system'], 1))
show('same-system share, Claude (%)', round(shares.loc['Claude_Code', 'same-system'], 1))
allrev = ev.groupby('authoring_agent').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
show('human share of Devin PR reviews (%)', round(allrev.loc['Devin', 'human'], 1))
show('cross share of Codex PR reviews (%)', round(allrev.loc['OpenAI_Codex', 'cross-system'], 1))

tab = pd.crosstab(ai_ev[ai_ev.task_type.isin(TASKS)].task_type, ai_ev[ai_ev.task_type.isin(TASKS)].actor)
chi2, p, dof, _ = chi2_contingency(tab)
show('type x task chi2', round(chi2, 1), '{:,.1f}')
show('type x task df', dof)
show('type x task V', round(cramers_v(chi2, tab.values.sum(), tab), 2))
show('type x task p', p, '{:.1e}')
tshares = ai_ev[ai_ev.task_type.isin(TASKS)].groupby('task_type').actor.value_counts(normalize=True).unstack(fill_value=0) * 100
for t in ['chore', 'ci', 'feat', 'test', 'fix', 'docs']:
    show(f'same-system share, {t} (%)', round(tshares.loc[t, 'same-system'], 1))

# ---- pairings ------------------------------------------------------------
print('\n== Review pairings')
same = ev[ev.actor == 'same-system']
pairs = same.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
show('Copilot-to-Copilot events', int(pairs.get(('Copilot', 'Copilot'), 0)), '{:,}')
show('Cursor-to-Cursor events', int(pairs.get(('Cursor', 'Cursor'), 0)), '{:,}')
show('Claude-to-Claude events', int(pairs.get(('Claude Code', 'Claude_Code'), 0)))
show('Copilot share of same-system (%)', round(pairs.get(('Copilot', 'Copilot'), 0) / len(same) * 100, 1))
show('Copilot-to-Copilot share of all AI-on-AI (%)', round(pairs.get(('Copilot', 'Copilot'), 0) / len(ai_ev) * 100, 1))
show('Claude Code events as reviewer', int((ev.reviewer_system == 'Claude Code').sum()))
cross = ev[ev.actor == 'cross-system']
show('reviewing systems in cross-system', cross.reviewer_system.nunique())
cpairs = cross.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
show('cross-system pairings', len(cpairs))
for r, a in [('Copilot', 'OpenAI_Codex'), ('CodeRabbit', 'OpenAI_Codex'),
             ('Cursor', 'Devin'), ('Gemini Code Assist', 'OpenAI_Codex')]:
    show(f'{r.split()[0]} on {a} events', int(cpairs.get((r, a), 0)), '{:,}')
show('six largest pairings share (%)', round(cpairs.head(6).sum() / len(cross) * 100, 1))
show('singleton pairings (of the tail)', int((cpairs.iloc[6:] == 1).sum()))
show('tail pairings', len(cpairs) - 6)
show('Copilot cross-system events', int((cross.reviewer_system == 'Copilot').sum()), '{:,}')
show('Copilot share of cross-system (%)', round((cross.reviewer_system == 'Copilot').sum() / len(cross) * 100, 1))
show('CodeRabbit cross-system events', int((cross.reviewer_system == 'CodeRabbit').sum()), '{:,}')
show('CodeRabbit share of cross-system (%)', round((cross.reviewer_system == 'CodeRabbit').sum() / len(cross) * 100, 1))
cside = cross.authoring_agent.value_counts(normalize=True) * 100
for a in ['OpenAI_Codex', 'Devin', 'Cursor', 'Copilot']:
    show(f'cross-system on {a} (%)', round(cside[a], 1))

# ---- account identification ----------------------------------------------
print('\n== AI-reviewer accounts')
show('candidates from the platform bot flag', int((acc.source == 'bot flag').sum()))
show('candidates kept as AI reviewers', int(((acc.source == 'bot flag') & (acc.role == 'AI reviewer')).sum()))
show('candidates excluded as automation', int((acc.role == 'excluded automation').sum()))
show('accounts added by name inspection', int((acc.source == 'name inspection').sum()))
show('AI accounts in total', int((acc.role == 'AI reviewer').sum()))
