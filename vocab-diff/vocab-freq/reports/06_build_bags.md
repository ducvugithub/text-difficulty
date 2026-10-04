# 06 build bags
- frequency column: `freq`; 6,501,706 lemmas in the list
- bag 1 = rarest ... highest bag = most frequent
- columns of vocab_bags_{method}.tsv: `lemma`; `freq` the value of the frequency column; `bag` the bag number

## uniform_rank_bin -> vocab_bags_uniform_rank_bin.tsv

Every bag has the same NUMBER of lemmas. Lemmas are ordered by frequency and cut into 10 equal groups (original Revita definition, but over the whole list).

| bag | lemmas | freq range | % of total freq count |
|---:|---:|---|---:|
| 10 | 650,176 | 20 - 156,017,700 | 99.4% |
| 9 | 650,170 | 7 - 20 | 0.2% |
| 8 | 650,170 | 4 - 7 | 0.1% |
| 7 | 650,170 | 2 - 4 | 0.1% |
| 6 | 650,170 | 2 - 2 | 0.0% |
| 5 | 650,170 | 1 - 2 | 0.0% |
| 4 | 650,170 | 1 - 1 | 0.0% |
| 3 | 650,170 | 1 - 1 | 0.0% |
| 2 | 650,170 | 1 - 1 | 0.0% |
| 1 | 650,170 | 1 - 1 | 0.0% |

## uniform_cumfreq_bin -> vocab_bags_uniform_cumfreq_bin.tsv

Every bag covers the same share of the TOTAL freq count (10% each). Lemmas are ordered from most to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the grand total. The top bags hold few lemmas, the bottom bag holds millions.

| bag | lemmas | freq range | % of total freq count |
|---:|---:|---|---:|
| 10 | 3 | 54,720,650 - 156,017,700 | 10.5% |
| 9 | 15 | 12,707,829 - 48,055,503 | 9.6% |
| 8 | 39 | 5,412,591 - 12,650,659 | 10.0% |
| 7 | 78 | 2,898,871 - 5,302,826 | 9.9% |
| 6 | 158 | 1,392,615 - 2,884,576 | 10.0% |
| 5 | 309 | 708,442 - 1,391,607 | 10.0% |
| 4 | 667 | 311,233 - 707,825 | 10.0% |
| 3 | 1,728 | 104,905 - 311,225 | 10.0% |
| 2 | 7,521 | 17,415 - 104,886 | 10.0% |
| 1 | 6,491,188 | 1 - 17,412 | 10.0% |

## log10_freq_bin -> vocab_bags_log10_freq_bin.tsv

One bag per factor of 10 in frequency: bag = floor(log10(freq)) + 1 (freq 1-9 -> bag 1, 10-99 -> bag 2, ...). The data spans ~10^0 to 10^8, so 9 bags are used.

| bag | lemmas | freq range | % of total freq count |
|---:|---:|---|---:|
| 9 | 2 | 112,983,597 - 156,017,700 | 8.7% |
| 8 | 25 | 10,078,940 - 54,720,650 | 14.8% |
| 7 | 408 | 1,000,694 - 9,986,774 | 32.0% |
| 6 | 2,671 | 100,026 - 999,463 | 24.9% |
| 5 | 12,168 | 10,000 - 99,948 | 11.7% |
| 4 | 50,164 | 1,000 - 9,999 | 5.0% |
| 3 | 185,230 | 100 - 999 | 1.8% |
| 2 | 797,932 | 10 - 99 | 0.7% |
| 1 | 5,453,106 | 1 - 9 | 0.4% |
