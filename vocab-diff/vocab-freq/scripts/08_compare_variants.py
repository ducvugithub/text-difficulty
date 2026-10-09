"""Step 8: which bag method and level (stem or lemma bags) separates difficulty best?

For each bag method and each level (stem: every stem of a word is a unit; lemma: the word's own lemma), build the vocab
features on a sample (VocabDiffFeatureConstruct) and report the Spearman correlation with the difficulty label of:
  mean_log_freq        mean log10 count of the stems / of the lemmas in a bin (higher = easier words, expect negative)
  OOV_coverage         share of unknown words (expect positive)
  mean_bag             average bag number of the words that are in a bag (bag 1 = most frequent, so higher = rarer words, expect positive)
  borrowed_coverage    share of English-looking units (easy for English speakers, expect negative)
Shown for all rows and for Finnish-native-only rows.

Output: reports/08_compare_variants.md
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root: base.py, builder.py, dataset.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
from base import TextAnalysis  # noqa: E402
from builder import TextDiffFeaturesConstruct  # noqa: E402
from common import ensure_dirs, write_report  # noqa: E402
from text_common import BAG_METHODS, load_split  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="train", choices=["train", "valid", "test"])
    ap.add_argument("--sample", type=int, default=5000, help="texts to sample per subset (0 = all)")
    args = ap.parse_args()
    ensure_dirs()

    full = load_split(args.split)
    subsets = {"all": full, "finnish-native-only": full[full["origine"] == "Real"]}
    analyses = {}
    for name, df in subsets.items():
        if name != "all" and len(df) == len(full):
            continue  # identical to `all`
        if args.sample and len(df) > args.sample:
            df = df.sample(args.sample, random_state=0)
        analyses[name] = TextAnalysis(df)

    lines = [f"# 08 compare variants ({args.split}, stem and lemma bags)", "",
             "Spearman correlation with the difficulty label, for all rows and for `finnish-native-only` (`origine` = Real). "
             f"At most {args.sample or 'all'} texts per subset are sampled. mean_bag is over the words that are in a bag.", "",
             "| level | subset | texts | bag method | rho mean_log_freq | rho OOV_coverage | rho mean_bag | rho borrowed_coverage |", "|---|---|---:|---|---:|---:|---:|---:|"]
    for method in BAG_METHODS:
        construct = TextDiffFeaturesConstruct(configs={"vocab": {"signals": ["freq"], "lemma_bin_method": method, "stem_bin_method": method}}).constructs["vocab"].parts["freq"]
        for name, analysis in analyses.items():
            feats = construct.build(analysis)
            label = analysis.df["label"].to_numpy()
            for lv in ("stem", "lemma"):
                cov = feats[construct.bag_columns[lv]].to_numpy()
                weights = np.arange(1, construct.n_bags[lv] + 1)
                mean_bag = (cov * weights).sum(axis=1) / np.where(cov.sum(axis=1) == 0, 1, cov.sum(axis=1))
                rho = [spearmanr(x, label).statistic for x in (feats[f"mean_log_{lv}_freq"], feats[f"{lv}_OOV_coverage"], mean_bag, feats[f"{lv}_borrowed_coverage"])]
                lines.append(f"| {lv} | {name} | {len(analysis.df):,} | {method} | {rho[0]:+.3f} | {rho[1]:+.3f} | {rho[2]:+.3f} | {rho[3]:+.3f} |")
        print(f"{method} done")
    write_report("08_compare_variants.md", lines)


if __name__ == "__main__":
    main()
