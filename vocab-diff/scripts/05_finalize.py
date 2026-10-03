"""Step 5: last lemma-level sanity filters and the final ranked list.

Drops: single-character lemmas, lemmas that are not plain letter(-letter) words, prefix fragments (CLASS etuliite),
and lemmas under --min-freq (on the --sort-by column).

Input : cleaned/04_lemmas_stem.tsv
Output: cleaned/lemma_freq.tsv (rank, lemma, class, n_stems, n_forms, freq, rarest_stem_freq),
        sorted by --sort-by desc; reports/05_finalize.md
"""
import argparse
from collections import defaultdict

from common import CLEANED, WORD_RE, ensure_dirs, write_report

COLS = ["lemma", "class", "n_stems", "n_forms", "freq", "rarest_stem_freq"]


def reject_reason(lemma, cls):
    if len(lemma) < 2:
        return "single_character"
    if cls == "etuliite":
        return "prefix_fragment"
    if not WORD_RE.fullmatch(lemma):
        return "not_plain_word"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-freq", type=float, default=0, help="drop lemmas below this frequency (default 0 = keep all)")
    ap.add_argument("--sort-by", default="rarest_stem_freq", choices=COLS[4:])
    args = ap.parse_args()
    ensure_dirs()

    kept = []
    dropped = defaultdict(lambda: [0, []])
    with open(CLEANED / "04_lemmas_stem.tsv", encoding="utf-8") as fh:
        for line in fh:
            row = line.rstrip("\n").split("\t")
            rec = dict(zip(COLS, row))
            reason = reject_reason(rec["lemma"], rec["class"])
            if reason is None and float(rec[args.sort_by]) < args.min_freq:
                reason = "below_min_freq"
            if reason:
                d = dropped[reason]
                d[0] += 1
                if len(d[1]) < 15:
                    d[1].append(rec["lemma"])
            else:
                kept.append(row)

    key = COLS.index(args.sort_by)
    kept.sort(key=lambda r: -float(r[key]))
    out = CLEANED / "lemma_freq.tsv"
    with open(out, "w", encoding="utf-8") as dst:
        dst.write("rank\t" + "\t".join(COLS) + "\n")
        for rank, row in enumerate(kept, 1):
            dst.write(f"{rank}\t" + "\t".join(row) + "\n")

    n = len(kept)
    lines = [
        "# 05 finalize",
        f"- final lemmas: {n:,} -> {out.name} (sorted by {args.sort_by}, min-freq {args.min_freq})",
        "- lemmas by rank: " + ", ".join(f"top {k:,}: freq>={float(kept[k - 1][key]):,.0f}" for k in (1000, 10_000, 20_000, 100_000) if k <= n),
        "",
        "Columns of lemma_freq.tsv: `rank` position in the sorted list (1 = most frequent); `lemma`; `class` Voikko word class; "
        "`n_stems` number of stems; `n_forms` forms merged into the lemma; `freq` all forms added up; "
        "`rarest_stem_freq` `freq` of the rarest stem for compounds (= `freq` otherwise).",
        "",
        "| dropped | lemmas | examples |",
        "|---|---:|---|",
    ]
    lines += [f"| {r} | {c:,} | {', '.join(ex)} |" for r, (c, ex) in dropped.items()]
    write_report("05_finalize.md", lines)


if __name__ == "__main__":
    main()
