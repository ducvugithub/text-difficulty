"""What does the best model rely on? Permutation importance of the best curated feature set (gradient boosting, trained on the real-Finnish train texts).

For a feature (or a group of features) the values are shuffled across the 865 test texts; the importance is how much the average miss (MAE) grows. A feature that
does not matter leaves the error unchanged. Correlated features share their importance, so features are also shuffled in groups (one group per piece of the set).
The direction is the rank correlation of the feature with the label on the training texts.

    python curated_features/modeling/run_feature_importance.py        writes curated_features/modeling/reports/FEATURE_IMPORTANCE.md
"""
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from core.dataset import load_split, native_mask, train_mask  # noqa: E402
from core.reporting import md_table, mae_fmt, PCT_NOTE  # noqa: E402
from curated_features.modeling.feature_sets import FEATURE_SETS, LABELS, aligned_tables  # noqa: E402
from curated_features.modeling.make_results_report import meaning  # noqa: E402
from curated_features.utils import registry  # noqa: E402
from curated_features.utils.feature_store import signal_features  # noqa: E402

BEST = "vocab_grammar_coverage_cognitive"
REPEATS = 5
TOP = 20
REPORT = Path(__file__).resolve().parent / "reports" / "FEATURE_IMPORTANCE.md"
GROUPS = {  # a group is one piece of the set: its registry signals
    "vocab: word frequency bins": [("vocab", "freq")], "vocab: word form": [("vocab", "lexical")],
    "grammar concepts (one feature per concept)": [("grammar", "coverage_concepts")],
    "cognitive: sentence length": [("cognitive", "sentence_length")], "parse features (old)": [("cognitive", "parse_old")],
}


def shuffled_mae(model, X, y, cols, rng):
    """MAE after shuffling the columns `cols` together (the same permutation of the rows for all of them)."""
    out = []
    for _ in range(REPEATS):
        Z = X.copy()
        Z[:, cols] = Z[rng.permutation(len(Z))][:, cols]
        out.append(np.abs(model.predict(Z) - y).mean())
    return np.array(out)


def _rho(x, y):
    return float("nan") if np.ptp(x) == 0 else float(spearmanr(x, y).statistic)


def _fmt(v):
    return "–" if np.isnan(v) else f"{v:+.2f}"


def vocab_bin_section():
    """Markdown lines: rank correlation of every vocab frequency feature with the label (bin 1 = most frequent words, higher bins = rarer)."""
    feats = {s: signal_features(s, "vocab", "freq") for s in ("train", "test")}
    df = {s: load_split(s) for s in feats}
    native = native_mask(df["train"])
    rows = []
    for n in feats["train"].columns:
        ytr, yte = df["train"]["label"].to_numpy(), df["test"]["label"].to_numpy()
        x = feats["train"][n].to_numpy()
        rows.append((n, _rho(x, ytr), _rho(x[native], ytr[native]), _rho(feats["test"][n].to_numpy(), yte)))
    L = ["", "## Vocab frequency bins and the label: rank correlation", "",
         "Separate from the permutation importance above: how each word-frequency feature moves with the label. **Bin 1** holds the most frequent words, **higher bins** the rarer ones; "
         "each bin feature is the share of the text's words in that bin. +1 means a higher value always goes with a harder text, -1 the opposite, 0 no relationship. "
         "The columns use different rows: all 8,293 train rows (72% translated from Russian), the 2,332 real-Finnish train rows, and the 865 real-Finnish test texts. "
         "A correlation is not a cause: rarer words often come with longer words and longer texts."]
    for title, prefixes in (("Lemma level (the word's own lemma is placed in a bin)", ("lemma_", "mean_log_lemma")), ("Stem level (every stem of a word is placed in a bin)", ("stem_", "mean_log_stem"))):
        sub = sorted((r for r in rows if r[0].startswith(prefixes)), key=lambda r: (not r[0].startswith("mean_log"), "_bag_" not in r[0], r[0] if "_bag_" not in r[0] else int(r[0].split("_bag_")[1].split("_")[0])))
        L += ["", f"### {title}", ""] + md_table(["feature", "meaning", "all train rows", "real-Finnish train rows", "test set"],
                                               [[f"`{n}`", meaning(n), _fmt(a), _fmt(b), _fmt(c)] for n, a, b, c in sub])
    return L


def main():
    warnings.filterwarnings("ignore")
    tables = aligned_tables("train", ["test"], BEST)
    (Xtr, dtr), (Xte, dte) = tables["train"], tables["test"]
    mask = train_mask(dtr, "train_native")
    ytr, yte = dtr["label"].to_numpy(), dte["label"].to_numpy()
    model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0).fit(Xtr[mask].to_numpy(), ytr[mask])
    X = Xte.to_numpy()
    base = float(np.abs(model.predict(X) - yte).mean())
    print(f"baseline test MAE {mae_fmt(base)}", flush=True)
    names = list(Xte.columns)
    index = {n: i for i, n in enumerate(names)}
    rng = np.random.default_rng(0)

    group_rows = []
    for g, signals in GROUPS.items():
        cols = [index[n] for c, s in signals for n in registry.make(c, s).feature_names if n in index]
        grown = shuffled_mae(model, X, yte, cols, rng) - base
        group_rows.append((g, len(cols), grown.mean(), grown.std()))
    group_rows.sort(key=lambda r: -r[2])

    single = []
    for j, n in enumerate(names):
        grown = shuffled_mae(model, X, yte, [j], rng) - base
        rho = spearmanr(Xtr[n].to_numpy()[mask], ytr[mask]).statistic
        single.append((n, grown.mean(), grown.std(), 0.0 if np.isnan(rho) else float(rho)))
    single.sort(key=lambda r: -r[1])
    group_of = {n: g for g, signals in GROUPS.items() for c, s in signals for n in registry.make(c, s).feature_names}

    top_group, top_feature = group_rows[0], single[0]
    L = ["# What the best model relies on: permutation importance by feature group", "",
         f"Generated by `curated_features/modeling/run_feature_importance.py`. Model: {LABELS[BEST]}, {len(names)} features, gradient boosting, trained on the real-Finnish train texts; "
         f"the test set (865 texts) has an average miss of {mae_fmt(base)}.", "", "## Summary", "",
         f"- The group that matters most is **{top_group[0]}**: shuffling its {top_group[1]} features raises the average miss by {top_group[2]:.3f}.",
         f"- The single most important feature is `{top_feature[0]}`: {meaning(top_feature[0])} (shuffling it raises the miss by {top_feature[1]:.3f}).",
         f"- {sum(1 for r in single if r[1] > 0.002)} of {len(names)} features have an importance above 0.002; the rest add almost nothing on their own.", "",
         "## How to read it", "",
         "- **Permutation importance**: the values of a feature (or of a whole group of features) are scrambled, i.e. exchanged between the test texts, and we measure how much "
         "the performance gets worse. A group is scrambled as a block: all its features move together, so a text keeps the relationships among the group's own features.",
         "- **Importance** = how much the average miss (MAE) grows after the scramble. Bigger means the model relies on it more. One label step is 0.5. " + PCT_NOTE + "",
         "- **Spread** = how much the importance varies over 5 different random scrambles; small means the number is stable.",
         "- **Direction** = the rank correlation of the feature with the label on the training texts: **harder** means a higher value goes with a harder text, **easier** the opposite.",
         "- Features that carry the same information share their importance, so a single feature can look small even if its topic matters. The group table avoids this.",
         "- This shows what the model uses, not what causes difficulty. In this data the labels follow word and sentence length closely, so those measures rank high.", "",
         "## Permutation importance by group of features", ""]
    L += md_table(["group", "features", "importance (average miss grows by)", "spread over 5 scrambles"], [[g, n, f"{m:.3f}", f"±{s:.3f}"] for g, n, m, s in group_rows])
    L += ["", f"## Permutation importance of the {TOP} most important single features", ""]
    rows = [[f"`{n}`", group_of.get(n, ""), meaning(n), f"{m:.4f}", f"±{s:.4f}", ("harder" if r > 0.05 else "easier" if r < -0.05 else "unclear") + f" ({r:+.2f})"] for n, m, s, r in single[:TOP]]
    L += md_table(["feature", "group", "meaning", "importance", "spread", "direction (rank correlation)"], rows)
    for kind, prefix, n_all in (("grammar concepts", "grammar_concept_cov_", 268),):
        sub = [r for r in single if r[0].startswith(prefix)]
        fmt = lambda rows: md_table(["rank", "item", "importance (average miss grows by)", "spread", "direction (rank correlation)"],  # noqa: E731
                                    [[i, f"`{n[len(prefix):]}`", f"{m:.4f}", f"±{sd:.4f}", ("harder" if r > 0.05 else "easier" if r < -0.05 else "unclear") + f" ({r:+.2f})"]
                                     for i, (n, m, sd, r) in rows])
        L += ["", f"## Permutation importance of the {kind} ({len(sub)} items, each scrambled on its own)", "", f"The {TOP} most important:", ""]
        L += fmt(list(enumerate(sub[:TOP], 1)))
        L += ["", f"<details><summary>all {len(sub)} {kind}, ranked</summary>", ""] + fmt(list(enumerate(sub, 1))) + ["", "</details>"]
    L += vocab_bin_section()
    L += ["", "## Reproduce", "", "```", "python curated_features/modeling/run_feature_importance.py", "```", ""]
    REPORT.write_text("\n".join(L), encoding="utf-8")
    print("report ->", REPORT)


if __name__ == "__main__":
    main()
