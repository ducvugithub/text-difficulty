"""Step 4: stem inventory. Every lemma gets its number of stems, and every stem gets its full count.

A stem is a root of a word (työ, paikka, ostaa). Voikko gives a lemma its stems (WORDBASES, derivational suffixes ignored);
a lemma with 2 or more stems is a compound. A stem's `freq` = the `freq` of every lemma that contains it, added up.
Voikko's '=' marker inside a stem ('takaisin=kytkentä') is unreliable, so it is removed.
Capitalised stems are names or abbreviations (Aalto, EU) and are left out of the stem list: "Aamu" is not "aamu".

Input : cleaned/03_lemmas.tsv
Output: cleaned/04_lemmas_stem.tsv     (lemma, class, n_stems, n_forms, freq)
        cleaned/04_stems.tsv           (stem, freq, standalone_freq, n_lemmas, n_compounds)   one row per distinct lowercase stem
          freq             full count of the stem, also for stems that never occur as their own word
          standalone_freq  the `freq` of the lemma equal to the stem, empty if it never occurs as its own word
        cleaned/04_compound_stems.tsv  (compound, stem, stem_freq) one row per compound x stem, for auditing
"""
from collections import Counter

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))  # common.py, text_common.py

from common import CLEANED, ensure_dirs, write_report


def main():
    ensure_dirs()
    rows, standalone = [], {}
    with open(CLEANED / "03_lemmas.tsv", encoding="utf-8") as fh:
        for line in fh:
            lemma, cls, stems, n_forms, freq = line.rstrip("\n").split("\t")
            rows.append((lemma, cls, [x.replace("=", "") for x in stems.split("+")] if stems else [], int(n_forms), int(freq)))
            standalone[lemma] = int(freq)

    n_compounds = n_stems_total = 0
    stem_compounds, stem_full, stem_lemmas = Counter(), Counter(), Counter()
    with open(CLEANED / "04_lemmas_stem.tsv", "w", encoding="utf-8") as dst, open(
        CLEANED / "04_compound_stems.tsv", "w", encoding="utf-8"
    ) as audit:
        audit.write("compound\tstem\tstem_freq\n")
        for lemma, cls, stems, n_forms, freq in rows:
            for s in set(stems or [lemma]):
                stem_full[s] += freq
                stem_lemmas[s] += 1
            if len(stems) >= 2:
                n_compounds += 1
                for s in (s for s in stems if s != lemma):
                    stem_compounds[s] += 1
                    audit.write(f"{lemma}\t{s}\t{standalone.get(s, '')}\n")
            dst.write(f"{lemma}\t{cls}\t{len(stems)}\t{n_forms}\t{freq}\n")

    with open(CLEANED / "04_stems.tsv", "w", encoding="utf-8") as dst:
        dst.write("stem\tfreq\tstandalone_freq\tn_lemmas\tn_compounds\n")
        for stem, full in stem_full.most_common():
            if stem[:1].isupper():
                continue
            dst.write(f"{stem}\t{full}\t{standalone.get(stem, '')}\t{stem_lemmas[stem]}\t{stem_compounds[stem]}\n")
            n_stems_total += 1

    write_report("04_compound_stems.md", [
        "# 04 compound stems",
        f"- lemmas: {len(rows):,}; compounds (2 or more stems): {n_compounds:,}",
        f"- distinct lowercase stems: {n_stems_total:,}; never occurring as their own word: {sum(1 for s in stem_full if not s[:1].isupper() and s not in standalone):,}",
        "",
        "Columns of `04_lemmas_stem.tsv`:",
        "- `lemma`",
        "- `class`: Voikko word class",
        "- `n_stems`: number of stems (2 or more = compound)",
        "- `n_forms`: inflected forms merged into the lemma",
        "- `freq`: all its forms added up (from step 3)",
        "",
        "Columns of `04_stems.tsv`:",
        "- `stem`",
        "- `freq`: full count = the `freq` of every lemma containing the stem, added up",
        "- `standalone_freq`: the `freq` of the lemma equal to the stem, empty if it never occurs as its own word",
        "- `n_lemmas`: lemmas containing it",
        "- `n_compounds`: compounds containing it",
        "",
        "Columns of `04_compound_stems.tsv` (one row per compound x stem, for auditing):",
        "- `compound`",
        "- `stem`",
        "- `stem_freq`: that stem's standalone `freq`",
    ])


if __name__ == "__main__":
    main()
