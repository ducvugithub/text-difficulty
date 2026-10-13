# curated_features/categories/grammar

Which grammar a text uses, from Revita's concepts (`concept_tables/Concepts - fi-base.csv`) and syllabus topics (`syllabus/fin_syllabus.json`). Signals are in `signals/`, one folder each, and each works on one kind of item:

| signal | what it gives |
|---|---|
| `manual_concepts_levels`, `manual_topics_levels` | share of the text's levelled items at each CEFR level (Revita's manual levels; unlevelled items not counted) |
| `rarity_concepts`, `rarity_topics` | rarity from how often each item occurs in Revita's Finnish stories: bin shares, unseen share, mean IDF |
| `coverage_concepts`, `coverage_topics` | the share of every concept / topic in the text, one feature per item |

- `grammar_construct.py` — `GrammarDiffFeatureConstruct`, composes the signals (registered in `../utils/registry.py`).
- `shared/` — `grammar_items.py` (per-kind details), `grammar_base.py` (parent: counts from the data columns or from the analyser), `level_features.py`, `rarity_features.py`, `coverage_features.py`, `grammar_levels.py` (level tables read from the Revita repo, `REVITA_HOME`), `revita_analyser.py` (Revita's pipeline on a text).
- `reference/` — `export_reference.py` exports concept / topic frequencies from the Revita database (run inside a Revita container; no credentials stored here); `concept_freq.tsv`, `topic_freq.tsv` are its output.

Counts come from the precomputed Revita columns of the splits (`source="columns"`, default) or from Revita's own pipeline (`source="analyser"`, for new texts; needs the Revita environment, see `shared/revita_analyser.py`). The precomputed columns came from an older Revita run, so concepts differ somewhat from the analyser's.
