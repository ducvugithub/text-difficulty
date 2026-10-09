# Experiment: train on train_native (2,332 rows)

- Source and origin are not features. Test = real Finnish only; valid (native) = the real-Finnish rows of valid.
- **MAE**: mean absolute error in label units (the labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)
- **accuracy**: share of texts whose prediction, rounded to the nearest half step, is exactly the label
- **accuracy ±1 step**: share within 0.5 of the label
- **balanced accuracy**: mean of the per-label accuracies; every label counts equally, so favouring the common labels is punished
- dummy models predict one constant for every text, taken from the training labels: most common label (5.5); median label (5)
  They are the floor: a real model has to beat them

## test: ridge regression

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.681 | 26.5% | 48.6% | 25.5% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.659 | 26.1% | 48.7% | 26.3% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.657 | 26.9% | 48.7% | 26.3% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.657 | 28.3% | 48.8% | 27.1% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.647 | 28.0% | 50.1% | 27.3% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.744 | 18.8% | 37.8% | 22.5% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | 6.8% | 46.1% | 12.5% |

### test, ridge regression: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.69 | 0.88 | 0.78 | 0.58 | 0.47 | 0.64 | 0.63 | 0.48 |
| old_vocab_bins | 1.65 | 0.85 | 0.72 | 0.57 | 0.45 | 0.61 | 0.61 | 0.46 |
| new_lemma_bins | 1.64 | 0.84 | 0.77 | 0.57 | 0.45 | 0.60 | 0.60 | 0.48 |
| new_stem_bins | 1.68 | 0.83 | 0.75 | 0.58 | 0.43 | 0.58 | 0.60 | 0.47 |
| new_lemma_stem_bins | 1.65 | 0.82 | 0.73 | 0.56 | 0.43 | 0.59 | 0.60 | 0.46 |
| surface | 1.76 | 1.18 | 0.84 | 0.47 | 0.34 | 0.60 | 0.78 | 0.40 |

### test, ridge regression: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 9.4% | 22.4% | 15.0% | 27.3% | 29.2% | 22.0% | 27.9% | 51.1% |
| old_vocab_bins | 6.2% | 19.4% | 20.0% | 24.0% | 31.2% | 23.7% | 27.6% | 57.8% |
| new_lemma_bins | 9.4% | 21.4% | 16.7% | 27.9% | 29.2% | 22.0% | 28.2% | 55.6% |
| new_stem_bins | 6.2% | 22.4% | 16.7% | 28.4% | 35.4% | 23.7% | 30.6% | 53.3% |
| new_lemma_stem_bins | 12.5% | 22.4% | 18.3% | 28.4% | 31.2% | 20.3% | 29.7% | 55.6% |
| surface | 0.0% | 0.0% | 8.3% | 27.3% | 47.9% | 23.7% | 12.9% | 60.0% |

### test, ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 12.5% | 43.9% | 36.7% | 52.5% | 66.7% | 40.7% | 50.3% | 62.2% |
| old_vocab_bins | 15.6% | 40.8% | 40.0% | 48.1% | 62.5% | 44.1% | 52.9% | 62.2% |
| new_lemma_bins | 18.8% | 41.8% | 35.0% | 49.2% | 64.6% | 47.5% | 52.4% | 57.8% |
| new_stem_bins | 15.6% | 44.9% | 36.7% | 50.3% | 60.4% | 49.2% | 51.5% | 57.8% |
| new_lemma_stem_bins | 18.8% | 43.9% | 36.7% | 53.0% | 64.6% | 50.8% | 52.1% | 60.0% |
| surface | 6.2% | 5.1% | 28.3% | 59.6% | 79.2% | 49.2% | 27.6% | 73.3% |

## valid (native): ridge regression

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 1.237 | 21.7% | 38.0% | 23.8% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 1.242 | 21.7% | 39.2% | 26.0% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 1.183 | 22.4% | 38.8% | 26.1% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 1.218 | 25.9% | 37.3% | 29.5% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 1.188 | 23.6% | 39.2% | 27.7% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.793 | 13.3% | 31.9% | 19.5% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | 5.7% | 44.5% | 12.5% |

### valid (native), ridge regression: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.27 | 1.44 | 0.92 | 0.70 | 0.33 | 0.80 | 1.51 | 3.02 |
| old_vocab_bins | 1.23 | 1.44 | 0.87 | 0.68 | 0.36 | 0.74 | 1.55 | 3.04 |
| new_lemma_bins | 1.23 | 1.38 | 0.92 | 0.71 | 0.32 | 0.78 | 1.41 | 2.80 |
| new_stem_bins | 1.30 | 1.39 | 0.87 | 0.70 | 0.32 | 0.74 | 1.48 | 3.02 |
| new_lemma_stem_bins | 1.27 | 1.38 | 0.89 | 0.72 | 0.35 | 0.76 | 1.42 | 2.84 |
| surface | 1.33 | 1.22 | 0.87 | 0.50 | 0.17 | 0.62 | 0.88 | 0.52 |

### valid (native), ridge regression: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 6.7% | 6.9% | 17.6% | 30.6% | 54.5% | 13.3% | 18.6% | 41.7% |
| old_vocab_bins | 20.0% | 0.0% | 23.5% | 30.6% | 45.5% | 13.3% | 16.7% | 58.3% |
| new_lemma_bins | 13.3% | 10.3% | 23.5% | 29.0% | 54.5% | 26.7% | 17.6% | 33.3% |
| new_stem_bins | 13.3% | 13.8% | 23.5% | 32.3% | 54.5% | 26.7% | 21.6% | 50.0% |
| new_lemma_stem_bins | 13.3% | 10.3% | 29.4% | 24.2% | 54.5% | 26.7% | 21.6% | 41.7% |
| surface | 0.0% | 3.4% | 0.0% | 21.0% | 72.7% | 20.0% | 5.9% | 33.3% |

### valid (native), ridge regression: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 20.0% | 20.7% | 41.2% | 56.5% | 63.6% | 33.3% | 32.4% | 33.3% |
| old_vocab_bins | 20.0% | 27.6% | 41.2% | 54.8% | 72.7% | 33.3% | 32.4% | 41.7% |
| new_lemma_bins | 20.0% | 24.1% | 41.2% | 54.8% | 72.7% | 33.3% | 33.3% | 33.3% |
| new_stem_bins | 20.0% | 27.6% | 41.2% | 50.0% | 72.7% | 26.7% | 32.4% | 33.3% |
| new_lemma_stem_bins | 20.0% | 27.6% | 41.2% | 53.2% | 72.7% | 33.3% | 34.3% | 33.3% |
| surface | 0.0% | 10.3% | 23.5% | 59.7% | 90.9% | 40.0% | 16.7% | 58.3% |

## test: gradient boosting

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.386 | 56.1% | 78.0% | 43.8% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.374 | 58.4% | 77.0% | 45.6% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.387 | 54.1% | 76.9% | 41.8% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.384 | 56.8% | 77.7% | 46.2% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.380 | 57.2% | 77.1% | 47.2% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.433 | 55.7% | 72.8% | 40.7% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.284 | 39.3% | 51.3% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.229 | 6.8% | 46.1% | 12.5% |

### test, gradient boosting: MAE per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 1.06 | 0.52 | 0.58 | 0.25 | 0.62 | 0.38 | 0.31 | 0.28 |
| old_vocab_bins | 1.05 | 0.52 | 0.57 | 0.23 | 0.57 | 0.37 | 0.30 | 0.28 |
| new_lemma_bins | 1.06 | 0.53 | 0.55 | 0.25 | 0.58 | 0.34 | 0.32 | 0.31 |
| new_stem_bins | 1.01 | 0.52 | 0.56 | 0.25 | 0.59 | 0.37 | 0.31 | 0.27 |
| new_lemma_stem_bins | 1.08 | 0.52 | 0.55 | 0.26 | 0.55 | 0.32 | 0.31 | 0.26 |
| surface | 1.30 | 0.58 | 0.79 | 0.22 | 0.82 | 0.51 | 0.32 | 0.23 |

### test, gradient boosting: accuracy per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 31.2% | 48.0% | 25.0% | 72.1% | 14.6% | 49.2% | 66.2% | 44.4% |
| old_vocab_bins | 31.2% | 49.0% | 25.0% | 74.9% | 16.7% | 52.5% | 69.1% | 46.7% |
| new_lemma_bins | 31.2% | 43.9% | 18.3% | 74.3% | 18.8% | 47.5% | 62.9% | 37.8% |
| new_stem_bins | 34.4% | 46.9% | 30.0% | 70.5% | 22.9% | 52.5% | 65.9% | 46.7% |
| new_lemma_stem_bins | 34.4% | 44.9% | 33.3% | 71.6% | 27.1% | 55.9% | 65.6% | 44.4% |
| surface | 9.4% | 41.8% | 20.0% | 78.7% | 10.4% | 27.1% | 67.4% | 71.1% |

### test, gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=32) | 2 (n=98) | 3 (n=60) | 3.5 (n=183) | 4 (n=48) | 5 (n=59) | 5.5 (n=340) | 6 (n=45) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 46.9% | 76.5% | 55.0% | 86.9% | 45.8% | 78.0% | 83.8% | 88.9% |
| old_vocab_bins | 46.9% | 70.4% | 51.7% | 89.1% | 45.8% | 78.0% | 82.9% | 84.4% |
| new_lemma_bins | 50.0% | 70.4% | 55.0% | 86.3% | 50.0% | 81.4% | 81.8% | 86.7% |
| new_stem_bins | 40.6% | 72.4% | 51.7% | 88.5% | 50.0% | 72.9% | 84.1% | 93.3% |
| new_lemma_stem_bins | 43.8% | 71.4% | 53.3% | 85.8% | 52.1% | 81.4% | 82.4% | 91.1% |
| surface | 31.2% | 68.4% | 31.7% | 89.1% | 29.2% | 62.7% | 82.9% | 84.4% |

## valid (native): gradient boosting

| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |
|---|---|---:|---:|---:|---:|---:|
| no_vocab | the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts | 391 | 0.377 | 55.9% | 74.1% | 43.4% |
| old_vocab_bins | no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline | 402 | 0.380 | 56.3% | 73.8% | 43.5% |
| new_lemma_bins | no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count | 403 | 0.390 | 52.9% | 74.5% | 39.8% |
| new_stem_bins | no_vocab plus the stem bin features: the same measures, counted per stem | 404 | 0.391 | 54.8% | 72.6% | 43.5% |
| new_lemma_stem_bins | no_vocab plus the lemma and the stem bin features | 416 | 0.394 | 53.2% | 73.0% | 40.1% |
| surface | text length, characters, word length and average sentence length, a control for length shortcuts | 4 | 0.431 | 57.4% | 71.9% | 42.1% |
| dummy | always the most common label of the training data (5.5) | 0 | 1.361 | 38.8% | 49.0% | 12.5% |
| dummy | always the median label of the training data (5) | 0 | 1.295 | 5.7% | 44.5% | 12.5% |

### valid (native), gradient boosting: MAE per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 0.71 | 0.52 | 0.61 | 0.18 | 0.47 | 0.39 | 0.37 | 0.27 |
| old_vocab_bins | 0.71 | 0.50 | 0.68 | 0.16 | 0.40 | 0.38 | 0.39 | 0.31 |
| new_lemma_bins | 0.73 | 0.56 | 0.65 | 0.19 | 0.41 | 0.41 | 0.38 | 0.29 |
| new_stem_bins | 0.76 | 0.55 | 0.64 | 0.18 | 0.37 | 0.36 | 0.39 | 0.38 |
| new_lemma_stem_bins | 0.76 | 0.58 | 0.72 | 0.18 | 0.41 | 0.35 | 0.37 | 0.33 |
| surface | 0.79 | 0.67 | 0.98 | 0.15 | 0.66 | 0.64 | 0.35 | 0.27 |

### valid (native), gradient boosting: accuracy per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 20.0% | 51.7% | 29.4% | 75.8% | 18.2% | 40.0% | 61.8% | 50.0% |
| old_vocab_bins | 13.3% | 41.4% | 35.3% | 80.6% | 27.3% | 46.7% | 61.8% | 41.7% |
| new_lemma_bins | 20.0% | 44.8% | 35.3% | 75.8% | 18.2% | 33.3% | 57.8% | 33.3% |
| new_stem_bins | 26.7% | 37.9% | 29.4% | 80.6% | 27.3% | 46.7% | 57.8% | 41.7% |
| new_lemma_stem_bins | 26.7% | 41.4% | 17.6% | 79.0% | 18.2% | 46.7% | 57.8% | 33.3% |
| surface | 33.3% | 48.3% | 23.5% | 80.6% | 0.0% | 26.7% | 65.7% | 58.3% |

### valid (native), gradient boosting: accuracy ±1 step per label

| feature set | 1.5 (n=15) | 2 (n=29) | 3 (n=17) | 3.5 (n=62) | 4 (n=11) | 5 (n=15) | 5.5 (n=102) | 6 (n=12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| no_vocab | 33.3% | 65.5% | 47.1% | 95.2% | 45.5% | 66.7% | 77.5% | 83.3% |
| old_vocab_bins | 33.3% | 65.5% | 41.2% | 93.5% | 63.6% | 66.7% | 76.5% | 83.3% |
| new_lemma_bins | 40.0% | 62.1% | 47.1% | 88.7% | 72.7% | 86.7% | 74.5% | 100.0% |
| new_stem_bins | 26.7% | 65.5% | 41.2% | 91.9% | 81.8% | 80.0% | 72.5% | 75.0% |
| new_lemma_stem_bins | 33.3% | 62.1% | 41.2% | 88.7% | 63.6% | 86.7% | 76.5% | 75.0% |
| surface | 53.3% | 58.6% | 35.3% | 91.9% | 18.2% | 60.0% | 78.4% | 83.3% |
