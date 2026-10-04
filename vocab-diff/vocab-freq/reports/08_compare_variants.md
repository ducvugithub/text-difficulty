# 08 compare variants (train, stem and lemma bags)

Spearman correlation with the difficulty label, for all rows and for `finnish-native-only` (`origine` = Real). At most 5000 texts per subset are sampled. mean_bag is over the words that are in a bag.

| level | subset | texts | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag | rho borrowed_coverage |
|---|---|---:|---|---:|---:|---:|---:|
| stem | all | 5,000 | uniform_rank_bin | -0.292 | +0.060 | +0.229 | +0.167 |
| lemma | all | 5,000 | uniform_rank_bin | -0.442 | +0.074 | +0.362 | +0.167 |
| stem | finnish-native-only | 2,332 | uniform_rank_bin | -0.192 | +0.245 | +0.145 | +0.192 |
| lemma | finnish-native-only | 2,332 | uniform_rank_bin | -0.376 | +0.278 | +0.325 | +0.192 |
| stem | all | 5,000 | uniform_cumfreq_bin | -0.292 | +0.060 | +0.300 | +0.167 |
| lemma | all | 5,000 | uniform_cumfreq_bin | -0.442 | +0.074 | +0.415 | +0.167 |
| stem | finnish-native-only | 2,332 | uniform_cumfreq_bin | -0.192 | +0.245 | +0.211 | +0.192 |
| lemma | finnish-native-only | 2,332 | uniform_cumfreq_bin | -0.376 | +0.278 | +0.359 | +0.192 |
| stem | all | 5,000 | log10_freq_bin | -0.292 | +0.060 | +0.294 | +0.167 |
| lemma | all | 5,000 | log10_freq_bin | -0.442 | +0.074 | +0.447 | +0.167 |
| stem | finnish-native-only | 2,332 | log10_freq_bin | -0.192 | +0.245 | +0.161 | +0.192 |
| lemma | finnish-native-only | 2,332 | log10_freq_bin | -0.376 | +0.278 | +0.374 | +0.192 |
