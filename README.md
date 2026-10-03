# Artifact

## Overview

This package supports the replication of our empirical study of AI-on-AI review: the curated tables, the coded samples with their double-coding artifacts, the three coding instruments (codebooks), and the RQ-level scripts. Review-comment text is not redistributed (GitHub content policy), with one exception: the role-coding worksheet carries the short human-reply bodies it labels, with third-party account names replaced by pseudonyms. Comments elsewhere are provided as identifiers with lengths and reply flags and can be re-fetched from GitHub/AIDev.

---

## The AIDev dataset

The study is built on **AIDev**, the largest public collection of pull requests (PRs) autonomously authored by AI coding agents on GitHub. The original release aggregates 932,791 agent-authored PRs produced by five coding agents (OpenAI Codex, Devin, GitHub Copilot, Cursor, and Claude Code) across 116,211 repositories with 72,189 developers; its curated subset (repositories with more than 100 stars) is enriched with the review activity around those PRs, and this package releases the derived tables and coding artifacts our study uses. The raw AIDev tables are not redistributed here.

- **Dataset (download and documentation):** https://huggingface.co/datasets/hao-li/AIDev
- **Paper:** *AIDev: Studying AI Coding Agents on GitHub* (MSR 2026), DOI 10.1145/3793302.3797249; see also *The Rise of AI Teammates in Software Engineering (SE) 3.0* (arXiv:2507.15003).

---

## Directory Structure

```
.
├── README.md
├── ETHICS.md                            # Research-ethics and data-handling statement
├── codebooks/                           # The coding instruments behind the coded samples
│   ├── review_functions_inline.md       # RQ2: inline-comment codebook (boundary rules, worked examples)
│   ├── review_functions_summary.md      # RQ2: summary codebook (boundary notes)
│   └── reply_roles.md                   # RQ3: human-reply role codebook (5 roles, agreement)
├── data/
│   ├── common/                          # Tables shared by all RQs (no RQ marker)
│   │   ├── curated_pr_metadata.csv      # The 33,596 curated AIDev PRs (id, agent, dates, task, stars)
│   │   ├── review_events_final.csv      # The 28,714 review events with actor labels
│   │   ├── review_comments_final.csv    # The 26,443 inline comments on the 8,047 reviewed PRs
│   │   └── pr_review_profile.csv        # Per-PR review configuration and substance (8,047 rows)
│   ├── rq1/
│   │   └── ai_reviewer_accounts.csv     # AI-account identification and screening record (41 rows)
│   ├── rq2/
│   │   ├── same_system_inline_coded.csv     # Same-system inline sample (364)
│   │   ├── cross_system_inline_coded.csv    # Cross-system inline sample (357)
│   │   ├── same_system_summary_coded.csv    # Same-system summary sample (275)
│   │   ├── cross_system_summary_coded.csv   # Cross-system summary sample (348)
│   │   ├── rq2_sample_shares.json           # Per-stratum function shares
│   │   ├── rq2_kappa_redrawn_samples.json   # Four-stratum double-coding agreement
│   │   └── doublecoding/                    # pass1/pass2/wave/final per stratum + the 79-disagreement log
│   └── rq3/
│       ├── roles_pilot.csv                  # Role coding, pilot round (50 replies)
│       ├── roles_rest.csv                   # Role coding, remaining replies (266)
│       ├── rq3_kappa_rounds.json            # Role-coding agreement rounds
│       └── doublecoding/                    # Role-coding passes, adjudication log, blind worksheet
└── scripts/
    ├── rq2/
    │   └── coding_agreement.py          # Recomputes the four-stratum coding agreement
    └── rq3/
        ├── reply_roles_agreement.py     # Recomputes the role-coding agreement rounds
        └── presence_regression.py       # Fits the Table 3 model and the task-control test
```

**Reading the files.** Every RQ-specific CSV opens with a single `#`-comment line naming its RQ; read these with `comment='#'` (the released scripts do). JSON files cannot carry comments, so their RQ is in the folder and file name. The shared tables in `data/common/` carry no marker, and no marker is needed for them.

---

## RQ1 - Prevalence of AI-on-AI Review

**Data.** The shared tables above, plus `data/rq1/ai_reviewer_accounts.csv`, the screening record behind Section 2.2: 40 candidate accounts found through the platform's bot flag (31 kept as AI reviewers, 9 excluded as automation tools such as CI/CD and code-scanning accounts), plus one further account added by inspecting accounts whose names contain `bot`; 32 AI accounts in total, each mapped to a system identity (one vendor's products are reduced to one identity).

**Results.** The RQ1 figures are counts and association tests over these tables: 8,047 reviewed PRs of 33,596 curated, carrying 28,714 review events, of which 11,693 are AI-on-AI reviews (54.5% of the reviewed PRs; 24.6% reviewed by AI alone; same-system 62.4%). No script is needed for these counts.

---

## RQ2 - Characteristics of AI-on-AI Review

**Data (`data/rq2/`).**
- The four coded strata: `same_system_inline_coded.csv` (364), `cross_system_inline_coded.csv` (357), `same_system_summary_coded.csv` (275), `cross_system_summary_coded.csv` (348) -- 1,344 coded units in total, from the strata sized by Cochran's rule for the four populations (7,005 / 5,130 / 963 / 3,732).
- Pilot and remaining waves: within each stratum, the first 50 units drawn are the pilot that fixed the codebook and the rest are the remaining units labeled under it; the membership is recorded per unit in the `round` column of the double-coding files.
- `doublecoding/`: the two blind passes, the per-unit wave, the adjudicated final per stratum, and the log of all 79 disagreements with a one-line reason each (see the README in that directory).
- `rq2_sample_shares.json`: the per-stratum function shares; `rq2_kappa_redrawn_samples.json`: the agreement figures.

**Reproduce.**

```bash
python3 scripts/rq2/coding_agreement.py    # prints per-stratum and wave kappa next to the released values
```

---

## RQ3 - Human-in-the-Loop

**Data (`data/rq3/`).**
- `roles_pilot.csv` (50 replies) and `roles_rest.csv` (266 replies): the two annotators' role labels over the 316-reply sample -- the sizes Cochran's rule gives for the 1,787-reply frame -- with the pilot being the first draw that fixed the role codebook.
- `doublecoding/`: the two blind passes over the full sample, the adjudicated labels of record, the adjudication log, and the blind worksheet `roles_blind_full.csv` (the 316 replies with their bodies; third-party account names are replaced by pseudonyms) (see the README in that directory).
- `rq3_kappa_rounds.json`: agreement per round, kappa 0.74 (pilot), 0.85 (remaining), 0.83 pooled.

**Reproduce.**

```bash
python3 scripts/rq3/reply_roles_agreement.py   # agreement rounds and the pilot/remaining split
python3 scripts/rq3/presence_regression.py     # Table 3 (repository-clustered SEs) and the task-control test
```

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's five functions and ten leaves (Section 3.2.2) aggregate the per-form label sets of the two function codebooks, which differ by written form: the overview and digest labels and the approval verdict arise on summaries only, and change acknowledgment on inline comments only. `reply_roles.md` defines the five human-reply roles with the boundary rules decided on the adjudicated cases.

---

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/rq3/presence_regression.py`).

---

## Notes

- **Text policy.** Review and comment text is not redistributed, except the short human-reply bodies carried by one role-coding worksheet (`data/rq3/doublecoding/roles_blind_full.csv`), which are needed to interpret the role labels; third-party account names inside those bodies are replaced by pseudonyms. The excerpts quoted in the paper are reproduced for research purposes with the repliers' names pseudonymized.
- **Identifiers only.** Comments appear as identifiers with lengths and reply flags; no names, email addresses or other personal data are included.
- **Source data.** All PRs, reviews and comments come from the AIDev dataset (see above), curated subset: 33,596 PRs from 2,807 repositories with more than 100 stars.
- **Ethics and data handling.** See `ETHICS.md`.
