# lexical: word-form signal

`lexical_features.py` (`LexicalFeatures`): features of how the words in a text are built. Needs only Voikko and the lemma list.
- lexical diversity: `n_unique_lemmas`, `ttr_lemma_200`
- word form: `avg_word_length`, `long_word_ratio`
- compounding: `compound_ratio`, `avg_compound_parts`, `n_compound_tokens`
- derivation: `deriv_llinen_ratio`, `deriv_ton_ratio`, `deriv_minen_ratio` and `deriv_sti_ratio` (the last two are heuristics: Voikko treats -minen and -sti as inflection)

Definitions: `docs/features.md`. Correlations with the label: `../reports/vocab_features.md` (written by `../build_features.py`).
