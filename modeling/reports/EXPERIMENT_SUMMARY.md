# Do the new vocab bin features help predict text difficulty?

Updated 2026-10-09 (final English-borrowing tagging). Source and origin are never used as features. Full tables for every model: `experiment_train_native.md`, `experiment_train_all.md`.

## 1. In short
- We replaced only the 11 old vocab columns by the new vocab bin features and kept everything else.
- **The new bins add little** on top of the 391 other features (MAE differs by 0.013 at most when trained on native Finnish texts).
- **They help more when translated texts are in the training data:** MAE 0.475 with the lemma + stem bins (0.476 with the lemma bins) vs 0.493 with the old bins vs 0.519 without vocab.
- **The data is easy to separate with shortcuts:** four length features alone reach 55.7% accuracy, close to the full models (54% to 58%).
- **Every model favours the common labels** (3.5 and 5.5) and is weak on 1.5, 3.0 and 4.0.

## 2. What was compared

| feature set | in short | columns |
|---|---|---:|
| `no_vocab` | the original features without the old vocab columns | 391 |
| `old_vocab_bins` | no_vocab + the 11 old vocab columns (baseline) | 402 |
| `new_lemma_bins` | no_vocab + the lemma bin features | 403 |
| `new_stem_bins` | no_vocab + the stem bin features | 404 |
| `new_lemma_stem_bins` | no_vocab + both | 416 |
| `surface` | text length and word length only (a control for length shortcuts) | 4 |
| dummy | one constant for every text (the most common or the median training label); the floor | 0 |

## 3. How it was tested
- **Models:** ridge regression; gradient boosting (shown below)
- **Training sets:** real-Finnish rows of train (2,332), or all train rows (8,293, 72% translated from Russian)
- **Test:** 865 real-Finnish texts
- **Metrics**
  - MAE: mean absolute error in label units (labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)
  - accuracy: the prediction rounded to the nearest half step is exactly the label
  - accuracy ±1 step: within 0.5 of the label
  - balanced accuracy: the mean of the per-label accuracies, so every label counts equally
- Single run per setting, no confidence intervals

## 4. Main result: test set, gradient boosting

Trained on native rows (2,332):

| feature set | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---:|---:|---:|---:|
| no_vocab | 0.386 | 56.1% | 78.0% | 43.8% |
| old_vocab_bins | 0.374 | 58.4% | 77.0% | 45.6% |
| new_lemma_bins | 0.387 | 54.1% | 76.9% | 41.8% |
| new_stem_bins | 0.384 | 56.8% | 77.7% | 46.2% |
| new_lemma_stem_bins | 0.380 | 57.2% | 77.1% | 47.2% |
| surface | 0.433 | 55.7% | 72.8% | 40.7% |
| dummy: most common label (5.5) | 1.284 | 39.3% | 51.3% | 12.5% |
| dummy: median label (5) | 1.229 | 6.8% | 46.1% | 12.5% |

Trained on all train rows (8,293):

| feature set | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---:|---:|---:|---:|
| no_vocab | 0.519 | 38.2% | 60.3% | 31.9% |
| old_vocab_bins | 0.493 | 41.4% | 63.1% | 34.5% |
| new_lemma_bins | 0.476 | 42.7% | 65.5% | 33.5% |
| new_stem_bins | 0.506 | 38.0% | 63.5% | 30.2% |
| new_lemma_stem_bins | 0.475 | 41.7% | 66.6% | 31.9% |
| surface | 0.529 | 41.2% | 59.2% | 34.2% |
| dummy: most common label (3) | 1.605 | 6.9% | 28.1% | 12.5% |
| dummy: median label (3.5) | 1.325 | 21.2% | 33.6% | 12.5% |

## 5. Bias: MAE per label (test, gradient boosting, trained on native rows)

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.06 | 0.52 | 0.58 | 0.25 | 0.62 | 0.38 | 0.31 | 0.28 |
| old_vocab_bins | 1.05 | 0.52 | 0.57 | 0.23 | 0.57 | 0.37 | 0.30 | 0.28 |
| new_lemma_bins | 1.06 | 0.53 | 0.55 | 0.25 | 0.58 | 0.34 | 0.32 | 0.31 |
| new_stem_bins | 1.01 | 0.52 | 0.56 | 0.25 | 0.59 | 0.37 | 0.31 | 0.27 |
| new_lemma_stem_bins | 1.08 | 0.52 | 0.55 | 0.26 | 0.55 | 0.32 | 0.31 | 0.26 |
| surface | 1.30 | 0.58 | 0.79 | 0.22 | 0.82 | 0.51 | 0.32 | 0.23 |

- Labels 3.5 and 5.5 (the most common) have a MAE of 0.2 to 0.3, half a step.
- Label 1.5 has a MAE of about 1.0 (two steps); 3.0 and 4.0 have 0.5 to 0.6.
- Accuracy (54% to 58%) is higher than balanced accuracy (42% to 47%): the overall figure flatters the models.

## 6. What to conclude
- The vocab bins, old or new, add little to the other 391 features: trained on native rows, the vocab rows differ by 0.013 MAE at most.
- Lemma bins help more than stem bins when the model is trained on all rows (MAE 0.476 vs 0.506). On native rows, lemma + stem bins together have the best balanced accuracy (47.2% vs 45.6% for the old bins).
- Because of the shortcuts, a good score does not prove the model measures difficulty.
- The stored `predicted_score` of the old model (test MAE 0.18) is far better than anything here, so it was probably not a held-out prediction.

## 7. Caveats
- One run per setting; differences of 0.01 to 0.02 MAE are within noise
- Small label groups on test (n = 32 to 60 for 1.5, 3.0, 4.0, 5.0, 6.0)
- Train and valid are mostly translated text; in the real data the label is almost a function of the source
- No document ids, so near-duplicate texts across splits cannot be ruled out
- Lemmas and stems come from Voikko without sentence context

## 8. Next steps
1. Bootstrap confidence intervals for the differences between feature sets
2. Evaluate within the `FI` source only (five labels, so source cannot explain the label)
3. Leave one source out at a time
4. Test the other new vocab features (word length, compounds, derivation, lexical diversity) as a separate set

## Appendix: other results
Test MAE, ridge regression:

| feature set | trained on native | trained on all |
|---|---:|---:|
| no_vocab | 0.681 | 0.964 |
| old_vocab_bins | 0.659 | 0.946 |
| new_lemma_bins | 0.657 | 0.926 |
| new_stem_bins | 0.657 | 0.946 |
| new_lemma_stem_bins | 0.647 | 0.907 |
| surface | 0.744 | 0.914 |

Valid (native rows only, 263 texts), gradient boosting trained on native rows, MAE:

| no_vocab | old_vocab_bins | new_lemma_bins | new_stem_bins | new_lemma_stem_bins | surface |
|---:|---:|---:|---:|---:|---:|
| 0.377 | 0.380 | 0.390 | 0.391 | 0.394 | 0.431 |

Per-label MAE when trained on all train rows, and accuracy per label, are in `experiment_train_all.md` and `experiment_train_native.md`.

## Reproduce
```
cd text-difficulty
.venv/bin/python vocab-diff/build_features.py    # new features -> outputs/
.venv/bin/python modeling/run_experiment.py --train train_native
.venv/bin/python modeling/run_experiment.py --train train_all
```
