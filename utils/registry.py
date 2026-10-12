"""The registry of feature signals: what exists, and which run by default. It is the one place to edit to add a signal.

SIGNALS      category -> signal name -> (module, class). A signal is one folder in categories/<category>/signals/.
DEFAULTS     the signals a category builds when none are named (parser-based ones are left out: they need the parser server).
NEEDS_PARSER signals that need the parser server.

  Add a signal: write the class (subclass the category's parent), add a line to SIGNALS.
The named feature sets an experiment compares are in modeling/feature_sets.py.
"""
import importlib

SIGNALS = {
    "vocab": {
        "freq": ("categories.vocab.signals.vocab_freq.freq_features", "FreqBinFeatures"),
        "lexical": ("categories.vocab.signals.lexical.lexical_features", "LexicalFeatures"),
    },
    "grammar": {
        "manual_concepts_levels": ("categories.grammar.signals.manual_concepts_levels.concept_level_features", "ConceptLevelFeatures"),
        "manual_topics_levels": ("categories.grammar.signals.manual_topics_levels.topic_level_features", "TopicLevelFeatures"),
        "rarity_concepts": ("categories.grammar.signals.rarity_concepts.concept_rarity_features", "ConceptRarityFeatures"),
        "rarity_topics": ("categories.grammar.signals.rarity_topics.topic_rarity_features", "TopicRarityFeatures"),
        "coverage_concepts": ("categories.grammar.signals.coverage_concepts.concept_coverage_features", "ConceptCoverageFeatures"),
        "coverage_topics": ("categories.grammar.signals.coverage_topics.topic_coverage_features", "TopicCoverageFeatures"),
    },
    "cognitive": {
        "sentence_length": ("categories.cognitive.signals.sentence_length.sentence_length_features", "SentenceLengthFeatures"),
        "dependency": ("categories.cognitive.signals.dependency.dependency_features", "DependencyFeatures"),
        "parse_precomputed": ("categories.cognitive.signals.parse_precomputed.parse_precomputed_features", "PrecomputedParseFeatures"),
    },
}
DEFAULTS = {
    "vocab": ["freq", "lexical"],
    "grammar": list(SIGNALS["grammar"]),
    "cognitive": ["sentence_length"],
}
NEEDS_PARSER = {("cognitive", "dependency")}


def make(category: str, signal: str, **settings):
    """An instance of a registered signal."""
    if signal not in SIGNALS.get(category, {}):
        raise ValueError(f"unknown signal {category}.{signal}; available: {list(SIGNALS.get(category, {}))}")
    module, cls = SIGNALS[category][signal]
    return getattr(importlib.import_module(module), cls)(**settings)
