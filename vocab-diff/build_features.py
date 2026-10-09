"""Build the vocab-category text features (VocabDiffFeatureConstruct: the frequency-bin and lexical signals) for
train/valid/test and report how each relates to the difficulty label.

The features and their definitions: vocab-diff/vocab_construct.py and docs/features.md.

Output: outputs/vocab_text_features_{split}.csv, vocab-diff/reports/vocab_features.md
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root: base.py, builder.py, dataset.py
sys.path.insert(0, str(Path(__file__).resolve().parent / "shared"))
from base import ROOT, TextAnalysis  # noqa: E402
from builder import TextDiffFeaturesConstruct  # noqa: E402
from common import ensure_dirs  # noqa: E402
from text_common import BAG_METHODS, SPLIT_FILES, load_split  # noqa: E402

OUT_DIR = ROOT / "outputs"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lemma-bin-method", default="log10_freq_bin", choices=BAG_METHODS)
    ap.add_argument("--stem-bin-method", default="uniform_cumfreq_bin", choices=BAG_METHODS)
    ap.add_argument("--lemma-n-bins", type=int, default=10)
    ap.add_argument("--stem-n-bins", type=int, default=10)
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(exist_ok=True)

    builder = TextDiffFeaturesConstruct(configs={"vocab": {"lemma_bin_method": args.lemma_bin_method, "stem_bin_method": args.stem_bin_method, "lemma_n_bins": args.lemma_n_bins, "stem_n_bins": args.stem_n_bins}})

    frames, feats = {}, {}
    for split in SPLIT_FILES:
        frames[split] = load_split(split)
        feats[split] = builder.build(TextAnalysis(frames[split]), category=["vocab"])
        out = feats[split].copy()
        out.insert(0, "label", frames[split]["label"])
        out.to_csv(OUT_DIR / f"vocab_text_features_{split}.csv", index_label="row")

    names = [n for n in feats["train"].columns if "_bag_" not in n]
    df, f = frames["train"], feats["train"]
    native = (df["origine"] == "Real").to_numpy()
    lines = ["# 09 vocab text features", "",
             f"Built by `VocabDiffFeatureConstruct` (lemma bins {args.lemma_bin_method}/{args.lemma_n_bins}, stem bins {args.stem_bin_method}/{args.stem_n_bins}). "
             "Definitions in `docs/features.md`. `-minen` and `-sti` are heuristics (Voikko does not mark them as derivations). "
             "Lemmas are context-free (see the TODO in CLEANUP_SUMMARY.md). The `stem_bag_k_coverage` / `lemma_bag_k_coverage` columns are in the CSVs but not listed here.",
             "", "Spearman correlation with the difficulty label (train); more extreme = stronger relationship.", "",
             "| feature | rho all rows | rho finnish-native-only |", "|---|---:|---:|"]
    for n in names:
        lines.append(f"| {n} | {spearmanr(f[n], df['label']).statistic:+.3f} | {spearmanr(f[n][native], df['label'][native]).statistic:+.3f} |")
    lines += ["", "## Mean per split", "", "| feature | " + " | ".join(feats) + " |", "|---|" + "---:|" * len(feats)]
    for n in names:
        lines.append(f"| {n} | " + " | ".join(f"{feats[s][n].mean():.3f}" for s in feats) + " |")
    report = Path(__file__).resolve().parent / "reports" / "vocab_features.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report ->", report)


if __name__ == "__main__":
    main()
