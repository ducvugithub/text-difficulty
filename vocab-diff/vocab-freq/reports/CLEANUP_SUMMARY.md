# Cleanup steps summary (updated 2026-10-05)

- Scripts: `vocab-diff/vocab-freq/scripts/` (steps 1-8), `vocab-diff/build_features.py` (features of both vocab signals); shared helpers: `vocab-diff/shared/`
- Intermediate files: `cleaned/` (git-ignored)
- Per-step numbers: the `0N_*.md` reports next to this file

**Total count** = the `freq` counts of the rows added up (how often those forms appear in the corpus), not the number of different forms.

### 1. Normalize: `01_normalize.py`
- **Input:** `data/finnish_vocab.txt`, lines `count word`, e.g. `300063 kova`, `217933667 .`
- **Output:** `cleaned/01_normalized.tsv`, e.g. `300063	kova`
- **Steps:** drop
  - digits, punctuation, URLs and forum markup (`&gt`, `author=`)
  - colon/dot forms (`EU:n`, `esim.`)
  - hyphen fragments (`sosiaali-`)
  - words over 45 characters
- **Results:** 44.65M → 36.10M rows (the dropped part of the total count was mostly punctuation)

### 2. Analyze: `02_analyze.py`
- **Input:** `cleaned/01_normalized.tsv`
- **Output:** `cleaned/02_analysis.tsv`, columns `count word readings`
  - reading = `lemma|class|stems` (see [Word classes](#word-classes))
  - `40995	työpaikkojen	työpaikka|nimisana|työ+paikka`
  - `8477348	voi	voi|nimisana|voi;voida|teonsana|voida;...` (ambiguous: several readings)
  - `674945	mä	-` (`-` = not recognised)
- **Steps:** Voikko analysis of every word, 10 workers in parallel (~3 min)
- **Results:** 36.1M words analysed

### 3. Merge lemmas: `03_merge_lemmas.py`
- **Input:** `cleaned/02_analysis.tsv`
- **Output:**
  - `cleaned/03_lemmas.tsv`, columns:
    - `lemma`: dictionary form
    - `class`: Voikko word class
    - `stems`: stems joined by `+` (`työ+paikka`)
    - `n_forms`: inflected forms merged into the lemma
    - `freq`: their counts added up
    - e.g. `talo`: nimisana, stem `talo`, 366 forms, `freq` 1,044,279
  - `cleaned/03_unrecognised.tsv`: top 50k rejected words, for review
- **Steps:**
  - Drop names (Helsingissä), abbreviations and unrecognised words (typos, English, spoken Finnish)
  - Merge forms into lemmas (talo / talon / talossa → talo) and add up the counts
  - Lowercase the lemmas
  - If the analyser returns the same lemma twice for one form, once capitalised and once lowercase (lappeenranta and Lappeenranta), merge them and add the form's count once
  - Ambiguous form with several lemmas: each lemma gets the full count
- **Results:** 36.1M forms → 20.6M kept → 6,459,885 lemmas, none capitalised
  - Dropped: 15.3M unrecognised forms, 206k name forms, 4.2k abbreviation forms

### 4. Stem inventory: `04_compound_stems.py`
- **Input:** `cleaned/03_lemmas.tsv`
- **Output:**
  - `cleaned/04_lemmas_stem.tsv`, columns `lemma class n_stems n_forms freq`
    - `n_stems`: number of stems (2 or more = compound)
    - `työpaikka`: 2 stems; `talo`: 1 stem
  - `cleaned/04_stems.tsv`, columns `stem freq standalone_freq n_lemmas n_compounds`: 26,211 lowercase stems
    - `freq`: full count = the `freq` of every lemma containing the stem, added up
    - `standalone_freq`: the `freq` of the lemma equal to the stem; empty if it never occurs alone
    - `n_lemmas`, `n_compounds`: lemmas / compounds containing it
    - `työ`: `freq` 13,841,006 (standalone 3,418,001, in 95,942 lemmas)
    - `säädäntö`: 356,295, only inside compounds such as lainsäädäntö
    - 223 stems never occur alone; they still have a `freq`
    - Capitalised name stems (Aalto, EU) are left out: "Aamu" is not "aamu"
  - `cleaned/04_compound_stems.tsv`, columns `compound stem stem_freq`: one row per compound × stem (14.7M rows), for auditing
- **Steps:**
  - Voikko gives each lemma its stems; a lemma with 2 or more stems is a compound
  - A stem's `freq` adds up the `freq` of every lemma that contains it
  - Voikko's `=` marker inside a stem (`takaisin=kytkentä`) is unreliable, so it is removed
- **Results:** 6,459,885 lemmas; 6,126,323 compounds; 26,211 stems

### 5. Rank and filter English-looking words: `05_rank_and_filter.py`
- **Helpers:** `english_borrowing.py`, `wiktionary.py`
- **Input:** `cleaned/04_lemmas_stem.tsv`, `04_stems.tsv`, `03_lemmas.tsv`, `05_translations.tsv`
  - **One-time download** of the Wiktionary Finnish dump (kaikki.org, 4.6 GB, ~20 min, CC BY-SA). The entries of our stems are saved in `cleaned/05_wiktionary_entries.jsonl`; `05_translations.tsv` is rebuilt from that file in seconds. The dump is downloaded only when the entries file is missing (`--refetch` redoes it)
  - `05_translations.tsv`, columns `stem english english_all etymology en_source`
    - `english`: single-word English translations of the stem's **first meaning** only (a later meaning can be unrelated: puku = suit, but also an antelope)
    - `english_all`: translations of all meanings, for reference
    - `etymology`: tags such as `bor:sv` (borrowed from Swedish), `der:la` (derived from Latin), `inh:urj-fin-pro` (inherited from Proto-Finnic); taken from the same entry as the first meaning
    - `en_source`: the English source word when the etymology says borrowed from English (biisi ← piece)
- **Output:**
  - `cleaned/05_lemma_freq.tsv`, columns `rank lemma class n_stems n_forms freq`: final lemma list
  - `cleaned/05_stem_freq.tsv`, columns `rank stem freq standalone_freq n_lemmas n_compounds`: final stem list, ranked by `freq`
  - `cleaned/05_stem_borrowing.tsv`, columns `stem freq english english_from edit_score norm borrowed reason etymology`: audit of every judged stem; tagged first, most frequent first
    - `english`: the English word the stem was scored against; `english_from`: `translation` (first meaning) or `etymology` (the English source word, for stems tagged only by `bor:en`)
    - `edit_score`: weighted edit distance; `norm`: edit score / longer word length × 100
    - `borrowed`: 1 = tagged English-looking
    - `reason`: `edit score`; `bor:en` (etymology says borrowed from English); `native etymology` (a rule fired, but the stem is inherited from Proto-Finnic / Uralic, so not tagged)
- **Steps:**
  - **Find the translation** of every lowercase stem (26,211 stems)
  - **Calculate the edit score** between the stem and its translation
    - a normal edit (insert, delete, change a letter) costs 1
    - the usual changes Finnish makes when it borrows a word cost 0.2: final -i, doubled letters, k/c, f/ph, ... (from the team sheet)
    - `norm` = edit score / length of the longer word × 100
  - **Rules to filter English-looking stems**
    - tag the stem when `norm` is at most 35
    - tag it also when Wiktionary says it was borrowed from English
    - do not tag it when Wiktionary says it is inherited Finnish
    - skip stems with no translation, very short stems and names
  - **Lemmas:** a lemma counts as English-looking when all its stems are English-looking, and is removed
  - **Then:** sort lemmas and stems by `freq` and add `rank`
- **Results:**

  | | before | tagged / removed | final |
  |---|---:|---:|---:|
  | stems | 26,211 | 5,507 | 20,704 |
  | lemmas | 6,459,885 | 176,702 (3.35% of all lemma counts) | 6,283,183 |

  - Stems: 24,337 found in Wiktionary, 19,145 with a translation; of the 5,507 tagged, 5,415 by edit score and 92 only by etymology
  - Checked by hand: pulla, puku, kissa, rotta, mutta, todeta, kerma are not tagged; kämppä, biisi, tiimi, taksi, okei are tagged by etymology; radio, euro by edit score
  - Calibration: every borrowed pair of the sheet scores 33.3 or less, every native pair 50 or more (`reports/05_rank_and_filter.md`)
- **Caveats:**
  - A tag means "looks like its English translation" or "Wiktionary says borrowed from English". It also catches loans that came through Swedish, Latin or Greek and some Germanic cognates (merkki, linja)
  - About 1,900 stems have no Wiktionary entry, and others no usable translation; they stay in the lists
  - The cost table is generous: a short word with two or three 0.2 edits can pass at 35

### 6. Build bags (stems and lemmas): `06_build_bags.py`
- **Input:** `cleaned/05_stem_freq.tsv` (20,420 stems), `05_lemma_freq.tsv` (6.27M lemmas)
- **Output:** `cleaned/06_stem_bags_{method}.tsv`, `06_lemma_bags_{method}.tsv`, columns `stem` or `lemma`, `freq`, `bag`
  - `freq`: a stem's full count, or a lemma's own count
  - `bag`: 1 = most frequent, highest number = rarest
  - `olla 175065322 1` (stem), `olla 156017700 1` (lemma)
- **Steps:** cut each ranked list into bags with `--bag-method` (default: all three)
  - `uniform_rank_bin`: same number of items per bag (2,042 stems each); bag 1 still holds 91% of the stem count
  - `uniform_cumfreq_bin`: each bag covers 10% of the total count. Items go from most to least frequent with a running total; a new bag starts at every 10%
  - `log10_freq_bin`: one bag per factor of 10; 9 bags
    - fixed bands, same for stems and lemmas: bag b covers `10^(9-b)` to `10^(10-b) - 1`
    - the bag depends only on the item's own count, never on the rest of the list

    | bag | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
    |---|---|---|---|---|---|---|---|---|---|
    | count | 100M+ | 10M–99.9M | 1M–9.99M | 100k–999k | 10k–99,999 | 1k–9,999 | 100–999 | 10–99 | 1–9 |
    | lemmas | 2 | 25 | 401 | 2,502 | 11,012 | 46,629 | 176,769 | 768,222 | 5,277,621 |
    | stems | 2 | 32 | 584 | 2,119 | 5,143 | 6,580 | 3,787 | 1,802 | 655 |

    - example: count 1,184,221 → bag 3
- **Results:** per-bag counts, ranges and % of total count: `reports/06_build_bags.md`
  - `uniform_cumfreq_bin`: bag 1 = 3 stems / 3 lemmas (olla, ja, se) holding about 11%; bag 10 = 18,560 stems / 6.26M lemmas holding 10%

### 7. Text features (stem and lemma bins): `07_text_features.py`
- **Input:** train/valid/test CSVs (`text` column), the bins, the English-looking stems
- **Options** (per level): `--lemma-bin-method` (default `log10_freq_bin`), `--stem-bin-method` (default `uniform_cumfreq_bin`), `--lemma-n-bins`, `--stem-n-bins` (default 10)
  - `n_bins` is a maximum: `log10_freq_bin` gives one bin per decade (9 here) and merges the rarest decades into the last bin when `n_bins` is smaller
- **Output:** `outputs/vocab_features_{train,valid,test}.csv`, columns `row`, `label`, then per level (`stem_`, `lemma_`)
  - `{level}_OOV_coverage`: share of units that are unknown
  - `{level}_borrowed_coverage`: share of English-looking units (not OOV)
  - `{level}_bag_1..N_coverage`: share of units per bin (1 = most frequent)
  - `mean_log_{level}_freq`: mean log10 count of the units in a bin
- **Steps:**
  - Voikko analyses each word (no context)
  - **Lemma level:** a unit is a word, placed by the count of its lemma
  - **Stem level:** a word is split into its stems and every stem is a unit, placed by its own stem count (työpaikka = työ + paikka = 2 units); no "rarest stem" rule
  - Lemma or stems removed in step 5 → `borrowed`, not OOV
  - Word Voikko does not recognise (1 unit), or lemma / stem not in the list → OOV
  - Names and abbreviations are skipped
  - Every table: all rows and Finnish-native-only rows
- **Results** (default bins; train, all rows; the four shares add up to 100% of the units):

  | level | units | in bin | borrowed | OOV: Voikko-unknown | OOV: not in list | skipped (% of words) |
  |---|---:|---:|---:|---:|---:|---:|
  | stem | 1,292,989 | 91.9% | 4.5% | 3.5% | 0.2% | 3.5% |
  | lemma | 1,183,525 | 92.4% | 3.7% | 3.8% | 0.1% | 3.5% |

  - Per-text-avg-oov (stem / lemma): train all 4.9% / 5.1%; train native 3.6% / 4.0%; test 3.5% / 3.8%
  - Old pipeline: 22.4% (train all), 27.9% (train native)
  - By-label tables: `07_text_features.md`

### 8. Compare variants (stem and lemma bins): `08_compare_variants.py`
- **Input:** the bins, 5,000 sampled train texts (all 2,332 native rows for the native subset)
- **Output:** `reports/08_compare_variants.md`, columns `level subset texts bag_method rho_mean_log_freq rho_OOV_coverage rho_mean_bag rho_borrowed_coverage`
  - `rho_*`: Spearman correlation with the difficulty label
  - `mean_bag`: average bin number of the units in a bin (higher = rarer)
- **Steps:** build the vocab features per bin method, correlate with the label
- **Results:**

  | level | subset | bin method | rho mean_log_freq | rho OOV_coverage | rho mean_bag | rho borrowed_coverage |
  |---|---|---|---:|---:|---:|---:|
  | stem | all | uniform_rank_bin | -0.293 | +0.045 | +0.208 | +0.260 |
  | lemma | all | uniform_rank_bin | -0.441 | +0.075 | +0.362 | +0.234 |
  | stem | all | uniform_cumfreq_bin | -0.293 | +0.045 | +0.297 | +0.260 |
  | lemma | all | uniform_cumfreq_bin | -0.441 | +0.075 | +0.414 | +0.234 |
  | stem | all | log10_freq_bin | -0.293 | +0.045 | +0.295 | +0.260 |
  | lemma | all | log10_freq_bin | -0.441 | +0.075 | **+0.446** | +0.234 |
  | stem | native only | uniform_rank_bin | -0.168 | +0.233 | +0.121 | +0.213 |
  | lemma | native only | uniform_rank_bin | -0.373 | +0.278 | +0.323 | +0.199 |
  | stem | native only | uniform_cumfreq_bin | -0.168 | +0.233 | +0.174 | +0.213 |
  | lemma | native only | uniform_cumfreq_bin | -0.373 | +0.278 | +0.354 | +0.199 |
  | stem | native only | log10_freq_bin | -0.168 | +0.233 | +0.145 | +0.213 |
  | lemma | native only | log10_freq_bin | -0.373 | +0.278 | **+0.370** | +0.199 |

  - Lemma bins beat stem bins in every row: `mean_bag` +0.446 vs +0.297 (all), +0.370 vs +0.174 (native)
  - Best bin method: `log10_freq_bin` for lemmas, `uniform_cumfreq_bin` for stems; `uniform_rank_bin` is the weakest
  - `borrowed_coverage` is positive: harder texts have more English-looking units, not fewer

### 9. Vocab text features: `vocab-diff/build_features.py`
- **Input:** train/valid/test CSVs (`text` column), `05_lemma_freq.tsv` (to pick the lemma of an ambiguous word)
- **Output:** `outputs/vocab_text_features_{train,valid,test}.csv`: `row`, `label`, one column per feature (definitions: `docs/features.md`)
  - `n_unique_lemmas`, `ttr_lemma_200` (distinct lemmas among the first 200 / 200)
  - `avg_word_length`, `long_word_ratio` (10 or more characters)
  - `compound_ratio`, `avg_compound_parts`, `n_compound_tokens`: compounds (2 or more stems) among content words
  - `deriv_llinen_ratio`, `deriv_ton_ratio`: Voikko derivation suffixes
  - `deriv_minen_ratio`, `deriv_sti_ratio`: heuristics (Voikko treats these as inflection)
  - plus the step 7 bag features
- **Steps:** `VocabDiffFeatureConstruct` (`vocab-diff/vocab_construct.py`, called through `TextDiffFeaturesConstruct` in `builder.py`) composes two signals: the frequency bins (`vocab-freq/freq_features.py`) and the lexical features (`lexical/lexical_features.py`); the correlation report is `vocab-diff/reports/vocab_features.md`
- **Results** (Spearman with the label, train, all rows / native only):
  - `n_compound_tokens` +0.53 / +0.50
  - `avg_word_length` +0.50 / +0.50
  - `long_word_ratio` +0.48 / +0.49
  - `n_unique_lemmas` +0.41 / +0.36
  - The count-based ones also grow with text length

## Word classes

`class` = the part of speech Voikko assigns to a lemma (Finnish terms).
- Used only to drop names, abbreviations and prefix fragments; the counts do not depend on it
- With several readings, the first one Voikko lists is kept

In `04_lemmas_stem.tsv` (6,459,885 lemmas):

| class | meaning | lemmas | example |
|---|---|---:|---|
| `nimisana` | noun | 5,613,904 | talo, työpaikka |
| `laatusana` | adjective | 715,623 | kaunis |
| `teonsana` | verb | 81,123 | olla |
| `nimisana_laatusana` | noun and adjective | 39,772 | |
| `seikkasana` | adverb | 7,778 | myös |
| `lukusana` | numeral | 1,560 | kaksi |
| `huudahdussana` | interjection | 42 | voi! |
| `asemosana` | pronoun | 29 | se, joka |
| `sidesana` | conjunction | 27 | ja, mutta |
| `suhdesana` | adposition | 17 | |
| `kieltosana` | negation word | 10 | ei |

Dropped earlier:

| class | meaning | dropped in |
|---|---|---|
| `nimi`, `etunimi`, `sukunimi`, `paikannimi` | proper names (Pekka, Helsinki) | step 3 |
| `lyhenne` | abbreviation (EU, km) | step 3 |
| `etuliite` | prefix fragment (koulu-) | step 1 |

## Open points
- **Stem or lemma bins:** both are built as separate feature sets. Lemma bins correlate better (step 8); the stem bins are meant to add to them, not replace them. Not yet tested together in a model
- **Names inside stems:** a capitalised stem is dropped, so the counts of its lowercase parts are slightly too low. Not fixed
- **English filter:** the cost table is generous, so some stems may still pass by accident; the audit file `05_stem_borrowing.tsv` is the place to check
- **TODO: context-aware analyser for the text side.** Steps 7-9 use Voikko without context; an ambiguous word gets the candidate lemma with the highest list frequency. Plan: Stanza picks among Voikko's candidates (see below). The step 7-9 numbers will change
- Spoken Finnish (mun, mä, oon) is dropped as unrecognised and counts as OOV in text

---

# Which analyser where: Voikko for the list, Stanza for the text

Decided 2026-10-03.

## Decision
| side | input | analyser | why |
|---|---|---|---|
| Frequency list (steps 1-6) | `finnish_vocab.txt`: words and counts, **no sentences** | **Voikko** only | No context exists to use. Stanza on isolated words is the same guess, slower. Voikko also gives the stems and runs 36M words in ~3 min |
| Text side: train/valid/test (steps 7-9) | full sentences | **Stanza** (Finnish) to disambiguate, Voikko for the candidate lemmas | Context picks the right reading ("voi" butter or can, "sinä" → sinä or se) |

## How the text side would combine them (planned, not built)
1. Voikko lists the candidate lemmas of a token.
2. Stanza lemmatizes the token in its sentence.
3. If Stanza's lemma is one of Voikko's candidates, use it. Otherwise use the candidate with the highest list frequency (today's rule).
4. The list keeps Voikko's lemma spellings, so Stanza's conventions cannot cause fake OOV.

Rejected: Stanza lemmas directly. Closer to the old Revita features, but the spellings differ from the Voikko list and would inflate OOV.

## Status
- Steps 1-9 use Voikko only, including the text side (no context)
- To do: install Stanza and the Finnish model (a few hundred MB), run once over the 3 splits (~10-30 min CPU), cache it, switch `text_common.py` and steps 7-9 to it
- Open: which parser gave the lemmas in the old features (Stanza or Turku)? If known, match its choice

## Voikko facts
- Rule-based finite-state analyser (`libvoikko` 4.3.3 via Homebrew), not a trained model. Deterministic, no context, returns every reading of an ambiguous word
- Needs a UTF-8 locale (`LC_ALL=en_US.UTF-8`), or it silently rejects every word with ä/ö. `common.run_voikko` sets it
- Misses by design: spoken Finnish (mun, mä, oon, ku, mut), most typos, English. These count as OOV in text
- A capitalised name that also has a common-word reading is counted as the common word
