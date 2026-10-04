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
  - Drop names (Helsingissä), abbreviations, unrecognised words (typos, English, spoken Finnish)
  - Ambiguous words with multiple lemmas: each lemma gets the full count
- **Results:** 36.1M forms → 20.6M kept → 6.5M lemmas
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
  - `cleaned/04_stems.tsv`, columns: `stem freq n_compounds` (28,623 distinct stems)
    - `stem`: a stem found inside compounds (e.g. `tilata`)
    - `freq`: its standalone lemma frequency from the list; empty if it never occurs as its own word (5,996 stems)
    - `n_compounds`: how many compound lemmas contain it
  - `cleaned/04_compound_stems.tsv`, columns: `compound stem stem_freq` (14.8M rows, one per compound × stem), for auditing
    - e.g. `ostotilaustoiminnallisuus`: `ostaa` 1,518,077, `tilata` 1,391,607, `toimia` 2,981,153 → `rarest_stem_freq` 1,391,607
- **Steps:**
  - For a compound (≥2 stems), look up each stem's standalone `freq` and take the smallest: a reader needs all the stems
  - A stem with no standalone entry is rare, so the compound's own `freq` also joins the minimum
  - Voikko's `=` inside a stem (`takaisin=kytkentä`) is removed before lookup, so the stem matches its standalone lemma
- **Results:** 6.5M lemmas, 6.17M of them compounds, 5.78M changed, 389k had a missing stem

### 5. Rank: `05_rank.py`
- **Input:** `cleaned/04_lemmas_stem.tsv`, `cleaned/04_stems.tsv`
- **Output:**
  - `cleaned/lemma_freq.tsv`, columns: `rank lemma class n_stems n_forms freq rarest_stem_freq`
    - `rank`: position in the sorted list (1 = most frequent); the other columns as in step 4
    - e.g. `1 olla teonsana 1 957 156017700 156017700`
  - `cleaned/stem_freq.tsv`, columns: `rank stem freq n_compounds`
    - `rank`: position by `freq` (empty if the stem never occurs as its own word, listed last)
    - `freq`, `n_compounds`: as in `04_stems.tsv`
    - e.g. `1 olla 156017700 773`
- **Steps:**
  - Sort the lemmas by `--sort-by` (default `freq`; `rarest_stem_freq` is the alternative) and add `rank`: this ranking is what step 6 cuts into bags
  - Sort the stems by `freq` and add `rank`
  - Optional `--min-freq`: drop lemmas below this value of the `--sort-by` column (off by default)
  - No cleaning here: names, abbreviations, single letters, fragments and non-words were already removed in steps 1 and 3
- **Results:** 6.5M lemmas in and out; 22,627 stems ranked + 5,996 stems with no standalone freq (no rank)

### 6. Build bags: `06_build_bags.py`
- **Input:** `cleaned/lemma_freq.tsv`
- **Output:** `cleaned/vocab_bags_{method}.tsv`, one file per bag method, columns: `lemma freq bag`
  - `freq`: the value of the chosen `--freq-column` (`freq` or `rarest_stem_freq`)
  - `bag`: 1 (rarest) up to the highest bag number (most frequent)
  - e.g. `olla 156017700 10`
- **Steps:** cut the ranked lemmas into bags with `--freq-column` (default `freq`) and `--bag-method` (default: all three)
  - `uniform_rank_bin`: every bag has the same number of lemmas (the original Revita definition, over the whole list). Lemmas ordered by frequency are cut into 10 equal groups
  - `uniform_cumfreq_bin`: every bag covers 10% of the total freq count. Lemmas ordered from most to least frequent with a running total of `freq`; a new bag starts each time the running total passes another 10% of the grand total. Top bags hold few lemmas, the bottom bag holds millions
  - `log10_freq_bin`: one bag per factor of 10 in frequency, `floor(log10(freq)) + 1`; 9 bags are used because the data spans ~10^0 to 10^8
- **Results:** per-bag lemma counts, freq ranges and % of total freq count are in `reports/06_build_bags.md`; e.g. `uniform_rank_bin`: bag 10 = 650k lemmas holding 99.4% of the total freq count; `uniform_cumfreq_bin`: bag 10 = 26k lemmas and bag 1 = 4.3M lemmas, each holding 10%

### 7. Text features: `07_text_features.py`
- **Input:** train/valid/test CSVs (`text` column) + `lemma_freq.tsv`; options `--freq-column` (default `freq`), `--bag-method` (default `uniform_cumfreq_bin`)
- **Output:** `text-diff/feature-curated-based/outputs/vocab_features_{bag_method}_{train,valid,test}.csv`, columns:
  - `row`: row index in the source CSV; `label`: difficulty label
  - `n_word_tokens`: word tokens counted (names/abbreviations excluded)
  - `OOV_coverage`: share of tokens not in any bag
  - `vocab_bag_1..N_coverage`: share of tokens in each bag
  - `frac_unrecognised`, `frac_unlisted`: the OOV share split by reason
  - e.g. `row 0, label 1.0, n_word_tokens 193, OOV_coverage 0.28`
- **Steps:**
  - Tokenize, lemmatize with Voikko (highest-frequency candidate), look up the bag
  - Recompute `OOV_coverage` and `vocab_bag_k_coverage`; names/abbreviations skipped
- **Subsets:** every table in `07_text_features.md` is shown for `all` rows and for `finnish-native-only` (`origine` = Real; the Russian-origin rows are translations). Test is all native, so it appears once
- **Results** (`freq` + `uniform_cumfreq_bin`, whole list), per-text-avg-oov: train all 5.1%, train native 4.0%; valid all 5.6%, valid native 4.0%; test 3.8%
  - Shares of all words in train (all rows), adding up to 100%:

    | in bag | OOV: Voikko-unknown | OOV: recognised, not in list | skipped (name/abbrev) |
    |---:|---:|---:|---:|
    | 92.7% | 3.6% | 0.2% | 3.5% |

  - `per-text-avg-oov`: each text's OOV rate, averaged over texts (old pipeline: 22.4% train all, 27.9% train native)
  - `all-text-pool-oov`: all unknown words / all counted words (train all 3.9%); names/abbreviations are left out of the denominator
  - By label (see `07_text_features.md`): average share of words in each bag. In train (all rows) the rarest bag (bag 1) rises from 3.3% at label 1.0 to 13.9% at label 6.0
  - An earlier run that binned only the top 20k lemmas gave per-text-avg-oov 54-58%, because 49% of words fell beyond the cut; that cut has been removed

### 8. Compare variants: `08_compare_variants.py`
- **Input:** `cleaned/lemma_freq.tsv` + 5,000 sampled train texts
- **Output:** `reports/08_compare_variants.md`, columns: `freq column, bag method, rho_mean_log_freq, rho_OOV_coverage, rho_mean_bag`
  - `rho_*`: Spearman correlation with the difficulty label for that text feature (more negative on mean log-freq / mean bag = better)
  - e.g. `freq | uniform_cumfreq_bin | - | -0.319 | +0.074 | -0.368`
- **Steps:** compute the three text features per text for each freq column × bag method, correlate with the label
- **Results:** correlation with the label on train (more negative on `mean_bag` / `mean_log_freq` = better), for all rows (5,000 sampled) and for Finnish-native-only (all 2,332 native rows):

  | subset | freq column | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag |
  |---|---|---|---:|---:|---:|
  | all | freq | uniform_rank_bin | -0.319 | +0.074 | -0.082 |
  | all | freq | uniform_cumfreq_bin | -0.319 | +0.074 | **-0.368** |
  | all | freq | log10_freq_bin | -0.319 | +0.074 | -0.319 |
  | all | rarest_stem_freq | uniform_rank_bin | -0.262 | +0.074 | -0.217 |
  | all | rarest_stem_freq | uniform_cumfreq_bin | -0.262 | +0.074 | -0.315 |
  | all | rarest_stem_freq | log10_freq_bin | -0.262 | +0.074 | -0.265 |
  | native only | freq | uniform_rank_bin | -0.406 | +0.278 | -0.287 |
  | native only | freq | uniform_cumfreq_bin | -0.406 | +0.278 | -0.396 |
  | native only | freq | log10_freq_bin | -0.406 | +0.278 | **-0.403** |
  | native only | rarest_stem_freq | uniform_rank_bin | -0.370 | +0.278 | -0.330 |
  | native only | rarest_stem_freq | uniform_cumfreq_bin | -0.370 | +0.278 | -0.342 |
  | native only | rarest_stem_freq | log10_freq_bin | -0.370 | +0.278 | -0.370 |

  - The vocab signals are stronger on Finnish-native-only (mean_log_freq -0.41 vs -0.32, OOV +0.28 vs +0.07): the translated rows dilute them
  - `freq` beats `rarest_stem_freq` everywhere; `uniform_cumfreq_bin` and `log10_freq_bin` are about equal and clearly better than `uniform_rank_bin`

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
- **Freq column and bag method are not settled** (leaning `freq` + `uniform_cumfreq_bin`; differences between methods are small).
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
