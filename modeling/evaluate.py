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


def metrics(y, pred):
    y, pred = np.asarray(y, float), np.asarray(pred, float)
    hit, near = round_to_step(pred) == y, np.abs(pred - y) <= 0.5
    per_label = {k: {"n": int((y == k).sum()), "mae": float(np.abs(pred[y == k] - k).mean()),
                     "accuracy": float(hit[y == k].mean()), "accuracy_1step": float(near[y == k].mean())} for k in np.unique(y)}
    return {"mae": float(np.abs(pred - y).mean()), "accuracy": float(hit.mean()), "accuracy_1step": float(near.mean()),
            "balanced_accuracy": float(np.mean([v["accuracy"] for v in per_label.values()])), "per_label": per_label}
