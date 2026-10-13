"""ConceptCoverageFeatures: the share of each Revita concept in a text (see shared/coverage_features.py)."""
from curated_features.categories.grammar.shared.coverage_features import CoverageFeatures


class ConceptCoverageFeatures(CoverageFeatures):
    kind = "concept"
