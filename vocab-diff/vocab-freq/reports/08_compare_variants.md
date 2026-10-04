# 08 compare variants (train)

Each combination is shown for two subsets: `all` rows, and `finnish-native-only` (`origine` = Real; the Russian-origin rows are translations). At most 5000 texts per subset are sampled.

| subset | texts | freq column | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag |
|---|---:|---|---|---:|---:|---:|
| all | 5,000 | freq | uniform_rank_bin | -0.319 | +0.074 | -0.082 |
| all | 5,000 | freq | uniform_cumfreq_bin | -0.319 | +0.074 | -0.368 |
| all | 5,000 | freq | log10_freq_bin | -0.319 | +0.074 | -0.319 |
| all | 5,000 | rarest_stem_freq | uniform_rank_bin | -0.262 | +0.074 | -0.217 |
| all | 5,000 | rarest_stem_freq | uniform_cumfreq_bin | -0.262 | +0.074 | -0.315 |
| all | 5,000 | rarest_stem_freq | log10_freq_bin | -0.262 | +0.074 | -0.265 |
| finnish-native-only | 2,332 | freq | uniform_rank_bin | -0.406 | +0.278 | -0.287 |
| finnish-native-only | 2,332 | freq | uniform_cumfreq_bin | -0.406 | +0.278 | -0.396 |
| finnish-native-only | 2,332 | freq | log10_freq_bin | -0.406 | +0.278 | -0.403 |
| finnish-native-only | 2,332 | rarest_stem_freq | uniform_rank_bin | -0.370 | +0.278 | -0.330 |
| finnish-native-only | 2,332 | rarest_stem_freq | uniform_cumfreq_bin | -0.370 | +0.278 | -0.342 |
| finnish-native-only | 2,332 | rarest_stem_freq | log10_freq_bin | -0.370 | +0.278 | -0.370 |
