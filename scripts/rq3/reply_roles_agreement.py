#!/usr/bin/env python3
"""Role-coding agreement (Cohen's kappa) for the RQ3 reply sample.

Run from the package root:  python3 scripts/rq3/reply_roles_agreement.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / 'data'


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


d = pd.read_csv(DATA / 'rq3' / 'doublecoding' / 'roles_full_coded.csv', comment='#')
k, n = kappa(list(d.pass1.str.strip().str.lower()), list(d.pass2.str.strip().str.lower()))
print(f'role coding  n={n}  kappa={k:.4f}')
json.dump({'note': 'the sampled replies are double-coded blind; the adjudicated '
                   'final is the coding of record', 'n': n, 'kappa': round(k, 4)},
          open(DATA / 'rq3' / 'rq3_kappa.json', 'w'), indent=1)
print('wrote data/rq3/rq3_kappa.json')
