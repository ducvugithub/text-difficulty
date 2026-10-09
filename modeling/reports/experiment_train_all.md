# Experiment: train on train_all (8,293 rows)

- Source and origin are not features. Test = real Finnish only; valid (native) = the real-Finnish rows of valid.
- **MAE**: mean absolute error in label units (the labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)
- **accuracy**: share of texts whose prediction, rounded to the nearest half step, is exactly the label
- **accuracy ±1 step**: share within 0.5 of the label
- **balanced accuracy**: mean of the per-label accuracies; every label counts equally, so favouring the common labels is punished
- dummy models predict one constant for every text, taken from the training labels: most common label (3); median label (3.5)
  They are the floor: a real model has to beat them

## test: ridge regression

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.964 | 15.1% | 28.8% | 14.6% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.946 | 15.3% | 28.9% | 15.7% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.926 | 14.7% | 28.0% | 14.7% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.946 | 16.0% | 28.1% | 16.5% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.907 | 15.4% | 28.9% | 16.5% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.914 | 17.7% | 31.7% | 15.7% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | 21.2% | 33.6% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.90 | 1.29 | 0.70 | 0.29 | 0.29 | 0.74 | 1.32 | 1.06 |
| old_vocab_bins | 1.91 | 1.29 | 0.68 | 0.29 | 0.27 | 0.70 | 1.28 | 1.06 |
| new_lemma_bins | 1.90 | 1.27 | 0.74 | 0.33 | 0.30 | 0.65 | 1.22 | 1.00 |
| new_stem_bins | 1.90 | 1.30 | 0.71 | 0.30 | 0.26 | 0.69 | 1.28 | 0.99 |
| new_lemma_stem_bins | 1.88 | 1.25 | 0.72 | 0.33 | 0.29 | 0.63 | 1.20 | 0.85 |
| surface | 1.85 | 1.25 | 0.55 | 0.27 | 0.31 | 1.00 | 1.14 | 1.44 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 0.0% | 0.0% | 11.7% | 53.0% | 43.8% | 8.5% | 0.3% | 0.0% |
| old_vocab_bins | 0.0% | 0.0% | 15.0% | 49.7% | 50.0% | 10.2% | 0.6% | 0.0% |
| new_lemma_bins | 0.0% | 0.0% | 16.7% | 44.8% | 41.7% | 10.2% | 2.4% | 2.2% |
| new_stem_bins | 0.0% | 0.0% | 16.7% | 50.3% | 52.1% | 11.9% | 1.2% | 0.0% |
| new_lemma_stem_bins | 0.0% | 0.0% | 16.7% | 44.8% | 52.1% | 11.9% | 2.1% | 4.4% |
| surface | 0.0% | 0.0% | 16.7% | 50.3% | 47.9% | 3.4% | 7.6% | 0.0% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 0.0% | 0.0% | 31.7% | 84.7% | 89.6% | 25.4% | 4.1% | 6.7% |
| old_vocab_bins | 0.0% | 0.0% | 36.7% | 83.6% | 89.6% | 25.4% | 4.1% | 6.7% |
| new_lemma_bins | 0.0% | 0.0% | 35.0% | 76.5% | 77.1% | 32.2% | 5.3% | 15.6% |
| new_stem_bins | 0.0% | 0.0% | 30.0% | 80.9% | 89.6% | 25.4% | 4.7% | 6.7% |
| new_lemma_stem_bins | 0.0% | 0.0% | 31.7% | 76.5% | 81.2% | 37.3% | 5.6% | 24.4% |
| surface | 0.0% | 0.0% | 45.0% | 87.4% | 81.2% | 5.1% | 13.2% | 0.0% |

## valid (native): ridge regression

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.989 | 14.8% | 29.3% | 15.2% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.976 | 14.1% | 29.3% | 15.3% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.960 | 14.4% | 25.9% | 14.3% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.971 | 14.4% | 28.5% | 15.0% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.954 | 12.9% | 26.2% | 14.8% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.951 | 13.7% | 31.6% | 10.9% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | 23.6% | 34.2% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.71 | 1.30 | 0.62 | 0.32 | 0.29 | 0.79 | 1.35 | 1.18 |
| old_vocab_bins | 1.70 | 1.29 | 0.60 | 0.33 | 0.29 | 0.77 | 1.32 | 1.16 |
| new_lemma_bins | 1.63 | 1.30 | 0.67 | 0.38 | 0.29 | 0.72 | 1.25 | 1.14 |
| new_stem_bins | 1.70 | 1.29 | 0.61 | 0.35 | 0.27 | 0.74 | 1.31 | 1.11 |
| new_lemma_stem_bins | 1.62 | 1.28 | 0.68 | 0.41 | 0.31 | 0.73 | 1.24 | 0.95 |
| surface | 1.51 | 1.27 | 0.54 | 0.30 | 0.30 | 0.97 | 1.23 | 1.61 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 0.0% | 0.0% | 11.8% | 48.4% | 54.5% | 6.7% | 0.0% | 0.0% |
| old_vocab_bins | 0.0% | 0.0% | 17.6% | 43.5% | 54.5% | 6.7% | 0.0% | 0.0% |
| new_lemma_bins | 0.0% | 0.0% | 11.8% | 45.2% | 36.4% | 20.0% | 1.0% | 0.0% |
| new_stem_bins | 0.0% | 0.0% | 11.8% | 46.8% | 54.5% | 6.7% | 0.0% | 0.0% |
| new_lemma_stem_bins | 0.0% | 0.0% | 5.9% | 38.7% | 45.5% | 20.0% | 0.0% | 8.3% |
| surface | 0.0% | 0.0% | 11.8% | 45.2% | 27.3% | 0.0% | 2.9% | 0.0% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 0.0% | 3.4% | 58.8% | 83.9% | 81.8% | 33.3% | 0.0% | 0.0% |
| old_vocab_bins | 0.0% | 3.4% | 64.7% | 82.3% | 72.7% | 33.3% | 1.0% | 0.0% |
| new_lemma_bins | 0.0% | 3.4% | 52.9% | 67.7% | 90.9% | 26.7% | 2.0% | 0.0% |
| new_stem_bins | 0.0% | 3.4% | 52.9% | 77.4% | 81.8% | 33.3% | 2.9% | 0.0% |
| new_lemma_stem_bins | 0.0% | 3.4% | 52.9% | 62.9% | 81.8% | 26.7% | 5.9% | 8.3% |
| surface | 0.0% | 0.0% | 47.1% | 83.9% | 90.9% | 13.3% | 10.8% | 0.0% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.519 | 38.2% | 60.3% | 31.9% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.493 | 41.4% | 63.1% | 34.5% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.476 | 42.7% | 65.5% | 33.5% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.506 | 38.0% | 63.5% | 30.2% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.475 | 41.7% | 66.6% | 31.9% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.529 | 41.2% | 59.2% | 34.2% |
| dummy | always the most common label of the training data (3) | 0 | 1.605 | 6.9% | 28.1% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.325 | 21.2% | 33.6% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.13 | 0.71 | 0.53 | 0.31 | 0.52 | 0.53 | 0.50 | 0.60 |
| old_vocab_bins | 1.17 | 0.68 | 0.51 | 0.30 | 0.46 | 0.53 | 0.47 | 0.58 |
| new_lemma_bins | 1.23 | 0.69 | 0.48 | 0.28 | 0.48 | 0.44 | 0.44 | 0.58 |
| new_stem_bins | 1.21 | 0.69 | 0.52 | 0.32 | 0.50 | 0.53 | 0.47 | 0.61 |
| new_lemma_stem_bins | 1.28 | 0.71 | 0.43 | 0.30 | 0.46 | 0.43 | 0.43 | 0.55 |
| surface | 1.23 | 0.70 | 0.66 | 0.19 | 0.61 | 0.55 | 0.57 | 0.41 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 21.9% | 24.5% | 31.7% | 53.6% | 27.1% | 40.7% | 40.6% | 15.6% |
| old_vocab_bins | 21.9% | 24.5% | 33.3% | 59.0% | 35.4% | 37.3% | 44.4% | 20.0% |
| new_lemma_bins | 21.9% | 29.6% | 33.3% | 61.2% | 22.9% | 35.6% | 47.6% | 15.6% |
| new_stem_bins | 18.8% | 24.5% | 35.0% | 54.1% | 18.8% | 30.5% | 42.4% | 17.8% |
| new_lemma_stem_bins | 12.5% | 27.6% | 40.0% | 55.7% | 22.9% | 32.2% | 49.1% | 15.6% |
| surface | 12.5% | 23.5% | 18.3% | 79.2% | 18.8% | 32.2% | 35.6% | 53.3% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 31.2% | 41.8% | 60.0% | 80.3% | 54.2% | 59.3% | 62.1% | 35.6% |
| old_vocab_bins | 31.2% | 45.9% | 58.3% | 79.2% | 54.2% | 59.3% | 67.4% | 46.7% |
| new_lemma_bins | 31.2% | 46.9% | 66.7% | 83.1% | 50.0% | 67.8% | 69.7% | 40.0% |
| new_stem_bins | 31.2% | 51.0% | 60.0% | 80.3% | 54.2% | 57.6% | 67.4% | 37.8% |
| new_lemma_stem_bins | 28.1% | 44.9% | 73.3% | 82.0% | 56.2% | 64.4% | 70.6% | 53.3% |
| surface | 34.4% | 46.9% | 30.0% | 86.3% | 41.7% | 59.3% | 56.2% | 73.3% |

## valid (native): gradient boosting

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.531 | 31.6% | 57.0% | 24.6% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.506 | 38.4% | 55.9% | 32.2% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.514 | 34.6% | 57.4% | 24.8% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.516 | 34.2% | 58.9% | 27.8% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.508 | 35.4% | 58.9% | 28.9% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.568 | 41.4% | 59.7% | 37.6% |
| dummy | always the most common label of the training data (3) | 0 | 1.576 | 6.5% | 30.0% | 12.5% |
| dummy | always the median label of the training data (3.5) | 0 | 1.308 | 23.6% | 34.2% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.00 | 0.74 | 0.45 | 0.31 | 0.43 | 0.52 | 0.54 | 0.73 |
| old_vocab_bins | 1.02 | 0.71 | 0.52 | 0.30 | 0.42 | 0.43 | 0.50 | 0.64 |
| new_lemma_bins | 1.12 | 0.79 | 0.50 | 0.30 | 0.42 | 0.47 | 0.49 | 0.60 |
| new_stem_bins | 1.05 | 0.77 | 0.46 | 0.31 | 0.37 | 0.46 | 0.51 | 0.69 |
| new_lemma_stem_bins | 1.11 | 0.77 | 0.49 | 0.30 | 0.36 | 0.43 | 0.50 | 0.54 |
| surface | 0.84 | 0.68 | 0.74 | 0.21 | 0.35 | 0.65 | 0.70 | 0.55 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 13.3% | 20.7% | 29.4% | 46.8% | 18.2% | 26.7% | 33.3% | 8.3% |
| old_vocab_bins | 13.3% | 20.7% | 29.4% | 58.1% | 36.4% | 53.3% | 38.2% | 8.3% |
| new_lemma_bins | 6.7% | 13.8% | 23.5% | 56.5% | 18.2% | 33.3% | 38.2% | 8.3% |
| new_stem_bins | 6.7% | 17.2% | 35.3% | 48.4% | 27.3% | 33.3% | 37.3% | 16.7% |
| new_lemma_stem_bins | 0.0% | 13.8% | 23.5% | 56.5% | 36.4% | 40.0% | 36.3% | 25.0% |
| surface | 6.7% | 27.6% | 17.6% | 74.2% | 45.5% | 46.7% | 32.4% | 50.0% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 20.0% | 37.9% | 64.7% | 80.6% | 63.6% | 73.3% | 52.9% | 25.0% |
| old_vocab_bins | 13.3% | 34.5% | 52.9% | 80.6% | 45.5% | 73.3% | 53.9% | 41.7% |
| new_lemma_bins | 6.7% | 27.6% | 58.8% | 80.6% | 72.7% | 66.7% | 57.8% | 41.7% |
| new_stem_bins | 26.7% | 31.0% | 64.7% | 80.6% | 63.6% | 73.3% | 56.9% | 41.7% |
| new_lemma_stem_bins | 6.7% | 27.6% | 58.8% | 85.5% | 63.6% | 66.7% | 58.8% | 50.0% |
| surface | 40.0% | 51.7% | 47.1% | 88.7% | 63.6% | 46.7% | 50.0% | 66.7% |
