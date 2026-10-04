# Cleanup steps summary (run 2026-10-03)

Scripts in `vocab-diff/scripts/`, intermediate files in `cleaned/` (git-ignored), per-step numbers in the `0N_*.md` reports next to this file.

### 1. Normalize: `01_normalize.py`
- **Input:** `data/finnish_vocab.txt`, lines `count word`, e.g. `300063 kova`, `217933667 .`
- **Output:** `cleaned/01_normalized.tsv`, e.g. `300063	kova`
- **Steps:**
  - Drop digits, punctuation, URLs/forum markup (`&gt`, `author=`)
  - Drop colon/dot forms (`EU:n`, `esim.`), hyphen fragments (`sosiaali-`), words >45 chars
- **Results:** 44.65M → 36.10M rows (dropped tokens were mostly punctuation)

### 2. Analyze: `02_analyze.py`
- **Input:** `cleaned/01_normalized.tsv`
- **Output:** `cleaned/02_analysis.tsv`, `count word readings`, e.g.
  - `40995	työpaikkojen	työpaikka|nimisana|työ+paikka` (reading = `lemma|class|stems`, see [Word classes](#word-classes))
  - `8477348	voi	voi|nimisana|voi;voida|teonsana|voida;...` (ambiguous: several readings)
  - `674945	mä	-` (`-` = not recognised)
- **Steps:** Voikko analysis of every word, parallel on 10 workers (~3 min)
- **Results:** 36.1M words analysed

### 3. Merge lemmas: `03_merge_lemmas.py`
- **Input:** `cleaned/02_analysis.tsv`
- **Output:**
  - `cleaned/03_lemmas.tsv`, columns: `lemma class stems n_forms freq`
    - `lemma`: dictionary form
    - `class`: Voikko word class (see [Word classes](#word-classes))
    - `stems`: stems it is built from, joined by `+` (`työ+paikka`)
    - `n_forms`: how many inflected forms were merged into the lemma
    - `freq`: all those forms' counts added up
    - e.g. `talo`: nimisana, stem `talo`, 366 forms, `freq` 1,044,279
  - `cleaned/03_unrecognised.tsv`: top 50k rejected words, for review
- **Steps:**
  - Forms → lemmas (talo/talon/talossa → talo), counts added up into `freq`
  - Names and abbreviations are dropped first, then lemmas are lowercased and readings of one form that differ only by case are one lemma, counted once (lappeenranta / Lappeenranta used to be two lemmas with the same 94,626 count). Capitalised lemmas left: 0
  - Drop names (Helsingissä), abbreviations, unrecognised words (typos, English, spoken Finnish)
  - Ambiguous words with multiple lemmas: each lemma gets the full count
- **Results:** 36.1M forms → 20.6M kept → 6,459,885 lemmas
  - Dropped: 15.3M unrecognised forms, 206k name forms, 4.2k abbreviation forms

### 4. Compound stems: `04_compound_stems.py`
- **Input:** `cleaned/03_lemmas.tsv`
- **Output:**
  - `cleaned/04_lemmas_stem.tsv`, columns: `lemma class n_stems n_forms freq rarest_stem_freq`
    - `n_stems`: number of stems (≥2 = compound)
    - `freq`: unchanged from step 3
    - `rarest_stem_freq`: the `freq` of the compound's rarest stem; equals `freq` for non-compounds
    - e.g. `työpaikka`: 2 stems, `freq` 520,192, `rarest_stem_freq` 3,418,001 (the rarer of työ 3,418,001 and paikka 3,462,791)
    - e.g. `talo`: 1 stem, `freq` 1,044,279, `rarest_stem_freq` 1,044,279 (not a compound)
  - `cleaned/04_stems.tsv`, columns: `stem freq standalone_freq n_lemmas n_compounds` (26,212 distinct lowercase stems; capitalised name stems such as Aalto or EU are left out, because "Aamu" is not "aamu")
    - `stem`: a stem of any lemma (e.g. `tilata`)
    - `freq`: the full count of the stem: the `freq` of every lemma that contains it, added up (the stem on its own, in compounds, in derivations). Every stem has one, also the 223 stems that never occur as their own word (e.g. `säädäntö`, 356,318, only in compounds such as lainsäädäntö)
    - `standalone_freq`: the `freq` of the lemma equal to the stem; empty if it never occurs as its own word
    - `n_lemmas`, `n_compounds`: how many lemmas / compound lemmas contain it
    - e.g. `työ`: `freq` 13,843,664 (standalone 3,418,001, in 96,267 lemmas); `ostaa`: 2,695,349 (standalone 1,518,077)
  - `cleaned/04_compound_stems.tsv`, columns: `compound stem stem_freq` (14.8M rows, one per compound × stem), for auditing
    - e.g. `ostotilaustoiminnallisuus`: `ostaa` 1,518,077, `tilata` 1,391,607, `toimia` 2,981,153 → `rarest_stem_freq` 1,391,607
- **Steps:**
  - For a compound (≥2 stems), look up each stem's standalone `freq` and take the smallest: a reader needs all the stems
  - A stem with no standalone entry is rare, so the compound's own `freq` also joins the minimum
  - Voikko's `=` inside a stem (`takaisin=kytkentä`) is removed before lookup, so the stem matches its standalone lemma
- **Results:** 6,459,885 lemmas, 6,126,323 of them compounds, 5,775,354 changed, 350,873 had a missing stem

### 5. Rank and filter English-looking words: `05_rank_and_filter.py` (helpers: `english_borrowing.py`, `wiktionary.py`)
- **Input:** `cleaned/04_lemmas_stem.tsv`, `cleaned/04_stems.tsv`, `cleaned/03_lemmas.tsv`, `cleaned/05_translations.tsv`
  - `05_translations.tsv` (columns `stem english etymology`) is a **one-time fetch** from the Wiktionary Finnish dump (kaikki.org, 4.6 GB streamed, ~20 min, CC BY-SA); it is only downloaded when the file is missing (`--refetch` to redo it). `english` = single-word English glosses joined by `|`; `etymology` = tags such as `bor:sv der:la`, `inh:urj-fin-pro` (inherited from Proto-Finnic)
- **Output:**
  - `cleaned/05_lemma_freq.tsv`, columns: `rank lemma class n_stems n_forms freq rarest_stem_freq`: the final lemma list
    - `rank`: position (1 = most frequent); the other columns as in step 4
  - `cleaned/05_stem_freq.tsv`, columns: `rank stem freq standalone_freq n_lemmas n_compounds`: the final stem list, ranked by the full count `freq`
  - `cleaned/05_stem_borrowing.tsv`, columns: `stem freq english edit_score norm borrowed reason etymology`: audit of the 19,330 stems that have an English gloss (stems without one cannot be judged), tagged stems first, most frequent first
    - `freq`: the stem's full count; `english`: closest English gloss; `edit_score`: weighted edit distance; `norm`: edit score / longer word length x 100
    - `borrowed`: 1 = tagged English-looking; `reason`: `edit score`, `bor:en` (etymology says borrowed from English) or `native etymology` (rule fired but the stem is inherited from Proto-Finnic / Uralic, so not tagged)
- **Steps:**
  - Edit score from each stem to its closest English gloss: normal edits cost 1, the STANDARD modifications Finnish applies when it borrows a word cost 0.2 (final -i, tt/t, ss/s, any doubled letter, k/c, f/ph, k/ch, ia/y, ...; the table is `RULES` in `english_borrowing.py`, taken from the team sheet)
  - Tag a stem when norm is at most **35**, or when its etymology says `bor:en`; do not tag stems inherited from Proto-Finnic / Uralic; stems under 3 characters, without a Wiktionary entry or an English gloss, and capitalised stems are not judged
  - Lemma rule `--lemma-rule`: remove a lemma when all of its stems are tagged (default), any, or none; `--keep-borrowed` removes nothing
  - Sort lemmas by `--sort-by` (default `freq`) and stems by `freq`, add `rank`; optional `--min-freq` cut (off by default)
- **Results:** 5,791 of 19,330 stems with a gloss are tagged; stem list 20,420 stems (26,211 before); lemma list 6,265,299 lemmas, 194,586 removed (4.14% of all lemma counts)
  - Calibration: the edit score reproduces the sheet for most pairs (see `reports/05_rank_and_filter.md`); every borrowed pair of the sheet scores 33.3 or less, every native pair 50 or more, tee/tea (33.3) is the borderline
- **Caveats:**
  - A tag means "looks like its English translation", not strictly "borrowed from English": it also catches Swedish, Latin and Greek loans and some Germanic cognates
  - **False positives among very frequent words are possible**: "mutta" (16.8M, gloss "but", norm 24.0) and "todeta" (gloss "note") are tagged and removed; the native-etymology veto does not catch them (their etymology has no `inh:` tag). Needs a review of the most frequent tagged stems
  - Stems without a Wiktionary entry (1,911) or without an English gloss cannot be judged and stay

### 6. Build bags (stems and lemmas): `06_build_bags.py`
- **Input:** `cleaned/05_stem_freq.tsv` (20,420 stems) and `cleaned/05_lemma_freq.tsv` (6.27M lemmas); English-looking ones are already removed
- **Output:** `cleaned/06_stem_bags_{method}.tsv` and `cleaned/06_lemma_bags_{method}.tsv`, one file per level and bag method, columns: `stem` or `lemma`, `freq`, `bag`
  - `freq`: a stem's full count, or a lemma's own count; `bag`: 1 (most frequent) up to the highest number (rarest)
  - e.g. `olla 175065322 1` (stem), `olla 156017700 1` (lemma)
- **Steps:** cut each ranked list into bags with `--bag-method` (default: all three)
  - `uniform_rank_bin`: every bag has the same number of items (2,042 stems per bag); bag 1 still holds 91% of the total stem count
  - `uniform_cumfreq_bin`: every bag covers 10% of the total freq count. Items ordered from most to least frequent with a running total; a new bag starts each time the total passes another 10%
  - `log10_freq_bin`: one bag per factor of 10 in frequency, bag 1 = the most frequent decade; 9 bags are used
    - the bands are fixed, the same for stems and lemmas: bag b covers `10^(9-b)` up to `10^(10-b) - 1` (the data tops out at 156M / 175M, so bag 1 is 100M and up). Bag membership depends only on the item's own count, never on the rest of the list
    - bag 1: 100M and up; 2: 10M to 99.9M; 3: 1M to 9.99M; 4: 100k to 999k; 5: 10k to 99,999; 6: 1k to 9,999; 7: 100 to 999; 8: 10 to 99; 9: 1 to 9
    - example: a count of 1,184,221 is in the 1M band, so bag 3
    - lemma sizes per bag: 2, 24, 399, 2,489, 10,950, 46,409, 176,128, 765,794, 5,263,104 lemmas; the % of the total count per bag is in `reports/06_build_bags.md`
- **Results:** per-bag counts, freq ranges and % of total count are in `reports/06_build_bags.md`; e.g. `uniform_cumfreq_bin`: bag 1 = 3 stems / 3 lemmas (olla, ja, se) holding about 11%, bag 10 = 18,560 stems / 6.26M lemmas holding 10.0%

### 7. Text features (stem and lemma bags): `07_text_features.py`
- **Input:** train/valid/test CSVs (`text` column), the stem and lemma bags, the list of English-looking stems; option `--bag-method` (default `uniform_cumfreq_bin`)
- **Output:** `outputs/vocab_features_{bag_method}_{train,valid,test}.csv`, columns: `row`, `label`, then
  - `borrowed_coverage`: share of words whose stems are all English-looking (shared by both levels)
  - per level (`stem_` and `lemma_`): `{level}_OOV_coverage` (share of counted words that are unknown), `{level}_bag_1..N_coverage` (share of words in each bag, 1 = most frequent), `mean_log_{level}_freq` (mean log10 count of the word's rarest known stem, or of its lemma)
- **Steps:**
  - Each word is analysed by Voikko (context-free). Stem level: the word's bag is the bag of its **rarest known stem** (a compound is as hard as its hardest part). Lemma level: the bag of its own lemma
  - A word whose stems were all removed in step 5 counts as `borrowed`, not OOV; a word Voikko does not recognise, or that is not in the list, is OOV; names and abbreviations are skipped
  - Every table is shown for all rows and for Finnish-native-only rows
- **Results** (`uniform_cumfreq_bin`), shares of all words in train (all rows), adding up to 100%:

  | level | in bag | borrowed (English-looking) | OOV: Voikko-unknown | OOV: recognised, not in list | skipped (name/abbrev) |
  |---|---:|---:|---:|---:|---:|
  | stem | 88.3% | 4.3% | 3.6% | 0.2% | 3.5% |
  | lemma | 88.4% | 4.3% | 3.6% | 0.1% | 3.5% |

  - per-text-avg-oov: train all 5.2% (stem) / 5.1% (lemma), train native 4.0% / 4.0%, test 3.9% / 3.8% (old pipeline: 22.4% train all, 27.9% train native)
  - Treating English-looking words as `borrowed` (not OOV) keeps OOV at about 5%; when they were simply removed from the lemma list, OOV rose to 9.5%
  - By label (see `07_text_features.md`): average share of words per bag, per level, split and subset

### 8. Compare variants (stem and lemma bags): `08_compare_variants.py`
- **Input:** the stem and lemma bags and 5,000 sampled train texts (all 2,332 native rows for the native subset)
- **Output:** `reports/08_compare_variants.md`, columns: `level subset texts bag_method rho_mean_log_freq rho_OOV_coverage rho_mean_bag rho_borrowed_coverage`
  - `rho_*`: Spearman correlation with the difficulty label; `mean_bag` is the average bag number of the words that are in a bag (bag 1 = most frequent, so a higher mean = rarer words)
- **Steps:** build the vocab features for each bag method and correlate them with the label
- **Results:**

  | level | subset | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag | rho borrowed_coverage |
  |---|---|---|---:|---:|---:|---:|
  | stem | all | uniform_rank_bin | -0.292 | +0.060 | +0.229 | +0.167 |
  | lemma | all | uniform_rank_bin | -0.442 | +0.074 | +0.362 | +0.167 |
  | stem | all | uniform_cumfreq_bin | -0.292 | +0.060 | +0.300 | +0.167 |
  | lemma | all | uniform_cumfreq_bin | -0.442 | +0.074 | +0.415 | +0.167 |
  | stem | all | log10_freq_bin | -0.292 | +0.060 | +0.294 | +0.167 |
  | lemma | all | log10_freq_bin | -0.442 | +0.074 | **+0.447** | +0.167 |
  | stem | native only | uniform_rank_bin | -0.192 | +0.245 | +0.145 | +0.192 |
  | lemma | native only | uniform_rank_bin | -0.376 | +0.278 | +0.325 | +0.192 |
  | stem | native only | uniform_cumfreq_bin | -0.192 | +0.245 | +0.211 | +0.192 |
  | lemma | native only | uniform_cumfreq_bin | -0.376 | +0.278 | +0.359 | +0.192 |
  | stem | native only | log10_freq_bin | -0.192 | +0.245 | +0.161 | +0.192 |
  | lemma | native only | log10_freq_bin | -0.376 | +0.278 | **+0.374** | +0.192 |

  - **Lemma bags correlate better than stem bags in every row** (mean_bag +0.447 vs +0.300 on all rows, +0.374 vs +0.211 on native; mean log count -0.44 vs -0.29)
  - For lemma bags `log10_freq_bin` is now the best bag method and `uniform_cumfreq_bin` is close; `uniform_rank_bin` is the weakest. For stem bags `uniform_cumfreq_bin` is the best
  - `borrowed_coverage` correlates positively with the label (+0.17 all, +0.19 native): harder texts contain more English-looking words, not fewer

### 9. Vocab text features: `09_vocab_text_features.py`
- **Input:** train/valid/test CSVs (`text` column) + `05_lemma_freq.tsv` (for choosing the lemma of an ambiguous word)
- **Output:** `outputs/vocab_text_features_{train,valid,test}.csv`, columns: `row`, `label`, and one column per feature
  - `n_unique_lemmas`: distinct lemmas; `ttr_lemma_200`: distinct lemmas among the first 200 / 200; `avg_word_length`, `long_word_ratio` (10+ characters)
  - `compound_ratio`, `avg_compound_parts`, `n_compound_tokens`: compounds (2+ stems) among content words
  - `deriv_llinen_ratio`, `deriv_ton_ratio`: Voikko derivation suffixes; `deriv_minen_ratio`, `deriv_sti_ratio`: heuristics (Voikko treats these as inflection)
  - definitions: `docs/features.md`
- **Steps:** `VocabDiffFeatureConstruct` (`vocab-diff/vocab_construct.py`, called through `TextDiffFeaturesConstruct` in `builder.py`) tokenizes, takes the Voikko reading of each word (context-free) and computes the features per text; the CSV also contains `OOV_coverage` and `vocab_bag_k_coverage` (same values as step 7)
- **Results** (Spearman correlation with the label on train, all rows / native only): `n_compound_tokens` +0.53 / +0.50, `avg_word_length` +0.50 / +0.50, `long_word_ratio` +0.48 / +0.49, `n_unique_lemmas` +0.41 / +0.36 (the count-based ones also grow with text length)

## Word classes

`class` is the part of speech Voikko assigns to a lemma (Finnish terms). Used only to drop names, abbreviations and prefix fragments; the frequency columns do not depend on it. If a lemma has several readings, the first one Voikko lists is kept.

In the final list (`04_lemmas_stem.tsv`, 6.5M lemmas):

| class | meaning | lemmas | example |
|---|---|---:|---|
| `nimisana` | noun | 5,651,851 | talo, työpaikka |
| `laatusana` | adjective | 718,721 | kaunis |
| `teonsana` | verb | 81,508 | olla |
| `nimisana_laatusana` | noun and adjective | 40,100 | |
| `seikkasana` | adverb | 7,798 | myös |
| `lukusana` | numeral | 1,603 | kaksi |
| `huudahdussana` | interjection | 42 | voi! |
| `asemosana` | pronoun | 29 | se, joka |
| `sidesana` | conjunction | 27 | ja, mutta |
| `suhdesana` | adposition | 17 | |
| `kieltosana` | negation word | 10 | ei |

Dropped before the final list:

| class | meaning | dropped in |
|---|---|---|
| `nimi`, `etunimi`, `sukunimi`, `paikannimi` | proper names (Pekka, Helsinki) | step 3 |
| `lyhenne` | abbreviation (EU, km) | step 3 |
| `etuliite` | prefix fragment (koulu-) | step 5 |

## Open points
- **`rarest_stem_freq` makes junk compounds look common.**
  - Some lemmas are junk, e.g. "hyvänhyvyys" (two words stuck together) appears only 24 times (`freq` 24)
  - The compound rule gives it the `freq` of its rarest stem. Its stems are common words, so its `rarest_stem_freq` is over 10M, as high as "hyvä" itself
  - Ranking or binning by `rarest_stem_freq` therefore puts such junk among the real common words (see `manual_check_sample.md`)
  - The default is now `freq`, so the bags are not affected; the problem only appears if `rarest_stem_freq` is used for ranking
  - Options: (a) keep ranking by `freq` and use `rarest_stem_freq` only when looking up words in a text; (b) drop compounds with a very low `freq` (e.g. under 5) before ranking
- **Stem or lemma bags**: both are built and kept as separate feature sets; lemma bags correlate better with the label (step 8), so stems add to them rather than replace them
- **TODO: use a context-aware analyser for the text side.** Steps 7-8 currently use Voikko without context: an ambiguous word gets the candidate lemma with the highest list frequency, whatever the sentence says. Plan: Stanza picks among Voikko's candidates (see the section below). The step 7-8 numbers will change once it is in.
- Spoken Finnish (mun, mä, oon...) is dropped as unrecognised and counts as OOV in text.

---

# Which analyser where: Voikko for the list, Stanza for the text

Decided 2026-10-03.

## Decision
| side | input | analyser | why |
|---|---|---|---|
| Cleaning the frequency list (steps 1-6) | `finnish_vocab.txt`: words + counts, **no sentences** | **Voikko** only | No context exists, so a contextual model has nothing to use. Stanza on isolated words is the same context-free guess, slower and no better. Voikko also gives compound stems (`WORDBASES`) that the rarest-stem rule needs, and runs 36M words in ~3 min. |
| Text side: train/valid/test OOV and `vocab_bag_k_coverage` (steps 7-8) | full sentences | **Stanza** (Finnish) for disambiguation, Voikko for the candidate lemmas | Context picks the right reading of ambiguous tokens ("voi" butter/can, "sinä" -> sinä/se). |

## How the text side combines them (planned, not implemented yet)
1. Voikko lists the candidate lemmas for each token.
2. Stanza lemmatizes the token in its sentence.
3. If Stanza's lemma is one of Voikko's candidates, use it. Otherwise fall back to the current rule: the candidate with the highest list frequency.
4. The list keeps Voikko's lemma spellings, so Stanza's conventions (compounds, participles) cannot cause fake OOV mismatches.

Rejected alternative: use Stanza lemmas directly on the text. Closer to the old Revita features, but its lemma spellings differ from the Voikko-built list and inflate OOV.

## Status
- Steps 1-8 currently use Voikko only, including the text side (context-free: highest-frequency candidate). Step 7/8 numbers will change once Stanza disambiguation is in.
- To do: `pip install stanza` + Finnish model (a few hundred MB), one cached run over the 3 splits (~10-30 min CPU), then switch `text_common.py` / steps 7-8 to the cached output.
- Open question: which parser produced the lemmas in the old features (Revita parser: Stanza or Turku neural parser)? If known, match its lemma choice more closely.

## Voikko facts worth remembering
- Rule-based finite-state analyser (`libvoikko` 4.3.3 via Homebrew), not a trained model; deterministic, no context. Returns every reading for ambiguous words.
- Needs a UTF-8 locale (`LC_ALL=en_US.UTF-8`) or it silently rejects every word with ä/ö. `common.run_voikko` sets it.
- Misses by design: spoken Finnish (mun, mä, oon, ku, mut), most typos, English. These count as OOV in text.
- Capitalised names that also have a common-word reading are counted as the common word.
