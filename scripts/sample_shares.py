#!/usr/bin/env python3
"""Compute data/rq2_sample_shares.json -- the per-stratum function shares that
RQ2 and Figure 7 report -- directly from the hand-coding artifacts:

  - inline, same-system stratum        : data/labeling_full_coded.csv
  - inline, cross-system stratum       : data/cross_inline_sample_coded.csv (357 units)
  - summaries, same-system stratum     : data/rq2_summary_sample_coded.csv
  - summaries, cross-system            : data/cross_summary_sample_coded.csv (348 units)

The two cross-system strata are drawn uniformly at random from the comments
and summaries of the AI reviewing systems identified in Section 2.2 (the
RQ1-screened pools), at the sizes Cochran's rule gives for their populations:
357 inline comments of the 5,130 and 348 summaries of the 3,732
(cross_inline_sample_coded.csv, seed 20261005; cross_summary_sample_coded.csv,
seed 20261006). There is no post-hoc screening: the draws are made from the
AI-system pools directly. Human and same-system strata follow the same rule.

Category mapping (the 5 functions of the paper's taxonomy):
  A Descriptive            = explanation                      (inline)
                           = findings digest + change overview + explanation (summaries)
  B Code-directed          = improvement suggestion + code-issue feedback
                           + workflow/verification report                      (both forms)
  C Confirmatory           = change acknowledgment                            (inline)
                           = approval verdict                                  (summaries)
  D Interactive/directive  = response to feedback + clarification/question
                           + agent instruction                                 (inline)
  E Other                  = platform notice + other                          (inline)
                           = other + review unavailable + platform notice      (summaries)

Writes the shares rounded to one decimal, exactly as the manuscript quotes them.
Run from the package root:  python3 scripts/sample_shares.py
"""
import json
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'

INLINE_MAP = {
    'explanation': 'Descriptive',
    'improvement suggestion': 'Code-directed', 'code-issue feedback': 'Code-directed',
    'workflow/verification report': 'Code-directed',
    'change acknowledgment': 'Confirmatory',
    'response to feedback': 'Interactive/directive',
    'clarification/question': 'Interactive/directive',
    'agent instruction': 'Interactive/directive',
    'platform notice': 'Other', 'other': 'Other',
}
SUMMARY_MAP = {
    'findings digest': 'Descriptive', 'change overview': 'Descriptive', 'explanation': 'Descriptive',
    'improvement suggestion': 'Code-directed', 'verification report': 'Code-directed',
    'approval verdict': 'Confirmatory',
    'agent instruction': 'Interactive/directive', 'response to feedback': 'Interactive/directive',
    'clarification': 'Interactive/directive',
    'other': 'Other', 'review unavailable': 'Other', 'platform notice': 'Other',
}
KEYS = ['Descriptive', 'Code-directed', 'Confirmatory', 'Interactive/directive', 'Other']


def shares(codes, mapping):
    cats = codes.str.strip().str.lower().map(mapping)
    n = len(cats)
    return {k: round(float((cats == k).sum()) / n * 100, 1) for k in KEYS}


def order(d):
    return {k: d[k] for k in KEYS}


out = {'inline': {}, 'summary': {}}

inl = pd.read_csv(DATA / 'labeling_full_coded.csv')
out['inline']['same-system'] = order(shares(inl[inl.rtype == 'Self-review'].code, INLINE_MAP))

cross = pd.read_csv(DATA / 'cross_inline_sample_coded.csv')['code']  # 357 units (Section 2.3)
assert len(cross) == 357, 'the cross-system inline sample holds 357 analyzed units'
out['inline']['cross-system'] = order(shares(cross, INLINE_MAP))

acc = pd.read_csv(DATA / 'ai_reviewer_accounts.csv')
ai = set(acc.loc[acc.role == 'AI reviewer', 'user'])
smr = pd.read_csv(DATA / 'rq2_summary_sample_coded.csv')
smr = smr[smr.user.isin(ai)]        # the AI reviewing systems (Section 2.2)
cross_s = pd.read_csv(DATA / 'cross_summary_sample_coded.csv')['code']  # 348 units (Section 2.3)
assert len(cross_s) == 348, 'the cross-system summary sample holds 348 analyzed units'
out['summary']['cross-system'] = order(shares(cross_s, SUMMARY_MAP))
out['summary']['same-system'] = order(shares(smr[smr.actor_kind == 'same-system'].summary_code, SUMMARY_MAP))

with open(DATA / 'rq2_sample_shares.json', 'w') as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
