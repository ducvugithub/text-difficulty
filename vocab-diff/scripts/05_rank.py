"""Step 5: rank the lemma list and the stem list by frequency.

Lemmas: sorted by --sort-by (default freq) descending, `rank` added; optional --min-freq drops lemmas
below that value on the --sort-by column (default 0 = keep all).
Stems: sorted by freq descending, `rank` added; stems with no standalone freq are listed last without a rank.

Input : cleaned/04_lemmas_stem.tsv, cleaned/04_stems.tsv
Output: cleaned/lemma_freq.tsv (rank, lemma, class, n_stems, n_forms, freq, rarest_stem_freq)
        cleaned/stem_freq.tsv  (rank, stem, freq, n_compounds)
        reports/05_rank.md
"""
import argparse

from common import CLEANED, ensure_dirs, write_report

COLS = ["lemma", "class", "n_stems", "n_forms", "freq", "rarest_stem_freq"]


def rank_lemmas(sort_by, min_freq):
    key = COLS.index(sort_by)
    with open(CLEANED / "04_lemmas_stem.tsv", encoding="utf-8") as fh:
        rows = [line.rstrip("\n").split("\t") for line in fh]
    n_in = len(rows)
    rows = [r for r in rows if float(r[key]) >= min_freq]
    rows.sort(key=lambda r: -float(r[key]))
    with open(CLEANED / "lemma_freq.tsv", "w", encoding="utf-8") as dst:
        dst.write("rank\t" + "\t".join(COLS) + "\n")
        for rank, row in enumerate(rows, 1):
            dst.write(f"{rank}\t" + "\t".join(row) + "\n")
    return n_in, rows


def rank_stems():
    with open(CLEANED / "04_stems.tsv", encoding="utf-8") as fh:
        next(fh)
        rows = [line.rstrip("\n").split("\t") for line in fh]
    ranked = sorted((r for r in rows if r[1]), key=lambda r: -int(r[1]))
    unranked = [r for r in rows if not r[1]]
    with open(CLEANED / "stem_freq.tsv", "w", encoding="utf-8") as dst:
        dst.write("rank\tstem\tfreq\tn_compounds\n")
        for rank, (stem, freq, n) in enumerate(ranked, 1):
            dst.write(f"{rank}\t{stem}\t{freq}\t{n}\n")
        for stem, freq, n in unranked:
            dst.write(f"\t{stem}\t{freq}\t{n}\n")
    return len(ranked), len(unranked)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-freq", type=float, default=0, help="drop lemmas below this value of --sort-by (default 0 = keep all)")
    ap.add_argument("--sort-by", default="freq", choices=COLS[4:])
    args = ap.parse_args()
    ensure_dirs()

    n_in, kept = rank_lemmas(args.sort_by, args.min_freq)
    n_ranked, n_unranked = rank_stems()
    n = len(kept)
    key = COLS.index(args.sort_by)
    write_report("05_rank.md", [
        "# 05 rank",
        f"- lemmas: {n_in:,} in, {n:,} out (sorted by {args.sort_by}, min-freq {args.min_freq}) -> lemma_freq.tsv",
        "- lemmas by rank: " + ", ".join(f"top {k:,}: {args.sort_by}>={float(kept[k - 1][key]):,.0f}" for k in (1000, 10_000, 20_000, 100_000) if k <= n),
        f"- stems: {n_ranked:,} ranked by freq + {n_unranked:,} with no standalone freq (listed last, no rank) -> stem_freq.tsv",
        "",
        "Columns of lemma_freq.tsv: `rank` position in the sorted list (1 = most frequent); `lemma`; `class` Voikko word class; "
        "`n_stems` number of stems; `n_forms` forms merged into the lemma; `freq` all forms added up; "
        "`rarest_stem_freq` `freq` of the rarest stem for compounds (= `freq` otherwise).",
        "",
        "Columns of stem_freq.tsv: `rank` position by `freq` (empty if the stem never occurs as its own word); `stem`; "
        "`freq` its standalone lemma frequency; `n_compounds` compounds containing it.",
    ])


if __name__ == "__main__":
    main()
