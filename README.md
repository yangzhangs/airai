# Artifact

## Overview

This package supports the replication of our empirical study of AI-on-AI review on the curated AIDev subset: the derived tables, the coded samples with their double-coding and adjudication records, the three codebooks, and one statistics script per RQ that recomputes the figures of Sections 3.1-3.3 next to the released values.

## The AIDev dataset

The study is built on [**AIDev**](https://huggingface.co/datasets/hao-li/AIDev), the largest public collection of pull requests (PRs) autonomously authored by AI coding agents on GitHub. The original release aggregates 932,791 agent-authored PRs produced by five coding agents (OpenAI Codex, Devin, GitHub Copilot, Cursor, and Claude Code) across 116,211 repositories with 72,189 developers; its curated subset (repositories with more than 100 stars) is enriched with the review activity around those PRs, and this package releases the derived tables and coding artifacts our study uses. The raw AIDev tables are not redistributed here.

---

## Directory Structure

```
.
├── README.md
├── ETHICS.md                            # Research-ethics and data-handling statement
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
│   │       ├── README.md                            # waves, boundary rules, agreement tables
│   │       ├── same_inline_sample_doublecoding.csv   # 364 units: pass1, pass2, wave, adjudicated final
│   │       ├── cross_inline_sample_doublecoding.csv  # 357 units, same columns
│   │       ├── same_summary_sample_doublecoding.csv  # 275 units, same columns
│   │       ├── cross_summary_sample_doublecoding.csv # 348 units, same columns
│   │       └── adjudication_log.csv                  # the 79 disagreements with one-line reasons
│   └── rq3/
│       ├── roles_pilot.csv              # first 50 replies (both annotators' labels)
│       ├── roles_rest.csv               # the 266 remaining replies (both annotators' labels)
│       ├── rq3_kappa_rounds.json        # agreement per round
│       └── doublecoding/
│           ├── README.md                        # boundary rules and the final role distribution
│           ├── roles_blind_full.csv             # the 316 replies as annotated (pseudonymized bodies)
│           ├── roles_full_pass1.csv             # annotator 1 labels over the 316
│           ├── roles_full_pass2.csv             # annotator 2 labels over the 316
│           ├── roles_full_final.csv             # adjudicated labels of record
│           └── roles_full_adjudication_log.csv  # 42 arbitrated units with one-line reasons
└── scripts/
    ├── rq1/prevalence_statistics.py     # Section 3.1
    ├── rq2/coding_agreement.py          # four-stratum coding agreement
    ├── rq2/characteristics_statistics.py# Section 3.2
    ├── rq3/reply_roles_agreement.py     # role-coding agreement rounds
    ├── rq3/presence_regression.py       # Table 3
    └── rq3/human_loop_statistics.py     # Section 3.3
```

Every RQ-specific CSV opens with one `#`-comment line naming its RQ; read them with `comment='#'` (the released scripts do). `data/common/` tables carry no marker; JSON files are identified by folder.

---

## RQ1 - Prevalence of AI-on-AI Review (Section 3.1)

- **Account identification (Section 2.2)** - `data/rq1/ai_reviewer_accounts.csv`: 40 candidates from the platform bot flag (31 kept as AI reviewers, 9 excluded as automation) plus 1 added by name inspection; 32 AI accounts in total.
- **Reviewed PRs and review configurations (Section 3.1.1, Table 1)** - `curated_pr_metadata.csv`, `pr_review_profile.csv`, and for Table 1 also `review_events_final.csv`, `review_summary_meta.csv`, `review_comments_final.csv`.
- **AI-on-AI review types and pairings (Sections 3.1.2-3.1.3)** - `review_events_final.csv`.

```bash
python3 scripts/rq1/prevalence_statistics.py   # recomputes the Section 3.1 figures next to the released values
```

## RQ2 - Characteristics of AI-on-AI Review (Section 3.2)

- **Sampling design (Section 2.3)** - the four coded samples; the four populations and the Cochran sample sizes recomputed from `review_comments_final.csv` and `review_summary_meta.csv`.
- **Review form (Table 2)** - `review_events_final.csv` + `review_summary_meta.csv` + `review_comments_final.csv`.
- **Review length** - `review_comments_final.csv` (comment lengths), `review_summary_meta.csv` (summary lengths).
- **Review arrival time** - `review_events_final.csv` + `curated_pr_metadata.csv` (PR creation times).
- **Review functions (Section 3.2.2)** - the four coded samples, the two function codebooks, `rq2_sample_shares.json`.
- **Review type comparison and robustness (Section 3.2.3)** - the four coded samples plus `full_corpus_inline_rule_coded.csv` (joined to `review_comments_final.csv` for reviewer and authoring agent).
- **Double-coding record (Section 2.3)** - `data/rq2/doublecoding/`: the two blind passes over every coded unit, the wave per unit, the adjudicated final, and all 79 disagreements with a one-line reason each; the README there documents the boundary rules.

```bash
python3 scripts/rq2/coding_agreement.py             # per-stratum and wave kappa next to the released values
python3 scripts/rq2/characteristics_statistics.py   # recomputes the Section 3.2 figures next to the released values
```

## RQ3 - Human-in-the-Loop (Section 3.3)

- **Reply frame and sampling (Section 2.4)** - `review_comments_final.csv` (reply flag; 1,787 replies), `roles_pilot.csv` and `roles_rest.csv` (the 50+266 split).
- **Human presence, verdicts and timing (Section 3.3.1, Table 4)** - `pr_review_profile.csv`, `review_events_final.csv`, `curated_pr_metadata.csv` (merge outcomes and timestamps).
- **Presence regression (Table 3)** - `pr_review_profile.csv` + `curated_pr_metadata.csv` + `review_events_final.csv`.
- **Reply roles (Section 3.3.2)** - `roles_pilot.csv`, `roles_rest.csv`, `rq3_kappa_rounds.json`, and `data/rq3/doublecoding/`: the blind worksheet, both annotators' passes, the adjudicated labels of record, and the 42-unit adjudication log; the README there documents the boundary rules and the final role distribution.
- **Role codebook** - `codebooks/reply_roles.md`.

```bash
python3 scripts/rq3/presence_regression.py     # Table 3 (repository-clustered SEs) and the joint task-control test
python3 scripts/rq3/reply_roles_agreement.py   # agreement rounds and the pilot/remaining split
python3 scripts/rq3/human_loop_statistics.py   # recomputes the Section 3.3 figures next to the released values
```

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's five functions and ten leaves (Section 3.2.2) aggregate the per-form label sets of the two function codebooks, which differ by written form: the overview and digest labels and the approval verdict arise on summaries only, and change acknowledgment on inline comments only.

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the statistics and agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/rq3/presence_regression.py`).

## Notes

- **Text policy.** Review and comment text is not redistributed, except the short human-reply bodies in the RQ3 blind worksheet, with third-party account names pseudonymized; ethics and data handling are detailed in `ETHICS.md`.
- **Identifiers only.** Comments appear as identifiers with lengths and reply flags, and reviews as a summary-text flag with its character count; no review text and no personal data beyond public GitHub logins are included.
- **Source data.** All tables derive from the AIDev curated subset (33,596 PRs from 2,807 repositories with more than 100 stars); the raw tables are not redistributed.
