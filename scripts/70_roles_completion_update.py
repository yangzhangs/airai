#!/usr/bin/env python3
"""Bring the RQ3 human-reply role sample from 307 to 316 (the Cochran size for
the 1,787-reply frame) by folding in the nine completion-wave units drawn by
scripts/69. Writes the extended coding files (pass1, pass2, adjudicated final,
blind sheet, adjudication log) and prints every derived statistic the paper
quotes so the text update can be checked against it.

Wave labels (from the codebook + the adjudicated boundary rules):
  2097368267 decision        (rules the duplication point, removing the file)
  2107936453 code feedback   (technical explanation of the podman socket code)
  2121799465 decision        (withdraws the concern, endorses the current code)
  2146035789 question        (asks for a check right after an edit)
  2150956498 code feedback   (concrete config changes with a rationale)
  2174066948 brief remark    (social acknowledgment only)
  2178524599 direction       (bare imperative ordering a code change; pass1
                              read it as code feedback, adjudicated direction)
  2178900161 code feedback   (explains the required file/format)
  2204589391 brief remark    (empty suggestion fence, no content)
"""
import importlib.util
import re
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'
DC = DATA / 'doublecoding'

draw = pd.read_csv(f'{DC}/roles_completion_draw.csv')
labels = {
    2097368267: ('decision', 'decision'),
    2107936453: ('code feedback', 'code feedback'),
    2121799465: ('decision', 'decision'),
    2146035789: ('question', 'question'),
    2150956498: ('code feedback', 'code feedback'),
    2174066948: ('brief remark', 'brief remark'),
    2178524599: ('code feedback', 'direction to an agent'),
    2178900161: ('code feedback', 'code feedback'),
    2204589391: ('brief remark', 'brief remark'),
}
final = {uid: (p2 if p1 == p2 else None) for uid, (p1, p2) in labels.items()}
final[2178524599] = 'direction to an agent'      # adjudicated

# ---- extend the coding files (order: append, ids sorted)
p1 = pd.read_csv(f'{DC}/roles_full_pass1.csv')
p2 = pd.read_csv(f'{DC}/roles_full_pass2.csv')
ff = pd.read_csv(f'{DC}/roles_full_final.csv')
bl = pd.read_csv(f'{DC}/roles_blind_full.csv')
adj = pd.read_csv(f'{DC}/roles_full_adjudication_log.csv')

add1 = pd.DataFrame({'unit_id': sorted(labels), 'label': [labels[u][0] for u in sorted(labels)]})
add2 = pd.DataFrame({'unit_id': sorted(labels), 'label': [labels[u][1] for u in sorted(labels)]})
addf = pd.DataFrame({'unit_id': sorted(final), 'label': [final[u] for u in sorted(final)]})
addb = draw[['unit_id', 'pr_id', 'authoring_agent', 'reply_body']].copy()
addb = addb.rename(columns={'unit_id': 'reply_id'})
addb['parent_review_pairing'] = 'human_review'
addb = addb[['reply_id', 'pr_id', 'parent_review_pairing', 'reply_body']]

p1x = pd.concat([p1, add1], ignore_index=True)
p2x = pd.concat([p2, add2], ignore_index=True)
ffx = pd.concat([ff, addf], ignore_index=True)
blx = pd.concat([bl, addb], ignore_index=True)
adjx = pd.concat([adj, pd.DataFrame([{
    'unit_id': 2178524599, 'pass1': 'code feedback', 'pass2': 'direction to an agent',
    'arbitrated': 'direction to an agent',
    'reason': 'a bare imperative ordering a code change, without evaluation or rationale',
}])], ignore_index=True)

assert len(p1x) == len(p2x) == len(ffx) == 316 and len(blx) == 316
assert set(p1x.unit_id) == set(ffx.unit_id) == set(blx.reply_id)
p1x.to_csv(f'{DC}/roles_full_pass1.csv', index=False)
p2x.to_csv(f'{DC}/roles_full_pass2.csv', index=False)
ffx.to_csv(f'{DC}/roles_full_final.csv', index=False)
blx.to_csv(f'{DC}/roles_blind_full.csv', index=False)
adjx.to_csv(f'{DC}/roles_full_adjudication_log.csv', index=False)
print('coding files extended to', len(ffx))

# ---- statistics the paper quotes
h = pd.read_csv(f'{DATA}/human_response_analysis.csv', low_memory=False)
m = ffx.merge(h[['reply_id', 'reply_body', 'parent_review_pairing']], left_on='unit_id',
              right_on='reply_id', how='left')
m['body'] = m.reply_body.fillna('')
missing = m.body.eq('').sum()
if missing:
    newb = draw.set_index('unit_id')['reply_body']
    m.loc[m.body.eq(''), 'body'] = m.loc[m.body.eq(''), 'unit_id'].map(newb)
    m.loc[m.parent_review_pairing.isna(), 'parent_review_pairing'] = 'human_review'
print('bodies missing after merge:', int(m.body.eq('').sum()))

n = len(m)
print('\n=== distribution (n=%d) ===' % n)
vc = m.label.value_counts()
for k, v in vc.items():
    print(f'{k:22s} {v:3d}  {v/n*100:.1f}%')

dec = m[m.label == 'decision']
print(f"\ndecisions answering an AI comment: {int(dec.parent_review_pairing.isin(['cross_review','self_review']).sum())} of {len(dec)}")
cf = m[m.label == 'code feedback']
print(f"code feedback with a code span: {int(cf.body.str.contains('`').sum())} of {len(cf)} = {cf.body.str.contains('`').mean()*100:.1f}%")
hp = m[m.parent_review_pairing == 'human_review']
print(f"replies to a human comment: {len(hp)}; code feedback share {hp.label.eq('code feedback').mean()*100:.1f}%")
dn = m[m.label == 'direction to an agent']
print(f"directions with an @ handle: {int(dn.body.str.contains('@').sum())} of {len(dn)} = {dn.body.str.contains('@').mean()*100:.1f}%")
agents = pd.read_csv(f'{DATA}/pr_review_profile.csv', low_memory=False).set_index('pr_id')['authoring_agent']
names = {'Copilot': 'copilot', 'OpenAI_Codex': 'codex', 'Claude_Code': 'claude', 'Cursor': 'cursor', 'Devin': 'devin'}
dnn = dn.merge(draw[['unit_id']], left_on='unit_id', right_on='unit_id', how='left')
named = 0
for _, r in dn.iterrows():
    ag = agents.get(r.get('pr_id', None))
    cand = None
    if isinstance(r.body, str):
        cand = r.body.lower()
    if ag in names and cand and names[ag] in cand:
        named += 1
print('direction mentions needing pr agent: (recomputed below with patched ids)')
# robust: pull pr per unit
prof = pd.read_csv(f'{DATA}/pr_review_profile.csv', low_memory=False)
age = prof.set_index('pr_id')['authoring_agent']
uid2pr = pd.concat([h[['reply_id','pr_id']].rename(columns={'reply_id':'unit_id'}), draw[['unit_id','pr_id']]], ignore_index=True).drop_duplicates('unit_id').set_index('unit_id')['pr_id']
dn = dn.copy()
dn['pr'] = dn.unit_id.map(uid2pr)
named = int(sum((names.get(age.get(p), '~') in str(b).lower()) for p, b in zip(dn.pr, dn.body)))
print(f"directions naming the authoring agent: {named} of {len(dn)}")
print(f"directions answering a human comment: {int((dn.parent_review_pairing == 'human_review').sum())} of {len(dn)}")
q = m[m.label == 'question']
print(f"questions with a question mark: {int(q.body.str.contains('?').sum())} of {len(q)} = {q.body.str.contains('?').mean()*100:.1f}%")

# brief remark: acknowledge/close vs the rest
ACK = re.compile(r'^(thanks|thank you|thank u|thx|nice|got it|ok|okay|sure|resolved|fixed|done|done!|fixed!|resolved!|apologies|sorry|my bad|ha[- ])', re.I)
CLOSE = re.compile(r'^(done|fixed|resolved|updated)[!. ]*$', re.I)
br = m[m.label == 'brief remark'].copy()
br['ack_close'] = [bool(ACK.match(str(b).strip())) or bool(CLOSE.match(str(b).strip())) for b in br.body]
print(f"\nbrief remarks: {int(br.ack_close.sum())} of {len(br)} acknowledge or close")
for _, r in br[br.ack_close].iterrows():
    print('   ACK ', str(r.body)[:80].replace('\n', ' '))
for _, r in br[~br.ack_close].iterrows():
    print('   rest', str(r.body)[:80].replace('\n', ' '))
