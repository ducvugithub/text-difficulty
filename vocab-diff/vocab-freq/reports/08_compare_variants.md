# 08 compare variants (train, stem and lemma bags)

Spearman correlation with the difficulty label, for all rows and for `finnish-native-only` (`origine` = Real). At most 5000 texts per subset are sampled. mean_bag is over the words that are in a bag.

| level | subset | texts | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag | rho borrowed_coverage |
|---|---|---:|---|---:|---:|---:|---:|
| stem | all | 5,000 | uniform_rank_bin | -0.293 | +0.045 | +0.208 | +0.260 |
| lemma | all | 5,000 | uniform_rank_bin | -0.441 | +0.075 | +0.362 | +0.234 |
| stem | finnish-native-only | 2,332 | uniform_rank_bin | -0.168 | +0.233 | +0.121 | +0.213 |
| lemma | finnish-native-only | 2,332 | uniform_rank_bin | -0.373 | +0.278 | +0.323 | +0.199 |
| stem | all | 5,000 | uniform_cumfreq_bin | -0.293 | +0.045 | +0.297 | +0.260 |
| lemma | all | 5,000 | uniform_cumfreq_bin | -0.441 | +0.075 | +0.414 | +0.234 |
| stem | finnish-native-only | 2,332 | uniform_cumfreq_bin | -0.168 | +0.233 | +0.174 | +0.213 |
| lemma | finnish-native-only | 2,332 | uniform_cumfreq_bin | -0.373 | +0.278 | +0.354 | +0.199 |
| stem | all | 5,000 | log10_freq_bin | -0.293 | +0.045 | +0.295 | +0.260 |
| lemma | all | 5,000 | log10_freq_bin | -0.441 | +0.075 | +0.446 | +0.234 |
| stem | finnish-native-only | 2,332 | log10_freq_bin | -0.168 | +0.233 | +0.145 | +0.213 |
| lemma | finnish-native-only | 2,332 | log10_freq_bin | -0.373 | +0.278 | +0.370 | +0.199 |
