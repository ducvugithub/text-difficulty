# text-difficulty

- `data/` — raw inputs (train/valid/test CSVs, `finnish_vocab.txt` frequency list). Local only, git-ignored.
- `vocab-diff/` — word-level difficulty: the cleaned frequency list (`scripts/`, `vocab-freq/`) and `vocab_construct.py` (`VocabDiffFeatureConstruct`).
- `grammar-diff/`, `cognitive-diff/` — syntactic / morphological and processing-load signals (constructs to come).
- `base.py` — `TextAnalysis` (texts + shared preprocessing, computed once) and the `FeatureConstruct` base class.
- `builder.py` — `TextDiffFeaturesConstruct`: builds the features of any subset of categories.
- `docs/features.md` — every feature, its category and status.
- `outputs/` — generated feature tables (git-ignored).

```python
builder = TextDiffFeaturesConstruct(configs={"vocab": {"bag_method": "uniform_cumfreq_bin"}})
features = builder.build(TextAnalysis(df), category=["vocab"])   # default: every available category
```

text difficulty = vocab + grammar + cognitive. Dependency order: vocab-diff list cleaning -> `VocabDiffFeatureConstruct` -> builder.
Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`; `voikkospell` on PATH.
