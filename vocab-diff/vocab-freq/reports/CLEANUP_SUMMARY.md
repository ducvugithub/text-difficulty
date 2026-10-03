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
- **Output:** `cleaned/04_lemmas_stem.tsv`, columns: `lemma class n_stems n_forms freq rarest_stem_freq`
  - `n_stems`: number of stems (≥2 = compound); the stem names are not kept
  - `freq`: unchanged from step 3
  - `rarest_stem_freq`: the `freq` of the compound's rarest stem; equals `freq` for non-compounds
  - e.g. `työpaikka`: 2 stems, `freq` 520,192, `rarest_stem_freq` 3,418,001 (the rarer of työ 3,418,001 and paikka 3,462,791)
  - e.g. `talo`: 1 stem, `freq` 1,044,279, `rarest_stem_freq` 1,044,279 (not a compound)
- **Steps:**
  - For a compound (≥2 stems), look up each stem's standalone `freq` and take the smallest: a reader needs all the stems
  - A stem with no standalone entry is rare, so the compound's own `freq` also joins the minimum
- **Results:** 6.5M lemmas, 6.17M of them compounds, 5.66M changed, 510k had a missing stem

### 5. Finalize: `05_finalize.py`
- **Input:** `cleaned/04_lemmas_stem.tsv`
- **Output:** `cleaned/lemma_freq.tsv`, columns: `rank lemma class n_stems n_forms freq rarest_stem_freq`
  - `rank`: position in the sorted list (1 = most frequent); the other columns as in step 4
  - e.g. `1 olla teonsana 1 957 156017700 156017700`
- **Steps:**
  - Drop single letters (`a`, `x`: letters and symbols, not words), prefix fragments (`koulu-`: not standalone words), non-plain words (anything that is not letters with inner hyphens)
  - Sort by `--sort-by` (default `rarest_stem_freq`; `freq` is the alternative): the ranking is what step 6 cuts into bags, so it decides which lemmas count as "frequent"
  - Optional `--min-freq`: drop rare lemmas (off by default)
- **Results:** nothing dropped, 6.5M lemmas

### 6. Build bags: `06_build_bags.py`
- **Input:** `cleaned/lemma_freq.tsv`
- **Output:** `cleaned/vocab_bags.tsv`, columns: `lemma freq bag`
  - `freq`: the value of the chosen `--variant` column (`freq` or `rarest_stem_freq`)
  - `bag`: 1 (rarest) to 10 (most frequent)
  - e.g. `olla 156017700 10`
- **Steps:**
  - Keep the `--top-n` most frequent lemmas (default 20000)
  - 10 equal-count bins over the frequency-ascending list (1 = rarest, 10 = most frequent), original Revita definition
- **Results:** 20,000 lemmas → 2,000 per bag

### 7. Text features: `07_text_features.py`
- **Input:** train/valid/test CSVs (`text` column) + `lemma_freq.tsv`
- **Output:** `text-diff/feature-curated-based/outputs/vocab_features_{train,valid,test}.csv`, columns:
  - `row`: row index in the source CSV; `label`: difficulty label
  - `n_word_tokens`: word tokens counted (names/abbreviations excluded)
  - `OOV_coverage`: share of tokens not in any bag
  - `vocab_bag_1..10_coverage`: share of tokens in each bag
  - `frac_unrecognised`, `frac_unlisted`, `frac_beyond_top_n`: the OOV share split by reason
  - e.g. `row 0, label 1.0, n_word_tokens 193, OOV_coverage 0.28`
- **Steps:**
  - Tokenize, lemmatize with Voikko (highest-frequency candidate), look up the bag
  - Recompute `OOV_coverage` and `vocab_bag_k_coverage`; names/abbreviations skipped
- **Results:** 97% of lemma types in each split are in the full list; 3.6% of tokens unrecognised; 49% beyond the top 20k

### 8. Compare variants: `08_compare_variants.py`
- **Input:** `cleaned/lemma_freq.tsv` + 5,000 sampled train texts
- **Output:** `reports/08_compare_variants.md`, columns: `variant top-n rho_mean_log_freq rho_OOV_coverage rho_mean_bag`
  - `variant`: `freq` or `rarest_stem_freq`; `top-n`: how many top lemmas were binned
  - `rho_*`: Spearman correlation with the difficulty label for that text feature
  - e.g. `rarest_stem_freq | 10000 | -0.264 | +0.353 | -0.358`
- **Steps:** compute the three text features per text for each variant × top-n, correlate with the label
- **Results:**
  - `freq` is better on mean log-freq (-0.32 vs -0.26); equal on OOV and bags at 10k
  - Smaller top-n better (10k > 20k > 50k)
  - Earlier test of other ways to combine forms (most frequent form, rarest form): no better than `freq`, so dropped

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
- **Compound rule inflates junk compounds** (e.g. "hyvänhyvyys", own count 24, gets the frequency of "hyvä"), which then rank in the top 20k. Options: rank by the plain sum and apply the rule only when looking up text tokens, or filter low-count compounds first.
- **`freq` vs `rarest_stem_freq`, and top-n for the bags, are not settled** (leaning `freq` + 10k).
- **Stanza disambiguation on the text side is not built yet** (see the section below); steps 7-8 numbers will change once it is.
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
