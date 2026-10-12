# text-difficulty

Features and models for Finnish text difficulty. A text's difficulty is described by three categories of signals: vocab, grammar and cognitive. Every signal is registered in `utils/registry.py`.

```
text-difficulty/
├── categories/       the three categories of signals
│   ├── vocab/        word-level difficulty: signals/vocab_freq (frequency bins; list cleaning, bins), signals/lexical (word form, compounds, derivation)
│   ├── grammar/      which grammar a text uses, from Revita's concepts and topics: CEFR level shares, rarity, coverage per item
│   └── cognitive/    sentence length, tree depth, dependency distance
├── utils/            the shared machinery the categories plug into
├── modeling/         the experiments; the results are in modeling/reports/RESULTS.md (raw outputs in reports/runs/)
├── scripts/          commands you run (build_features.py)
├── docs/features.md  every feature, its category and status
├── data/             raw inputs (train/valid/test CSVs, frequency list); local only, git-ignored
└── outputs/          generated feature tables and caches; git-ignored
```

Each folder in `categories/` has `signals/` (one folder per signal), `shared/` (helpers and parent classes) and a `*_construct.py` that composes its signals. Their READMEs say more.

`utils/`:
- `dataset.py` — loads the train/valid/test CSVs and names the column groups
- `base.py` — `TextAnalysis` (texts + shared preprocessing computed once: Voikko readings, sentences, dependency parse) and the `FeatureConstruct` / `CategoryConstruct` base classes
- `binning.py` — the frequency-bin methods shared by the vocab and grammar frequency signals
- `registry.py` — every signal, and which a category builds by default
- `feature_store.py` — builds a signal's features and caches them in `outputs/features/`
- `feature_builder.py` — `TextDiffFeaturesConstruct`: builds the features of any subset of categories

```python
builder = TextDiffFeaturesConstruct(configs={"vocab": {"lemma_bin_method": "log10_freq_bin"}})
features = builder.build(TextAnalysis(df), category=["vocab", "grammar"])   # default: every category
```

- **Add a signal:** write the class in `categories/<category>/signals/<name>/`, register it in `utils/registry.py`.
- **Add a feature set:** an entry in `FEATURE_SETS` in `modeling/feature_sets.py`.
- **Build features:** `python scripts/build_features.py --list`, then `--sets <name>` or `--signals <category.signal>`.
- **Run an experiment, then rebuild the results file:** `python modeling/run_experiment.py --train train_native --tag main`, the same with `train_all`, then `python modeling/make_results_report.py`.

Imports are absolute from this folder, so run scripts from here. Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`; `voikkospell` on PATH. Grammar needs the Revita repo next to this one (or `REVITA_HOME`).
