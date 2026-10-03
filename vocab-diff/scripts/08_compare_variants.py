"""Step 8: which frequency variant / list size separates difficulty best?

For each variant (`freq`, `rarest_stem_freq` = with the compound rule) and
top-n, compute text-level features on a sample and report Spearman correlation with the difficulty label:
  mean_log_freq (log10(freq+1) per token, OOV = 0), OOV_coverage, mean_bag (OOV = 0).
A strongly negative mean_log_freq / mean_bag correlation = a better difficulty signal.

Output: reports/08_compare_variants.md
"""
import argparse
import math

import pandas as pd
from scipy.stats import spearmanr

from common import ensure_dirs, write_report
from text_common import analyse_tokens, assign_bags, best_lemma, load_lemma_list, load_split, token_counts

VARIANTS = ["freq", "rarest_stem_freq"]
TOP_NS = [10_000, 20_000, 50_000, 100_000, 0]


def features(counts, chosen, freq, bags):
    """Per text: (mean_log_freq, OOV_coverage, mean_bag) over non-skipped tokens."""
    out = []
    for cnt in counts:
        denom = logf = oov = bag_sum = 0
        for tok, n in cnt.items():
            kind, lemma = chosen[tok]
            if kind == "skip":
                continue
            denom += n
            if lemma is None:
                oov += n
                continue
            logf += n * math.log10(freq[lemma] + 1)
            b = bags.get(lemma)
            if b is None:
                oov += n
            else:
                bag_sum += n * b
        out.append((logf / denom, oov / denom, bag_sum / denom) if denom else (0.0, 1.0, 0.0))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="train", choices=["train", "valid", "test"])
    ap.add_argument("--sample", type=int, default=5000, help="texts to sample (0 = all)")
    args = ap.parse_args()
    ensure_dirs()

    df = load_split(args.split)
    if args.sample and len(df) > args.sample:
        df = df.sample(args.sample, random_state=0)
    counts = token_counts(df["text"])
    analysis = analyse_tokens({t for c in counts for t in c})
    label = df["label"].to_numpy()

    lines = [f"# 08 compare variants ({args.split}, {len(df):,} texts)", "",
             "| variant | top-n | rho mean_log_freq | rho OOV_coverage | rho mean_bag |", "|---|---:|---:|---:|---:|"]
    for variant in VARIANTS:
        lemmas, freq = load_lemma_list(variant)
        chosen = {tok: ("skip", None) if st in ("name", "abbrev") else ("w", best_lemma(c, freq) if st == "ok" else None)
                  for tok, (st, c) in analysis.items()}
        for top_n in TOP_NS:
            feats = pd.DataFrame(features(counts, chosen, freq, assign_bags(lemmas, top_n)), columns=["lf", "oov", "bag"])
            rho = [spearmanr(feats[c], label).statistic for c in ("lf", "oov", "bag")]
            lines.append(f"| {variant} | {top_n or 'all'} | {rho[0]:+.3f} | {rho[1]:+.3f} | {rho[2]:+.3f} |")
        print(f"{variant} done")
    write_report("08_compare_variants.md", lines)


if __name__ == "__main__":
    main()
