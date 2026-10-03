# feature-curated-based

Hand-crafted features (syntax, morphology paradigms, vocab_bag_* coverage, OOV) + classical model (GBM/LR).
- `src/` — feature extraction, model training/eval.
- `outputs/` — feature tables, metrics, models.
To do: recompute `vocab_bag_*_coverage` + `OOV_coverage` from `vocab-diff/vocab-freq/cleaned/`; compare old vs new.
Feature definitions: see `../../data/Source_ ... - Features.csv`.
