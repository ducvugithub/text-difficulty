# text-difficulty

- `data/` — raw inputs (train/valid/test CSVs, `finnish_vocab.txt` frequency list). Read-only.
- `vocab-diff/` — word-level difficulty. Produces the cleaned frequency list + other word signals.
- `grammar-diff/` — syntactic / morphological complexity signals.
- `cognitive-diff/` — processing-load signals (discourse, density, surprisal).
- `text-diff/` — document-level models. text-diff = vocab + grammar + cognitive; consumes the three signal dirs.

Dependency order: vocab-diff -> (grammar-diff, cognitive-diff) -> text-diff/{feature-curated-based,bert-based}.
