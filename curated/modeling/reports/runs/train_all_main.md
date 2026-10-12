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
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 1.217 | [1.169, 1.261] | 18.6% | 26.0% | 13.8% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 1.249 | [1.199, 1.294] | 18.3% | 26.5% | 14.5% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.963 | [0.926, 1.000] | 15.4% | 27.1% | 16.0% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.962 | [0.925, 0.999] | 15.1% | 27.1% | 15.7% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 1.137 | [1.093, 1.185] | 16.6% | 26.1% | 11.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.777 | [0.744, 0.811] | 16.5% | 34.1% | 16.3% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.639 | [0.611, 0.669] | 21.6% | 45.3% | 21.4% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.639 | [0.611, 0.669] | 21.5% | 45.4% | 21.1% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.946 | [0.908, 0.982] | 15.3% | 28.9% | 15.7% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | | 21.2% | 33.6% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.82 | 1.11 | 0.47 | 0.29 | 0.38 | 1.14 | 1.15 | 1.44 |
| original_vocab_bins | 1.99 | 1.46 | 0.47 | 0.16 | 0.43 | 1.31 | 1.84 | 2.31 |
| vocab | 1.90 | 1.30 | 0.70 | 0.43 | 0.27 | 0.93 | 0.98 | 1.19 |
| grammar_manual | 1.92 | 1.34 | 0.59 | 0.17 | 0.44 | 1.31 | 1.78 | 2.00 |
| grammar_rarity | 2.04 | 1.42 | 0.50 | 0.18 | 0.42 | 1.25 | 1.83 | 2.14 |
| grammar_coverage | 1.95 | 1.26 | 0.68 | 0.32 | 0.27 | 0.78 | 1.29 | 1.13 |
| grammar_all | 1.95 | 1.26 | 0.68 | 0.32 | 0.27 | 0.78 | 1.29 | 1.13 |
| cognitive | 2.04 | 1.59 | 0.50 | 0.23 | 0.45 | 1.15 | 1.50 | 2.03 |
| vocab_grammar_coverage | 1.86 | 1.21 | 0.65 | 0.39 | 0.28 | 0.76 | 0.83 | 0.92 |
| vocab_grammar_coverage_cognitive | 1.61 | 0.59 | 0.37 | 0.36 | 0.41 | 0.70 | 0.76 | 0.82 |
| all_new | 1.61 | 0.59 | 0.37 | 0.36 | 0.41 | 0.70 | 0.76 | 0.82 |
| original_all | 1.91 | 1.29 | 0.68 | 0.29 | 0.27 | 0.70 | 1.28 | 1.06 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 23.3% | 47.0% | 31.2% | 1.7% | 7.4% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 16.7% | 80.9% | 12.5% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 25.0% | 31.1% | 52.1% | 5.1% | 7.9% | 0.0% |
| grammar_manual | 0.0% | 0.0% | 10.0% | 79.2% | 20.8% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 16.7% | 74.3% | 25.0% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 15.0% | 49.2% | 54.2% | 8.5% | 0.9% | 0.0% |
| grammar_all | 0.0% | 0.0% | 15.0% | 48.6% | 54.2% | 6.8% | 0.9% | 0.0% |
| cognitive | 0.0% | 0.0% | 10.0% | 67.8% | 14.6% | 0.0% | 2.1% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 20.0% | 34.4% | 54.2% | 6.8% | 10.6% | 4.4% |
| vocab_grammar_coverage_cognitive | 0.0% | 17.3% | 43.3% | 37.2% | 39.6% | 13.6% | 13.5% | 6.7% |
| all_new | 0.0% | 17.3% | 43.3% | 37.2% | 37.5% | 13.6% | 13.5% | 6.7% |
| original_all | 0.0% | 0.0% | 15.0% | 49.7% | 50.0% | 10.2% | 0.6% | 0.0% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 56.7% | 86.9% | 66.7% | 1.7% | 13.5% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 58.3% | 95.6% | 70.8% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 1.0% | 36.7% | 63.9% | 83.3% | 8.5% | 19.7% | 4.4% |
| grammar_manual | 0.0% | 0.0% | 26.7% | 97.8% | 62.5% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 40.0% | 96.2% | 60.4% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 1.0% | 35.0% | 80.9% | 87.5% | 20.3% | 2.6% | 2.2% |
| grammar_all | 0.0% | 1.0% | 35.0% | 80.9% | 87.5% | 20.3% | 2.6% | 2.2% |
| cognitive | 0.0% | 0.0% | 55.0% | 80.9% | 60.4% | 3.4% | 3.8% | 2.2% |
| vocab_grammar_coverage | 0.0% | 2.0% | 36.7% | 69.4% | 83.3% | 27.1% | 23.5% | 17.8% |
| vocab_grammar_coverage_cognitive | 0.0% | 44.9% | 73.3% | 71.6% | 66.7% | 35.6% | 31.5% | 28.9% |
| all_new | 0.0% | 44.9% | 73.3% | 72.1% | 66.7% | 35.6% | 31.5% | 28.9% |
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
| 1.5 | 0 | 0 | 0 | 0 | 10 | 18 | 4 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 25 | 69 | 4 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 6 | 39 | 14 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 20 | 145 | 17 | 1 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 3 | 35 | 10 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 35 | 24 | 0 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 214 | 120 | 5 | 1 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 8 | 34 | 3 | 0 | 0 | 0 |

### test, ridge regression: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 3 | 24 | 5 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 22 | 69 | 7 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 10 | 40 | 10 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 14 | 136 | 32 | 1 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 4 | 32 | 12 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 28 | 31 | 0 | 0 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 251 | 84 | 4 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 12 | 31 | 2 | 0 | 0 | 0 |

### test, ridge regression: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 13 | 10 | 5 | 0 | 1 | 1 | 0 |
| 2 | 0 | 0 | 0 | 9 | 48 | 30 | 8 | 2 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 2 | 9 | 22 | 22 | 4 | 0 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 8 | 90 | 69 | 13 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 18 | 26 | 4 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 6 | 27 | 20 | 5 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 25 | 175 | 118 | 18 | 3 | 1 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | 25 | 5 | 0 |

### test, ridge regression: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 2 | 13 | 10 | 5 | 0 | 1 | 1 | 0 |
| 2 | 0 | 0 | 0 | 9 | 48 | 30 | 8 | 2 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 2 | 9 | 22 | 22 | 4 | 0 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 9 | 89 | 69 | 13 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 18 | 26 | 4 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 7 | 26 | 21 | 4 | 1 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 25 | 173 | 119 | 19 | 3 | 1 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | 25 | 5 | 0 |

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
| 1.5 | 0 | 0 | 0 | 8 | 7 | 10 | 3 | 2 | 2 | 0 | 0 |
| 2 | 0 | 0 | 0 | 9 | 52 | 27 | 9 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 2 | 12 | 23 | 21 | 2 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 18 | 63 | 85 | 13 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 17 | 26 | 5 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 7 | 21 | 24 | 4 | 2 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 5 | 53 | 121 | 105 | 36 | 20 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 9 | 21 | 12 | 2 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 10 | 7 | 9 | 2 | 2 | 0 | 0 | 0 |
| 2 | 0 | 0 | 17 | 57 | 17 | 5 | 1 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 2 | 6 | 26 | 21 | 4 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 24 | 68 | 76 | 12 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 7 | 18 | 19 | 3 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 23 | 22 | 8 | 2 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 5 | 47 | 102 | 117 | 46 | 23 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 22 | 15 | 3 |

### test, ridge regression: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 2 | 10 | 7 | 9 | 2 | 2 | 0 | 0 | 0 |
| 2 | 0 | 0 | 17 | 57 | 17 | 5 | 1 | 1 | 0 | 0 | 0 |
| 3 | 0 | 0 | 2 | 6 | 26 | 21 | 4 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 24 | 68 | 76 | 12 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 7 | 19 | 18 | 3 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 23 | 22 | 8 | 2 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 5 | 48 | 101 | 117 | 46 | 23 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 22 | 15 | 3 |

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
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 1.196 | [1.109, 1.282] | 20.2% | 28.1% | 17.9% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 1.233 | [1.140, 1.324] | 22.1% | 30.0% | 18.9% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 1.004 | [0.937, 1.071] | 14.4% | 27.0% | 17.1% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 1.003 | [0.937, 1.071] | 14.4% | 27.0% | 17.1% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 1.190 | [1.111, 1.269] | 11.0% | 20.5% | 6.9% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.840 | [0.782, 0.900] | 15.6% | 28.9% | 17.4% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.697 | [0.643, 0.753] | 20.9% | 38.0% | 25.7% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.697 | [0.644, 0.753] | 20.9% | 37.6% | 25.7% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.976 | [0.910, 1.044] | 14.1% | 29.3% | 15.3% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | | 23.6% | 34.2% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.49 | 1.16 | 0.42 | 0.31 | 0.39 | 1.08 | 1.24 | 1.59 |
| original_vocab_bins | 1.96 | 1.43 | 0.48 | 0.20 | 0.39 | 1.36 | 1.87 | 2.32 |
| vocab | 1.56 | 1.35 | 0.68 | 0.48 | 0.30 | 0.81 | 1.06 | 1.22 |
| grammar_manual | 1.91 | 1.34 | 0.54 | 0.19 | 0.34 | 1.35 | 1.75 | 1.97 |
| grammar_rarity | 2.00 | 1.43 | 0.45 | 0.17 | 0.28 | 1.17 | 1.85 | 2.15 |
| grammar_coverage | 1.78 | 1.31 | 0.61 | 0.36 | 0.17 | 0.85 | 1.35 | 1.26 |
| grammar_all | 1.78 | 1.31 | 0.61 | 0.36 | 0.17 | 0.85 | 1.34 | 1.25 |
| cognitive | 1.77 | 1.55 | 0.47 | 0.36 | 0.48 | 1.18 | 1.60 | 2.09 |
| vocab_grammar_coverage | 1.56 | 1.28 | 0.56 | 0.46 | 0.23 | 0.80 | 0.94 | 1.04 |
| vocab_grammar_coverage_cognitive | 1.44 | 0.63 | 0.31 | 0.45 | 0.27 | 0.70 | 0.84 | 0.92 |
| all_new | 1.44 | 0.63 | 0.31 | 0.45 | 0.27 | 0.70 | 0.84 | 0.92 |
| original_all | 1.70 | 1.29 | 0.60 | 0.33 | 0.29 | 0.77 | 1.32 | 1.16 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 17.6% | 38.7% | 27.3% | 0.0% | 4.9% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 23.5% | 72.6% | 9.1% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 11.8% | 24.2% | 63.6% | 26.7% | 5.9% | 0.0% |
| grammar_manual | 0.0% | 0.0% | 17.6% | 71.0% | 54.5% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 17.6% | 79.0% | 54.5% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 11.8% | 43.5% | 81.8% | 0.0% | 0.0% | 0.0% |
| grammar_all | 0.0% | 0.0% | 11.8% | 43.5% | 81.8% | 0.0% | 0.0% | 0.0% |
| cognitive | 0.0% | 0.0% | 11.8% | 43.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 11.8% | 38.7% | 63.6% | 20.0% | 4.9% | 0.0% |
| vocab_grammar_coverage_cognitive | 0.0% | 10.3% | 58.8% | 35.5% | 63.6% | 20.0% | 8.8% | 8.3% |
| all_new | 0.0% | 10.3% | 58.8% | 35.5% | 63.6% | 20.0% | 8.8% | 8.3% |
| original_all | 0.0% | 0.0% | 17.6% | 43.5% | 54.5% | 6.7% | 0.0% | 0.0% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.0% | 0.0% | 58.8% | 80.6% | 63.6% | 6.7% | 10.8% | 0.0% |
| original_vocab_bins | 0.0% | 0.0% | 58.8% | 90.3% | 90.9% | 0.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 41.2% | 62.9% | 81.8% | 26.7% | 13.7% | 8.3% |
| grammar_manual | 0.0% | 0.0% | 52.9% | 93.5% | 63.6% | 0.0% | 0.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 58.8% | 96.8% | 81.8% | 0.0% | 0.0% | 0.0% |
| grammar_coverage | 0.0% | 0.0% | 47.1% | 72.6% | 100.0% | 26.7% | 2.9% | 0.0% |
| grammar_all | 0.0% | 0.0% | 47.1% | 72.6% | 100.0% | 26.7% | 2.9% | 0.0% |
| cognitive | 0.0% | 0.0% | 58.8% | 56.5% | 72.7% | 0.0% | 1.0% | 0.0% |
| vocab_grammar_coverage | 0.0% | 0.0% | 47.1% | 59.7% | 81.8% | 20.0% | 18.6% | 0.0% |
| vocab_grammar_coverage_cognitive | 0.0% | 48.3% | 76.5% | 59.7% | 81.8% | 33.3% | 19.6% | 16.7% |
| all_new | 0.0% | 48.3% | 76.5% | 58.1% | 81.8% | 33.3% | 19.6% | 16.7% |
| original_all | 0.0% | 3.4% | 64.7% | 82.3% | 72.7% | 33.3% | 1.0% | 0.0% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| surface | surface measures: words, characters, mean word length, mean sentence length | 4 | 0.473 | [0.445, 0.506] | 47.2% | 64.4% | 42.0% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.966 | [0.921, 1.013] | 17.6% | 32.6% | 15.8% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.539 | [0.505, 0.575] | 37.0% | 59.2% | 31.7% |
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 1.030 | [0.993, 1.068] | 9.2% | 21.0% | 10.1% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 0.997 | [0.952, 1.043] | 16.6% | 31.8% | 13.9% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.568 | [0.535, 0.603] | 36.0% | 57.6% | 27.7% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.575 | [0.542, 0.611] | 35.8% | 54.6% | 27.3% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.507 | [0.473, 0.542] | 42.7% | 64.2% | 32.3% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.469 | [0.440, 0.500] | 42.8% | 67.4% | 34.9% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.350 | [0.326, 0.377] | 56.1% | 77.6% | 45.4% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.355 | [0.332, 0.380] | 51.8% | 76.4% | 42.1% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.493 | [0.463, 0.524] | 41.4% | 63.1% | 34.5% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | | 21.2% | 33.6% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 1.12 | 0.28 | 0.46 | 0.27 | 0.54 | 0.75 | 0.51 | 0.52 |
| original_vocab_bins | 2.05 | 1.61 | 0.65 | 0.54 | 0.48 | 0.84 | 0.93 | 1.90 |
| vocab | 1.49 | 0.75 | 0.69 | 0.36 | 0.38 | 0.53 | 0.48 | 0.54 |
| grammar_manual | 1.86 | 1.20 | 0.87 | 0.47 | 0.56 | 1.15 | 1.20 | 1.63 |
| grammar_rarity | 2.11 | 1.42 | 0.63 | 0.37 | 0.57 | 0.98 | 1.13 | 1.80 |
| grammar_coverage | 1.34 | 0.76 | 0.69 | 0.40 | 0.45 | 0.66 | 0.50 | 0.66 |
| grammar_all | 1.34 | 0.78 | 0.72 | 0.38 | 0.49 | 0.70 | 0.50 | 0.67 |
| cognitive | 1.21 | 0.36 | 0.44 | 0.22 | 0.75 | 0.45 | 0.54 | 1.14 |
| vocab_grammar_coverage | 1.42 | 0.71 | 0.65 | 0.29 | 0.40 | 0.48 | 0.38 | 0.44 |
| vocab_grammar_coverage_cognitive | 1.10 | 0.36 | 0.32 | 0.22 | 0.46 | 0.39 | 0.32 | 0.43 |
| all_new | 1.09 | 0.36 | 0.36 | 0.22 | 0.44 | 0.36 | 0.33 | 0.46 |
| original_all | 1.17 | 0.68 | 0.51 | 0.30 | 0.46 | 0.53 | 0.47 | 0.58 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 6.2% | 61.2% | 45.0% | 63.4% | 39.6% | 22.0% | 42.9% | 55.6% |
| original_vocab_bins | 0.0% | 0.0% | 35.0% | 25.7% | 31.2% | 16.9% | 17.4% | 0.0% |
| vocab | 15.6% | 24.5% | 25.0% | 42.6% | 41.7% | 30.5% | 42.9% | 31.1% |
| grammar_manual | 0.0% | 0.0% | 21.7% | 26.8% | 22.9% | 8.5% | 0.6% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 23.3% | 38.8% | 25.0% | 10.2% | 11.8% | 2.2% |
| grammar_coverage | 21.9% | 27.6% | 20.0% | 45.4% | 31.2% | 20.3% | 44.1% | 11.1% |
| grammar_all | 18.8% | 23.5% | 25.0% | 48.6% | 27.1% | 16.9% | 43.2% | 15.6% |
| cognitive | 0.0% | 46.9% | 26.7% | 70.5% | 18.8% | 45.8% | 40.6% | 8.9% |
| vocab_grammar_coverage | 12.5% | 29.6% | 20.0% | 54.1% | 35.4% | 35.6% | 49.7% | 42.2% |
| vocab_grammar_coverage_cognitive | 18.8% | 54.1% | 50.0% | 70.5% | 27.1% | 47.5% | 62.1% | 33.3% |
| all_new | 15.6% | 46.9% | 46.7% | 69.4% | 29.2% | 42.4% | 55.6% | 31.1% |
| original_all | 21.9% | 24.5% | 33.3% | 59.0% | 35.4% | 37.3% | 44.4% | 20.0% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 18.8% | 82.7% | 55.0% | 83.1% | 54.2% | 35.6% | 61.5% | 64.4% |
| original_vocab_bins | 0.0% | 1.0% | 55.0% | 54.1% | 52.1% | 27.1% | 31.8% | 0.0% |
| vocab | 18.8% | 44.9% | 45.0% | 76.0% | 66.7% | 55.9% | 61.2% | 51.1% |
| grammar_manual | 0.0% | 2.0% | 36.7% | 61.2% | 39.6% | 15.3% | 5.3% | 0.0% |
| grammar_rarity | 0.0% | 1.0% | 45.0% | 74.3% | 52.1% | 15.3% | 21.8% | 6.7% |
| grammar_coverage | 31.2% | 38.8% | 50.0% | 69.4% | 60.4% | 52.5% | 62.9% | 42.2% |
| grammar_all | 25.0% | 35.7% | 31.7% | 69.9% | 60.4% | 52.5% | 61.2% | 31.1% |
| cognitive | 21.9% | 75.5% | 60.0% | 87.4% | 39.6% | 74.6% | 60.9% | 17.8% |
| vocab_grammar_coverage | 21.9% | 46.9% | 45.0% | 82.0% | 77.1% | 64.4% | 72.9% | 66.7% |
| vocab_grammar_coverage_cognitive | 34.4% | 74.5% | 73.3% | 91.8% | 64.6% | 71.2% | 80.0% | 66.7% |
| all_new | 37.5% | 75.5% | 73.3% | 89.6% | 64.6% | 72.9% | 77.9% | 62.2% |
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
| 1.5 | 0 | 0 | 0 | 7 | 10 | 6 | 5 | 2 | 2 | 0 | 0 |
| 2 | 0 | 0 | 0 | 21 | 40 | 24 | 9 | 3 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 0 | 13 | 16 | 15 | 10 | 5 | 1 | 0 |
| 3.5 | 0 | 0 | 0 | 14 | 54 | 49 | 41 | 20 | 5 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 18 | 14 | 11 | 3 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 1 | 5 | 28 | 10 | 10 | 5 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 9 | 40 | 97 | 129 | 63 | 2 | 0 |
| 6 | 0 | 0 | 0 | 0 | 1 | 2 | 14 | 18 | 9 | 1 | 0 |

### test, gradient boosting: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 1 | 11 | 8 | 8 | 2 | 2 | 0 | 0 |
| 2 | 0 | 0 | 0 | 8 | 33 | 32 | 19 | 5 | 1 | 0 | 0 |
| 3 | 0 | 0 | 0 | 5 | 14 | 18 | 18 | 5 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 13 | 49 | 71 | 40 | 9 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 13 | 16 | 12 | 5 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 16 | 26 | 10 | 6 | 0 | 0 |
| 5.5 | 0 | 0 | 0 | 1 | 7 | 53 | 99 | 74 | 65 | 40 | 1 |
| 6 | 0 | 0 | 0 | 0 | 0 | 9 | 23 | 6 | 4 | 2 | 1 |

### test, gradient boosting: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 7 | 4 | 3 | 5 | 5 | 5 | 0 | 2 | 0 | 0 |
| 2 | 0 | 0 | 27 | 29 | 22 | 13 | 5 | 2 | 0 | 0 | 0 |
| 3 | 0 | 1 | 0 | 1 | 12 | 23 | 14 | 8 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 12 | 29 | 83 | 40 | 13 | 6 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 6 | 21 | 15 | 3 | 2 | 1 | 0 |
| 5 | 0 | 0 | 0 | 1 | 3 | 4 | 13 | 22 | 12 | 4 | 0 |
| 5.5 | 0 | 0 | 0 | 1 | 0 | 8 | 25 | 47 | 97 | 150 | 12 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 16 | 20 | 5 |

### test, gradient boosting: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 6 | 3 | 4 | 8 | 5 | 2 | 1 | 2 | 0 | 0 |
| 2 | 0 | 4 | 23 | 30 | 22 | 11 | 6 | 2 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 0 | 15 | 16 | 19 | 8 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 10 | 29 | 89 | 36 | 15 | 4 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 6 | 23 | 13 | 3 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 4 | 5 | 13 | 19 | 10 | 8 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 3 | 4 | 21 | 59 | 96 | 147 | 10 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 14 | 21 | 7 |

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
| 1.5 | 3 | 4 | 4 | 3 | 5 | 7 | 4 | 1 | 0 | 1 | 0 |
| 2 | 0 | 0 | 29 | 33 | 16 | 13 | 5 | 2 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 5 | 12 | 21 | 14 | 4 | 3 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 2 | 31 | 99 | 39 | 11 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 4 | 16 | 17 | 9 | 1 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 5 | 8 | 22 | 21 | 3 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 14 | 41 | 108 | 169 | 6 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 8 | 16 | 19 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 4 | 6 | 4 | 1 | 9 | 5 | 3 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 53 | 32 | 9 | 3 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 2 | 14 | 30 | 10 | 3 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 22 | 129 | 24 | 4 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 24 | 13 | 1 | 4 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 12 | 28 | 9 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 1 | 17 | 23 | 86 | 211 | 2 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 7 | 22 | 15 |

### test, gradient boosting: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 4 | 5 | 5 | 3 | 7 | 6 | 2 | 0 | 0 | 0 | 0 |
| 2 | 0 | 2 | 46 | 35 | 11 | 3 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 1 | 2 | 15 | 28 | 11 | 3 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 1 | 26 | 127 | 26 | 2 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 5 | 24 | 14 | 2 | 2 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 19 | 25 | 10 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 12 | 24 | 110 | 189 | 3 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 9 | 21 | 14 |

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
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 0.998 | [0.927, 1.069] | 9.9% | 21.3% | 9.5% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 1.009 | [0.932, 1.088] | 14.1% | 26.6% | 15.0% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.552 | [0.492, 0.609] | 33.1% | 59.3% | 24.6% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.556 | [0.495, 0.617] | 34.6% | 58.2% | 25.5% |
| cognitive | cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.521 | [0.456, 0.595] | 41.4% | 64.3% | 36.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.493 | [0.439, 0.543] | 36.5% | 63.5% | 30.1% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.384 | [0.336, 0.435] | 49.4% | 74.1% | 40.7% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.388 | [0.340, 0.440] | 47.9% | 74.5% | 40.8% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.506 | [0.452, 0.559] | 38.4% | 55.9% | 32.2% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | | 23.6% | 34.2% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 0.99 | 0.32 | 0.44 | 0.27 | 0.47 | 0.85 | 0.67 | 0.56 |
| original_vocab_bins | 1.81 | 1.59 | 0.56 | 0.45 | 0.30 | 0.65 | 0.90 | 1.76 |
| vocab | 1.24 | 0.78 | 0.73 | 0.42 | 0.38 | 0.50 | 0.58 | 0.60 |
| grammar_manual | 1.85 | 1.18 | 0.66 | 0.49 | 0.90 | 1.08 | 1.11 | 1.67 |
| grammar_rarity | 2.08 | 1.41 | 0.49 | 0.44 | 0.64 | 0.73 | 1.18 | 1.64 |
| grammar_coverage | 1.11 | 0.84 | 0.46 | 0.35 | 0.58 | 0.57 | 0.49 | 0.77 |
| grammar_all | 1.15 | 0.84 | 0.49 | 0.37 | 0.49 | 0.55 | 0.50 | 0.76 |
| cognitive | 1.03 | 0.38 | 0.34 | 0.24 | 0.64 | 0.33 | 0.61 | 1.30 |
| vocab_grammar_coverage | 1.13 | 0.77 | 0.49 | 0.33 | 0.32 | 0.57 | 0.42 | 0.58 |
| vocab_grammar_coverage_cognitive | 0.98 | 0.40 | 0.34 | 0.29 | 0.39 | 0.45 | 0.34 | 0.47 |
| all_new | 1.01 | 0.38 | 0.32 | 0.31 | 0.33 | 0.43 | 0.35 | 0.44 |
| original_all | 1.02 | 0.71 | 0.52 | 0.30 | 0.42 | 0.43 | 0.50 | 0.64 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 20.0% | 62.1% | 35.3% | 66.1% | 27.3% | 13.3% | 35.3% | 41.7% |
| original_vocab_bins | 0.0% | 0.0% | 47.1% | 32.3% | 45.5% | 6.7% | 15.7% | 0.0% |
| vocab | 6.7% | 20.7% | 11.8% | 35.5% | 36.4% | 20.0% | 41.2% | 50.0% |
| grammar_manual | 0.0% | 0.0% | 41.2% | 27.4% | 0.0% | 6.7% | 1.0% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 41.2% | 27.4% | 18.2% | 26.7% | 6.9% | 0.0% |
| grammar_coverage | 13.3% | 17.2% | 29.4% | 43.5% | 18.2% | 26.7% | 40.2% | 8.3% |
| grammar_all | 13.3% | 13.8% | 29.4% | 45.2% | 9.1% | 33.3% | 43.1% | 16.7% |
| cognitive | 20.0% | 34.5% | 52.9% | 61.3% | 36.4% | 53.3% | 36.3% | 0.0% |
| vocab_grammar_coverage | 6.7% | 17.2% | 23.5% | 53.2% | 36.4% | 13.3% | 40.2% | 50.0% |
| vocab_grammar_coverage_cognitive | 13.3% | 34.5% | 52.9% | 58.1% | 27.3% | 40.0% | 57.8% | 41.7% |
| all_new | 6.7% | 41.4% | 41.2% | 56.5% | 45.5% | 40.0% | 53.9% | 41.7% |
| original_all | 13.3% | 20.7% | 29.4% | 58.1% | 36.4% | 53.3% | 38.2% | 8.3% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| surface | 26.7% | 72.4% | 58.8% | 87.1% | 63.6% | 20.0% | 49.0% | 66.7% |
| original_vocab_bins | 0.0% | 3.4% | 58.8% | 67.7% | 72.7% | 46.7% | 28.4% | 0.0% |
| vocab | 20.0% | 51.7% | 35.3% | 64.5% | 81.8% | 53.3% | 59.8% | 58.3% |
| grammar_manual | 0.0% | 0.0% | 47.1% | 61.3% | 0.0% | 20.0% | 6.9% | 0.0% |
| grammar_rarity | 0.0% | 0.0% | 47.1% | 59.7% | 27.3% | 26.7% | 16.7% | 8.3% |
| grammar_coverage | 26.7% | 37.9% | 64.7% | 77.4% | 45.5% | 60.0% | 62.7% | 33.3% |
| grammar_all | 20.0% | 41.4% | 47.1% | 72.6% | 54.5% | 60.0% | 64.7% | 33.3% |
| cognitive | 26.7% | 75.9% | 64.7% | 87.1% | 36.4% | 80.0% | 59.8% | 8.3% |
| vocab_grammar_coverage | 20.0% | 34.5% | 64.7% | 79.0% | 72.7% | 40.0% | 70.6% | 66.7% |
| vocab_grammar_coverage_cognitive | 13.3% | 75.9% | 64.7% | 88.7% | 81.8% | 60.0% | 77.5% | 66.7% |
| all_new | 13.3% | 72.4% | 70.6% | 82.3% | 81.8% | 60.0% | 81.4% | 75.0% |
| original_all | 13.3% | 34.5% | 52.9% | 80.6% | 45.5% | 73.3% | 53.9% | 41.7% |

## Paired MAE differences (first minus second; negative = the first is better)

Bootstrap over the evaluation texts (1,000 resamples, the same resamples for both models). A 95% interval that does not contain 0 is a difference larger than noise.

### test, ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | -0.026 | [-0.044, -0.006] * |
| grammar_coverage | surface | +0.052 | [+0.017, +0.086] * |
| cognitive | surface | +0.227 | [+0.198, +0.256] * |
| grammar_coverage | grammar_manual | -0.254 | [-0.281, -0.225] * |
| grammar_coverage | grammar_rarity | -0.285 | [-0.316, -0.254] * |
| grammar_all | grammar_coverage | -0.001 | [-0.001, -0.000] * |
| vocab_grammar_coverage | vocab | -0.107 | [-0.124, -0.090] * |
| vocab_grammar_coverage | original_all | -0.168 | [-0.199, -0.138] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.138 | [-0.160, -0.118] * |
| vocab_grammar_coverage_cognitive | original_all | -0.306 | [-0.338, -0.274] * |
| all_new | vocab_grammar_coverage_cognitive | -0.000 | [-0.000, -0.000] * |
| all_new | original_all | -0.306 | [-0.338, -0.274] * |
| vocab | original_vocab_bins | -0.378 | [-0.420, -0.334] * |
| original_all | surface | +0.035 | [-0.003, +0.072] |
| vocab_grammar_coverage_cognitive | surface | -0.271 | [-0.303, -0.241] * |
| all_new | surface | -0.271 | [-0.303, -0.242] * |

### valid (native), ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | -0.022 | [-0.057, +0.015] |
| grammar_coverage | surface | +0.061 | [+0.003, +0.121] * |
| cognitive | surface | +0.247 | [+0.204, +0.289] * |
| grammar_coverage | grammar_manual | -0.190 | [-0.237, -0.144] * |
| grammar_coverage | grammar_rarity | -0.229 | [-0.286, -0.178] * |
| grammar_all | grammar_coverage | -0.001 | [-0.001, -0.000] * |
| vocab_grammar_coverage | vocab | -0.081 | [-0.113, -0.052] * |
| vocab_grammar_coverage | original_all | -0.135 | [-0.188, -0.085] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.143 | [-0.175, -0.107] * |
| vocab_grammar_coverage_cognitive | original_all | -0.279 | [-0.335, -0.224] * |
| all_new | vocab_grammar_coverage_cognitive | -0.000 | [-0.000, +0.000] |
| all_new | original_all | -0.279 | [-0.335, -0.224] * |
| vocab | original_vocab_bins | -0.350 | [-0.424, -0.281] * |
| original_all | surface | +0.032 | [-0.030, +0.096] |
| vocab_grammar_coverage_cognitive | surface | -0.246 | [-0.295, -0.197] * |
| all_new | surface | -0.246 | [-0.294, -0.198] * |

### test, gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.067 | [+0.031, +0.101] * |
| grammar_coverage | surface | +0.096 | [+0.060, +0.133] * |
| cognitive | surface | +0.033 | [+0.001, +0.067] * |
| grammar_coverage | grammar_manual | -0.461 | [-0.502, -0.422] * |
| grammar_coverage | grammar_rarity | -0.428 | [-0.472, -0.379] * |
| grammar_all | grammar_coverage | +0.007 | [-0.004, +0.019] |
| vocab_grammar_coverage | vocab | -0.070 | [-0.096, -0.044] * |
| vocab_grammar_coverage | original_all | -0.023 | [-0.047, +0.000] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.120 | [-0.142, -0.097] * |
| vocab_grammar_coverage_cognitive | original_all | -0.143 | [-0.165, -0.121] * |
| all_new | vocab_grammar_coverage_cognitive | +0.005 | [-0.004, +0.014] |
| all_new | original_all | -0.138 | [-0.160, -0.113] * |
| vocab | original_vocab_bins | -0.426 | [-0.473, -0.381] * |
| original_all | surface | +0.020 | [-0.017, +0.055] |
| vocab_grammar_coverage_cognitive | surface | -0.123 | [-0.153, -0.094] * |
| all_new | surface | -0.118 | [-0.146, -0.090] * |

### valid (native), gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | surface | +0.060 | [-0.012, +0.126] |
| grammar_coverage | surface | +0.013 | [-0.058, +0.087] |
| cognitive | surface | -0.019 | [-0.084, +0.045] |
| grammar_coverage | grammar_manual | -0.446 | [-0.505, -0.381] * |
| grammar_coverage | grammar_rarity | -0.457 | [-0.536, -0.381] * |
| grammar_all | grammar_coverage | +0.005 | [-0.014, +0.022] |
| vocab_grammar_coverage | vocab | -0.105 | [-0.156, -0.055] * |
| vocab_grammar_coverage | original_all | -0.013 | [-0.056, +0.032] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.109 | [-0.148, -0.072] * |
| vocab_grammar_coverage_cognitive | original_all | -0.122 | [-0.162, -0.084] * |
| all_new | vocab_grammar_coverage_cognitive | +0.003 | [-0.012, +0.018] |
| all_new | original_all | -0.119 | [-0.159, -0.081] * |
| vocab | original_vocab_bins | -0.298 | [-0.379, -0.219] * |
| original_all | surface | -0.033 | [-0.099, +0.038] |
| vocab_grammar_coverage_cognitive | surface | -0.155 | [-0.210, -0.099] * |
| all_new | surface | -0.151 | [-0.209, -0.095] * |

