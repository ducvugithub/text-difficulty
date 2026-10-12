# categories/cognitive

How much the reader has to hold in mind: sentence length, nesting, dependency distance. Signals are in `signals/`, one folder each:

| signal | what it gives | needs |
|---|---|---|
| `sentence_length` | sentence count, mean / max / std length in words | nothing (plain sentence split) |
| `parse_precomputed` | tree depth, distinct POS and tokens per sentence from the dependency parse, precomputed by Revita's pipeline | the splits' precomputed columns |
| `dependency` | tree depth, dependency distance, clauses and subordinate clauses per sentence | the Turku parser server (`shared/parser_client.py`; reached from the Revita hosts, e.g. through an SSH tunnel) |

- `cognitive_construct.py` — `CognitiveDiffFeatureConstruct`, composes the signals (registered in `../utils/registry.py`).
- `shared/` — `cognitive_base.py` (parent class), `sentences.py` (sentence split), `parser_client.py` (parser client with an on-disk cache, one request at a time).

The `dependency` signal has not been run on the splits: the parser takes roughly 0.5-1 s per 1,000 characters, and an SSH tunnel to it dropped during testing.

Ideas not built: discourse (connective density, coreference distance, lemma overlap between sentences), information density (lexical density, propositions per sentence), center-embedding count, LM surprisal, named-entity density.
