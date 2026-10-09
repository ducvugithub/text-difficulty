"""VocabDiffFeatureConstruct: the vocab category, composed of signals. Each signal is a folder with its own code and reports.

  freq     vocab-freq/freq_features.py     FreqBinFeatures: stem and lemma frequency bins, OOV, English-looking share
  lexical  lexical/lexical_features.py     LexicalFeatures: word form, compounding, derivation, lexical diversity

    VocabDiffFeatureConstruct()                                   both signals, default bins
    VocabDiffFeatureConstruct(signals=["lexical"])                the lexical signal only
    VocabDiffFeatureConstruct(lemma_bin_method="uniform_rank_bin", stem_n_bins=8)   bin settings go to the freq signal

A new signal (concreteness, CEFR levels, ...) is a new folder with a class that subclasses VocabFeatureConstruct
(vocab-diff/shared/vocab_base.py, the parent of every signal), registered in SIGNALS.
"""
import importlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from base import ROOT, FeatureConstruct, TextAnalysis  # noqa: E402

sys.path.insert(0, str(ROOT))
# signal -> (module path, class name); the folder names contain hyphens, so import by string
SIGNALS = {
    "freq": ("vocab-diff.vocab-freq.freq_features", "FreqBinFeatures"),
    "lexical": ("vocab-diff.lexical.lexical_features", "LexicalFeatures"),
}


class VocabDiffFeatureConstruct(FeatureConstruct):
    category = "vocab"

    def __init__(self, signals=("freq", "lexical"), **freq_settings):
        unknown = [s for s in signals if s not in SIGNALS]
        if unknown:
            raise ValueError(f"unknown signals {unknown}; available: {list(SIGNALS)}")
        self.parts = {}
        for name in signals:
            module, cls = SIGNALS[name]
            settings = freq_settings if name == "freq" else {}
            self.parts[name] = getattr(importlib.import_module(module), cls)(**settings)
        self.feature_names = [n for part in self.parts.values() for n in part.feature_names]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        return pd.concat([part.build(analysis) for part in self.parts.values()], axis=1)
