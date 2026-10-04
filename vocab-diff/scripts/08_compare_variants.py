"""Step 8: which frequency column / bag method / list size separates difficulty best?

For each --freq-column x bag method (all on the full list), compute
text-level features on a sample and report Spearman correlation with the difficulty label:
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

FREQ_COLUMNS = ["freq", "rarest_stem_freq"]
METHODS = ["uniform_rank_bin", "uniform_cumfreq_bin", "log10_freq_bin"]


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

    full = load_split(args.split)
    subsets = {"all": full, "finnish-native-only": full[full["origine"] == "Real"]}
    lists = {column: load_lemma_list(column) for column in FREQ_COLUMNS}

    lines = [f"# 08 compare variants ({args.split})", "",
             "Each combination is shown for two subsets: `all` rows, and `finnish-native-only` (`origine` = Real; the Russian-origin rows are translations). "
             f"At most {args.sample or 'all'} texts per subset are sampled.", "",
             "| subset | texts | freq column | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag |", "|---|---:|---|---|---:|---:|---:|"]
    for name, df in subsets.items():
        if name != "all" and len(df) == len(full):
            continue  # identical to `all`
        if args.sample and len(df) > args.sample:
            df = df.sample(args.sample, random_state=0)
        counts = token_counts(df["text"])
        analysis = analyse_tokens({t for c in counts for t in c})
        label = df["label"].to_numpy()
        for column, (lemmas, freq) in lists.items():
            chosen = {tok: ("skip", None) if st in ("name", "abbrev") else ("w", best_lemma(c, freq) if st == "ok" else None)
                      for tok, (st, c) in analysis.items()}
            for method in METHODS:
                feats = pd.DataFrame(features(counts, chosen, freq, assign_bags(lemmas, freq, method)), columns=["lf", "oov", "bag"])
                rho = [spearmanr(feats[c], label).statistic for c in ("lf", "oov", "bag")]
                lines.append(f"| {name} | {len(df):,} | {column} | {method} | {rho[0]:+.3f} | {rho[1]:+.3f} | {rho[2]:+.3f} |")
        print(f"{name} done")
    write_report("08_compare_variants.md", lines)


if __name__ == "__main__":
    main()
