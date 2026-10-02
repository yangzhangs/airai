#!/usr/bin/env python3
"""Recompute the statistics quoted in the paper from this package alone.

Run:  python3 scripts/verify_statistics.py
Reads only data/ in this directory. The raw AIDev tables are needed only to
re-derive the event table itself (scripts/22_build_review_episodes.py).

Note: review-form counts (Table 2) are verified from the counts as published,
because the summary-text flag of a review lives in the AIDev pr_reviews.body,
whose text this package does not redistribute (GitHub content policy);
data/review_comments_final.csv carries comment lengths and reply flags instead.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

D = Path(__file__).resolve().parent.parent / 'data'
ev = pd.read_csv(f'{D}/review_events_final.csv')
prof = pd.read_csv(f'{D}/pr_review_profile.csv')
cm = pd.read_csv(f'{D}/review_comments_final.csv')
meta = pd.read_csv(f'{D}/curated_pr_metadata.csv').set_index('id')
prof['task'] = prof.pr_id.map(meta['task_type'])
prof['merged'] = prof.pr_id.map(meta['is_merged']).astype(int)

conf3 = prof.review_config.map({'human': 'human-only', 'same': 'AI-only', 'cross': 'AI-only',
    'same+cross': 'AI-only', 'same+human': 'human+AI', 'cross+human': 'human+AI',
    'same+cross+human': 'human+AI'})
keep10 = ~prof.task.isin(['other', 'revert'])

def chi(tab, label, paper):
    chi2, p, df, _ = chi2_contingency(tab)
    n = tab.values.sum(); r, c = tab.shape
    V = np.sqrt(chi2 / (n * (min(r, c) - 1)))
    print(f"{label:36s} chi2={chi2:9.1f} df={df} V={V:.2f}   paper: {paper}")

print('== inferential statistics ==')
chi(pd.crosstab(prof.authoring_agent, conf3), 'config x agent (PRs)', '3,063.2 df=8 V=0.44')
chi(pd.crosstab(prof.task[keep10], conf3[keep10]), 'config x task (PRs)', '115.5 df=18 V=0.08')
_ai = ev[ev.actor != 'human']
chi(pd.crosstab(_ai.authoring_agent, _ai.actor), 'same/cross x agent (events)', '10,480.3 df=4 V=0.95')
_t = ev[~ev.task_type.isin(['other', 'revert'])]
_t = _t[_t.actor != 'human']
chi(pd.crosstab(_t.task_type, _t.actor), 'same/cross x task (events)', '247.2 df=9 V=0.15')
t3 = pd.DataFrame([[6329, 657, 306, 0], [608, 2059, 1673, 61], [8976, 2438, 647, 4960]],
                  index=['same-system', 'cross-system', 'human'],
                  columns=['inline only', 'summary only', 'both', 'bare verdict'])
chi(t3, 'form x actor (Table 2 counts)', '13,166.9 df=6 V=0.48')

CAT = {'improvement suggestion': 'B', 'code-issue feedback': 'B',
       'workflow/verification report': 'B', 'change acknowledgment': 'C',
       'response to feedback': 'D', 'clarification/question': 'D',
       'agent instruction': 'D', 'platform notice': 'E', 'other': 'E', 'explanation': 'A'}
def cat5(s): return s.str.strip().str.lower().map(CAT)
inl = pd.read_csv(f'{D}/labeling_full_coded.csv')
same = cat5(inl[inl.rtype == 'Self-review'].code).value_counts()
cross_sample = pd.read_csv(f'{D}/cross_inline_sample_coded.csv')
cross = cat5(cross_sample['code']).value_counts()   # 357 units (Section 2.3)
t6 = pd.DataFrame([[same.get(k, 0) for k in 'ABCDE'],
                   [cross.get(k, 0) for k in 'ABCDE']],
                  index=['same-system', 'cross-system'], columns=list('ABCDE'))
chi(t6, 'function x type (inline)', '594.3 df=4 V=0.91')
smr = pd.read_csv(f'{D}/rq2_summary_sample_coded.csv')
acc = pd.read_csv(f'{D}/ai_reviewer_accounts.csv')
acc_ai = set(acc.loc[acc.role == 'AI reviewer', 'user'])
smr = smr[smr.actor_kind == 'same-system']          # same-system summaries
cross_sum_frame = pd.read_csv(f'{D}/cross_summary_sample_coded.csv')
SUM = {'findings digest': 'A', 'change overview': 'A', 'explanation': 'A',
       'improvement suggestion': 'B', 'verification report': 'B',
       'approval verdict': 'C', 'agent instruction': 'D', 'response to feedback': 'D',
       'clarification': 'D', 'other': 'E', 'review unavailable': 'E', 'platform notice': 'E'}
def srow(k):
    c = cat5_map(smr[smr.actor_kind == k].summary_code, SUM).value_counts()
    return [c.get(x, 0) for x in 'ABCDE']
def cat5_map(s, m): return s.str.strip().str.lower().map(m)
xc = cat5_map(cross_sum_frame['code'], SUM).value_counts()
t7 = pd.DataFrame([srow('same-system'), [xc.get(x, 0) for x in 'ABCDE']],
                  index=['same-system', 'cross-system'], columns=list('ABCDE'))
t7 = t7.loc[:, t7.sum() > 0]   # no Interactive/directive for same-system summaries
chi(t7, 'function x type (summaries)', '23.7 df=4 V=0.20')

print('\n== RQ2 taxonomy (the four strata) ==')
n_same_inl = int((inl.rtype == 'Self-review').sum()); n_cross_inl = int(cross.sum())
n_same_sum = int((smr.actor_kind == 'same-system').sum()); n_cross_sum = int(xc.sum())
tot = n_same_inl + n_cross_inl + n_same_sum + n_cross_sum
sums = t7.sum(axis=0).add(t6.sum(axis=0), fill_value=0)
print(f"strata n: same-inline {n_same_inl}, cross-inline {n_cross_inl}, "
      f"same-summary {n_same_sum}, cross-summary {n_cross_sum} | total {tot} (paper 1,344)")
print('A-E: ' + ', '.join(f"{k} {int(sums[k])} ({sums[k]/tot*100:.1f}%)" for k in 'ABCDE')
      + '   (paper: A 525 39.1%, B 382 28.4%, C 306 22.8%, D 91 6.8%, E 40 3.0%)')
print('cross-system inline shares: ' + ', '.join(
    f"{k} {cross.get(k, 0)/cross.sum()*100:.1f}%" for k in 'ABCDE')
      + '   (paper: A 0.0%, B 96.9%, C 0.8%, D 0.6%, E 1.7%)')

print('\n== descriptive statistics ==')
print(f"reviewed PRs: {len(prof):,} of {len(meta):,} curated ({len(prof)/len(meta)*100:.1f}%)")
ai_pr = prof[prof.any_same | prof.any_cross]
print(f"AI-reviewed PRs: {len(ai_pr):,} = {len(ai_pr)/len(prof)*100:.1f}% of reviewed, "
      f"{len(ai_pr)/len(meta)*100:.1f}% of curated")
per = ai_pr.groupby('authoring_agent').size()
for ag in per.index:
    n = int((meta.agent == ag).sum())
    print(f"  {ag:14s} {int(per[ag]):5d}/{n:6,} = {per[ag]/n*100:.1f}% of curated")
g = [cm[cm.owner_actor == k].char_length.dropna() for k in ['same-system', 'cross-system', 'human']]
H, p = kruskal(*g)
print(f"\ninline length Kruskal H={H:.1f}; medians {[round(float(x.median())) for x in g]} (paper 163/575/77)")
print('>1000 chars: cross %.1f%% same %.1f%% human %.1f%%; human<=100: %.1f%%'
      % ((g[1] > 1000).mean() * 100, (g[0] > 1000).mean() * 100,
         (g[2] > 1000).mean() * 100, (g[2] <= 100).mean() * 100))
pc = ev[ev.actor == 'cross-system'].groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
print(f"\ncross-system: {ev[ev.actor == 'cross-system'].reviewer_system.nunique()} systems, "
      f"{len(pc)} pairings, top-6 {pc.head(6).sum()/pc.sum()*100:.1f}%, single-event {(pc == 1).sum()}")
tgt = ev[ev.actor == 'cross-system'].authoring_agent.value_counts(normalize=True) * 100
print('cross targets %:', {k: round(v, 1) for k, v in tgt.items()})

ai_set = set(prof[prof.review_config != 'human'].pr_id)
print('\n== reply rates (RQ3 scope: the AI-on-AI reviewed PRs) ==')
ai_ids = set(prof[prof.review_config != 'human'].pr_id)
Cs = cm[cm.pr_id.isin(ai_ids)]
roots_hit = set(Cs[Cs.is_human_reply].in_reply_to_id.dropna().astype(int))
Cs = Cs.assign(got=Cs.id.isin(roots_hit))  # root comments that drew >=1 human reply
tab = Cs.groupby('owner_actor')['got'].agg(['size', 'sum', 'mean'])
print(tab.to_string())
print('(paper: 72/7,005 = 1.0%, 234/5,130 = 4.6%, 971/9,286 = 10.5%)')

print('\n== merge outcomes (RQ3 scope) ==')
appr = set(ev[(ev.actor == 'human') & (ev.state == 'APPROVED')].pr_id) & ai_set
req = set(ev[(ev.actor == 'human') & (ev.state == 'CHANGES_REQUESTED')].pr_id) & ai_set
hum = set(ev[ev.actor == 'human'].pr_id) & ai_set
none_ = ai_set - hum
m = prof.set_index('pr_id')['merged']
for name, ids in [('human approval', appr), ('request for changes', req),
                  ('human events, no verdict', hum - appr - req), ('no human event', none_)]:
    ids = [i for i in ids if i in m.index]
    print(f"  {name:28s} {len(ids):5d}  merged {m.loc[ids].mean()*100:.1f}%")
never = [i for i in meta.index if i not in set(prof.pr_id)]
print(f"  {'never reviewed (curated)':28s} {len(never):5d}  merged {meta.loc[never, 'is_merged'].mean()*100:.1f}%")
