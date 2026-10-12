"""Named feature sets for the experiments, built by utils/feature_store.py.

A set is made of registered signals (vocab, grammar, cognitive), and optionally the original data columns ("original"), chosen
data columns ("columns") and the text-length control ("surface"). Source and origin are never features. To add a set, add an
entry to FEATURE_SETS here (and to EXPERIMENT_SETS to include it by default; LABELS gives its readable name for reports).
"""
from utils.dataset import OLD_VOCAB
from utils.feature_store import feature_table

VOCAB = [("vocab", "freq"), ("vocab", "lexical")]
MANUAL = [("grammar", "manual_concepts_levels"), ("grammar", "manual_topics_levels")]
RARITY = [("grammar", "rarity_concepts"), ("grammar", "rarity_topics")]
COVERAGE = [("grammar", "coverage_concepts"), ("grammar", "coverage_topics")]
COGNITIVE = [("cognitive", "parse_precomputed"), ("cognitive", "sentence_length")]

FEATURE_SETS = {
    # controls and the original features that come with the data
    "text_length": {"description": "text length only: words, characters, mean word length, mean sentence length", "surface": True},
    "original_vocab_bins": {"description": "the 11 old vocabulary-bin columns that come with the data (OOV and 10 bags)", "columns": OLD_VOCAB},
    "original_all": {"description": "the 402 original columns: syntax averages, old vocab bins, concept and topic columns", "original": "all"},
    # one category each
    "vocab": {"description": "vocab: lemma and stem frequency bins, English-looking share, lexical features", "signals": VOCAB},
    "grammar_manual": {"description": "grammar: share of concept and topic occurrences per CEFR level (Revita's manual levels)", "signals": MANUAL},
    "grammar_rarity": {"description": "grammar: how rare the concepts and topics are in Revita's Finnish stories (bin shares, mean IDF)", "signals": RARITY},
    "grammar_coverage": {"description": "grammar: the share of every concept and every topic in the text (one feature each)", "signals": COVERAGE},
    "grammar_all": {"description": "grammar: manual levels, rarity and coverage together", "signals": MANUAL + RARITY + COVERAGE},
    "cognitive": {"description": "cognitive: the old parse features (tree depth, distinct POS, sentence length) plus sentence count / mean / max / std length", "signals": COGNITIVE},
    "cognitive_dependency": {"description": "cognitive: tree depth, dependency distance, clauses from our own parse (needs the parser)", "signals": [("cognitive", "dependency")]},
    # combinations
    "vocab_grammar_coverage": {"description": "vocab and grammar coverage", "signals": VOCAB + COVERAGE},
    "vocab_grammar_coverage_cognitive": {"description": "vocab, grammar coverage and cognitive", "signals": VOCAB + COVERAGE + COGNITIVE},
    "all_new": {"description": "every new feature: vocab, all grammar, cognitive", "signals": VOCAB + MANUAL + RARITY + COVERAGE + COGNITIVE},
}

# the sets an experiment compares by default (--sets chooses others), in the order of the reports
EXPERIMENT_SETS = ["text_length", "original_vocab_bins", "vocab", "grammar_manual", "grammar_rarity", "grammar_coverage", "grammar_all", "cognitive",
                   "vocab_grammar_coverage", "vocab_grammar_coverage_cognitive", "all_new", "original_all"]
# readable names for reports: (new) = built here, (old) = the columns that come with the data
LABELS = {
    "text_length": "length only (new)", "original_vocab_bins": "vocab_bins (old)", "original_all": "all (old)",
    "vocab": "vocab (new)", "grammar_manual": "grammar_manual (new)", "grammar_rarity": "grammar_rarity (new)",
    "grammar_coverage": "grammar_coverage (new)", "grammar_all": "grammar_all (new)", "cognitive": "cognitive (new)",
    "cognitive_dependency": "cognitive_dependency (new)", "vocab_grammar_coverage": "vocab + grammar_coverage (new)",
    "vocab_grammar_coverage_cognitive": "vocab + grammar_coverage + cognitive (new)", "all_new": "all (new)",
}
DESCRIPTIONS = {name: spec["description"] for name, spec in FEATURE_SETS.items()}


def aligned_tables(train_split, eval_splits, name):
    """X for the train split and every eval split, with identical columns (needed for one-hot features)."""
    tables = {s: feature_table(s, FEATURE_SETS[name]) for s in [train_split, *eval_splits]}
    cols = list(tables[train_split][0].columns)
    return {s: (X.reindex(columns=cols, fill_value=0.0), df) for s, (X, df) in tables.items()}
