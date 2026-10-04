# 06 build bags
- bag 1 = most frequent ... highest bag = rarest
- columns of the bag files: `stem` / `lemma`; `freq` its count (a stem's full count, a lemma's own count); `bag` the bag number

# Stem bags

20,420 stems in the list, ranked by `freq`

## stems: uniform_rank_bin -> 06_stem_bags_uniform_rank_bin.tsv

Every bag has the same NUMBER of stems. Stems are ordered by frequency and cut into 10 equal groups (the original Revita definition).

| bag | stems | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 2,042 | 165,089 - 175,065,322 | 91.0% |
| 2 | 2,042 | 44,521 - 164,915 | 5.6% |
| 3 | 2,042 | 18,098 - 44,501 | 1.8% |
| 4 | 2,042 | 8,934 - 18,098 | 0.8% |
| 5 | 2,042 | 4,579 - 8,930 | 0.4% |
| 6 | 2,042 | 2,253 - 4,577 | 0.2% |
| 7 | 2,042 | 986 - 2,250 | 0.1% |
| 8 | 2,042 | 337 - 985 | 0.0% |
| 9 | 2,042 | 67 - 336 | 0.0% |
| 10 | 2,042 | 1 - 67 | 0.0% |

## stems: uniform_cumfreq_bin -> 06_stem_bags_uniform_cumfreq_bin.tsv

Every bag covers the same share of the TOTAL freq count (10% each). Stems are ordered from most to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the grand total. The first bags hold few stems, the last bag holds most of them.

| bag | stems | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 3 | 54,720,650 - 175,065,322 | 10.7% |
| 2 | 14 | 15,004,818 - 52,204,225 | 9.7% |
| 3 | 30 | 7,395,601 - 14,676,465 | 9.8% |
| 4 | 53 | 4,833,139 - 7,149,367 | 9.8% |
| 5 | 89 | 2,809,297 - 4,816,725 | 10.0% |
| 6 | 144 | 1,840,740 - 2,808,914 | 10.0% |
| 7 | 218 | 1,134,827 - 1,839,461 | 10.0% |
| 8 | 391 | 581,250 - 1,134,595 | 10.0% |
| 9 | 918 | 197,429 - 580,689 | 10.0% |
| 10 | 18,560 | 1 - 197,007 | 10.0% |

## stems: log10_freq_bin -> 06_stem_bags_log10_freq_bin.tsv

One bag per factor of 10 in frequency, from the most frequent decade (bag 1) down to the rarest (bag = highest decade - floor(log10(freq)) + 1). The data spans ~10^0 to 10^8, so 9 bags are used.

| bag | stems | band (fixed edges) | observed freq range | % of total freq count |
|---:|---:|---|---|---:|
| 1 | 2 | 100,000,000 to 999,999,999 | 112,983,597 - 175,065,322 | 9.0% |
| 2 | 31 | 10,000,000 to 99,999,999 | 10,071,947 - 54,720,650 | 17.5% |
| 3 | 582 | 1,000,000 to 9,999,999 | 1,006,337 - 9,992,537 | 45.6% |
| 4 | 2,102 | 100,000 to 999,999 | 100,007 - 998,521 | 21.6% |
| 5 | 5,084 | 10,000 to 99,999 | 10,005 - 99,945 | 5.4% |
| 6 | 6,467 | 1,000 to 9,999 | 1,001 - 9,998 | 0.8% |
| 7 | 3,706 | 100 to 999 | 100 - 999 | 0.1% |
| 8 | 1,793 | 10 to 99 | 10 - 99 | 0.0% |
| 9 | 653 | 1 to 9 | 1 - 9 | 0.0% |

# Lemma bags

6,265,299 lemmas in the list, ranked by `freq`

## lemmas: uniform_rank_bin -> 06_lemma_bags_uniform_rank_bin.tsv

Every bag has the same NUMBER of lemmas. Lemmas are ordered by frequency and cut into 10 equal groups (the original Revita definition).

| bag | lemmas | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 626,529 | 20 - 156,017,700 | 99.4% |
| 2 | 626,529 | 7 - 20 | 0.2% |
| 3 | 626,529 | 4 - 7 | 0.1% |
| 4 | 626,529 | 2 - 4 | 0.1% |
| 5 | 626,529 | 2 - 2 | 0.0% |
| 6 | 626,529 | 1 - 2 | 0.0% |
| 7 | 626,529 | 1 - 1 | 0.0% |
| 8 | 626,529 | 1 - 1 | 0.0% |
| 9 | 626,529 | 1 - 1 | 0.0% |
| 10 | 626,538 | 1 - 1 | 0.0% |

## lemmas: uniform_cumfreq_bin -> 06_lemma_bags_uniform_cumfreq_bin.tsv

Every bag covers the same share of the TOTAL freq count (10% each). Lemmas are ordered from most to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the grand total. The first bags hold few lemmas, the last bag holds most of them.

| bag | lemmas | observed freq range | % of total freq count |
|---:|---:|---|---:|
| 1 | 3 | 54,720,650 - 156,017,700 | 11.0% |
| 2 | 13 | 12,957,636 - 48,055,503 | 9.1% |
| 3 | 35 | 5,631,200 - 12,707,829 | 10.0% |
| 4 | 71 | 3,017,955 - 5,508,195 | 10.1% |
| 5 | 139 | 1,477,483 - 3,013,835 | 10.0% |
| 6 | 271 | 785,804 - 1,476,501 | 10.0% |
| 7 | 571 | 347,333 - 783,759 | 10.0% |
| 8 | 1,469 | 119,845 - 346,425 | 10.0% |
| 9 | 6,474 | 19,097 - 119,791 | 10.0% |
| 10 | 6,256,253 | 1 - 19,093 | 10.0% |

## lemmas: log10_freq_bin -> 06_lemma_bags_log10_freq_bin.tsv

One bag per factor of 10 in frequency, from the most frequent decade (bag 1) down to the rarest (bag = highest decade - floor(log10(freq)) + 1). The data spans ~10^0 to 10^8, so 9 bags are used.

| bag | lemmas | band (fixed edges) | observed freq range | % of total freq count |
|---:|---:|---|---|---:|
| 1 | 2 | 100,000,000 to 999,999,999 | 112,983,597 - 156,017,700 | 9.1% |
| 2 | 24 | 10,000,000 to 99,999,999 | 10,078,940 - 54,720,650 | 14.8% |
| 3 | 399 | 1,000,000 to 9,999,999 | 1,000,694 - 9,986,774 | 32.9% |
| 4 | 2,489 | 100,000 to 999,999 | 100,026 - 999,463 | 24.5% |
| 5 | 10,950 | 10,000 to 99,999 | 10,001 - 99,919 | 11.0% |
| 6 | 46,409 | 1,000 to 9,999 | 1,000 - 9,999 | 4.8% |
| 7 | 176,128 | 100 to 999 | 100 - 999 | 1.8% |
| 8 | 765,794 | 10 to 99 | 10 - 99 | 0.7% |
| 9 | 5,263,104 | 1 to 9 | 1 - 9 | 0.4% |
