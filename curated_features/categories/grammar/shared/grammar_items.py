"""What the grammar signals count, per kind: Revita concepts or syllabus topics. The per-kind differences live here
so the signals themselves are kind-agnostic.

  ids(kind)        the items counted (concepts Revita's difficulty model counts; syllabus topics except the listening exercises)
  levels(kind)     the CEFR bins; level_map(kind): item -> bin ("unlevelled" items are not counted by the level signals)
  reference(kind)  how often each item occurs in Revita's Finnish stories (reference/*.tsv, made by reference/export_reference.py)
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

from curated_features.categories.grammar.shared.grammar_levels import CONCEPT_LEVELS, TOPIC_LEVELS, concept_level, fin_concepts, topic_level

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "reference"
KINDS = ("concept", "topic")
LISTENING = "Topic: Listen"  # listening exercises, not grammar


def _check(kind):
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")


@lru_cache(maxsize=None)
def ids(kind: str) -> list:
    _check(kind)
    if kind == "concept":
        return fin_concepts()
    return [t for t in topic_level() if not t.startswith(LISTENING)]


def levels(kind: str) -> tuple:
    _check(kind)
    return CONCEPT_LEVELS if kind == "concept" else TOPIC_LEVELS


def level_map(kind: str) -> dict:
    _check(kind)
    return concept_level() if kind == "concept" else topic_level()


@lru_cache(maxsize=None)
def reference(kind: str) -> pd.DataFrame:
    """Reference occurrences, indexed by item, most frequent first: columns `count` (occurrences), `n_stories`."""
    _check(kind)
    df = pd.read_csv(REFERENCE_DIR / f"{kind}_freq.tsv", sep="\t", index_col="id")
    return df[df.index.isin(set(ids(kind)))].sort_values("count", ascending=False, kind="stable")
