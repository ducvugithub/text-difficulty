"""Step 4: compound lemmas take the frequency of their rarest stem.

A compound = lemma with >=2 real stems (Voikko WORDBASES, derivational suffixes ignored).
rarest_stem_freq = the smallest `freq` among the compound's stems (each stem's own standalone lemma freq).
A stem that never occurs standalone is itself rare, so the compound's own `freq` joins the minimum
(typo-compounds like 'x-oleva' stay rare). Lemmas with 0-1 stems keep rarest_stem_freq = freq.

Input : cleaned/03_lemmas.tsv
Output: cleaned/04_lemmas_stem.tsv (lemma, class, n_stems, n_forms, freq, rarest_stem_freq)
"""
from common import CLEANED, ensure_dirs, write_report


def main():
    ensure_dirs()
    rows = []
    table = {}
    with open(CLEANED / "03_lemmas.tsv", encoding="utf-8") as fh:
        for line in fh:
            lemma, cls, stems, n_forms, freq = line.rstrip("\n").split("\t")
            rows.append((lemma, cls, stems.split("+") if stems else [], int(n_forms), int(freq)))
            table[lemma] = int(freq)

    n_compounds = n_changed = n_missing_stem = 0
    biggest = []  # (freq, rarest_stem_freq, lemma)
    with open(CLEANED / "04_lemmas_stem.tsv", "w", encoding="utf-8") as dst:
        for lemma, cls, stems, n_forms, freq in rows:
            rarest = freq
            if len(stems) >= 2:
                n_compounds += 1
                parts = [s for s in stems if s != lemma]
                bounds = [table[s] for s in parts if s in table]
                if len(bounds) < len(parts):  # some stem has no standalone entry
                    n_missing_stem += 1
                    bounds.append(freq)
                rarest = min(bounds)
                if rarest != freq:
                    n_changed += 1
                    biggest.append((freq, rarest, lemma))
            dst.write(f"{lemma}\t{cls}\t{len(stems)}\t{n_forms}\t{freq}\t{rarest}\n")

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
        "## Largest changes (freq -> rarest_stem_freq)",
        "| lemma | freq | rarest_stem_freq |",
        "|---|---:|---:|",
    ]
    lines += [f"| {lem} | {own:,} | {rs:,} |" for own, rs, lem in biggest[:40]]
    write_report("04_compound_stems.md", lines)


if __name__ == "__main__":
    main()
