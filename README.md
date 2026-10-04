# Artifact

## Overview

This package supports the replication of our empirical study of AI-on-AI review on the curated AIDev subset: the derived tables, the coded samples with their double-coding records, the three codebooks, and statistics scripts.

## Directory Structure

```
.
├── README.md
├── .gitignore
├── codebooks/                           # The coding instruments behind the coded samples
│   ├── review_functions_inline.md       # RQ2: inline-comment codebook
│   ├── review_functions_summary.md      # RQ2: summary codebook
│   └── reply_roles.md                   # RQ3: human-reply role codebook
├── data/
│   ├── common/                          # Tables shared by all RQs (no RQ marker)
│   │   ├── curated_pr_metadata.csv      # 33,596 curated PRs (agent, dates, task, stars, merge)
│   │   ├── review_events_final.csv      # 28,714 review events (actor, reviewer system, verdict)
│   │   ├── review_comments_final.csv    # 26,443 inline comments (length, reply flag)
│   │   ├── review_summary_meta.csv      # 28,714 events: summary-text flag + character count
│   │   └── pr_review_profile.csv        # 8,047 reviewed PRs: configuration + substance
│   ├── rq1/
│   │   ├── ai_reviewer_accounts.csv     # 41-row account screening record (32 AI accounts)
│   │   ├── configurations.csv           # per reviewed PR: agent, task, review configuration
│   │   └── review_types.csv             # per review event: actor, reviewer system, authoring agent
│   ├── rq2/
│   │   ├── rq2_sample_shares.json            # per-stratum function shares
│   │   ├── rq2_kappa.json                    # agreement per stratum
│   │   ├── sampling_design.csv               # the four coded populations
│   │   ├── review_forms.csv                  # per review event: written-form flags
│   │   ├── comment_lengths.csv               # per inline comment: owner actor, characters
│   │   ├── summary_lengths.csv               # per summary: actor, characters
│   │   ├── arrival_times.csv                 # per review event: form flags, arrival hours
│   │   ├── copilot_comment_arrivals.csv      # per comment on Copilot PRs: arrival hours
│   │   ├── cross_sample_units.csv            # cross-system sample units with reviewer and agent
│   │   └── doublecoding/
│   │       ├── README.md               # the double-coding record and agreement
│   │       ├── same_inline_coded.csv   # 364 units: both annotations and the adjudicated final
│   │       ├── cross_inline_coded.csv  # 357 units, same columns
│   │       ├── same_summary_coded.csv  # 275 units, same columns
│   │       └── cross_summary_coded.csv # 348 units, same columns
│   └── rq3/
│       ├── rq3_kappa.json               # agreement over the reply sample
│       ├── sampling_design.csv          # the human replies in the frame
│       ├── presence.csv                 # per AI-on-AI PR: presence flags, authoring agent
│       ├── review_verdicts.csv          # per event on AI-on-AI PRs: actor, verdict, time
│       ├── merge_outcomes.csv           # per curated PR: group, merge flag, merge time
│       ├── event_times.csv              # per event on AI-on-AI PRs: actor, arrival hours
│       ├── presence_regression.csv      # per AI-on-AI PR: outcome, review types, controls
│       └── doublecoding/
│           ├── README.md            # the double-coding record and agreement
│           └── roles_full_coded.csv # 316 replies: bodies, both annotations and the adjudicated final
└── scripts/
    ├── rq1/prevalence_statistics.py     # RQ1 statistics
    ├── rq2/coding_agreement.py          # four-stratum coding agreement (kappa)
    ├── rq2/characteristics_statistics.py# RQ2 statistics
    ├── rq3/reply_roles_agreement.py     # role-coding kappa
    ├── rq3/presence_regression.py       # the Table 3 logistic regression
    └── rq3/human_loop_statistics.py     # RQ3 statistics
```


## RQ1 - Prevalence

- **Account identification** - `data/rq1/ai_reviewer_accounts.csv`: 40 candidates from the platform bot flag (31 kept as AI reviewers, 9 excluded as automation) plus 1 added by name inspection; 32 AI accounts in total.
- **Reviewed PRs and review configurations (Table 1)** - `configurations.csv` (per reviewed PR: authoring agent, task type, review configuration); Table 1 reads the common corpus tables.
- **AI-on-AI review types and pairings** - `review_types.csv` (per review event: actor, reviewer system, authoring agent).

```bash
python3 scripts/rq1/prevalence_statistics.py   # RQ1 statistics
```

## RQ2 - Characteristics

- **Sampling design** - `sampling_design.csv` (the four coded populations).
- **Review form (Table 2)** - `review_forms.csv` (per review event: written-form flags).
- **Review length** - `comment_lengths.csv` (comment lengths), `summary_lengths.csv` (summary lengths).
- **Review arrival time** - `arrival_times.csv` (event level), `copilot_comment_arrivals.csv` (the Copilot example).
- **Review functions** - the four coded samples, the two function codebooks, `rq2_sample_shares.json`.
- **Review type comparison and robustness** - the four coded samples, plus `cross_sample_units.csv` for the composition checks.
- **Double-coding record** - `data/rq2/doublecoding/`: each coded unit with both annotations and the adjudicated final; a disagreement is visible where `pass1` and `pass2` differ.

```bash
python3 scripts/rq2/coding_agreement.py             # four-stratum coding agreement (kappa)
python3 scripts/rq2/characteristics_statistics.py   # RQ2 statistics
```

## RQ3 - Human Participation

- **Reply frame and sampling** - `sampling_design.csv` (the 1,787 human replies in the frame).
- **Human presence, verdicts, merge outcomes and timing (Table 4)** - `presence.csv`, `review_verdicts.csv`, `merge_outcomes.csv`, `event_times.csv`.
- **Presence regression (Table 3)** - `presence_regression.csv`.
- **Reply roles** - `rq3_kappa.json` and `data/rq3/doublecoding/roles_full_coded.csv`: the reply bodies (pseudonymized) with both annotations, the adjudicated final, and the PR authoring agent.
- **Role codebook** - `codebooks/reply_roles.md`.

```bash
python3 scripts/rq3/presence_regression.py     # the Table 3 logistic regression
python3 scripts/rq3/reply_roles_agreement.py   # role-coding kappa
python3 scripts/rq3/human_loop_statistics.py   # RQ3 statistics
```

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's five functions and ten leaves aggregate the per-form label sets of the two function codebooks, which differ by written form: the overview and digest labels and the approval verdict arise on summaries only, and change acknowledgment on inline comments only.

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the statistics and agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/rq3/presence_regression.py`).

## Notes

- **Data.** The study analyzes public GitHub data only. Review and comment text is not redistributed, except the short human-reply bodies in `data/rq3/doublecoding/roles_full_coded.csv`, with third-party account names pseudonymized.
- **Identifiers only.** Comments appear as identifiers with lengths and reply flags, and reviews as a summary-text flag with its character count; no review text and no personal data beyond public GitHub logins are included.
- **Traceability.** The tables carry the AIDev identifiers (comment, review and pull-request ids, repository slugs); joined to the original AIDev tables they retrieve the full text of every coded unit, including the detail of each summary, inline comment and sampled reply.
- **Source data.** All tables derive from the [AIDev](https://huggingface.co/datasets/hao-li/AIDev) curated subset (33,596 PRs from 2,807 repositories with more than 100 stars); the raw tables are not redistributed.
