"""Base classes for the text-difficulty feature constructs.

TextAnalysis      the texts plus their shared preprocessing (tokens, Voikko readings), computed once and cached,
                  so every construct reuses it: Voikko readings (vocab), sentences, and the dependency parse (cognitive).
FeatureConstruct  base class of the per-category constructs (VocabDiffFeatureConstruct, ...).
"""
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

from curated_features.categories.cognitive.shared.sentences import split_sentences
from curated_features.categories.vocab.shared.common import WORD_RE
from curated_features.categories.vocab.shared.text_common import analyse_tokens_full


class TextAnalysis:
    """`df` must have a `text` column; its index is kept on the feature tables."""

    def __init__(self, df: pd.DataFrame, text_col: str = "text"):
        self.df = df
        self.texts = df[text_col].astype(str).tolist()

    @cached_property
    def tokens(self) -> list[list[str]]:
        """Word tokens per text, in order."""
        return [WORD_RE.findall(t) for t in self.texts]

    @cached_property
    def voikko(self) -> dict:
        """token -> (status, readings); readings are (base, class, stems, suffixes). Context-free."""
        return analyse_tokens_full({tok for toks in self.tokens for tok in toks})

    @cached_property
    def sentences(self) -> list[list[str]]:
        """Sentences per text from a plain split (curated_features/categories/cognitive/shared/sentences.py)."""
        return [split_sentences(t) for t in self.texts]

    @cached_property
    def parse(self) -> list[list[list[dict]]]:
        """Dependency parse per text: sentences of tokens {id, form, upos, feats, head, deprel}. Needs the parser server
        (curated_features/categories/cognitive/shared/parser_client.py); parses are cached on disk."""
        from curated_features.categories.cognitive.shared.parser_client import parse_texts
        return parse_texts(self.texts)


class FeatureConstruct(ABC):
    category: str  # e.g. "vocab"
    feature_names: list[str]

    @abstractmethod
    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        """One row per text (index = analysis.df.index), one column per feature."""


class CategoryConstruct(FeatureConstruct):
    """A category (vocab, grammar, cognitive) made of its signals, which come from curated_features.utils/registry.py.

    `signals` are signal names (default: registry.DEFAULTS[category]); `settings` maps a signal name to the keyword arguments
    of its class. Subclasses only fix the category and, if they want, a friendlier constructor.
    """

    def __init__(self, signals=None, settings=None):
        from curated_features.utils import registry
        names = registry.DEFAULTS[self.category] if signals is None else list(signals)
        self.parts = {name: registry.make(self.category, name, **(settings or {}).get(name, {})) for name in names}
        self.feature_names = [n for part in self.parts.values() for n in part.feature_names]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        return pd.concat([part.build(analysis) for part in self.parts.values()], axis=1)
