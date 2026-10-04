#!/usr/bin/env python3
"""RQ3 statistics (human presence, verdicts, merge outcomes, timing, reply roles).

Run from the package root:  python3 scripts/rq3/human_loop_statistics.py
"""
import re
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




def show(name, value, fmt='{:g}'):
    print(f'{name:52s} {fmt.format(value):>14s}')


# ---- sampling design ------------------------------------------------------
n0 = 1.96 ** 2 * 0.25 / 0.05 ** 2   # Cochran, as in the RQ2 script
frame = cm[cm.is_human_reply & cm.pr_id.isin(set(AI.pr_id))]
show('human replies in the frame', len(frame), '{:,}')
show('Cochran sample for the reply frame', round(n0 / (1 + (n0 - 1) / len(frame))))

# ---- human presence -------------------------------------------------------
print('\n== Human presence')
only_ai = AI[~AI.any_human]
show('AI-on-AI PRs', len(AI), '{:,}')
show('AI-only reviewed PRs', len(only_ai), '{:,}')
show('no human event share (%)', round((~AI.any_human).mean() * 100, 1))
show('cross-system only', int(((only_ai.any_cross) & (~only_ai.any_same)).sum()), '{:,}')
show('same-system only', int(((only_ai.any_same) & (~only_ai.any_cross)).sum()), '{:,}')
show('both types, AI-only', int((only_ai.any_same & only_ai.any_cross).sum()))
show('human present PRs', int(AI.any_human.sum()), '{:,}')
show('human present share (%)', round(AI.any_human.mean() * 100, 1))
same = prof[prof.any_same]; cross = prof[prof.any_cross]
show('PRs with same-system review', len(same), '{:,}')
show('human present among same-system PRs (%)', round(same.any_human.mean() * 100, 1))
show('PRs with cross-system review', len(cross), '{:,}')
show('human present among cross-system PRs (%)', round(cross.any_human.mean() * 100, 1))
show('AI-only PRs authored by Codex', int((only_ai.authoring_agent == 'OpenAI_Codex').sum()), '{:,}')
show('PRs with both review types', int((prof.any_same & prof.any_cross).sum()))
show('both-types share (%)', round((AI.any_same & AI.any_cross).mean() * 100, 1))
show('AI-only PRs without line-anchored content', int((~only_ai.any_inline).sum()), '{:,}')
show('without line-anchored content share (%)', round((~only_ai.any_inline).mean() * 100, 1))

# ---- verdicts (Table 4) ---------------------------------------------------
print('\n== Review verdicts')
va = E.state == 'APPROVED'; vc = E.state == 'CHANGES_REQUESTED'
for actor in ['same-system', 'cross-system', 'human']:
    a = E[E.actor == actor]
    show(f'{actor} events on AI-on-AI PRs', len(a), '{:,}')
    show(f'{actor} events with a verdict', int((a.state.isin(['APPROVED', 'CHANGES_REQUESTED'])).sum()), '{:,}')
    show(f'{actor} approvals', int((a.state == 'APPROVED').sum()), '{:,}')
    show(f'{actor} requests changes', int((a.state == 'CHANGES_REQUESTED').sum()), '{:,}')
show('cross-system verdict share (%)', round((E[E.actor == 'cross-system'].state.isin(['APPROVED', 'CHANGES_REQUESTED'])).mean() * 100, 1))
show('human verdict share (%)', round((E[E.actor == 'human'].state.isin(['APPROVED', 'CHANGES_REQUESTED'])).mean() * 100, 1))
hp = E[E.actor == 'human'].groupby('pr_id').state.apply(lambda s: s.isin(['APPROVED', 'CHANGES_REQUESTED']).any())
hap = E[(E.actor == 'human') & va].pr_id.unique(); hch = E[(E.actor == 'human') & vc].pr_id.unique()
show('PRs with a human approval', len(hap), '{:,}')
show('PRs with a human request-changes', len(hch), '{:,}')
show('human approval share of AI-on-AI PRs (%)', round(len(hap) / len(AI) * 100, 1))
show('human request-changes share (%)', round(len(hch) / len(AI) * 100, 1))
show('human-review PRs with a verdict', int(hp.sum()), '{:,}')
show('human-review PRs with a verdict share (%)', round(hp.mean() * 100, 1))
show('PRs with both human verdicts', len(set(hap) & set(hch)))
aiv = E[(E.actor != 'human') & (va | vc)].pr_id.unique()
show('PRs with an AI verdict', len(aiv))
show('AI-verdict share of AI-on-AI PRs (%)', round(len(aiv) / len(AI) * 100, 1))

# ---- merge outcomes -------------------------------------------------------
print('\n== Merge outcomes')
merged = AI.is_merged
show('approval PRs merged (%)', round(AI[AI.pr_id.isin(hap)].is_merged.mean() * 100, 1))
show('approval PRs merged (n)', int(AI[AI.pr_id.isin(hap)].is_merged.sum()), '{:,}')
show('request-changes PRs merged (%)', round(AI[AI.pr_id.isin(hch)].is_merged.mean() * 100, 1))
show('request-changes PRs merged (n)', int(AI[AI.pr_id.isin(hch)].is_merged.sum()), '{:,}')
no_verdict = AI[AI.any_human & ~AI.pr_id.isin(set(hap) | set(hch))]
show('no-verdict human PRs', len(no_verdict), '{:,}')
show('no-verdict human PRs merged (%)', round(no_verdict.is_merged.mean() * 100, 1))
show('no-verdict human PRs merged (n)', int(no_verdict.is_merged.sum()), '{:,}')
both = set(hap) & set(hch)
show('request-changes with approval merge (%)', round(AI[AI.pr_id.isin(both)].is_merged.mean() * 100, 1))
show('request-changes without approval PRs (n)', len(set(hch) - both))
show('request-changes without approval merge (%)', round(AI[AI.pr_id.isin(set(hch) - both)].is_merged.mean() * 100, 1))
ap = E[(E.actor == 'human') & va].copy()
ap['merged_at'] = ap.pr_id.map(meta.merged_at)
onm = ap[ap.merged_at.notna()]
show('human approvals before the merge (%)', round((pd.to_datetime(onm.submitted_at, utc=True) < pd.to_datetime(onm.merged_at, utc=True)).mean() * 100, 1))
show('AI-only PRs merged (%)', round(only_ai.is_merged.mean() * 100, 1))
show('AI-only PRs merged (n)', int(only_ai.is_merged.sum()), '{:,}')
byagent = only_ai.groupby('authoring_agent').is_merged.mean() * 100
show('AI-only merge, Copilot (%)', round(byagent['Copilot'], 1))
show('AI-only merge, Codex (%)', round(byagent['OpenAI_Codex'], 1))
show('AI-only merge, agent range', f'{byagent.min():.1f}-{byagent.max():.1f}', '{:s}')
unrev = meta[~meta.index.isin(set(prof.pr_id))]
show('unreviewed curated PRs', len(unrev), '{:,}')
show('unreviewed curated merge (%)', round(unrev.is_merged.mean() * 100, 1))
show('merged AI-on-AI PRs', int(merged.sum()), '{:,}')
no_hv = ~hp.reindex(AI.pr_id).fillna(False).astype(bool).values
show('merged with no human verdict', int((merged.values & no_hv).sum()), '{:,}')
show('merged with no human verdict share (%)', round((merged.values & no_hv).sum() / merged.values.sum() * 100, 1))

# ---- timing ---------------------------------------------------------------
print('\n== Timing')
for a, lab in [('cross-system', 'cross'), ('same-system', 'same'), ('human', 'human')]:
    show(f'event arrival median, {lab} (h)', round(E[E.actor == a].wait.median(), 1))
g = [E[E.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
show('event arrival Kruskal-Wallis H', round(H.statistic, 1), '{:,.1f}')
show('event arrival KW p', H.pvalue, '{:.1e}')
# on a shared first timestamp the human event takes precedence
E['ai_rank'] = (E.actor != 'human').astype(int)
first = E.sort_values(['submitted_at', 'ai_rank'], kind='mergesort').groupby('pr_id').first()
fs = first.actor.value_counts(normalize=True) * 100
show('first event cross-system (%)', round(fs['cross-system'], 1))
show('first event human (%)', round(fs['human'], 1))
show('first event same-system (%)', round(fs['same-system'], 1))
fa = E.sort_values('submitted_at', kind='mergesort').groupby(['pr_id', 'actor']).first().reset_index()
fm = fa.groupby('actor').wait.median().round(2)
show('median first event, cross (h)', fm['cross-system'], '{:g}')
show('median first event, same (h)', round(fm['same-system'], 1))
show('median first event, human (h)', round(fm['human'], 1))
human_prs = set(AI[AI.any_human].pr_id)
show('AI first among human-carrying PRs (%)', round(first.loc[list(human_prs)].actor.ne('human').mean() * 100, 1))
for a, lab in [('human', 'human'), ('same-system', 'same'), ('cross-system', 'cross')]:
    show(f'tail >24h, {lab} (%)', round((E[E.actor == a].wait > 24).mean() * 100, 1))

# ---- reply roles ----------------------------------------------------------
print('\n== Reply roles')
d = pd.read_csv(DATA / 'rq3' / 'doublecoding' / 'roles_full_coded.csv', comment='#')
d['agent'] = d.pr_id.map(meta.agent)
show('sampled human replies', len(d))
sh = d.final.value_counts(normalize=True) * 100
for role in ['code feedback', 'direction to an agent', 'decision', 'brief remark', 'question']:
    show(f'{role} share (%)', round(sh[role], 1))
cf = d[d.final == 'code feedback']; dr = d[d.final == 'direction to an agent']
qu = d[d.final == 'question']; de = d[d.final == 'decision']; br = d[d.final == 'brief remark']
show('code feedback units', len(cf))
show('code feedback carrying a code span (%)', round(cf.reply_body.str.contains('`', regex=False).mean() * 100, 1))
show('direction units', len(dr))
show('direction carrying a handle (%)', round(dr.reply_body.str.contains(r'@[A-Za-z0-9_-]+', regex=True).mean() * 100, 1))
NAMES = {'Copilot': 'copilot', 'Devin': 'devin', 'OpenAI_Codex': 'codex', 'Cursor': 'cursor', 'Claude_Code': 'claude'}
names_self = [bool(re.search(NAMES.get(a, '(?!)'), b, re.I)) if isinstance(a, str) else False
              for a, b in zip(dr.agent, dr.reply_body)]
show('directions naming the authoring agent', int(np.sum(names_self)))
to_human = d.parent_review_pairing == 'human_review'
show('direction answering a human comment', int((~dr.parent_review_pairing.ne('human_review')).sum()))
show('replies to a human comment', int(to_human.sum()))
hh = d[to_human]
show('code feedback among replies to humans (%)', round((hh.final == 'code feedback').mean() * 100, 1))
show('code feedback is the modal role among replies to humans', hh.final.mode()[0], '{:s}')
show('decision units', len(de))
show('decisions answering an AI comment', int(de.parent_review_pairing.ne('human_review').sum()))
show('question units', len(qu))
show('questions carrying a question mark (%)', round(qu.reply_body.str.contains(r'\?', regex=True).mean() * 100, 1))
show('brief remark units', len(br))
