#!/usr/bin/env python3
"""Recompute the statistics of RQ2 (Sec. 3.2) from this package alone and check
each recomputed figure against the value the paper reports.

Sources: data/common/review_events_final.csv (events), review_summary_meta.csv
(whether a review carries summary text and its character count),
review_comments_final.csv (inline comments with their lengths), the four coded
samples in data/rq2/ (with data/rq2/rq2_sample_shares.json holding the released
per-stratum function shares) and data/rq2/full_corpus_inline_rule_coded.csv
(the rule-coded inline corpus used for the robustness check).

Run from the package root:  python3 scripts/rq2/characteristics_statistics.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, kruskal, mannwhitneyu

DATA = Path(__file__).resolve().parents[2] / 'data'

ev = pd.read_csv(DATA / 'common' / 'review_events_final.csv', low_memory=False)
sm = pd.read_csv(DATA / 'common' / 'review_summary_meta.csv', low_memory=False)
cm = pd.read_csv(DATA / 'common' / 'review_comments_final.csv', low_memory=False)
meta = pd.read_csv(DATA / 'common' / 'curated_pr_metadata.csv', low_memory=False)
EV = ev.merge(sm, on='id')
sub = meta.set_index('id')
EV['has_inline'] = EV.id.isin(set(cm.pull_request_review_id.dropna().astype('int64')))
EV['form'] = np.where(EV.has_inline & EV.has_summary, 'both',
                      np.where(EV.has_inline, 'inline only',
                               np.where(EV.has_summary, 'summary only', 'verdict-only')))
wait = lambda created, later: (pd.to_datetime(later, utc=True) - pd.to_datetime(created, utc=True)).dt.total_seconds() / 3600
EV['wait'] = wait(sub.created_at.reindex(EV.pr_id).values, EV.submitted_at)

FAILS = []


def check(name, paper, got, fmt='{:g}'):
    ok = fmt.format(got) == fmt.format(paper)
    print(f'{name:52s} paper {fmt.format(paper):>12s} | recomputed {fmt.format(got):>12s}'
          + ('' if ok else '   <-- MISMATCH'))
    if not ok:
        FAILS.append(name)


def cramers_v(chi2, n, table):
    return np.sqrt(chi2 / (n * (min(table.shape) - 1)))


def r_rb(a, b):
    U = mannwhitneyu(np.asarray(a, float), np.asarray(b, float), alternative='two-sided')
    return U.statistic, 2 * U.statistic / (len(a) * len(b)) - 1


# ---- review form (Table 2) ------------------------------------------------
print('== Review form')
tab = EV.groupby(['actor', 'form']).size().unstack(fill_value=0)
row = tab.loc['same-system']
check('same-system inline only', 6329, row['inline only'], '{:,}')
check('same-system summary only', 657, row['summary only'], '{:,}')
check('same-system both', 306, row['both'], '{:,}')
check('same-system verdict-only', 0, row['verdict-only'], '{:,}')
row = tab.loc['cross-system']
check('cross-system inline only', 608, row['inline only'], '{:,}')
check('cross-system summary only', 2059, row['summary only'], '{:,}')
check('cross-system both', 1673, row['both'], '{:,}')
check('cross-system verdict-only', 61, row['verdict-only'], '{:,}')
row = tab.loc['human']
check('human inline only', 8976, row['inline only'], '{:,}')
check('human summary only', 2438, row['summary only'], '{:,}')
check('human both', 647, row['both'], '{:,}')
check('human verdict-only', 4960, row['verdict-only'], '{:,}')
check('column totals inline only', 15913, int(tab['inline only'].sum()), '{:,}')
check('column totals summary only', 5154, int(tab['summary only'].sum()), '{:,}')
check('column totals both', 2626, int(tab['both'].sum()), '{:,}')
check('column totals verdict-only', 5021, int(tab['verdict-only'].sum()), '{:,}')
ai = EV[EV.actor != 'human']
check('AI-on-AI inline-only share (%)', 59.3, round((ai.form == 'inline only').mean() * 100, 1))
check('AI-on-AI with-summary share (%)', 40.2, round(ai.form.isin(['both', 'summary only']).mean() * 100, 1))
check('AI-on-AI with written content (%)', 99.5, round(ai.form.ne('verdict-only').mean() * 100, 1))
check('human with written content (%)', 70.9, round(EV[EV.actor == 'human'].form.ne('verdict-only').mean() * 100, 1))
chi2, p, dof, _ = chi2_contingency(tab)
check('form x actor chi2', 13166.9, round(chi2, 1), '{:,.1f}')
check('form x actor df', 6, dof)
check('form x actor V', 0.48, round(cramers_v(chi2, len(EV), tab), 2))
check('same-system with-summary share (%)', 13.2, round((tab.loc['same-system', 'both'] + tab.loc['same-system', 'summary only']) / tab.loc['same-system'].sum() * 100, 1))
check('cross-system with-summary share (%)', 84.8, round((tab.loc['cross-system', 'both'] + tab.loc['cross-system', 'summary only']) / tab.loc['cross-system'].sum() * 100, 1))

# ---- review length --------------------------------------------------------
print('\n== Review length')
med = {a: int(cm[cm.owner_actor == a].char_length.median()) for a in ['cross-system', 'same-system', 'human']}
check('cross-system comment median (chars)', 575, med['cross-system'])
check('same-system comment median (chars)', 163, med['same-system'])
check('human comment median (chars)', 77, med['human'])
tail = {a: round((cm[cm.owner_actor == a].char_length > 1000).mean() * 100, 1) for a in med}
check('cross-system comments >1,000 chars (%)', 38.5, tail['cross-system'])
check('same-system comments >1,000 chars (%)', 0.8, tail['same-system'])
check('human comments >1,000 chars (%)', 0.7, tail['human'])
check('AI-on-AI comment median (chars)', 233, int(cm[cm.owner_actor != 'human'].char_length.median()))
g = [cm[cm.owner_actor == a].char_length.values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
check('comment length Kruskal-Wallis H', 10180.1, round(H.statistic, 1), '{:,.1f}')
check('comment length KW df', 2, len(g) - 1)
ps = [mannwhitneyu(g[i], g[j], alternative='two-sided').pvalue for i, j in [(0, 1), (0, 2), (1, 2)]]
check('comment pairwise p all below Bonferroni', True, all(p < 0.05 / 3 for p in ps))

smd = EV[EV.has_summary]
L = lambda a: smd[smd.actor == a].summary_chars.values.astype(float)
check('cross-system summary median (chars)', 1968, int(np.median(L('cross-system'))))
check('same-system summary median (chars)', 1723, int(np.median(L('same-system'))))
check('human summary median (chars)', 46, int(np.median(L('human'))))
U, r = r_rb(L('cross-system'), L('same-system'))
check('summary p cross vs same', 7.8e-07, mannwhitneyu(L('cross-system'), L('same-system'), alternative='two-sided').pvalue, '{:.1e}')
check('summary |r| cross vs same', 0.1, round(abs(r), 2))
check('summary |r| cross vs human', 0.93, round(abs(r_rb(L('cross-system'), L('human'))[1]), 2))
check('summary |r| same vs human', 0.91, round(abs(r_rb(L('same-system'), L('human'))[1]), 2))

# ---- review arrival time (event level) ------------------------------------
print('\n== Review arrival time')
E_inl, E_sum = EV[EV.has_inline], EV[EV.has_summary]
m = {a: round(E_inl[E_inl.actor == a].wait.median(), 1) for a in ['cross-system', 'same-system', 'human']}
check('inline arrival median, cross (h)', 0.2, m['cross-system'])
check('inline arrival median, same (h)', 5.4, m['same-system'])
check('inline arrival median, human (h)', 12.6, m['human'])
fh = {a: round((E_inl[E_inl.actor == a].wait < 1).mean() * 100, 1) for a in m}
check('inline inside first hour, cross (%)', 62.5, fh['cross-system'])
check('inline inside first hour, same (%)', 21.3, fh['same-system'])
check('inline inside first hour, human (%)', 24.0, fh['human'])
g = [E_inl[E_inl.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
check('inline arrival Kruskal-Wallis H', 1475.2, round(H.statistic, 1), '{:,.1f}')
check('inline arrival |r| cross vs same', 0.49, round(abs(r_rb(g[0], g[1])[1]), 2))
check('inline arrival |r| cross vs human', 0.49, round(abs(r_rb(g[0], g[2])[1]), 2))
tt = {a: round((E_inl[E_inl.actor == a].wait > 24).mean() * 100, 1) for a in m}
check('inline tail >24h, human (%)', 37.5, tt['human'])
check('inline tail >24h, same (%)', 29.7, tt['same-system'])
check('inline tail >24h, cross (%)', 17.3, tt['cross-system'])
m = {a: round(E_sum[E_sum.actor == a].wait.median(), 1) for a in ['cross-system', 'same-system', 'human']}
check('summary arrival median, cross (h)', 0.1, m['cross-system'])
check('summary arrival median, same (h)', 1.2, m['same-system'])
check('summary arrival median, human (h)', 6.7, m['human'])
fh = {a: round((E_sum[E_sum.actor == a].wait < 1).mean() * 100, 1) for a in m}
check('summary inside first hour, cross (%)', 70.1, fh['cross-system'])
check('summary inside first hour, same (%)', 48.7, fh['same-system'])
check('summary inside first hour, human (%)', 28.4, fh['human'])
g = [E_sum[E_sum.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
check('summary arrival Kruskal-Wallis H', 1734.7, round(H.statistic, 1), '{:,.1f}')
check('summary arrival |r| cross vs same', 0.43, round(abs(r_rb(g[0], g[1])[1]), 2))
check('summary arrival |r| cross vs human', 0.57, round(abs(r_rb(g[0], g[2])[1]), 2))
# the Copilot example is read per inline comment on Copilot-authored PRs
cop = cm[(cm.pr_id.map(meta.set_index('id').agent) == 'Copilot') & (cm.owner_actor != 'human')].copy()
cop['wait'] = wait(cop.pr_id.map(meta.set_index('id').created_at).values, cop.created_at)
check('comment arrival on Copilot PRs, cross (h)', 74.8, round(cop[cop.owner_actor == 'cross-system'].wait.median(), 1))
check('comment arrival on Copilot PRs, same (h)', 5.2, round(cop[cop.owner_actor == 'same-system'].wait.median(), 1))

# ---- review functions -----------------------------------------------------
print('\n== Review functions')
si = pd.read_csv(DATA / 'rq2' / 'same_system_inline_coded.csv', comment='#')
ci = pd.read_csv(DATA / 'rq2' / 'cross_system_inline_coded.csv', comment='#')
ss = pd.read_csv(DATA / 'rq2' / 'same_system_summary_coded.csv', comment='#')
cs = pd.read_csv(DATA / 'rq2' / 'cross_system_summary_coded.csv', comment='#')
check('coded units in total', 1344, len(si) + len(ci) + len(ss) + len(cs), '{:,}')
check('same-system inline sample', 364, len(si))
check('cross-system inline sample', 357, len(ci))
check('same-system summary sample', 275, len(ss))
check('cross-system summary sample', 348, len(cs))

FUNC = {
    'findings digest': 'Descriptive', 'change overview': 'Descriptive',
    'Explanation': 'Descriptive', 'explanation': 'Descriptive',
    'Improvement suggestion': 'Code-directed', 'improvement suggestion': 'Code-directed',
    'Code-issue feedback': 'Code-directed', 'code-issue feedback': 'Code-directed',
    'Workflow/verification report': 'Code-directed', 'workflow/verification report': 'Code-directed',
    'verification report': 'Code-directed',
    'Change acknowledgment': 'Confirmatory', 'change acknowledgment': 'Confirmatory',
    'approval verdict': 'Confirmatory',
    'Response to feedback': 'Interactive/directive', 'response to feedback': 'Interactive/directive',
    'Clarification/question': 'Interactive/directive', 'clarification/question': 'Interactive/directive',
    'clarification': 'Interactive/directive',
    'Other': 'Other', 'other': 'Other', 'platform notice': 'Other', 'review unavailable': 'Other',
}
leaves = pd.concat([si.code, ci.code, ss.summary_code, cs.code]).map(FUNC)
cats = leaves.value_counts()
check('Descriptive units', 525, int(cats['Descriptive']), '{:,}')
check('Code-directed units', 382, int(cats['Code-directed']), '{:,}')
check('Confirmatory units', 306, int(cats['Confirmatory']), '{:,}')
check('Interactive/directive units', 91, int(cats['Interactive/directive']), '{:,}')
check('Other units', 40, int(cats['Other']), '{:,}')
sh = leaves.value_counts(normalize=True) * 100
for c, v in [('Descriptive', 39.1), ('Code-directed', 28.4), ('Confirmatory', 22.8), ('Interactive/directive', 6.8), ('Other', 3.0)]:
    check(f'{c} share (%)', v, round(sh[c], 1))
leafsh = pd.concat([si.code, ci.code, ss.summary_code, cs.code]).str.lower().value_counts(normalize=True) * 100
for leaf, v in [('findings digest', 14.7), ('change overview', 23.6), ('explanation', 0.8),
                ('improvement suggestion', 25.8), ('code-issue feedback', 1.8),
                ('change acknowledgment', 17.8), ('approval verdict', 5.0),
                ('response to feedback', 6.5)]:
    check(f'leaf {leaf} share (%)', v, round(leafsh.get(leaf, 0), 1))
ver = leafsh.get('workflow/verification report', 0) + leafsh.get('verification report', 0)
check('leaf verification report share (%)', 0.8, round(ver, 1))
cq = leafsh.get('clarification/question', 0) + leafsh.get('clarification', 0)
check('leaf clarification/question share (%)', 0.3, round(cq, 1))
check('descriptive+confirmatory share (%)', 61.8, round(sh['Descriptive'] + sh['Confirmatory'], 1))

# type comparison, per stratum (adjudicated codes against the released shares)
for label, codes in [('same-inline', si.code), ('cross-inline', ci.code),
                     ('same-summary', ss.summary_code), ('cross-summary', cs.code)]:
    shares = codes.map(FUNC).value_counts(normalize=True) * 100
    released = json.load(open(DATA / 'rq2' / 'rq2_sample_shares.json'))
    strat, kind = label.split('-')
    rel = released[kind][f'{strat}-system']
    ok = all(round(shares.get(k, 0), 1) == v for k, v in rel.items())
    check(f'{label} shares match released json', True, ok)
summ_tab = pd.DataFrame({'same-system': ss.summary_code.map(FUNC).value_counts(),
                         'cross-system': cs.code.map(FUNC).value_counts()}).fillna(0)
sm_sh = (summ_tab / summ_tab.sum() * 100).round(1)
check('summary descriptive, same (%)', 89.1, sm_sh.loc['Descriptive', 'same-system'])
check('summary descriptive, cross (%)', 77.3, sm_sh.loc['Descriptive', 'cross-system'])
check('summary confirmatory, cross (%)', 15.2, sm_sh.loc['Confirmatory', 'cross-system'])
check('summary confirmatory, same (%)', 5.1, sm_sh.loc['Confirmatory', 'same-system'])
chi2, p, dof, _ = chi2_contingency(summ_tab.T)
check('summary function x type chi2', 23.7, round(chi2, 1))
check('summary function x type V', 0.20, round(cramers_v(chi2, summ_tab.values.sum(), summ_tab.T), 2))
inl_tab = pd.DataFrame({'same-system': si.code.map(FUNC).value_counts(),
                        'cross-system': ci.code.map(FUNC).value_counts()}).fillna(0)
in_sh = (inl_tab / inl_tab.sum() * 100).round(1)
check('inline confirmatory, same (%)', 64.8, in_sh.loc['Confirmatory', 'same-system'])
check('inline interactive, same (%)', 24.2, in_sh.loc['Interactive/directive', 'same-system'])
check('inline code-directed, same (%)', 8.0, in_sh.loc['Code-directed', 'same-system'])
check('inline code-directed, cross (%)', 96.9, in_sh.loc['Code-directed', 'cross-system'])
check('inline confirmatory, cross (%)', 0.8, in_sh.loc['Confirmatory', 'cross-system'])
chi2, p, dof, _ = chi2_contingency(inl_tab.T)
check('inline function x type chi2', 594.3, round(chi2, 1))
check('inline function x type V', 0.91, round(cramers_v(chi2, inl_tab.values.sum(), inl_tab.T), 2))

# ---- robustness checks ----------------------------------------------------
print('\n== Robustness (composition)')
check('same-system confirmatory share (%)', 64.8, round((si.code.map(FUNC) == 'Confirmatory').mean() * 100, 1))
ci2 = ci.merge(cm[['id', 'pr_id']], on='id')
ci2['agent'] = ci2.pr_id.map(sub.agent)
codedir = ci.code.map(FUNC) == 'Code-directed'
ag = ci2.assign(cd=codedir).groupby('agent').cd.agg(['mean', 'size']) * [100, 1]
check('cross code-directed, Codex units', 193, int(ag.loc['OpenAI_Codex', 'size']))
check('cross code-directed, Codex (%)', 94.8, round(ag.loc['OpenAI_Codex', 'mean'], 1))
check('cross code-directed, Claude units', 45, int(ag.loc['Claude_Code', 'size']))
check('cross code-directed, Claude (%)', 100.0, round(ag.loc['Claude_Code', 'mean'], 1))
check('cross code-directed, max deviation from pooled', 3.1, round(abs(ag['mean'] - 96.9).max(), 1))
cop_cross = ci.merge(cm[['id', 'user']], on='id').query("user == 'Copilot'")
check('Copilot cross comments (n)', 95, len(cop_cross))
check('Copilot cross comments code-directed (%)', 98.9, round((cop_cross.code.map(FUNC) == 'Code-directed').mean() * 100, 1))
full = pd.read_csv(DATA / 'rq2' / 'full_corpus_inline_rule_coded.csv', comment='#', low_memory=False)
CD = {'improvement suggestion', 'code-issue feedback', 'workflow/verification report'}
cop = full[full.authoring_agent == 'Copilot']
same_n, cross_n = cop[cop.reviewer_type == 'same-system'], cop[cop.reviewer_type == 'cross-system']
same_cd = int(same_n.code.isin(CD).sum()); cross_cd = int(cross_n.code.isin(CD).sum())
check('rule-coded Copilot-authored same code-directed (%)', 15.2, round(same_cd / len(same_n) * 100, 1))
check('rule-coded Copilot-authored cross code-directed (%)', 80.9, round(cross_cd / len(cross_n) * 100, 1))
odds, pf = fisher_exact([[same_cd, len(same_n) - same_cd], [cross_cd, len(cross_n) - cross_cd]])
check('rule-coded Fisher p below 1e-22', True, pf < 1e-22)

print()
if FAILS:
    print('MISMATCHES:', ', '.join(FAILS))
    sys.exit(1)
print('all RQ2 figures match the paper.')
