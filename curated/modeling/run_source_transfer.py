"""Source-transfer check: can the features grade texts from a source the model has never seen?

In the real-Finnish data four of the five sources have one label for all their texts (easy_text 1.5, yle-selkouutiset 3.5, yle and HS 5.5),
so a model can score well by recognising the source. Here each of those four sources is excluded from training in turn. For an excluded source S the
model is trained on the real-Finnish train texts of the other sources (FI included) and graded twice:

  test set   the original test set, as in RESULTS.md (all real-Finnish test texts; it includes S's own test texts, which the model never saw)
  excl. set  all texts of the excluded source S, which the model has never seen: the detail

Gradient boosting. A first row, "none", is the normal model with nothing excluded, so it reproduces the main experiment.

    python curated/modeling/run_source_transfer.py        writes curated/modeling/reports/SOURCE_TRANSFER.md
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from core.evaluate import bootstrap_mae, ci, round_to_step  # noqa: E402
from curated.modeling.feature_sets import FEATURE_SETS, LABELS  # noqa: E402
from curated.utils.feature_store import feature_table  # noqa: E402

BEST = "vocab_grammar_coverage_cognitive"
REFERENCES = ["original_all", "surface"]
NOT_A_FOLD = ("FI",)  # kept in training and in the test set, but never the held-out source (FI has varied labels and may be translated text)
REPORT = Path(__file__).resolve().parent / "reports" / "SOURCE_TRANSFER.md"
SUMMARY = "@@summary@@"


def pooled(set_name):
    """Features and metadata (label, source, split) of all real-Finnish texts."""
    parts = [(split, *feature_table(split, FEATURE_SETS[set_name])) for split in ("train", "valid", "test")]
    cols = list(parts[0][1].columns)
    X = pd.concat([x.reindex(columns=cols, fill_value=0.0) for _, x, _ in parts], ignore_index=True)
    meta = pd.concat([d[["label", "source", "origine"]].assign(split=split) for split, _, d in parts], ignore_index=True)
    keep = (meta["origine"] == "Real").to_numpy()
    return X[keep].reset_index(drop=True), meta[keep].reset_index(drop=True)


def fit(X, meta, train):
    model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)
    return model.fit(X[train].to_numpy(), meta["label"][train])


def scores(y, pred):
    return {"mae": float(np.abs(pred - y).mean()), "exact": float((round_to_step(pred) == y).mean()), "near": float((np.abs(pred - y) <= 0.5).mean())}


def run(set_name):
    """For 'none' and for every excluded source: predictions on the original test set and on the excluded source."""
    X, meta = pooled(set_name)
    is_test, is_train = (meta["split"] == "test").to_numpy(), (meta["split"] == "train").to_numpy()
    y = meta["label"].to_numpy()
    out = {"none": {"test": (y[is_test], fit(X, meta, is_train).predict(X[is_test].to_numpy())), "excl": None, "n_excl": 0}}
    for s in sorted(set(meta["source"]) - set(NOT_A_FOLD)):
        is_s = (meta["source"] == s).to_numpy()
        model = fit(X, meta, is_train & ~is_s)
        out[s] = {"test": (y[is_test], model.predict(X[is_test].to_numpy())), "excl": (y[is_s], model.predict(X[is_s].to_numpy())), "n_excl": int(is_s.sum())}
    return out, X.shape[1], meta


def pct(x):
    return f"{100 * x:.0f}%"


def main():
    warnings.filterwarnings("ignore")
    sets = [BEST] + REFERENCES
    runs, n_feat = {}, {}
    for name in sets:
        runs[name], n_feat[name], meta = run(name)
        print(name, "done", flush=True)
    folds = [s for s in meta["source"].value_counts().index if s not in NOT_A_FOLD]
    best = runs[BEST]

    def excl_pooled(res):
        y = np.concatenate([res[s]["excl"][0] for s in folds])
        p = np.concatenate([res[s]["excl"][1] for s in folds])
        return y, p, scores(y, p)

    yt, pt = best["none"]["test"]
    sn = scores(yt, pt)
    fold_test = [scores(*best[s]["test"])["mae"] for s in folds]
    ey, ep, es = excl_pooled(best)
    ly, lp, ls = excl_pooled(runs["surface"])
    diff = bootstrap_mae(ey, ep) - bootstrap_mae(ly, lp)
    lo, hi = ci(diff)
    outcome = "no clear difference" if lo <= 0 <= hi else ("best set better" if hi < 0 else "surface baseline better")
    summary = "\n".join([
        f"- Original test set: the normal model misses by **{sn['mae']:.3f}**. With one source left out of training: {min(fold_test):.3f} to {max(fold_test):.3f}.",
        f"- On the left-out source itself: **{es['mae']:.3f}** (surface baseline: {ls['mae']:.3f}, {outcome}).",
        "- `yle` and `HS` are graded well, since they share a label (5.5). `easy_text` and `yle-selkouutiset` are graded badly, since no other source has their label.", ""])

    L = ["# Source-transfer check: grading a source the model has never seen", "",
         "Generated by `curated/modeling/run_source_transfer.py`. Separate from `RESULTS.md`.", "", "## Summary", "", summary,
         "## What this tests", "",
         "Four of the five real-Finnish sources have one fixed label each, so a model can score well just by recognising the source. "
         "Here each of those four sources is left out of training in turn.", "",
         f"- **Feature set**: {LABELS[BEST]} ({n_feat[BEST]} features), gradient boosting, trained as in `RESULTS.md` but without the left-out source.",
         "- **Test set**: the original 865 test texts, as in `RESULTS.md`.",
         "- **Excl. set**: all texts of the left-out source. This is the detail.",
         "- `FI` stays in training and in the test set; it is never left out.",
         "- **MAE**: average miss, smaller is better (one label step is 0.5). **Exactly acc**: share of predictions exactly right. **Within 0.5 acc**: share off by at most 0.5.", "",
         "## Result for the best feature set", "",
         "| excl. source | excl. count | test MAE | test exactly acc | test within 0.5 acc | excl. MAE | excl. exactly acc | excl. within 0.5 acc |",
         "|---|---:|---:|---:|---:|---:|---:|---:|",
         f"| none (normal model) | 0 | {sn['mae']:.3f} | {pct(sn['exact'])} | {pct(sn['near'])} | | | |"]
    for s in folds:
        t, e = scores(*best[s]["test"]), scores(*best[s]["excl"])
        L.append(f"| {s} | {best[s]['n_excl']} | {t['mae']:.3f} | {pct(t['exact'])} | {pct(t['near'])} | {e['mae']:.3f} | {pct(e['exact'])} | {pct(e['near'])} |")
    L.append(f"| **all {len(folds)}, pooled** | {len(ey)} | | | | **{es['mae']:.3f}** | {pct(es['exact'])} | {pct(es['near'])} |")

    L += ["", "## The same for two reference feature sets", "",
          "| feature set | test MAE (none excluded) | " + " | ".join(f"excl. MAE: {s}" for s in folds) + " | excl. MAE (pooled) |", "|---|---:|" + "---:|" * (len(folds) + 1)]
    for name in sets:
        r = runs[name]
        L.append(f"| **{LABELS[name]}** | {scores(*r['none']['test'])['mae']:.3f} | " + " | ".join(f"{scores(*r[s]['excl'])['mae']:.3f}" for s in folds)
                 + f" | {excl_pooled(r)[2]['mae']:.3f} |")

    L += ["", "## How to read it", "",
          "- **Test vs excl.**: the test-set columns are the normal evaluation, so they stay comparable with `RESULTS.md`. The excl. columns show how the model does on a source it has never seen; "
          "the gap between the two is the cost of a new source.",
          "- **A source can only be graded as well as the labels the model has seen.** The other sources never have label 1.5 or 3.5, and 5.5 appears only in `yle` and `HS`. "
          "So excluding `easy_text` (1.5) or `yle-selkouutiset` (3.5) asks the model for a label it has never been trained on; a large miss there is expected.",
          "- **`yle` and `HS` share the label 5.5**, so excluding one still leaves the other in training. Those two rows are the easiest and prove the least.", ""]
    REPORT.write_text("\n".join(L), encoding="utf-8")
    print("report ->", REPORT)


if __name__ == "__main__":
    main()
