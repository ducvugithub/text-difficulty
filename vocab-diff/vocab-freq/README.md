# vocab-freq — clean the frequency list

Input `data/finnish_vocab.txt` (raw surface forms, 44.6M lines, web/forum corpus) -> lemma-level list.
Scripts live in `scripts/` (this folder) (run in order from there; intermediate files in `cleaned/`, one report per step in `reports/`).

Setup: `voikkospell` on PATH (Voikko dictionary installed); steps 6-8 need `python -m venv .venv && .venv/bin/pip install -r requirements.txt`.
Gotcha: Voikko needs a UTF-8 locale or it silently rejects every word with ä/ö (`common.run_voikko` sets `LC_ALL`).

| step | script | what it does |
|---|---|---|
| 1 | `01_normalize.py` | drop digits, symbols/URLs, punctuation, hyphen fragments, >45 chars (`--min-count`) |
| 2 | `02_analyze.py` | Voikko analysis, parallel (~3 min); lemma readings + compound stems per surface form |
| 3 | `03_merge_lemmas.py` | forms -> lemmas; drops names, abbreviations, unrecognised (typos/English/spoken Finnish); ambiguous forms count in full for each lemma; `freq` = all forms added up |
| 4 | `04_compound_stems.py` | stem inventory: `n_stems` per lemma, every stem with its full count (`04_stems.tsv`), audit of compound x stem |
| 5 | `05_rank_and_filter.py` | tag English-looking stems (edit score <= 35 to the Wiktionary English gloss, helpers `english_borrowing.py`, `wiktionary.py`), remove them and their lemmas, rank the final `05_lemma_freq.tsv` and `05_stem_freq.tsv` |
| 6 | `06_build_bags.py` | bag the ranked stems AND lemmas: `--bag-method` (`uniform_rank_bin` / `uniform_cumfreq_bin` / `log10_freq_bin`, explained in `reports/06_build_bags.md`) |
| 7 | `07_text_features.py` | recompute OOV / `vocab_bag_k_coverage` for train/valid/test + OOV overlap report |
| 8 | `08_compare_variants.py` | Spearman vs label for each level (stem / lemma) and bag method, all rows and Finnish-native-only |
| 9 | `../build_features.py` | builds the features of both vocab signals with `VocabDiffFeatureConstruct` (`vocab-diff/vocab_construct.py`) and correlates them with the label; list in `docs/features.md` |

Step-by-step input/output/columns and findings: `reports/CLEANUP_SUMMARY.md`.
