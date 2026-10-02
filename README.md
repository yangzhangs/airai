# Artifact for "When AI Reviews AI: An Empirical Study of AI Code Reviews on AI-Authored Pull Requests"

## Overview

This package supports the replication of an empirical study of AI-on-AI code
review: the review that AI-authored pull requests receive from AI systems. The
study analyzes 8,047 reviewed AI-authored PRs and the 28,714 review events they
carry, separating *same-system* review (the reviewing system matches the PR's
authoring agent, e.g., Copilot reviewing a Copilot-authored PR) from
*cross-system* review; codes samples of the review text across four strata (364
and 357 inline comments, 275 and 348 summaries, 1,344 units in total) into a
five-category function taxonomy; and codes 316 sampled human replies into five
participation roles. Every statistic quoted in the paper is recomputed from the
released tables by `scripts/verify_statistics.py`.

The package contains the curated tables, the coded samples with their
double-coding artifacts, the three coding instruments (codebooks), and the
verification scripts. Review-comment text is not redistributed (GitHub content
policy), with one exception: the role-coding worksheets carry the short
human-reply bodies they label. Comments elsewhere are provided as identifiers
with lengths and reply flags and can be re-fetched from GitHub/AIDev with the
included recipes.

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
│   ├── pr_episodes.csv                  # Per-(PR × actor) review episodes
│   ├── ai_reviewer_accounts.csv         # Bot accounts -> system identities, with the exclusions
│   ├── labeling_full_coded.csv          # Same-system inline sample + the original cross-system draw
│   ├── cross_inline_sample_coded.csv    # Cross-system inline sample (357)
│   ├── rq2_summary_sample_coded.csv     # Same-system summary sample (275)
│   ├── cross_summary_sample_coded.csv   # Cross-system summary sample (348)
│   ├── cursor_same_system_coded.csv     # Cursor same-system register (26)
│   ├── rq2_sample_shares.json           # Per-stratum function shares
│   ├── rq2_kappa_redrawn_samples.json   # Four-stratum double-coding agreement
│   ├── rq3_roles_pilot.csv              # Role coding, pilot round (50 replies)
│   ├── rq3_roles_rest.csv               # Role coding, remaining replies (266)
│   ├── rq3_kappa_rounds.json            # Role-coding agreement rounds
│   └── doublecoding/                    # Double-coding artifacts and adjudication logs (see its README)
└── scripts/
    ├── verify_statistics.py             # Recomputes every statistic quoted in the paper
    ├── 22_build_review_episodes.py      # Rebuilds the event and comment tables from raw AIDev
    ├── 56_sample_shares.py              # Regenerates rq2_sample_shares.json
    ├── 57_rq2_agreement.py              # Recomputes the four-stratum agreement figures
    ├── 58_rq3_roles_pilot_split.py      # Recomputes the role-coding agreement rounds
    ├── 62_presence_regression.py        # Fits the Table 3 model and the task-control test
    ├── 63_cursor_contrast.py            # Checks the Cursor same-system register (26 units)
    ├── 69_sample_reply_roles_completion.py  # Draws the nine-reply completion wave
    └── 70_roles_completion_update.py    # Folds the wave into the released coding files
```

---

## Data Description

### `data/curated_pr_metadata.csv`
The 33,596 curated AIDev PRs (the subset the study draws on) with basic
metadata. **Key columns:** `id`, `agent` (authoring agent), `created_at`,
`is_merged`, `task_type`, `repo_name`, `stars`.

### `data/review_events_final.csv`
The 28,714 review events carried by the 8,047 reviewed AI-authored PRs, one row
per recorded review submission. **Key columns:** `id`, `pr_id`, `user`,
`user_type`, `state` (COMMENTED, APPROVED, CHANGES_REQUESTED), `submitted_at`,
`actor` (same-system / cross-system / human), `reviewer_system`,
`authoring_agent`, `task_type`, `repo_name`, `is_merged`.

### `data/review_comments_final.csv`
The review comments of the curated corpus (81,716 rows; the 26,443 on the 8,047
reviewed PRs are the analyzed set), one row per inline comment, with no bodies.
**Key columns:** `id`, `pull_request_review_id`, `pr_id`, `user`, `user_type`,
`in_reply_to_id`, `created_at`, `char_length`, `owner_actor` (the actor of the
review the comment belongs to), `is_human_reply`.

### `data/pr_review_profile.csv`
The per-PR review profile of the 8,047 reviewed PRs: which actors reviewed the
PR (`any_same`, `any_cross`, `any_human`), which written forms occur
(`any_inline`, `any_summary`), the workflow label `review_config`, and the
content `substance` flag.

### `data/pr_episodes.csv`
Per-(PR × actor) review episodes: what each actor's review produced
(`submissions`, `bare`, `summary`, `inline`, `inline_n`, `summary_chars`) and
when it ran (`first_at`, `last_at`; `actor_kind`, `is_ai`).

### `data/ai_reviewer_accounts.csv`
The 58 bot accounts and their mapping to system identities and roles
(Section 2.2 of the paper); 32 of the accounts appear in the curated review
records, and the automation exclusions are marked.

### The coded review-function samples (Sections 2.3 and 3.2)
- `labeling_full_coded.csv` (714 rows): the 364 same-system inline comments and
  the original 350-comment cross-system draw, with the adjudicated `code`.
- `cross_inline_sample_coded.csv` (357 rows): the analyzed cross-system inline
  sample (seed 20261005), with the coded `code` and the rule-based `rule_code`
  kept alongside for comparison.
- `rq2_summary_sample_coded.csv` (275 rows): the same-system summary sample;
  its label column is `summary_code` (all other coded files use `code`).
- `cross_summary_sample_coded.csv` (348 rows): the cross-system summary sample
  (seed 20261006), `code` + `rule_code`.
- `cursor_same_system_coded.csv` (26 rows): the Cursor same-system inline
  comments coded under the codebook (all code-directed), with the rule-based
  labels alongside.

The two cross-system samples are drawn uniformly at random from the pools of
the AI reviewing systems identified in Section 2.2 -- the identification and
screening happen once, in RQ1, and RQ2 samples the resulting AI-only pools
directly, with no post-hoc screening: 357 inline comments of the 5,130 (seed
20261005) and 348 summaries of the 3,732 (seed 20261006), the sizes Cochran's
rule gives for the two populations.

### The double-coding artifacts (`data/doublecoding/`)
The full-sample second coding of all four strata (`same_inline_`, `cross_inline_`,
`same_summary_`, `cross_summary_sample_doublecoding.csv`; each with pass1,
pass2, the double-coding wave, and the adjudicated final), the adjudication log
with a per-unit reason for all 79 disagreements, the a-priori re-coding batch
that refined the cross-system inline codebook (`inline_cross_v2/`), and the RQ3
role coding over the 316 sampled replies (`roles_*` files; the nine-reply
completion wave included). See the README in that directory for the file table
and the boundary decision rules.

### The RQ3 human replies (Section 3.3)
- `rq3_roles_pilot.csv` / `rq3_roles_rest.csv`: the 50-reply pilot and the 266
  remaining replies of the 316 coded sample, with both annotators' labels.
- `rq3_kappa_rounds.json`: agreement per round, kappa 0.74 (pilot), 0.85
  (remaining), 0.83 pooled.
- The draw of the nine-reply completion wave is
  `data/doublecoding/roles_completion_draw.csv` (seed 20261001).

### Derived JSONs
`rq2_sample_shares.json` (per-stratum function shares),
`rq2_kappa_redrawn_samples.json` (four-stratum agreement figures), and
`rq3_kappa_rounds.json` (role-coding agreement); each is regenerated by the
script named in Reproduction Steps below.

---

## Codebooks

The three codebooks are the instruments behind the coded samples. The paper's
five functions and ten leaves (Section 3.2.2) aggregate the per-form label sets
of the two function codebooks, which differ by written form: the overview and
digest labels and the approval verdict arise on summaries only, and change
acknowledgment on inline comments only. `reply_roles.md` defines the five
human-reply roles with the boundary rules decided on the adjudicated cases.

---

## Software Requirements

- **Python 3.9+** with `pandas`, `numpy` and `scipy` for the statistics, sample
  and agreement scripts.
- `statsmodels` for the Table 3 regression (`scripts/62_presence_regression.py`).
- `pyarrow` for the completion-wave draw
  (`scripts/69_sample_reply_roles_completion.py`).

---

## Reproduction Steps

All commands run from the package root.

### Every quoted statistic

```bash
python3 scripts/verify_statistics.py
```

Reads only `data/` and prints each inferential and descriptive statistic next
to the value quoted in the paper: chi-square and Kruskal-Wallis tests with
effect sizes, reply rates and merge outcomes, the Table 3 regression rows
(review types, agents, stars, month and the task-type panel) and the joint
task-control test.

### Samples, shares and agreement

```bash
python3 scripts/56_sample_shares.py          # per-stratum function shares
python3 scripts/57_rq2_agreement.py          # four-stratum double-coding agreement
python3 scripts/58_rq3_roles_pilot_split.py  # role-coding agreement rounds
```

The RQ3 role sample codes 316 replies, the size Cochran's rule gives for the
1,787-reply frame; the pilot set stays fixed at its first draw (seed 20260930)
and nine replies arrived in a completion wave (seed 20261001).

### Models and register checks

```bash
python3 scripts/62_presence_regression.py    # Table 3 (repository-clustered SEs) and the task-control test
python3 scripts/63_cursor_contrast.py        # the Cursor same-system register (26 of 26 code-directed)
```

### Recipes for the raw data

`scripts/22_build_review_episodes.py` rebuilds the event and comment tables
from the raw AIDev curated-subset tables (`pr_reviews`, `pr_review_comments`,
`pr_pull`, exported to `/tmp` as parquet). The completion wave is reproduced by
`scripts/69_sample_reply_roles_completion.py` and
`scripts/70_roles_completion_update.py`; 69 needs a local copy of the raw
review-comment table (its path is set via the `AIDEV_V2_COMMENTS` environment
variable), and 70 is a one-shot fold of the wave into the released coding files.

---

## Notes

- **Text policy.** Review and comment text is not redistributed, except the
  short human-reply bodies carried by the role-coding worksheets
  (`data/doublecoding/roles_blind*.csv`, `roles_disagreements.csv`), which are
  needed to interpret the role labels. The excerpts quoted in the paper are
  reproduced for research purposes with the repliers' names pseudonymized.
- **Identifiers only.** Comments elsewhere appear as identifiers with lengths
  and reply flags; no personally identifiable information is included.
- **Source data.** All PRs, reviews and comments come from the AIDev dataset
  (Li et al., 2025), curated subset: 33,596 PRs from 2,807 repositories with
  more than 100 stars.
- **Ethics and data handling.** See `ETHICS.md`.
