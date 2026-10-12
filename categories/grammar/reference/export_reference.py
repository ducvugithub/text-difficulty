"""Export how often each grammar concept / syllabus topic occurs in Revita's Finnish stories (the reference corpus).

Runs INSIDE a Revita container, because only Revita can reach its database; no credentials are used or stored here:

    ssh revita_staging 'docker exec -i -w /app/revita -e LANGTOOLS_HOME=/language-tools revita-main-1 python3 - concepts' \
        < export_reference.py | grep '^TSV' | cut -f2- > concept_freq.tsv        (same with `topics` -> topic_freq.tsv)

Output columns: id, count (occurrences), n_stories (stories it occurs in). The ids are exported unfiltered; the
loader (shared/grammar_reference.py) keeps the concepts Revita's difficulty model counts and the syllabus topics.
Counting follows Revita: a concept once per candidate (extract_concept_features), a topic per entry of the
candidate's `usable_topics` (Story.__get_snippet_topic_diff).
"""
import sys

sys.path.insert(0, "/app/revita")
import config  # noqa: F401,E402  (Revita's config; sets up its environment)
from scripts.mongo_connection import db  # noqa: E402

kind = sys.argv[1]
if kind == "concepts":
    items = {"$setUnion": ["$concepts.concept_id", []]}
elif kind == "topics":
    usable = {"$ifNull": ["$usable_topics", []]}
    items = {"$map": {"input": {"$filter": {"input": {"$ifNull": ["$topics", []]}, "as": "t",
                                            "cond": {"$in": ["$$t.topic_id", usable]}}},
                      "as": "t", "in": "$$t.topic_id"}}
else:
    raise SystemExit("usage: export_reference.py concepts|topics")

pipeline = [
    {"$match": {"language": "Finnish"}},
    {"$project": {"story_id": 1, "items": items}},
    {"$unwind": "$items"},
    {"$group": {"_id": {"id": "$items", "story": "$story_id"}, "n": {"$sum": 1}}},
    {"$group": {"_id": "$_id.id", "count": {"$sum": "$n"}, "n_stories": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]
print("TSV\tid\tcount\tn_stories")
for r in db.candidates.aggregate(pipeline, allowDiskUse=True, maxTimeMS=100000):
    print(f"TSV\t{r['_id']}\t{r['count']}\t{r['n_stories']}")
