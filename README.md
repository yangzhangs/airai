# Replication package

**When AI Reviews AI: An Empirical Study of AI Code Reviews on AI-Authored Pull Requests**

This package reproduces every statistic quoted in the paper from the artifacts
in `data/`. Raw review-comment text is not redistributed (GitHub content);
comments are provided as identifiers with lengths and reply flags, and can be
re-fetched from GitHub/AIDev with the included recipes.

## Contents

```
codebooks/                     the coding instruments (see below)
  review_functions_inline.md   the inline review-comment codebook: 10 label codes,
                               boundary rules and worked examples
  review_functions_summary.md  the review-summary codebook: 12 label codes and
                               boundary notes
  reply_roles.md               the human-reply role codebook: 5 roles, boundary
                               rules and agreement figures
data/
  curated_pr_metadata.csv      the 33,596 curated AIDev PRs (id, agent, dates,
                               is_merged, task_type, repo_name, stars)
  review_events_final.csv      the 28,714 review events of the 8,047 reviewed PRs,
                               with actor labels (human / same-system / cross-system)
  review_comments_final.csv    the inline review comments linked to those events
                               (no bodies; char_length and reply flags included)
  pr_review_profile.csv        per-PR review configuration and substance
  pr_episodes.csv              per-(PR x actor) review episodes
  ai_reviewer_accounts.csv     the 58 bot accounts -> system-identity mapping and
                               the automation exclusions (Section 2.2); 32 of the
                               accounts appear in the curated review records
  labeling_full_coded.csv      the hand-coded inline function sample: the 364
                               same-system comments and the original 350-comment
                               cross-system draw (the analyzed cross-system sample
                               is cross_inline_sample_coded.csv)
  cursor_same_system_coded.csv the 26 Cursor same-system inline comments coded under
                               the codebook (all code-directed; rule-based labels kept
                               alongside for comparison)
  cross_inline_sample_coded.csv the cross-system inline sample, 357 comments drawn
                               uniformly at random from the AI-system pool (seed
                               20261005), with the rule-based labels alongside
  cross_summary_sample_coded.csv the cross-system summary sample, 348 summaries drawn
                               uniformly at random from the AI-system pool (seed
                               20261006), rule-based labels alongside
  doublecoding/                the double-coding artifacts: the full-sample
                               second coding of all four strata
                               (same_inline_sample_doublecoding.csv,
                               cross_inline_sample_doublecoding.csv,
                               same_summary_sample_doublecoding.csv,
                               cross_summary_sample_doublecoding.csv; each with
                               pass1, pass2, the double-coding wave, and the
                               adjudicated final), the adjudication log with a
                               per-unit reason for all 79 disagreements, and
                               the re-coding batch that refined the codebook for
                               the cross-system inline stratum
                               (inline_cross_v2/final_adjudicated.csv, 302
                               AI-system units, kappa 0.79 on the batch; its
                               instrument is codebooks/review_functions_inline.md),
                               and the RQ3 human-reply role coding over the 316
                               sampled replies (roles_* files; see the README
                               in that directory)
  rq2_summary_sample_coded.csv the hand-coded same-system summary sample (275
                               rows; the label column is `summary_code`); the
                               analyzed cross-system sample is
                               cross_summary_sample_coded.csv (348 rows)
  rq2_sample_shares.json       the per-stratum function shares (regenerate with
                               scripts/56_sample_shares.py)
  rq2_kappa_redrawn_samples.json  the full-sample agreement figures per stratum
                               (regenerate with scripts/57_rq2_agreement.py)
  rq3_roles_pilot.csv          the RQ3 human-reply role sample: the 50-reply
  rq3_roles_rest.csv           pilot and the 266 remaining replies with both
                               passes' labels (316 coded replies in total)
  rq3_kappa_rounds.json        the per-round role-coding agreement: kappa 0.74
                               (pilot), 0.85 (remaining), 0.83 pooled
scripts/
  verify_statistics.py         recomputes every inferential and descriptive
                               statistic quoted in the paper (see below)
  56_sample_shares.py          regenerates rq2_sample_shares.json from the coded samples
  57_rq2_agreement.py          recomputes the full-sample agreement figures
                               (kappa, observed agreement and n per stratum)
                               and checks them against the paper
  62_presence_regression.py    fits the human-presence model behind Table 3
                               (repository-clustered SEs) and checks it against the table
  63_cursor_contrast.py        checks the Cursor same-system register against the
                               External Validity sentence (26 of 26 code-directed)
  58_rq3_roles_pilot_split.py  recomputes the role-coding agreement rounds
                               (pilot 50 / remaining 266 / pooled over 316)
  69_sample_reply_roles_completion.py  draws the nine-reply completion wave
                               (seed 20261001) that brings the role sample to 316
  70_roles_completion_update.py  folds the nine replies into the coding files
                               and prints the role statistics quoted in the paper
  22_build_review_episodes.py  rebuilds the event table from the raw AIDev tables
```

The three codebooks are the instruments behind the coded samples. The paper's
five functions and ten leaves (Section 3.2.2) aggregate the per-form label sets
of the two function codebooks, which differ by written form: the overview and
digest labels and the approval verdict arise on summaries only, and change
acknowledgment on inline comments only. Same-system summaries carry their label
in the column `summary_code`; all other coded files use `code`.

Both cross-system RQ2 samples are drawn uniformly at random from the pools of
the AI reviewing systems identified in Section 2.2 -- the identification and
screening happen once, in RQ1, and RQ2 samples the resulting AI-only pools
directly, with no post-hoc screening: 357 inline comments of the 5,130
(seed 20261005) and 348 summaries of the 3,732 (seed 20261006), the sizes
Cochran's rule gives for the two populations. The RQ3 human-reply role sample
codes 316 replies, the size Cochran's rule gives for the 1,787-reply frame; the
pilot set stays fixed at its first draw (seed 20260930) and nine replies arrived
in a completion wave (seed 20261001, scripts/69-70).

## Reproducing the paper's numbers

```bash
python3 scripts/verify_statistics.py    # all chi-square/Kruskal-Wallis tests,
                                        # effect sizes, descriptives, reply rates,
                                        # merge outcomes
python3 scripts/56_sample_shares.py     # the per-stratum function shares (RQ2, Fig. 7)
python3 scripts/62_presence_regression.py  # the Table 3 model, checked against the table
python3 scripts/63_cursor_contrast.py      # the Cursor same-system register (26 units)
python3 scripts/57_rq2_agreement.py         # the four-stratum double-coding agreement
python3 scripts/58_rq3_roles_pilot_split.py # the role-coding agreement rounds
```

Run these from the package root; they need Python 3 with pandas, numpy and
scipy (scripts/69 additionally needs pyarrow and a local copy of the raw
review-comment table).

`verify_statistics.py` reads only `data/` and prints each statistic next to the
value quoted in the paper. The one input it does not carry is the raw
review-comment text (lengths and reply linkage are precomputed in
`review_comments_final.csv`); to re-derive the event and comment tables from
scratch, fetch the AIDev curated-subset tables (`pr_reviews`,
`pr_review_comments`, `pr_pull`, `pr_review_summary_complete`) and run
`scripts/22_build_review_episodes.py`.

## Source data

All PRs, reviews, and comments come from the AIDev dataset (Li et al., 2025),
curated subset: 33,596 PRs from 2,807 repositories with more than 100 stars.
The coded samples carry only identifiers, labels, and coding metadata; quoted
comment excerpts appear in the paper itself.
