"""Base classes for the text-difficulty feature constructs.

TextAnalysis      the texts plus their shared preprocessing (tokens, Voikko readings), computed once and cached,
                  so every construct reuses it. Later: a dependency parse for grammar / cognitive features.
FeatureConstruct  base class of the per-category constructs (VocabDiffFeatureConstruct, ...).
"""
import sys
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
# the Voikko helpers are shared by the vocab signals
sys.path.insert(0, str(ROOT / "vocab-diff" / "shared"))

from common import WORD_RE  # noqa: E402
from text_common import analyse_tokens_full  # noqa: E402


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


class FeatureConstruct(ABC):
    category: str  # e.g. "vocab"
    feature_names: list[str]

    @abstractmethod
    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        """One row per text (index = analysis.df.index), one column per feature."""
