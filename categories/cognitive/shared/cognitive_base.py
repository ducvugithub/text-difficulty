"""CognitiveFeatureConstruct: the parent of the cognitive signals (how much the reader has to hold in mind: sentence length,
nesting, dependency distance). It fixes the category; a signal subclasses it and implements build()."""
from utils.base import FeatureConstruct


class CognitiveFeatureConstruct(FeatureConstruct):
    category = "cognitive"
