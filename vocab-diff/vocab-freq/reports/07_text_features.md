# 07 text features / OOV check
- variant rarest_stem_freq, top-n 20000 (20,000 binned lemmas, 6,501,706 in full list), names: skip

| split | texts | tokens | OOV old | OOV new | in bag | unrecognised | listed beyond top-n | name/abbrev (skipped) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 8,293 | 1,226,757 | 0.224 | 0.542 | 43.6% | 3.6% | 49.1% | 3.5% |
| valid | 1,011 | 141,641 | 0.225 | 0.545 | 44.1% | 3.8% | 48.3% | 3.7% |
| test | 865 | 264,256 | 0.281 | 0.583 | 41.1% | 3.5% | 50.9% | 4.3% |

## Type-level overlap (unique lemmas / unrecognised forms)

| split | recognised lemma types | in full list | in bags | unrecognised form types |
|---|---:|---:|---:|---:|
| train | 45,918 | 44,548 | 614 | 19,919 |
| valid | 12,876 | 12,708 | 331 | 3,311 |
| test | 21,521 | 21,217 | 386 | 4,715 |

## By label

### train: mean OOV_coverage by label

| label | texts | OOV new |
|---|---:|---:|
| 1.0 | 241 | 0.497 |
| 1.5 | 342 | 0.617 |
| 2.0 | 595 | 0.489 |
| 2.5 | 75 | 0.468 |
| 3.0 | 2820 | 0.460 |
| 3.5 | 1836 | 0.638 |
| 4.0 | 772 | 0.526 |
| 5.0 | 493 | 0.566 |
| 5.5 | 976 | 0.604 |
| 6.0 | 143 | 0.637 |

### valid: mean OOV_coverage by label

| label | texts | OOV new |
|---|---:|---:|
| 1.0 | 27 | 0.497 |
| 1.5 | 32 | 0.593 |
| 2.0 | 90 | 0.488 |
| 2.5 | 13 | 0.568 |
| 3.0 | 320 | 0.466 |
| 3.5 | 248 | 0.642 |
| 4.0 | 95 | 0.518 |
| 5.0 | 69 | 0.576 |
| 5.5 | 102 | 0.595 |
| 6.0 | 15 | 0.616 |

### test: mean OOV_coverage by label

| label | texts | OOV new |
|---|---:|---:|
| 1.5 | 32 | 0.522 |
| 2.0 | 98 | 0.504 |
| 3.0 | 60 | 0.551 |
| 3.5 | 183 | 0.595 |
| 4.0 | 48 | 0.543 |
| 5.0 | 59 | 0.613 |
| 5.5 | 340 | 0.601 |
| 6.0 | 45 | 0.666 |
