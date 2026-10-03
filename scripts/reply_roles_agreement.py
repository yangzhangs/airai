#!/usr/bin/env python3
"""Split the double-coded RQ3 human-reply roles into the pilot (the 50 replies
that fixed the role codebook, as first drawn at seed 20260930) and the
remaining replies, and report Cohen's kappa for each round (mirrors 57_ for
RQ2). The sample now holds 316 replies (the Cochran size for the 1,787-reply
frame; nine drawn in a completion wave from the raw table and folded into the released files),
so the remaining round covers 266 replies while the pilot set stays fixed.

Inputs: data/doublecoding/roles_full_pass1.csv and roles_full_pass2.csv
        (the two independent passes) and data/rq3_roles_pilot.csv (the pilot
        membership as first drawn).
Writes data/rq3_roles_pilot.csv, data/rq3_roles_rest.csv, data/rq3_kappa_rounds.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'
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


a = pd.read_csv(f'{DATA}/doublecoding/roles_full_pass1.csv').rename(columns={'label': 'label_a'})
b = pd.read_csv(f'{DATA}/doublecoding/roles_full_pass2.csv').rename(columns={'label': 'label_b'})
D = a.merge(b, on='unit_id')
D['label_a'] = D['label_a'].str.strip().str.lower()
D['label_b'] = D['label_b'].str.strip().str.lower()
assert len(D) == 316

pilot_ids = set(pd.read_csv(f'{DATA}/rq3_roles_pilot.csv').unit_id.astype('int64'))
pilot = D[D.unit_id.astype('int64').isin(pilot_ids)]
rest = D[~D.unit_id.astype('int64').isin(pilot_ids)]
assert len(pilot) == 50 and len(rest) == 266

kp, pop_, np_ = kappa(list(pilot.label_a), list(pilot.label_b))
kr, por_, nr_ = kappa(list(rest.label_a), list(rest.label_b))
kall, poall, nall = kappa(list(D.label_a), list(D.label_b))

report = {'seed': SEED, 'pilot_n': 50,
          'pilot': {'n': np_, 'kappa': round(kp, 4), 'observed': round(pop_, 4)},
          'rest': {'n': nr_, 'kappa': round(kr, 4), 'observed': round(por_, 4)},
          'all_double_coded': {'n': nall, 'kappa': round(kall, 4), 'observed': round(poall, 4)}}
print(f"pilot n={np_} kappa={kp:.3f} po={pop_:.3f} | rest n={nr_} kappa={kr:.3f} po={por_:.3f} | all n={nall} kappa={kall:.3f}")

pilot.to_csv(f'{DATA}/rq3_roles_pilot.csv', index=False)
rest.to_csv(f'{DATA}/rq3_roles_rest.csv', index=False)
json.dump(report, open(f'{DATA}/rq3_kappa_rounds.json', 'w'), indent=1)
print("wrote rq3_roles_pilot.csv, rq3_roles_rest.csv, rq3_kappa_rounds.json")
