"""TopicRarityFeatures: how rare the Revita syllabus topics of a text are, from their frequency in Revita's Finnish stories (see shared/rarity_features.py)."""
from curated_features.categories.grammar.shared.rarity_features import RarityFeatures


class TopicRarityFeatures(RarityFeatures):
    kind = "topic"
