# 05 rank
- lemmas: 6,501,706 in, 6,501,706 out (sorted by freq, min-freq 0) -> lemma_freq.tsv
- lemmas by rank: top 1,000: freq>=412,668, top 10,000: freq>=18,835, top 20,000: freq>=6,678, top 100,000: freq>=482
- stems: 22,627 ranked by freq + 5,996 with no standalone freq (listed last, no rank) -> stem_freq.tsv

Columns of lemma_freq.tsv: `rank` position in the sorted list (1 = most frequent); `lemma`; `class` Voikko word class; `n_stems` number of stems; `n_forms` forms merged into the lemma; `freq` all forms added up; `rarest_stem_freq` `freq` of the rarest stem for compounds (= `freq` otherwise).

Columns of stem_freq.tsv: `rank` position by `freq` (empty if the stem never occurs as its own word); `stem`; `freq` its standalone lemma frequency; `n_compounds` compounds containing it.
