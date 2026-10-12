"""Builds and caches the features of registered signals, and assembles a feature set (a spec like those in modeling/feature_sets.py).

A signal's features for a split are cached in outputs/features/ (git-ignored) and rebuilt when the signal's feature names change or
with refresh=True; after changing a signal's code, refresh (python scripts/build_features.py --refresh) so the cache is not stale.
"""
import hashlib
import json
import time

import pandas as pd

from utils import registry
from utils.base import ROOT, TextAnalysis
from utils.dataset import OLD_VOCAB, load_split, original_feature_columns, surface_features

CACHE_DIR = ROOT / "outputs" / "features"
_originals = {}


def _path(split, category, signal, settings):
    tag = hashlib.md5(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:8] if settings else "default"
    return CACHE_DIR / f"{category}.{signal}.{tag}.{split}.pkl"


def signal_features(split, category, signal, settings=None, refresh=False) -> pd.DataFrame:
    """The features of one signal for one split (from the cache when present)."""
    settings = settings or {}
    construct = registry.make(category, signal, **settings)
    path = _path(split, category, signal, settings)
    if path.exists() and not refresh:
        cached = pd.read_pickle(path)
        if list(cached.columns) == list(construct.feature_names):
            return cached
    start = time.time()
    features = construct.build(TextAnalysis(load_split(split)))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    features.to_pickle(path)
    print(f"built {category}.{signal} {split}: {features.shape} in {time.time() - start:.0f}s", flush=True)
    return features


def _original_columns():
    if "all" not in _originals:
        _originals["all"] = original_feature_columns()
    return _originals["all"]


def feature_table(split, spec, refresh=False):
    """(X, df): the feature matrix of a feature set for a split, and the split's metadata frame.

    `spec` is an entry of modeling/feature_sets.FEATURE_SETS: {"signals": [(category, signal[, settings])], "original": "all" | "no_vocab", "columns": [data columns], "surface": bool}.
    """
    df = load_split(split)
    parts = []
    if spec.get("original"):
        cols = _original_columns()
        parts.append(df[[c for c in cols if spec["original"] == "all" or c not in OLD_VOCAB]])
    if spec.get("columns"):
        parts.append(df[spec["columns"]])
    if spec.get("surface"):
        parts.append(surface_features(df))
    for category, signal, *rest in spec.get("signals", []):
        parts.append(signal_features(split, category, signal, rest[0] if rest else None, refresh))
    return pd.concat(parts, axis=1), df
