"""Metrics for the difficulty experiments (labels 1.0-6.0 in steps of 0.5).

mae                 mean |prediction - label|, in label units (one step = 0.5)
accuracy            share of texts whose prediction, rounded to the nearest half step, equals the label
accuracy_1step      share of texts within one step (|prediction - label| <= 0.5)
balanced_accuracy   mean of the per-label accuracies: every label counts equally, so predicting only the common labels is punished
per_label           for each label: n, mae, accuracy, accuracy_1step
"""
import numpy as np


def round_to_step(pred):
    return np.clip(np.round(np.asarray(pred, float) * 2) / 2, 1.0, 6.0)


CLASSES = np.arange(1.0, 6.01, 0.5)


def confusion_counts(y, pred):
    """(true labels present, counts): rows = true label, columns = the prediction rounded to the nearest half step (1.0 to 6.0)."""
    y, p = np.asarray(y, float), round_to_step(pred)
    labels = np.unique(y)
    return labels, np.array([[int(((y == t) & (p == c)).sum()) for c in CLASSES] for t in labels])


def metrics(y, pred):
    y, pred = np.asarray(y, float), np.asarray(pred, float)
    hit, near = round_to_step(pred) == y, np.abs(pred - y) <= 0.5
    per_label = {k: {"n": int((y == k).sum()), "mae": float(np.abs(pred[y == k] - k).mean()),
                     "accuracy": float(hit[y == k].mean()), "accuracy_1step": float(near[y == k].mean())} for k in np.unique(y)}
    return {"mae": float(np.abs(pred - y).mean()), "accuracy": float(hit.mean()), "accuracy_1step": float(near.mean()),
            "balanced_accuracy": float(np.mean([v["accuracy"] for v in per_label.values()])), "per_label": per_label}


def bootstrap_mae(y, pred, n=1000, seed=0):
    """MAE of `n` bootstrap resamples of the texts. The same seed gives the same resamples, so two models stay paired."""
    y, pred = np.asarray(y, float), np.asarray(pred, float)
    idx = np.random.default_rng(seed).integers(0, len(y), (n, len(y)))
    return np.abs(pred - y)[idx].mean(axis=1)


def ci(values, level=0.95):
    lo, hi = np.percentile(values, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(lo), float(hi)
