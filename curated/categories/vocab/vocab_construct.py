"""VocabDiffFeatureConstruct: the vocab category, composed of signals. Each signal is a folder with its own code and reports.

  freq     signals/vocab_freq/freq_features.py     FreqBinFeatures: stem and lemma frequency bins, OOV, English-looking share
  lexical  signals/lexical/lexical_features.py     LexicalFeatures: word form, compounding, derivation, lexical diversity

    VocabDiffFeatureConstruct()                                   both signals, default bins
    VocabDiffFeatureConstruct(signals=["lexical"])                the lexical signal only
    VocabDiffFeatureConstruct(lemma_bin_method="uniform_rank_bin", stem_n_bins=8)   bin settings go to the freq signal

Signals are registered in curated/utils/registry.py; a new one subclasses VocabFeatureConstruct (curated/categories/vocab/shared/vocab_base.py).
"""
from curated.utils.base import CategoryConstruct


class VocabDiffFeatureConstruct(CategoryConstruct):
    category = "vocab"

    def __init__(self, signals=None, **freq_settings):
        super().__init__(signals, {"freq": freq_settings})
