"""Run one experiment: train on one split, evaluate on the others, for several feature sets and models.

  python run_experiment.py --train train_native          # train on the real-Finnish rows of train
  python run_experiment.py --train train_all             # train on all train rows (72% translated)

Evaluation sets: test (all real Finnish) and valid (native rows only). Writes curated_features/modeling/reports/runs/{train}_{tag}.md with,
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from core import predictions  # noqa: E402
from core.dataset import native_mask, train_mask  # noqa: E402
from core.evaluate import CLASSES, bootstrap_mae, ci, confusion_counts, metrics  # noqa: E402
from curated_features.modeling.feature_sets import DESCRIPTIONS, EXPERIMENT_SETS, aligned_tables  # noqa: E402

REPORTS = Path(__file__).resolve().parent / "reports"
MODELS = {
    "ridge": ("ridge regression", lambda: make_pipeline(StandardScaler(), Ridge(alpha=100.0))),
    "gbm": ("gradient boosting", lambda: HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)),
}
EVALS = ("test", "valid (native)")
# the comparisons of interest: does a category beat the length control, does one add to the other, which grammar variant is better
PAIRS = [("vocab", "surface"), ("grammar_coverage", "surface"), ("cognitive", "surface"), ("grammar_coverage", "grammar_manual"),
         ("grammar_coverage", "grammar_rarity"), ("grammar_all", "grammar_coverage"), ("vocab_grammar_coverage", "vocab"),
         ("vocab_grammar_coverage", "original_all"), ("vocab_grammar_coverage_cognitive", "vocab_grammar_coverage"),
         ("vocab_grammar_coverage_cognitive", "original_all"), ("all_new", "vocab_grammar_coverage_cognitive"), ("all_new", "original_all"),
         ("vocab", "original_vocab_bins"), ("original_all", "surface"), ("vocab_grammar_coverage_cognitive", "surface"), ("all_new", "surface")]


def pct(x):
    return f"{100 * x:.1f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", default="train_native", choices=["train_native", "train_all"])
    ap.add_argument("--sets", nargs="*", default=EXPERIMENT_SETS)
    ap.add_argument("--tag", default="", help="suffix of the report name, so a new run does not overwrite an earlier report")
    ap.add_argument("--models", nargs="*", default=list(MODELS))
    args = ap.parse_args()
    warnings.filterwarnings("ignore")

    results, preds, n_cols, n_train, dummies = {}, {}, {}, 0, {}
    for name in args.sets:
        tables = aligned_tables("train", ["valid", "test"], name)
        X_tr, d_tr = tables["train"]
        mask = train_mask(d_tr, args.train)
        n_train, n_cols[name] = int(mask.sum()), X_tr.shape[1]
        valid_native = native_mask(tables["valid"][1])
        evals = {"test": tables["test"], "valid (native)": (tables["valid"][0][valid_native], tables["valid"][1][valid_native])}
        for model_name in args.models:
            model = MODELS[model_name][1]().fit(X_tr[mask].to_numpy(), d_tr["label"][mask])
            for ev, (X, d) in evals.items():
                pred = model.predict(X.to_numpy())
                results[(model_name, name, ev)] = metrics(d["label"], pred)
                results[(model_name, name, ev)]["mae_ci"] = ci(bootstrap_mae(d["label"], pred))
                preds[(model_name, name, ev)] = (d["label"].to_numpy(), pred)
                if ev == "test":
                    predictions.save("curated", model_name, name, args.train, d["label"].to_numpy(), pred)
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
            lines += ["", f"## {ev}: {title}", "", "| feature set | what is in it | columns | MAE | MAE 95% CI | accuracy | accuracy ±1 step | balanced accuracy |", "|---|---|---:|---:|---|---:|---:|---:|"]
            for name in args.sets:
                r = results[(model_name, name, ev)]
                lines.append(f"| {name} | {DESCRIPTIONS[name]} | {n_cols[name]} | {r['mae']:.3f} | [{r['mae_ci'][0]:.3f}, {r['mae_ci'][1]:.3f}] | {pct(r['accuracy'])} | {pct(r['accuracy_1step'])} | {pct(r['balanced_accuracy'])} |")
            for dname, dv in dummies.items():
                b = dv[ev]
                lines.append(f"| dummy | always the {dname} of the training data ({dv['value']:g}) | 0 | {b['mae']:.3f} | | {pct(b['accuracy'])} | {pct(b['accuracy_1step'])} | {pct(b['balanced_accuracy'])} |")
            labels = sorted(r0["per_label"])
            header = "| feature set | " + " | ".join(f"{k:g} (n={r0['per_label'][k]['n']})" for k in labels) + " |"
            sep = "|---|" + "---:|" * len(labels)
            for what, key, fmt in (("MAE per label", "mae", lambda v: f"{v:.2f}"), ("accuracy per label", "accuracy", pct), ("accuracy ±1 step per label", "accuracy_1step", pct)):
                lines += ["", f"### {ev}, {title}: {what}", "", header, sep]
                for name in args.sets:
                    pl = results[(model_name, name, ev)]["per_label"]
                    lines.append(f"| {name} | " + " | ".join(fmt(pl[k][key]) if k in pl else "" for k in labels) + " |")
            if ev == "test":  # confusion matrices: rows = true label, columns = predicted label (rounded to the nearest half step)
                for name in args.sets:
                    true, counts = confusion_counts(*preds[(model_name, name, ev)])
                    lines += ["", f"### test, {title}: confusion matrix: {name}", "", "| true \\ predicted | " + " | ".join(f"{c:g}" for c in CLASSES) + " |", "|---|" + "---:|" * len(CLASSES)]
                    lines += [f"| {t:g} | " + " | ".join(str(v) for v in row) + " |" for t, row in zip(true, counts)]
    pairs = [(a, b) for a, b in PAIRS if a in args.sets and b in args.sets]
    if pairs:
        lines += ["", "## Paired MAE differences (first minus second; negative = the first is better)", "",
                  "Bootstrap over the evaluation texts (1,000 resamples, the same resamples for both models). "
                  "A 95% interval that does not contain 0 is a difference larger than noise.", ""]
        for model_name in args.models:
            for ev in EVALS:
                lines += [f"### {ev}, {MODELS[model_name][0]}", "", "| first | second | difference in MAE | 95% CI |", "|---|---|---:|---|"]
                for a, b in pairs:
                    y, pa = preds[(model_name, a, ev)]
                    diff = bootstrap_mae(y, pa) - bootstrap_mae(y, preds[(model_name, b, ev)][1])
                    lo, hi = ci(diff)
                    lines.append(f"| {a} | {b} | {diff.mean():+.3f} | [{lo:+.3f}, {hi:+.3f}]{'' if lo <= 0 <= hi else ' *'} |")
                lines.append("")
    (REPORTS / "runs").mkdir(parents=True, exist_ok=True)
    out = REPORTS / "runs" / f"{args.train}{'_' + args.tag if args.tag else ''}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report ->", out)


if __name__ == "__main__":
    main()
