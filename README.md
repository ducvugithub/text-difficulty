# text-difficulty

Predicting how difficult a Finnish text is, in two ways (overall result: [SUMMARY.md](SUMMARY.md)): with hand-curated features (`curated_features/`) and with BERT (`bert_based/`).

```
text-difficulty/
├── core/                  shared by both ways
│   ├── dataset.py         load the train / valid / test splits, column groups, text surface features
│   ├── evaluate.py        MAE, accuracy, within-one-step, balanced accuracy, bootstrap intervals, confusion matrices
│   └── reporting.py       markdown report helpers
├── curated_features/      way 1: hand-curated vocab, grammar and cognitive features
│   ├── categories/        vocab, grammar, cognitive: one folder per signal
│   ├── utils/             base classes, registry, feature builder and cache
│   ├── modeling/          feature sets, experiments, reports (RESULTS.md, SOURCE_TRANSFER.md, runs/)
│   ├── scripts/           build_features.py
│   └── docs/features.md   every feature, its category and status
├── bert_based/            way 2: BERT embeddings and fine-tuning
│   ├── embeddings.py  run_layers.py  run_finetune.py
│   └── reports/           BERT_LAYERS.md, BERT_FINETUNE.md
├── data/                  raw inputs (train/valid/test CSVs, frequency list); local only, git-ignored
└── outputs/               generated feature tables, embeddings and caches; git-ignored
```

## Way 1: curated features

Features come in three categories, each made of signals registered in `curated_features/utils/registry.py`:
vocab, grammar (from Revita's concepts and topics) and cognitive (sentence length, parse features). The experiments compare named feature sets
(defined in `curated_features/modeling/feature_sets.py`) with gradient boosting and ridge regression. Results: `curated_features/modeling/reports/RESULTS.md`.

- **Build features:** `python curated_features/scripts/build_features.py --list`, then `--sets <name>` or `--signals <category.signal>`.
- **Run an experiment, then rebuild the results file:** `python curated_features/modeling/run_experiment.py --train train_native --tag main`, the same with `train_all`, then `python curated_features/modeling/make_results_report.py`.
- **Add a signal:** write the class in `curated_features/categories/<category>/signals/<name>/` and register it in `curated_features/utils/registry.py`. **Add a feature set:** an entry in `FEATURE_SETS` in `curated_features/modeling/feature_sets.py`.

## Way 2: BERT based

Uses the Finnish BERT model `TurkuNLP/bert-base-finnish-cased-v1` (`--model` chooses another). Texts longer than 512 word-pieces are cut into windows.

- `bert_based/embeddings.py`: frozen embeddings, one vector per text and layer, cached in `outputs/embeddings/` (`python bert_based/embeddings.py`).
- `bert_based/run_layers.py`: ridge regression on each layer's embedding; writes `bert_based/reports/BERT_LAYERS.md`.
- `bert_based/run_finetune.py`: BERT with a regression head, fine-tuned; `--lora` trains only small adapters (0.24% of the weights), without it every weight is trained. Writes `bert_based/reports/BERT_FINETUNE.md` (needs a machine with free memory).

## Setup

Imports are absolute from this folder, so run scripts from here. `python -m venv .venv && .venv/bin/pip install -r requirements.txt`; `voikkospell` on PATH.
The grammar features need the Revita repo next to this one (or `REVITA_HOME`).
