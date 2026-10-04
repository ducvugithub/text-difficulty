"""Step 9: build the vocab-category text features (VocabDiffFeatureConstruct) for train/valid/test and report how
each relates to the difficulty label.

The features and their definitions: vocab-diff/vocab_construct.py and docs/features.md.

Output: outputs/vocab_text_features_{split}.csv, reports/09_vocab_text_features.md
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from base import ROOT, TextAnalysis  # noqa: E402
from builder import TextDiffFeaturesConstruct  # noqa: E402
from common import ensure_dirs, write_report  # noqa: E402
from text_common import SPLIT_FILES, load_split  # noqa: E402

OUT_DIR = ROOT / "outputs"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bag-method", default="uniform_cumfreq_bin")
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(exist_ok=True)

    builder = TextDiffFeaturesConstruct(configs={"vocab": {"bag_method": args.bag_method}})

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
             f"Built by `VocabDiffFeatureConstruct` (stem bags, bag method {args.bag_method}). "
             "Definitions in `docs/features.md`. `-minen` and `-sti` are heuristics (Voikko does not mark them as derivations). "
             "Lemmas are context-free (see the TODO in CLEANUP_SUMMARY.md). The `stem_bag_k_coverage` / `lemma_bag_k_coverage` columns are in the CSVs but not listed here.",
             "", "Spearman correlation with the difficulty label (train); more extreme = stronger relationship.", "",
             "| feature | rho all rows | rho finnish-native-only |", "|---|---:|---:|"]
    for n in names:
        lines.append(f"| {n} | {spearmanr(f[n], df['label']).statistic:+.3f} | {spearmanr(f[n][native], df['label'][native]).statistic:+.3f} |")
    lines += ["", "## Mean per split", "", "| feature | " + " | ".join(feats) + " |", "|---|" + "---:|" * len(feats)]
    for n in names:
        lines.append(f"| {n} | " + " | ".join(f"{feats[s][n].mean():.3f}" for s in feats) + " |")
    write_report("09_vocab_text_features.md", lines)


if __name__ == "__main__":
    main()
