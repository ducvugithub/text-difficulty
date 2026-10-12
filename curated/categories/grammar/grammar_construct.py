"""GrammarDiffFeatureConstruct: the grammar category, composed of signals. Each signal is a folder with its own code
and works on one kind of item (Revita concepts or syllabus topics).

  manual_concepts_levels  share of concept occurrences per CEFR level        (Revita's manual levels)
  manual_topics_levels    share of syllabus-topic occurrences per CEFR level
  rarity_concepts           how rare the concepts are, from their frequency in Revita's Finnish stories
  rarity_topics             how rare the topics are, the same way
  coverage_concepts       the share of each concept in the text, one feature per concept (no guess about which are hard)
  coverage_topics         the same per syllabus topic

    GrammarDiffFeatureConstruct()                                    every signal, from the precomputed Revita columns
    GrammarDiffFeatureConstruct(signals=["rarity_topics"])             one signal only
    GrammarDiffFeatureConstruct(bin_method="uniform_cumfreq_bin", n_bins=5)   bin settings go to the rarity signals
    GrammarDiffFeatureConstruct(source="analyser")                   run Revita's pipeline on the text instead (new texts)

Signals are registered in curated/utils/registry.py.
"""
from curated.utils.base import CategoryConstruct
from curated.utils.registry import SIGNALS


class GrammarDiffFeatureConstruct(CategoryConstruct):
    category = "grammar"

    def __init__(self, signals=None, source="columns", **rarity_settings):
        settings = {name: {"source": source, **(rarity_settings if name.startswith("rarity_") else {})} for name in SIGNALS["grammar"]}
        super().__init__(signals, settings)
