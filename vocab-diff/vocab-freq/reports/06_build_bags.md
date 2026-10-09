# 06 build bags
- bag 1 = most frequent ... highest bag = rarest
- columns of the bag files: `stem` / `lemma`; `freq` its count (a stem's full count, a lemma's own count); `bag` the bag number

# Stem bags

20,704 stems in the list, ranked by `freq`

## stems: uniform_rank_bin -> 06_stem_bags_uniform_rank_bin.tsv

Every bag has the same NUMBER of stems. Stems are ordered by frequency and cut into 10 equal groups (the original Revita definition).

| bag | stems | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 2,070 | 163,114 - 175,065,322 | 91.1% |
| 2 | 2,070 | 44,114 - 163,099 | 5.5% |
| 3 | 2,070 | 17,974 - 44,081 | 1.8% |
| 4 | 2,070 | 8,854 - 17,971 | 0.8% |
| 5 | 2,070 | 4,535 - 8,854 | 0.4% |
| 6 | 2,070 | 2,236 - 4,529 | 0.2% |
| 7 | 2,070 | 985 - 2,235 | 0.1% |
| 8 | 2,070 | 341 - 984 | 0.0% |
| 9 | 2,070 | 69 - 341 | 0.0% |
| 10 | 2,074 | 1 - 69 | 0.0% |

## stems: uniform_cumfreq_bin -> 06_stem_bags_uniform_cumfreq_bin.tsv

Every bag covers the same share of the TOTAL freq count (10% each). Stems are ordered from most to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the grand total. The first bags hold few stems, the last bag holds most of them.

| bag | stems | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 3 | 54,720,650 - 175,065,322 | 10.6% |
| 2 | 14 | 16,151,777 - 52,204,225 | 9.6% |
| 3 | 29 | 7,869,777 - 15,004,818 | 9.7% |
| 4 | 54 | 4,847,870 - 7,419,314 | 10.0% |
| 5 | 89 | 2,825,640 - 4,833,139 | 10.0% |
| 6 | 144 | 1,848,071 - 2,823,300 | 10.0% |
| 7 | 219 | 1,148,169 - 1,844,483 | 10.0% |
| 8 | 394 | 581,250 - 1,135,701 | 10.0% |
| 9 | 929 | 196,076 - 580,689 | 10.0% |
| 10 | 18,829 | 1 - 194,915 | 10.0% |

## stems: log10_freq_bin -> 06_stem_bags_log10_freq_bin.tsv

One bag per factor of 10 in frequency, from the most frequent decade (bag 1) down to the rarest (bag = highest decade - floor(log10(freq)) + 1). The data spans ~10^0 to 10^8, so 9 bags are used.

| bag | stems | band (fixed edges) | observed freq range | % of total freq count |
|---:|---:|---|---|---:|
| 1 | 2 | 100,000,000 to 999,999,999 | 112,983,597 - 175,065,322 | 8.9% |
| 2 | 32 | 10,000,000 to 99,999,999 | 10,071,947 - 54,720,650 | 17.9% |
| 3 | 584 | 1,000,000 to 9,999,999 | 1,006,337 - 9,992,537 | 45.4% |
| 4 | 2,119 | 100,000 to 999,999 | 100,007 - 998,521 | 21.5% |
| 5 | 5,143 | 10,000 to 99,999 | 10,005 - 99,945 | 5.4% |
| 6 | 6,580 | 1,000 to 9,999 | 1,001 - 9,998 | 0.8% |
| 7 | 3,787 | 100 to 999 | 100 - 999 | 0.1% |
| 8 | 1,802 | 10 to 99 | 10 - 99 | 0.0% |
| 9 | 655 | 1 to 9 | 1 - 9 | 0.0% |

# Lemma bags

6,283,183 lemmas in the list, ranked by `freq`

## lemmas: uniform_rank_bin -> 06_lemma_bags_uniform_rank_bin.tsv

Every bag has the same NUMBER of lemmas. Lemmas are ordered by frequency and cut into 10 equal groups (the original Revita definition).

| bag | lemmas | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 628,318 | 20 - 156,017,700 | 99.4% |
| 2 | 628,318 | 7 - 20 | 0.2% |
| 3 | 628,318 | 4 - 7 | 0.1% |
| 4 | 628,318 | 2 - 4 | 0.1% |
| 5 | 628,318 | 2 - 2 | 0.0% |
| 6 | 628,318 | 1 - 2 | 0.0% |
| 7 | 628,318 | 1 - 1 | 0.0% |
| 8 | 628,318 | 1 - 1 | 0.0% |
| 9 | 628,318 | 1 - 1 | 0.0% |
| 10 | 628,321 | 1 - 1 | 0.0% |

## lemmas: uniform_cumfreq_bin -> 06_lemma_bags_uniform_cumfreq_bin.tsv

Every bag covers the same share of the TOTAL freq count (10% each). Lemmas are ordered from most to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the grand total. The first bags hold few lemmas, the last bag holds most of them.

| bag | lemmas | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 3 | 54,720,650 - 156,017,700 | 10.9% |
| 2 | 14 | 12,957,636 - 48,055,503 | 9.6% |
| 3 | 34 | 5,760,807 - 12,707,829 | 9.7% |
| 4 | 69 | 3,114,990 - 5,631,200 | 9.9% |
| 5 | 138 | 1,512,057 - 3,052,195 | 10.0% |
| 6 | 270 | 796,284 - 1,511,283 | 10.0% |
| 7 | 571 | 349,067 - 795,981 | 10.0% |
| 8 | 1,472 | 120,701 - 348,210 | 10.0% |
| 9 | 6,469 | 19,256 - 120,697 | 10.0% |
| 10 | 6,274,143 | 1 - 19,256 | 10.0% |

## lemmas: log10_freq_bin -> 06_lemma_bags_log10_freq_bin.tsv

One bag per factor of 10 in frequency, from the most frequent decade (bag 1) down to the rarest (bag = highest decade - floor(log10(freq)) + 1). The data spans ~10^0 to 10^8, so 9 bags are used.

| bag | lemmas | band (fixed edges) | observed freq range | % of total freq count |
|---:|---:|---|---|---:|
| 1 | 2 | 100,000,000 to 999,999,999 | 112,983,597 - 156,017,700 | 9.0% |
| 2 | 25 | 10,000,000 to 99,999,999 | 10,078,940 - 54,720,650 | 15.3% |
| 3 | 401 | 1,000,000 to 9,999,999 | 1,000,694 - 9,986,774 | 32.7% |
| 4 | 2,502 | 100,000 to 999,999 | 100,026 - 999,463 | 24.3% |
| 5 | 11,012 | 10,000 to 99,999 | 10,001 - 99,919 | 11.0% |
| 6 | 46,629 | 1,000 to 9,999 | 1,000 - 9,999 | 4.8% |
| 7 | 176,769 | 100 to 999 | 100 - 999 | 1.8% |
| 8 | 768,222 | 10 to 99 | 10 - 99 | 0.7% |
| 9 | 5,277,621 | 1 to 9 | 1 - 9 | 0.4% |

## log10_freq_bin: bands and items per bag (lemmas and stems)

| bag | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| count | 100,000,000 to 999,999,999 | 10,000,000 to 99,999,999 | 1,000,000 to 9,999,999 | 100,000 to 999,999 | 10,000 to 99,999 | 1,000 to 9,999 | 100 to 999 | 10 to 99 | 1 to 9 |
| lemmas | 2 | 25 | 401 | 2,502 | 11,012 | 46,629 | 176,769 | 768,222 | 5,277,621 |
| stems | 2 | 32 | 584 | 2,119 | 5,143 | 6,580 | 3,787 | 1,802 | 655 |
