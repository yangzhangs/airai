#!/usr/bin/env python3
"""Recompute the statistics of RQ3 (Sec. 3.3) from this package alone and check
each recomputed figure against the value the paper reports.

Sources: data/common/pr_review_profile.csv (one row per reviewed PR with its
review configuration), curated_pr_metadata.csv (authoring agent, merge
outcome), review_events_final.csv (events, verdicts, timestamps) and the role
coding in data/rq3/ (labels of record in doublecoding/roles_full_final.csv,
bodies in doublecoding/roles_blind_full.csv, third-party names pseudonymized).

The logistic regression behind Table 3 and the joint test of its task controls
are recomputed by scripts/rq3/presence_regression.py.

Run from the package root:  python3 scripts/rq3/human_loop_statistics.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu

DATA = Path(__file__).resolve().parents[2] / 'data'

prof = pd.read_csv(DATA / 'common' / 'pr_review_profile.csv', low_memory=False)
meta = pd.read_csv(DATA / 'common' / 'curated_pr_metadata.csv', low_memory=False).set_index('id')
ev = pd.read_csv(DATA / 'common' / 'review_events_final.csv', low_memory=False)
cm = pd.read_csv(DATA / 'common' / 'review_comments_final.csv', low_memory=False)
sub = meta.reindex(prof.pr_id)
prof['authoring_agent'] = sub.agent.values
prof['is_merged'] = sub.is_merged.values
wait = lambda created, later: (pd.to_datetime(later, utc=True) - pd.to_datetime(created, utc=True)).dt.total_seconds() / 3600

AI = prof[prof.any_same | prof.any_cross]
E = ev[ev.pr_id.isin(set(AI.pr_id))].copy()
E['wait'] = wait(E.pr_id.map(meta.created_at).values, E.submitted_at)

FAILS = []


def check(name, paper, got, fmt='{:g}'):
    ok = fmt.format(got) == fmt.format(paper)
    print(f'{name:52s} paper {fmt.format(paper):>12s} | recomputed {fmt.format(got):>12s}'
          + ('' if ok else '   <-- MISMATCH'))
    if not ok:
        FAILS.append(name)


# ---- sampling design (Sec. 2.4) -------------------------------------------
n0 = 1.96 ** 2 * 0.25 / 0.05 ** 2   # Cochran (1977), as in Sec. 2.3
frame = cm[cm.is_human_reply & cm.pr_id.isin(set(AI.pr_id))]
check('human replies in the frame', 1787, len(frame), '{:,}')
check('Cochran sample for the reply frame', 316, round(n0 / (1 + (n0 - 1) / 1787)))

# ---- human presence -------------------------------------------------------
print('\n== Human presence')
only_ai = AI[~AI.any_human]
check('AI-on-AI PRs', 4386, len(AI), '{:,}')
check('AI-only reviewed PRs', 1983, len(only_ai), '{:,}')
check('no human event share (%)', 45.2, round((~AI.any_human).mean() * 100, 1))
check('cross-system only', 1741, int(((only_ai.any_cross) & (~only_ai.any_same)).sum()), '{:,}')
check('same-system only', 205, int(((only_ai.any_same) & (~only_ai.any_cross)).sum()), '{:,}')
check('both types, AI-only', 37, int((only_ai.any_same & only_ai.any_cross).sum()))
check('human present PRs', 2403, int(AI.any_human.sum()), '{:,}')
check('human present share (%)', 54.8, round(AI.any_human.mean() * 100, 1))
same = prof[prof.any_same]; cross = prof[prof.any_cross]
check('PRs with same-system review', 1930, len(same), '{:,}')
check('human present among same-system PRs (%)', 87.5, round(same.any_human.mean() * 100, 1))
check('PRs with cross-system review', 2517, len(cross), '{:,}')
check('human present among cross-system PRs (%)', 29.4, round(cross.any_human.mean() * 100, 1))
check('AI-only PRs authored by Codex', 1159, int((only_ai.authoring_agent == 'OpenAI_Codex').sum()), '{:,}')
check('PRs with both review types', 61, int((prof.any_same & prof.any_cross).sum()))
check('both-types share (%)', 1.4, round((AI.any_same & AI.any_cross).mean() * 100, 1))
check('AI-only PRs without line-anchored content', 940, int((~only_ai.any_inline).sum()), '{:,}')
check('without line-anchored content share (%)', 47.4, round((~only_ai.any_inline).mean() * 100, 1))

# ---- verdicts (Table 4) ---------------------------------------------------
print('\n== Review verdicts')
va = E.state == 'APPROVED'; vc = E.state == 'CHANGES_REQUESTED'
for actor, n_ev, n_verdict, appr, chg in [
        ('same-system', 7292, 0, 0, 0), ('cross-system', 4401, 161, 63, 98), ('human', 9258, 3732, 2753, 979)]:
    a = E[E.actor == actor]
    check(f'{actor} events on AI-on-AI PRs', n_ev, len(a), '{:,}')
    check(f'{actor} events with a verdict', n_verdict, int((a.state.isin(['APPROVED', 'CHANGES_REQUESTED'])).sum()), '{:,}')
    check(f'{actor} approvals', appr, int(((a.state == 'APPROVED')).sum()), '{:,}')
    check(f'{actor} requests changes', chg, int(((a.state == 'CHANGES_REQUESTED')).sum()), '{:,}')
check('cross-system verdict share (%)', 3.7, round((E[E.actor == 'cross-system'].state.isin(['APPROVED', 'CHANGES_REQUESTED'])).mean() * 100, 1))
check('human verdict share (%)', 40.3, round((E[E.actor == 'human'].state.isin(['APPROVED', 'CHANGES_REQUESTED'])).mean() * 100, 1))
hp = E[E.actor == 'human'].groupby('pr_id').state.apply(lambda s: s.isin(['APPROVED', 'CHANGES_REQUESTED']).any())
hap = E[(E.actor == 'human') & va].pr_id.unique(); hch = E[(E.actor == 'human') & vc].pr_id.unique()
check('PRs with a human approval', 1599, len(hap), '{:,}')
check('PRs with a human request-changes', 529, len(hch), '{:,}')
check('human approval share of AI-on-AI PRs (%)', 36.5, round(len(hap) / len(AI) * 100, 1))
check('human request-changes share (%)', 12.1, round(len(hch) / len(AI) * 100, 1))
check('human-review PRs with a verdict', 1844, int(hp.sum()), '{:,}')
check('human-review PRs with a verdict share (%)', 76.7, round(hp.mean() * 100, 1))
check('PRs with both human verdicts', 284, len(set(hap) & set(hch)))
aiv = E[(E.actor != 'human') & (va | vc)].pr_id.unique()
check('PRs with an AI verdict', 103, len(aiv))
check('AI-verdict share of AI-on-AI PRs (%)', 2.3, round(len(aiv) / len(AI) * 100, 1))

# ---- merge outcomes -------------------------------------------------------
print('\n== Merge outcomes')
merged = AI.is_merged
check('approval PRs merged (%)', 87.2, round(AI[AI.pr_id.isin(hap)].is_merged.mean() * 100, 1))
check('approval PRs merged (n)', 1394, int(AI[AI.pr_id.isin(hap)].is_merged.sum()), '{:,}')
check('request-changes PRs merged (%)', 53.9, round(AI[AI.pr_id.isin(hch)].is_merged.mean() * 100, 1))
check('request-changes PRs merged (n)', 285, int(AI[AI.pr_id.isin(hch)].is_merged.sum()), '{:,}')
no_verdict = AI[AI.any_human & ~AI.pr_id.isin(set(hap) | set(hch))]
check('no-verdict human PRs', 559, len(no_verdict), '{:,}')
check('no-verdict human PRs merged (%)', 38.1, round(no_verdict.is_merged.mean() * 100, 1))
check('no-verdict human PRs merged (n)', 213, int(no_verdict.is_merged.sum()), '{:,}')
both = set(hap) & set(hch)
check('request-changes with approval merge (%)', 78.5, round(AI[AI.pr_id.isin(both)].is_merged.mean() * 100, 1))
check('request-changes without approval PRs (n)', 245, len(set(hch) - both))
check('request-changes without approval merge (%)', 25.3, round(AI[AI.pr_id.isin(set(hch) - both)].is_merged.mean() * 100, 1))
ap = E[(E.actor == 'human') & va].copy()
ap['merged_at'] = ap.pr_id.map(meta.merged_at)
onm = ap[ap.merged_at.notna()]
check('human approvals before the merge (%)', 99.8, round((pd.to_datetime(onm.submitted_at, utc=True) < pd.to_datetime(onm.merged_at, utc=True)).mean() * 100, 1))
check('AI-only PRs merged (%)', 65.2, round(only_ai.is_merged.mean() * 100, 1))
check('AI-only PRs merged (n)', 1292, int(only_ai.is_merged.sum()), '{:,}')
byagent = only_ai.groupby('authoring_agent').is_merged.mean() * 100
check('AI-only merge, Copilot (%)', 48.1, round(byagent['Copilot'], 1))
check('AI-only merge, Codex (%)', 71.9, round(byagent['OpenAI_Codex'], 1))
check('AI-only merge, agent range', '48.1-71.9', f"{byagent.min():.1f}-{byagent.max():.1f}", '{:s}')
unrev = meta[~meta.index.isin(set(prof.pr_id))]
check('unreviewed curated PRs', 25549, len(unrev), '{:,}')
check('unreviewed curated merge (%)', 71.1, round(unrev.is_merged.mean() * 100, 1))
check('merged AI-on-AI PRs', 2961, int(merged.sum()), '{:,}')
no_hv = ~hp.reindex(AI.pr_id).fillna(False).astype(bool).values
check('merged with no human verdict', 1505, int((merged.values & no_hv).sum()), '{:,}')
check('merged with no human verdict share (%)', 50.8, round((merged.values & no_hv).sum() / merged.values.sum() * 100, 1))

# ---- timing ---------------------------------------------------------------
print('\n== Timing')
m = {a: round(E[E.actor == a].wait.median(), 1) for a in ['cross-system', 'same-system', 'human']}
check('event arrival median, cross (h)', 0.1, m['cross-system'])
check('event arrival median, same (h)', 4.7, m['same-system'])
check('event arrival median, human (h)', 16.2, m['human'])
g = [E[E.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
check('event arrival Kruskal-Wallis H', 3670.5, round(kruskal(*g).statistic, 1), '{:,.1f}')
# on a shared first timestamp the human event takes precedence, so an AI event
# counts as first only when it strictly precedes the first human event
E['ai_rank'] = (E.actor != 'human').astype(int)
first = E.sort_values(['submitted_at', 'ai_rank'], kind='mergesort').groupby('pr_id').first()
fs = first.actor.value_counts(normalize=True) * 100
check('first event cross-system (%)', 53.8, round(fs['cross-system'], 1))
check('first event human (%)', 33.8, round(fs['human'], 1))
check('first event same-system (%)', 12.4, round(fs['same-system'], 1))
# the median first event is read per actor: each actor's own first event per PR
fa = E.sort_values('submitted_at', kind='mergesort').groupby(['pr_id', 'actor']).first().reset_index()
fm = fa.groupby('actor').wait.median().round(2)
check('median first event, cross (h)', 0.04, fm['cross-system'], '{:g}')
check('median first event, same (h)', 1.2, round(fm['same-system'], 1))
check('median first event, human (h)', 1.8, round(fm['human'], 1))
human_prs = set(AI[AI.any_human].pr_id)
check('AI first among human-carrying PRs (%)', 38.2, round(first.loc[list(human_prs)].actor.ne('human').mean() * 100, 1))
tt = {a: round((E[E.actor == a].wait > 24).mean() * 100, 1) for a in ['human', 'same-system', 'cross-system']}
check('tail >24h, human (%)', 40.7, tt['human'])
check('tail >24h, same (%)', 28.9, tt['same-system'])
check('tail >24h, cross (%)', 14.0, tt['cross-system'])

# ---- reply roles ----------------------------------------------------------
print('\n== Reply roles')
rf = pd.read_csv(DATA / 'rq3' / 'doublecoding' / 'roles_full_final.csv', comment='#')
rb = pd.read_csv(DATA / 'rq3' / 'doublecoding' / 'roles_blind_full.csv', comment='#')
d = rb.merge(rf, left_on='reply_id', right_on='unit_id')
d['agent'] = d.pr_id.map(meta.agent)
check('sampled human replies', 316, len(d))
sh = d.label.value_counts(normalize=True) * 100
for role, v in [('code feedback', 27.8), ('direction to an agent', 24.7), ('decision', 19.0),
                ('brief remark', 15.8), ('question', 12.7)]:
    check(f'{role} share (%)', v, round(sh[role], 1))
cf = d[d.label == 'code feedback']; dr = d[d.label == 'direction to an agent']
qu = d[d.label == 'question']; de = d[d.label == 'decision']; br = d[d.label == 'brief remark']
check('code feedback units', 88, len(cf))
check('code feedback carrying a code span (%)', 35.2, round(cf.reply_body.str.contains('`', regex=False).mean() * 100, 1))
check('direction units', 78, len(dr))
check('direction carrying a handle (%)', 44.9, round(dr.reply_body.str.contains(r'@[A-Za-z0-9_-]+', regex=True).mean() * 100, 1))
NAMES = {'Copilot': 'copilot', 'Devin': 'devin', 'OpenAI_Codex': 'codex', 'Cursor': 'cursor', 'Claude_Code': 'claude'}
names_self = [bool(re.search(NAMES.get(a, '(?!)'), b, re.I)) if isinstance(a, str) else False
              for a, b in zip(dr.agent, dr.reply_body)]
check('directions naming the authoring agent', 32, int(np.sum(names_self)))
to_human = d.parent_review_pairing == 'human_review'
check('direction answering a human comment', 72, int((~dr.parent_review_pairing.ne('human_review')).sum()))
check('replies to a human comment', 271, int(to_human.sum()))
hh = d[to_human]
check('code feedback among replies to humans (%)', 28.4, round((hh.label == 'code feedback').mean() * 100, 1))
check('code feedback is the modal role among replies to humans', 'code feedback', hh.label.mode()[0], '{:s}')
check('decision units', 60, len(de))
check('decisions answering an AI comment', 15, int(de.parent_review_pairing.ne('human_review').sum()))
check('question units', 40, len(qu))
check('questions carrying a question mark (%)', 75.0, round(qu.reply_body.str.contains(r'\?', regex=True).mean() * 100, 1))
check('brief remark units', 50, len(br))

print()
if FAILS:
    print('MISMATCHES:', ', '.join(FAILS))
    sys.exit(1)
print('all RQ3 figures match the paper.')
