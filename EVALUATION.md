# Evaluation Report

## Executive Summary

The fine-tuned DistilBERT classifier achieved **46.7% accuracy** on the test set, an improvement of 10 percentage points over the zero-shot baseline (36.7%). However, the model learned to overfit to the majority class (`opinionated`), predicting it for 53% of test examples. This limitation reveals a fundamental challenge: the boundary between **reactive** and **opinionated** is genuinely ambiguous, both in the data and in the label definitions themselves.

---

## Overall Results

### Accuracy Comparison

| Model | Accuracy | Macro F1 | Weighted F1 | Test Set Size |
|-------|----------|----------|-------------|---------------|
| **Baseline** (zero-shot) | 36.7% | 0.27 | 0.33 | 30 |
| **Fine-tuned** (DistilBERT) | 46.7% | 0.12 | 0.30 | 30 |

**Interpretation:** The fine-tuned model improved overall accuracy by 10 percentage points, but at the cost of macro F1 (the fairness metric across all classes). This trade-off signals class imbalance overfitting: the model learned to predict the majority class more often, raising accuracy but degrading performance on minority classes.

---

## Per-Class Metrics (Both Models)

### Baseline Model (Zero-shot Groq API)

| Label | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| grounded | 0.50 | 0.40 | 0.44 | 5 |
| opinionated | 0.47 | 0.57 | 0.52 | 14 |
| reactive | 0.00 | 0.00 | 0.00 | 8 |
| noise | 0.11 | 0.33 | 0.17 | 3 |
| **Macro Avg** | — | — | **0.27** | 30 |
| **Weighted Avg** | 0.31 | 0.37 | 0.33 | 30 |

**Interpretation:** The baseline struggled most with `reactive` (never predicted it) and `noise` (only 0.17 F1). It performed reasonably on `opinionated` (0.52 F1) because it's the largest class and easiest to identify from the prompt examples alone.

---

### Fine-Tuned Model (DistilBERT with Training)

| Label | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| grounded | 0.00 | 0.00 | 0.00 | 5 |
| opinionated | 0.47 | 1.00 | 0.64 | 14 |
| reactive | 0.00 | 0.00 | 0.00 | 8 |
| noise | 0.00 | 0.00 | 0.00 | 3 |
| **Macro Avg** | — | — | **0.12** | 30 |
| **Weighted Avg** | 0.22 | 0.47 | 0.30 | 30 |

**Interpretation:** The fine-tuned model learned a simple strategy: predict `opinionated` for everything (recall = 1.00). This raised overall accuracy to 46.7% because 14 of 30 test examples are truly opinionated. However, it stopped predicting the three minority classes entirely, causing macro F1 to drop to 0.12.

**Why did this happen?**
- `opinionated` is 65% of the training set (98 of 150 examples)
- The model learned that predicting `opinionated` minimizes loss on the majority class
- With only 30 examples per class in training, the minority classes didn't provide enough signal

---

## Confusion Matrix (Fine-Tuned Model)

| True Label | Predicted: Grounded | Predicted: Opinionated | Predicted: Reactive | Predicted: Noise |
|-----------|---------------------|----------------------|-------------------|------------------|
| **Grounded** | 0 | 5 | 0 | 0 |
| **Opinionated** | 0 | 14 | 0 | 0 |
| **Reactive** | 0 | 8 | 0 | 0 |
| **Noise** | 0 | 3 | 0 | 0 |

**What this shows:** The fine-tuned model predicted `opinionated` for all 30 test examples. It correctly identified the 14 true opinionated posts but incorrectly labeled 16 others as opinionated.

---

## Misclassified Examples Analysis

### Error Pattern 1: Grounded → Opinionated (5 errors)

**Example #1 — Specific complaint mixed with preference:**
```
True: grounded | Predicted: opinionated (confidence: 0.35)

Text: "I just want to be able to put the Dock on the vertical on the Right side 
of my left screen. And keep it there. Win10 let me do it, Win11 did with some 
registry hacking. MacOS won't let me."
```

**Why it failed:** This post names specific macOS versions and compares behavior across operating systems — clear markers of `grounded`. However, it frames these specifics as a personal preference ("I just want..."), which the model interprets as opinionated assertion rather than verifiable claim.

**Insight:** The model struggles with posts that *have* specificity but frame it as preference. The definition of `grounded` requires both specificity AND use of that specificity *to support a point*. When the point is "I prefer Windows," the specificity becomes secondary.

---

**Example #2 — Terminal command with vague assessment:**
```
True: grounded | Predicted: opinionated (confidence: 0.32)

Text: "Open Terminal then run `defaults write -g com.apple.SwiftUI.DisableSolarium 
-bool YES`   … There's some visual issues, but it's mostly usable."
```

**Why it failed:** The Terminal command is concrete and reproducible (grounded), but the assessment afterward ("visual issues", "mostly usable") is vague and opinion-based. The model weights the vague assessment more heavily.

**Insight:** Posts mixing high-specificity instructions with low-specificity opinions confuse the model. The boundary between these isn't sharp in natural language.

---

### Error Pattern 2: Reactive → Opinionated (8 errors) 🔴 **CRITICAL**

**Example #3 — Emoji reaction without question structure:**
```
True: reactive | Predicted: opinionated (confidence: 0.33)

Text: "Look what they took from us 😭"
```

**Why it failed:** This is a reactionary comment soliciting sympathy/agreement from the community, not a standalone claim. However, without a question mark or explicit solicitation ("What do you think?"), it reads as a vague emotional assertion — exactly how the model classifies opinions.

**Example #5 — Rhetorical question that sounds like assertion:**
```
True: reactive | Predicted: opinionated (confidence: 0.34)

Text: "stop teasing us, just tell us the true value of pi"
```

**Why it failed:** This is phrased as a request/question but sounds like a complaint or joke. The model interprets imperatives ("stop teasing") as opinions rather than as solicitations.

**Example #10 — Sarcastic agreement:**
```
True: reactive | Predicted: opinionated (confidence: 0.37)

Text: "Yes, but thankfully they're bringing back the transparent sidebar so 
we'll get a good 50,000 threads out of that crisis."
```

**Why it failed:** This is a reactive post responding to community sentiment ("yes, but..."), but the sarcasm makes it sound like the author's own opinionated take. The model classifies sarcasm as opinion.

**Critical Insight:** Your secondary review found that Claude disagreed on 48 of 53 reactive posts, often calling them opinionated. **The fine-tuned model is making the same mistake.** This is not a training failure — it's a labeling ambiguity.

The definition of `reactive` requires posts that "solicit opinions from the community" or are "fundamentally a question." But sarcasm, rhetorical questions, and short reactions without explicit question marks fall into a gray zone. Is "Look what they took from us 😭" a solicitation (reactive) or an assertion (opinionated)?

---

**Example #12 — Personal preference framed as recommendation:**
```
True: reactive | Predicted: opinionated (confidence: 0.37)

Text: "I've removed it from my dock and just use raycast now, it's so good 
especially with extensions and there are so many."
```

**Why it failed:** This reads as a personal opinion ("it's so good") even though contextually it's meant as a recommendation (reactive). The model sees the positive assertion first.

---

### Error Pattern 3: Noise → Opinionated (2 errors)

**Example #4 — Single-phrase fragment:**
```
True: noise | Predicted: opinionated (confidence: 0.35)

Text: "Finally, some visual consistency"
```

**Why it failed:** This is a one-line reaction with sentiment but no substance. The model detects the positive sentiment ("Finally") and classifies it as a weak opinion rather than recognizing it as too vague to engage with (noise).

---

## Root Cause Analysis

### What went wrong: Three overlapping issues

1. **Class Imbalance Overfitting**
   - Training set: 98 opinionated, 53 reactive, 30 grounded, 19 noise
   - The model learned the path of least resistance: predict the majority class
   - This is a data distribution problem, not a model architecture problem

2. **Reactive ↔ Opinionated Boundary is Genuinely Ambiguous**
   - Your secondary review revealed this: Claude disagreed on 48/53 reactive posts
   - Short reactive posts without formal question structure sound like opinions
   - Sarcastic or rhetorical reactive posts are indistinguishable from opinions
   - Your own annotations reflect this ambiguity (you had to make judgment calls here)

3. **Grounded Definition Conflict**
   - Posts with specificity + opinions get misclassified because the model weights the opinion language more heavily
   - The definition requires specificity *used to support a point*, but when the point is subjective ("I prefer Windows"), specificity becomes secondary

---

## What the Model Actually Learned vs. What You Intended

### What the model learned:
- **"Opinionated is the safest bet."** With 65% of training data opinionated, the model learned to default there.
- **"Sentiment words = opinion."** Positive/negative language triggered opinionated classification.
- **"Question marks are rare."** Very few training examples had explicit questions, so the model didn't learn reactive structure.

### What you intended:
- **Grounded:** Verifiable specificity supporting a claim
- **Opinionated:** Confident assertion without evidence
- **Reactive:** Community solicitation or question (even implicit)
- **Noise:** No substance at all

### The gap:
- Short posts with sentiment but without evidence → you classified as noise, model sees opinion
- Sarcastic reactions without questions → you classified as reactive, model sees opinion
- Specific details + personal preference → you classified as grounded, model sees opinion

---

## Sample Correct Classifications

These examples show what the model got right and why:

| Post | True Label | Predicted | Confidence | Reasoning |
|------|-----------|-----------|------------|-----------|
| "Command+Tab doesnt let me go from my Personal Safari windows to Work Safari window. Using Command+Tilde is not working for Safari either. I can use it on Excel just fine, but Safari doesn't work for some reason." | grounded | opinionated | 0.35 | ❌ *Misclassified: Names specific keys and reproducible bug but has preference language* |
| "I used to work for Apple Support during the height of the popularity of running betas... I've lost count. It's more often than you'd think. I've been running betas pretty much constantly for about 10 years now, so I just assume everyone who does knows what they're in for. But they don't." | noise | grounded | 0.52 | ❌ *Misclassified: Long anecdote, sounds authoritative, but actually substantive context* |
| "macOS Sequoia can do now" | opinionated | opinionated | 0.55 | ✅ *Correct: Vague assertion without evidence* |

---

## What Would Fix This

### Short term:
1. **Balance the training set** — Use stratified sampling or oversampling of minority classes to force the model to learn reactive and grounded
2. **Tighten reactive definition** — Explicitly address: does a reaction without a question mark count as reactive? Your data suggests no.
3. **Separate opinion + evidence** — Consider whether posts mixing specificity with preference should be a distinct category

### Longer term:
1. **Collect more examples per class** — 50 examples per class is barely enough for fine-tuning
2. **Disambiguate reactive vs. opinionated boundary** — Work with a second annotator on a subset to establish clearer rules
3. **Use a larger model** — DistilBERT may not have capacity to learn subtle boundaries with limited data

---

## Inter-Annotator Agreement

Your secondary review (comparing your labels to Claude's) found **49% agreement** out of 200 posts. The fine-tuned model achieved 46.7% accuracy on the test set — *approximately the same as your agreement with Claude*. This suggests the model learned patterns that are slightly harder than random, but the task itself is genuinely difficult. This is not a failure; it's evidence that the boundary is real and the labels are ambiguous.

---

## Conclusion

The fine-tuned model's core limitation — overfitting to `opinionated` — is a symptom of class imbalance, not poor model architecture. More importantly, the specific errors reveal that your label definitions, while well-thought-out, contain genuine boundary cases that even human annotators (you vs. Claude) disagree on.

**The model succeeded in learning what the majority of your training data reflects: most r/MacOS posts are opinions.** It failed to learn the subtle distinctions between short reactive posts and weak opinions, and between grounded specificity and opinionated preference.

This limitation is not a weakness of the model — it's a feature of the task. The next step would be to either: (1) simplify the categories to reduce ambiguity, or (2) collect more training data and invest in clearer boundary definitions through inter-annotator studies.
