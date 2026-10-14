# Experiment: train on train_native (2,332 rows)

- Source and origin are not features. Test = real Finnish only; valid (native) = the real-Finnish rows of valid.
- **MAE**: mean absolute error in label units (the labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)
- **accuracy**: share of texts whose prediction, rounded to the nearest half step, is exactly the label
- **accuracy ±1 step**: share within 0.5 of the label
- **balanced accuracy**: mean of the per-label accuracies; every label counts equally, so favouring the common labels is punished
- dummy models predict one constant for every text, taken from the training labels: most common label (5.5); median label (5)
  They are the floor: a real model has to beat them

## test: ridge regression

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.625 | [0.593, 0.656] | 23.4% | 46.1% | 26.6% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.125 | [1.088, 1.167] | 6.5% | 15.8% | 9.6% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.742 | [0.708, 0.778] | 18.8% | 36.9% | 19.0% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 0.951 | [0.912, 0.988] | 13.9% | 26.6% | 15.2% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 1.042 | [1.002, 1.081] | 10.6% | 22.9% | 13.1% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.686 | [0.649, 0.726] | 23.0% | 43.0% | 26.1% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.686 | [0.649, 0.726] | 23.2% | 43.2% | 26.4% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.708 | [0.672, 0.745] | 22.4% | 39.2% | 25.5% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.592 | [0.560, 0.624] | 27.3% | 50.9% | 27.8% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.513 | [0.482, 0.541] | 32.9% | 59.4% | 33.9% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.513 | [0.482, 0.541] | 32.9% | 59.4% | 33.8% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.659 | [0.624, 0.698] | 26.1% | 48.7% | 26.3% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | | 6.8% | 46.1% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.77 | 0.67 | 0.40 | 0.52 | 0.39 | 0.75 | 0.59 | 0.80 |
| original_vocab_bins | 2.53 | 1.94 | 0.95 | 0.84 | 0.30 | 0.57 | 1.11 | 1.50 |
| vocab | 1.70 | 0.97 | 0.76 | 0.58 | 0.43 | 0.81 | 0.73 | 0.53 |
| grammar_manual | 2.26 | 1.54 | 1.24 | 0.55 | 0.39 | 0.69 | 0.97 | 0.76 |
| grammar_rarity | 2.69 | 1.96 | 1.04 | 0.62 | 0.47 | 0.41 | 1.04 | 1.08 |
| grammar_coverage | 1.88 | 0.95 | 0.79 | 0.53 | 0.43 | 0.60 | 0.65 | 0.40 |
| grammar_all | 1.88 | 0.95 | 0.79 | 0.54 | 0.43 | 0.60 | 0.65 | 0.40 |
| cognitive | 1.95 | 1.09 | 0.39 | 0.55 | 0.37 | 0.73 | 0.63 | 0.95 |
| vocab_grammar_coverage | 1.57 | 0.79 | 0.63 | 0.50 | 0.43 | 0.58 | 0.54 | 0.39 |
| vocab_grammar_coverage_cognitive | 1.40 | 0.56 | 0.44 | 0.47 | 0.43 | 0.50 | 0.46 | 0.56 |
| all_new | 1.40 | 0.56 | 0.44 | 0.47 | 0.43 | 0.50 | 0.46 | 0.56 |
| original_all | 1.65 | 0.85 | 0.72 | 0.57 | 0.45 | 0.61 | 0.61 | 0.46 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 2.0% | 41.7% | 20.2% | 35.4% | 15.3% | 22.9% | 75.6% |
| original_vocab_bins | 0.0% | 0.0% | 6.7% | 2.7% | 47.9% | 15.3% | 4.4% | 0.0% |
| vocab | 0.0% | 3.1% | 18.3% | 27.3% | 31.2% | 10.2% | 17.1% | 44.4% |
| grammar_manual | 0.0% | 1.0% | 8.3% | 31.1% | 39.6% | 20.3% | 5.6% | 15.6% |
| grammar_rarity | 0.0% | 0.0% | 8.3% | 17.5% | 37.5% | 32.2% | 4.7% | 4.4% |
| grammar_coverage | 0.0% | 17.3% | 16.7% | 27.9% | 39.6% | 16.9% | 17.4% | 73.3% |
| grammar_all | 0.0% | 18.4% | 16.7% | 29.0% | 39.6% | 16.9% | 17.1% | 73.3% |
| cognitive | 0.0% | 0.0% | 48.3% | 21.3% | 33.3% | 15.3% | 21.2% | 64.4% |
| vocab_grammar_coverage | 3.1% | 23.5% | 18.3% | 30.1% | 33.3% | 22.0% | 25.6% | 66.7% |
| vocab_grammar_coverage_cognitive | 9.4% | 31.6% | 31.7% | 29.0% | 43.8% | 28.8% | 32.9% | 64.4% |
| all_new | 9.4% | 31.6% | 31.7% | 29.5% | 41.7% | 28.8% | 32.9% | 64.4% |
| original_all | 6.2% | 19.4% | 20.0% | 24.0% | 31.2% | 23.7% | 27.6% | 57.8% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 26.5% | 68.3% | 54.1% | 72.9% | 28.8% | 47.4% | 44.4% |
| original_vocab_bins | 0.0% | 0.0% | 18.3% | 19.7% | 77.1% | 40.7% | 8.2% | 2.2% |
| vocab | 0.0% | 18.4% | 31.7% | 49.7% | 64.6% | 30.5% | 35.3% | 48.9% |
| grammar_manual | 0.0% | 1.0% | 13.3% | 54.1% | 72.9% | 33.9% | 15.0% | 35.6% |
| grammar_rarity | 0.0% | 0.0% | 15.0% | 42.6% | 56.2% | 72.9% | 10.3% | 13.3% |
| grammar_coverage | 12.5% | 34.7% | 31.7% | 53.6% | 60.4% | 42.4% | 38.8% | 68.9% |
| grammar_all | 12.5% | 34.7% | 31.7% | 53.6% | 62.5% | 42.4% | 39.1% | 68.9% |
| cognitive | 0.0% | 0.0% | 76.7% | 47.0% | 70.8% | 28.8% | 41.5% | 33.3% |
| vocab_grammar_coverage | 15.6% | 36.7% | 43.3% | 58.5% | 70.8% | 50.8% | 50.9% | 64.4% |
| vocab_grammar_coverage_cognitive | 18.8% | 58.2% | 70.0% | 61.7% | 60.4% | 54.2% | 61.8% | 55.6% |
| all_new | 18.8% | 58.2% | 70.0% | 61.7% | 60.4% | 54.2% | 61.8% | 55.6% |
| original_all | 15.6% | 40.8% | 40.0% | 48.1% | 62.5% | 44.1% | 52.9% | 62.2% |

### test, ridge regression: confusion matrix: surface

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 9 | 9 | 8 | 4 | 0 | 2 | 0 | 0 |
| 2 | 0 | 0 | 2 | 64 | 29 | 3 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 2 | 7 | 25 | 19 | 6 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 8 | 37 | 91 | 46 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 6 | 20 | 17 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 6 | 21 | 17 | 9 | 5 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 2 | 16 | 87 | 140 | 78 | 16 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 6 | 34 |

### test, ridge regression: confusion matrix: original_vocab_bins

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 2 | 5 | 16 | 7 | 2 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 0 | 33 | 44 | 18 | 3 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 4 | 19 | 21 | 13 | 3 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 0 | 5 | 82 | 75 | 14 | 2 | 5 |
| 4 | 0 | 0 | 0 | 0 | 1 | 4 | 23 | 17 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 17 | 30 | 9 | 2 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 10 | 124 | 145 | 43 | 15 | 3 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 29 | 7 | 1 | 0 |

### test, ridge regression: confusion matrix: vocab

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 0 | 2 | 9 | 6 | 4 | 6 | 3 | 1 | 0 | 0 |
| 2 | 0 | 0 | 3 | 34 | 37 | 13 | 10 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 2 | 8 | 11 | 14 | 14 | 9 | 2 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 12 | 50 | 71 | 36 | 5 | 3 | 3 |
| 4 | 0 | 0 | 0 | 0 | 7 | 11 | 15 | 12 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 3 | 9 | 12 | 18 | 6 | 7 | 4 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 6 | 34 | 105 | 102 | 58 | 34 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 5 | 17 | 20 |

### test, ridge regression: confusion matrix: grammar_manual

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 9 | 6 | 7 | 6 | 0 | 1 | 1 |
| 2 | 0 | 0 | 1 | 0 | 23 | 51 | 17 | 4 | 2 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 5 | 9 | 17 | 16 | 10 | 2 | 1 |
| 3.5 | 0 | 0 | 0 | 2 | 6 | 57 | 69 | 38 | 7 | 3 | 1 |
| 4 | 0 | 0 | 0 | 0 | 1 | 13 | 19 | 12 | 0 | 3 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 23 | 17 | 12 | 3 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 8 | 75 | 160 | 66 | 19 | 12 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 9 | 11 | 17 | 7 |

### test, ridge regression: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 1 | 5 | 8 | 14 | 3 | 1 | 0 |
| 2 | 0 | 0 | 0 | 1 | 7 | 30 | 36 | 16 | 5 | 3 | 0 |
| 3 | 0 | 0 | 0 | 0 | 5 | 12 | 20 | 18 | 5 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 5 | 32 | 92 | 36 | 12 | 2 | 1 |
| 4 | 0 | 0 | 0 | 1 | 1 | 7 | 18 | 13 | 8 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 27 | 19 | 4 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 1 | 91 | 182 | 44 | 16 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 13 | 22 | 6 | 2 |

### test, ridge regression: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 2 | 0 | 4 | 5 | 7 | 3 | 4 | 2 | 2 | 1 | 2 |
| 2 | 6 | 8 | 17 | 24 | 15 | 12 | 10 | 4 | 1 | 1 | 0 |
| 3 | 0 | 1 | 1 | 5 | 10 | 16 | 16 | 10 | 1 | 0 | 0 |
| 3.5 | 0 | 1 | 2 | 6 | 12 | 51 | 70 | 33 | 8 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 11 | 19 | 9 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 11 | 24 | 10 | 8 | 3 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 2 | 18 | 94 | 133 | 59 | 32 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 10 | 33 |

### test, ridge regression: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 2 | 0 | 4 | 5 | 7 | 3 | 4 | 2 | 2 | 1 | 2 |
| 2 | 6 | 8 | 18 | 23 | 15 | 12 | 10 | 4 | 1 | 1 | 0 |
| 3 | 0 | 1 | 1 | 5 | 10 | 16 | 16 | 10 | 1 | 0 | 0 |
| 3.5 | 0 | 1 | 2 | 6 | 11 | 53 | 69 | 33 | 8 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 11 | 19 | 9 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 10 | 24 | 10 | 8 | 3 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 2 | 18 | 94 | 134 | 58 | 32 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 10 | 33 |

### test, ridge regression: confusion matrix: cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 4 | 8 | 12 | 5 | 2 | 0 | 1 | 0 |
| 2 | 0 | 0 | 0 | 4 | 75 | 17 | 2 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 4 | 29 | 17 | 5 | 4 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 15 | 18 | 39 | 79 | 28 | 3 | 1 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 28 | 16 | 3 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 22 | 19 | 9 | 3 | 3 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 3 | 25 | 87 | 135 | 72 | 17 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 8 | 29 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 2 | 1 | 5 | 8 | 3 | 6 | 2 | 1 | 3 | 1 | 0 |
| 2 | 3 | 10 | 23 | 24 | 16 | 12 | 8 | 1 | 1 | 0 | 0 |
| 3 | 0 | 1 | 2 | 8 | 11 | 21 | 13 | 4 | 0 | 0 | 0 |
| 3.5 | 0 | 1 | 3 | 5 | 13 | 55 | 70 | 29 | 6 | 1 | 0 |
| 4 | 0 | 0 | 0 | 2 | 4 | 15 | 16 | 11 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 12 | 17 | 13 | 10 | 4 |
| 5.5 | 0 | 0 | 0 | 1 | 0 | 1 | 9 | 57 | 138 | 87 | 47 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 11 | 30 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 6 | 8 | 4 | 5 | 1 | 4 | 0 | 1 | 0 |
| 2 | 1 | 11 | 31 | 28 | 17 | 7 | 1 | 2 | 0 | 0 | 0 |
| 3 | 0 | 2 | 4 | 7 | 19 | 22 | 5 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 4 | 4 | 17 | 53 | 77 | 26 | 2 | 0 | 0 |
| 4 | 0 | 0 | 0 | 2 | 6 | 17 | 21 | 2 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 2 | 7 | 22 | 17 | 8 | 3 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 6 | 41 | 135 | 112 | 44 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 11 | 29 |

### test, ridge regression: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 6 | 8 | 4 | 5 | 1 | 4 | 0 | 1 | 0 |
| 2 | 1 | 11 | 31 | 28 | 17 | 7 | 1 | 2 | 0 | 0 | 0 |
| 3 | 0 | 2 | 3 | 8 | 19 | 22 | 5 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 4 | 4 | 17 | 54 | 76 | 26 | 2 | 0 | 0 |
| 4 | 0 | 0 | 0 | 2 | 6 | 18 | 20 | 2 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 2 | 7 | 22 | 17 | 8 | 3 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 6 | 40 | 136 | 112 | 44 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 11 | 29 |

### test, ridge regression: confusion matrix: original_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 2 | 2 | 5 | 9 | 2 | 0 | 7 | 3 | 0 | 0 | 2 |
| 2 | 2 | 8 | 19 | 30 | 16 | 11 | 6 | 5 | 0 | 0 | 1 |
| 3 | 0 | 4 | 2 | 4 | 12 | 18 | 14 | 5 | 1 | 0 | 0 |
| 3.5 | 0 | 1 | 3 | 5 | 18 | 44 | 65 | 41 | 5 | 1 | 0 |
| 4 | 0 | 0 | 0 | 2 | 3 | 12 | 15 | 11 | 5 | 0 | 0 |
| 5 | 0 | 0 | 0 | 1 | 0 | 2 | 14 | 16 | 14 | 9 | 3 |
| 5.5 | 0 | 0 | 1 | 1 | 1 | 5 | 20 | 50 | 95 | 94 | 73 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 14 | 26 |

## valid (native): ridge regression

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.653 | [0.598, 0.714] | 22.8% | 38.8% | 27.9% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.181 | [1.109, 1.253] | 4.9% | 12.9% | 11.1% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.819 | [0.749, 0.890] | 17.9% | 31.9% | 18.6% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 1.007 | [0.934, 1.079] | 12.9% | 22.4% | 17.1% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 1.036 | [0.952, 1.126] | 14.4% | 25.9% | 15.8% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 1.205 | [0.989, 1.438] | 18.3% | 36.9% | 24.4% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 1.206 | [0.990, 1.440] | 18.3% | 37.3% | 24.4% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.747 | [0.677, 0.827] | 18.6% | 36.1% | 26.0% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.798 | [0.689, 0.911] | 23.2% | 43.7% | 25.7% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.863 | [0.720, 1.012] | 27.0% | 47.5% | 36.6% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.863 | [0.720, 1.013] | 27.0% | 47.9% | 36.6% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 1.242 | [1.015, 1.499] | 21.7% | 39.2% | 26.0% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | | 5.7% | 44.5% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.46 | 0.84 | 0.32 | 0.51 | 0.35 | 0.75 | 0.66 | 0.49 |
| original_vocab_bins | 2.44 | 1.89 | 0.97 | 0.89 | 0.25 | 0.64 | 1.15 | 1.52 |
| vocab | 1.39 | 1.06 | 0.84 | 0.69 | 0.45 | 0.91 | 0.80 | 0.54 |
| grammar_manual | 2.17 | 1.56 | 1.05 | 0.69 | 0.53 | 0.74 | 0.97 | 0.91 |
| grammar_rarity | 2.60 | 1.92 | 0.93 | 0.52 | 0.75 | 0.27 | 1.03 | 1.02 |
| grammar_coverage | 1.44 | 1.46 | 0.85 | 0.67 | 0.32 | 0.71 | 1.47 | 2.74 |
| grammar_all | 1.44 | 1.46 | 0.85 | 0.67 | 0.32 | 0.71 | 1.47 | 2.74 |
| cognitive | 1.76 | 1.21 | 0.38 | 0.60 | 0.33 | 0.65 | 0.70 | 0.55 |
| vocab_grammar_coverage | 1.16 | 1.11 | 0.65 | 0.62 | 0.31 | 0.71 | 0.78 | 1.40 |
| vocab_grammar_coverage_cognitive | 1.12 | 0.94 | 0.54 | 0.61 | 0.26 | 0.48 | 1.00 | 1.97 |
| all_new | 1.12 | 0.94 | 0.54 | 0.61 | 0.26 | 0.48 | 1.00 | 1.97 |
| original_all | 1.23 | 1.44 | 0.87 | 0.68 | 0.36 | 0.74 | 1.55 | 3.04 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 6.9% | 52.9% | 21.0% | 45.5% | 0.0% | 21.6% | 75.0% |
| original_vocab_bins | 0.0% | 0.0% | 0.0% | 4.8% | 63.6% | 20.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 11.8% | 25.8% | 45.5% | 6.7% | 17.6% | 41.7% |
| grammar_manual | 0.0% | 0.0% | 17.6% | 21.0% | 27.3% | 40.0% | 5.9% | 25.0% |
| grammar_rarity | 0.0% | 0.0% | 5.9% | 30.6% | 9.1% | 66.7% | 5.9% | 8.3% |
| grammar_coverage | 13.3% | 10.3% | 17.6% | 25.8% | 54.5% | 13.3% | 9.8% | 50.0% |
| grammar_all | 13.3% | 10.3% | 17.6% | 25.8% | 54.5% | 13.3% | 9.8% | 50.0% |
| cognitive | 0.0% | 0.0% | 47.1% | 12.9% | 36.4% | 20.0% | 16.7% | 75.0% |
| vocab_grammar_coverage | 20.0% | 10.3% | 23.5% | 30.6% | 54.5% | 13.3% | 19.6% | 33.3% |
| vocab_grammar_coverage_cognitive | 13.3% | 17.2% | 47.1% | 24.2% | 72.7% | 40.0% | 19.6% | 58.3% |
| all_new | 13.3% | 17.2% | 47.1% | 24.2% | 72.7% | 40.0% | 19.6% | 58.3% |
| original_all | 20.0% | 0.0% | 23.5% | 30.6% | 45.5% | 13.3% | 16.7% | 58.3% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 13.8% | 76.5% | 48.4% | 72.7% | 26.7% | 36.3% | 50.0% |
| original_vocab_bins | 0.0% | 0.0% | 5.9% | 24.2% | 100.0% | 40.0% | 1.0% | 0.0% |
| vocab | 6.7% | 10.3% | 23.5% | 41.9% | 63.6% | 20.0% | 31.4% | 66.7% |
| grammar_manual | 0.0% | 0.0% | 17.6% | 40.3% | 54.5% | 40.0% | 14.7% | 33.3% |
| grammar_rarity | 0.0% | 0.0% | 17.6% | 61.3% | 36.4% | 86.7% | 8.8% | 8.3% |
| grammar_coverage | 20.0% | 24.1% | 35.3% | 59.7% | 72.7% | 33.3% | 23.5% | 58.3% |
| grammar_all | 20.0% | 24.1% | 35.3% | 59.7% | 72.7% | 33.3% | 24.5% | 58.3% |
| cognitive | 0.0% | 3.4% | 70.6% | 37.1% | 72.7% | 46.7% | 35.3% | 66.7% |
| vocab_grammar_coverage | 20.0% | 27.6% | 58.8% | 58.1% | 63.6% | 26.7% | 40.2% | 50.0% |
| vocab_grammar_coverage_cognitive | 20.0% | 44.8% | 76.5% | 54.8% | 81.8% | 53.3% | 37.3% | 58.3% |
| all_new | 20.0% | 44.8% | 76.5% | 54.8% | 81.8% | 53.3% | 38.2% | 58.3% |
| original_all | 20.0% | 27.6% | 41.2% | 54.8% | 72.7% | 33.3% | 32.4% | 41.7% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.354 | [0.322, 0.388] | 63.1% | 76.2% | 46.8% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.909 | [0.862, 0.960] | 20.7% | 37.3% | 16.8% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.471 | [0.436, 0.509] | 47.5% | 68.2% | 38.3% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 0.821 | [0.777, 0.868] | 22.3% | 41.3% | 18.0% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 0.793 | [0.745, 0.844] | 28.4% | 46.1% | 21.8% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.460 | [0.426, 0.493] | 48.3% | 68.8% | 38.9% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.472 | [0.438, 0.508] | 46.2% | 67.3% | 37.1% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.340 | [0.310, 0.370] | 63.8% | 79.1% | 48.3% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.382 | [0.352, 0.416] | 57.2% | 74.7% | 45.9% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.257 | [0.233, 0.284] | 71.1% | 84.9% | 57.8% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.258 | [0.233, 0.285] | 72.3% | 85.5% | 59.4% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.374 | [0.343, 0.408] | 58.4% | 77.0% | 45.6% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | | 6.8% | 46.1% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.22 | 0.27 | 0.60 | 0.32 | 0.57 | 0.74 | 0.19 | 0.23 |
| original_vocab_bins | 2.15 | 1.59 | 0.87 | 0.64 | 0.50 | 0.62 | 0.78 | 1.48 |
| vocab | 1.32 | 0.62 | 0.77 | 0.37 | 0.45 | 0.44 | 0.37 | 0.40 |
| grammar_manual | 2.00 | 1.06 | 1.30 | 0.75 | 0.65 | 0.58 | 0.65 | 0.87 |
| grammar_rarity | 2.47 | 1.41 | 1.11 | 0.47 | 0.67 | 0.46 | 0.62 | 1.03 |
| grammar_coverage | 1.23 | 0.63 | 0.78 | 0.32 | 0.63 | 0.48 | 0.35 | 0.32 |
| grammar_all | 1.28 | 0.66 | 0.80 | 0.35 | 0.59 | 0.48 | 0.35 | 0.37 |
| cognitive | 1.23 | 0.38 | 0.47 | 0.22 | 0.72 | 0.44 | 0.22 | 0.32 |
| vocab_grammar_coverage | 1.12 | 0.61 | 0.68 | 0.23 | 0.52 | 0.37 | 0.27 | 0.27 |
| vocab_grammar_coverage_cognitive | 0.87 | 0.30 | 0.36 | 0.19 | 0.51 | 0.35 | 0.16 | 0.22 |
| all_new | 0.82 | 0.30 | 0.35 | 0.21 | 0.51 | 0.36 | 0.15 | 0.23 |
| original_all | 1.05 | 0.52 | 0.57 | 0.23 | 0.57 | 0.37 | 0.30 | 0.28 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 9.4% | 68.4% | 25.0% | 67.8% | 29.2% | 16.9% | 82.1% | 75.6% |
| original_vocab_bins | 0.0% | 4.1% | 20.0% | 25.1% | 33.3% | 27.1% | 25.0% | 0.0% |
| vocab | 9.4% | 40.8% | 21.7% | 46.4% | 41.7% | 37.3% | 60.6% | 48.9% |
| grammar_manual | 0.0% | 19.4% | 6.7% | 15.8% | 22.9% | 30.5% | 30.6% | 17.8% |
| grammar_rarity | 0.0% | 13.3% | 13.3% | 42.6% | 14.6% | 40.7% | 31.8% | 17.8% |
| grammar_coverage | 25.0% | 38.8% | 18.3% | 57.4% | 22.9% | 39.0% | 58.5% | 51.1% |
| grammar_all | 21.9% | 33.7% | 18.3% | 52.5% | 31.2% | 37.3% | 57.6% | 44.4% |
| cognitive | 12.5% | 57.1% | 40.0% | 76.0% | 22.9% | 39.0% | 78.8% | 60.0% |
| vocab_grammar_coverage | 37.5% | 49.0% | 13.3% | 71.0% | 18.8% | 49.2% | 68.2% | 60.0% |
| vocab_grammar_coverage_cognitive | 31.2% | 68.4% | 41.7% | 80.3% | 29.2% | 49.2% | 84.7% | 77.8% |
| all_new | 43.8% | 68.4% | 45.0% | 79.2% | 25.0% | 50.8% | 87.1% | 75.6% |
| original_all | 31.2% | 49.0% | 25.0% | 74.9% | 16.7% | 52.5% | 69.1% | 46.7% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 31.2% | 81.6% | 41.7% | 80.9% | 50.0% | 40.7% | 90.3% | 91.1% |
| original_vocab_bins | 0.0% | 11.2% | 33.3% | 44.3% | 60.4% | 52.5% | 43.8% | 4.4% |
| vocab | 31.2% | 68.4% | 36.7% | 72.1% | 62.5% | 67.8% | 75.9% | 68.9% |
| grammar_manual | 9.4% | 32.7% | 18.3% | 40.4% | 47.9% | 50.8% | 51.5% | 20.0% |
| grammar_rarity | 0.0% | 21.4% | 23.3% | 64.5% | 39.6% | 61.0% | 52.4% | 28.9% |
| grammar_coverage | 37.5% | 62.2% | 31.7% | 78.1% | 37.5% | 66.1% | 78.2% | 82.2% |
| grammar_all | 34.4% | 57.1% | 35.0% | 80.3% | 50.0% | 57.6% | 75.6% | 71.1% |
| cognitive | 31.2% | 74.5% | 60.0% | 90.2% | 39.6% | 67.8% | 89.7% | 80.0% |
| vocab_grammar_coverage | 50.0% | 63.3% | 35.0% | 86.3% | 50.0% | 78.0% | 83.5% | 77.8% |
| vocab_grammar_coverage_cognitive | 50.0% | 81.6% | 73.3% | 89.6% | 54.2% | 76.3% | 93.2% | 93.3% |
| all_new | 50.0% | 83.7% | 75.0% | 89.1% | 56.2% | 74.6% | 94.7% | 91.1% |
| original_all | 46.9% | 70.4% | 51.7% | 89.1% | 45.8% | 78.0% | 82.9% | 84.4% |

### test, gradient boosting: confusion matrix: surface

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 10 | 8 | 1 | 3 | 4 | 2 | 0 | 1 | 0 |
| 2 | 0 | 1 | 67 | 19 | 10 | 1 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 13 | 18 | 15 | 4 | 6 | 2 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 1 | 9 | 124 | 24 | 13 | 8 | 4 | 0 |
| 4 | 0 | 0 | 2 | 1 | 5 | 9 | 14 | 12 | 3 | 2 | 0 |
| 5 | 0 | 0 | 0 | 1 | 1 | 9 | 10 | 10 | 10 | 17 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 2 | 4 | 8 | 6 | 34 | 279 | 7 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 0 | 8 | 34 |

### test, gradient boosting: confusion matrix: original_vocab_bins

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 2 | 7 | 6 | 5 | 6 | 4 | 0 | 0 |
| 2 | 0 | 1 | 4 | 19 | 18 | 16 | 12 | 11 | 15 | 2 | 0 |
| 3 | 0 | 2 | 4 | 6 | 12 | 13 | 7 | 10 | 5 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 17 | 46 | 51 | 44 | 21 | 1 | 0 |
| 4 | 0 | 0 | 1 | 2 | 6 | 9 | 16 | 13 | 0 | 1 | 0 |
| 5 | 0 | 0 | 0 | 1 | 3 | 4 | 7 | 19 | 16 | 7 | 2 |
| 5.5 | 0 | 0 | 2 | 1 | 3 | 21 | 58 | 62 | 95 | 85 | 13 |
| 6 | 0 | 0 | 0 | 1 | 0 | 4 | 6 | 19 | 10 | 5 | 0 |

### test, gradient boosting: confusion matrix: vocab

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 9 | 7 | 5 | 1 | 3 | 2 | 0 | 2 | 0 |
| 2 | 0 | 1 | 40 | 32 | 8 | 6 | 3 | 6 | 1 | 1 | 0 |
| 3 | 0 | 0 | 7 | 15 | 13 | 6 | 6 | 9 | 4 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 13 | 85 | 56 | 22 | 5 | 0 | 0 |
| 4 | 0 | 0 | 0 | 3 | 2 | 6 | 20 | 10 | 7 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 2 | 5 | 22 | 22 | 6 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 3 | 5 | 13 | 33 | 73 | 206 | 7 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 2 | 18 | 22 |

### test, gradient boosting: confusion matrix: grammar_manual

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 6 | 2 | 8 | 5 | 2 | 2 | 4 | 2 | 1 |
| 2 | 0 | 3 | 19 | 26 | 14 | 14 | 11 | 7 | 3 | 1 | 0 |
| 3 | 0 | 0 | 4 | 4 | 4 | 10 | 9 | 9 | 13 | 6 | 1 |
| 3.5 | 0 | 0 | 1 | 17 | 39 | 29 | 38 | 27 | 20 | 11 | 1 |
| 4 | 0 | 0 | 0 | 1 | 9 | 7 | 11 | 9 | 7 | 3 | 1 |
| 5 | 0 | 0 | 0 | 0 | 2 | 4 | 14 | 13 | 18 | 8 | 0 |
| 5.5 | 0 | 0 | 0 | 3 | 4 | 14 | 25 | 71 | 114 | 104 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 5 | 17 | 11 | 8 |

### test, gradient boosting: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 1 | 1 | 4 | 7 | 7 | 7 | 3 | 0 | 2 |
| 2 | 0 | 2 | 13 | 17 | 10 | 25 | 10 | 7 | 10 | 4 | 0 |
| 3 | 0 | 1 | 1 | 7 | 8 | 9 | 8 | 15 | 8 | 3 | 0 |
| 3.5 | 0 | 0 | 0 | 5 | 21 | 78 | 41 | 24 | 10 | 4 | 0 |
| 4 | 0 | 0 | 1 | 1 | 7 | 14 | 7 | 6 | 11 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 9 | 11 | 24 | 12 | 0 |
| 5.5 | 0 | 0 | 1 | 0 | 4 | 10 | 33 | 61 | 108 | 108 | 15 |
| 6 | 0 | 0 | 0 | 0 | 0 | 5 | 4 | 7 | 9 | 12 | 8 |

### test, gradient boosting: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 8 | 5 | 4 | 4 | 4 | 2 | 2 | 2 | 0 | 0 |
| 2 | 0 | 5 | 38 | 29 | 8 | 9 | 4 | 4 | 1 | 0 | 0 |
| 3 | 0 | 1 | 0 | 9 | 11 | 10 | 17 | 10 | 2 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 2 | 13 | 105 | 46 | 11 | 5 | 0 | 0 |
| 4 | 0 | 0 | 0 | 5 | 6 | 11 | 11 | 10 | 4 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 5 | 6 | 19 | 23 | 4 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 3 | 17 | 27 | 81 | 199 | 13 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 18 | 23 |

### test, gradient boosting: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 7 | 6 | 4 | 4 | 2 | 4 | 1 | 3 | 0 | 0 |
| 2 | 0 | 8 | 33 | 29 | 9 | 9 | 5 | 4 | 1 | 0 | 0 |
| 3 | 0 | 1 | 0 | 10 | 11 | 12 | 12 | 11 | 3 | 0 | 0 |
| 3.5 | 0 | 0 | 2 | 3 | 12 | 96 | 51 | 14 | 4 | 1 | 0 |
| 4 | 0 | 0 | 0 | 5 | 8 | 7 | 15 | 10 | 2 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 2 | 1 | 8 | 17 | 22 | 9 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 3 | 9 | 31 | 90 | 196 | 10 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 18 | 20 |

### test, gradient boosting: confusion matrix: cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 4 | 8 | 6 | 6 | 2 | 4 | 1 | 1 | 0 | 0 |
| 2 | 0 | 2 | 56 | 26 | 10 | 1 | 2 | 0 | 1 | 0 | 0 |
| 3 | 0 | 1 | 7 | 16 | 24 | 6 | 4 | 2 | 0 | 0 | 0 |
| 3.5 | 0 | 1 | 0 | 0 | 11 | 139 | 22 | 4 | 5 | 1 | 0 |
| 4 | 0 | 0 | 1 | 6 | 8 | 6 | 11 | 10 | 4 | 2 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 7 | 23 | 19 | 2 |
| 5.5 | 0 | 0 | 0 | 1 | 0 | 3 | 10 | 10 | 45 | 268 | 3 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 3 | 14 | 27 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 12 | 5 | 4 | 1 | 4 | 2 | 2 | 1 | 1 | 0 |
| 2 | 1 | 4 | 48 | 16 | 12 | 6 | 8 | 3 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 13 | 8 | 17 | 15 | 5 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 1 | 11 | 130 | 31 | 8 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 20 | 9 | 9 | 3 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 1 | 6 | 16 | 29 | 6 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 9 | 19 | 73 | 232 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 17 | 27 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 10 | 7 | 3 | 4 | 4 | 3 | 0 | 0 | 0 | 0 |
| 2 | 0 | 2 | 67 | 20 | 4 | 4 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 4 | 20 | 25 | 8 | 2 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 0 | 10 | 147 | 15 | 6 | 4 | 0 | 0 |
| 4 | 0 | 0 | 1 | 1 | 6 | 19 | 14 | 3 | 4 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 0 | 5 | 12 | 29 | 11 | 1 |
| 5.5 | 0 | 0 | 1 | 0 | 0 | 2 | 4 | 8 | 30 | 288 | 7 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 7 | 35 |

### test, gradient boosting: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 14 | 5 | 3 | 5 | 3 | 2 | 0 | 0 | 0 | 0 |
| 2 | 0 | 3 | 67 | 17 | 6 | 4 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 6 | 18 | 27 | 7 | 2 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 0 | 9 | 145 | 18 | 7 | 2 | 1 | 0 |
| 4 | 0 | 0 | 1 | 0 | 5 | 24 | 12 | 3 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 0 | 6 | 10 | 30 | 11 | 1 |
| 5.5 | 0 | 0 | 1 | 0 | 0 | 2 | 3 | 8 | 27 | 296 | 3 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 8 | 34 |

### test, gradient boosting: confusion matrix: original_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 10 | 8 | 4 | 2 | 3 | 1 | 2 | 2 | 0 | 0 |
| 2 | 0 | 5 | 48 | 26 | 6 | 7 | 3 | 0 | 2 | 1 | 0 |
| 3 | 0 | 1 | 3 | 13 | 15 | 13 | 10 | 5 | 0 | 0 | 0 |
| 3.5 | 0 | 1 | 1 | 2 | 6 | 137 | 29 | 2 | 3 | 2 | 0 |
| 4 | 0 | 0 | 1 | 0 | 4 | 23 | 8 | 7 | 4 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 2 | 6 | 10 | 31 | 10 | 0 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 5 | 10 | 22 | 63 | 235 | 3 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 23 | 21 |

## valid (native): gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.340 | [0.283, 0.401] | 61.2% | 79.8% | 46.1% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.916 | [0.821, 1.005] | 20.9% | 39.5% | 19.0% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.524 | [0.455, 0.600] | 48.7% | 65.0% | 40.6% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 0.831 | [0.740, 0.919] | 23.2% | 43.0% | 17.6% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 0.842 | [0.744, 0.949] | 31.9% | 44.5% | 23.9% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.483 | [0.423, 0.540] | 46.0% | 63.5% | 34.9% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.482 | [0.424, 0.544] | 44.5% | 65.8% | 35.3% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.325 | [0.266, 0.383] | 66.9% | 83.7% | 51.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.392 | [0.335, 0.448] | 55.1% | 74.1% | 44.0% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.257 | [0.209, 0.308] | 70.0% | 87.8% | 53.3% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.265 | [0.217, 0.318] | 69.2% | 86.7% | 55.8% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.380 | [0.327, 0.433] | 56.3% | 73.8% | 43.5% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | | 5.7% | 44.5% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.02 | 0.34 | 0.44 | 0.25 | 0.43 | 0.73 | 0.22 | 0.25 |
| original_vocab_bins | 2.19 | 1.71 | 0.83 | 0.60 | 0.38 | 0.48 | 0.78 | 1.34 |
| vocab | 1.04 | 0.61 | 0.77 | 0.38 | 0.50 | 0.53 | 0.49 | 0.39 |
| grammar_manual | 2.12 | 1.08 | 0.98 | 0.71 | 1.18 | 0.61 | 0.60 | 0.97 |
| grammar_rarity | 2.27 | 1.45 | 1.01 | 0.48 | 0.80 | 0.45 | 0.70 | 0.97 |
| grammar_coverage | 0.98 | 0.85 | 0.61 | 0.30 | 0.52 | 0.50 | 0.40 | 0.40 |
| grammar_all | 1.07 | 0.83 | 0.63 | 0.29 | 0.50 | 0.48 | 0.39 | 0.47 |
| cognitive | 1.10 | 0.40 | 0.43 | 0.13 | 0.64 | 0.35 | 0.25 | 0.37 |
| vocab_grammar_coverage | 0.97 | 0.61 | 0.46 | 0.21 | 0.56 | 0.50 | 0.31 | 0.35 |
| vocab_grammar_coverage_cognitive | 0.66 | 0.42 | 0.35 | 0.16 | 0.31 | 0.34 | 0.19 | 0.19 |
| all_new | 0.66 | 0.45 | 0.31 | 0.16 | 0.31 | 0.38 | 0.20 | 0.20 |
| original_all | 0.71 | 0.50 | 0.68 | 0.16 | 0.40 | 0.38 | 0.39 | 0.31 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 20.0% | 51.7% | 52.9% | 66.1% | 27.3% | 13.3% | 79.4% | 58.3% |
| original_vocab_bins | 0.0% | 10.3% | 17.6% | 30.6% | 27.3% | 46.7% | 19.6% | 0.0% |
| vocab | 13.3% | 41.4% | 17.6% | 54.8% | 45.5% | 26.7% | 58.8% | 66.7% |
| grammar_manual | 6.7% | 10.3% | 23.5% | 27.4% | 0.0% | 26.7% | 29.4% | 16.7% |
| grammar_rarity | 0.0% | 10.3% | 5.9% | 54.8% | 27.3% | 33.3% | 34.3% | 25.0% |
| grammar_coverage | 13.3% | 27.6% | 35.3% | 58.1% | 18.2% | 20.0% | 56.9% | 50.0% |
| grammar_all | 20.0% | 27.6% | 29.4% | 59.7% | 18.2% | 26.7% | 51.0% | 50.0% |
| cognitive | 40.0% | 48.3% | 47.1% | 85.5% | 18.2% | 46.7% | 78.4% | 50.0% |
| vocab_grammar_coverage | 40.0% | 37.9% | 35.3% | 67.7% | 27.3% | 20.0% | 65.7% | 58.3% |
| vocab_grammar_coverage_cognitive | 40.0% | 55.2% | 35.3% | 83.9% | 27.3% | 40.0% | 86.3% | 58.3% |
| all_new | 40.0% | 51.7% | 41.2% | 77.4% | 45.5% | 46.7% | 85.3% | 58.3% |
| original_all | 13.3% | 41.4% | 35.3% | 80.6% | 27.3% | 46.7% | 61.8% | 41.7% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 33.3% | 82.8% | 70.6% | 85.5% | 72.7% | 46.7% | 89.2% | 83.3% |
| original_vocab_bins | 0.0% | 17.2% | 47.1% | 51.6% | 72.7% | 66.7% | 40.2% | 0.0% |
| vocab | 40.0% | 58.6% | 47.1% | 74.2% | 63.6% | 40.0% | 71.6% | 66.7% |
| grammar_manual | 6.7% | 24.1% | 29.4% | 43.5% | 9.1% | 53.3% | 56.9% | 50.0% |
| grammar_rarity | 0.0% | 20.7% | 17.6% | 71.0% | 27.3% | 60.0% | 48.0% | 25.0% |
| grammar_coverage | 26.7% | 41.4% | 47.1% | 80.6% | 54.5% | 53.3% | 70.6% | 58.3% |
| grammar_all | 26.7% | 48.3% | 52.9% | 80.6% | 63.6% | 66.7% | 70.6% | 58.3% |
| cognitive | 46.7% | 75.9% | 70.6% | 98.4% | 36.4% | 86.7% | 89.2% | 83.3% |
| vocab_grammar_coverage | 40.0% | 65.5% | 58.8% | 88.7% | 45.5% | 46.7% | 83.3% | 66.7% |
| vocab_grammar_coverage_cognitive | 73.3% | 75.9% | 76.5% | 93.5% | 81.8% | 80.0% | 92.2% | 100.0% |
| all_new | 60.0% | 75.9% | 82.4% | 93.5% | 81.8% | 80.0% | 91.2% | 91.7% |
| original_all | 33.3% | 65.5% | 41.2% | 93.5% | 63.6% | 66.7% | 76.5% | 83.3% |

## Paired MAE differences (first minus second; negative = the first is better)

Bootstrap over the evaluation texts (1,000 resamples, the same resamples for both models). A 95% interval that does not contain 0 is a difference larger than noise.

### test, ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.117 | [+0.084, +0.151] * |
| grammar_coverage | surface | +0.061 | [+0.023, +0.104] * |
| cognitive | surface | +0.083 | [+0.059, +0.107] * |
| grammar_coverage | grammar_manual | -0.265 | [-0.303, -0.225] * |
| grammar_coverage | grammar_rarity | -0.356 | [-0.395, -0.315] * |
| grammar_all | grammar_coverage | -0.000 | [-0.000, +0.000] |
| vocab_grammar_coverage | vocab | -0.150 | [-0.183, -0.120] * |
| vocab_grammar_coverage | original_all | -0.067 | [-0.097, -0.036] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.079 | [-0.100, -0.060] * |
| vocab_grammar_coverage_cognitive | original_all | -0.146 | [-0.173, -0.117] * |
| all_new | vocab_grammar_coverage_cognitive | +0.000 | [+0.000, +0.001] * |
| all_new | original_all | -0.146 | [-0.173, -0.117] * |
| vocab | original_vocab_bins | -0.384 | [-0.427, -0.344] * |
| original_all | surface | +0.034 | [-0.004, +0.075] |
| vocab_grammar_coverage_cognitive | surface | -0.112 | [-0.140, -0.083] * |
| all_new | surface | -0.112 | [-0.140, -0.083] * |

### valid (native), ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.167 | [+0.096, +0.237] * |
| grammar_coverage | surface | +0.551 | [+0.342, +0.787] * |
| cognitive | surface | +0.094 | [+0.048, +0.138] * |
| grammar_coverage | grammar_manual | +0.199 | [-0.020, +0.441] |
| grammar_coverage | grammar_rarity | +0.167 | [-0.050, +0.411] |
| grammar_all | grammar_coverage | +0.002 | [+0.001, +0.003] * |
| vocab_grammar_coverage | vocab | -0.024 | [-0.131, +0.091] |
| vocab_grammar_coverage | original_all | -0.448 | [-0.632, -0.285] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | +0.066 | [-0.003, +0.142] |
| vocab_grammar_coverage_cognitive | original_all | -0.381 | [-0.505, -0.271] * |
| all_new | vocab_grammar_coverage_cognitive | +0.000 | [-0.000, +0.001] |
| all_new | original_all | -0.381 | [-0.504, -0.271] * |
| vocab | original_vocab_bins | -0.361 | [-0.436, -0.284] * |
| original_all | surface | +0.590 | [+0.361, +0.854] * |
| vocab_grammar_coverage_cognitive | surface | +0.209 | [+0.070, +0.368] * |
| all_new | surface | +0.209 | [+0.071, +0.369] * |

### test, gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.117 | [+0.080, +0.156] * |
| grammar_coverage | surface | +0.106 | [+0.071, +0.138] * |
| cognitive | surface | -0.014 | [-0.044, +0.016] |
| grammar_coverage | grammar_manual | -0.361 | [-0.406, -0.316] * |
| grammar_coverage | grammar_rarity | -0.334 | [-0.382, -0.288] * |
| grammar_all | grammar_coverage | +0.013 | [-0.001, +0.027] |
| vocab_grammar_coverage | vocab | -0.089 | [-0.119, -0.060] * |
| vocab_grammar_coverage | original_all | +0.007 | [-0.019, +0.033] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.125 | [-0.151, -0.099] * |
| vocab_grammar_coverage_cognitive | original_all | -0.118 | [-0.142, -0.093] * |
| all_new | vocab_grammar_coverage_cognitive | +0.001 | [-0.006, +0.008] |
| all_new | original_all | -0.117 | [-0.141, -0.093] * |
| vocab | original_vocab_bins | -0.439 | [-0.488, -0.389] * |
| original_all | surface | +0.021 | [-0.012, +0.054] |
| vocab_grammar_coverage_cognitive | surface | -0.097 | [-0.121, -0.072] * |
| all_new | surface | -0.096 | [-0.121, -0.071] * |

### valid (native), gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.185 | [+0.111, +0.261] * |
| grammar_coverage | surface | +0.144 | [+0.080, +0.207] * |
| cognitive | surface | -0.015 | [-0.072, +0.042] |
| grammar_coverage | grammar_manual | -0.347 | [-0.425, -0.266] * |
| grammar_coverage | grammar_rarity | -0.361 | [-0.465, -0.262] * |
| grammar_all | grammar_coverage | +0.000 | [-0.024, +0.023] |
| vocab_grammar_coverage | vocab | -0.132 | [-0.191, -0.075] * |
| vocab_grammar_coverage | original_all | +0.012 | [-0.039, +0.066] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.136 | [-0.186, -0.086] * |
| vocab_grammar_coverage_cognitive | original_all | -0.123 | [-0.168, -0.077] * |
| all_new | vocab_grammar_coverage_cognitive | +0.009 | [-0.003, +0.020] |
| all_new | original_all | -0.115 | [-0.159, -0.068] * |
| vocab | original_vocab_bins | -0.391 | [-0.485, -0.291] * |
| original_all | surface | +0.040 | [-0.017, +0.100] |
| vocab_grammar_coverage_cognitive | surface | -0.083 | [-0.126, -0.039] * |
| all_new | surface | -0.074 | [-0.118, -0.031] * |

