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
| grammar_manual | 0.835 | 0.926 | 0.724 | 0.711 | 0.695 | 1.995 |
| grammar_rarity | 0.787 | 1.024 | 0.440 | 0.582 | 0.617 | 2.476 |
| grammar_coverage | 0.472 | 0.599 | 0.330 | 0.370 | 0.356 | 1.200 |
| grammar_all | 0.476 | 0.595 | 0.331 | 0.379 | 0.363 | 1.261 |
| cognitive | 0.340 | 0.451 | 0.223 | 0.228 | 0.206 | 1.234 |
| vocab_grammar_coverage | 0.388 | 0.520 | 0.236 | 0.254 | 0.310 | 1.112 |
| vocab_grammar_coverage_cognitive | 0.268 | 0.354 | 0.197 | 0.185 | 0.154 | 0.872 |
| all_new | 0.266 | 0.352 | 0.208 | 0.182 | 0.144 | 0.861 |
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
| grammar_manual | 0.849 | [0.776, 0.922] | 20.6% | 35.2% | +0.70 |
| grammar_rarity | 0.872 | [0.800, 0.947] | 18.7% | 38.1% | +0.66 |
| grammar_coverage | 0.448 | [0.395, 0.502] | 45.2% | 69.7% | +0.88 |
| grammar_all | 0.446 | [0.397, 0.500] | 43.9% | 67.7% | +0.89 |
| cognitive | 0.394 | [0.347, 0.438] | 51.0% | 71.0% | +0.90 |
| vocab_grammar_coverage | 0.411 | [0.360, 0.460] | 50.6% | 71.9% | +0.90 |
| vocab_grammar_coverage_cognitive | 0.277 | [0.246, 0.314] | 63.9% | 81.3% | +0.94 |
| all_new | 0.273 | [0.241, 0.310] | 63.5% | 83.5% | +0.94 |
| original_all | 0.387 | [0.341, 0.434] | 51.3% | 72.6% | +0.91 |

### (b) trained on all real-Finnish train rows (n=2332)

| feature set | MAE | MAE 95% CI | accuracy | within one step | rho |
|---|---:|---|---:|---:|---:|
| dummy (median) | 1.287 | [1.187, 1.390] | 19.4% | 19.4% | |
| surface | 0.466 | [0.418, 0.519] | 45.2% | 62.6% | +0.88 |
| original_vocab_bins | 1.083 | [0.992, 1.173] | 15.5% | 30.0% | +0.43 |
| vocab | 0.557 | [0.497, 0.624] | 37.7% | 61.3% | +0.83 |
| grammar_manual | 0.926 | [0.852, 1.009] | 16.8% | 35.2% | +0.63 |
| grammar_rarity | 1.024 | [0.945, 1.110] | 16.1% | 29.4% | +0.56 |
| grammar_coverage | 0.599 | [0.538, 0.658] | 31.9% | 54.8% | +0.83 |
| grammar_all | 0.595 | [0.539, 0.653] | 31.6% | 52.3% | +0.84 |
| cognitive | 0.451 | [0.402, 0.499] | 45.5% | 65.8% | +0.89 |
| vocab_grammar_coverage | 0.520 | [0.463, 0.582] | 41.9% | 60.3% | +0.86 |
| vocab_grammar_coverage_cognitive | 0.354 | [0.315, 0.397] | 52.3% | 75.8% | +0.92 |
| all_new | 0.352 | [0.312, 0.393] | 51.6% | 75.2% | +0.92 |
| original_all | 0.476 | [0.423, 0.531] | 39.7% | 66.5% | +0.87 |

## Feature sets

- `surface`: surface measures: words, characters, mean word length, mean sentence length
- `original_vocab_bins`: the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags)
- `vocab`: vocab: lemma and stem frequency bins, English-looking share, lexical features
- `grammar_manual`: grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels)
- `grammar_rarity`: grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF)
- `grammar_coverage`: grammar: the share of every concept and every topic in the text (one feature each)
- `grammar_all`: grammar: manual levels, rarity and coverage together
- `cognitive`: cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length
- `vocab_grammar_coverage`: vocab and grammar coverage
- `vocab_grammar_coverage_cognitive`: vocab, grammar coverage and cognitive
- `all_new`: every new feature: vocab, all grammar, cognitive
- `original_all`: the 402 original columns: syntax averages, old vocab bins, concept and topic columns
