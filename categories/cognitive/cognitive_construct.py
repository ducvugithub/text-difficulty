"""CognitiveDiffFeatureConstruct: the cognitive category (how much the reader has to hold in mind), composed of signals.

  sentence_length  signals/sentence_length/   sentence count, mean / max / std length (plain sentence split, no parser)
  dependency       signals/dependency/        tree depth, dependency distance, clauses and subordination (needs the parser server)
  parse_old    signals/parse_old/     Revita's tree depth, distinct POS and sentence length columns (splits only)

    CognitiveDiffFeatureConstruct()                           the signals that need no parser (sentence_length)
    CognitiveDiffFeatureConstruct(signals=["dependency"])     parse the texts (categories/cognitive/shared/parser_client.py)

Signals are registered in utils/registry.py.
"""
from utils.base import CategoryConstruct


class CognitiveDiffFeatureConstruct(CategoryConstruct):
    category = "cognitive"
