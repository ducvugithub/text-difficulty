"""Named feature sets for the experiments.

The data files carry 402 precomputed features. The experiments swap only the 11 old vocab columns (OOV_coverage and
vocab_bag_k_coverage) for the new vocab bin features and leave everything else unchanged:

  no_vocab             the original features without the old vocab columns (reference)
  old_vocab_bins       the 402 original features: no_vocab + the 11 old vocab columns (baseline)
  new_lemma_bins       no_vocab + the lemma bin features (OOV, English-looking share, bin coverage, mean log count)
  new_stem_bins        no_vocab + the stem bin features (the same, per stem)
  new_lemma_stem_bins  no_vocab + both
  surface              control for length shortcuts: text length, word length, average sentence length
Source and origin are never used as features.
The new features come from outputs/vocab_text_features_{split}.csv (step 9).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataset import OLD_VOCAB, ROOT, load_split, original_feature_columns, surface_features  # noqa: E402

_cache = {}


def _original_columns():
    if "orig" not in _cache:
        _cache["orig"] = original_feature_columns()
    return _cache["orig"]


def new_bins(split):
    """(lemma bin features, stem bin features) of a split."""
    df = pd.read_csv(ROOT / "outputs" / f"vocab_text_features_{split}.csv", index_col="row").drop(columns=["label"])
    lemma = [c for c in df.columns if c.startswith("lemma_") or c == "mean_log_lemma_freq"]
    stem = [c for c in df.columns if c.startswith("stem_") or c == "mean_log_stem_freq"]
    return df[lemma], df[stem]


def feature_table(split, name):
    """(X, df): the feature matrix of a split for a feature set, and the split's metadata frame."""
    df = load_split(split)
    orig = _original_columns()
    no_vocab = df[[c for c in orig if c not in OLD_VOCAB]]
    lemma_bins, stem_bins = new_bins(split)
    sets = {
        "no_vocab": lambda: no_vocab,
        "old_vocab_bins": lambda: df[orig],
        "new_lemma_bins": lambda: pd.concat([no_vocab, lemma_bins], axis=1),
        "new_stem_bins": lambda: pd.concat([no_vocab, stem_bins], axis=1),
        "new_lemma_stem_bins": lambda: pd.concat([no_vocab, lemma_bins, stem_bins], axis=1),
        "surface": lambda: pd.concat([surface_features(df), df[["average_sentence_length"]]], axis=1),
    }
    return sets[name](), df


FEATURE_SETS = ["no_vocab", "old_vocab_bins", "new_lemma_bins", "new_stem_bins", "new_lemma_stem_bins", "surface"]
DESCRIPTIONS = {
    "no_vocab": "the original features without the old vocab columns: syntax averages, grammar, morphology and topic counts",
    "old_vocab_bins": "no_vocab plus the 11 old vocab columns (OOV and bag coverage): the baseline",
    "new_lemma_bins": "no_vocab plus the lemma bin features: OOV, English-looking share, share of words per bin, mean log count",
    "new_stem_bins": "no_vocab plus the stem bin features: the same measures, counted per stem",
    "new_lemma_stem_bins": "no_vocab plus the lemma and the stem bin features",
    "surface": "text length, characters, word length and average sentence length, a control for length shortcuts",
}


def aligned_tables(train_split, eval_splits, name):
    """X for the train split and every eval split, with identical columns (needed for one-hot features)."""
    tables = {s: feature_table(s, name) for s in [train_split, *eval_splits]}
    cols = list(tables[train_split][0].columns)
    return {s: (X.reindex(columns=cols, fill_value=0.0), df) for s, (X, df) in tables.items()}
