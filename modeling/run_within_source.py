"""Shortcut check: how much of a feature set's test accuracy is just recognising the source?

In the real-Finnish rows the label is constant within four of the five sources (easy_text 1.5, yle-selkouutiset 3.5, yle and HS 5.5);
only FI has varied labels (1-6). A model that recognises the source therefore gets most texts right without measuring difficulty.
This script reports, for the experiment's feature sets (gradient boosting):

  1. the source structure of the test set
  2. a diagnostic model that sees only the source (not a feature set: it shows what source recognition alone achieves)
  3. test MAE per source, trained on the real-Finnish train rows
  4. FI only, where the source cannot explain the label: test MAE with a bootstrap 95% CI, accuracy and Spearman rho, trained
     (a) on the FI train rows only and (b) on all real-Finnish train rows; both against a constant dummy (the FI median label)

    python modeling/run_within_source.py            writes modeling/reports/runs/within_source.md
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root
from modeling.evaluate import bootstrap_mae, ci, metrics  # noqa: E402
from modeling.feature_sets import DESCRIPTIONS, EXPERIMENT_SETS, aligned_tables  # noqa: E402

SETS = EXPERIMENT_SETS
REPORT = Path(__file__).resolve().parent / "reports" / "runs" / "within_source.md"


def gbm():
    return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)


def pct(x):
    return f"{100 * x:.1f}%"


def main():
    warnings.filterwarnings("ignore")
    tables = {name: aligned_tables("train", ["test"], name) for name in SETS}
    d_tr, d_te = tables[SETS[0]]["train"][1], tables[SETS[0]]["test"][1]
    native = (d_tr["origine"] == "Real").to_numpy()
    fi_tr, fi_te = (d_tr["source"] == "FI").to_numpy() & native, (d_te["source"] == "FI").to_numpy()
    y_tr, y_te = d_tr["label"].to_numpy(), d_te["label"].to_numpy()
    sources = d_te["source"].value_counts().index.tolist()
    lines = ["# Shortcut check: within a single source", "",
             "In the real-Finnish rows the label is constant within four of the five sources; only FI varies. "
             "Gradient boosting throughout; test = the 865 real-Finnish texts.", "",
             "## 1. Source structure of the test set", "", "| source | texts | labels |", "|---|---:|---|"]
    for s in sources:
        lab = sorted(d_te.loc[d_te["source"] == s, "label"].unique())
        lines.append(f"| {s} | {int((d_te['source'] == s).sum())} | {lab[0]:g}" + (" (constant)" if len(lab) == 1 else f" to {lab[-1]:g}, {len(lab)} values") + " |")

    onehot = pd.get_dummies(pd.concat([d_tr["source"], d_te["source"]]), dtype=float)
    X_src_tr, X_src_te = onehot.iloc[:len(d_tr)].to_numpy(), onehot.iloc[len(d_tr):].to_numpy()
    src_pred = gbm().fit(X_src_tr[native], y_tr[native]).predict(X_src_te)
    m = metrics(y_te, src_pred)
    lines += ["", "## 2. A model that sees only the source (diagnostic, never a feature set)", "",
              f"Trained on the real-Finnish train rows, tested on all test texts: MAE {m['mae']:.3f} [{ci(bootstrap_mae(y_te, src_pred))[0]:.3f}, "
              f"{ci(bootstrap_mae(y_te, src_pred))[1]:.3f}], accuracy {pct(m['accuracy'])}, within one step {pct(m['accuracy_1step'])}. "
              "This is what recognising the source alone achieves; a feature set near it is mostly recognising the source.", ""]
    mf = metrics(y_te[fi_te], src_pred[fi_te])
    lines.append(f"On the FI texts alone the source-only model has MAE {mf['mae']:.3f}: it cannot separate FI labels.")

    preds_all = {}
    for name in SETS:
        X_tr, X_te = tables[name]["train"][0].to_numpy(), tables[name]["test"][0].to_numpy()
        preds_all[name] = gbm().fit(X_tr[native], y_tr[native]).predict(X_te)
    lines += ["", "## 3. Test MAE per source (trained on the real-Finnish train rows)", "",
              "| feature set | all | " + " | ".join(f"{s} (n={int((d_te['source'] == s).sum())})" for s in sources) + " |", "|---|---:|" + "---:|" * len(sources)]
    lines.append("| source only | " + f"{np.abs(src_pred - y_te).mean():.3f} | " + " | ".join(f"{np.abs(src_pred[(d_te['source'] == s).to_numpy()] - y_te[(d_te['source'] == s).to_numpy()]).mean():.3f}" for s in sources) + " |")
    for name in SETS:
        p = preds_all[name]
        lines.append(f"| {name} | {np.abs(p - y_te).mean():.3f} | " + " | ".join(f"{np.abs(p[(d_te['source'] == s).to_numpy()] - y_te[(d_te['source'] == s).to_numpy()]).mean():.3f}" for s in sources) + " |")

    lines += ["", "## 4. FI only: the source cannot explain the label", "",
              f"FI test texts: {int(fi_te.sum())}, labels {[float(v) for v in sorted(set(y_te[fi_te]))]}. The dummy always predicts the FI train median "
              f"({np.median(y_tr[fi_tr]):g}). rho = Spearman correlation of prediction and label.", ""]
    for title, mask in (("(a) trained on the FI train rows only (n=%d)" % fi_tr.sum(), fi_tr), ("(b) trained on all real-Finnish train rows (n=%d)" % native.sum(), native)):
        lines += [f"### {title}", "", "| feature set | MAE | MAE 95% CI | accuracy | within one step | rho |", "|---|---:|---|---:|---:|---:|"]
        dummy = np.full(fi_te.sum(), np.median(y_tr[fi_tr]))
        md = metrics(y_te[fi_te], dummy)
        lines.append(f"| dummy (median) | {md['mae']:.3f} | [{ci(bootstrap_mae(y_te[fi_te], dummy))[0]:.3f}, {ci(bootstrap_mae(y_te[fi_te], dummy))[1]:.3f}] | {pct(md['accuracy'])} | {pct(md['accuracy_1step'])} | |")
        for name in SETS:
            p = gbm().fit(tables[name]["train"][0].to_numpy()[mask], y_tr[mask]).predict(tables[name]["test"][0].to_numpy()[fi_te])
            mm = metrics(y_te[fi_te], p); lo, hi = ci(bootstrap_mae(y_te[fi_te], p))
            lines.append(f"| {name} | {mm['mae']:.3f} | [{lo:.3f}, {hi:.3f}] | {pct(mm['accuracy'])} | {pct(mm['accuracy_1step'])} | {spearmanr(p, y_te[fi_te]).statistic:+.2f} |")
        lines.append("")
    lines += ["## Feature sets", ""] + [f"- `{n}`: {DESCRIPTIONS[n]}" for n in SETS]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report ->", REPORT)


if __name__ == "__main__":
    main()
