# vocab-freq — clean the frequency list

Input: `../../data/finnish_vocab.txt` (`count word`, ~44.6M lines, raw surface forms).
Output: `cleaned/` (lemma-level freq list) + `reports/` (what each step dropped/merged).

## Steps (src/, run in order; each writes a report)
1. `01_normalize` — lowercase, strip punctuation-only / numeric / URL / too-long tokens.
2. `02_analyze` — run the analyser (apertium-fin / Voikko / Omorfi) -> lemma(s) per surface form. Cache results.
   Keep all readings with the surface count split or first-reading (decide + log).
3. `03_compound_split` — compounds (>1 stem): word freq = freq of the RAREST component stem.
4. `04_merge_lemmas` — surface forms -> same lemma: DECISION PENDING, compare sum vs min vs max.
   Sum is the standard for lemma frequency (min would punish common lemmas for rare inflections);
   evaluate by correlation with train labels.
5. `05_filter_foreign` — drop English borrowings / foreign tokens (analyser fails + latin chars pattern,
   or language-ID). Report how many and the top examples; check not removing established loans (e.g. "kahvi").
6. `06_other_cleaning` — candidates: proper nouns/names, typos (hapax with edit-distance-1 to a frequent word),
   abbreviations, HTML/URL residue, case merging, very-low-frequency hapax cutoff.
7. `07_build_bags` — rank -> `vocab_bag_1..10` (same bucketing as existing features; check
   existing definition in the Features.csv before redefining).

## Reports (`reports/`)
Per step: rows in/out, top-N dropped, top-N merged. Review before trusting the list.
