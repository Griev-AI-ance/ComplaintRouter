# Final Presentation Guide — Griev.AI.ance

**When:** Monday, November 30, during class. **Length:** 10 minutes, then 2–3 minutes of questions
(±1 minute is not penalized, so aim for 9:30–10:30). **Slides due:** before class on Nov 30; one
upload per team.

This is the *content* for the deck: what goes on each slide, which figure to use, and what to
say. **The team's working deck is [GrievAIance_Final_Presentation.pptx](GrievAIance_Final_Presentation.pptx)**:
a 16-slide draft (12 main, 4 backup) that follows this plan, with these talking points as its
speaker notes. It's a normal editable PowerPoint, built on a theme with layouts and sections, so
fonts and colors change in one place. The instructor penalizes AI-generated slides, so rework it
before Nov 30: reword the slides and notes in your own words, rearrange layouts the way you'd
present them, and don't run it through slide generators (Copilot/Designer, Gamma, Canva Magic
Design, Google "Help me create"). To edit it together, keep one shared copy in OneDrive
(PowerPoint co-editing) or Google Drive (open with Google Slides) instead of emailing versions. All
figures are in [figures/](figures/); they are plots of our own results, from our notebooks and
[make_slide_figures.py](make_slide_figures.py).

## Grading checklist (from the announcement)

| Points | Requirement | Where it is covered |
|---|---|---|
| 2 | 10 min ± 1, then 2–3 min Q&A | timing column below; rehearse with a timer |
| 3 | Original slides, **high-contrast** (dark text on white) | design rules below |
| 3 | Must include: problem/motivation · methods/algorithms · dataset · results **compared with baselines** · future directions | slides 2, 4, 3, 5–9, 11 |
| 3 | Clarity, delivery, professionalism | rehearse twice end to end; clean handoffs between speakers |
| 2 | Answering questions | Q&A bank at the bottom |

## Design rules

- White background, black or dark-blue text. No dark themes, no text over photos, no light gray text.
- Titles 32 pt or larger, body text 24 pt or larger. Keep it to 3–5 short bullets per slide; the
  details go in what you say.
- One main figure per slide, as large as possible. The figures already have white backgrounds and
  large labels.
- Slide numbers on every slide (helps with questions: "can you go back to slide 6?").
- Write the numbers you say on the slide (0.784, 0.695, 7×) so the audience can follow.
- Put "Data: CFPB Consumer Complaint Database (archived Aug 15, 2026)" in small text on the
  dataset slide.

## Slide-by-slide plan (about 10:05 total)

Speakers are labeled S1/S2/S3. The split gives each person about 3:20; swap the assignments as you
like.

| # | Slide | Time | Speaker | Figure |
|---|---|---|---|---|
| 1 | Title | 0:20 | S1 | — |
| 2 | Problem and motivation | 1:00 | S1 | — (optionally one example complaint) |
| 3 | Dataset | 1:15 | S1 | `product_class_distribution.png` or the funnel as a table |
| 4 | Methods and algorithms | 1:15 | S2 | pipeline diagram you draw (shapes and arrows) |
| 5 | Results: routing vs. baseline | 1:15 | S2 | `slide_routing_vs_baseline.png` |
| 6 | Where the model makes mistakes | 0:50 | S2 | `linear_svm_confusion_matrix.png` |
| 7 | Why sparse beats compressed (SVD) | 0:50 | S3 | `svd_components_vs_macro_f1.png` |
| 8 | Monetary relief | 1:00 | S3 | `slide_relief_lift.png` |
| 9 | What the model learned and when to trust it | 0:50 | S3 | `error_confidence_distribution.png` |
| 10 | Demo | 0:30 | S3 | `demo_screenshot.jpg` |
| 11 | Conclusion and future directions | 1:00 | S1 | — |
| 12 | Questions / thank you | — | all | — |
| — | Backup slides (after "Questions") | — | — | per-class F1 table, t-SNE, MLP loss curve |

### 1. Title (0:20, S1)
**On the slide:** Griev.AI.ance: Routing Consumer Financial Complaints with Machine Learning ·
Raina Bethea, Omar Elkady, Victor Googe · CSC 4850, Fall 2026.

**Say:** Introduce the team in one sentence and the one-line idea: we read a complaint's text and
predict where it should go.

### 2. Problem and motivation (1:00, S1)
**On the slide:**
- The CFPB receives millions of complaints: 2.36M with a narrative from Aug 2023 to Jul 2026
- Each one must reach the team for its product (11 products)
- About 6% end in monetary relief, the costliest outcome
- Task 1: narrative → product (11 classes) · Task 2: narrative → will it get monetary relief?

**Say:** Why misrouting matters (slower resolution, wasted analyst time). We use the text the
consumer wrote, not the form fields. Macro-F1 is our main metric because the classes are
imbalanced and we care about small products too.

### 3. Dataset (1:15, S1)
**On the slide:**
- CFPB Consumer Complaint Database, Aug 2023 – Jul 2026 (one product taxonomy)
- CFPB stopped publishing narratives Aug 14, 2026 → we rebuilt from the Internet Archive copy
- 2.36M narratives → 1.18M unique (template letters: one appears 29,024 times)
- Capped sample: 162,500 complaints, 80/20 split (130,000 train / 32,500 test)

**Figure:** `product_class_distribution.png`, or a small funnel table:
17.1M rows → 2.36M narratives → 1.18M unique → 162,500 sampled.

**Say:** The surprise was duplicates. Almost half the narratives are copy-paste template letters,
so we deduplicated on cleaned text and dropped texts filed under more than one product. Credit
reporting is 53% of the real data, so we capped each product (7:1 instead of 119:1). Placeholders
like XXXX were removed and dollar amounts replaced with one token.

### 4. Methods and algorithms (1:15, S2)
**On the slide (draw this as a simple diagram):**
- Text → TF-IDF (words + bigrams, 100k features, fit on train only)
- Sparse models: Naive Bayes, Complement NB, Logistic Regression, Linear SVM
- Truncated SVD → 300 dense features → k-NN, Random Forest, Gradient Boosting, MLP
- Tuning: 3-fold stratified cross-validation on the training set; test set used once

**Say:** Why two feature types: trees, neighbors and neural nets are slow on 100,000 sparse
dimensions, so they get the SVD (LSA) version. Every model uses the same split and the same
tuning protocol, so the comparison is fair. The relief task uses class-weighted logistic regression
with PR-AUC, because only 5.6% are positive.

### 5. Results: routing vs. baseline (1:15, S2)
**Figure:** `slide_routing_vs_baseline.png`

**On the slide:** Best: **Linear SVM, macro-F1 0.784, accuracy 80.6%** · Mid-term baseline: 0.695.

**Say:** The gray bar is our mid-term naive Bayes baseline (5,000 unigrams). Better features and
tuning alone bring naive Bayes to 0.723; the linear SVM reaches 0.784, a gain of 0.089. The blue
bars (sparse features) beat every orange bar (SVD features), including the MLP at 0.747.
Cross-validation (0.777) matches the test score, so we didn't overfit the tuning.

### 6. Where the model makes mistakes (0:50, S2)
**Figure:** `linear_svm_confusion_matrix.png`

**On the slide:**
- Easiest: student loans (F1 0.92), mortgages (0.92), with distinctive words and servicer names
- Hardest: debt/credit management (0.50), payday loans (0.69)
- Main mix-ups: debt collection ↔ credit reporting, money transfer ↔ checking

**Say:** Many errors are real ambiguity. A debt-collection complaint is often about a collection
account on a credit report, and consumers choose the product themselves.

### 7. Why sparse beats compressed (0:50, S3)
**Figure:** `svd_components_vs_macro_f1.png`

**On the slide:** 100 components keep 88% of full-TF-IDF macro-F1 · 300 keep 94% · 500 keep 96%.

**Say:** This answers why the nonlinear models lost: compressing to 300 dimensions already costs a
linear model about 0.05 macro-F1, and the nonlinear models don't win it back. The rare words that
SVD throws away (company names, specific terms) are exactly what helps classify.

### 8. Monetary relief (1:00, S3)
**Figure:** `slide_relief_lift.png`

**On the slide:** Best: text + product + company, **PR-AUC 0.393 = 7× the 5.6% base rate**,
ROC-AUC 0.915 · Catches 59% of relief cases while flagging 10% of complaints.

**Say:** Accuracy is useless here (always saying "no" is 94% accurate), so we use PR-AUC, where
random is 0.056. The text does most of the work. Company adds the most on top, because company
policy matters: the credit bureaus almost never pay, American Express pays in about 35% of cases.

### 9. What the model learned and when to trust it (0:50, S3)
**Figure:** `error_confidence_distribution.png`

**On the slide:**
- Top features are often company names (Equifax, MOHELA, Zelle, Capital One)
- Confidence > 0.9: 46% of complaints, 94.9% accurate
- Send confidence ≤ 0.7 to a human: 29% of complaints, catches about 65% of errors
- Leakage check: removing near-duplicate templates changes macro-F1 only 0.776 → 0.771

**Say:** Wrong predictions are usually low-confidence, so the system can route the easy ones and
pass the uncertain ones to a person.

### 10. Demo (0:30, S3)
**Figure:** `demo_screenshot.jpg` (Streamlit app). Use the screenshot, not a live demo; a live
demo adds risk and time.

**Say:** You paste a complaint and get the top-3 products, a relief score and the words that drove
the prediction.

### 11. Conclusion and future directions (1:00, S1)
**On the slide:**
- Linear SVM on TF-IDF: 0.784 macro-F1 (baseline 0.695); relief ranked at 7× the base rate
- Simple sparse linear models beat compressed nonlinear ones here
- Future: fine-tune DistilBERT/BERT and compare with few-shot LLMs · test on a time-based split
  (drift, new template campaigns) · predict sub-product and issue (hierarchical) · mask company
  names to test robustness · calibrated confidence for human review

**Say:** Limitations in one breath: the sample is more balanced than real traffic, we used a random
split rather than a time-based one, and the model leans on company names. Each future direction
addresses one of these.

### 12. Questions / thank you
Keep the backup slides after this one: the per-class F1 table (report Table III), the t-SNE map,
and the MLP loss curve.

## Rehearsal plan

1. **By Nov 27:** each speaker drafts their slides in the shared deck; one person unifies fonts and
   colors.
2. **Nov 28 or 29:** two full run-throughs with a timer (target 9:30–10:30). Cut words, not slides,
   if you run long. Practice the handoffs ("Now Victor will show our results").
3. **Before class Nov 30:** export to PDF as a backup, submit the slides (one upload for the team),
   and bring the file on a USB drive.

## Q&A bank (likely questions, short answers)

- **Why macro-F1 and not accuracy?** Classes are imbalanced; macro-F1 weights all 11 products
  equally, so small products like prepaid cards count as much as credit reporting.
- **Why did the linear SVM beat the neural network?** The MLP only saw 300 SVD features, which
  already lose about 0.05 macro-F1 for a linear model. Text has many sparse, informative features,
  which suits linear models (Joachims, 1998).
- **Did you try BERT/transformers?** It was our stretch goal; it needs a GPU. It's our first
  future direction.
- **How do you know you didn't overfit?** Hyperparameters were chosen by 3-fold CV on the training
  set only; the test set was used once. CV macro-F1 (0.777) matches test (0.784).
- **What about duplicate template letters leaking into the test set?** Exact duplicates were
  removed. 5.6% of test complaints share their first 200 characters with a training complaint;
  removing them changes macro-F1 only from 0.776 to 0.771.
- **Is the test set realistic?** It's capped per product, so it's more balanced than real traffic
  (53% credit reporting). Accuracy on real traffic would differ; we say this in the report.
- **Why is debt/credit management so hard?** Smallest class (5,000), and its complaints read like
  debt-collection or credit-report complaints: 19% are predicted as debt collection.
- **Isn't relying on company names cheating?** The company is in the text and is a real clue (e.g.,
  MOHELA only services student loans). The risk is new companies; testing with names masked is
  future work.
- **How does your relief result compare with Wang et al.?** They report ROC-AUC 0.78 on a
  time-based split; ours is 0.915 on a random split of a different sample, so the numbers are not
  directly comparable.
- **Why truncated SVD instead of PCA?** TF-IDF is a huge sparse matrix; truncated SVD works
  directly on it without centering (which would make it dense). On text it's called LSA.
- **What did k-means find?** Themes, not just products: issue clusters (unauthorized
  transactions, merchant disputes), template campaigns (Cash App, Zelle), even a Wells Fargo
  cluster. ARI 0.19 against products. Relief rates differ a lot by theme (gift cards 33%).
- **How would this be used in practice?** Auto-route high-confidence complaints (>0.9 is 95%
  accurate) and send low-confidence ones (≤0.7) to a person.
- **Where did the data come from if the CFPB removed narratives?** The official CFPB bulk file as
  archived by the Internet Archive on Aug 15, 2026, the day after the removal.
