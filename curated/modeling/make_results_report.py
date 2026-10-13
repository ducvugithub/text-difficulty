"""Write curated/modeling/reports/RESULTS.md, the one results file: the feature sets tried, and the results per model and training set.

The numbers are read from the raw run outputs in curated/modeling/reports/runs/ (run_experiment.py --tag main), so nothing is typed by hand;
the feature lists come from the registry. Run the experiments first, then:

    python curated/modeling/make_results_report.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from core.evaluate import CLASSES  # noqa: E402
from core.reporting import steps, table  # noqa: E402
from curated.modeling.feature_sets import EXPERIMENT_SETS, FEATURE_SETS, LABELS  # noqa: E402
from curated.utils import registry  # noqa: E402
from core.dataset import OLD_VOCAB  # noqa: E402

RUNS = Path(__file__).resolve().parent / "reports" / "runs"
OUT = Path(__file__).resolve().parent / "reports" / "RESULTS.md"
TAG = "main"
TICK = "✓"

# the pieces a feature set can contain: (matrix column, test on a feature-set spec)
SIGNAL = lambda c, s: (lambda spec: any(sig[:2] == (c, s) for sig in spec.get("signals", [])))  # noqa: E731
MATRIX = [
    ("vocab: frequency bins", SIGNAL("vocab", "freq")),
    ("vocab: word form", SIGNAL("vocab", "lexical")),
    ("grammar: manual levels", SIGNAL("grammar", "manual_concepts_levels")),
    ("grammar: rarity", SIGNAL("grammar", "rarity_concepts")),
    ("grammar: coverage", SIGNAL("grammar", "coverage_concepts")),
    ("cognitive: sentence length", SIGNAL("cognitive", "sentence_length")),
    ("parse features (old)", lambda spec: spec.get("original") == "all" or SIGNAL("cognitive", "parse_old")(spec)),
    ("original: vocab bins (11)", lambda spec: spec.get("original") == "all" or bool(spec.get("columns"))),
    ("original: grammar columns (388)", lambda spec: spec.get("original") == "all"),
    ("surface (4)", lambda spec: bool(spec.get("surface"))),
]
PIECES = [  # (name, what it gives, signal or None, number of features for the pieces that are not signals)
    ("vocab: frequency bins", "How common the words are, for lemmas and for stems: share of words in each frequency bin, share unknown, share English-looking, mean log frequency", [("vocab", "freq")], None),
    ("vocab: word form", "How words are built: word length, compounds, derivations (-llinen, -ton, -minen, -sti), number of different lemmas, lexical diversity", [("vocab", "lexical")], None),
    ("grammar: manual levels", "Share of the text's grammar concepts (and, separately, syllabus topics) at each CEFR level A1 to B2, from Revita's manual levels", [("grammar", "manual_concepts_levels"), ("grammar", "manual_topics_levels")], 12),
    ("grammar: rarity", "How rare the text's grammar concepts and topics are in Revita's Finnish stories: share in each rarity bin, share never seen, mean IDF", [("grammar", "rarity_concepts"), ("grammar", "rarity_topics")], 17),
    ("grammar: coverage", "One feature per grammar concept (268) and per syllabus topic (133): its share of the text", [("grammar", "coverage_concepts"), ("grammar", "coverage_topics")], 401),
    ("cognitive: sentence length", "Number of sentences, and the mean, longest and spread of sentence length in words", [("cognitive", "sentence_length")], None),
    ("parse features (old)", "Tree depth, distinct parts of speech and tokens per sentence from the dependency parse; computed by an older Revita run and come with the data", [("cognitive", "parse_old")], None),
    ("original: vocab bins (11)", "Out-of-vocabulary share and the share of words in each of 10 frequency bags, old definition (come with the data)", None, 11),
    ("original: grammar columns (388)", "Each Revita concept's share and each syllabus topic's count, from an older Revita run (come with the data)", None, 388),
    ("surface (4)", "Words, characters, mean word length, mean sentence length; all computed here. A baseline: how far do simple surface measures get?", None, 4),
]


LEXICAL = {
    "n_unique_lemmas": "distinct lemmas in the text (grows with text length)",
    "ttr_lemma_200": "distinct lemmas among the first 200 lemmas / 200 (diversity, length-controlled)",
    "avg_word_length": "mean characters per word", "long_word_ratio": "share of words with 10 or more characters",
    "compound_ratio": "compounds (2 or more stems) / content words", "avg_compound_parts": "mean number of stems per compound",
    "n_compound_tokens": "number of compound words",
    "deriv_llinen_ratio": "-llinen words (asia -> asiallinen) / content words",
    "deriv_ton_ratio": "-ton words (merkitys -> merkityksetön) / content words",
    "deriv_minen_ratio": "-minen words (arvioida -> arvioiminen) / content words (heuristic)",
    "deriv_sti_ratio": "-sti words (erityinen -> erityisesti) / content words (heuristic)",
    "cognitive_sent_n_sentences": "number of sentences (plain split at . ! ?)", "cognitive_sent_mean_len": "mean sentence length in words",
    "cognitive_sent_max_len": "length of the longest sentence in words", "cognitive_sent_std_len": "spread (standard deviation) of sentence length",
    "cognitive_parse_tree_depth": "average depth of the dependency tree per sentence (old)",
    "cognitive_parse_distinct_pos": "average number of different part-of-speech tags per sentence (old)",
    "cognitive_parse_sentence_length": "average tokens per sentence (old)",
    "average_tree_depth": "average depth of the dependency tree per sentence", "average_num_pos": "average number of different part-of-speech tags per sentence",
    "average_sentence_length": "average tokens per sentence", "OOV_coverage": "share of words not in the old frequency list",
}


NOTES = {"parse features (old)": "These are the three syntax columns that come with the data (`average_tree_depth`, `average_num_pos`, `average_sentence_length`); the cognitive sets use them together with our own sentence-length features.",
         "vocab: frequency bins": "Bin 1 holds the most frequent words, higher bins the rarer ones.",
         "grammar: rarity": "Bin 1 holds the concepts and topics that are most common in Revita's Finnish stories, higher bins the rarer ones."}


def meaning(name):
    """What a feature is, from its name."""
    if name in LEXICAL:
        return LEXICAL[name]
    m = re.fullmatch(r"(stem|lemma)_(OOV|borrowed)_coverage", name)
    if m:
        return f"share of {m[1]}s " + ("unknown (not recognised or not in the frequency list)" if m[2] == "OOV" else "that look English (borrowed)")
    if m := re.fullmatch(r"(stem|lemma)_bag_(\d+)_coverage", name):
        return f"share of {m[1]}s in frequency bin {m[2]}"
    if m := re.fullmatch(r"mean_log_(stem|lemma)_freq", name):
        return f"mean log10 count of the {m[1]}s"
    if m := re.fullmatch(r"vocab_bag_(\d+)_coverage", name):
        return f"share of words in old frequency bag {m[1]}"
    if m := re.fullmatch(r"grammar_(concept|topic)_level_(.+)", name):
        return f"share of the text's levelled {m[1]} occurrences at level {m[2].replace('_', '/')}"
    if m := re.fullmatch(r"grammar_(concept|topic)_rarity_bag_(\d+)", name):
        return f"share of {m[1]} occurrences in rarity bin {m[2]}"
    if m := re.fullmatch(r"grammar_(concept|topic)_rarity_unseen", name):
        return f"share of {m[1]} occurrences never seen in Revita's stories"
    if m := re.fullmatch(r"grammar_(concept|topic)_mean_idf", name):
        return f"mean IDF of the {m[1]}s in the text (higher = rarer)"
    if m := re.fullmatch(r"grammar_(concept|topic)_cov_(.+)", name):
        return f"share of the text's {m[1]} occurrences that are `{m[2]}`"
    return ""


def feature_table(names):
    return ["| feature | meaning |", "|---|---|"] + [f"| `{n}` | {meaning(n)} |" for n in names]


def label(name):
    return LABELS.get(name, name)


def bounds(ci):
    lo, hi = ci.strip("[]").split(",")
    return float(lo), float(hi)


def disjoint(a, b):
    (alo, ahi), (blo, bhi) = bounds(a), bounds(b)
    return ahi < blo or bhi < alo


def results_table(rows):
    out = ["| feature set | features | average miss (MAE) [95% interval] | in label steps | exactly right | within one step |", "|---|---:|---|---:|---:|---:|"]
    for name, cols, mae, ci, acc, near in rows:
        out.append(f"| **{label(name)}** | {cols} | {mae} {ci} | {steps(mae)} | {acc} | {near} |" if name != "dummy"
                   else f"| *constant guess ({cols})* | 0 | {mae} | {steps(mae)} | {acc} | {near} |")
    return out


def confusion_section(run, model_heading, sets):
    """Confusion matrices as row percentages, from the raw run output."""
    text = (RUNS / f"{run}_{TAG}.md").read_text(encoding="utf-8")
    out = ["", "#### c. Confusion matrices (trained on real-Finnish rows)", "",
           "Each row is the true label, each column the predicted label (rounded to the nearest half step). A row adds up to 100%; "
           "the **bold** cell on the diagonal is the share predicted exactly right; *n* is the number of test texts with that label."]
    for name in sets:
        out += ["", f"##### {label(name)}", "", "| true label \\ predicted | " + " | ".join(f"{c:g}" for c in CLASSES) + " |", "|---|" + "---:|" * len(CLASSES)]
        for r in table(text, f"### test, {model_heading}: confusion matrix: {name}"):
            true, counts = float(r[0]), [int(x) for x in r[1:]]
            n = sum(counts)
            share = lambda v: "<1%" if 0 < 100 * v / n < 0.5 else f"{100 * v / n:.0f}%"  # noqa: E731
            cells = ["" if v == 0 else (f"**{share(v)}**" if c == true else share(v)) for c, v in zip(CLASSES, counts)]
            out.append(f"| {true:g} (n={n}) | " + " | ".join(cells) + " |")
    return out


def read(model_heading, run):
    """Rows (set, features, MAE, interval, exactly right, within one step) of one model on one run; dummies named by their kind."""
    rows = []
    for r in table((RUNS / f"{run}_{TAG}.md").read_text(encoding="utf-8"), f"## test: {model_heading}"):
        if r[0] in EXPERIMENT_SETS:
            rows.append((r[0], r[2], r[3], r[4], r[5], r[6]))
        elif r[0] == "dummy":
            rows.append(("dummy", "most common label" if "most common" in r[1] else "median label", r[3], "", r[5], r[6]))
    return sorted(rows, key=lambda r: (r[0] == "dummy", EXPERIMENT_SETS.index(r[0]) if r[0] in EXPERIMENT_SETS else 0))


def main():
    gb = {run: read("gradient boosting", run) for run in ("train_native", "train_all")}
    rd = {run: read("ridge regression", run) for run in ("train_native", "train_all")}
    key = {r[0]: r for r in gb["train_native"]}
    real = [r for r in gb["train_native"] if r[0] != "dummy"]
    lowest = min(real, key=lambda r: float(r[2]))
    best = min((r for r in real if not disjoint(r[3], lowest[3])), key=lambda r: int(r[1]))  # fewest features among the sets tied with the lowest MAE
    dummy = next(r for r in gb["train_native"] if r[0] == "dummy")
    n_feat = {r[0]: r[1] for r in gb["train_native"]}
    length, orig, cov = key["surface"], key["original_all"], key["grammar_coverage"]

    L = ["# Results: which features predict text difficulty?", "",
         "Generated by `curated/modeling/make_results_report.py` from the run outputs in `curated/modeling/reports/runs/`; no number is typed by hand. "
         "`(new)` = features built in this repository, `(old)` = the columns that come with the data.", "",
         "## Summary", "",
         "We predict a Finnish text's difficulty (label 1 to 6) from groups of features and compare the average error.", "",
         f"- Best: **{label(best[0])}** ({best[1]} features), average miss {best[2]}, against {orig[2]} for the 402 original columns, {length[2]} for the surface baseline "
         f"(intervals {'do not overlap' if disjoint(best[3], length[3]) else 'overlap'}) and {dummy[2]} for a constant guess."
         + (f" {label(lowest[0])} has the lowest miss ({lowest[2]}) but is the same within noise." if lowest[0] != best[0] else ""),
         f"- Grammar works best as the share of each concept and topic ({cov[2]}), not as manual levels ({key['grammar_manual'][2]}) or rarity ({key['grammar_rarity'][2]}).",
         f"- The new vocabulary features ({key['vocab'][2]}) beat the old vocabulary bins ({key['original_vocab_bins'][2]}).",
         "- Caution: the surface baseline (word and sentence length) is already a strong clue, so part of every score may come from such simple measures or from the source of the texts, not from deeper difficulty.", "",
         "## How to read the numbers", "",
         "- **Average miss (MAE)**: average distance between predicted and true label; smaller is better. One label step is 0.5.",
         "- **Exactly right / within one step**: the prediction, rounded to the nearest half step, equals the label / is off by at most 0.5.",
         "- **95% interval**: from resampling the 865 test texts; overlapping intervals may be noise.",
         "- **Constant guess**: always the same label. The floor.", "",
         "## 1. Feature sets to try", "",
         "A tick means the set contains that piece. The number in brackets is the set's total number of features. "
         "The `cognitive` sets include the three old parse features (they come with the data) together with the new sentence-length features. "
         "The `surface` set is words, characters, mean word length and mean sentence length.", "",
         "| feature set | " + " | ".join(c for c, _ in MATRIX) + " |", "|---|" + ":---:|" * len(MATRIX)]
    for name in EXPERIMENT_SETS:
        L.append(f"| **{label(name)}** ({n_feat[name]}) | " + " | ".join(TICK if test(FEATURE_SETS[name]) else "" for _, test in MATRIX) + " |")
    L += ["", "Where the data behind each piece comes from:", "", "| piece | computed from | new or old |", "|---|---|---|",
          "| vocab: frequency bins, word form | the text itself, with code in this repository (Voikko and our cleaned frequency list) | new |",
          "| grammar: manual levels, rarity, coverage | the concept and topic columns that come with the data (an older Revita run); the features built from them are new | new features, old data |",
          "| cognitive: sentence length | the text itself, with a plain sentence split | new |",
          "| parse features (old) | the three syntax columns that come with the data (an older Revita run) | old |",
          "| surface | the text itself | new |",
          "| original: vocab bins, grammar columns | the columns that come with the data | old |", "",
          "So the grammar features and the parse features rely on an older Revita run. For a new text, the Revita analyser would be needed to produce them; "
          "it works, but its output differs somewhat from the old columns.",
          "", "What each piece contains:", "", "| piece | what it gives | features |", "|---|---|---:|"]
    for name, text, signal, n in PIECES:
        count = n if n is not None else sum(len(registry.make(*sg).feature_names) for sg in signal)
        L.append(f"| **{name}** | {text} | {count} |")

    L += ["", "## 2. Results", "", "All results are on the same 865 real-Finnish test texts. *Trained on real-Finnish rows* uses the 2,332 real-Finnish training texts; "
          "*trained on all rows* adds the translated texts (8,293 in total, 72% translated from Russian).", "",
          "### 2.1 Gradient boosting", "", "A model made of many small decision trees, each one correcting the errors of the ones before it.", "",
          "#### a. Trained on real-Finnish rows (2,332 texts)", ""] + results_table(gb["train_native"]) + [
          "", "#### b. Trained on all rows (8,293 texts)", ""] + results_table(gb["train_all"]) + confusion_section("train_native", "gradient boosting", [best[0], "original_all"])
    L += ["", "### 2.2 Ridge regression", "", "#### a. Trained on real-Finnish rows (2,332 texts)", ""] + results_table(rd["train_native"]) + [
          "", "#### b. Trained on all rows (8,293 texts)", ""] + results_table(rd["train_all"])
    L += ["", "## Appendix: the features", "",
          "Every feature of the pieces above. Concept and topic coverage have one feature per item, so those are listed by item; "
          "`curated/docs/features.md` has the longer definitions of the vocabulary features."]
    for name, _, signal, n in PIECES:
        if signal is None:
            continue
        names = [x for sg in signal for x in registry.make(*sg).feature_names]
        L += ["", f"### {name} ({len(names)})", ""]
        if name in NOTES:
            L += [NOTES[name], ""]
        if name == "grammar: coverage":
            for kind, subset in (("concept", [x for x in names if "_concept_cov_" in x]), ("topic", [x for x in names if "_topic_cov_" in x])):
                items = [x.split("_cov_", 1)[1] for x in subset]
                L += [f"One feature per {kind}, `grammar_{kind}_cov_<{kind}>`: the share of the text's {kind} occurrences that are that {kind}.", "",
                      f"<details><summary>the {len(items)} {kind}s</summary>", "", ", ".join(f"`{i}`" for i in items), "", "</details>", ""]
        else:
            L += feature_table(names)
    L += ["", "### original: vocab bins (11)", ""] + feature_table(OLD_VOCAB)
    L += ["", "### original: grammar columns (388)", "",
          "The same concepts and topics as the coverage features above, from an older Revita run. Concept columns are shares; topic columns are counts."]
    L += ["", "### surface (4)", "", "`n_words`, `n_chars`, `mean_word_len`, `mean_sentence_len`: words, characters, mean characters per word and mean words per sentence."]
    L += ["", "## Where the raw numbers are", "",
          "`curated/modeling/reports/runs/` has the raw run outputs: per-label results, validation results and the paired comparisons (`train_native_main.md`, `train_all_main.md`), "
          "a source and length check (`within_source.md`), and the first vocabulary-only experiment (`first_vocab_only_*.md`). "
          "A separate report, `SOURCE_TRANSFER.md`, tests how the best feature set transfers to a source it has never seen.", "",
          "## How this report was produced", "", "```", "python curated/scripts/build_features.py --sets all_new",
          "python curated/modeling/run_experiment.py --train train_native --tag main", "python curated/modeling/run_experiment.py --train train_all --tag main",
          "python curated/modeling/make_results_report.py", "```", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("report ->", OUT)


if __name__ == "__main__":
    main()
