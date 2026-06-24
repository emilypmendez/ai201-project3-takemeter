# TakeMeter — planning.md
**Project:** Fine-tuned discourse quality classifier for r/MacOS  
**Author:** Emily  
**Last updated:** 2026-06-22

---

## 1. Community

**Chosen community:** r/MacOS — the primary Reddit home for macOS users, ranging from developers and power users to people who just bought their first Mac.

**Why this community?** r/MacOS is a good classification target for three reasons.

First, the discourse is genuinely varied. In a single day's feed you'll find a well-sourced post comparing window management across macOS versions, a screenshot with zero context, a heartfelt rant about icon design, and a question asking which PDF reader people use. That range means the labels have real work to do — this isn't a community where every post sounds roughly the same.

Second, there's a meaningful quality gap that the community itself cares about. Long-time members frequently note the difference between "someone with a real complaint they've actually thought about" and "someone who just wants to vent." That tacit distinction maps directly onto the classifier's goal.

Third, the content is text-primary and short enough to annotate efficiently. Most posts are a title plus 0–3 sentences of body text, which keeps per-example annotation time low and reduces the risk of annotation fatigue skewing the labels.

---

## 2. Labels

Four labels. Each is defined so that two independent annotators, given the definition, would agree on the same post at least 80% of the time.

---

### `grounded`
**Definition:** The post makes a claim that is specific and verifiable — naming a macOS version, a particular tool or setting, a reproducible behavior, or a concrete before/after comparison — and uses that specificity to support its point.

The key test: could the claim in principle be checked by a third party? If yes, and the post uses that checkable detail to make its point, it is `grounded`.

**Example posts:**
1. *"Since Sonoma 14.4, the stage manager sidebar no longer preserves window order after sleep/wake — confirmed on two M2 machines, not a clean install issue."* — names a specific version and a reproducible bug on specific hardware.
2. *"I've been using Raycast instead of Spotlight for 18 months. Search latency is consistently under 80ms vs 200–400ms for Spotlight on the same file index."* — named tools, a time range, specific measurements.

---

### `opinionated`
**Definition:** The post expresses a confident opinion or preference without specific, verifiable support. The claim may be true or reasonable, but the post asserts it rather than demonstrating it. Generalizations, taste preferences, and bold takes all qualify.

The key test: if you stripped the opinion framing, would anything checkable remain? If no — if what's left is pure assertion — it is `opinionated`.

**Example posts:**
1. *"Icons from the 2000s were masterpieces. Everything since Yosemite has been a downgrade."* — strong aesthetic claim, no comparative evidence, no version-specific argument.
2. *"The Apps app is one of the worst things Apple has ever added to macOS."* — ungrounded superlative. "One of the worst" is asserted with no reference class or comparison.

---

### `reactive`
**Definition:** The post's primary move is to solicit opinions, experiences, or recommendations from the community. The poster does not take a substantive position; the post's value depends on what others say in response.

The key test: does the post make a complete claim without the replies? If no — if it's fundamentally a question or prompt — it is `reactive`.

**Example posts:**
1. *"What's one thing you wish macOS did better?"* — an explicit open-ended prompt. The poster has no stated position.
2. *"What menu bar apps do you actually keep running? Looking to trim mine down."* — a request for recommendations with no opinion attached.

---

### `noise`
**Definition:** The post has no substantive content — it makes no claim, poses no real question, and contributes nothing a reader could engage with. This includes context-free screenshots, one-word reactions, vague "anyone else?" posts without elaboration, and posts so generic they could apply to any software.

The key test: is there a proposition, question, or argument that another person could respond to meaningfully? If no, it is `noise`.

**Example posts:**
1. *"My Mac just did this 😭 [screenshot with no explanation]"* — no question, no claim, no context.
2. *"Anyone else feel like macOS has gotten worse?"* — too vague to be `opinionated` (no specific claim) and too vague to be `reactive` (no specific question worth answering).

---

## 3. Hard Edge Cases

### Primary boundary: `grounded` vs `opinionated`

This is the boundary that will cause the most annotation errors.

**The ambiguous post type:** A post that names a specific macOS version or tool, but uses that specificity as context rather than as evidence.

Example: *"macOS Ventura ruined my workflow."*

This names a version — which looks like `grounded` — but "ruined my workflow" is ungrounded. The version is decorative context, not evidence. There is no verifiable claim here.

A slightly different version: *"macOS Ventura broke my window tiling shortcuts — Command-Option-Left no longer works in full-screen mode."* — now the named version is doing work. The claim is reproducible.

**Decision rule for this boundary:** Ask: does the specific detail (version, tool, setting) *support* the claim, or merely *contextualize* it? If the specificity could be removed without weakening the argument, it is decorative and the post is `opinionated`. If the specificity is the argument — removing it would make the post unprovable — it is `grounded`.

A one-stat or one-detail post (like naming a version without saying what changed) defaults to `opinionated` unless the detail directly enables verification.

---

### Secondary boundary: `reactive` vs `opinionated`

**The ambiguous post type:** A post that includes a personal opinion as a prompt-setter before asking others.

Example: *"What's your most-hated macOS feature? Mine is Stage Manager — it's completely unusable for multi-monitor setups."*

This contains both an opinion ("Stage Manager is unusable") and a solicitation ("what's yours?").

**Decision rule for this boundary:** What is the post's primary move? If the post is structured to collect responses — evidenced by an explicit question, "I'll start" framing, or a call for community replies — label it `reactive`, even if a personal opinion appears as a prompt. If the question is rhetorical and the post stands alone as a complete argument, label it `opinionated`. A good heuristic: would the post be satisfying to read if no one ever replied? If yes → `opinionated`. If it feels incomplete without replies → `reactive`.

---

### Tertiary boundary: `noise` vs `reactive`

**The ambiguous post type:** *"Anyone else having issues with macOS updates lately?"*

This is technically a question but asks for nothing specific.

**Decision rule:** If the question is so vague that any answer would be equally valid — "yes" and "no" are both complete responses — label it `noise`. A `reactive` post asks something that a community member could actually answer substantively.

---

## 4. Data Collection Plan

### Sources

Primary source: Reddit r/MacOS, collected via the Reddit API or manual browsing, filtered to posts from the last 12 months. Use the top/hot/new feeds to sample across popularity levels — top posts are more likely to be `grounded` or `opinionated`, new posts are more likely to contain `noise`.

Secondary source: The five seed posts identified in Milestone 1 are included in the annotation set and serve as calibration anchors for the label definitions.

### Target counts

| Label | Target count | Rationale |
|---|---|---|
| `grounded` | 55 | Expect this to be naturally underrepresented; r/MacOS skews toward strong opinions |
| `opinionated` | 65 | Likely the plurality class |
| `reactive` | 50 | Common but tends to cluster (AMA-style threads) |
| `noise` | 30 | Genuinely rare once you filter for posts with any text |
| **Total** | **200** | — |

### If a label is underrepresented after 150 examples

If `grounded` is below 40 examples: search specifically for posts comparing macOS versions, bug reports with version numbers, or posts with hardware specifics. These are the reliable `grounded` sources.

If `noise` is below 20: search the new feed, not top/hot, and look for posts in the first hour after posting (high noise-to-signal ratio before community curation kicks in).

If `opinionated` is above 90 after 150 examples: stop collecting indiscriminately from hot/top and switch to stratified sampling — actively seek examples from underrepresented classes before returning to general collection.

### Annotation protocol

- Annotate all 200 examples personally before any AI pre-labeling review.
- Record each example as: `post_id`, `post_title`, `post_body_excerpt` (first 300 chars), `label`, `confidence` (high/medium/low), `notes`.
- Flag medium- and low-confidence examples for a second-pass review after completing the full 200.
- Do not annotate more than 50 examples in a single sitting to avoid drift in how the rules are applied.

---

## 5. Evaluation Metrics

**The primary metric is macro F1**, not accuracy.

Accuracy is insufficient here for a clear reason: the class distribution is unbalanced. A classifier that predicts `opinionated` for every post would achieve roughly 33% accuracy (if `opinionated` is the plurality class at ~65/200) and would be completely useless. Macro F1 averages F1 across all four labels equally, so it penalizes the model for ignoring any one class regardless of size.

**Per-class F1** is reported alongside macro F1. The reason: `grounded` is the most important class for downstream use (identifying substantive posts), and `noise` is the most important class to get right in moderation contexts. Knowing that the model has high macro F1 but poor F1 on `grounded` specifically would be a deployment-blocking finding.

**Confusion matrix** is a required artifact. The most informative error patterns are:
- `opinionated` predicted as `grounded` (false elevation — the model thinks vague claims are substantive)
- `reactive` predicted as `noise` (false dismissal — the model misses real questions)
- `grounded` predicted as `opinionated` (false demotion — the model misses specific evidence)

These error types have different costs depending on use case, so the confusion matrix is more decision-relevant than any single scalar metric.

**Inter-annotator agreement** will be computed on a 20-example held-out subset that is re-annotated after a one-week gap. Cohen's kappa ≥ 0.75 is the target — this establishes that the labels are stable enough to be worth training on.

---

## 6. Definition of Success

### Minimum bar for a "useful" classifier

A classifier is useful for a real community tool if it can reliably separate the top and bottom of the quality distribution. Specifically:

- **Macro F1 ≥ 0.72** on the held-out test set (25% of data, stratified).
- **Per-class F1 ≥ 0.65 for every label**, including `grounded` and `noise` — no class is allowed to drag below this threshold even if macro F1 looks healthy.
- **`grounded` precision ≥ 0.70** — if the model calls a post grounded, it should be right 70% of the time, because false elevation (surfacing bad posts as high-quality) is the more damaging error in a recommendation context.

### "Good enough for deployment"

A macro F1 of 0.72 and no per-class F1 below 0.65 would be good enough for a soft deployment: surfacing `grounded` posts in a quality digest, or flagging `noise` for moderator review, with human oversight in the loop. Automated moderation (removing posts based on model output alone) would require macro F1 ≥ 0.82 and per-class F1 ≥ 0.78 — that is a stretch goal, not the primary target.

### What would constitute failure

- Macro F1 below 0.60 means the model has learned less than a simple heuristic (e.g., "if post contains a question mark, label `reactive`").
- `grounded` F1 below 0.55 means the model cannot detect the most important class — the classifier is not solving the intended problem.
- Inter-annotator kappa below 0.65 means the labels themselves are unreliable, and the model cannot learn a consistent signal regardless of how it performs by F1.

---

## 7. AI Tool Plan

### 7.1 Label stress-testing (before annotation)

**Goal:** Find posts that sit at the boundary between two labels to expose weaknesses in the definitions before the annotation phase locks them in.

**Process:** Feed the four label definitions and the three decision rules (§3) to Claude and ask it to generate 8–10 synthetic posts that are genuinely difficult to classify — specifically targeting the `grounded`/`opinionated` boundary and the `reactive`/`opinionated` boundary.

If any generated post cannot be cleanly classified using the decision rules, that is a signal to tighten the definition — not a signal to discard the post. The goal is to break the taxonomy before it encounters 200 real examples.

**Timing:** This step happens before annotation begins. Any definition changes that result from this stress-test are made to this planning document (with a dated revision note) before proceeding.

**Disclosure:** Synthetic posts generated during stress-testing will not be included in the training or evaluation set.

---

### 7.2 Annotation assistance

**Decision:** Use LLM pre-labeling for a secondary review pass, not for the primary annotation.

**Process:**
1. Annotate all 200 examples personally first, recording my label and confidence rating.
2. After the first pass is complete, submit all 200 examples to Claude (with the label definitions in the system prompt) and request a pre-label for each.
3. Compare Claude's labels to my own. For examples where they disagree, re-read the post with the decision rules in hand and record a final label. Do not default to Claude's label — disagreement is a flag for careful human review, not a tiebreaker.
4. Track which examples had a disagreement in the `notes` column. Report the agreement rate between my initial labels and Claude's labels as an additional calibration metric in the final writeup.

**Why this order matters:** If Claude pre-labels first, my subsequent annotations are anchored to its outputs (anchoring bias). Annotating first preserves the independence of my judgments.

**Disclosure:** All examples where AI pre-labeling was part of the review process will be disclosed in the AI Usage section of the final report. The training set will be labeled by human judgment; AI labels are used only as a disagreement-detection tool.

---

### 7.3 Failure analysis

**Goal:** After evaluation, identify systematic error patterns in the model's wrong predictions before writing up the results.

**Process:**
1. Extract all test examples where the model's prediction does not match the ground-truth label.
2. Submit the full list of wrong predictions — post text, true label, predicted label — to Claude with the following prompt: *"Here are the posts this classifier got wrong. Identify any systematic patterns in the errors: are there specific phrasings, post structures, or linguistic features that consistently lead to misclassification? Group the errors into patterns and describe each pattern in one sentence."*
3. Review Claude's pattern analysis critically. For each proposed pattern, check it manually against the error list: does it actually hold across multiple examples, or is it an artifact of a small sample? Only patterns confirmed by manual review are reported in the writeup.
4. Use confirmed patterns to write the "where it falls apart" section of the evaluation — this is the most valuable output of the failure analysis.

**What to look for specifically:**
- Posts where specificity language ("I've tried X, Y, Z") misleads the model into predicting `grounded` when the claim is still unverifiable.
- Posts where a question mark at the end of an otherwise `opinionated` post gets classified as `reactive`.
- Very short posts (title only, no body) that get predicted as `noise` when they're actually `opinionated`.

**Verification requirement:** Every pattern surfaced by the AI tool must be verified against the raw error list before it appears in the final writeup. AI-generated pattern descriptions that cannot be confirmed manually are discarded.

---

## Appendix: Revision log

| Date | Change |
|---|---|
| 2026-06-22 | Initial draft |
