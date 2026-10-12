"""CEFR levels of the Revita grammar concepts and syllabus topics, read straight from the Revita repo (REVITA_HOME).

Concepts: concept_tables/Concepts - fi-base.csv, column `level`, e.g. "['A2/B1']".
Topics:   syllabus/fin_syllabus.json, field `level`, e.g. "A1.3"; the sublevel is dropped (A1.3 -> A1).
Anything without a level is "unlevelled"; it is not a feature bin and is left out of the counts.
"""
import ast
import csv
import importlib.util
import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REVITA = Path(os.environ.get("REVITA_HOME", ROOT.parent / "revita"))
UNLEVELLED = "unlevelled"
CONCEPT_LEVELS = ("A1", "A1/A2", "A1/B1", "A2", "A2/B1", "B1", "B1/B2", "B2")
TOPIC_LEVELS = ("A1", "A2", "B1", "B2")


@lru_cache(maxsize=1)
def concept_level() -> dict:
    """concept_id -> level bin, for every concept in the Finnish concept table."""
    with open(REVITA / "concept_tables" / "Concepts - fi-base.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["concept_id"]: (ast.literal_eval(r["level"])[0] if r["level"].strip() else UNLEVELLED) for r in rows}


@lru_cache(maxsize=1)
def topic_level() -> dict:
    """topic_id -> level bin, for every Finnish syllabus topic."""
    with open(REVITA / "syllabus" / "fin_syllabus.json", encoding="utf-8") as f:
        items = json.load(f)
    return {t["topic_id"]: (t["level"].split(".")[0] if t.get("level") else UNLEVELLED)
            for t in items if t.get("type", "topic") == "topic"}


@lru_cache(maxsize=1)
def fin_concepts() -> list:
    """The concepts Revita's difficulty model counts (difficulty_api/all_fin_concepts.py, loaded by path)."""
    spec = importlib.util.spec_from_file_location("all_fin_concepts", REVITA / "difficulty_api" / "all_fin_concepts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.all_fin_concepts)
