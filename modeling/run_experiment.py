"""Run one experiment: train on one split, evaluate on the others, for several feature sets and models.

  python run_experiment.py --train train_native          # train on the real-Finnish rows of train
  python run_experiment.py --train train_all             # train on all train rows (72% translated)

Evaluation sets: test (all real Finnish) and valid (native rows only). Writes modeling/reports/experiment_{train}.md with,
per model: an overall table (MAE, accuracy, accuracy within one step, balanced accuracy) and per-label MAE and accuracy
tables, so a bias towards the common labels shows. Source and origin are never features.
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import metrics  # noqa: E402
from feature_sets import DESCRIPTIONS, FEATURE_SETS, aligned_tables  # noqa: E402

REPORTS = Path(__file__).resolve().parent / "reports"
MODELS = {
    "ridge": ("ridge regression", lambda: make_pipeline(StandardScaler(), Ridge(alpha=100.0))),
    "gbm": ("gradient boosting", lambda: HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)),
}
EVALS = ("test", "valid (native)")


def pct(x):
    return f"{100 * x:.1f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", default="train_native", choices=["train_native", "train_all"])
    ap.add_argument("--sets", nargs="*", default=FEATURE_SETS)
    ap.add_argument("--models", nargs="*", default=list(MODELS))
    args = ap.parse_args()
    warnings.filterwarnings("ignore")

    results, n_cols, n_train, dummies = {}, {}, 0, {}
    for name in args.sets:
        tables = aligned_tables("train", ["valid", "test"], name)
        X_tr, d_tr = tables["train"]
        mask = (d_tr["origine"] == "Real").to_numpy() if args.train == "train_native" else np.ones(len(d_tr), bool)
        n_train, n_cols[name] = int(mask.sum()), X_tr.shape[1]
        valid_native = (tables["valid"][1]["origine"] == "Real").to_numpy()
        evals = {"test": tables["test"], "valid (native)": (tables["valid"][0][valid_native], tables["valid"][1][valid_native])}
        for model_name in args.models:
            model = MODELS[model_name][1]().fit(X_tr[mask].to_numpy(), d_tr["label"][mask])
            for ev, (X, d) in evals.items():
                results[(model_name, name, ev)] = metrics(d["label"], model.predict(X.to_numpy()))
            r = results[(model_name, name, "test")]
            print(name, model_name, f"test MAE {r['mae']:.3f} acc {r['accuracy']:.3f}", flush=True)
        if not dummies:  # dummy models: one constant prediction, taken from the training labels
            labels_train = d_tr["label"][mask]
            for dname, value in (("most common label", labels_train.mode().iloc[0]), ("median label", labels_train.median())):
                dummies[dname] = {"value": value, **{ev: metrics(d["label"], np.full(len(d), value)) for ev, (X, d) in evals.items()}}

    lines = [f"# Experiment: train on {args.train} ({n_train:,} rows)", "",
             "- Source and origin are not features. Test = real Finnish only; valid (native) = the real-Finnish rows of valid.",
             "- **MAE**: mean absolute error in label units (the labels run from 1.0 to 6.0 in steps of 0.5, one step = 0.5)",
             "- **accuracy**: share of texts whose prediction, rounded to the nearest half step, is exactly the label",
             "- **accuracy ±1 step**: share within 0.5 of the label",
             "- **balanced accuracy**: mean of the per-label accuracies; every label counts equally, so favouring the common labels is punished",
             "- dummy models predict one constant for every text, taken from the training labels: " + "; ".join(f"{k} ({v['value']:g})" for k, v in dummies.items()),
             "  They are the floor: a real model has to beat them"]
    for model_name in args.models:
        title = MODELS[model_name][0]
        for ev in EVALS:
            r0 = results[(model_name, args.sets[0], ev)]
            lines += ["", f"## {ev}: {title}", "", "| feature set | what is in it | columns | MAE | accuracy | accuracy ±1 step | balanced accuracy |", "|---|---|---:|---:|---:|---:|---:|"]
            for name in args.sets:
                r = results[(model_name, name, ev)]
                lines.append(f"| {name} | {DESCRIPTIONS[name]} | {n_cols[name]} | {r['mae']:.3f} | {pct(r['accuracy'])} | {pct(r['accuracy_1step'])} | {pct(r['balanced_accuracy'])} |")
            for dname, dv in dummies.items():
                b = dv[ev]
                lines.append(f"| dummy | always the {dname} of the training data ({dv['value']:g}) | 0 | {b['mae']:.3f} | {pct(b['accuracy'])} | {pct(b['accuracy_1step'])} | {pct(b['balanced_accuracy'])} |")
            labels = sorted(r0["per_label"])
            header = "| feature set | " + " | ".join(f"{k:g} (n={r0['per_label'][k]['n']})" for k in labels) + " |"
            sep = "|---|" + "---:|" * len(labels)
            for what, key, fmt in (("MAE per label", "mae", lambda v: f"{v:.2f}"), ("accuracy per label", "accuracy", pct), ("accuracy ±1 step per label", "accuracy_1step", pct)):
                lines += ["", f"### {ev}, {title}: {what}", "", header, sep]
                for name in args.sets:
                    pl = results[(model_name, name, ev)]["per_label"]
                    lines.append(f"| {name} | " + " | ".join(fmt(pl[k][key]) if k in pl else "" for k in labels) + " |")
    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"experiment_{args.train}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report ->", out)


if __name__ == "__main__":
    main()
