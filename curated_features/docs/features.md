# Text-difficulty features by category

text-diff = vocab + grammar + cognitive. Rule of thumb for where a feature lives:
- **vocab**: a property of the words themselves (frequency, length, how a word is built)
- **grammar**: which structures and forms a sentence uses
- **cognitive**: how much the reader has to hold in mind (length, nesting, distance)

The feature list comes from the older `data/*Features.csv` / `*_document_features.csv` (computed there with a UD parser, train only).
Status: **done** = implemented here for all splits, **todo** = not implemented yet.

## Vocab (`curated_features/categories/vocab`)

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

## Grammar (`curated_features/categories/grammar`)

Grammar items are Revita's concepts (268 counted, e.g. `Case-Illative`, `Noun-Paradigm-talo`) and syllabus topics (133, e.g. "All possessive forms"). Counts come from the precomputed Revita columns of the splits, or from Revita's own pipeline for new texts (`source="analyser"`). Each signal works on one kind of item.

| signal | features | meaning | status |
|---|---|---|---|
| `manual_concepts_levels` | `grammar_concept_level_{A1, A1_A2, A1_B1, A2, A2_B1, B1, B1_B2, B2}` | share of the text's levelled concept occurrences at each CEFR level, from Revita's manual levels; concepts without a level are not counted | done |
| `manual_topics_levels` | `grammar_topic_level_{A1, A2, B1, B2}` | the same for syllabus topics (the sublevel is dropped, A1.3 -> A1) | done |
| `rarity_concepts`, `rarity_topics` | `grammar_{kind}_rarity_bag_k`, `..._rarity_unseen`, `..._mean_idf` | rarity: how often each item occurs in Revita's 10,221 Finnish stories (`reference/`), as bin shares (bin 1 = most common), the share of items missing from the reference, and the mean IDF | done |
| `coverage_concepts`, `coverage_topics` | `grammar_{kind}_cov_<item>` (268 + 133) | the share of each concept / topic in the text, one feature per item, no guess about which are hard; topic counts are turned into shares | done |

Covered by `coverage_concepts` and no longer separate to-dos: case ratios, mood and passive ratios, non-finite verb forms, negation (the `Case-*`, `Mood-*`, `Voice-*`, `Infinitive-*`, `Participle-*`, `Polarity-*` concepts). Still todo: morphological feature counts per token (`avg_morph_feats_per_token`, `n_unique_morph_feat_types`).

**The experiments use the concept signals only.** The topic signals (`manual_topics_levels`, `rarity_topics`, `coverage_topics`) stay registered but are not used in any feature set: the topic features add nothing once the concepts are there (see `modeling/reports/GRAMMAR_CONCEPTS_VS_TOPICS.md`).

Listening exercises (`Topic: Listen ...`, `Listening-*`) are Revita exercise types, not grammar, and are never counted.

## Cognitive (`curated_features/categories/cognitive`)

| signal | features | meaning | status |
|---|---|---|---|
| `sentence_length` | `cognitive_sent_{n_sentences, mean_len, max_len, std_len}` | sentence count and length in words, from a plain sentence split (no parser) | done |
| `parse_old` | `cognitive_parse_{tree_depth, distinct_pos, sentence_length}` | the three syntax columns Revita's pipeline computed (average tree depth, distinct POS per sentence, tokens per sentence); splits only | done |
| `dependency` | `cognitive_dep_{mean_tree_depth, max_tree_depth, mean_distance, max_distance, clauses_per_sentence, subordinate_per_sentence, mean_distinct_pos}` | tree depth, dependency distance (Gibson 1998), clauses (finite verbs) and subordinate clauses per sentence, from the Turku parser | code written, **not run on the splits** (needs the parser server and takes hours) |

## Where features are registered
`curated_features/utils/registry.py` lists every signal; `curated_features/modeling/feature_sets.py` defines the named feature sets an experiment compares; `curated_features/scripts/build_features.py` builds and caches the features (`python curated_features/scripts/build_features.py --list`).

## Cautions
- Length-dependent features (`n_tokens`, `n_sentences`, `n_unique_lemmas`, `max_sentence_length`) can pick up the source or split instead of difficulty: test texts are much longer (median 229 words vs 65 in train). Prefer the normalised ones (`ttr_lemma_200`, the ratios, the averages).
- About 72% of train and 74% of valid are Russian-origin (translated) rows; test is all real Finnish. Check every feature on `finnish-native-only` as well as `all`.
- `ttr_lemma_200` is not length-controlled for texts under 200 words (it then uses all their lemmas), so short texts get a high value; its correlation flips sign between `all` (-0.20) and `finnish-native-only` (+0.30).
- Compared with the old document-features file (train): the row order differs, so rows cannot be matched, but the means are close (e.g. `avg_word_length` 6.88 vs 7.11, `n_unique_lemmas` 85.5 vs 90.0). `compound_ratio` is lower here (0.088 vs 0.122): Voikko's compounds are not the same as the parser's.
- Only `cognitive.dependency` needs a dependency parser (the Turku parser Revita uses); vocab needs Voikko, grammar the Revita analyser or its precomputed columns.
- The cognitive length features look strong in the experiments (7 features alone reach test MAE 0.34, better than the 402 original features) but may be shortcuts: test texts are much longer than train texts and sentence count / length follow the source. Not yet checked within a single source.
- Ideas not in the old list: rarest-10%-of-words frequency, hapax share, loanword share, connectives per sentence, adjacent-sentence lexical overlap, LM surprisal, named-entity share.
