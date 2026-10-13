"""Run Revita's own pipeline on a text and count the concepts and topics it finds. Nothing is re-implemented:
DummyStory (revita_library/story_dummy.py) builds `candidates`, each with `concepts` and `topics`; the counting
mirrors Revita's extract_concept_features (a concept once per candidate) and Story.__get_snippet_topic_diff
(a topic only when it is in the candidate's `usable_topics`).

Needs Revita's Python environment, its parser server and its MongoDB, all configured in Revita itself (this code
holds no credentials): REVITA_HOME is the Revita repo (default: the sibling folder `revita`), MODEL_HOME_URL the
parser host, and the database comes from Revita's curated_features/scripts/mongo_connection.py. Easiest is to run inside a Revita
container.

Results are cached by text hash, so a text is analysed once.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from curated_features.categories.grammar.shared.grammar_levels import REVITA, fin_concepts

CACHE = Path(__file__).resolve().parents[1] / "outputs" / "revita_analyser_cache.json"


def _count(story) -> dict:
    wanted = set(fin_concepts())
    concepts = Counter(c for cand in story.candidates for c in {x["concept_id"] for x in cand["concepts"]} & wanted)
    topics = Counter(t["topic_id"] for cand in story.candidates for t in cand.get("topics", [])
                     if t["topic_id"] in cand.get("usable_topics", []))
    return {"concepts": dict(concepts), "topics": dict(topics)}


def analyse(texts: list[str]) -> list[dict]:
    """[{"concepts": {id: n}, "topics": {id: n}}] per text, from Revita's pipeline (cached)."""
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
    todo = [(k, t) for k, t in zip(keys, texts) if k not in cache]
    if todo:
        sys.path.insert(0, str(REVITA))
        import config  # noqa: F401  (Revita's config puts its language tools, model_interface, on sys.path)
        from revita_library.story_dummy import DummyStory  # Revita's code
        from scripts.mongo_connection import db  # Revita's own connection, configured in Revita
        for k, t in dict(todo).items():
            story = DummyStory(db, "Finnish", t, compute_difficulty=False, compute_category=False, compute_stats=False)
            cache[k] = _count(story)
            CACHE.parent.mkdir(exist_ok=True)
            CACHE.write_text(json.dumps(cache))
    return [cache[k] for k in keys]


def count_table(texts: list[str], kind: str) -> pd.DataFrame:
    """One row per text, one column per concept (kind="concepts") or topic (kind="topics")."""
    return pd.DataFrame([r[kind] for r in analyse(texts)]).fillna(0.0)
