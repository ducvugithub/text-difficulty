# Text-difficulty features by category

text-diff = vocab + grammar + cognitive. Rule of thumb for where a feature lives:
- **vocab**: a property of the words themselves (frequency, length, how a word is built)
- **grammar**: which structures and forms a sentence uses
- **cognitive**: how much the reader has to hold in mind (length, nesting, distance)

The feature list comes from the older `data/*Features.csv` / `*_document_features.csv` (computed there with a UD parser, train only).
Status: **done** = implemented here for all splits, **todo** = not implemented yet.

## Vocab (`vocab-diff`)

| feature | meaning | status |
|---|---|---|
| `stem_*` and `lemma_*`: `{level}_OOV_coverage`, `{level}_borrowed_coverage`, `{level}_bag_k_coverage`, `mean_log_{level}_freq` | share of unknown units / of English-looking units / of units per frequency bin (1 = most frequent); stem level: every stem of a word is a unit placed by its own stem count, lemma level: the word is placed by its lemma | done (step 7, `VocabDiffFeatureConstruct`) |
| `n_unique_lemmas` | distinct lemmas in the text (grows with text length) | done (step 9) |
| `ttr_lemma_200` | distinct lemmas among the first 200 lemmas / 200 (length-controlled diversity) | done (step 9) |
| `avg_word_length` | mean characters per word | done (step 9) |
| `long_word_ratio` | share of words with 10 or more characters | done (step 9) |
| `compound_ratio` | compounds (2+ stems) / content words | done (step 9) |
| `avg_compound_parts` | mean number of stems per compound | done (step 9) |
| `n_compound_tokens` | number of compound words | done (step 9) |
| `deriv_llinen_ratio` | `-llinen` (noun to adjective, asia -> asiallinen) / content words | done (step 9, Voikko suffix marker) |
| `deriv_ton_ratio` | `-ton` (without, merkitys -> merkityksetön) / content words | done (step 9, Voikko suffix marker) |
| `deriv_minen_ratio` | `-minen` (verb to noun, arvioida -> arvioiminen) / content words | done (step 9, **heuristic**: verb lemma + a -mi- noun ending) |
| `deriv_sti_ratio` | `-sti` (adjective to adverb, erityinen -> erityisesti) / content words | done (step 9, **heuristic**: word ends in -sti and its lemma is an adjective) |

Borderline: the derivational ratios could also sit in grammar (morphology). Kept in vocab because they describe how a word is built.

## Grammar (`grammar-diff`)

| feature | meaning | status |
|---|---|---|
| `avg_sentence_length`, `std_sentence_length`, `max/min_sentence_length` | sentence length (borderline with cognitive) | todo |
| `avg_morph_feats_per_token`, `n_unique_morph_feat_types` | morphological complexity | todo |
| `case_ratio_*` (nom, gen, par, ...), `case_ratio_oblique`, `case_entropy` | case usage | todo |
| `mood_ratio_cnd`, `mood_ratio_pot`, `passive_ratio`, `nonfinite_verb_ratio`, `negation_ratio` | rare verb forms and constructions | todo |
| `avg_clauses_per_sent`, `avg_subord_per_sent` | clause structure | todo |

## Cognitive (`cognitive-diff`)

| feature | meaning | status |
|---|---|---|
| `avg_dep_length` | mean dependency distance, a working-memory measure (Gibson 1998) | todo |
| `avg_max_dep_depth` | mean maximum depth of the dependency tree (borderline with grammar) | todo |
| `n_sentences`, `n_tokens` | text length / reading load | todo |

## Cautions
- Length-dependent features (`n_tokens`, `n_sentences`, `n_unique_lemmas`, `max_sentence_length`) can pick up the source or split instead of difficulty: test texts are much longer (median 229 words vs 65 in train). Prefer the normalised ones (`ttr_lemma_200`, the ratios, the averages).
- About 72% of train and 74% of valid are Russian-origin (translated) rows; test is all real Finnish. Check every feature on `finnish-native-only` as well as `all`.
- `ttr_lemma_200` is not length-controlled for texts under 200 words (it then uses all their lemmas), so short texts get a high value; its correlation flips sign between `all` (-0.20) and `finnish-native-only` (+0.30).
- Compared with the old document-features file (train): the row order differs, so rows cannot be matched, but the means are close (e.g. `avg_word_length` 6.88 vs 7.11, `n_unique_lemmas` 85.5 vs 90.0). `compound_ratio` is lower here (0.088 vs 0.122): Voikko's compounds are not the same as the parser's.
- Parser-based features (grammar, cognitive) need a dependency parser (Stanza / Turku); the vocab ones here need only Voikko.
- Ideas not in the old list: rarest-10%-of-words frequency, hapax share, loanword share, connectives per sentence, adjacent-sentence lexical overlap, LM surprisal, named-entity share.
