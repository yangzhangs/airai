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


def coded(df):
    return (list(df.pass1.str.strip().str.lower()),
            list(df.pass2.str.strip().str.lower()))


out = {'round': 'full samples: every coded unit double-coded blind '
                '(pilot, rest and completion waves), disagreements adjudicated '
                '(adjudication_log.csv)',
       'strata': {}}
for stratum, fn in [('same-inline', 'same_inline_sample_doublecoding.csv'),
                    ('cross-inline', 'cross_inline_sample_doublecoding.csv'),
                    ('same-summary', 'same_summary_sample_doublecoding.csv'),
                    ('cross-summary', 'cross_summary_sample_doublecoding.csv')]:
    d = pd.read_csv(DC / fn, comment='#')
    assert d.pass2.notna().all(), f'{fn}: every unit must be double-coded'
    k, n = kappa(*coded(d))
    print(f'{stratum:14s} n={n:3d}  kappa={k:.4f}')
    waves = {}
    for wname, mask in [('pilot', d['round'] == 'pilot'),
                        ('remaining', d['round'].isin(['rest', 'completion']))]:
        g = d[mask]
        wk, wn = kappa(*coded(g))
        waves[wname] = {'n': wn, 'kappa': round(wk, 4)}
        print(f"{'':14s} {wname:10s} n={wn:3d}  kappa={wk:.4f}")
    out['strata'][stratum] = {'n': n, 'kappa': round(k, 4),
                              'pass2_rounds': {r: int(v) for r, v in
                                               d['round'].value_counts().items()},
                              'waves': waves}

adj = pd.read_csv(DC / 'adjudication_log.csv', comment='#')
print(f"\nadjudication log: {len(adj)} units")
for stratum in out['strata']:
    n = int((adj.stratum == stratum).sum())
    if n:
        print(f'  {stratum}: {n} units adjudicated')

json.dump(out, open(DATA / 'rq2' / 'rq2_kappa_redrawn_samples.json', 'w'), indent=1)
print('\nwrote data/rq2/rq2_kappa_redrawn_samples.json')
