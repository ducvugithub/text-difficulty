# 05 finalize
- final lemmas: 6,501,706 -> lemma_freq.tsv (sorted by rarest_stem_freq, min-freq 0)
- lemmas by rank: top 1,000: freq>=5,128,973, top 10,000: freq>=2,803,525, top 20,000: freq>=2,017,124, top 100,000: freq>=968,887

Columns of lemma_freq.tsv: `rank` position in the sorted list (1 = most frequent); `lemma`; `class` Voikko word class; `n_stems` number of stems; `n_forms` forms merged into the lemma; `freq` all forms added up; `rarest_stem_freq` `freq` of the rarest stem for compounds (= `freq` otherwise).

| dropped | lemmas | examples |
|---|---:|---|
