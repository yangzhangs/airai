# Artifact

## Overview

This package supports the replication of our empirical study of AI-on-AI review on the curated AIDev subset: the derived tables, the coded samples with their double-coding records, the three codebooks, and statistics scripts.

## Directory Structure

```
.
├── README.md
├── .gitignore
├── codebooks/                           # The coding instruments behind the coded samples
│   ├── review_functions_inline.md       # RQ2: inline-comment codebook (boundary rules, worked examples)
│   ├── review_functions_summary.md      # RQ2: summary codebook (boundary notes)
│   └── reply_roles.md                   # RQ3: human-reply role codebook (5 roles, boundary rules)
├── data/
│   ├── common/                          # Tables shared by all RQs (no RQ marker)
│   │   ├── curated_pr_metadata.csv      # 33,596 curated PRs (agent, dates, task, stars, merge)
│   │   ├── review_events_final.csv      # 28,714 review events (actor, reviewer system, verdict)
│   │   ├── review_comments_final.csv    # 26,443 inline comments (length, reply flag)
│   │   ├── review_summary_meta.csv      # 28,714 events: summary-text flag + character count
│   │   └── pr_review_profile.csv        # 8,047 reviewed PRs: configuration + substance
│   ├── rq1/
│   │   └── ai_reviewer_accounts.csv     # 41-row account screening record (32 AI accounts)
│   ├── rq2/
│   │   ├── same_system_inline_coded.csv      # coded sample, 364 units
│   │   ├── cross_system_inline_coded.csv     # coded sample, 357 units
│   │   ├── same_system_summary_coded.csv     # coded sample, 275 units
│   │   ├── cross_system_summary_coded.csv    # coded sample, 348 units
│   │   ├── full_corpus_inline_rule_coded.csv # rule-coded inline corpus, 26,443 units
│   │   ├── rq2_sample_shares.json            # per-stratum function shares
│   │   ├── rq2_kappa_redrawn_samples.json    # agreement per stratum and wave
│   │   └── doublecoding/
│   │       ├── README.md                            # waves and agreement tables
│   │       ├── same_inline_sample_doublecoding.csv   # 364 units: pass1, pass2, wave, adjudicated final
│   │       ├── cross_inline_sample_doublecoding.csv  # 357 units, same columns
│   │       ├── same_summary_sample_doublecoding.csv  # 275 units, same columns
│   │       ├── cross_summary_sample_doublecoding.csv # 348 units, same columns
│   │       └── adjudication_log.csv                  # the 79 arbitrated disagreements
│   └── rq3/
│       ├── roles_pilot.csv              # first 50 replies (both annotators' labels)
│       ├── roles_rest.csv               # the 266 remaining replies (both annotators' labels)
│       ├── rq3_kappa_rounds.json        # agreement per round
│       └── doublecoding/
│           ├── README.md                        # the final role distribution
│           ├── roles_blind_full.csv             # the 316 replies as annotated (pseudonymized bodies)
│           ├── roles_full_pass1.csv             # annotator 1 labels over the 316
│           ├── roles_full_pass2.csv             # annotator 2 labels over the 316
│           ├── roles_full_final.csv             # adjudicated labels of record
│           └── roles_full_adjudication_log.csv  # the 42 arbitrated units
└── scripts/
    ├── rq1/prevalence_statistics.py     # RQ1 statistics
    ├── rq2/coding_agreement.py          # four-stratum coding agreement (kappa)
    ├── rq2/characteristics_statistics.py# RQ2 statistics
    ├── rq3/reply_roles_agreement.py     # role-coding kappa and the pilot/remaining split
    ├── rq3/presence_regression.py       # the Table 3 logistic regression
    └── rq3/human_loop_statistics.py     # RQ3 statistics
```


## RQ1 - Prevalence

- **Account identification** - `data/rq1/ai_reviewer_accounts.csv`: 40 candidates from the platform bot flag (31 kept as AI reviewers, 9 excluded as automation) plus 1 added by name inspection; 32 AI accounts in total.
- **Reviewed PRs and review configurations (Table 1)** - `curated_pr_metadata.csv`, `pr_review_profile.csv`, and for Table 1 also `review_events_final.csv`, `review_summary_meta.csv`, `review_comments_final.csv`.
- **AI-on-AI review types and pairings** - `review_events_final.csv`.

```bash
python3 scripts/rq1/prevalence_statistics.py   # RQ1 statistics
```

## RQ2 - Characteristics

- **Sampling design** - the four coded samples; the four populations and the Cochran sample sizes recomputed from `review_comments_final.csv` and `review_summary_meta.csv`.
- **Review form (Table 2)** - `review_events_final.csv` + `review_summary_meta.csv` + `review_comments_final.csv`.
- **Review length** - `review_comments_final.csv` (comment lengths), `review_summary_meta.csv` (summary lengths).
- **Review arrival time** - `review_events_final.csv` + `curated_pr_metadata.csv` (PR creation times).
- **Review functions** - the four coded samples, the two function codebooks, `rq2_sample_shares.json`.
- **Review type comparison and robustness** - the four coded samples plus `full_corpus_inline_rule_coded.csv` (joined to `review_comments_final.csv` for reviewer and authoring agent).
- **Double-coding record** - `data/rq2/doublecoding/`: both blind passes over every coded unit, the wave per unit, and the adjudicated finals.

```bash
python3 scripts/rq2/coding_agreement.py             # four-stratum coding agreement (kappa)
python3 scripts/rq2/characteristics_statistics.py   # RQ2 statistics
```

## RQ3 - Human-in-the-Loop

- **Reply frame and sampling** - `review_comments_final.csv` (reply flag; 1,787 replies), `roles_pilot.csv` and `roles_rest.csv` (the 50+266 split).
- **Human presence, verdicts, merge outcomes and timing (Table 4)** - `pr_review_profile.csv`, `review_events_final.csv`, `curated_pr_metadata.csv` (merge outcomes and timestamps).
- **Presence regression (Table 3)** - `pr_review_profile.csv` + `curated_pr_metadata.csv` + `review_events_final.csv`.
- **Reply roles** - `roles_pilot.csv`, `roles_rest.csv`, `rq3_kappa_rounds.json`, and `data/rq3/doublecoding/`: the blind worksheet, both annotators' passes, the adjudicated labels of record, and the adjudication log.
- **Role codebook** - `codebooks/reply_roles.md`.

```bash
python3 scripts/rq3/presence_regression.py     # the Table 3 logistic regression
python3 scripts/rq3/reply_roles_agreement.py   # role-coding kappa and the pilot/remaining split
python3 scripts/rq3/human_loop_statistics.py   # RQ3 statistics
```

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's five functions and ten leaves aggregate the per-form label sets of the two function codebooks, which differ by written form: the overview and digest labels and the approval verdict arise on summaries only, and change acknowledgment on inline comments only.

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the statistics and agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/rq3/presence_regression.py`).

## Notes

- **Data.** The study analyzes public GitHub data only. Review and comment text is not redistributed, except the short human-reply bodies in the RQ3 blind worksheet, with third-party account names pseudonymized.
- **Identifiers only.** Comments appear as identifiers with lengths and reply flags, and reviews as a summary-text flag with its character count; no review text and no personal data beyond public GitHub logins are included.
- **Source data.** All tables derive from the [AIDev](https://huggingface.co/datasets/hao-li/AIDev) curated subset (33,596 PRs from 2,807 repositories with more than 100 stars); the raw tables are not redistributed.
