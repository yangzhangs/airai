#!/usr/bin/env python3
"""Four-stratum coding agreement (Cohen's kappa) for the RQ2 coded samples.

Run from the package root:  python3 scripts/rq2/coding_agreement.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / 'data'
DC = DATA / 'rq2' / 'doublecoding'


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    idx = {c: i for i, c in enumerate(cats)}
    n = len(a)
    M = np.zeros((len(cats), len(cats)))
    for x, y in zip(a, b):
        M[idx[x], idx[y]] += 1
    po = np.trace(M) / n
    pe = (M.sum(axis=1) @ M.sum(axis=0)) / (n * n)
    return float((po - pe) / (1 - pe)), int(n)


out = {'note': 'every coded unit is double-coded blind; the adjudicated final is '
               'the coding of record', 'strata': {}}
for stratum, fn in [('same-inline', 'same_inline_coded.csv'),
                    ('cross-inline', 'cross_inline_coded.csv'),
                    ('same-summary', 'same_summary_coded.csv'),
                    ('cross-summary', 'cross_summary_coded.csv')]:
    d = pd.read_csv(DC / fn, comment='#')
    assert d.pass2.notna().all(), f'{fn}: every unit must be double-coded'
    k, n = kappa(list(d.pass1.str.strip().str.lower()), list(d.pass2.str.strip().str.lower()))
    print(f'{stratum:14s} n={n:3d}  kappa={k:.4f}')
    out['strata'][stratum] = {'n': n, 'kappa': round(k, 4)}

json.dump(out, open(DATA / 'rq2' / 'rq2_kappa.json', 'w'), indent=1)
print('\nwrote data/rq2/rq2_kappa.json')
