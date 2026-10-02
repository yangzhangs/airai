#!/usr/bin/env python3
"""Build the review-episode dataset that the redesigned RQs are anchored on.

Channel A (review submissions, AIDev `pr_reviews`) is the backbone; channel B
(inline review comments, `pr_review_comments`) tells us whether an episode
produced line-anchored feedback. Channel C (issue comments) is deliberately out
of scope.

UNIT = review episode = (PR x actor), where actor is the reviewer's system
identity for AI bots and the login for humans. Raw submissions are NOT the unit:
bots submit several reviews per pass (29,403 submissions collapse to 14,154
episodes for the curated subset), so counting submissions inflates activity.

Per episode we record which actors reviewed, what the episode produced
(bare verdict / written summary / line-anchored comments), and for how long.

Output: data/pr_episodes.csv (episode level) and data/pr_review_profile.csv
(PR level). No paper numbers are touched by this script. Raw inputs are the
AIDev curated-subset tables exported to /tmp/pr_reviews.parquet,
/tmp/pr_review_comments.parquet and /tmp/pr_pull.parquet (see the package README).
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / 'data'

# ---------------------------------------------------------------- reviewer identity
# bot login -> AI system identity. One vendor distributing several products maps
# to one identity (the Copilot coding agent and the Copilot reviewer are both
# "Copilot"); third-party review bots keep their own identity.
SYSTEM_OF = {
    'copilot-swe-agent[bot]': 'Copilot', 'copilot-pull-request-reviewer[bot]': 'Copilot',
    'copilot[bot]': 'Copilot', 'github-copilot[bot]': 'Copilot', 'Copilot': 'Copilot',
    'coderabbitai[bot]': 'CodeRabbit',
    'cursor[bot]': 'Cursor', 'cursoragent': 'Cursor',
    'claude[bot]': 'Claude Code', 'Claude': 'Claude Code',
    'devin-ai-integration[bot]': 'Devin',
    'gemini-code-assist[bot]': 'Gemini Code Assist',
    'greptile-apps[bot]': 'Greptile', 'greptile-apps-staging[bot]': 'Greptile',
    'github-advanced-security[bot]': 'GitHub Advanced Security',
    'graphite-app[bot]': 'Graphite', 'cubic-dev-ai[bot]': 'Cubic Dev AI',
    'ellipsis-dev[bot]': 'Ellipsis', 'sourcery-ai[bot]': 'Sourcery AI',
    'entelligence-ai-pr-reviews[bot]': 'Entelligence', 'entelligence-ai[bot]': 'Entelligence',
    'github-actions[bot]': 'GitHub Actions', 'seer-by-sentry[bot]': 'Seer',
    'aikido-pr-checks[bot]': 'Aikido', 'codescene-delta-analysis[bot]': 'CodeScene',
    'recurseml[bot]': 'RecurseML', 'kodus-ai[bot]': 'Kodus',
    'qodo-merge-for-open-source[bot]': 'Qodo', 'qodo-merge-pro[bot]': 'Qodo',
    'lunary-bot': 'Lunary', 'kilo-code-bot[bot]': 'Kilo Code',
    'codegen-sh[bot]': 'Codegen', 'tembo[bot]': 'Tembo', 'sweep-ai[bot]': 'Sweep',
    'macroscope-app[bot]': 'Macroscope', 'baz-reviewer[bot]': 'Baz',
    'whatsapp-codereview-bot[bot]': 'WhatsApp Code Review',
    'amazon-q-developer[bot]': 'Amazon Q', 'codex[bot]': 'Codex',
    'chatgpt-codex-connector[bot]': 'Codex',
    # rare review bots found by the mapping-coverage check (33 reviews in total)
    'pullrequest[bot]': 'PullRequest', 'windsurf-bot[bot]': 'Windsurf',
    'wispbit-ai[bot]': 'Wispbit', 'semgrep-code-getsentry[bot]': 'Semgrep',
    'semgrep-code-zeta-chain[bot]': 'Semgrep', 'propel-code-bot[bot]': 'Propel',
    'hound[bot]': 'Hound', 'callstackai[bot]': 'CallstackAI', 'vercel[bot]': 'Vercel',
    'agent-optibot[bot]': 'Optibot', 'codefactor-io[bot]': 'CodeFactor',
    'charliecreates[bot]': 'Charlie', 'codeant-ai[bot]': 'CodeAnt',
    'dust-agent[bot]': 'Dust', 'matter-code-review[bot]': 'Matter',
    'giselles-ai[bot]': 'Giselles', 'starrocks-cr[bot]': 'StarRocks',
    'korbit-ai[bot]': 'Korbit',
}
# Bot accounts that are automation rather than AI review: CI, linters, static
# analysis, deployment. They submit reviews but do not review the change with a
# model, so they are neither AI-on-AI review nor human review and are excluded
# from the corpus. Screened by hand over the 40 bot accounts that review the
# curated subset; these 8 logins (7 system identities) are what the screen
# removed, 130 review events and 174 inline comments.
NON_AI_AUTOMATION = {
    'github-actions[bot]',              # CI automation
    'aikido-pr-checks[bot]',            # security scanner
    'codescene-delta-analysis[bot]',    # code-health analytics
    'semgrep-code-getsentry[bot]',      # static analysis
    'semgrep-code-zeta-chain[bot]',     # static analysis
    'codefactor-io[bot]',               # linter
    'hound[bot]',                       # code search
    'vercel[bot]',                      # deployment
    'github-advanced-security[bot]',    # CodeQL and lintrunner code scanning, not AI review
}

# AIDev's authoring-agent label -> the AI system identity it corresponds to
AGENT_TO_SYSTEM = {'Copilot': 'Copilot', 'Claude_Code': 'Claude Code', 'Cursor': 'Cursor',
                   'Devin': 'Devin', 'OpenAI_Codex': 'Codex'}


def load():
    reviews = pd.read_parquet('/tmp/pr_reviews.parquet')
    rcomments = pd.read_parquet('/tmp/pr_review_comments.parquet',
                                columns=['id', 'pull_request_review_id', 'created_at'])
    pull = pd.read_parquet('/tmp/pr_pull.parquet',
                           columns=['id', 'html_url', 'number', 'agent', 'created_at', 'closed_at', 'merged_at'])
    summary = pd.read_csv(f'{DATA}/pr_review_summary_complete.csv', low_memory=False,
                          usecols=['id', 'agent', 'state', 'is_merged', 'task_type', 'stars', 'repo_name'])
    return reviews, rcomments, pull, summary


def build():
    reviews, rcomments, pull, summary = load()

    # scope: the curated subset, all five authoring agents
    scope = set(summary['id'])
    A = reviews[reviews.pr_id.isin(scope)].copy()
    # Consider only the three decisions GitHub documents for submitting a review
    # (comment / approve / request changes). DISMISSED is not a decision a
    # reviewer makes: it is set when someone with write access voids an
    # already-submitted review, so its verdict no longer stands; PENDING never
    # occurs here because an unsubmitted review carries no timestamp.
    A = A[A.state.isin(['COMMENTED', 'APPROVED', 'CHANGES_REQUESTED'])].copy()
    with_inline = set(rcomments.pull_request_review_id.dropna().astype(int))
    A['has_inline'] = A.id.isin(with_inline)
    A['text'] = A.body.fillna('').str.strip()
    A['has_summary'] = A.text != ''

    meta = summary.set_index('id')
    A['authoring_agent'] = A.pr_id.map(meta['agent'])

    # ------------------------------------------------------------ reviewer classification
    def system_of(row):
        s = SYSTEM_OF.get(str(row.user))
        if s:
            return s
        return None                                  # unmapped: human or unknown bot

    A = A[~A.user.isin(NON_AI_AUTOMATION)].copy()      # automation, not AI review
    A['reviewer_system'] = A.apply(system_of, axis=1)
    A['is_ai'] = A.reviewer_system.notna()
    A['author_system'] = A.authoring_agent.map(AGENT_TO_SYSTEM)

    def actor_kind(r):
        if not r.is_ai:
            return 'human'
        return 'same-system' if r.reviewer_system == r.author_system else 'cross-system'
    A['actor_kind'] = A.apply(actor_kind, axis=1)

    # actor key: system identity for AI, login for humans
    A['actor'] = np.where(A.is_ai, A.reviewer_system, A.user.astype(str))

    # ------------------------------------------------------------ episode aggregation
    g = A.groupby(['pr_id', 'actor'], dropna=False)
    ep = pd.DataFrame({
        'submissions':   g.size(),
        'bare':          g.apply(lambda d: ((~d.has_summary) & (~d.has_inline)).any(), include_groups=False),
        'summary':       g.apply(lambda d: (d.has_summary & ~d.has_inline).any(), include_groups=False),
        'inline':        g.apply(lambda d: d.has_inline.any(), include_groups=False),
        'inline_n':      g.apply(lambda d: int(d.has_inline.sum()), include_groups=False),
        'summary_chars': g.apply(lambda d: int(d.text.str.len().sum()), include_groups=False),
        'first_at':      g['submitted_at'].min(),
        'last_at':       g['submitted_at'].max(),
        'actor_kind':    g['actor_kind'].first(),
        'is_ai':         g['is_ai'].first(),
        'authoring_agent': g['authoring_agent'].first(),
        'states':        g['state'].apply(lambda s: '+'.join(sorted(set(s)))),
    }).reset_index()

    # form of the episode: what it produced
    def form_of(r):
        if r.inline and r.summary:  return 'summary + inline'
        if r.inline:                return 'inline only'
        if r.summary:               return 'summary only'
        return 'bare verdict'
    ep['form'] = ep.apply(form_of, axis=1)

    ep['first_at'] = pd.to_datetime(ep.first_at, errors='coerce', utc=True)
    ep['last_at'] = pd.to_datetime(ep.last_at, errors='coerce', utc=True)

    ep.to_csv(f'{DATA}/pr_episodes.csv', index=False)

    # ------------------------------------------------------------ PR profile
    pr = pd.DataFrame({
        'episodes':        g.size().groupby('pr_id').size(),
        'episodes_ai':     A[A.is_ai].groupby('pr_id')['actor'].nunique(),
        'episodes_human':  A[~A.is_ai].groupby('pr_id')['actor'].nunique(),
        'any_same':        A[A.actor_kind == 'same-system'].groupby('pr_id').size().gt(0),
        'any_cross':       A[A.actor_kind == 'cross-system'].groupby('pr_id').size().gt(0),
        'any_human':       A[A.actor_kind == 'human'].groupby('pr_id').size().gt(0),
        'any_inline':      A.groupby('pr_id')['has_inline'].any(),
        'any_summary':     A.groupby('pr_id')['has_summary'].any(),
    }).reset_index().rename(columns={'index': 'pr_id'})
    for c in ['any_same', 'any_cross', 'any_human', 'any_inline', 'any_summary']:
        pr[c] = pr[c].fillna(False)
    pr['authoring_agent'] = pr.pr_id.map(meta['agent'])

    def pr_config(r):
        parts = [n for n, f in (('same', r.any_same), ('cross', r.any_cross), ('human', r.any_human)) if f]
        return '+'.join(parts) if parts else 'none'
    pr['review_config'] = pr.apply(pr_config, axis=1)

    def pr_substance(r):
        if r.any_inline:  return 'line-anchored'
        if r.any_summary: return 'summary only'
        return 'bare verdicts only'
    pr['substance'] = pr.apply(pr_substance, axis=1)
    pr.to_csv(f'{DATA}/pr_review_profile.csv', index=False)

    # ------------------------------------------------------------ report
    print(f'submissions (channel A): {len(A):,}   episodes: {len(ep):,}   '
          f'PRs reviewed: {A.pr_id.nunique():,} of {len(scope):,} curated')
    print(f'inflation factor: {len(A)/len(ep):.2f} submissions per episode\n')

    print('=== RQ1 main table: episodes by actor kind x form ===')
    t = pd.crosstab(ep.actor_kind, ep.form, margins=True)
    print(t.to_string())
    print('\n=== same / cross split by reviewer system (AI episodes) ===')
    ai = ep[ep.is_ai]
    print(pd.crosstab(ai.actor_kind, ai.actor, margins=True).to_string())
    print('\n=== PR-level review configuration ===')
    print(pr.review_config.value_counts().to_string())
    print('\n=== PR-level substance ===')
    print(pr.substance.value_counts().to_string())
    print('\n=== unmapped reviewers (not in the identity table) ===')
    unk = A[~A.is_ai]
    bots = unk[unk.user.astype(str).str.contains(r'\[bot\]$|bot$|-bot', case=False, regex=True)]
    print(f'  reviews by login not in SYSTEM_OF: {len(unk):,}')
    print(f'    of which look like bots: {len(bots):,} across {bots.user.nunique()} logins')
    if len(bots):
        print('    top:', bots.user.value_counts().head(8).to_dict())
    return ep, pr


if __name__ == '__main__':
    ep, pr = build()
    print('\nsaved data/pr_episodes.csv and data/pr_review_profile.csv')
