*Instrument for RQ2 (review-function coding; Sections 2.3 and 3.2).*

# Codebook v2 — inline review-comment coding (refined decision rules)

You are annotating **inline code-review comments** posted by AI review bots on
AI-authored pull requests. For each comment, assign **exactly one code** from the
list below. Work unit by unit; read at most the first 4,000 characters of a body
(the dominant intent is always in the head of these comments).

Use EXACTLY these code labels (spelling matters):

1. `Improvement suggestion`
2. `Code-issue feedback`
3. `Workflow/verification report`
4. `Change acknowledgment`
5. `Response to feedback`
6. `Clarification/question`
7. `Agent instruction`
8. `Platform notice`
9. `Explanation`
10. `Other`

## The codes

- **Improvement suggestion** — identifies a problem in the changed code *and*
  supplies a concrete replacement, fix, or specific alternative (a diff, or a
  precise instruction such as "replace X with Y", "extract this into Z",
  "use X instead of Y"). Also covers a pure proposal of a better approach even
  when no defect is claimed.
- **Code-issue feedback** — names a bug, security risk, performance problem,
  correctness risk, or rule/style violation in the changed code, but does **not**
  supply a concrete replacement. Pointing at the affected line and explaining the
  risk is enough.
- **Workflow/verification report** — relays the outcome of a check the *reviewer
  itself ran*: test/build/lint results, pass–fail summaries, coverage numbers,
  "verification inconclusive".
- **Change acknowledgment** — narrates an action that has *already been applied*
  (past tense, a commit reference, "done", "fixed", "updated", "removed"), without
  responding to a previously raised review point.
- **Response to feedback** — reports what was done about a point that a review
  *previously raised* ("as requested", "per your comment", "addressing the
  feedback", "in response to ..."), typically with a commit reference.
- **Clarification/question** — asks the author (human or agent) for information
  needed to proceed ("could you provide the PR number?", "what does X cover?").
- **Agent instruction** — instructs the authoring agent/bot to perform an action,
  typically addressing it by name ("@copilot apply this feedback please").
- **Platform notice** — content about the reviewing *service* rather than the
  change: plan/trial expiry, pricing, quotas, upgrade prompts, bot availability.
- **Explanation** — explains why the code is the way it is (no defect claimed, no
  proposal, no question).
- **Other** — anything with no review substance: brief remarks ("Nice edit",
  "thanks"), pure emoji/greeting/noise, empty or whitespace-only bodies, and
  substantive content that fits none of the codes above.

## Decision procedure

Apply the rules in this order; the **first rule that matches wins**. When several
rules match, code the comment's **dominant intent** (the main point it spends its
length on), and use the rule order only to break ties.

- **R1.** Body is empty/whitespace, or contains no review-relevant content
  (pure emoji, greeting, noise) → `Other`.
- **R2.** The comment is about the reviewing service itself (plan, trial,
  pricing, quota, upgrade, availability) rather than about the change →
  `Platform notice`.
- **R3.** The comment asks a question or requests information →
  `Clarification/question`. A rhetorical question that carries a clear proposal
  ("should this be X instead?") is *not* here; it falls under R7/R8/R9.
- **R4.** The comment instructs the authoring agent/bot to do something,
  typically addressing it by name → `Agent instruction`.
- **R5.** The comment relays results of a check the reviewer itself ran →
  `Workflow/verification report`.
- **R6.** The comment reports an action already applied:
  - it explicitly responds to a previously raised point ("as requested",
    "per your comment", "addressing the feedback") → `Response to feedback`;
  - otherwise → `Change acknowledgment`.
- **R7.** A defect/risk is named **and** a concrete replacement or specific
  alternative is supplied → `Improvement suggestion`.
- **R8.** A defect/risk is named without a concrete replacement →
  `Code-issue feedback`.
- **R9.** A better approach is proposed without claiming a defect →
  `Improvement suggestion`.
- **R10.** Anything else with substantive content → `Other`.

## Boundary rules (these decide the hard cases)

- **B1 — Template headers.** Structured bot comments carry emoji headings such as
  "⚠️ Potential issue" or "🛠️ Refactor suggestion". The heading *signals* the
  category, but the **body decides**: a "Potential issue" comment whose body
  supplies a concrete replacement is `Improvement suggestion` (R7); one that only
  describes the risk is `Code-issue feedback` (R8). A "Refactor suggestion"
  heading with a concrete restructuring proposal is `Improvement suggestion`.
- **B2 — Report vs proposal.** A comment that narrates an *applied* change and
  also proposes something further is coded by its dominant intent; if both parts
  carry real weight, prefer the proposal (`Improvement suggestion`) only when the
  proposal names a concrete change, otherwise `Change acknowledgment`.
- **B3 — Suggestion vs issue.** "Consider doing X" with a specific X is
  `Improvement suggestion`. Flagging "this may break under Y" without saying what
  to do is `Code-issue feedback`.
- **B4 — Style/lint.** A style violation with the fix shown (or trivially
  prescribable, e.g., "add braces after if") is `Improvement suggestion`; the
  same violation merely flagged is `Code-issue feedback`.
- **B5 — Acknowledgment vs response.** The presence of an explicit reference to
  earlier feedback ("as requested") makes it `Response to feedback`; a bare
  report of an applied action is `Change acknowledgment` even if it cites a
  commit.
- **B6 — Verification vs suggestion.** A list of test/build outcomes the reviewer
  produced is `Workflow/verification report` even when it also *recommends*
  running more tests; a recommendation to add tests to the *change* is
  `Improvement suggestion`.

## Worked examples (canonical)

- "style: accentColor should follow theme like other colors instead of being
  hardcoded" → `Improvement suggestion` (defect + concrete alternative).
- "The static variable `oldState` is not thread-safe and will cause incorrect
  behavior when multiple threads call ..." → `Code-issue feedback` (risk named,
  no replacement).
- "Here are the comprehensive test results for single-file builds across all
  platforms ..." → `Workflow/verification report`.
- "Translated the docstring for the Reverse class iterator. Commit a553961" →
  `Change acknowledgment`.
- "Removed the redundant test as requested in commit 9949f56" →
  `Response to feedback`.
- "I need the PR number to add the link. Could you provide the PR number for this
  change?" → `Clarification/question`.
- "Bugbot free trial expires on August 7, 2025" → `Platform notice`.
- "" (empty) → `Other`.

## Mapping to the paper's function taxonomy

The paper aggregates these codes into five review functions (Section 3.2.2):
[A] Descriptive groups `Explanation`; [B] Code-directed groups `Improvement
suggestion`, `Code-issue feedback` and `Workflow/verification report`; [C]
Confirmatory groups `Change acknowledgment`; [D] Interactive/directive groups
`Response to feedback` and `Clarification/question`; [E] Other collects
`Platform notice` and the residue. `Agent instruction` is defined in the
instrument, but no unit in the coded samples carries it, and it is not a leaf
of the paper's taxonomy. Each written form is coded
with the subset of labels its content admits: the overview and digest labels
(A.1, A.2) and the approval verdict (C.2) arise on summaries only, and the
change acknowledgment (C.1) on inline comments only.
