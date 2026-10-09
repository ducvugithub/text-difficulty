"""The difficulty data: loading the three splits and naming their column groups.

Every split CSV carries 402 precomputed features shared by all three (syntax averages, old vocab-bag coverage,
grammar / morphology / topic counts). Columns that came from an earlier model (`Predict Label`, `Diff`, `true_score`,
`predicted_score`, `Difference`) are leakage and never used as features.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SPLIT_FILES = {"train": "Fi_train.csv", "valid": "Fi_valid.csv", "test": "Fi_test.csv"}
META = ["text", "label", "origine", "source"]
OLD_VOCAB = ["OOV_coverage"] + [f"vocab_bag_{k}_coverage" for k in range(1, 11)]
_WORD = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")


def load_split(split):
    return pd.read_csv(DATA / f"Source_ Finnish Difficulty texts with features - {SPLIT_FILES[split]}")


def original_feature_columns():
    """The 402 feature columns present in all three splits (leakage columns and metadata excluded)."""
    cols = [list(load_split(s).columns) for s in SPLIT_FILES]
    common = [c for c in cols[0] if all(c in c2 for c2 in cols[1:])]
    return [c for c in common if c not in META]


def surface_features(df):
    """Plain length features computed from the text."""
    words = [_WORD.findall(str(t)) for t in df["text"]]
    return pd.DataFrame({
        "n_words": [len(w) for w in words],
        "n_chars": [len(str(t)) for t in df["text"]],
        "mean_word_len": [sum(map(len, w)) / len(w) if w else 0.0 for w in words],
    }, index=df.index)
