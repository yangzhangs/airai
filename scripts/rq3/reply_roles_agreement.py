#!/usr/bin/env python3
"""Role-coding agreement (Cohen's kappa) for the RQ3 reply sample; writes
data/rq3/roles_pilot.csv, roles_rest.csv and rq3_kappa_rounds.json.

Run from the package root:  python3 scripts/rq3/reply_roles_agreement.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / 'data'
SEED = 20260930


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


a = pd.read_csv(f'{DATA}/rq3/doublecoding/roles_full_pass1.csv', comment='#').rename(columns={'label': 'label_a'})
b = pd.read_csv(f'{DATA}/rq3/doublecoding/roles_full_pass2.csv', comment='#').rename(columns={'label': 'label_b'})
D = a.merge(b, on='unit_id')
D['label_a'] = D['label_a'].str.strip().str.lower()
D['label_b'] = D['label_b'].str.strip().str.lower()

pilot_ids = set(pd.read_csv(f'{DATA}/rq3/roles_pilot.csv', comment='#').unit_id.astype('int64'))
pilot = D[D.unit_id.astype('int64').isin(pilot_ids)]
rest = D[~D.unit_id.astype('int64').isin(pilot_ids)]

kp, _, np_ = kappa(list(pilot.label_a), list(pilot.label_b))
kr, _, nr_ = kappa(list(rest.label_a), list(rest.label_b))
kall, _, nall = kappa(list(D.label_a), list(D.label_b))

report = {'seed': SEED, 'pilot_n': 50,
          'pilot': {'n': np_, 'kappa': round(kp, 4)},
          'rest': {'n': nr_, 'kappa': round(kr, 4)},
          'all_double_coded': {'n': nall, 'kappa': round(kall, 4)}}
print(f"pilot n={np_} kappa={kp:.3f} | rest n={nr_} kappa={kr:.3f} | all n={nall} kappa={kall:.3f}")

MARK_PILOT = "# RQ3 | role coding, pilot round (50 replies, first draw seed 20260930; both annotators\u2019 labels)\n"
MARK_REST = "# RQ3 | role coding, remaining replies (266 of the 316-reply sample; both annotators\u2019 labels)\n"


def write_marked(df, path, mark):
    with open(path, 'w') as f:
        f.write(mark)
        df.to_csv(f, index=False)


write_marked(pilot, f'{DATA}/rq3/roles_pilot.csv', MARK_PILOT)
write_marked(rest, f'{DATA}/rq3/roles_rest.csv', MARK_REST)
json.dump(report, open(f'{DATA}/rq3/rq3_kappa_rounds.json', 'w'), indent=1)
print('wrote roles_pilot.csv, roles_rest.csv, rq3_kappa_rounds.json')
