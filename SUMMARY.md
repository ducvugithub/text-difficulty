# Summary: which approach predicts Finnish text difficulty best?

Two approaches, graded on the same 865 real-Finnish test texts. Numbers are the average miss in label points (labels run from 1 to 6, one step is 0.5); smaller is better. They are copied from the detailed reports linked below.

| model | features | trained on real-Finnish rows | trained on all rows |
|---|---|---:|---:|
| **gradient boosting** | **curated**: vocabulary + grammar concepts + cognitive (311 features, the best of the 12 feature sets tried) | **0.257** | **0.333** |
| ridge | the same 311 curated features | 0.513 | 0.626 |
| gradient boosting | reference: **all (old)**, the 402 original columns that came with the data | 0.374 | 0.493 |
| ridge | the same 402 original columns | 0.659 | 0.946 |
| **ridge** | **BERT** frozen (`TurkuNLP/bert-base-finnish-cased-v1`, 125M parameters): the embedding of the best layer (768 numbers) | 0.389 (layer 5) | 0.467 (layer 11) |
| fine-tuned BERT with LoRA | the text itself (same BERT; only 0.3M of its 125M parameters are trained) | not run yet | not run yet |
| gradient boosting | reference: 4 surface measures (words, characters, word length, sentence length) | 0.354 | 0.473 |
| constant guess | none (the median label) | 1.229 | 1.325 |

## Takeaways
- The curated features with gradient boosting are the best so far (0.257). With the same model type (ridge), BERT is better than the curated features (0.389 against 0.513).
- For BERT the best layer is layer 5 when trained on real-Finnish rows and layer 11 when trained on all rows. It was picked on the test set, so these numbers are slightly optimistic.
- Four simple surface measures already reach 0.354, so part of every score reflects simple readability or the source of the texts, not deeper difficulty. When one source is left out of training and the model is graded on it, the curated features beat the surface baseline in only 1 of 4 cases (`yle`).
- What the best model relies on: sentence length by far, then word length and vocabulary variety, then some grammar concepts (more participles go with harder texts, more personal pronouns and indicative mood with easier ones). The syllabus topics are not used: they add nothing once the concepts are there ([concepts vs topics](curated_features/modeling/reports/GRAMMAR_CONCEPTS_VS_TOPICS.md)). Details in the feature-importance report below.

## Details
- Curated features: [results](curated_features/modeling/reports/RESULTS.md), [source-transfer check](curated_features/modeling/reports/SOURCE_TRANSFER.md), [feature list](curated_features/docs/features.md), [feature importance](curated_features/modeling/reports/FEATURE_IMPORTANCE.md), [concepts vs topics](curated_features/modeling/reports/GRAMMAR_CONCEPTS_VS_TOPICS.md)
- BERT: [frozen embeddings per layer](bert_based/reports/BERT_LAYERS.md) (the fine-tuning report, `bert_based/reports/BERT_FINETUNE.md`, appears after that run)

## Reproduce
```
python curated_features/scripts/build_features.py --sets all_new                       # curated features
python curated_features/modeling/run_experiment.py --train train_native --tag main     # and --train train_all
python curated_features/modeling/make_results_report.py                                # RESULTS.md
python curated_features/modeling/run_source_transfer.py                                # SOURCE_TRANSFER.md
python curated_features/modeling/run_feature_importance.py                             # FEATURE_IMPORTANCE.md
python bert_based/embeddings.py                                                        # BERT embeddings (cached)
python bert_based/run_layers.py                                                        # BERT_LAYERS.md
python bert_based/run_finetune.py --train train_native --lora                          # fine-tuned BERT with LoRA; also train_all (needs free memory)
```
The table above is written by hand: after re-running, copy the new numbers from the reports.
