"""ConceptRarityFeatures: how rare the Revita concepts of a text are, from their frequency in Revita's Finnish stories (see shared/rarity_features.py)."""
from curated.categories.grammar.shared.rarity_features import RarityFeatures


class ConceptRarityFeatures(RarityFeatures):
    kind = "concept"
