"""Step 4: compound lemmas take the frequency of their rarest stem.

A compound = lemma with >=2 real stems (Voikko WORDBASES, derivational suffixes ignored).
rarest_stem_freq = the smallest `freq` among the compound's stems (each stem's own standalone lemma freq).
A stem that never occurs standalone is itself rare, so the compound's own `freq` joins the minimum
(typo-compounds like 'x-oleva' stay rare). Lemmas with 0-1 stems keep rarest_stem_freq = freq.

Voikko marks lexicalised units inside a stem with '=' ('takaisin=kytkentä'); it is removed before lookup.

Input : cleaned/03_lemmas.tsv
Output: cleaned/04_lemmas_stem.tsv     (lemma, class, n_stems, n_forms, freq, rarest_stem_freq)
        cleaned/04_stems.tsv           (stem, freq, standalone_freq, n_lemmas, n_compounds)   one row per distinct lowercase stem
          freq             full count of the stem: the `freq` of every lemma that contains it, added up (the stem on its own,
                           in compounds, in derivations); every stem has one, also stems that never occur as their own word
          standalone_freq  the `freq` of the lemma equal to the stem, empty if it never occurs as its own word
          (capitalised name stems such as Aalto or EU are left out: "Aamu" is not "aamu")
        cleaned/04_compound_stems.tsv  (compound, stem, stem_freq) one row per compound x stem, for auditing
"""
from collections import Counter

from common import CLEANED, ensure_dirs, write_report


def main():
    ensure_dirs()
    rows = []
    table = {}
    with open(CLEANED / "03_lemmas.tsv", encoding="utf-8") as fh:
        for line in fh:
            lemma, cls, stems, n_forms, freq = line.rstrip("\n").split("\t")
            rows.append((lemma, cls, [x.replace("=", "") for x in stems.split("+")] if stems else [], int(n_forms), int(freq)))
            table[lemma] = int(freq)

    n_compounds = n_changed = n_missing_stem = n_stems = 0
    biggest = []  # (freq, rarest_stem_freq, lemma)
    stem_compounds = Counter()  # stem -> number of compounds containing it
    stem_full, stem_lemmas = Counter(), Counter()  # stem -> full count / number of lemmas containing it
    with open(CLEANED / "04_lemmas_stem.tsv", "w", encoding="utf-8") as dst, open(
        CLEANED / "04_compound_stems.tsv", "w", encoding="utf-8"
    ) as audit:
        audit.write("compound\tstem\tstem_freq\n")
        for lemma, cls, stems, n_forms, freq in rows:
            rarest = freq
            for s in set(stems or [lemma]):
                stem_full[s] += freq
                stem_lemmas[s] += 1
            if len(stems) >= 2:
                n_compounds += 1
                parts = [s for s in stems if s != lemma]
                for s in parts:
                    stem_compounds[s] += 1
                    audit.write(f"{lemma}\t{s}\t{table.get(s, '')}\n")
                bounds = [table[s] for s in parts if s in table]
                if len(bounds) < len(parts):  # some stem has no standalone entry
                    n_missing_stem += 1
                    bounds.append(freq)
                rarest = min(bounds)
                if rarest != freq:
                    n_changed += 1
                    biggest.append((freq, rarest, lemma))
            dst.write(f"{lemma}\t{cls}\t{len(stems)}\t{n_forms}\t{freq}\t{rarest}\n")

    with open(CLEANED / "04_stems.tsv", "w", encoding="utf-8") as dst:
        dst.write("stem\tfreq\tstandalone_freq\tn_lemmas\tn_compounds\n")
        for stem, full in stem_full.most_common():
            if stem[:1].isupper():  # names / abbreviations (Aalto, EU): not vocabulary stems, and "Aamu" is not "aamu"
                continue
            dst.write(f"{stem}\t{full}\t{table.get(stem, '')}\t{stem_lemmas[stem]}\t{stem_compounds[stem]}\n")
            n_stems += 1

    biggest.sort(key=lambda t: -abs(t[1] - t[0]))
    lines = [
        "# 04 compound stems",
        f"- lemmas: {len(rows):,}; compounds (>=2 stems): {n_compounds:,}",
        f"- compounds whose freq changed: {n_changed:,}; with a stem missing standalone (own freq caps them): {n_missing_stem:,}",
        "",
        "Columns of 04_lemmas_stem.tsv: `lemma`; `class` Voikko word class; `n_stems` number of stems (>=2 = compound); "
        "`n_forms` inflected forms merged into the lemma; `freq` all its forms added up (from step 3); "
        "`rarest_stem_freq` = `freq` of the compound's rarest stem (= `freq` for non-compounds).",
        "",
        f"Also written: `04_stems.tsv` ({n_stems:,} distinct lowercase stems; `stem`; `freq` full count = the `freq` of every lemma containing the stem, added up; "
        f"`standalone_freq` the `freq` of the lemma equal to the stem, empty if it never occurs as its own word; `n_lemmas` lemmas containing it; "
        f"`n_compounds` compounds containing it) and `04_compound_stems.tsv` "
        "(`compound`, `stem`, `stem_freq`: one row per compound x stem, to audit the rarest-stem rule).",
        "",
        "## Largest changes (freq -> rarest_stem_freq)",
        "| lemma | freq | rarest_stem_freq |",
        "|---|---:|---:|",
    ]
    lines += [f"| {lem} | {own:,} | {rs:,} |" for own, rs, lem in biggest[:40]]
    write_report("04_compound_stems.md", lines)


if __name__ == "__main__":
    main()
