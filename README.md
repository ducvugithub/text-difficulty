# text-difficulty

Predicting how difficult a Finnish text is, in two ways.

```
text-difficulty/
├── core/                  shared by both ways
│   ├── dataset.py         load the train / valid / test splits, column groups, text surface features
│   └── evaluate.py        MAE, accuracy, within-one-step, balanced accuracy, bootstrap intervals, confusion matrices
├── curated/               the feature-curated way: hand-built vocab, grammar and cognitive features
│   ├── categories/        vocab, grammar, cognitive: one folder per signal
│   ├── utils/             base classes, registry, feature builder and cache
│   ├── modeling/          feature sets, experiments, reports (RESULTS.md, SOURCE_TRANSFER.md, runs/)
│   ├── scripts/           build_features.py
│   └── docs/features.md   every feature, its category and status
├── bert/                  the BERT-driven way (in progress)
├── data/                  raw inputs (train/valid/test CSVs, frequency list); local only, git-ignored
└── outputs/               generated feature tables and caches; git-ignored
```

## The feature-curated way

Features come in three categories, each made of signals registered in `curated/utils/registry.py`:
vocab, grammar (from Revita's concepts and topics) and cognitive (sentence length, parse features). The experiments compare named feature sets
(defined in `curated/modeling/feature_sets.py`) with gradient boosting and ridge regression. Results: `curated/modeling/reports/RESULTS.md`.

- **Build features:** `python curated/scripts/build_features.py --list`, then `--sets <name>` or `--signals <category.signal>`.
- **Run an experiment, then rebuild the results file:** `python curated/modeling/run_experiment.py --train train_native --tag main`, the same with `train_all`, then `python curated/modeling/make_results_report.py`.
- **Add a signal:** write the class in `curated/categories/<category>/signals/<name>/` and register it in `curated/utils/registry.py`. **Add a feature set:** an entry in `FEATURE_SETS` in `curated/modeling/feature_sets.py`.

## The BERT-driven way

Uses the Finnish BERT model `TurkuNLP/bert-base-finnish-cased-v1` (`--model` chooses another). Texts longer than 512 word-pieces are cut into windows.

- `bert/embeddings.py`: frozen embeddings, one vector per text and layer, cached in `outputs/embeddings/` (`python bert/embeddings.py`).
- `bert/run_layers.py`: ridge regression on each layer's embedding; writes `bert/reports/BERT_LAYERS.md`.
- `bert/run_finetune.py`: BERT with a regression head, fine-tuned; writes `bert/reports/BERT_FINETUNE.md` (needs a machine with free memory: about an hour per training set).

## Setup

Imports are absolute from this folder, so run scripts from here. `python -m venv .venv && .venv/bin/pip install -r requirements.txt`; `voikkospell` on PATH.
The grammar features need the Revita repo next to this one (or `REVITA_HOME`).
