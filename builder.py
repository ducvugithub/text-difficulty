"""TextDiffFeaturesConstruct: build text-difficulty features from the per-category constructs.

    builder = TextDiffFeaturesConstruct(configs={"vocab": {"lemma_bin_method": "log10_freq_bin", "stem_bin_method": "uniform_cumfreq_bin"}})   # configs: constructor kwargs per category
    features = builder.build(TextAnalysis(df), category=["vocab"])                    # default: every available category

Each category lives in its own directory (vocab-diff/, grammar-diff/, cognitive-diff/) as a FeatureConstruct subclass.
Categories whose module does not exist yet are skipped and raise a clear error if requested.
"""
import importlib
import sys

import pandas as pd

from base import ROOT, FeatureConstruct, TextAnalysis

sys.path.insert(0, str(ROOT))

# category -> (module path, class name); directory names contain hyphens, so import by string
CONSTRUCTS = {
    "vocab": ("vocab-diff.vocab_construct", "VocabDiffFeatureConstruct"),
    "grammar": ("grammar-diff.grammar_construct", "GrammarDiffFeatureConstruct"),
    "cognitive": ("cognitive-diff.cognitive_construct", "CognitiveDiffFeatureConstruct"),
}


class TextDiffFeaturesConstruct:
    def __init__(self, configs: dict[str, dict] | None = None):
        """`configs` maps a category to the keyword arguments of its construct, e.g. {"vocab": {"stem_n_bins": 8}}."""
        configs = configs or {}
        self.constructs: dict[str, FeatureConstruct] = {}
        for category, (module, cls) in CONSTRUCTS.items():
            try:
                self.constructs[category] = getattr(importlib.import_module(module), cls)(**configs.get(category, {}))
            except ModuleNotFoundError as e:
                if e.name != module.split(".")[0] and e.name != module:
                    raise  # a real missing dependency, not a category that is not implemented yet

    @property
    def categories(self) -> list[str]:
        return list(self.constructs)

    def build(self, analysis: TextAnalysis, category: list[str] | None = None) -> pd.DataFrame:
        categories = category or self.categories
        missing = [c for c in categories if c not in self.constructs]
        if missing:
            raise ValueError(f"categories not available: {missing}; available: {self.categories}")
        return pd.concat([self.constructs[c].build(analysis) for c in categories], axis=1)
