# 04 compound stems
- lemmas: 6,459,885; compounds (2 or more stems): 6,126,323
- distinct lowercase stems: 26,211; never occurring as their own word: 223

Columns of `04_lemmas_stem.tsv`:
- `lemma`
- `class`: Voikko word class
- `n_stems`: number of stems (2 or more = compound)
- `n_forms`: inflected forms merged into the lemma
- `freq`: all its forms added up (from step 3)

Columns of `04_stems.tsv`:
- `stem`
- `freq`: full count = the `freq` of every lemma containing the stem, added up
- `standalone_freq`: the `freq` of the lemma equal to the stem, empty if it never occurs as its own word
- `n_lemmas`: lemmas containing it
- `n_compounds`: compounds containing it

Columns of `04_compound_stems.tsv` (one row per compound x stem, for auditing):
- `compound`
- `stem`
- `stem_freq`: that stem's standalone `freq`
