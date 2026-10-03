#!/usr/bin/env python3
"""Verify the statistics quoted in the paper from this package alone.

Run:  python3 scripts/verify_statistics.py
Reads only data/ in this directory; writes nothing.

Coverage. Recomputed from the released tables: the RQ1 review configurations,
review-type shares and pairings; the RQ2 review-form shares, inline length and
arrival statistics, the function taxonomy over the coded samples and the
sampling sizes; the RQ3 presence, verdict, merge and timing statistics, and the
reply-role sample and distribution.

Two families cannot be recomputed here because they need the review summary
text (`pr_reviews.body`), which the package does not redistribute under the
GitHub content policy: the per-agent summary counts of Table 1 (and with them
the summary-text splits of Table 2 and the summary length/arrival statistics of
Section 3.2.1). For those, this script checks the published counts as carried
by the tables.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

D = Path(__file__).resolve().parent.parent / 'data'

ev = pd.read_csv(f'{D}/review_events_final.csv', parse_dates=['submitted_at'], low_memory=False)
cm = pd.read_csv(f'{D}/review_comments_final.csv', parse_dates=['created_at'], low_memory=False)
meta = pd.read_csv(f'{D}/curated_pr_metadata.csv', parse_dates=['created_at', 'merged_at'], low_memory=False).set_index('id')
prof = pd.read_csv(f'{D}/pr_review_profile.csv')
prof['task'] = prof.pr_id.map(meta['task_type'])
prof['merged'] = prof.pr_id.map(meta['is_merged']).astype(int)

# PR creation time attached to every review event
ev = ev.merge(meta[['created_at']].rename(columns={'created_at': 'pr_created'}),
              left_on='pr_id', right_index=True, how='left')
ev['hours'] = (ev.submitted_at - ev.pr_created).dt.total_seconds() / 3600

P = prof[prof.any_same | prof.any_cross]          # the 4,386 AI-on-AI reviewed PRs
Pids = set(P.pr_id)
evp = ev[ev.pr_id.isin(Pids)]                     # events on those PRs
ai = ev[ev.actor != 'human']
same, cross = ev[ev.actor == 'same-system'], ev[ev.actor == 'cross-system']

conf3 = prof.review_config.map({'human': 'human-only', 'same': 'AI-only', 'cross': 'AI-only',
    'same+cross': 'AI-only', 'same+human': 'human+AI', 'cross+human': 'human+AI',
    'same+cross+human': 'human+AI'})
prof['conf3'] = conf3


def line(tag, got, paper=None):
    p = f'   paper: {paper}' if paper else ''
    print(f'{tag:44s} {got}{p}')


def chi(tab, label, paper):
    chi2, p, df, _ = chi2_contingency(tab)
    n = tab.values.sum(); r, c = tab.shape
    V = np.sqrt(chi2 / (n * (min(r, c) - 1)))
    print(f"{label:36s} chi2={chi2:9.1f} df={df} V={V:.2f}   paper: {paper}")


print('== RQ1: configurations, review types, pairings ==')
line('reviewed PRs', f'{len(prof):,}', '8,047')
for k, want in [('human-only', '3,661 (45.5%)'), ('human+AI', '2,403 (29.9%)'), ('AI-only', '1,983 (24.6%)')]:
    m = conf3 == k
    line(f'  {k}', f'{int(m.sum()):,} = {m.mean()*100:.1f}%', want)
line('AI-on-AI reviewed PRs', f'{len(P):,} = {len(P)/len(prof)*100:.1f}%', '4,386 (54.5%)')
line('AI-on-AI review events', f'{len(ai):,} of {len(ev):,} = {len(ai)/len(ev)*100:.1f}%', '11,693 (40.7%)')

for ag, want in [('Copilot', 'AI-only 3.8%, Both 60.1%'),
                 ('OpenAI_Codex', 'AI-only 49.6%'),
                 ('Devin', 'AI-on-AI 26.1%, human-only 73.9%')]:
    sel = prof.authoring_agent == ag
    g = prof[sel]
    line(f'  {ag}: of its reviewed PRs', f'AI-on-AI {(g.any_same | g.any_cross).mean()*100:.1f}%, '
         f'AI-only {conf3[sel].eq("AI-only").mean()*100:.1f}%, Both {conf3[sel].eq("human+AI").mean()*100:.1f}%, '
         f'human-only {conf3[sel].eq("human-only").mean()*100:.1f}%', want)

ss = ai.groupby('authoring_agent')['actor'].apply(lambda s: (s == 'same-system').mean() * 100)
line('same-system share of a PR\'s AI reviews, by author', ' '.join(f'{k} {v:.1f}%' for k, v in ss.items()),
     'Copilot 99.2, Cursor 45.7, Claude 0.4, Codex 0, Devin 0')
rv = same.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
line('same-system pairings', ', '.join(f'{a}/{b} {n}' for (a, b), n in rv.items()),
     'Copilot/Copilot 6,867, Cursor/Cursor 424, Claude Code 1')
line('Copilot share of same-system events', f'{rv.iloc[0]/len(same)*100:.1f}%', '94.2%')
line('Copilot-on-Copilot share of all AI-on-AI events', f'{rv.iloc[0]/len(ai)*100:.1f}%', '58.7%')
line('Claude Code as reviewer, all events', f'{(ev.reviewer_system == "Claude Code").sum()}', '55')
line('Devin-authored PR reviews: human share', f"{ev[ev.authoring_agent=='Devin'].actor.eq('human').mean()*100:.1f}%", '79.2%')
line('Codex-authored PR reviews: cross-system share', f"{ev[ev.authoring_agent=='OpenAI_Codex'].actor.eq('cross-system').mean()*100:.1f}%", '53.7%')

pc = cross.groupby(['reviewer_system', 'authoring_agent']).size().sort_values(ascending=False)
line('cross top pairs', ', '.join(f'{a}/{b.split("_")[-1]} {n}' for (a, b), n in pc.head(4).items()),
     'Copilot/Codex 898, CodeRabbit/Codex 752, Cursor/Devin 519, Gemini/Codex 259')
line('cross-system diversity', f'{cross.reviewer_system.nunique()} systems, {len(pc)} pairings', '30 systems, 67 pairings')
line('  six largest pairs', f'{pc.head(6).sum()/len(cross)*100:.1f}%', '62.9%')
line('  single-event pairings', f'{int((pc == 1).sum())}', '15 of 61')
by_sys = cross.reviewer_system.value_counts()
line('  two busiest systems', f'Copilot {by_sys.iloc[0]} ({by_sys.iloc[0]/len(cross)*100:.1f}%), '
     f'CodeRabbit {by_sys.iloc[1]} ({by_sys.iloc[1]/len(cross)*100:.1f}%)', '1,190 (27.0%), 1,029 (23.4%)')
tgt = cross.authoring_agent.value_counts(normalize=True) * 100
tname = {'OpenAI_Codex': 'Codex', 'Claude_Code': 'Claude Code'}
line('  cross events by target author', ' '.join(f'{tname.get(k, k)} {v:.1f}%' for k, v in tgt.items()),
     'Codex 55.4, Devin 26.4, Cursor 11.4, Copilot 1.2')

print('\n== Table 1 (recomputable columns) ==')
rev = prof.groupby('authoring_agent').size()
revs = ev.groupby('authoring_agent').size()
inl = cm[cm.pr_id.isin(set(prof.pr_id))]
inl_by = inl.pr_id.map(meta['agent']).value_counts()
want_t1 = {'Copilot': '2,705 / 16,209 / 15,220', 'Cursor': '727 / 1,727 / 1,336', 'Devin': '2,089 / 5,581 / 4,821',
           'Claude_Code': '189 / 652 / 1,159', 'OpenAI_Codex': '2,337 / 4,545 / 3,907'}
for ag in want_t1:
    line(f'  {ag}', f'reviewed {rev[ag]} / reviews {revs[ag]} / inline {inl_by[ag]}', want_t1[ag])
line('  totals', f'{len(prof):,} reviewed ({len(prof)/len(meta)*100:.1f}% of {len(meta):,}), '
     f'{len(ev):,} reviews, {len(inl):,} inline', '8,047 (24.0%), 28,714, 26,443')
line('  summaries column', 'not recomputable from the package (needs pr_reviews.body)', '7,780 total')

print('\n== inferential statistics ==')
keep10 = ~prof.task.isin(['other', 'revert'])
chi(pd.crosstab(prof.authoring_agent, conf3), 'config x agent (PRs)', '3,063.2 df=8 V=0.44')
chi(pd.crosstab(prof.task[keep10], conf3[keep10]), 'config x task (PRs)', '115.5 df=18 V=0.08')
chi(pd.crosstab(ai.authoring_agent, ai.actor), 'same/cross x agent (events)', '10,480.3 df=4 V=0.95')
_t = ai[~ai.task_type.isin(['other', 'revert'])]
chi(pd.crosstab(_t.task_type, _t.actor), 'same/cross x task (events)', '247.2 df=9 V=0.15')
t3 = pd.DataFrame([[6329, 657, 306, 0], [608, 2059, 1673, 61], [8976, 2438, 647, 4960]],
                  index=['same-system', 'cross-system', 'human'],
                  columns=['inline only', 'summary only', 'both', 'bare verdict'])
chi(t3, 'form x actor (Table 2 counts, as published)', '13,166.9 df=6 V=0.48')

print('\n== RQ2: form shares derived from the published Table 2 counts ==')
line('written-content events, AI-on-AI', f'{11693-61} of 11,693 = {(11693-61)/11693*100:.1f}%', '11,632 (99.5%)')
line('written-content events, human', f'{17021-4960} of 17,021 = {(17021-4960)/17021*100:.1f}%', '12,061 (70.9%)')
line('same-system events with a summary', f'{657+306} of 7,292 = {(657+306)/7292*100:.1f}%', '13.2%')
line('cross-system events with a summary', f'{2059+1673} of 4,401 = {(2059+1673)/4401*100:.1f}%', '84.8%')

print('\n== RQ2: inline length ==')
g = [cm[cm.owner_actor == k].char_length.dropna() for k in ['same-system', 'cross-system', 'human']]
H, _ = kruskal(*g)
line('inline length medians', f'same {g[0].median():.0f}, cross {g[1].median():.0f}, human {g[2].median():.0f} (H={H:.1f})',
     '163 / 575 / 77 (H=10,180.1)')
pooled = cm[cm.owner_actor.isin(['same-system', 'cross-system'])].char_length.dropna()
line('AI-on-AI comments, median', f'{pooled.median():.0f}', '233, about 3x the human median')
line('comments over 1,000 chars', f'cross {(g[1]>1000).mean()*100:.1f}%, same {(g[0]>1000).mean()*100:.1f}%, '
     f'human {(g[2]>1000).mean()*100:.1f}%', '38.5 / 0.8 / 0.7%')

print('\n== RQ2: inline arrival time (review events carrying inline comments) ==')
evi = ev[ev.id.isin(set(cm.pull_request_review_id.dropna().astype('int64')))]
gi = [evi[evi.actor == k].hours.dropna() for k in ['cross-system', 'same-system', 'human']]
H, _ = kruskal(*gi)
line('inline arrival medians, hours', f'cross {gi[0].median():.2f}, same {gi[1].median():.2f}, human {gi[2].median():.2f} (H={H:.1f})',
     '0.2 / 5.4 / 12.6 (H=1,475.2)')
line('inside the first hour', f'cross {(gi[0]<1).mean()*100:.1f}%, same {(gi[1]<1).mean()*100:.1f}%, '
     f'human {(gi[2]<1).mean()*100:.1f}%', '62.5 / 21.3 / 24.0%')
# the Copilot example in the paper is computed per inline comment (cm.created_at)
com = cm.merge(prof[['pr_id', 'authoring_agent']], on='pr_id', how='left')
com = com.merge(meta[['created_at']].rename(columns={'created_at': 'pc'}), left_on='pr_id', right_index=True, how='left')
com['hours'] = (com.created_at - com.pc).dt.total_seconds() / 3600
cpc = com[com.authoring_agent == 'Copilot']
line('  Copilot-authored PRs (per inline comment)',
     f'cross {cpc[cpc.owner_actor=="cross-system"].hours.median():.1f}h vs '
     f'same {cpc[cpc.owner_actor=="same-system"].hours.median():.1f}h', '74.8 vs 5.2')
line('  summary length / arrival', 'not recomputable from the package (needs pr_reviews.body)', '1,956/1,723/46 chars; 0.1/1.2/6.7 h')

print('\n== RQ2: sampling sizes (Cochran, 95% CI, 5% margin) ==')
z = 1.96; n0 = z * z * 0.25 / 0.05 ** 2
for N, want in [(7005, 364), (5130, 357), (963, 275), (3732, 348), (1787, 316)]:
    n = n0 / (1 + (n0 - 1) / N)
    line(f'  population {N:,}', f'n={n:.1f} -> {round(n)}', f'{want}')

CAT = {'improvement suggestion': 'B', 'code-issue feedback': 'B',
       'workflow/verification report': 'B', 'change acknowledgment': 'C',
       'response to feedback': 'D', 'clarification/question': 'D',
       'agent instruction': 'D', 'platform notice': 'E', 'other': 'E', 'explanation': 'A'}
def cat5(s): return s.str.strip().str.lower().map(CAT)
inl6 = pd.read_csv(f'{D}/labeling_full_coded.csv')
same6 = cat5(inl6[inl6.rtype == 'Self-review'].code).value_counts()
cross_sample = pd.read_csv(f'{D}/cross_inline_sample_coded.csv')
cross6 = cat5(cross_sample['code']).value_counts()   # 357 units
t6 = pd.DataFrame([[same6.get(k, 0) for k in 'ABCDE'], [cross6.get(k, 0) for k in 'ABCDE']],
                  index=['same-system', 'cross-system'], columns=list('ABCDE'))
chi(t6, 'function x type (inline)', '594.3 df=4 V=0.91')

SUM = {'findings digest': 'A', 'change overview': 'A', 'explanation': 'A',
       'improvement suggestion': 'B', 'verification report': 'B',
       'approval verdict': 'C', 'agent instruction': 'D', 'response to feedback': 'D',
       'clarification': 'D', 'other': 'E', 'review unavailable': 'E', 'platform notice': 'E'}
def cat5m(s, m): return s.str.strip().str.lower().map(m)
smr = pd.read_csv(f'{D}/rq2_summary_sample_coded.csv')
smr = smr[smr.actor_kind == 'same-system']
cross_summary_frame = pd.read_csv(f'{D}/cross_summary_sample_coded.csv')
srow = cat5m(smr.summary_code, SUM).value_counts()
xc = cat5m(cross_summary_frame['code'], SUM).value_counts()
t7 = pd.DataFrame([[srow.get(k, 0) for k in 'ABCDE'], [xc.get(k, 0) for k in 'ABCDE']],
                  index=['same-system', 'cross-system'], columns=list('ABCDE'))
t7 = t7.loc[:, t7.sum() > 0]
chi(t7, 'function x type (summaries)', '23.7 df=4 V=0.20')

print('\n== RQ2 taxonomy (the four strata) ==')
n_same_inl = int((inl6.rtype == 'Self-review').sum()); n_cross_inl = int(cross6.sum())
n_same_sum = int(srow.sum()); n_cross_sum = int(xc.sum())
tot = n_same_inl + n_cross_inl + n_same_sum + n_cross_sum
line('strata n', f'same-inline {n_same_inl}, cross-inline {n_cross_inl}, same-summary {n_same_sum}, '
     f'cross-summary {n_cross_sum} | total {tot}', '364 / 357 / 275 / 348 | 1,344')
sums = t7.sum(axis=0).add(t6.sum(axis=0), fill_value=0)
line('A-E counts', ' '.join(f'{k} {int(sums[k])} ({sums[k]/tot*100:.1f}%)' for k in 'ABCDE'),
     'A 525 39.1%, B 382 28.4%, C 306 22.8%, D 91 6.8%, E 40 3.0%')
line('cross inline shares', ' '.join(f'{k} {cross6.get(k,0)/cross6.sum()*100:.1f}%' for k in 'ABCDE'),
     'A 0.0%, B 96.9%, C 0.8%, D 0.6%, E 1.7%')
leaves = pd.concat([inl6[inl6.rtype == 'Self-review'].code, cross_sample['code'],
                    smr.summary_code, cross_summary_frame['code']]).str.strip().str.lower().value_counts()
want_leaf = {'findings digest': 197, 'change overview': 317, 'explanation': 11, 'improvement suggestion': 347,
             'code-issue feedback': 24, 'workflow/verification report': 11, 'change acknowledgment': 239,
             'approval verdict': 67, 'response to feedback': 87, 'clarification/question': 4}
leaf_b3 = leaves.get('workflow/verification report', 0) + leaves.get('verification report', 0)
leaf_d2 = leaves.get('clarification/question', 0) + leaves.get('clarification', 0)
line('leaf counts', ' '.join(
    f'{k}: {leaf_b3 if k == "workflow/verification report" else leaf_d2 if k == "clarification/question" else leaves.get(k, 0)}'
    for k in want_leaf), ' / '.join(f'{k} {v}' for k, v in want_leaf.items()))
line('  E (other)', f'{int(leaves.get("platform notice", 0) + leaves.get("other", 0) + leaves.get("review unavailable", 0))}', '40')

print('\n== RQ3: presence ==')
nh = P[~P.any_human]
line('AI-on-AI PRs with no human review event', f'{len(nh):,} = {len(nh)/len(P)*100:.1f}%', '1,983 (45.2%)')
line('  cross-only / same-only / both', f'{int((P.any_cross & ~P.any_same & ~P.any_human).sum())} / '
     f'{int((P.any_same & ~P.any_cross & ~P.any_human).sum())} / {int((P.any_same & P.any_cross & ~P.any_human).sum())}',
     '1,741 / 205 / 37')
line('  with a human reviewer', f'{int(P.any_human.sum()):,} = {P.any_human.mean()*100:.1f}%', '2,403 (54.8%)')
gs, gc = P[P.any_same], P[P.any_cross]
line('human review present, same-system PRs', f'{int(gs.any_human.sum())} of {len(gs)} = {gs.any_human.mean()*100:.1f}%', '1,930: 87.5%')
line('human review present, cross-system PRs', f'{int(gc.any_human.sum())} of {len(gc)} = {gc.any_human.mean()*100:.1f}%', '2,517: 29.4%')
line('  overlap (both review types)', f'{int((P.any_same & P.any_cross).sum())} = {(P.any_same & P.any_cross).mean()*100:.1f}%', '61 (1.4%)')
line('  AI-only PRs, Codex-authored', f'{int((nh.authoring_agent == "OpenAI_Codex").sum())} of {len(nh)}', '1,159 of 1,983')
line('  AI-only PRs with no line-anchored content', f'{int((~nh.pr_id.isin(set(cm.pr_id))).sum())} = '
     f'{(~nh.pr_id.isin(set(cm.pr_id))).mean()*100:.1f}%', '940 (47.4%)')

print('\n== RQ3: verdicts (Table 4, on the 4,386 AI-on-AI PRs) ==')
line('events on those PRs', f'same {int(evp.actor.eq("same-system").sum()):,}, '
     f'cross {int(evp.actor.eq("cross-system").sum()):,}, human {int(evp.actor.eq("human").sum()):,}',
     '7,292 / 4,401 / 9,258')
hv = evp[evp.actor == 'human']
cv = evp[(evp.actor == 'cross-system') & evp.state.isin(['APPROVED', 'CHANGES_REQUESTED'])]
ap = set(hv[hv.state == 'APPROVED'].pr_id); rc = set(hv[hv.state == 'CHANGES_REQUESTED'].pr_id)
line('cross-system events carrying a verdict', f'{len(cv)} = {len(cv)/int(evp.actor.eq("cross-system").sum())*100:.1f}% '
     f'({int((cv.state=="APPROVED").sum())} approvals / {int((cv.state=="CHANGES_REQUESTED").sum())} changes)', '161 (3.7%): 63 / 98')
hv_verdict = hv.state.isin(['APPROVED', 'CHANGES_REQUESTED'])
line('human events carrying a verdict', f'{int(hv_verdict.sum())} of {len(hv):,} = {hv_verdict.mean()*100:.1f}% '
     f'({int((hv.state=="APPROVED").sum())} approvals / {int((hv.state=="CHANGES_REQUESTED").sum())} changes)',
     '3,732 (40.3%): 2,753 / 979')
line('PRs with human approval / request', f'{len(ap)} ({len(ap)/len(P)*100:.1f}%) / {len(rc)} ({len(rc)/len(P)*100:.1f}%)',
     '1,599 (36.5%) / 529 (12.1%)')
line('  both / at least one', f'{len(ap & rc)} / {len(ap | rc)} ({len(ap | rc)/int(P.any_human.sum())*100:.1f}% '
     f'of those with human review)', '284 / 1,844 (76.7%)')
line('PRs with an AI verdict', f'{cv.pr_id.nunique()} = {cv.pr_id.nunique()/len(P)*100:.1f}%', '103 (2.3%)')

print('\n== RQ3: merge outcomes ==')
m = prof.set_index('pr_id')['merged']
for name, ids, want in [('human approval', ap & Pids, '1,599 -> 87.2%'),
                        ('request for changes', rc & Pids, '529 -> 53.9%'),
                        ('human events, no verdict', (evp[evp.actor == 'human'].pr_id.pipe(set) & Pids) - ap - rc, '559 -> 38.1%'),
                        ('no human event', Pids - set(hv.pr_id), '1,983 -> 65.2%')]:
    row = [i for i in ids if i in m.index]
    line(f'  {name}', f'{len(row):,} merged {m.loc[row].mean()*100:.1f}%', want)
line('  request+approval vs request only',
     f'{m.loc[[i for i in (ap & rc) & Pids]].mean()*100:.1f}% vs {m.loc[[i for i in (rc - ap) & Pids]].mean()*100:.1f}%',
     '284: 78.5% vs 245: 25.3%')
bef = hv[hv.state == 'APPROVED'].merge(meta[['merged_at']], left_on='pr_id', right_index=True)
bef = bef[bef.merged_at.notna()]
line('  approvals before the merge', f'{(bef.submitted_at < bef.merged_at).mean()*100:.1f}%', '99.8%')
tot_merge = int(m.loc[sorted(Pids)].sum())
nover = [i for i in Pids if i not in ap and i not in rc]
line('  merges without any human verdict', f'{int(m.loc[nover].sum())} of {tot_merge} = {int(m.loc[nover].sum())/tot_merge*100:.1f}%',
     '1,505 of 2,961 (50.8%)')
for ag, want in [('Copilot', '48.1%'), ('OpenAI_Codex', '71.9%')]:
    g = nh[nh.authoring_agent == ag]
    line(f'  AI-only merges, {ag}', f'{m.loc[list(g.pr_id)].mean()*100:.1f}%', want)
never = [i for i in meta.index if i not in set(prof.pr_id)]
line('  never reviewed (curated)', f'{len(never):,} merged {meta.loc[never, "is_merged"].mean()*100:.1f}%', '71.1%')

print('\n== RQ3: timing (events on the 4,386 AI-on-AI PRs) ==')
for k, want in [('cross-system', '0.1 h'), ('same-system', '4.7 h'), ('human', '16.2 h')]:
    line(f'  median event, {k}', f'{evp[evp.actor==k].hours.median():.2f} h', want)
fp = evp.groupby(['pr_id', 'actor']).hours.min().unstack()
who = fp[['cross-system', 'same-system', 'human']].idxmin(axis=1)
line('  first event', 'cross %.1f%%, human %.1f%%, same %.1f%%' % (
     (who == 'cross-system').mean()*100, (who == 'human').mean()*100, (who == 'same-system').mean()*100),
     '53.8 / 33.8 / 12.4%')
line('  median first event', 'cross %.2f, same %.2f, human %.2f h' % tuple(
     fp[k].median() for k in ['cross-system', 'same-system', 'human']), '0.04 / 1.2 / 1.8 h')
hp = fp[fp['human'].notna()]
line('  AI event before the first human one', f'{(hp[["cross-system","same-system"]].min(axis=1) < hp["human"]).mean()*100:.1f}% '
     f'of {len(hp):,}', '38.2% of 2,403')
line('  tail over a day', ' '.join(f'{a} {(evp[evp.actor==a].hours>24).mean()*100:.1f}%' for a in ['human', 'same-system', 'cross-system']),
     'human 40.7 / same 28.9 / cross 14.0%')

print('\n== RQ3: reply roles ==')
frame = cm[cm.pr_id.isin(Pids) & cm.is_human_reply]
line('human replies in scope', f'{len(frame):,}', '1,787')
ff = pd.read_csv(f'{D}/doublecoding/roles_full_final.csv')
vc = ff.label.str.strip().str.lower().value_counts()
line('coded sample', f'{len(ff)}', '316')
line('role shares', ' '.join(f'{k} {v} ({v/len(ff)*100:.1f}%)' for k, v in vc.items()),
     'code feedback 88 (27.8%), direction 78 (24.7%), decision 60 (19.0%), brief remark 50 (15.8%), question 40 (12.7%)')

print('\nall checks printed above; compare each line against the paper.')
