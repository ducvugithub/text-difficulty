"""The test-set predictions of every run, in one shared format, so runs of the two ways can be compared in one place.

One file per run: outputs/predictions/<way>__<model>__<name>__<train>.npz, with the test labels, the predictions (in test-split order) and the run's identity.
  way     curated | bert                  model  gbm | ridge | finetune          name  the feature set, or the BERT layer
  train   train_native | train_all

    from core import predictions
    predictions.save("curated", "gbm", "vocab_grammar_coverage_cognitive", "train_native", y_test, pred)
    for run in predictions.load_all(): print(run["way"], run["name"], run["mae"])
"""
import json
from pathlib import Path

import numpy as np

DIR = Path(__file__).resolve().parents[1] / "outputs" / "predictions"


def save(way: str, model: str, name: str, train: str, label, pred) -> Path:
    label, pred = np.asarray(label, float), np.asarray(pred, float)
    if label.shape != pred.shape:
        raise ValueError("label and pred must have the same length")
    DIR.mkdir(parents=True, exist_ok=True)
    path = DIR / f"{way}__{model}__{name}__{train}.npz"
    np.savez(path, label=label, pred=pred, meta=json.dumps({"way": way, "model": model, "name": name, "train": train}))
    return path


def load_all() -> list[dict]:
    """Every saved run: {way, model, name, train, label, pred, mae}."""
    runs = []
    for path in sorted(DIR.glob("*.npz")):
        with np.load(path) as f:
            run = {**json.loads(str(f["meta"])), "label": f["label"], "pred": f["pred"]}
        run["mae"] = float(np.abs(run["pred"] - run["label"]).mean())
        runs.append(run)
    return runs
