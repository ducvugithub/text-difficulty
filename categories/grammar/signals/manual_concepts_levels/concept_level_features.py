"""ConceptLevelFeatures: share of a text's Revita concept occurrences at each CEFR level (concept_tables/Concepts - fi-base.csv)."""
from categories.grammar.shared.level_features import LevelFeatures


class ConceptLevelFeatures(LevelFeatures):
    kind = "concept"
