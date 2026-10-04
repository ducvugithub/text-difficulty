"""Step 6: cut the ranked STEM list and the ranked LEMMA list into vocab bags (1 = most frequent ... highest = rarest).

Stems are the roots of the words (työ, paikka, ostaa) with their full count (every lemma that contains them, added up);
lemmas are the dictionary forms with their own count. English-looking stems / lemmas were removed in step 5, so they
are not in a bag. --bag-method picks how to cut (default: all three, one output file each):
  uniform_rank_bin     equal number of items per bag
  uniform_cumfreq_bin  equal share (10%) of the total freq count per bag
  log10_freq_bin       one bag per factor of 10 in frequency
Explanations of each method are written into the report.

Input : cleaned/05_stem_freq.tsv, cleaned/05_lemma_freq.tsv
Output: cleaned/06_stem_bags_{method}.tsv, cleaned/06_lemma_bags_{method}.tsv (item, freq, bag), reports/06_build_bags.md
"""
import argparse
import math

from common import CLEANED, ensure_dirs, write_report
from text_common import BAG_METHOD_DOCS, BAG_METHODS, assign_bags, load_lemma_list, load_stem_list


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bag-method", default="all", choices=["all", *BAG_METHODS])
    args = ap.parse_args()
    ensure_dirs()

    lines = ["# 06 build bags", "- bag 1 = most frequent ... highest bag = rarest",
             "- columns of the bag files: `stem` / `lemma`; `freq` its count (a stem's full count, a lemma's own count); `bag` the bag number"]
    for level, loader in (("stem", load_stem_list), ("lemma", lambda: load_lemma_list("freq"))):
        items, freq = loader()
        grand_total = sum(freq.values())
        lines += ["", f"# {level.capitalize()} bags", "", f"{len(items):,} {level}s in the list, ranked by `freq`"]
        for method in BAG_METHODS if args.bag_method == "all" else [args.bag_method]:
            bags = assign_bags(items, freq, method)
            out = CLEANED / f"06_{level}_bags_{method}.tsv"
            stats = {}  # bag -> [items, max freq, min freq, freq total]
            with open(out, "w", encoding="utf-8") as dst:
                dst.write(f"{level}\tfreq\tbag\n")
                for item in items:
                    b, f = bags[item], int(freq[item])
                    dst.write(f"{item}\t{f}\t{b}\n")
                    st = stats.setdefault(b, [0, f, f, 0])
                    st[0] += 1
                    st[1], st[2], st[3] = max(st[1], f), min(st[2], f), st[3] + f
            doc = BAG_METHOD_DOCS[method].replace("lemmas", f"{level}s").replace("Lemmas", f"{level.capitalize()}s")
            band = method == "log10_freq_bin"  # fixed band edges: bag b covers 10^(top-b+1) <= freq < 10^(top-b+2)
            top = max(int(math.log10(freq[i])) for i in items) if band else 0
            lines += ["", f"## {level}s: {method} -> {out.name}", "", doc, "",
                      f"| bag | {level}s | " + ("band (fixed edges) | " if band else "") + "observed freq range | % of total freq count |",
                      "|---:|---:|" + ("---|" if band else "") + "---|---:|"]
            for b in sorted(stats):
                n, hi, lo, tot = stats[b]
                edges = f" {10 ** (top - b + 1):,} to {10 ** (top - b + 2) - 1:,} |" if band else ""
                lines.append(f"| {b} | {n:,} |{edges} {lo:,} - {hi:,} | {100 * tot / grand_total:.1f}% |")
    write_report("06_build_bags.md", lines)


if __name__ == "__main__":
    main()
