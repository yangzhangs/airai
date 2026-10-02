#!/usr/bin/env python3
"""Completion-wave draw for the RQ3 human-reply roles: nine more replies to
bring the coded sample to 316, the Cochran size for the 1,787-reply frame
(95% CI, 5% margin, p=0.5, finite population correction; see Sec. 2.3).

The original 307 were drawn when the reply corpus held ~1,52x replies; the
final identification yields 1,787 and the same rule gives 316, so this wave
draws the missing nine uniformly from the replies not yet sampled. Draws come
from the coded corpus's frame (replies with a fetched body), excluding the 307.

Writes data/doublecoding/roles_completion_draw.csv (id, pr, agent, parent
fields, body) and prints the nine ids for the coding sheets.
"""
import importlib.util
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'
SEED = 20261001
K = 9

# the raw review-comment table (bodies and reply links) is not redistributed;
# point AIDEV_V2_COMMENTS at a local copy of it to reproduce this wave
V2 = os.environ.get('AIDEV_V2_COMMENTS', '/root/AIDev/pr_review_comments_v2.parquet')

rc = pd.read_csv(DATA / 'review_comments_final.csv', low_memory=False)
prof = pd.read_csv(DATA / 'pr_review_profile.csv', low_memory=False)
v2 = pd.read_parquet(V2)

scope = set(prof[~prof.review_config.str.fullmatch('human')].pr_id.astype('int64'))
frame = rc[rc.pr_id.isin(scope) & rc.is_human_reply]
frame_ids = set(frame.id.astype('int64'))
coded_all = set(pd.read_csv(DATA / 'doublecoding' / 'roles_full_final.csv').unit_id.astype('int64'))
draw_file = DATA / 'doublecoding' / 'roles_completion_draw.csv'
if draw_file.exists():   # rerun: reconstruct the pre-wave state so the draw repeats
    wave = set(pd.read_csv(draw_file).unit_id.astype('int64'))
    coded = coded_all - wave
    assert len(coded) == 307 and wave <= coded_all
else:
    coded = coded_all
v2_ids = set(v2.id.astype('int64'))
codeable = frame_ids & v2_ids
remaining = sorted(codeable - coded)
print(f'frame={len(frame_ids)}  codeable={len(codeable)}  coded={len(coded)}  remaining={len(remaining)}')

rng = np.random.default_rng(SEED)
draw = sorted(rng.choice(np.array(remaining), size=K, replace=False).tolist())
assert not (set(draw) & coded), 'draw overlaps the coded sample'

agg = pd.read_csv(f'{DATA}/pr_review_profile.csv', low_memory=False).set_index('pr_id')['authoring_agent']
v2i = v2.set_index('id')
rows = []
for uid in draw:
    r = v2i.loc[uid]
    pid = int(r.in_reply_to_id) if pd.notna(r.in_reply_to_id) else None
    pu = pt = None
    if pid is not None and pid in v2i.index:
        p = v2i.loc[pid]
        pu, pt = p.user, p.user_type
    rows.append({
        'unit_id': uid,
        'pr_id': int(r.pull_request_url.rstrip('/').split('/')[-2]) if False else None,
        'authoring_agent': agg.get(int(r.pull_request_url.rstrip('/').split('/')[-1]) if False else -1),
        'parent_id': pid,
        'parent_user': pu,
        'parent_user_type': pt,
        'reply_body': r.body,
    })

# pr_id: from the released table (has pr_id column)
pr_of = rc.set_index('id')['pr_id']
for row in rows:
    row['pr_id'] = int(pr_of.loc[row['unit_id']])
    row['authoring_agent'] = agg.get(row['pr_id'])

out = pd.DataFrame(rows)
out.to_csv(f'{DATA}/doublecoding/roles_completion_draw.csv', index=False)
print(out[['unit_id', 'pr_id', 'authoring_agent', 'parent_user', 'parent_user_type']].to_string())
print()
for _, r in out.iterrows():
    print(f"--- {r.unit_id}  [{r.authoring_agent}]  parent={r.parent_user} ({r.parent_user_type})")
    print('   ', str(r.reply_body)[:300].replace('\n', ' '))
