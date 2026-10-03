#!/usr/bin/env python3
"""RQ2 statistics.

Run from the package root:  python3 scripts/rq2/characteristics_statistics.py
"""
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


def show(name, value, fmt='{:g}'):
    print(f'{name:52s} {fmt.format(value):>14s}')


def cramers_v(chi2, n, table):
    return np.sqrt(chi2 / (n * (min(table.shape) - 1)))


def r_rb(a, b):
    U = mannwhitneyu(np.asarray(a, float), np.asarray(b, float), alternative='two-sided')
    return U.statistic, 2 * U.statistic / (len(a) * len(b)) - 1


# ---- sampling design ------------------------------------------------------
print('== Sampling design')
n0 = 1.96 ** 2 * 0.25 / 0.05 ** 2   # Cochran: 95% confidence, 5% margin, p=0.5
pop_inline = cm.owner_actor.value_counts()
pop_summ = EV[EV.has_summary].actor.value_counts()
show('same-system inline population', int(pop_inline['same-system']), '{:,}')
show('cross-system inline population', int(pop_inline['cross-system']), '{:,}')
show('same-system summary population', int(pop_summ['same-system']), '{:,}')
show('cross-system summary population', int(pop_summ['cross-system']), '{:,}')
pops = [int(pop_inline['same-system']), int(pop_inline['cross-system']),
        int(pop_summ['same-system']), int(pop_summ['cross-system'])]
for N in pops:
    show(f'Cochran sample for N={N:,}', round(n0 / (1 + (n0 - 1) / N)))

# ---- review form (Table 2) ------------------------------------------------
print('\n== Review form')
tab = EV.groupby(['actor', 'form']).size().unstack(fill_value=0)
for actor in ['same-system', 'cross-system', 'human']:
    for f in ['inline only', 'summary only', 'both', 'verdict-only']:
        show(f'{actor} {f}', int(tab.loc[actor, f]), '{:,}')
for f in ['inline only', 'summary only', 'both', 'verdict-only']:
    show(f'column totals {f}', int(tab[f].sum()), '{:,}')
ai = EV[EV.actor != 'human']
show('AI-on-AI inline-only events', int(ai.form.eq('inline only').sum()), '{:,}')
show('AI-on-AI with-summary events', int(ai.form.isin(['both', 'summary only']).sum()), '{:,}')
show('AI-on-AI with written content (n)', int(ai.form.ne('verdict-only').sum()), '{:,}')
show('human with written content (n)', int(EV[EV.actor == 'human'].form.ne('verdict-only').sum()), '{:,}')
show('human events in the corpus', int((EV.actor == 'human').sum()), '{:,}')
show('AI-on-AI inline-only share (%)', round((ai.form == 'inline only').mean() * 100, 1))
show('AI-on-AI with-summary share (%)', round(ai.form.isin(['both', 'summary only']).mean() * 100, 1))
show('AI-on-AI with written content (%)', round(ai.form.ne('verdict-only').mean() * 100, 1))
show('human with written content (%)', round(EV[EV.actor == 'human'].form.ne('verdict-only').mean() * 100, 1))
chi2, p, dof, _ = chi2_contingency(tab)
show('form x actor chi2', round(chi2, 1), '{:,.1f}')
show('form x actor df', dof)
show('form x actor V', round(cramers_v(chi2, len(EV), tab), 2))
show('form x actor p', p, '{:.1e}')
show('same-system inline-only share (%)', round(tab.loc['same-system', 'inline only'] / tab.loc['same-system'].sum() * 100, 1))
show('same-system with-summary share (%)', round((tab.loc['same-system', 'both'] + tab.loc['same-system', 'summary only']) / tab.loc['same-system'].sum() * 100, 1))
show('cross-system with-summary share (%)', round((tab.loc['cross-system', 'both'] + tab.loc['cross-system', 'summary only']) / tab.loc['cross-system'].sum() * 100, 1))
show('human inline-only share (%)', round(tab.loc['human', 'inline only'] / tab.loc['human'].sum() * 100, 1))
show('human with-summary share (%)', round((tab.loc['human', 'both'] + tab.loc['human', 'summary only']) / tab.loc['human'].sum() * 100, 1))

# ---- review length --------------------------------------------------------
print('\n== Review length')
med = {a: int(cm[cm.owner_actor == a].char_length.median()) for a in ['cross-system', 'same-system', 'human']}
for a in ['cross-system', 'same-system', 'human']:
    show(f'{a} comment median (chars)', med[a])
    show(f'{a} comments >1,000 chars (%)', round((cm[cm.owner_actor == a].char_length > 1000).mean() * 100, 1))
show('AI-on-AI comment median (chars)', int(cm[cm.owner_actor != 'human'].char_length.median()))
g = [cm[cm.owner_actor == a].char_length.values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
show('comment length Kruskal-Wallis H', round(H.statistic, 1), '{:,.1f}')
show('comment length KW df', len(g) - 1)
show('comment length KW p', H.pvalue, '{:.1e}')
for (i, j), lab in [((0, 1), 'cross vs same'), ((0, 2), 'cross vs human'), ((1, 2), 'same vs human')]:
    show(f'comment pairwise p, {lab}', mannwhitneyu(g[i], g[j], alternative='two-sided').pvalue, '{:.1e}')

smd = EV[EV.has_summary]
L = lambda a: smd[smd.actor == a].summary_chars.values.astype(float)
show('cross-system summary median (chars)', int(np.median(L('cross-system'))))
show('same-system summary median (chars)', int(np.median(L('same-system'))))
show('human summary median (chars)', int(np.median(L('human'))))
_, r = r_rb(L('cross-system'), L('same-system'))
show('summary p cross vs same', mannwhitneyu(L('cross-system'), L('same-system'), alternative='two-sided').pvalue, '{:.1e}')
show('summary |r| cross vs same', round(abs(r), 2))
show('summary |r| cross vs human', round(abs(r_rb(L('cross-system'), L('human'))[1]), 2))
show('summary |r| same vs human', round(abs(r_rb(L('same-system'), L('human'))[1]), 2))

# ---- review arrival time (event level) ------------------------------------
print('\n== Review arrival time')
E_inl, E_sum = EV[EV.has_inline], EV[EV.has_summary]
SHORT = {'cross-system': 'cross', 'same-system': 'same', 'human': 'human'}
for a in ['cross-system', 'same-system', 'human']:
    show(f'inline arrival median, {SHORT[a]} (h)', round(E_inl[E_inl.actor == a].wait.median(), 1))
    show(f'inline inside first hour, {SHORT[a]} (%)', round((E_inl[E_inl.actor == a].wait < 1).mean() * 100, 1))
g = [E_inl[E_inl.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
show('inline arrival Kruskal-Wallis H', round(H.statistic, 1), '{:,.1f}')
show('inline arrival KW p', H.pvalue, '{:.1e}')
show('inline arrival |r| cross vs same', round(abs(r_rb(g[0], g[1])[1]), 2))
show('inline arrival |r| cross vs human', round(abs(r_rb(g[0], g[2])[1]), 2))
for a, lab in [('human', 'human'), ('same-system', 'same'), ('cross-system', 'cross')]:
    show(f'inline tail >24h, {lab} (%)', round((E_inl[E_inl.actor == a].wait > 24).mean() * 100, 1))
for a in ['cross-system', 'same-system', 'human']:
    show(f'summary arrival median, {SHORT[a]} (h)', round(E_sum[E_sum.actor == a].wait.median(), 1))
    show(f'summary inside first hour, {SHORT[a]} (%)', round((E_sum[E_sum.actor == a].wait < 1).mean() * 100, 1))
g = [E_sum[E_sum.actor == a].wait.dropna().values.astype(float) for a in ['cross-system', 'same-system', 'human']]
H = kruskal(*g)
show('summary arrival Kruskal-Wallis H', round(H.statistic, 1), '{:,.1f}')
show('summary arrival KW p', H.pvalue, '{:.1e}')
show('summary arrival |r| cross vs same', round(abs(r_rb(g[0], g[1])[1]), 2))
show('summary arrival |r| cross vs human', round(abs(r_rb(g[0], g[2])[1]), 2))
# per inline comment, on Copilot-authored PRs
cop = cm[(cm.pr_id.map(meta.set_index('id').agent) == 'Copilot') & (cm.owner_actor != 'human')].copy()
cop['wait'] = wait(cop.pr_id.map(meta.set_index('id').created_at).values, cop.created_at)
show('comment arrival on Copilot PRs, cross (h)', round(cop[cop.owner_actor == 'cross-system'].wait.median(), 1))
show('comment arrival on Copilot PRs, same (h)', round(cop[cop.owner_actor == 'same-system'].wait.median(), 1))

# ---- review functions -----------------------------------------------------
print('\n== Review functions')
DC = DATA / 'rq2' / 'doublecoding'
si = pd.read_csv(DC / 'same_inline_coded.csv', comment='#')
ci = pd.read_csv(DC / 'cross_inline_coded.csv', comment='#')
ss = pd.read_csv(DC / 'same_summary_coded.csv', comment='#')
cs = pd.read_csv(DC / 'cross_summary_coded.csv', comment='#')
show('same-system inline sample', len(si))
show('cross-system inline sample', len(ci))
show('same-system summary sample', len(ss))
show('cross-system summary sample', len(cs))
show('coded units in total', len(si) + len(ci) + len(ss) + len(cs), '{:,}')
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
leaves = pd.concat([si.final, ci.final, ss.final, cs.final]).map(FUNC)
cats = leaves.value_counts()
for c in ['Descriptive', 'Code-directed', 'Confirmatory', 'Interactive/directive', 'Other']:
    show(f'{c} units', int(cats[c]), '{:,}')
sh = leaves.value_counts(normalize=True) * 100
for c in ['Descriptive', 'Code-directed', 'Confirmatory', 'Interactive/directive', 'Other']:
    show(f'{c} share (%)', round(sh[c], 1))
show('descriptive+confirmatory share (%)', round(sh['Descriptive'] + sh['Confirmatory'], 1))
ALIAS = {'verification report': 'workflow/verification report', 'clarification': 'clarification/question'}
canon = pd.concat([si.final, ci.final, ss.final, cs.final]).str.lower().replace(ALIAS)
E_RESIDUE = {'other', 'platform notice', 'review unavailable'}
show('five function categories', len(cats))
show('ten leaf sub-categories (A.1-D.2)', canon[~canon.isin(E_RESIDUE)].nunique())
leafsh = pd.concat([si.final, ci.final, ss.final, cs.final]).str.lower().value_counts(normalize=True) * 100
for leaf in ['findings digest', 'change overview', 'explanation', 'improvement suggestion',
             'code-issue feedback', 'change acknowledgment', 'approval verdict', 'response to feedback']:
    show(f'leaf {leaf} share (%)', round(leafsh.get(leaf, 0), 1))
show('leaf verification report share (%)', round(leafsh.get('workflow/verification report', 0) + leafsh.get('verification report', 0), 1))
show('leaf clarification/question share (%)', round(leafsh.get('clarification/question', 0) + leafsh.get('clarification', 0), 1))
for label, codes in [('same-inline', si.final), ('cross-inline', ci.final),
                     ('same-summary', ss.final), ('cross-summary', cs.final)]:
    shares = codes.map(FUNC).value_counts(normalize=True) * 100
    print(f'{label:14s} shares: ' + '  '.join(f'{k} {v:.1f}' for k, v in shares.items()))

# ---- review type comparison -----------------------------------------------
print('\n== Review type comparison')
summ_tab = pd.DataFrame({'same-system': ss.final.map(FUNC).value_counts(),
                         'cross-system': cs.final.map(FUNC).value_counts()}).fillna(0)
sm_sh = (summ_tab / summ_tab.sum() * 100).round(1)
show('summary descriptive, same (%)', sm_sh.loc['Descriptive', 'same-system'])
show('summary descriptive, cross (%)', sm_sh.loc['Descriptive', 'cross-system'])
show('summary confirmatory, cross (%)', sm_sh.loc['Confirmatory', 'cross-system'])
show('summary confirmatory, same (%)', sm_sh.loc['Confirmatory', 'same-system'])
chi2, p, dof, _ = chi2_contingency(summ_tab.T)
show('summary function x type chi2', round(chi2, 1))
show('summary function x type V', round(cramers_v(chi2, summ_tab.values.sum(), summ_tab.T), 2))
show('summary function x type p', p, '{:.1e}')
inl_tab = pd.DataFrame({'same-system': si.final.map(FUNC).value_counts(),
                        'cross-system': ci.final.map(FUNC).value_counts()}).fillna(0)
in_sh = (inl_tab / inl_tab.sum() * 100).round(1)
show('inline confirmatory, same (%)', in_sh.loc['Confirmatory', 'same-system'])
show('inline interactive, same (%)', in_sh.loc['Interactive/directive', 'same-system'])
show('inline code-directed, same (%)', in_sh.loc['Code-directed', 'same-system'])
show('inline code-directed, cross (%)', in_sh.loc['Code-directed', 'cross-system'])
show('inline confirmatory, cross (%)', in_sh.loc['Confirmatory', 'cross-system'])
chi2, p, dof, _ = chi2_contingency(inl_tab.T)
show('inline function x type chi2', round(chi2, 1))
show('inline function x type V', round(cramers_v(chi2, inl_tab.values.sum(), inl_tab.T), 2))
show('inline function x type p', p, '{:.1e}')

# ---- robustness -----------------------------------------------------------
print('\n== Robustness (composition)')
show('same-system confirmatory share (%)', round((si.final.map(FUNC) == 'Confirmatory').mean() * 100, 1))
ci2 = ci.merge(cm[['id', 'pr_id']], on='id')
ci2['agent'] = ci2.pr_id.map(sub.agent)
ag = ci2.assign(cd=ci.final.map(FUNC) == 'Code-directed').groupby('agent').cd.agg(['mean', 'size']) * [100, 1]
show('cross code-directed, Codex units', int(ag.loc['OpenAI_Codex', 'size']))
show('cross code-directed, Codex (%)', round(ag.loc['OpenAI_Codex', 'mean'], 1))
show('cross code-directed, Claude units', int(ag.loc['Claude_Code', 'size']))
show('cross code-directed, Claude (%)', round(ag.loc['Claude_Code', 'mean'], 1))
pooled_cd = (ci.final.map(FUNC) == 'Code-directed').mean() * 100
show('cross code-directed, pooled (%)', round(pooled_cd, 1))
show('cross code-directed, max deviation from pooled', round(abs(ag['mean'] - pooled_cd).max(), 1))
cop_cross = ci.merge(cm[['id', 'user']], on='id').query("user == 'Copilot'")
show('Copilot cross comments (n)', len(cop_cross))
show('Copilot cross comments code-directed (%)', round((cop_cross.final.map(FUNC) == 'Code-directed').mean() * 100, 1))
full = pd.read_csv(DATA / 'rq2' / 'full_corpus_inline_rule_coded.csv', comment='#', low_memory=False)
CD = {'improvement suggestion', 'code-issue feedback', 'workflow/verification report'}
cop = full[full.authoring_agent == 'Copilot']
same_n, cross_n = cop[cop.reviewer_type == 'same-system'], cop[cop.reviewer_type == 'cross-system']
same_cd = int(same_n.code.isin(CD).sum()); cross_cd = int(cross_n.code.isin(CD).sum())
show('rule-coded Copilot-authored same code-directed (%)', round(same_cd / len(same_n) * 100, 1))
show('rule-coded Copilot-authored cross code-directed (%)', round(cross_cd / len(cross_n) * 100, 1))
show('rule-coded Fisher p', fisher_exact([[same_cd, len(same_n) - same_cd], [cross_cd, len(cross_n) - cross_cd]])[1], '{:.1e}')
