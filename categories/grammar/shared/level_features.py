"""LevelFeatures: share of a text's levelled occurrences that falls in each CEFR level (Revita's manual levels).

Items without a level are not counted. One feature per bin: grammar_{kind}_level_{bin}; a text with no levelled item is all 0.
"""
import numpy as np
import pandas as pd

from utils.base import TextAnalysis
from categories.grammar.shared import grammar_items
from categories.grammar.shared.grammar_base import GrammarFeatureConstruct


class LevelFeatures(GrammarFeatureConstruct):
    def __init__(self, source: str = "columns"):
        super().__init__(source)
        self.levels = tuple(b for b in grammar_items.levels(self.kind))
        self.feature_names = [f"grammar_{self.kind}_level_{b.replace('/', '_')}" for b in self.levels]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        counts = self.counts(analysis)
        bins = counts.columns.map(grammar_items.level_map(self.kind))
        by_level = counts.T.groupby(bins).sum().T.reindex(columns=self.levels, fill_value=0.0)  # unlevelled has no bin
        shares = by_level.div(by_level.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        shares.columns = self.feature_names
        return shares
