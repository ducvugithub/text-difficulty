# 08 compare variants (train, 5,000 texts)

| freq column | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag |
|---|---|---:|---:|---:|
| freq | uniform_rank_bin | -0.319 | +0.074 | -0.082 |
| freq | uniform_cumfreq_bin | -0.319 | +0.074 | -0.368 |
| freq | log10_freq_bin | -0.319 | +0.074 | -0.319 |
| rarest_stem_freq | uniform_rank_bin | -0.262 | +0.074 | -0.217 |
| rarest_stem_freq | uniform_cumfreq_bin | -0.262 | +0.074 | -0.315 |
| rarest_stem_freq | log10_freq_bin | -0.262 | +0.074 | -0.265 |
