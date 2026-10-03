"""Step 6: rank the cleaned list into 10 vocab bags (original Revita definition).

Equal-count bins over the frequency-ascending list: bag 1 = rarest, bag 10 = most frequent.
The original list had ~20k lemmas, so --top-n defaults to 20000 (bins over millions of lemmas would put
almost every real word in bag 10).

Input : cleaned/lemma_freq.tsv
Output: cleaned/vocab_bags.tsv (lemma, freq, bag), reports/06_build_bags.md
"""
import argparse

from common import CLEANED, ensure_dirs, write_report
from text_common import N_BAGS, assign_bags, load_lemma_list


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default="rarest_stem_freq", choices=["freq", "rarest_stem_freq"])
    ap.add_argument("--top-n", type=int, default=20_000, help="bin only the N most frequent lemmas (0 = all)")
    args = ap.parse_args()
    ensure_dirs()

    lemmas, freq = load_lemma_list(args.variant)
    bags = assign_bags(lemmas, args.top_n)
    out = CLEANED / "vocab_bags.tsv"
    stats = {b: [0, None, None] for b in range(1, N_BAGS + 1)}  # bag -> [lemmas, max freq, min freq]
    with open(out, "w", encoding="utf-8") as dst:
        dst.write("lemma\tfreq\tbag\n")
        for lemma in lemmas[: args.top_n or None]:
            b, f = bags[lemma], freq[lemma]
            dst.write(f"{lemma}\t{f:.2f}\t{b}\n")
            st = stats[b]
            st[0] += 1
            st[1] = f if st[1] is None else max(st[1], f)
            st[2] = f if st[2] is None else min(st[2], f)
    lines = ["# 06 build bags", f"- variant {args.variant}, top-n {args.top_n or 'all'}, {len(bags):,} lemmas -> {out.name}", "",
             "Columns of vocab_bags.tsv: `lemma`; `freq` the chosen variant's value; `bag` 1 (rarest) .. 10 (most frequent).", "",
             "| bag | lemmas | freq range |", "|---:|---:|---|"]
    for b in range(N_BAGS, 0, -1):
        n, hi, lo = stats[b]
        lines.append(f"| {b} | {n:,} | {lo:,.0f} - {hi:,.0f} |")
    write_report("06_build_bags.md", lines)


if __name__ == "__main__":
    main()
