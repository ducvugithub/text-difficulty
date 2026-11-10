"""Run inside the Revita container (revita-main-1): Revita's own concept and topic counts for texts, read-only.
The database handle is wrapped so that any write raises instead of changing the database.
Usage: python - [texts.json] < this_script    (without an argument it analyses one test sentence)"""
import json
import sys
from collections import Counter

sys.path.insert(0, "/app/revita")
import config  # noqa: F401,E402
from revita_library.story_dummy import DummyStory  # noqa: E402
from scripts.mongo_connection import db as real_db  # noqa: E402

WRITES = {"insert_one", "insert_many", "update_one", "update_many", "replace_one", "delete_one", "delete_many", "bulk_write", "find_one_and_update",
          "find_one_and_replace", "find_one_and_delete", "drop", "create_index", "drop_collection", "create_collection", "rename", "aggregate_out"}


class GuardedCollection:
    def __init__(self, c):
        self._c = c

    def __getattr__(self, name):
        if name in WRITES:
            raise RuntimeError(f"blocked a database write: {name}")
        return getattr(self._c, name)


class GuardedDB:
    def __init__(self, d):
        self._d = d

    def __getattr__(self, name):
        if name in WRITES or name in ("drop_collection", "create_collection", "command"):
            raise RuntimeError(f"blocked a database write: {name}")
        return GuardedCollection(getattr(self._d, name))

    def __getitem__(self, name):
        return GuardedCollection(self._d[name])


db = GuardedDB(real_db)
texts = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else ["Minä olen Pedro. Olen brasilialainen ja asun nyt Helsingissä. Puhun suomea vähän."]
out = []
for t in texts:
    story = DummyStory(db, "Finnish", t, compute_difficulty=False, compute_category=False, compute_stats=False)
    concepts = Counter(c for cand in story.candidates for c in {x["concept_id"] for x in cand["concepts"]})
    topics = Counter(x["topic_id"] for cand in story.candidates for x in cand.get("topics", []) if x["topic_id"] in cand.get("usable_topics", []))
    out.append({"concepts": dict(concepts), "topics": dict(topics)})
print("RESULT_JSON=" + json.dumps(out))
