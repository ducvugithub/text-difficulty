# Experiment: train on train_all (8,293 rows)

- Source and origin are not features. Test = real Finnish only; valid (native) = the real-Finnish rows of valid.
- **MAE**: mean absolute error in label units (the labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)
- **accuracy**: share of texts whose prediction, rounded to the nearest half step, is exactly the label
- **accuracy ±1 step**: share within 0.5 of the label
- **balanced accuracy**: mean of the per-label accuracies; every label counts equally, so favouring the common labels is punished
- dummy models predict one constant for every text, taken from the training labels: most common label (3); median label (3.5)
  They are the floor: a real model has to beat them

## test: ridge regression

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.911 | [0.872, 0.949] | 16.3% | 31.4% | 13.8% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.264 | [1.213, 1.313] | 19.0% | 28.2% | 13.8% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.885 | [0.850, 0.919] | 14.7% | 29.4% | 15.2% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 1.196 | [1.149, 1.239] | 19.3% | 25.8% | 15.1% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 1.241 | [1.190, 1.286] | 18.2% | 26.8% | 14.3% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.934 | [0.897, 0.970] | 14.1% | 27.1% | 15.0% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.933 | [0.897, 0.969] | 14.0% | 27.1% | 15.0% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 1.137 | [1.093, 1.185] | 16.6% | 26.1% | 11.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.769 | [0.736, 0.802] | 15.7% | 34.2% | 15.8% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.626 | [0.598, 0.655] | 22.7% | 45.4% | 22.5% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.625 | [0.598, 0.655] | 22.4% | 45.3% | 22.1% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.946 | [0.908, 0.982] | 15.3% | 28.9% | 15.7% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | | 21.2% | 33.6% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.82 | 1.11 | 0.47 | 0.29 | 0.38 | 1.14 | 1.15 | 1.44 |
| original_vocab_bins | 1.99 | 1.46 | 0.47 | 0.16 | 0.43 | 1.31 | 1.84 | 2.31 |
| vocab | 1.90 | 1.30 | 0.70 | 0.43 | 0.27 | 0.93 | 0.98 | 1.19 |
| grammar_manual | 1.93 | 1.32 | 0.63 | 0.18 | 0.41 | 1.26 | 1.74 | 1.92 |
| grammar_rarity | 2.05 | 1.41 | 0.52 | 0.18 | 0.40 | 1.22 | 1.82 | 2.12 |
| grammar_coverage | 1.94 | 1.23 | 0.73 | 0.35 | 0.27 | 0.72 | 1.23 | 1.01 |
| grammar_all | 1.95 | 1.23 | 0.73 | 0.34 | 0.27 | 0.72 | 1.23 | 1.01 |
| cognitive | 2.04 | 1.59 | 0.50 | 0.23 | 0.45 | 1.15 | 1.50 | 2.03 |
| vocab_grammar_coverage | 1.86 | 1.22 | 0.68 | 0.41 | 0.27 | 0.74 | 0.81 | 0.89 |
| vocab_grammar_coverage_cognitive | 1.60 | 0.59 | 0.40 | 0.38 | 0.40 | 0.68 | 0.72 | 0.76 |
| all_new | 1.60 | 0.59 | 0.40 | 0.38 | 0.40 | 0.68 | 0.72 | 0.76 |
| original_all | 1.91 | 1.29 | 0.68 | 0.29 | 0.27 | 0.70 | 1.28 | 1.06 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 23.3% | 47.0% | 31.2% | 1.7% | 7.4% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 16.7% | 80.9% | 12.5% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 25.0% | 31.1% | 52.1% | 5.1% | 7.9% | 0.0% |
| grammar_manual | 0.0% | 0.0% | 11.7% | 79.8% | 29.2% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 15.0% | 74.3% | 25.0% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 15.0% | 41.5% | 50.0% | 11.9% | 1.8% | 0.0% |
| grammar_all | 0.0% | 0.0% | 15.0% | 41.5% | 50.0% | 11.9% | 1.5% | 0.0% |
| cognitive | 0.0% | 0.0% | 10.0% | 67.8% | 14.6% | 0.0% | 2.1% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 18.3% | 31.1% | 52.1% | 10.2% | 10.3% | 4.4% |
| vocab_grammar_coverage_cognitive | 0.0% | 20.4% | 38.3% | 36.6% | 41.7% | 11.9% | 15.3% | 15.6% |
| all_new | 0.0% | 20.4% | 38.3% | 36.1% | 41.7% | 11.9% | 15.3% | 13.3% |
| original_all | 0.0% | 0.0% | 15.0% | 49.7% | 50.0% | 10.2% | 0.6% | 0.0% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 56.7% | 86.9% | 66.7% | 1.7% | 13.5% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 58.3% | 95.6% | 70.8% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 1.0% | 36.7% | 63.9% | 83.3% | 8.5% | 19.7% | 4.4% |
| grammar_manual | 0.0% | 0.0% | 28.3% | 95.1% | 66.7% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 38.3% | 96.2% | 68.8% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 2.0% | 28.3% | 76.5% | 91.7% | 25.4% | 4.1% | 4.4% |
| grammar_all | 0.0% | 2.0% | 28.3% | 76.5% | 91.7% | 25.4% | 4.1% | 4.4% |
| cognitive | 0.0% | 0.0% | 55.0% | 80.9% | 60.4% | 3.4% | 3.8% | 2.2% |
| vocab_grammar_coverage | 0.0% | 1.0% | 31.7% | 66.1% | 85.4% | 35.6% | 25.0% | 17.8% |
| vocab_grammar_coverage_cognitive | 0.0% | 43.9% | 66.7% | 68.3% | 66.7% | 35.6% | 35.0% | 28.9% |
| all_new | 0.0% | 43.9% | 66.7% | 67.8% | 66.7% | 35.6% | 35.0% | 28.9% |
| original_all | 0.0% | 0.0% | 36.7% | 83.6% | 89.6% | 25.4% | 4.1% | 6.7% |

### test, ridge regression: confusion matrix: surface

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 3 | 15 | 11 | 1 | 0 | 1 | 0 | 1 |
| 2 | 0 | 0 | 0 | 5 | 71 | 20 | 2 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 3 | 14 | 36 | 6 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 10 | 86 | 83 | 4 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 3 | 30 | 15 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 21 | 31 | 4 | 1 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 29 | 131 | 87 | 51 | 25 | 17 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 29 | 10 | 0 | 0 |

### test, ridge regression: confusion matrix: original_vocab_bins

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 3 | 26 | 3 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 9 | 82 | 7 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 10 | 42 | 8 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 1 | 148 | 29 | 5 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 4 | 38 | 6 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 39 | 19 | 1 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 252 | 84 | 3 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 31 | 14 | 0 | 0 | 0 | 0 |

### test, ridge regression: confusion matrix: vocab

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 5 | 9 | 10 | 5 | 1 | 2 | 0 | 0 |
| 2 | 0 | 0 | 0 | 1 | 46 | 43 | 8 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 15 | 15 | 23 | 7 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 1 | 9 | 57 | 92 | 22 | 2 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 17 | 25 | 6 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 11 | 29 | 15 | 3 | 0 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 16 | 85 | 116 | 73 | 27 | 22 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 20 | 19 | 5 | 0 |

### test, ridge regression: confusion matrix: grammar_manual

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 12 | 16 | 3 | 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 1 | 35 | 58 | 4 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 7 | 35 | 17 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 11 | 146 | 25 | 1 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 2 | 32 | 14 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 30 | 29 | 0 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 185 | 149 | 5 | 1 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 3 | 30 | 12 | 0 | 0 | 0 |

### test, ridge regression: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 2 | 24 | 6 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 22 | 67 | 9 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 9 | 43 | 8 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 10 | 136 | 36 | 1 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 3 | 33 | 12 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 27 | 32 | 0 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 241 | 94 | 4 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 8 | 34 | 3 | 0 | 0 | 0 |

### test, ridge regression: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 12 | 10 | 5 | 1 | 1 | 1 | 0 |
| 2 | 0 | 0 | 0 | 12 | 47 | 27 | 9 | 2 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 3 | 9 | 19 | 26 | 2 | 0 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 1 | 9 | 76 | 83 | 13 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 1 | 18 | 24 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 27 | 20 | 7 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 19 | 151 | 139 | 23 | 6 | 2 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 20 | 12 | 0 |

### test, ridge regression: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 12 | 10 | 5 | 1 | 1 | 1 | 0 |
| 2 | 0 | 0 | 0 | 12 | 46 | 28 | 9 | 2 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 3 | 9 | 19 | 26 | 2 | 0 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 1 | 9 | 76 | 84 | 12 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 1 | 18 | 24 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 27 | 20 | 7 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 19 | 150 | 141 | 23 | 5 | 2 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 21 | 12 | 0 |

### test, ridge regression: confusion matrix: cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 11 | 17 | 1 | 0 | 2 | 0 | 1 |
| 2 | 0 | 0 | 0 | 0 | 6 | 68 | 22 | 2 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 6 | 46 | 8 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 5 | 46 | 124 | 8 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 1 | 39 | 7 | 1 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 20 | 35 | 4 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 8 | 104 | 135 | 72 | 12 | 7 | 2 |
| 6 | 0 | 0 | 0 | 0 | 0 | 14 | 26 | 2 | 1 | 2 | 0 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 7 | 8 | 10 | 2 | 4 | 1 | 0 | 0 |
| 2 | 0 | 0 | 0 | 11 | 47 | 29 | 10 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 2 | 11 | 24 | 20 | 2 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 18 | 57 | 85 | 19 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 18 | 25 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 6 | 21 | 23 | 6 | 2 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 3 | 50 | 118 | 111 | 35 | 23 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 21 | 14 | 2 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 10 | 4 | 12 | 3 | 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 20 | 51 | 21 | 3 | 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 3 | 5 | 23 | 23 | 5 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 20 | 67 | 74 | 19 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 20 | 20 | 2 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 23 | 22 | 7 | 3 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 4 | 36 | 101 | 121 | 52 | 26 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 20 | 15 | 7 |

### test, ridge regression: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 10 | 4 | 12 | 3 | 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 20 | 51 | 21 | 3 | 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 3 | 5 | 23 | 23 | 5 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 21 | 66 | 74 | 19 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 20 | 20 | 2 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 23 | 22 | 7 | 3 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 4 | 36 | 101 | 121 | 52 | 26 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 20 | 16 | 6 |

### test, ridge regression: confusion matrix: original_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 3 | 14 | 7 | 5 | 2 | 1 | 0 | 0 |
| 2 | 0 | 0 | 0 | 6 | 43 | 40 | 7 | 1 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 5 | 9 | 19 | 24 | 2 | 0 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 12 | 91 | 71 | 6 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 1 | 18 | 24 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 20 | 28 | 6 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 37 | 157 | 111 | 32 | 2 | 1 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 23 | 10 | 0 |

## valid (native): ridge regression

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.944 | [0.877, 1.012] | 13.3% | 30.0% | 11.1% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.273 | [1.183, 1.364] | 19.0% | 28.9% | 13.2% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.922 | [0.861, 0.986] | 12.9% | 28.1% | 16.5% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 1.185 | [1.102, 1.268] | 19.4% | 25.9% | 17.5% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 1.224 | [1.130, 1.314] | 22.8% | 30.0% | 19.3% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.969 | [0.902, 1.036] | 14.8% | 26.6% | 16.0% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.968 | [0.901, 1.035] | 14.8% | 26.6% | 16.0% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 1.190 | [1.111, 1.269] | 11.0% | 20.5% | 6.9% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.829 | [0.771, 0.888] | 14.1% | 30.4% | 15.6% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.682 | [0.628, 0.736] | 20.9% | 39.2% | 25.5% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.682 | [0.628, 0.736] | 20.9% | 39.2% | 25.5% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.976 | [0.910, 1.044] | 14.1% | 29.3% | 15.3% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | | 23.6% | 34.2% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.49 | 1.16 | 0.42 | 0.31 | 0.39 | 1.08 | 1.24 | 1.59 |
| original_vocab_bins | 1.96 | 1.43 | 0.48 | 0.20 | 0.39 | 1.36 | 1.87 | 2.32 |
| vocab | 1.56 | 1.35 | 0.68 | 0.48 | 0.30 | 0.81 | 1.06 | 1.22 |
| grammar_manual | 1.89 | 1.30 | 0.57 | 0.21 | 0.35 | 1.32 | 1.73 | 1.91 |
| grammar_rarity | 2.00 | 1.43 | 0.47 | 0.17 | 0.27 | 1.15 | 1.83 | 2.13 |
| grammar_coverage | 1.77 | 1.24 | 0.66 | 0.35 | 0.23 | 0.79 | 1.28 | 1.15 |
| grammar_all | 1.77 | 1.24 | 0.66 | 0.35 | 0.23 | 0.79 | 1.28 | 1.15 |
| cognitive | 1.77 | 1.55 | 0.47 | 0.36 | 0.48 | 1.18 | 1.60 | 2.09 |
| vocab_grammar_coverage | 1.57 | 1.26 | 0.59 | 0.48 | 0.27 | 0.79 | 0.90 | 1.00 |
| vocab_grammar_coverage_cognitive | 1.45 | 0.61 | 0.34 | 0.47 | 0.29 | 0.69 | 0.80 | 0.84 |
| all_new | 1.45 | 0.61 | 0.34 | 0.47 | 0.29 | 0.69 | 0.80 | 0.84 |
| original_all | 1.70 | 1.29 | 0.60 | 0.33 | 0.29 | 0.77 | 1.32 | 1.16 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 17.6% | 38.7% | 27.3% | 0.0% | 4.9% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 23.5% | 72.6% | 9.1% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 11.8% | 24.2% | 63.6% | 26.7% | 5.9% | 0.0% |
| grammar_manual | 0.0% | 0.0% | 17.6% | 67.7% | 54.5% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 17.6% | 82.3% | 54.5% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 11.8% | 45.2% | 63.6% | 6.7% | 1.0% | 0.0% |
| grammar_all | 0.0% | 0.0% | 11.8% | 45.2% | 63.6% | 6.7% | 1.0% | 0.0% |
| cognitive | 0.0% | 0.0% | 11.8% | 43.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 11.8% | 32.3% | 54.5% | 20.0% | 5.9% | 0.0% |
| vocab_grammar_coverage_cognitive | 0.0% | 13.8% | 52.9% | 32.3% | 72.7% | 13.3% | 10.8% | 8.3% |
| all_new | 0.0% | 13.8% | 52.9% | 32.3% | 72.7% | 13.3% | 10.8% | 8.3% |
| original_all | 0.0% | 0.0% | 17.6% | 43.5% | 54.5% | 6.7% | 0.0% | 0.0% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 58.8% | 80.6% | 63.6% | 6.7% | 10.8% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 58.8% | 90.3% | 90.9% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 41.2% | 62.9% | 81.8% | 26.7% | 13.7% | 8.3% |
| grammar_manual | 0.0% | 0.0% | 35.3% | 90.3% | 54.5% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 58.8% | 96.8% | 81.8% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 41.2% | 72.6% | 90.9% | 26.7% | 3.9% | 0.0% |
| grammar_all | 0.0% | 0.0% | 41.2% | 72.6% | 90.9% | 26.7% | 3.9% | 0.0% |
| cognitive | 0.0% | 0.0% | 58.8% | 56.5% | 72.7% | 0.0% | 1.0% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 47.1% | 59.7% | 81.8% | 20.0% | 21.6% | 8.3% |
| vocab_grammar_coverage_cognitive | 0.0% | 48.3% | 70.6% | 54.8% | 81.8% | 33.3% | 25.5% | 25.0% |
| all_new | 0.0% | 48.3% | 70.6% | 54.8% | 81.8% | 33.3% | 25.5% | 25.0% |
| original_all | 0.0% | 3.4% | 64.7% | 82.3% | 72.7% | 33.3% | 1.0% | 0.0% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.473 | [0.445, 0.506] | 47.2% | 64.4% | 42.0% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.966 | [0.921, 1.013] | 17.6% | 32.6% | 15.8% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.539 | [0.505, 0.575] | 37.0% | 59.2% | 31.7% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 0.942 | [0.902, 0.981] | 12.7% | 28.2% | 12.3% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 0.953 | [0.911, 0.997] | 17.0% | 32.5% | 13.4% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.549 | [0.516, 0.583] | 36.6% | 59.8% | 29.7% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.553 | [0.521, 0.588] | 36.2% | 57.1% | 27.6% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.507 | [0.473, 0.542] | 42.7% | 64.2% | 32.3% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.452 | [0.423, 0.486] | 46.5% | 68.9% | 36.6% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.333 | [0.310, 0.358] | 57.1% | 79.7% | 47.0% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.341 | [0.319, 0.365] | 54.6% | 79.5% | 44.3% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.493 | [0.463, 0.524] | 41.4% | 63.1% | 34.5% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | | 21.2% | 33.6% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.12 | 0.28 | 0.46 | 0.27 | 0.54 | 0.75 | 0.51 | 0.52 |
| original_vocab_bins | 2.05 | 1.61 | 0.65 | 0.54 | 0.48 | 0.84 | 0.93 | 1.90 |
| vocab | 1.49 | 0.75 | 0.69 | 0.36 | 0.38 | 0.53 | 0.48 | 0.54 |
| grammar_manual | 1.83 | 1.20 | 1.00 | 0.52 | 0.57 | 0.94 | 1.00 | 1.36 |
| grammar_rarity | 2.14 | 1.40 | 0.69 | 0.41 | 0.56 | 0.85 | 1.03 | 1.66 |
| grammar_coverage | 1.33 | 0.75 | 0.69 | 0.39 | 0.45 | 0.63 | 0.47 | 0.57 |
| grammar_all | 1.32 | 0.78 | 0.70 | 0.38 | 0.48 | 0.62 | 0.47 | 0.61 |
| cognitive | 1.21 | 0.36 | 0.44 | 0.22 | 0.75 | 0.45 | 0.54 | 1.14 |
| vocab_grammar_coverage | 1.42 | 0.72 | 0.63 | 0.29 | 0.40 | 0.46 | 0.35 | 0.40 |
| vocab_grammar_coverage_cognitive | 1.07 | 0.35 | 0.33 | 0.23 | 0.45 | 0.35 | 0.29 | 0.37 |
| all_new | 1.09 | 0.37 | 0.34 | 0.23 | 0.47 | 0.35 | 0.29 | 0.39 |
| original_all | 1.17 | 0.68 | 0.51 | 0.30 | 0.46 | 0.53 | 0.47 | 0.58 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 6.2% | 61.2% | 45.0% | 63.4% | 39.6% | 22.0% | 42.9% | 55.6% |
| original_vocab_bins | 0.0% | 0.0% | 35.0% | 25.7% | 31.2% | 16.9% | 17.4% | 0.0% |
| vocab | 15.6% | 24.5% | 25.0% | 42.6% | 41.7% | 30.5% | 42.9% | 31.1% |
| grammar_manual | 0.0% | 0.0% | 23.3% | 29.0% | 27.1% | 11.9% | 6.8% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 21.7% | 36.1% | 20.8% | 11.9% | 14.7% | 2.2% |
| grammar_coverage | 21.9% | 26.5% | 26.7% | 44.3% | 29.2% | 25.4% | 43.8% | 20.0% |
| grammar_all | 21.9% | 21.4% | 23.3% | 46.4% | 25.0% | 16.9% | 45.6% | 20.0% |
| cognitive | 0.0% | 46.9% | 26.7% | 70.5% | 18.8% | 45.8% | 40.6% | 8.9% |
| vocab_grammar_coverage | 6.2% | 30.6% | 28.3% | 56.3% | 31.2% | 37.3% | 56.5% | 46.7% |
| vocab_grammar_coverage_cognitive | 18.8% | 53.1% | 41.7% | 67.2% | 35.4% | 50.8% | 65.0% | 44.4% |
| all_new | 18.8% | 45.9% | 50.0% | 66.1% | 25.0% | 44.1% | 62.6% | 42.2% |
| original_all | 21.9% | 24.5% | 33.3% | 59.0% | 35.4% | 37.3% | 44.4% | 20.0% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 18.8% | 82.7% | 55.0% | 83.1% | 54.2% | 35.6% | 61.5% | 64.4% |
| original_vocab_bins | 0.0% | 1.0% | 55.0% | 54.1% | 52.1% | 27.1% | 31.8% | 0.0% |
| vocab | 18.8% | 44.9% | 45.0% | 76.0% | 66.7% | 55.9% | 61.2% | 51.1% |
| grammar_manual | 0.0% | 2.0% | 33.3% | 60.7% | 43.8% | 22.0% | 22.1% | 4.4% |
| grammar_rarity | 0.0% | 2.0% | 41.7% | 68.9% | 54.2% | 22.0% | 25.3% | 6.7% |
| grammar_coverage | 25.0% | 39.8% | 40.0% | 72.1% | 64.6% | 50.8% | 67.4% | 53.3% |
| grammar_all | 25.0% | 38.8% | 41.7% | 68.3% | 54.2% | 54.2% | 65.0% | 42.2% |
| cognitive | 21.9% | 75.5% | 60.0% | 87.4% | 39.6% | 74.6% | 60.9% | 17.8% |
| vocab_grammar_coverage | 21.9% | 42.9% | 50.0% | 83.6% | 64.6% | 61.0% | 77.9% | 71.1% |
| vocab_grammar_coverage_cognitive | 37.5% | 78.6% | 81.7% | 90.7% | 66.7% | 72.9% | 82.6% | 64.4% |
| all_new | 40.6% | 74.5% | 78.3% | 90.2% | 68.8% | 76.3% | 82.9% | 66.7% |
| original_all | 31.2% | 45.9% | 58.3% | 79.2% | 54.2% | 59.3% | 67.4% | 46.7% |

### test, gradient boosting: confusion matrix: surface

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 2 | 11 | 8 | 4 | 4 | 2 | 1 | 0 | 0 | 0 |
| 2 | 0 | 2 | 60 | 25 | 10 | 1 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 9 | 15 | 27 | 2 | 5 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 2 | 3 | 14 | 116 | 37 | 10 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 4 | 9 | 11 | 19 | 4 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 1 | 1 | 7 | 17 | 14 | 13 | 5 | 1 |
| 5.5 | 0 | 0 | 0 | 1 | 4 | 8 | 16 | 66 | 95 | 146 | 4 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 8 | 6 | 25 |

### test, gradient boosting: confusion matrix: original_vocab_bins

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 13 | 4 | 9 | 1 | 3 | 0 | 0 |
| 2 | 0 | 0 | 0 | 7 | 27 | 21 | 25 | 16 | 2 | 0 | 0 |
| 3 | 0 | 0 | 0 | 4 | 21 | 13 | 11 | 8 | 3 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 1 | 44 | 47 | 39 | 44 | 7 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 12 | 14 | 15 | 6 | 0 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 5 | 8 | 17 | 18 | 10 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 1 | 10 | 32 | 57 | 89 | 89 | 59 | 3 |
| 6 | 0 | 0 | 0 | 0 | 2 | 14 | 10 | 12 | 6 | 1 | 0 |

### test, gradient boosting: confusion matrix: vocab

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 5 | 2 | 7 | 5 | 6 | 4 | 1 | 0 | 2 | 0 |
| 2 | 0 | 1 | 24 | 33 | 25 | 4 | 7 | 4 | 0 | 0 | 0 |
| 3 | 0 | 0 | 3 | 7 | 15 | 14 | 10 | 9 | 2 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 21 | 78 | 67 | 14 | 2 | 1 | 0 |
| 4 | 0 | 0 | 0 | 0 | 2 | 13 | 20 | 9 | 4 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 4 | 9 | 21 | 18 | 6 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 6 | 21 | 56 | 106 | 146 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 9 | 19 | 14 |

### test, gradient boosting: confusion matrix: grammar_manual

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 5 | 11 | 6 | 3 | 1 | 4 | 0 | 0 |
| 2 | 0 | 0 | 0 | 18 | 46 | 20 | 8 | 3 | 2 | 1 | 0 |
| 3 | 0 | 0 | 0 | 1 | 14 | 10 | 12 | 11 | 7 | 5 | 0 |
| 3.5 | 0 | 0 | 1 | 6 | 52 | 53 | 37 | 19 | 14 | 1 | 0 |
| 4 | 0 | 0 | 0 | 2 | 11 | 16 | 13 | 4 | 2 | 0 | 0 |
| 5 | 0 | 0 | 0 | 1 | 2 | 11 | 27 | 9 | 7 | 2 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 11 | 36 | 53 | 106 | 111 | 23 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 1 | 14 | 11 | 13 | 6 | 0 |

### test, gradient boosting: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 1 | 8 | 11 | 7 | 4 | 1 | 0 | 0 |
| 2 | 0 | 0 | 0 | 10 | 35 | 28 | 16 | 8 | 1 | 0 | 0 |
| 3 | 0 | 0 | 0 | 5 | 13 | 14 | 21 | 6 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 4 | 50 | 66 | 43 | 18 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 2 | 12 | 18 | 10 | 6 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 10 | 24 | 16 | 7 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 1 | 9 | 40 | 86 | 77 | 77 | 50 | 0 |
| 6 | 0 | 0 | 0 | 0 | 1 | 5 | 14 | 14 | 8 | 2 | 1 |

### test, gradient boosting: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 7 | 4 | 4 | 3 | 7 | 3 | 1 | 1 | 1 | 0 |
| 2 | 0 | 1 | 26 | 32 | 19 | 9 | 8 | 3 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 1 | 16 | 19 | 14 | 8 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 10 | 30 | 81 | 40 | 17 | 5 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 5 | 22 | 14 | 3 | 3 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 4 | 4 | 10 | 22 | 15 | 4 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 7 | 22 | 49 | 86 | 149 | 26 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 7 | 25 | 9 |

### test, gradient boosting: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 7 | 3 | 5 | 5 | 6 | 2 | 1 | 2 | 0 | 0 |
| 2 | 0 | 4 | 21 | 30 | 24 | 10 | 7 | 1 | 1 | 0 | 0 |
| 3 | 0 | 0 | 1 | 1 | 14 | 21 | 15 | 6 | 2 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 9 | 30 | 85 | 39 | 16 | 4 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 6 | 24 | 12 | 3 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 3 | 5 | 10 | 23 | 10 | 8 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 8 | 15 | 56 | 83 | 155 | 22 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 11 | 23 | 9 |

### test, gradient boosting: confusion matrix: cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 12 | 5 | 8 | 4 | 3 | 0 | 0 | 0 | 0 |
| 2 | 0 | 3 | 46 | 39 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 6 | 30 | 16 | 5 | 3 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 4 | 31 | 129 | 15 | 3 | 0 | 0 | 0 |
| 4 | 0 | 0 | 1 | 9 | 9 | 8 | 9 | 8 | 4 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 4 | 5 | 11 | 27 | 10 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 2 | 14 | 25 | 45 | 115 | 138 | 1 |
| 6 | 0 | 0 | 0 | 0 | 0 | 4 | 6 | 6 | 15 | 10 | 4 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 5 | 2 | 4 | 5 | 5 | 4 | 3 | 3 | 1 | 0 | 0 |
| 2 | 0 | 1 | 30 | 28 | 18 | 14 | 3 | 4 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 5 | 17 | 14 | 18 | 4 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 28 | 103 | 40 | 10 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 1 | 22 | 15 | 8 | 2 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 2 | 10 | 20 | 22 | 5 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 1 | 12 | 33 | 93 | 192 | 9 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 18 | 21 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 5 | 6 | 3 | 3 | 8 | 5 | 2 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 52 | 33 | 9 | 3 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 1 | 15 | 25 | 15 | 3 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 24 | 123 | 28 | 3 | 2 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 5 | 20 | 17 | 2 | 3 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 13 | 30 | 10 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 11 | 20 | 81 | 221 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 18 | 20 |

### test, gradient boosting: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 3 | 6 | 5 | 1 | 8 | 8 | 1 | 0 | 0 | 0 | 0 |
| 2 | 0 | 1 | 45 | 37 | 11 | 3 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 1 | 13 | 30 | 11 | 4 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 24 | 121 | 31 | 4 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 6 | 24 | 12 | 4 | 1 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 15 | 26 | 12 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 10 | 21 | 87 | 213 | 7 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 6 | 19 | 19 |

### test, gradient boosting: confusion matrix: original_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 2 | 7 | 4 | 8 | 2 | 4 | 3 | 0 | 2 | 0 | 0 |
| 2 | 0 | 2 | 24 | 36 | 21 | 10 | 3 | 2 | 0 | 0 | 0 |
| 3 | 0 | 1 | 0 | 4 | 20 | 22 | 8 | 4 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 9 | 27 | 108 | 33 | 4 | 1 | 1 | 0 |
| 4 | 0 | 0 | 0 | 0 | 9 | 16 | 17 | 5 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 4 | 11 | 16 | 22 | 5 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 10 | 19 | 38 | 108 | 151 | 14 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 8 | 25 | 9 |

## valid (native): gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.540 | [0.472, 0.604] | 43.3% | 59.7% | 37.6% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.898 | [0.818, 0.978] | 19.0% | 36.9% | 18.4% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.598 | [0.536, 0.666] | 32.7% | 56.7% | 27.8% |
| grammar_manual | grammar: share of concept occurrences per CEFR level (Revita's manual levels) | 8 | 0.944 | [0.871, 1.012] | 9.9% | 25.1% | 8.1% |
| grammar_rarity | grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF) | 9 | 0.968 | [0.890, 1.047] | 15.2% | 29.7% | 15.1% |
| grammar_coverage | grammar: the share of every concept in the text (one feature each) | 268 | 0.544 | [0.490, 0.602] | 33.1% | 58.9% | 23.6% |
| grammar_all | grammar: manual levels, rarity and coverage together | 285 | 0.536 | [0.477, 0.596] | 36.9% | 58.6% | 31.2% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.521 | [0.456, 0.595] | 41.4% | 64.3% | 36.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 304 | 0.476 | [0.425, 0.526] | 36.9% | 63.1% | 32.2% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 311 | 0.364 | [0.315, 0.414] | 51.7% | 76.8% | 43.7% |
| all_new | every new feature: vocab, all grammar, cognitive | 328 | 0.377 | [0.326, 0.430] | 50.6% | 71.5% | 41.1% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.506 | [0.452, 0.559] | 38.4% | 55.9% | 32.2% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | | 23.6% | 34.2% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.99 | 0.32 | 0.44 | 0.27 | 0.47 | 0.85 | 0.67 | 0.56 |
| original_vocab_bins | 1.81 | 1.59 | 0.56 | 0.45 | 0.30 | 0.65 | 0.90 | 1.76 |
| vocab | 1.24 | 0.78 | 0.73 | 0.42 | 0.38 | 0.50 | 0.58 | 0.60 |
| grammar_manual | 1.82 | 1.19 | 0.73 | 0.54 | 0.88 | 0.94 | 0.96 | 1.55 |
| grammar_rarity | 2.05 | 1.39 | 0.56 | 0.43 | 0.61 | 0.63 | 1.10 | 1.51 |
| grammar_coverage | 1.16 | 0.89 | 0.45 | 0.33 | 0.59 | 0.58 | 0.48 | 0.63 |
| grammar_all | 1.19 | 0.83 | 0.44 | 0.35 | 0.45 | 0.49 | 0.48 | 0.70 |
| cognitive | 1.03 | 0.38 | 0.34 | 0.24 | 0.64 | 0.33 | 0.61 | 1.30 |
| vocab_grammar_coverage | 1.14 | 0.73 | 0.42 | 0.35 | 0.36 | 0.47 | 0.40 | 0.52 |
| vocab_grammar_coverage_cognitive | 0.96 | 0.40 | 0.29 | 0.28 | 0.37 | 0.46 | 0.31 | 0.41 |
| all_new | 0.99 | 0.41 | 0.35 | 0.30 | 0.38 | 0.46 | 0.31 | 0.40 |
| original_all | 1.02 | 0.71 | 0.52 | 0.30 | 0.42 | 0.43 | 0.50 | 0.64 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 20.0% | 62.1% | 35.3% | 66.1% | 27.3% | 13.3% | 35.3% | 41.7% |
| original_vocab_bins | 0.0% | 0.0% | 47.1% | 32.3% | 45.5% | 6.7% | 15.7% | 0.0% |
| vocab | 6.7% | 20.7% | 11.8% | 35.5% | 36.4% | 20.0% | 41.2% | 50.0% |
| grammar_manual | 0.0% | 0.0% | 29.4% | 24.2% | 0.0% | 6.7% | 4.9% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 35.3% | 33.9% | 18.2% | 26.7% | 6.9% | 0.0% |
| grammar_coverage | 6.7% | 10.3% | 35.3% | 48.4% | 18.2% | 13.3% | 40.2% | 16.7% |
| grammar_all | 13.3% | 17.2% | 35.3% | 46.8% | 36.4% | 33.3% | 42.2% | 25.0% |
| cognitive | 20.0% | 34.5% | 52.9% | 61.3% | 36.4% | 53.3% | 36.3% | 0.0% |
| vocab_grammar_coverage | 0.0% | 17.2% | 35.3% | 41.9% | 27.3% | 33.3% | 44.1% | 58.3% |
| vocab_grammar_coverage_cognitive | 13.3% | 34.5% | 52.9% | 61.3% | 36.4% | 33.3% | 59.8% | 58.3% |
| all_new | 13.3% | 37.9% | 41.2% | 53.2% | 36.4% | 33.3% | 63.7% | 50.0% |
| original_all | 13.3% | 20.7% | 29.4% | 58.1% | 36.4% | 53.3% | 38.2% | 8.3% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 26.7% | 72.4% | 58.8% | 87.1% | 63.6% | 20.0% | 49.0% | 66.7% |
| original_vocab_bins | 0.0% | 3.4% | 58.8% | 67.7% | 72.7% | 46.7% | 28.4% | 0.0% |
| vocab | 20.0% | 51.7% | 35.3% | 64.5% | 81.8% | 53.3% | 59.8% | 58.3% |
| grammar_manual | 0.0% | 6.9% | 41.2% | 51.6% | 9.1% | 26.7% | 18.6% | 8.3% |
| grammar_rarity | 0.0% | 0.0% | 47.1% | 59.7% | 45.5% | 53.3% | 18.6% | 8.3% |
| grammar_coverage | 13.3% | 37.9% | 64.7% | 79.0% | 54.5% | 53.3% | 60.8% | 50.0% |
| grammar_all | 20.0% | 41.4% | 52.9% | 71.0% | 72.7% | 60.0% | 62.7% | 41.7% |
| cognitive | 26.7% | 75.9% | 64.7% | 87.1% | 36.4% | 80.0% | 59.8% | 8.3% |
| vocab_grammar_coverage | 13.3% | 37.9% | 64.7% | 77.4% | 72.7% | 46.7% | 69.6% | 66.7% |
| vocab_grammar_coverage_cognitive | 20.0% | 69.0% | 82.4% | 85.5% | 81.8% | 66.7% | 82.4% | 75.0% |
| all_new | 20.0% | 69.0% | 64.7% | 80.6% | 72.7% | 60.0% | 76.5% | 75.0% |
| original_all | 13.3% | 34.5% | 52.9% | 80.6% | 45.5% | 73.3% | 53.9% | 41.7% |

## Paired MAE differences (first minus second; negative = the first is better)

Bootstrap over the evaluation texts (1,000 resamples, the same resamples for both models). A 95% interval that does not contain 0 is a difference larger than noise.

### test, ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | -0.026 | [-0.044, -0.006] * |
| grammar_coverage | surface | +0.023 | [-0.014, +0.058] |
| cognitive | surface | +0.227 | [+0.198, +0.256] * |
| grammar_coverage | grammar_manual | -0.262 | [-0.291, -0.233] * |
| grammar_coverage | grammar_rarity | -0.306 | [-0.339, -0.273] * |
| grammar_all | grammar_coverage | -0.001 | [-0.001, -0.000] * |
| vocab_grammar_coverage | vocab | -0.115 | [-0.132, -0.098] * |
| vocab_grammar_coverage | original_all | -0.176 | [-0.207, -0.145] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.144 | [-0.165, -0.124] * |
| vocab_grammar_coverage_cognitive | original_all | -0.319 | [-0.353, -0.287] * |
| all_new | vocab_grammar_coverage_cognitive | -0.000 | [-0.000, -0.000] * |
| all_new | original_all | -0.320 | [-0.353, -0.287] * |
| vocab | original_vocab_bins | -0.378 | [-0.420, -0.334] * |
| original_all | surface | +0.035 | [-0.003, +0.072] |
| vocab_grammar_coverage_cognitive | surface | -0.285 | [-0.317, -0.254] * |
| all_new | surface | -0.285 | [-0.317, -0.254] * |

### valid (native), ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | -0.022 | [-0.057, +0.015] |
| grammar_coverage | surface | +0.026 | [-0.032, +0.085] |
| cognitive | surface | +0.247 | [+0.204, +0.289] * |
| grammar_coverage | grammar_manual | -0.214 | [-0.263, -0.166] * |
| grammar_coverage | grammar_rarity | -0.254 | [-0.314, -0.200] * |
| grammar_all | grammar_coverage | -0.001 | [-0.001, -0.000] * |
| vocab_grammar_coverage | vocab | -0.092 | [-0.122, -0.063] * |
| vocab_grammar_coverage | original_all | -0.146 | [-0.198, -0.094] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.148 | [-0.180, -0.112] * |
| vocab_grammar_coverage_cognitive | original_all | -0.294 | [-0.354, -0.239] * |
| all_new | vocab_grammar_coverage_cognitive | -0.000 | [-0.000, +0.000] |
| all_new | original_all | -0.294 | [-0.354, -0.239] * |
| vocab | original_vocab_bins | -0.350 | [-0.424, -0.281] * |
| original_all | surface | +0.032 | [-0.030, +0.096] |
| vocab_grammar_coverage_cognitive | surface | -0.262 | [-0.314, -0.209] * |
| all_new | surface | -0.262 | [-0.314, -0.209] * |

### test, gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.067 | [+0.031, +0.101] * |
| grammar_coverage | surface | +0.076 | [+0.040, +0.115] * |
| cognitive | surface | +0.033 | [+0.001, +0.067] * |
| grammar_coverage | grammar_manual | -0.393 | [-0.432, -0.356] * |
| grammar_coverage | grammar_rarity | -0.404 | [-0.448, -0.357] * |
| grammar_all | grammar_coverage | +0.004 | [-0.007, +0.013] |
| vocab_grammar_coverage | vocab | -0.088 | [-0.113, -0.062] * |
| vocab_grammar_coverage | original_all | -0.041 | [-0.064, -0.016] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.119 | [-0.142, -0.098] * |
| vocab_grammar_coverage_cognitive | original_all | -0.160 | [-0.181, -0.137] * |
| all_new | vocab_grammar_coverage_cognitive | +0.008 | [-0.000, +0.016] |
| all_new | original_all | -0.152 | [-0.173, -0.129] * |
| vocab | original_vocab_bins | -0.426 | [-0.473, -0.381] * |
| original_all | surface | +0.020 | [-0.017, +0.055] |
| vocab_grammar_coverage_cognitive | surface | -0.140 | [-0.168, -0.112] * |
| all_new | surface | -0.132 | [-0.162, -0.103] * |

### valid (native), gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.060 | [-0.012, +0.126] |
| grammar_coverage | surface | +0.006 | [-0.067, +0.079] |
| cognitive | surface | -0.019 | [-0.084, +0.045] |
| grammar_coverage | grammar_manual | -0.399 | [-0.456, -0.338] * |
| grammar_coverage | grammar_rarity | -0.424 | [-0.502, -0.351] * |
| grammar_all | grammar_coverage | -0.008 | [-0.028, +0.012] |
| vocab_grammar_coverage | vocab | -0.123 | [-0.172, -0.073] * |
| vocab_grammar_coverage | original_all | -0.030 | [-0.076, +0.012] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.112 | [-0.149, -0.076] * |
| vocab_grammar_coverage_cognitive | original_all | -0.142 | [-0.181, -0.102] * |
| all_new | vocab_grammar_coverage_cognitive | +0.013 | [-0.002, +0.027] |
| all_new | original_all | -0.130 | [-0.171, -0.091] * |
| vocab | original_vocab_bins | -0.298 | [-0.379, -0.219] * |
| original_all | surface | -0.033 | [-0.099, +0.038] |
| vocab_grammar_coverage_cognitive | surface | -0.175 | [-0.228, -0.121] * |
| all_new | surface | -0.162 | [-0.219, -0.106] * |

