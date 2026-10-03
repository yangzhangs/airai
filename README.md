# Artifact

## Overview

This package supports the replication of our empirical study of AI-on-AI review. The package contains the curated tables, the coded samples with their double-coding artifacts, the three coding instruments (codebooks), and the verification scripts.

Review-comment text is not redistributed (GitHub content policy), with one exception: the role-coding worksheet carries the short human-reply bodies it labels, with third-party account names replaced by pseudonyms. Comments elsewhere are provided as identifiers with lengths and reply flags and can be re-fetched from GitHub/AIDev.

---

## Directory Structure

```
.
├── README.md                            # This file
├── ETHICS.md                            # Research-ethics and data-handling statement
├── codebooks/                           # The coding instruments behind the coded samples
│   ├── review_functions_inline.md       # Inline-comment codebook (10 label codes, boundary rules, worked examples)
│   ├── review_functions_summary.md      # Summary codebook (12 label codes, boundary notes)
│   └── reply_roles.md                   # Human-reply role codebook (5 roles, boundary rules, agreement)
├── data/
│   ├── curated_pr_metadata.csv          # The 33,596 curated AIDev PRs (id, agent, dates, task, stars)
│   ├── review_events_final.csv          # The 28,714 review events with actor labels
│   ├── review_comments_final.csv        # Review comments of the curated corpus (lengths, reply flags)
│   ├── pr_review_profile.csv            # Per-PR review configuration and substance
│   ├── ai_reviewer_accounts.csv         # Bot accounts -> system identities, with the exclusions
│   ├── labeling_full_coded.csv          # Same-system inline sample + the original cross-system draw
│   ├── cross_inline_sample_coded.csv    # Cross-system inline sample (357)
│   ├── rq2_summary_sample_coded.csv     # Same-system summary sample (275)
│   ├── cross_summary_sample_coded.csv   # Cross-system summary sample (348)
│   ├── rq2_sample_shares.json           # Per-stratum function shares
│   ├── rq2_kappa_redrawn_samples.json   # Four-stratum double-coding agreement
│   ├── rq3_roles_pilot.csv              # Role coding, pilot round (50 replies)
│   ├── rq3_roles_rest.csv               # Role coding, remaining replies (266)
│   ├── rq3_kappa_rounds.json            # Role-coding agreement rounds
│   └── doublecoding/                    # Double-coding artifacts and adjudication logs (see its README)
└── scripts/
    ├── verify_statistics.py             # Recomputes the paper's statistics from data/ (coverage below)
    ├── sample_shares.py                 # Regenerates rq2_sample_shares.json
    ├── rq2_agreement.py                 # Recomputes the four-stratum coding agreement
    ├── reply_roles_agreement.py         # Recomputes the role-coding agreement rounds
    └── presence_regression.py           # Fits the Table 3 model and the task-control test
```

---

## Data Description

### `data/curated_pr_metadata.csv`
The 33,596 curated AIDev PRs (the subset the study draws on) with basic metadata. **Key columns:** `id`, `agent` (authoring agent), `created_at`, `merged_at`, `is_merged`, `task_type`, `repo_name`, `stars`.

### `data/review_events_final.csv`
The 28,714 review events carried by the 8,047 reviewed AI-authored PRs, one row per recorded review submission. **Key columns:** `id`, `pr_id`, `user`, `user_type`, `state` (COMMENTED, APPROVED, CHANGES_REQUESTED), `submitted_at`, `actor` (same-system / cross-system / human), `reviewer_system`, `authoring_agent`, `task_type`, `repo_name`, `is_merged`.

### `data/review_comments_final.csv`
The review comments of the curated corpus (81,716 rows; the 26,443 on the 8,047 reviewed PRs are the analyzed set), one row per inline comment, with no bodies. **Key columns:** `id`, `pull_request_review_id`, `pr_id`, `user`, `user_type`, `in_reply_to_id`, `created_at`, `char_length`, `owner_actor` (the actor of the review the comment belongs to), `is_human_reply`.

### `data/pr_review_profile.csv`
The per-PR review profile of the 8,047 reviewed PRs: which actors reviewed the PR ((`any_same`, `any_cross`, `any_human`), which written forms occur (`any_inline`, `any_summary`), the workflow label `review_config`, and the content `substance` flag.

### `data/ai_reviewer_accounts.csv`
The 58 bot accounts screened during identification and their mapping to system identities and roles (Section 2.2 of the paper); 32 of the accounts appear in the curated review records, and the automation exclusions are marked. Note that this file is the full screening roster: accounts marked `excluded automation` and accounts outside the curated records are kept so the screening decisions can be audited.

### The coded review-function samples (Sections 2.3 and 3.2)
- `labeling_full_coded.csv` (714 rows): the 364 same-system inline comments and the original 350-comment cross-system draw, with the adjudicated `code`.
- `cross_inline_sample_coded.csv` (357 rows): the analyzed cross-system inline sample (seed 20261005), with the coded `code` and the rule-based `rule_code` kept alongside for comparison.
- `rq2_summary_sample_coded.csv` (275 rows): the same-system summary sample; its label column is `summary_code` (all other coded files use `code`).
- `cross_summary_sample_coded.csv` (348 rows): the cross-system summary sample (seed 20261006), `code` + `rule_code`.

**Pilot and remaining waves.** Within each of the four strata, the first 50 units drawn are the pilot round that fixed the codebook, and the remaining units were labeled under it. The membership is recorded per unit in the `round` column (`pilot` / `rest` / `completion`) of the four double-coding files in `data/doublecoding/`, and `scripts/rq2_agreement.py` prints the pilot and remaining agreement of each stratum next to the released values.

The two cross-system samples are drawn uniformly at random from the pools of the AI reviewing systems identified in Section 2.2 -- the identification and screening happen once, in RQ1, and RQ2 samples the resulting AI-only pools directly, with no post-hoc screening: 357 inline comments of the 5,130 (seed 20261005) and 348 summaries of the 3,732 (seed 20261006), the sizes Cochran's rule gives for the two populations. Human and same-system strata follow the same rule.

### The double-coding artifacts (`data/doublecoding/`)
The full-sample second coding of all four strata (`same_inline_`, `cross_inline_`, `same_summary_`, `cross_summary_sample_doublecoding.csv`; each with `pass1`, `pass2`, the wave (`round`), and the adjudicated `final`), the adjudication log with a per-unit reason for all 79 disagreements, and the RQ3 role coding over the 316 sampled replies (`roles_*` files; the nine-reply completion wave included). See the README in that directory for the file table and the boundary decision rules.

### The RQ3 human replies (Section 3.3)
- `rq3_roles_pilot.csv` / `rq3_roles_rest.csv`: the 50-reply pilot (the first draw, seed 20260930, which fixed the role codebook) and the 266 remaining replies of the 316 coded sample, with both annotators' labels.
- `rq3_kappa_rounds.json`: agreement per round, kappa 0.74 (pilot), 0.85 (remaining), 0.83 pooled.
- The completion wave that brought the sample from 307 to 316 replies (nine replies drawn from the raw comment table at seed 20261001) is already folded into the released files; the worksheet with its reply bodies is part of `data/doublecoding/roles_blind_full.csv`.

### Derived JSONs
`rq2_sample_shares.json` (per-stratum function shares), `rq2_kappa_redrawn_samples.json` (four-stratum agreement figures), and `rq3_kappa_rounds.json` (role-coding agreement); each is regenerated by the script named in Reproduction Steps below.

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's five functions and ten leaves (Section 3.2.2) aggregate the per-form label sets of the two function codebooks, which differ by written form: the overview and digest labels and the approval verdict arise on summaries only, and change acknowledgment on inline comments only. `reply_roles.md` defines the five human-reply roles with the boundary rules decided on the adjudicated cases.

---

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the statistics, sample and agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/presence_regression.py`).

---

## Reproduction Steps

All commands run from the package root and read only `data/`.

### The statistics

```bash
python3 scripts/verify_statistics.py
```

Prints, next to the value quoted in the paper, every statistic the package recomputes: the RQ1 review configurations, review-type shares and pairings; the RQ2 review-form shares, inline length and arrival statistics, the function taxonomy and the sampling sizes; and the RQ3 presence, verdict, merge and timing statistics and the reply-role sample and distribution. Two families cannot be recomputed from the package because they need the review summary text (`pr_reviews.body`), which is not redistributed under the GitHub content policy: the per-agent summary counts of Table 1 (and with them the summary-text splits of Table 2 and the summary length/arrival statistics of Section 3.2.1). For those, the script checks the published counts as carried by the tables.

### Samples, shares and agreement

```bash
python3 scripts/sample_shares.py            # per-stratum function shares
python3 scripts/rq2_agreement.py            # four-stratum double-coding agreement
python3 scripts/reply_roles_agreement.py    # role-coding agreement rounds
```

### The model

```bash
python3 scripts/presence_regression.py      # Table 3 (repository-clustered SEs) and the task-control test
```

---

## Notes

- **Text policy.** Review and comment text is not redistributed, except the short human-reply bodies carried by one role-coding worksheet (`data/doublecoding/roles_blind_full.csv`), which are needed to interpret the role labels; third-party account names inside those bodies are replaced by pseudonyms. The excerpts quoted in the paper are reproduced for research purposes with the repliers' names pseudonymized.
- **Identifiers only.** Comments elsewhere appear as identifiers with lengths and reply flags; no names, email addresses or other personal data are included.
- **Source data.** All PRs, reviews and comments come from the AIDev dataset (Li et al., 2025), curated subset: 33,596 PRs from 2,807 repositories with more than 100 stars. The raw AIDev tables are not redistributed; the released event and comment tables are the analysis inputs.
- **Ethics and data handling.** See `ETHICS.md`.
