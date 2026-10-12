"""GrammarFeatureConstruct: parent of the grammar signals. A signal works on ONE kind of item, a Revita concept or a
syllabus topic (`kind`), and turns the item counts of each text into features.

Where the counts come from is `source`:
  "columns"   the precomputed Revita columns already in the data CSVs (the splits)
  "analyser"  Revita's own pipeline run on the text (shared/revita_analyser.py), for new texts
Subclasses implement build(): LevelFeatures (CEFR level shares) and RarityFeatures (rarity), one subclass per kind.
"""
import pandas as pd

from curated.utils.base import FeatureConstruct, TextAnalysis
from curated.categories.grammar.shared import grammar_items
from curated.categories.grammar.shared.revita_analyser import count_table


class GrammarFeatureConstruct(FeatureConstruct):
    category = "grammar"
    kind = ""  # "concept" | "topic"

    def __init__(self, source: str = "columns"):
        if source not in ("columns", "analyser"):
            raise ValueError("source must be 'columns' or 'analyser'")
        self.source = source

    def counts(self, analysis: TextAnalysis) -> pd.DataFrame:
        """Occurrences of each counted item per text (columns: items)."""
        if self.source == "columns":
            return analysis.df[[c for c in grammar_items.ids(self.kind) if c in analysis.df.columns]]
        return count_table(analysis.texts, f"{self.kind}s").set_axis(analysis.df.index)

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        raise NotImplementedError
