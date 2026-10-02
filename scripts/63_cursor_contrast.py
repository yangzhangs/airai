#!/usr/bin/env python3
"""The Cursor same-system contrast behind the External Validity sentence
(Section 4.3): the one non-Copilot same-system workflow in the corpus is Cursor
reviewing Cursor-authored PRs (424 events, 26 inline comments). The 26 comments
are coded under the same codebook as the review-function samples; the labels
live in data/cursor_same_system_coded.csv (unit_id, code, rule_code), with the
rule-based labels of the corpus coding kept alongside for transparency.

The script checks the sample size and reports the register: the manuscript
claims all 26 comments are code-directed bug reports and none are confirmatory.
Run from the package root:  python3 scripts/63_cursor_contrast.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'

COD = {'Improvement suggestion', 'Code-issue feedback', 'Workflow/verification report'}
CONF = {'Change acknowledgment', 'Approval verdict'}

com = pd.read_csv(DATA / 'review_comments_final.csv')
cursor = com[(com.owner_actor == 'same-system') & com.user.str.contains('cursor', case=False, na=False)]
coded = pd.read_csv(DATA / 'cursor_same_system_coded.csv')

assert len(cursor) == 26, 'the Cursor same-system stratum holds 26 inline comments'
assert set(coded.unit_id) == set(cursor.id), 'the coded file must cover exactly those comments'

n = len(coded)
n_cd = int(coded.code.isin(COD).sum())
n_conf = int(coded.code.isin(CONF).sum())
print(f'Cursor same-system inline comments: n={n}')
print(f"  code-directed: {n_cd}/{n} = {n_cd/n*100:.0f}%  (manuscript: all 26)")
print(f"  confirmatory:  {n_conf}/{n} = {n_conf/n*100:.0f}%  (manuscript: none)")
print('  code mix:', coded.code.value_counts().to_dict())
print('  rule-based labels for comparison:', coded.rule_code.value_counts().to_dict())
assert n_cd == n and n_conf == 0, 'mismatch against the manuscript sentence'
print('External Validity sentence reproduced.')
