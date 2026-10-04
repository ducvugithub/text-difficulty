"""Step 6: cut the ranked lemma list into vocab bags (1 = rarest ... highest = most frequent).

--freq-column picks the number to bin on (freq or rarest_stem_freq).
--bag-method picks how to cut (default: all three, one output file each):
  uniform_rank_bin     equal number of lemmas per bag (original Revita definition, over the whole list)
  uniform_cumfreq_bin  equal share (10%) of the total freq count per bag
  log10_freq_bin       one bag per factor of 10 in frequency
Explanations of each method are written into the report.

Input : cleaned/lemma_freq.tsv
Output: cleaned/vocab_bags_{method}.tsv (lemma, freq, bag), reports/06_build_bags.md
"""
import argparse

from common import CLEANED, ensure_dirs, write_report
from text_common import BAG_METHOD_DOCS, BAG_METHODS, assign_bags, load_lemma_list


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--freq-column", default="freq", choices=["freq", "rarest_stem_freq"])
    ap.add_argument("--bag-method", default="all", choices=["all", *BAG_METHODS])
    args = ap.parse_args()
    ensure_dirs()

    lemmas, freq = load_lemma_list(args.freq_column)
    grand_total = sum(freq.values())
    lines = [
        "# 06 build bags",
        f"- frequency column: `{args.freq_column}`; {len(lemmas):,} lemmas in the list",
        "- bag 1 = rarest ... highest bag = most frequent",
        "- columns of vocab_bags_{method}.tsv: `lemma`; `freq` the value of the frequency column; `bag` the bag number",
    ]
    for method in BAG_METHODS if args.bag_method == "all" else [args.bag_method]:
        bags = assign_bags(lemmas, freq, method)
        out = CLEANED / f"vocab_bags_{method}.tsv"
        stats = {}  # bag -> [lemmas, max freq, min freq, freq total]
        with open(out, "w", encoding="utf-8") as dst:
            dst.write("lemma\tfreq\tbag\n")
            for lemma in lemmas:
                b = bags.get(lemma)
                f = freq[lemma]
                dst.write(f"{lemma}\t{f}\t{b}\n")
                st = stats.setdefault(b, [0, f, f, 0])
                st[0] += 1
                st[1], st[2], st[3] = max(st[1], f), min(st[2], f), st[3] + f
        lines += ["", f"## {method} -> {out.name}", "", BAG_METHOD_DOCS[method], "",
                  "| bag | lemmas | freq range | % of total freq count |", "|---:|---:|---|---:|"]
        for b in sorted(stats, reverse=True):
            n, hi, lo, tot = stats[b]
            lines.append(f"| {b} | {n:,} | {lo:,} - {hi:,} | {100 * tot / grand_total:.1f}% |")
    write_report("06_build_bags.md", lines)


if __name__ == "__main__":
    main()
