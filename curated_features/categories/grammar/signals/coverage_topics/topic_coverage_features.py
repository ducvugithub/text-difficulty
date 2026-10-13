"""TopicCoverageFeatures: the share of each Revita syllabus topic in a text (see shared/coverage_features.py)."""
from curated_features.categories.grammar.shared.coverage_features import CoverageFeatures


class TopicCoverageFeatures(CoverageFeatures):
    kind = "topic"
