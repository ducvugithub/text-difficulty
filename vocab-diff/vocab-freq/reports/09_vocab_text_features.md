# 09 vocab text features

Built by `VocabDiffFeatureConstruct` (lemma bins log10_freq_bin/10, stem bins uniform_cumfreq_bin/10). Definitions in `docs/features.md`. `-minen` and `-sti` are heuristics (Voikko does not mark them as derivations). Lemmas are context-free (see the TODO in CLEANUP_SUMMARY.md). The `stem_bag_k_coverage` / `lemma_bag_k_coverage` columns are in the CSVs but not listed here.

Spearman correlation with the difficulty label (train); more extreme = stronger relationship.

| feature | rho all rows | rho finnish-native-only |
|---|---:|---:|
| stem_OOV_coverage | +0.048 | +0.233 |
| stem_borrowed_coverage | +0.215 | +0.252 |
| mean_log_stem_freq | -0.305 | -0.172 |
| lemma_OOV_coverage | +0.077 | +0.278 |
| lemma_borrowed_coverage | +0.164 | +0.193 |
| mean_log_lemma_freq | -0.453 | -0.376 |
| n_unique_lemmas | +0.412 | +0.360 |
| ttr_lemma_200 | -0.200 | +0.303 |
| avg_word_length | +0.502 | +0.504 |
| long_word_ratio | +0.482 | +0.487 |
| compound_ratio | +0.440 | +0.309 |
| avg_compound_parts | +0.441 | +0.342 |
| n_compound_tokens | +0.534 | +0.502 |
| deriv_llinen_ratio | +0.247 | +0.271 |
| deriv_ton_ratio | +0.230 | +0.194 |
| deriv_minen_ratio | +0.369 | +0.368 |
| deriv_sti_ratio | +0.230 | +0.297 |

## Mean per split

| feature | train | valid | test |
|---|---:|---:|---:|
| stem_OOV_coverage | 0.049 | 0.053 | 0.035 |
| stem_borrowed_coverage | 0.050 | 0.048 | 0.054 |
| mean_log_stem_freq | 6.533 | 6.536 | 6.457 |
| lemma_OOV_coverage | 0.051 | 0.056 | 0.038 |
| lemma_borrowed_coverage | 0.044 | 0.042 | 0.042 |
| mean_log_lemma_freq | 6.186 | 6.199 | 5.990 |
| n_unique_lemmas | 85.541 | 82.564 | 162.132 |
| ttr_lemma_200 | 0.744 | 0.734 | 0.609 |
| avg_word_length | 6.876 | 6.816 | 7.461 |
| long_word_ratio | 0.205 | 0.200 | 0.259 |
| compound_ratio | 0.088 | 0.085 | 0.144 |
| avg_compound_parts | 1.587 | 1.645 | 2.066 |
| n_compound_tokens | 12.136 | 10.499 | 32.355 |
| deriv_llinen_ratio | 0.011 | 0.011 | 0.008 |
| deriv_ton_ratio | 0.002 | 0.003 | 0.002 |
| deriv_minen_ratio | 0.008 | 0.007 | 0.012 |
| deriv_sti_ratio | 0.009 | 0.009 | 0.006 |
