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
| text_length | text length only: words, characters, mean word length, mean sentence length | 4 | 0.625 | [0.593, 0.656] | 23.4% | 46.1% | 26.6% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.125 | [1.088, 1.167] | 6.5% | 15.8% | 9.6% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.742 | [0.708, 0.778] | 18.8% | 36.9% | 19.0% |
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 0.950 | [0.910, 0.987] | 13.9% | 26.6% | 15.0% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 1.043 | [1.002, 1.082] | 10.8% | 22.8% | 13.1% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.697 | [0.661, 0.736] | 22.9% | 42.0% | 25.9% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.697 | [0.661, 0.736] | 22.9% | 41.7% | 25.6% |
| cognitive | cognitive: precomputed parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.708 | [0.672, 0.745] | 22.4% | 39.2% | 25.5% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.604 | [0.572, 0.637] | 25.0% | 49.7% | 25.5% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.518 | [0.488, 0.547] | 33.3% | 59.0% | 33.5% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.518 | [0.489, 0.547] | 33.5% | 59.1% | 33.8% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.659 | [0.624, 0.698] | 26.1% | 48.7% | 26.3% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | | 6.8% | 46.1% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 1.77 | 0.67 | 0.40 | 0.52 | 0.39 | 0.75 | 0.59 | 0.80 |
| original_vocab_bins | 2.53 | 1.94 | 0.95 | 0.84 | 0.30 | 0.57 | 1.11 | 1.50 |
| vocab | 1.70 | 0.97 | 0.76 | 0.58 | 0.43 | 0.81 | 0.73 | 0.53 |
| grammar_manual | 2.25 | 1.53 | 1.24 | 0.54 | 0.40 | 0.71 | 0.98 | 0.76 |
| grammar_rarity | 2.69 | 1.96 | 1.04 | 0.62 | 0.47 | 0.41 | 1.04 | 1.08 |
| grammar_coverage | 1.84 | 0.95 | 0.79 | 0.55 | 0.46 | 0.62 | 0.67 | 0.40 |
| grammar_all | 1.84 | 0.95 | 0.79 | 0.55 | 0.47 | 0.62 | 0.67 | 0.40 |
| cognitive | 1.95 | 1.09 | 0.39 | 0.55 | 0.37 | 0.73 | 0.63 | 0.95 |
| vocab_grammar_coverage | 1.54 | 0.79 | 0.64 | 0.53 | 0.43 | 0.60 | 0.55 | 0.40 |
| vocab_grammar_coverage_cognitive | 1.38 | 0.56 | 0.44 | 0.49 | 0.42 | 0.51 | 0.47 | 0.55 |
| all_new | 1.38 | 0.56 | 0.43 | 0.49 | 0.42 | 0.51 | 0.47 | 0.55 |
| original_all | 1.65 | 0.85 | 0.72 | 0.57 | 0.45 | 0.61 | 0.61 | 0.46 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 0.0% | 2.0% | 41.7% | 20.2% | 35.4% | 15.3% | 22.9% | 75.6% |
| original_vocab_bins | 0.0% | 0.0% | 6.7% | 2.7% | 47.9% | 15.3% | 4.4% | 0.0% |
| vocab | 0.0% | 3.1% | 18.3% | 27.3% | 31.2% | 10.2% | 17.1% | 44.4% |
| grammar_manual | 0.0% | 1.0% | 8.3% | 31.7% | 37.5% | 20.3% | 5.6% | 15.6% |
| grammar_rarity | 0.0% | 0.0% | 8.3% | 17.5% | 37.5% | 32.2% | 5.0% | 4.4% |
| grammar_coverage | 6.2% | 16.3% | 15.0% | 28.4% | 35.4% | 22.0% | 17.4% | 66.7% |
| grammar_all | 6.2% | 16.3% | 15.0% | 29.0% | 33.3% | 20.3% | 17.6% | 66.7% |
| cognitive | 0.0% | 0.0% | 48.3% | 21.3% | 33.3% | 15.3% | 21.2% | 64.4% |
| vocab_grammar_coverage | 3.1% | 24.5% | 13.3% | 26.8% | 31.2% | 23.7% | 23.2% | 57.8% |
| vocab_grammar_coverage_cognitive | 9.4% | 33.7% | 35.0% | 28.4% | 37.5% | 25.4% | 34.4% | 64.4% |
| all_new | 9.4% | 33.7% | 35.0% | 29.0% | 37.5% | 27.1% | 34.4% | 64.4% |
| original_all | 6.2% | 19.4% | 20.0% | 24.0% | 31.2% | 23.7% | 27.6% | 57.8% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 0.0% | 26.5% | 68.3% | 54.1% | 72.9% | 28.8% | 47.4% | 44.4% |
| original_vocab_bins | 0.0% | 0.0% | 18.3% | 19.7% | 77.1% | 40.7% | 8.2% | 2.2% |
| vocab | 0.0% | 18.4% | 31.7% | 49.7% | 64.6% | 30.5% | 35.3% | 48.9% |
| grammar_manual | 0.0% | 1.0% | 13.3% | 55.2% | 68.8% | 33.9% | 14.7% | 37.8% |
| grammar_rarity | 0.0% | 0.0% | 15.0% | 42.6% | 58.3% | 71.2% | 10.0% | 13.3% |
| grammar_coverage | 9.4% | 33.7% | 33.3% | 51.9% | 58.3% | 44.1% | 37.9% | 64.4% |
| grammar_all | 6.2% | 32.7% | 33.3% | 51.9% | 58.3% | 44.1% | 37.9% | 64.4% |
| cognitive | 0.0% | 0.0% | 76.7% | 47.0% | 70.8% | 28.8% | 41.5% | 33.3% |
| vocab_grammar_coverage | 9.4% | 35.7% | 46.7% | 56.8% | 62.5% | 45.8% | 50.9% | 66.7% |
| vocab_grammar_coverage_cognitive | 21.9% | 61.2% | 65.0% | 59.0% | 58.3% | 54.2% | 62.1% | 55.6% |
| all_new | 21.9% | 61.2% | 65.0% | 59.6% | 58.3% | 55.9% | 61.8% | 55.6% |
| original_all | 15.6% | 40.8% | 40.0% | 48.1% | 62.5% | 44.1% | 52.9% | 62.2% |

### test, ridge regression: confusion matrix: text_length

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
| 1.5 | 0 | 0 | 0 | 2 | 9 | 6 | 7 | 6 | 1 | 0 | 1 |
| 2 | 0 | 0 | 1 | 0 | 25 | 50 | 17 | 3 | 2 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 5 | 9 | 17 | 16 | 10 | 2 | 1 |
| 3.5 | 0 | 0 | 0 | 2 | 6 | 58 | 68 | 39 | 6 | 3 | 1 |
| 4 | 0 | 0 | 0 | 0 | 1 | 14 | 18 | 12 | 0 | 3 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 6 | 20 | 17 | 12 | 3 | 1 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 7 | 79 | 157 | 66 | 19 | 12 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 9 | 11 | 17 | 7 |

### test, ridge regression: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 0 | 1 | 5 | 8 | 14 | 3 | 1 | 0 |
| 2 | 0 | 0 | 0 | 1 | 7 | 30 | 36 | 16 | 5 | 3 | 0 |
| 3 | 0 | 0 | 0 | 0 | 5 | 12 | 20 | 18 | 5 | 0 | 0 |
| 3.5 | 0 | 0 | 0 | 3 | 5 | 32 | 92 | 35 | 13 | 2 | 1 |
| 4 | 0 | 0 | 0 | 1 | 1 | 7 | 18 | 13 | 8 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 27 | 19 | 4 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 1 | 92 | 181 | 43 | 17 | 5 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 12 | 23 | 6 | 2 |

### test, ridge regression: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 2 | 3 | 6 | 6 | 3 | 5 | 2 | 1 | 1 | 2 |
| 2 | 6 | 9 | 16 | 22 | 18 | 12 | 10 | 2 | 2 | 1 | 0 |
| 3 | 0 | 1 | 1 | 6 | 9 | 17 | 13 | 11 | 2 | 0 | 0 |
| 3.5 | 0 | 1 | 2 | 4 | 8 | 52 | 72 | 32 | 11 | 1 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 11 | 17 | 11 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 3 | 11 | 21 | 13 | 6 | 4 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 2 | 26 | 88 | 134 | 59 | 29 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 13 | 30 |

### test, ridge regression: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 2 | 3 | 6 | 6 | 3 | 5 | 2 | 1 | 1 | 2 |
| 2 | 6 | 9 | 16 | 22 | 18 | 12 | 10 | 2 | 2 | 1 | 0 |
| 3 | 0 | 1 | 1 | 6 | 9 | 17 | 13 | 11 | 2 | 0 | 0 |
| 3.5 | 0 | 1 | 2 | 5 | 7 | 53 | 71 | 32 | 11 | 1 | 0 |
| 4 | 0 | 0 | 0 | 1 | 5 | 12 | 16 | 11 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 3 | 11 | 22 | 12 | 6 | 4 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 2 | 26 | 87 | 135 | 60 | 28 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 13 | 30 |

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
| 1.5 | 2 | 1 | 7 | 6 | 1 | 9 | 2 | 1 | 1 | 2 | 0 |
| 2 | 3 | 9 | 24 | 26 | 15 | 11 | 7 | 2 | 1 | 0 | 0 |
| 3 | 0 | 1 | 2 | 9 | 8 | 23 | 12 | 5 | 0 | 0 | 0 |
| 3.5 | 0 | 1 | 2 | 3 | 17 | 49 | 75 | 28 | 6 | 2 | 0 |
| 4 | 0 | 0 | 0 | 2 | 4 | 17 | 15 | 10 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 12 | 16 | 14 | 10 | 4 |
| 5.5 | 0 | 0 | 0 | 1 | 0 | 1 | 14 | 61 | 138 | 79 | 46 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 15 | 26 |

### test, ridge regression: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 7 | 7 | 4 | 6 | 1 | 3 | 0 | 1 | 0 |
| 2 | 1 | 9 | 33 | 29 | 16 | 7 | 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 2 | 2 | 9 | 21 | 21 | 4 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 4 | 3 | 17 | 52 | 77 | 27 | 3 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 7 | 21 | 18 | 1 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 7 | 24 | 15 | 7 | 3 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 3 | 8 | 44 | 129 | 117 | 39 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 4 | 10 | 29 |

### test, ridge regression: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 3 | 7 | 7 | 4 | 6 | 1 | 3 | 0 | 1 | 0 |
| 2 | 1 | 9 | 33 | 29 | 16 | 7 | 2 | 1 | 0 | 0 | 0 |
| 3 | 0 | 2 | 2 | 9 | 21 | 21 | 4 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 4 | 3 | 17 | 53 | 76 | 27 | 3 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 7 | 21 | 18 | 1 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 7 | 24 | 16 | 6 | 3 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 3 | 8 | 44 | 130 | 117 | 38 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 4 | 10 | 29 |

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
| text_length | text length only: words, characters, mean word length, mean sentence length | 4 | 0.653 | [0.598, 0.714] | 22.8% | 38.8% | 27.9% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 1.181 | [1.109, 1.253] | 4.9% | 12.9% | 11.1% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.819 | [0.749, 0.890] | 17.9% | 31.9% | 18.6% |
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 1.005 | [0.932, 1.077] | 12.9% | 22.4% | 15.8% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 1.038 | [0.954, 1.128] | 14.4% | 25.5% | 15.8% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.936 | [0.811, 1.075] | 18.6% | 35.7% | 22.6% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.935 | [0.810, 1.074] | 18.6% | 36.1% | 22.6% |
| cognitive | cognitive: precomputed parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.747 | [0.677, 0.827] | 18.6% | 36.1% | 26.0% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.744 | [0.628, 0.888] | 22.4% | 44.9% | 27.1% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.738 | [0.599, 0.917] | 28.1% | 51.3% | 34.2% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.739 | [0.599, 0.920] | 28.5% | 51.3% | 34.4% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 1.242 | [1.015, 1.499] | 21.7% | 39.2% | 26.0% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | | 5.7% | 44.5% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 1.46 | 0.84 | 0.32 | 0.51 | 0.35 | 0.75 | 0.66 | 0.49 |
| original_vocab_bins | 2.44 | 1.89 | 0.97 | 0.89 | 0.25 | 0.64 | 1.15 | 1.52 |
| vocab | 1.39 | 1.06 | 0.84 | 0.69 | 0.45 | 0.91 | 0.80 | 0.54 |
| grammar_manual | 2.16 | 1.55 | 1.04 | 0.68 | 0.53 | 0.75 | 0.97 | 0.91 |
| grammar_rarity | 2.59 | 1.93 | 0.93 | 0.53 | 0.75 | 0.27 | 1.03 | 1.02 |
| grammar_coverage | 1.41 | 1.37 | 0.80 | 0.54 | 0.30 | 0.72 | 1.01 | 1.80 |
| grammar_all | 1.41 | 1.36 | 0.80 | 0.53 | 0.30 | 0.73 | 1.01 | 1.80 |
| cognitive | 1.76 | 1.21 | 0.38 | 0.60 | 0.33 | 0.65 | 0.70 | 0.55 |
| vocab_grammar_coverage | 1.11 | 0.98 | 0.53 | 0.76 | 0.28 | 0.71 | 0.67 | 1.07 |
| vocab_grammar_coverage_cognitive | 1.08 | 0.74 | 0.39 | 0.80 | 0.27 | 0.48 | 0.72 | 1.40 |
| all_new | 1.08 | 0.74 | 0.39 | 0.81 | 0.27 | 0.48 | 0.72 | 1.41 |
| original_all | 1.23 | 1.44 | 0.87 | 0.68 | 0.36 | 0.74 | 1.55 | 3.04 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 0.0% | 6.9% | 52.9% | 21.0% | 45.5% | 0.0% | 21.6% | 75.0% |
| original_vocab_bins | 0.0% | 0.0% | 0.0% | 4.8% | 63.6% | 20.0% | 0.0% | 0.0% |
| vocab | 0.0% | 0.0% | 11.8% | 25.8% | 45.5% | 6.7% | 17.6% | 41.7% |
| grammar_manual | 0.0% | 0.0% | 17.6% | 24.2% | 27.3% | 26.7% | 5.9% | 25.0% |
| grammar_rarity | 0.0% | 0.0% | 5.9% | 30.6% | 9.1% | 66.7% | 5.9% | 8.3% |
| grammar_coverage | 6.7% | 10.3% | 23.5% | 29.0% | 45.5% | 13.3% | 10.8% | 41.7% |
| grammar_all | 6.7% | 10.3% | 23.5% | 29.0% | 45.5% | 13.3% | 10.8% | 41.7% |
| cognitive | 0.0% | 0.0% | 47.1% | 12.9% | 36.4% | 20.0% | 16.7% | 75.0% |
| vocab_grammar_coverage | 20.0% | 13.8% | 17.6% | 32.3% | 63.6% | 13.3% | 14.7% | 41.7% |
| vocab_grammar_coverage_cognitive | 13.3% | 17.2% | 47.1% | 25.8% | 63.6% | 40.0% | 24.5% | 41.7% |
| all_new | 13.3% | 17.2% | 47.1% | 27.4% | 63.6% | 40.0% | 24.5% | 41.7% |
| original_all | 20.0% | 0.0% | 23.5% | 30.6% | 45.5% | 13.3% | 16.7% | 58.3% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 0.0% | 13.8% | 76.5% | 48.4% | 72.7% | 26.7% | 36.3% | 50.0% |
| original_vocab_bins | 0.0% | 0.0% | 5.9% | 24.2% | 100.0% | 40.0% | 1.0% | 0.0% |
| vocab | 6.7% | 10.3% | 23.5% | 41.9% | 63.6% | 20.0% | 31.4% | 66.7% |
| grammar_manual | 0.0% | 0.0% | 23.5% | 38.7% | 54.5% | 40.0% | 14.7% | 33.3% |
| grammar_rarity | 0.0% | 0.0% | 17.6% | 61.3% | 27.3% | 86.7% | 8.8% | 8.3% |
| grammar_coverage | 20.0% | 24.1% | 35.3% | 54.8% | 81.8% | 26.7% | 26.5% | 33.3% |
| grammar_all | 20.0% | 24.1% | 35.3% | 54.8% | 81.8% | 26.7% | 27.5% | 33.3% |
| cognitive | 0.0% | 3.4% | 70.6% | 37.1% | 72.7% | 46.7% | 35.3% | 66.7% |
| vocab_grammar_coverage | 20.0% | 27.6% | 58.8% | 58.1% | 81.8% | 26.7% | 42.2% | 41.7% |
| vocab_grammar_coverage_cognitive | 20.0% | 41.4% | 76.5% | 61.3% | 90.9% | 53.3% | 43.1% | 58.3% |
| all_new | 20.0% | 41.4% | 76.5% | 61.3% | 90.9% | 53.3% | 43.1% | 58.3% |
| original_all | 20.0% | 27.6% | 41.2% | 54.8% | 72.7% | 33.3% | 32.4% | 41.7% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---|---:|---:|---:|
| text_length | text length only: words, characters, mean word length, mean sentence length | 4 | 0.354 | [0.322, 0.388] | 63.1% | 76.2% | 46.8% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.909 | [0.862, 0.960] | 20.7% | 37.3% | 16.8% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.471 | [0.436, 0.509] | 47.5% | 68.2% | 38.3% |
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 0.835 | [0.788, 0.880] | 20.6% | 39.8% | 16.4% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 0.787 | [0.739, 0.836] | 29.9% | 46.8% | 21.2% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.472 | [0.439, 0.507] | 46.6% | 67.5% | 36.9% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.476 | [0.443, 0.510] | 46.5% | 66.6% | 36.5% |
| cognitive | cognitive: precomputed parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.340 | [0.310, 0.370] | 63.8% | 79.1% | 48.3% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.388 | [0.357, 0.423] | 59.0% | 74.7% | 48.3% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.268 | [0.243, 0.295] | 70.4% | 84.7% | 56.8% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.266 | [0.242, 0.292] | 70.2% | 84.7% | 55.2% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.374 | [0.343, 0.408] | 58.4% | 77.0% | 45.6% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | | 6.8% | 46.1% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 1.22 | 0.27 | 0.60 | 0.32 | 0.57 | 0.74 | 0.19 | 0.23 |
| original_vocab_bins | 2.15 | 1.59 | 0.87 | 0.64 | 0.50 | 0.62 | 0.78 | 1.48 |
| vocab | 1.32 | 0.62 | 0.77 | 0.37 | 0.45 | 0.44 | 0.37 | 0.40 |
| grammar_manual | 1.99 | 1.05 | 1.22 | 0.72 | 0.56 | 0.69 | 0.70 | 0.95 |
| grammar_rarity | 2.48 | 1.45 | 1.12 | 0.44 | 0.66 | 0.50 | 0.60 | 1.04 |
| grammar_coverage | 1.20 | 0.64 | 0.78 | 0.33 | 0.60 | 0.52 | 0.36 | 0.37 |
| grammar_all | 1.26 | 0.65 | 0.77 | 0.33 | 0.58 | 0.51 | 0.37 | 0.37 |
| cognitive | 1.23 | 0.38 | 0.47 | 0.22 | 0.72 | 0.44 | 0.22 | 0.32 |
| vocab_grammar_coverage | 1.11 | 0.60 | 0.71 | 0.24 | 0.48 | 0.41 | 0.28 | 0.27 |
| vocab_grammar_coverage_cognitive | 0.87 | 0.30 | 0.38 | 0.20 | 0.53 | 0.36 | 0.17 | 0.24 |
| all_new | 0.86 | 0.28 | 0.39 | 0.21 | 0.53 | 0.35 | 0.16 | 0.26 |
| original_all | 1.05 | 0.52 | 0.57 | 0.23 | 0.57 | 0.37 | 0.30 | 0.28 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 9.4% | 68.4% | 25.0% | 67.8% | 29.2% | 16.9% | 82.1% | 75.6% |
| original_vocab_bins | 0.0% | 4.1% | 20.0% | 25.1% | 33.3% | 27.1% | 25.0% | 0.0% |
| vocab | 9.4% | 40.8% | 21.7% | 46.4% | 41.7% | 37.3% | 60.6% | 48.9% |
| grammar_manual | 0.0% | 16.3% | 10.0% | 20.2% | 22.9% | 22.0% | 26.2% | 13.3% |
| grammar_rarity | 0.0% | 9.2% | 15.0% | 50.3% | 14.6% | 30.5% | 34.4% | 15.6% |
| grammar_coverage | 25.0% | 35.7% | 20.0% | 55.7% | 22.9% | 39.0% | 57.1% | 40.0% |
| grammar_all | 21.9% | 36.7% | 16.7% | 57.4% | 27.1% | 33.9% | 56.5% | 42.2% |
| cognitive | 12.5% | 57.1% | 40.0% | 76.0% | 22.9% | 39.0% | 78.8% | 60.0% |
| vocab_grammar_coverage | 37.5% | 52.0% | 15.0% | 74.9% | 31.2% | 47.5% | 67.9% | 60.0% |
| vocab_grammar_coverage_cognitive | 37.5% | 67.3% | 38.3% | 80.9% | 25.0% | 47.5% | 84.4% | 73.3% |
| all_new | 28.1% | 66.3% | 38.3% | 80.3% | 27.1% | 49.2% | 85.6% | 66.7% |
| original_all | 31.2% | 49.0% | 25.0% | 74.9% | 16.7% | 52.5% | 69.1% | 46.7% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 31.2% | 81.6% | 41.7% | 80.9% | 50.0% | 40.7% | 90.3% | 91.1% |
| original_vocab_bins | 0.0% | 11.2% | 33.3% | 44.3% | 60.4% | 52.5% | 43.8% | 4.4% |
| vocab | 31.2% | 68.4% | 36.7% | 72.1% | 62.5% | 67.8% | 75.9% | 68.9% |
| grammar_manual | 9.4% | 34.7% | 26.7% | 42.1% | 54.2% | 39.0% | 45.6% | 22.2% |
| grammar_rarity | 0.0% | 17.3% | 23.3% | 70.5% | 35.4% | 57.6% | 54.4% | 20.0% |
| grammar_coverage | 34.4% | 61.2% | 31.7% | 78.7% | 50.0% | 59.3% | 76.2% | 71.1% |
| grammar_all | 34.4% | 55.1% | 33.3% | 79.8% | 47.9% | 55.9% | 75.6% | 71.1% |
| cognitive | 31.2% | 74.5% | 60.0% | 90.2% | 39.6% | 67.8% | 89.7% | 80.0% |
| vocab_grammar_coverage | 53.1% | 64.3% | 33.3% | 86.3% | 56.2% | 69.5% | 83.5% | 80.0% |
| vocab_grammar_coverage_cognitive | 53.1% | 78.6% | 70.0% | 89.6% | 56.2% | 79.7% | 93.2% | 93.3% |
| all_new | 50.0% | 82.7% | 66.7% | 89.1% | 50.0% | 79.7% | 94.4% | 91.1% |
| original_all | 46.9% | 70.4% | 51.7% | 89.1% | 45.8% | 78.0% | 82.9% | 84.4% |

### test, gradient boosting: confusion matrix: text_length

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
| 1.5 | 0 | 0 | 5 | 5 | 4 | 5 | 6 | 1 | 3 | 2 | 1 |
| 2 | 0 | 3 | 16 | 24 | 20 | 16 | 8 | 7 | 2 | 2 | 0 |
| 3 | 0 | 0 | 3 | 4 | 6 | 9 | 12 | 9 | 12 | 5 | 0 |
| 3.5 | 0 | 0 | 2 | 15 | 44 | 37 | 32 | 24 | 17 | 9 | 3 |
| 4 | 0 | 0 | 0 | 2 | 4 | 14 | 11 | 9 | 5 | 3 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 6 | 20 | 15 | 13 | 4 | 0 |
| 5.5 | 0 | 0 | 0 | 4 | 5 | 10 | 36 | 71 | 119 | 89 | 6 |
| 6 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 8 | 16 | 10 | 6 |

### test, gradient boosting: confusion matrix: grammar_rarity

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 0 | 0 | 3 | 2 | 7 | 9 | 6 | 3 | 2 | 0 |
| 2 | 1 | 2 | 9 | 17 | 15 | 17 | 18 | 9 | 6 | 4 | 0 |
| 3 | 0 | 0 | 3 | 3 | 9 | 9 | 10 | 14 | 7 | 5 | 0 |
| 3.5 | 0 | 0 | 0 | 0 | 16 | 92 | 37 | 21 | 14 | 3 | 0 |
| 4 | 0 | 0 | 1 | 2 | 2 | 16 | 7 | 11 | 7 | 2 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 4 | 8 | 15 | 18 | 13 | 1 |
| 5.5 | 0 | 0 | 0 | 1 | 1 | 10 | 34 | 68 | 94 | 117 | 15 |
| 6 | 0 | 0 | 0 | 0 | 1 | 1 | 6 | 9 | 10 | 11 | 7 |

### test, gradient boosting: confusion matrix: grammar_coverage

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 8 | 9 | 2 | 4 | 3 | 2 | 2 | 2 | 0 | 0 |
| 2 | 0 | 7 | 35 | 27 | 13 | 5 | 7 | 4 | 0 | 0 | 0 |
| 3 | 0 | 1 | 1 | 8 | 12 | 10 | 16 | 10 | 2 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 2 | 15 | 102 | 44 | 14 | 4 | 1 | 0 |
| 4 | 0 | 0 | 0 | 3 | 8 | 13 | 11 | 9 | 2 | 2 | 0 |
| 5 | 0 | 0 | 0 | 0 | 2 | 3 | 11 | 14 | 23 | 6 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 4 | 13 | 33 | 83 | 194 | 12 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 22 | 18 |

### test, gradient boosting: confusion matrix: grammar_all

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 7 | 7 | 5 | 1 | 4 | 2 | 3 | 2 | 0 | 0 |
| 2 | 0 | 5 | 36 | 28 | 10 | 9 | 6 | 3 | 1 | 0 | 0 |
| 3 | 0 | 1 | 0 | 11 | 10 | 11 | 16 | 10 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 2 | 3 | 15 | 105 | 40 | 13 | 4 | 1 | 0 |
| 4 | 0 | 0 | 1 | 3 | 6 | 13 | 13 | 9 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 2 | 1 | 10 | 21 | 20 | 5 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 1 | 4 | 15 | 34 | 85 | 192 | 9 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 21 | 19 |

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
| 1.5 | 0 | 12 | 7 | 2 | 0 | 4 | 3 | 2 | 2 | 0 | 0 |
| 2 | 1 | 3 | 51 | 16 | 8 | 8 | 7 | 3 | 1 | 0 | 0 |
| 3 | 0 | 0 | 2 | 13 | 9 | 14 | 16 | 5 | 1 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 1 | 6 | 137 | 29 | 6 | 3 | 0 | 0 |
| 4 | 0 | 0 | 0 | 1 | 6 | 15 | 15 | 7 | 3 | 1 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 3 | 6 | 17 | 28 | 5 | 0 |
| 5.5 | 0 | 0 | 0 | 0 | 0 | 2 | 13 | 16 | 70 | 231 | 8 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 14 | 27 |

### test, gradient boosting: confusion matrix: vocab_grammar_coverage_cognitive

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 0 | 12 | 6 | 3 | 5 | 4 | 2 | 0 | 0 | 0 | 0 |
| 2 | 0 | 2 | 66 | 20 | 5 | 3 | 2 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 5 | 21 | 23 | 8 | 2 | 1 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 0 | 10 | 148 | 15 | 5 | 3 | 1 | 0 |
| 4 | 0 | 0 | 1 | 1 | 8 | 19 | 12 | 3 | 4 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 1 | 5 | 12 | 28 | 11 | 1 |
| 5.5 | 0 | 0 | 1 | 0 | 0 | 1 | 6 | 7 | 31 | 287 | 7 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 9 | 33 |

### test, gradient boosting: confusion matrix: all_new

| true \ predicted | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 | 4 | 4.5 | 5 | 5.5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.5 | 1 | 9 | 8 | 4 | 3 | 5 | 2 | 0 | 0 | 0 | 0 |
| 2 | 0 | 2 | 65 | 21 | 5 | 4 | 1 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 6 | 23 | 23 | 6 | 2 | 0 | 0 | 0 | 0 |
| 3.5 | 0 | 0 | 1 | 0 | 11 | 147 | 14 | 7 | 2 | 1 | 0 |
| 4 | 0 | 0 | 1 | 0 | 7 | 20 | 13 | 4 | 3 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 1 | 1 | 4 | 13 | 29 | 10 | 1 |
| 5.5 | 0 | 0 | 1 | 0 | 0 | 1 | 5 | 7 | 31 | 291 | 4 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 12 | 30 |

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
| text_length | text length only: words, characters, mean word length, mean sentence length | 4 | 0.340 | [0.283, 0.401] | 61.2% | 79.8% | 46.1% |
| original_vocab_bins | the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags) | 11 | 0.916 | [0.821, 1.005] | 20.9% | 39.5% | 19.0% |
| vocab | vocab: lemma and stem frequency bins, English-looking share, lexical features | 36 | 0.524 | [0.455, 0.600] | 48.7% | 65.0% | 40.6% |
| grammar_manual | grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels) | 12 | 0.837 | [0.747, 0.928] | 26.2% | 43.0% | 24.5% |
| grammar_rarity | grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF) | 17 | 0.831 | [0.731, 0.937] | 34.6% | 48.3% | 21.7% |
| grammar_coverage | grammar: the share of every concept and every topic in the text (one feature each) | 401 | 0.470 | [0.413, 0.526] | 46.0% | 63.9% | 36.3% |
| grammar_all | grammar: manual levels, rarity and coverage together | 430 | 0.475 | [0.418, 0.532] | 44.5% | 65.4% | 32.9% |
| cognitive | cognitive: precomputed parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length | 7 | 0.325 | [0.266, 0.383] | 66.9% | 83.7% | 51.8% |
| vocab_grammar_coverage | vocab and grammar coverage | 437 | 0.393 | [0.338, 0.452] | 53.2% | 74.9% | 43.3% |
| vocab_grammar_coverage_cognitive | vocab, grammar coverage and cognitive | 444 | 0.271 | [0.223, 0.323] | 68.8% | 86.7% | 53.3% |
| all_new | every new feature: vocab, all grammar, cognitive | 473 | 0.265 | [0.214, 0.319] | 70.3% | 87.5% | 55.8% |
| original_all | the 402 original columns: syntax averages, old vocab bins, concept and topic columns | 402 | 0.380 | [0.327, 0.433] | 56.3% | 73.8% | 43.5% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | | 5.7% | 44.5% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 1.02 | 0.34 | 0.44 | 0.25 | 0.43 | 0.73 | 0.22 | 0.25 |
| original_vocab_bins | 2.19 | 1.71 | 0.83 | 0.60 | 0.38 | 0.48 | 0.78 | 1.34 |
| vocab | 1.04 | 0.61 | 0.77 | 0.38 | 0.50 | 0.53 | 0.49 | 0.39 |
| grammar_manual | 2.11 | 1.02 | 0.95 | 0.75 | 1.05 | 0.66 | 0.62 | 0.98 |
| grammar_rarity | 2.32 | 1.54 | 1.00 | 0.43 | 0.82 | 0.33 | 0.69 | 0.94 |
| grammar_coverage | 0.94 | 0.77 | 0.57 | 0.27 | 0.46 | 0.56 | 0.41 | 0.42 |
| grammar_all | 0.98 | 0.77 | 0.62 | 0.26 | 0.52 | 0.52 | 0.41 | 0.48 |
| cognitive | 1.10 | 0.40 | 0.43 | 0.13 | 0.64 | 0.35 | 0.25 | 0.37 |
| vocab_grammar_coverage | 0.96 | 0.61 | 0.46 | 0.22 | 0.56 | 0.50 | 0.32 | 0.34 |
| vocab_grammar_coverage_cognitive | 0.68 | 0.45 | 0.33 | 0.16 | 0.30 | 0.41 | 0.20 | 0.23 |
| all_new | 0.68 | 0.43 | 0.32 | 0.17 | 0.30 | 0.38 | 0.19 | 0.21 |
| original_all | 0.71 | 0.50 | 0.68 | 0.16 | 0.40 | 0.38 | 0.39 | 0.31 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 20.0% | 51.7% | 52.9% | 66.1% | 27.3% | 13.3% | 79.4% | 58.3% |
| original_vocab_bins | 0.0% | 10.3% | 17.6% | 30.6% | 27.3% | 46.7% | 19.6% | 0.0% |
| vocab | 13.3% | 41.4% | 17.6% | 54.8% | 45.5% | 26.7% | 58.8% | 66.7% |
| grammar_manual | 6.7% | 17.2% | 23.5% | 24.2% | 18.2% | 33.3% | 31.4% | 41.7% |
| grammar_rarity | 0.0% | 10.3% | 11.8% | 58.1% | 0.0% | 26.7% | 42.2% | 25.0% |
| grammar_coverage | 13.3% | 34.5% | 29.4% | 64.5% | 36.4% | 20.0% | 51.0% | 41.7% |
| grammar_all | 13.3% | 37.9% | 29.4% | 58.1% | 18.2% | 20.0% | 52.9% | 33.3% |
| cognitive | 40.0% | 48.3% | 47.1% | 85.5% | 18.2% | 46.7% | 78.4% | 50.0% |
| vocab_grammar_coverage | 33.3% | 41.4% | 47.1% | 71.0% | 9.1% | 20.0% | 57.8% | 66.7% |
| vocab_grammar_coverage_cognitive | 33.3% | 51.7% | 47.1% | 80.6% | 36.4% | 33.3% | 85.3% | 58.3% |
| all_new | 26.7% | 58.6% | 35.3% | 80.6% | 45.5% | 46.7% | 86.3% | 66.7% |
| original_all | 13.3% | 41.4% | 35.3% | 80.6% | 27.3% | 46.7% | 61.8% | 41.7% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text_length | 33.3% | 82.8% | 70.6% | 85.5% | 72.7% | 46.7% | 89.2% | 83.3% |
| original_vocab_bins | 0.0% | 17.2% | 47.1% | 51.6% | 72.7% | 66.7% | 40.2% | 0.0% |
| vocab | 40.0% | 58.6% | 47.1% | 74.2% | 63.6% | 40.0% | 71.6% | 66.7% |
| grammar_manual | 6.7% | 27.6% | 29.4% | 43.5% | 18.2% | 46.7% | 56.9% | 41.7% |
| grammar_rarity | 0.0% | 17.2% | 11.8% | 74.2% | 36.4% | 93.3% | 52.0% | 25.0% |
| grammar_coverage | 26.7% | 48.3% | 52.9% | 82.3% | 45.5% | 60.0% | 66.7% | 66.7% |
| grammar_all | 20.0% | 58.6% | 52.9% | 85.5% | 54.5% | 46.7% | 67.6% | 66.7% |
| cognitive | 46.7% | 75.9% | 70.6% | 98.4% | 36.4% | 86.7% | 89.2% | 83.3% |
| vocab_grammar_coverage | 40.0% | 65.5% | 64.7% | 88.7% | 54.5% | 53.3% | 82.4% | 66.7% |
| vocab_grammar_coverage_cognitive | 60.0% | 69.0% | 76.5% | 95.2% | 90.9% | 80.0% | 92.2% | 91.7% |
| all_new | 73.3% | 75.9% | 82.4% | 95.2% | 81.8% | 80.0% | 90.2% | 91.7% |
| original_all | 33.3% | 65.5% | 41.2% | 93.5% | 63.6% | 66.7% | 76.5% | 83.3% |

## Paired MAE differences (first minus second; negative = the first is better)

Bootstrap over the evaluation texts (1,000 resamples, the same resamples for both models). A 95% interval that does not contain 0 is a difference larger than noise.

### test, ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | text_length | +0.117 | [+0.084, +0.151] * |
| grammar_coverage | text_length | +0.072 | [+0.035, +0.113] * |
| cognitive | text_length | +0.083 | [+0.059, +0.107] * |
| grammar_coverage | grammar_manual | -0.253 | [-0.292, -0.214] * |
| grammar_coverage | grammar_rarity | -0.346 | [-0.385, -0.304] * |
| grammar_all | grammar_coverage | -0.000 | [-0.001, +0.000] |
| vocab_grammar_coverage | vocab | -0.138 | [-0.170, -0.107] * |
| vocab_grammar_coverage | original_all | -0.055 | [-0.084, -0.026] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.086 | [-0.106, -0.066] * |
| vocab_grammar_coverage_cognitive | original_all | -0.141 | [-0.169, -0.113] * |
| all_new | vocab_grammar_coverage_cognitive | +0.000 | [-0.000, +0.000] |
| all_new | original_all | -0.141 | [-0.168, -0.113] * |
| vocab | original_vocab_bins | -0.384 | [-0.427, -0.344] * |
| original_all | text_length | +0.034 | [-0.004, +0.075] |
| vocab_grammar_coverage_cognitive | text_length | -0.107 | [-0.134, -0.078] * |
| all_new | text_length | -0.107 | [-0.133, -0.078] * |

### valid (native), ridge regression

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | text_length | +0.167 | [+0.096, +0.237] * |
| grammar_coverage | text_length | +0.282 | [+0.162, +0.416] * |
| cognitive | text_length | +0.094 | [+0.048, +0.138] * |
| grammar_coverage | grammar_manual | -0.069 | [-0.200, +0.075] |
| grammar_coverage | grammar_rarity | -0.104 | [-0.224, +0.037] |
| grammar_all | grammar_coverage | -0.001 | [-0.003, +0.001] |
| vocab_grammar_coverage | vocab | -0.079 | [-0.188, +0.061] |
| vocab_grammar_coverage | original_all | -0.503 | [-0.720, -0.310] * |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.007 | [-0.071, +0.055] |
| vocab_grammar_coverage_cognitive | original_all | -0.509 | [-0.706, -0.333] * |
| all_new | vocab_grammar_coverage_cognitive | +0.001 | [-0.001, +0.003] |
| all_new | original_all | -0.508 | [-0.706, -0.331] * |
| vocab | original_vocab_bins | -0.361 | [-0.436, -0.284] * |
| original_all | text_length | +0.590 | [+0.361, +0.854] * |
| vocab_grammar_coverage_cognitive | text_length | +0.081 | [-0.052, +0.269] |
| all_new | text_length | +0.082 | [-0.052, +0.272] |

### test, gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | text_length | +0.117 | [+0.080, +0.156] * |
| grammar_coverage | text_length | +0.118 | [+0.085, +0.151] * |
| cognitive | text_length | -0.014 | [-0.044, +0.016] |
| grammar_coverage | grammar_manual | -0.363 | [-0.407, -0.318] * |
| grammar_coverage | grammar_rarity | -0.316 | [-0.362, -0.270] * |
| grammar_all | grammar_coverage | +0.004 | [-0.009, +0.018] |
| vocab_grammar_coverage | vocab | -0.083 | [-0.113, -0.052] * |
| vocab_grammar_coverage | original_all | +0.014 | [-0.014, +0.040] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.121 | [-0.148, -0.094] * |
| vocab_grammar_coverage_cognitive | original_all | -0.107 | [-0.130, -0.082] * |
| all_new | vocab_grammar_coverage_cognitive | -0.002 | [-0.009, +0.005] |
| all_new | original_all | -0.109 | [-0.133, -0.084] * |
| vocab | original_vocab_bins | -0.439 | [-0.488, -0.389] * |
| original_all | text_length | +0.021 | [-0.012, +0.054] |
| vocab_grammar_coverage_cognitive | text_length | -0.086 | [-0.110, -0.061] * |
| all_new | text_length | -0.088 | [-0.113, -0.064] * |

### valid (native), gradient boosting

| first | second | difference in MAE | 95% CI |
|---|---|---:|---|
| vocab | text_length | +0.185 | [+0.111, +0.261] * |
| grammar_coverage | text_length | +0.132 | [+0.069, +0.194] * |
| cognitive | text_length | -0.015 | [-0.072, +0.042] |
| grammar_coverage | grammar_manual | -0.366 | [-0.446, -0.280] * |
| grammar_coverage | grammar_rarity | -0.361 | [-0.466, -0.264] * |
| grammar_all | grammar_coverage | +0.004 | [-0.015, +0.026] |
| vocab_grammar_coverage | vocab | -0.131 | [-0.190, -0.075] * |
| vocab_grammar_coverage | original_all | +0.013 | [-0.036, +0.066] |
| vocab_grammar_coverage_cognitive | vocab_grammar_coverage | -0.122 | [-0.176, -0.070] * |
| vocab_grammar_coverage_cognitive | original_all | -0.109 | [-0.151, -0.064] * |
| all_new | vocab_grammar_coverage_cognitive | -0.006 | [-0.017, +0.005] |
| all_new | original_all | -0.115 | [-0.160, -0.068] * |
| vocab | original_vocab_bins | -0.391 | [-0.485, -0.291] * |
| original_all | text_length | +0.040 | [-0.017, +0.100] |
| vocab_grammar_coverage_cognitive | text_length | -0.068 | [-0.111, -0.025] * |
| all_new | text_length | -0.074 | [-0.116, -0.032] * |

