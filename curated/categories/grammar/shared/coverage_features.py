"""CoverageFeatures: how much of a text each grammar item covers. The grammar counterpart of the vocab bag coverage, with
one feature per item (a concept or a syllabus topic) and no guess about which items are hard: the model learns that.

grammar_{kind}_cov_{item}   share of the text's counted occurrences that is this item; a row sums to 1 (all 0 if the text has none)
Concept columns of the data are already shares; topic columns are counts and are turned into shares here, so a longer text does not score higher.
"""
import numpy as np
import pandas as pd

from curated.utils.base import TextAnalysis
from curated.categories.grammar.shared import grammar_items
from curated.categories.grammar.shared.grammar_base import GrammarFeatureConstruct


class CoverageFeatures(GrammarFeatureConstruct):
    def __init__(self, source: str = "columns"):
        super().__init__(source)
        self.items = grammar_items.ids(self.kind)
        self.feature_names = [f"grammar_{self.kind}_cov_{item}" for item in self.items]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        counts = self.counts(analysis).reindex(columns=self.items, fill_value=0.0)  # same columns for every split
        shares = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        shares.columns = self.feature_names
        return shares
