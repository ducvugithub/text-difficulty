# Shortcut check: within a single source

In the real-Finnish rows the label is constant within four of the five sources; only FI varies. Gradient boosting throughout; test = the 865 real-Finnish texts.

## 1. Source structure of the test set

| source | texts | labels |
|---|---:|---|
| FI | 310 | 2 to 6, 5 values |
| yle-selkouutiset | 183 | 3.5 (constant) |
| HS | 170 | 5.5 (constant) |
| yle | 170 | 5.5 (constant) |
| easy_text | 32 | 1.5 (constant) |

## 2. A model that sees only the source (diagnostic, never a feature set)

Trained on the real-Finnish train rows, tested on all test texts: MAE 0.466 [0.417, 0.513], accuracy 64.2%, within one step 69.7%. This is what recognising the source alone achieves; a feature set near it is mostly recognising the source.

On the FI texts alone the source-only model has MAE 1.299: it cannot separate FI labels.

## 3. Test MAE per source (trained on the real-Finnish train rows)

| feature set | all | FI (n=310) | yle-selkouutiset (n=183) | HS (n=170) | yle (n=170) | easy_text (n=32) |
|---|---:|---:|---:|---:|---:|---:|
| source only | 0.466 | 1.299 | 0.000 | 0.000 | 0.000 | 0.000 |
| surface | 0.354 | 0.466 | 0.316 | 0.187 | 0.194 | 1.222 |
| original_vocab_bins | 0.909 | 1.083 | 0.644 | 0.712 | 0.839 | 2.154 |
| vocab | 0.471 | 0.557 | 0.374 | 0.303 | 0.427 | 1.316 |
| grammar_manual | 0.821 | 0.924 | 0.752 | 0.663 | 0.642 | 2.002 |
| grammar_rarity | 0.793 | 1.000 | 0.474 | 0.591 | 0.644 | 2.475 |
| grammar_coverage | 0.460 | 0.586 | 0.323 | 0.349 | 0.343 | 1.226 |
| grammar_all | 0.472 | 0.600 | 0.347 | 0.347 | 0.348 | 1.275 |
| cognitive | 0.340 | 0.451 | 0.223 | 0.228 | 0.206 | 1.234 |
| vocab_grammar_coverage | 0.382 | 0.512 | 0.232 | 0.255 | 0.292 | 1.121 |
| vocab_grammar_coverage_cognitive | 0.257 | 0.339 | 0.194 | 0.167 | 0.149 | 0.868 |
| all_new | 0.258 | 0.344 | 0.205 | 0.168 | 0.141 | 0.816 |
| original_all | 0.374 | 0.476 | 0.230 | 0.329 | 0.263 | 1.048 |

## 4. FI only: the source cannot explain the label

FI test texts: 310, labels [2.0, 3.0, 4.0, 5.0, 6.0]. The dummy always predicts the FI train median (3). rho = Spearman correlation of prediction and label.

### (a) trained on the FI train rows only (n=729)

| feature set | MAE | MAE 95% CI | accuracy | within one step | rho |
|---|---:|---|---:|---:|---:|
| dummy (median) | 1.287 | [1.187, 1.390] | 19.4% | 19.4% | |
| surface | 0.398 | [0.359, 0.439] | 46.8% | 67.4% | +0.92 |
| original_vocab_bins | 0.965 | [0.881, 1.059] | 19.0% | 35.8% | +0.54 |
| vocab | 0.478 | [0.427, 0.531] | 42.9% | 67.4% | +0.88 |
| grammar_manual | 0.820 | [0.745, 0.896] | 21.0% | 41.9% | +0.69 |
| grammar_rarity | 0.850 | [0.772, 0.935] | 18.7% | 37.7% | +0.66 |
| grammar_coverage | 0.445 | [0.394, 0.499] | 45.5% | 69.7% | +0.88 |
| grammar_all | 0.428 | [0.377, 0.479] | 46.1% | 68.1% | +0.89 |
| cognitive | 0.394 | [0.347, 0.438] | 51.0% | 71.0% | +0.90 |
| vocab_grammar_coverage | 0.409 | [0.359, 0.455] | 51.9% | 70.3% | +0.90 |
| vocab_grammar_coverage_cognitive | 0.277 | [0.243, 0.314] | 62.6% | 82.6% | +0.94 |
| all_new | 0.271 | [0.239, 0.308] | 64.8% | 83.9% | +0.94 |
| original_all | 0.387 | [0.341, 0.434] | 51.3% | 72.6% | +0.91 |

### (b) trained on all real-Finnish train rows (n=2332)

| feature set | MAE | MAE 95% CI | accuracy | within one step | rho |
|---|---:|---|---:|---:|---:|
| dummy (median) | 1.287 | [1.187, 1.390] | 19.4% | 19.4% | |
| surface | 0.466 | [0.418, 0.519] | 45.2% | 62.6% | +0.88 |
| original_vocab_bins | 1.083 | [0.992, 1.173] | 15.5% | 30.0% | +0.43 |
| vocab | 0.557 | [0.497, 0.624] | 37.7% | 61.3% | +0.83 |
| grammar_manual | 0.924 | [0.848, 1.007] | 19.4% | 33.9% | +0.65 |
| grammar_rarity | 1.000 | [0.920, 1.093] | 19.4% | 33.2% | +0.56 |
| grammar_coverage | 0.586 | [0.528, 0.645] | 34.2% | 56.1% | +0.84 |
| grammar_all | 0.600 | [0.540, 0.660] | 32.6% | 53.9% | +0.83 |
| cognitive | 0.451 | [0.402, 0.499] | 45.5% | 65.8% | +0.89 |
| vocab_grammar_coverage | 0.512 | [0.458, 0.570] | 39.0% | 60.6% | +0.86 |
| vocab_grammar_coverage_cognitive | 0.339 | [0.299, 0.381] | 54.8% | 76.5% | +0.92 |
| all_new | 0.344 | [0.305, 0.386] | 54.8% | 77.1% | +0.92 |
| original_all | 0.476 | [0.423, 0.531] | 39.7% | 66.5% | +0.87 |

## Feature sets

- `surface`: surface measures: words, characters, mean word length, mean sentence length
- `original_vocab_bins`: the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags)
- `vocab`: vocab: lemma and stem frequency bins, English-looking share, lexical features
- `grammar_manual`: grammar: share of concept occurrences per CEFR level (Revita's manual levels)
- `grammar_rarity`: grammar: how rare the concepts are in Revita's Finnish stories (bin shares, mean IDF)
- `grammar_coverage`: grammar: the share of every concept in the text (one feature each)
- `grammar_all`: grammar: manual levels, rarity and coverage together
- `cognitive`: cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length
- `vocab_grammar_coverage`: vocab and grammar coverage
- `vocab_grammar_coverage_cognitive`: vocab, grammar coverage and cognitive
- `all_new`: every new feature: vocab, all grammar, cognitive
- `original_all`: the 402 original columns: syntax averages, old vocab bins, concept and topic columns
