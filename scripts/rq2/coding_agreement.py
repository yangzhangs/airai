#!/usr/bin/env python3
"""Recompute the RQ2 agreement figures from the full-sample double-coding files
and check them against the values the paper reports.

Every coded unit of the four strata is double-coded blind (the pilot, rest and
completion waves recorded in data/rq2/doublecoding/*_sample_doublecoding.csv) and a
third annotator arbitrated the disagreements (adjudication_log.csv). The method
section quotes Cohen's kappa per stratum over the full samples; the pilot and
remaining wave figures are released in the json for transparency. This script
recomputes the overall and the wave figures, checks them, and rewrites
data/rq2/rq2_kappa_redrawn_samples.json.

Run from the package root:  python3 scripts/rq2/coding_agreement.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / 'data'
DC = DATA / 'rq2' / 'doublecoding'

PAPER_WAVES = {   # per-stratum wave kappa, released in the json
    'same-inline':    {'pilot': 0.87, 'remaining': 0.81},
    'cross-inline':   {'pilot': 1.00, 'remaining': 0.93},
    'same-summary':   {'pilot': 0.79, 'remaining': 0.96},
    'cross-summary':  {'pilot': 1.00, 'remaining': 0.85},
}
PAPER_STRATA = {   # per-stratum kappa and n over the full samples, quoted in the method section
    'same-inline':    (0.82, 364),
    'cross-inline':   (0.94, 357),
    'same-summary':   (0.93, 275),
    'cross-summary':  (0.88, 348),
}


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    idx = {c: i for i, c in enumerate(cats)}
    n = len(a)
    M = np.zeros((len(cats), len(cats)))
    for x, y in zip(a, b):
        M[idx[x], idx[y]] += 1
    po = np.trace(M) / n
    pe = (M.sum(axis=1) @ M.sum(axis=0)) / (n * n)
    return float((po - pe) / (1 - pe)), float(po), int(n)


def coded(df):
    return (list(df.pass1.str.strip().str.lower()),
            list(df.pass2.str.strip().str.lower()))


out = {'round': 'full samples: every coded unit double-coded blind '
                '(pilot, rest and completion waves), disagreements adjudicated '
                '(adjudication_log.csv)',
       'strata': {}}
ok = True
for stratum, fn in [('same-inline', 'same_inline_sample_doublecoding.csv'),
                    ('cross-inline', 'cross_inline_sample_doublecoding.csv'),
                    ('same-summary', 'same_summary_sample_doublecoding.csv'),
                    ('cross-summary', 'cross_summary_sample_doublecoding.csv')]:
    d = pd.read_csv(DC / fn, comment='#')
    assert d.pass2.notna().all(), f'{fn}: every unit must be double-coded'
    k, po, n = kappa(*coded(d))
    pk, pn = PAPER_STRATA[stratum]
    match = (n == pn) and abs(k - pk) < 0.005
    ok &= match
    print(f"{stratum:14s} n={n:3d} (expected {pn})  observed={po:.4f}  "
          f"kappa={k:.4f} (expected {pk:.2f})  {'OK' if match else 'MISMATCH'}")
    waves = {}
    for wname, mask in [('pilot', d['round'] == 'pilot'),
                        ('remaining', d['round'].isin(['rest', 'completion']))]:
        g = d[mask]
        wk, wpo, wn = kappa(*coded(g))
        waves[wname] = {'n': wn, 'observed': round(wpo, 4), 'kappa': round(wk, 4)}
        want = PAPER_WAVES[stratum][wname]
        wmatch = abs(wk - want) < 0.005
        ok &= wmatch
        print(f"{'':14s} {wname:10s} n={wn:3d}  observed={wpo:.4f}  "
              f"kappa={wk:.4f} (released {want:.2f})  {'OK' if wmatch else 'MISMATCH'}")
    out['strata'][stratum] = {'n': n, 'observed': round(po, 4), 'kappa': round(k, 4),
                              'pass2_rounds': {r: int(v) for r, v in
                                               d['round'].value_counts().items()},
                              'waves': waves}

adj = pd.read_csv(DC / 'adjudication_log.csv', comment='#')
print(f"\nadjudicated disagreements on record: {len(adj)}")
for stratum in PAPER_STRATA:
    n = int((adj.stratum == stratum).sum()) if 'stratum' in adj.columns else 0
    if n:
        print(f"  {stratum}: {n} units adjudicated, finals applied to the coded samples")

json.dump(out, open(DATA / 'rq2' / 'rq2_kappa_redrawn_samples.json', 'w'), indent=1)
print('\nwrote data/rq2/rq2_kappa_redrawn_samples.json')
assert ok, 'kappa values do not match the paper'
print('all agreement figures match the paper.')
