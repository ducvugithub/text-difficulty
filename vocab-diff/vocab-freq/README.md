# vocab-freq — clean the frequency list

Input `data/finnish_vocab.txt` (raw surface forms, 44.6M lines, web/forum corpus) -> lemma-level list.
Scripts live in `../scripts/` (run in order from there; intermediate files in `cleaned/`, one report per step in `reports/`).

Setup: `voikkospell` on PATH (Voikko dictionary installed); steps 6-8 need `python -m venv .venv && .venv/bin/pip install -r requirements.txt`.
Gotcha: Voikko needs a UTF-8 locale or it silently rejects every word with ä/ö (`common.run_voikko` sets `LC_ALL`).

| step | script | what it does |
|---|---|---|
| 1 | `01_normalize.py` | drop digits, symbols/URLs, punctuation, hyphen fragments, >45 chars (`--min-count`) |
| 2 | `02_analyze.py` | Voikko analysis, parallel (~3 min); lemma readings + compound stems per surface form |
| 3 | `03_merge_lemmas.py` | forms -> lemmas; drops names, abbreviations, unrecognised (typos/English/spoken Finnish); ambiguous forms count in full for each lemma; `freq` = all forms added up |
| 4 | `04_compound_stems.py` | adds `rarest_stem_freq`: a compound (>=2 stems) takes the `freq` of its rarest stem; a stem with no standalone entry caps it at the compound's own `freq` |
| 5 | `05_finalize.py` | sanity filters + ranked `lemma_freq.tsv` (`--min-freq`) |
| 6 | `06_build_bags.py` | 10 equal-count bags, original Revita definition (`--variant`, `--top-n`) |
| 7 | `07_text_features.py` | recompute OOV / `vocab_bag_k_coverage` for train/valid/test + OOV overlap report |
| 8 | `08_compare_variants.py` | Spearman vs label for each variant x top-n (`freq` vs `rarest_stem_freq`) |

Step-by-step input/output/columns and findings: `reports/CLEANUP_SUMMARY.md`.
