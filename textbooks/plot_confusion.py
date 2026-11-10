"""Heatmaps of the textbook scoring (data/textbooks/predictions_<set>.csv, written by score_textbooks.py).

Rows: the SM book, labelled with its estimated label range (SM1 1.0 to 1.5, SM2 1.5 to 2.0, SM3 2.5 to 3.0, SM4 3.0 to 4.0). Columns: the level the model
predicted, rounded to the nearest 0.5. Cell: number of texts. The title gives the share of texts predicted inside the range of their book.
One figure per text set in reports/textbook_evaluation/graphs/.

    python textbooks/plot_confusion.py
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "textbooks"
OUT = ROOT / "reports" / "textbook_evaluation" / "graphs"
RANGES = {"sm1": (1.0, 1.5), "sm2": (1.5, 2.0), "sm3": (2.5, 3.0), "sm4": (3.0, 4.0)}  # estimated label range of each book
MODELS = {
    "bert-base-finnish-cased-v1 frozen, layer 5 + gradient boosting": "BERT frozen, layer 5",
    "bert-base-finnish-cased-v1 LoRA + linear head (0.3M trained)": "BERT LoRA fine-tuned",
    "bert-base-finnish-cased-v1 full + linear head (124.5M trained)": "BERT full fine-tuned",
    "concept individual share (268)": "concept individual share (268)",
    "vocabulary (bins + lexical) + concept individual share": "vocabulary (bins + lexical) + concept individual share",
    "vocabulary + concept individual share + surface": "vocabulary + concept individual share + surface",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    books = list(RANGES)
    for name in ["paragraph", "dialogue"]:
        p = pd.read_csv(DATA / f"predictions_{name}.csv")
        row = p["book"].map({b: i for i, b in enumerate(books)}).to_numpy()
        lo_r = np.array([RANGES[b][0] for b in p["book"]])
        hi_r = np.array([RANGES[b][1] for b in p["book"]])
        preds = {m: np.round(p[m].to_numpy() * 2) / 2 for m in MODELS}
        lo, hi = 1.0, 6.0  # the whole label scale, the same in every panel
        classes = np.arange(lo, hi + 0.25, 0.5)
        vmax = 1
        mats, inside = {}, {}
        for m, v in preds.items():
            M = np.zeros((len(books), len(classes)), dtype=int)
            for r, q in zip(row, v):
                M[r, int(round((q - lo) * 2))] += 1
            mats[m] = M
            vmax = max(vmax, M.max())
            inside[m] = float(((p[m].to_numpy() >= lo_r) & (p[m].to_numpy() <= hi_r)).mean())
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        for ax, (m, M) in zip(axes.ravel(), mats.items()):
            ax.imshow(M, cmap="Blues", vmin=0, vmax=vmax, origin="lower", aspect="auto")
            for i in range(M.shape[0]):
                for j in range(M.shape[1]):
                    if M[i, j]:
                        ax.text(j, i, M[i, j], ha="center", va="center", fontsize=9, color="white" if M[i, j] > vmax * 0.6 else "black")
            ax.set_xticks(range(len(classes)), [f"{c:g}" for c in classes], fontsize=7)
            ax.set_yticks(range(len(books)), [f"{b.upper()} ({RANGES[b][0]:g} to {RANGES[b][1]:g})" for b in books], fontsize=8)
            ax.set_xlabel("predicted level (rounded to 0.5)", fontsize=8)
            ax.set_ylabel("SM book (estimated label range)", fontsize=8)
            ax.set_title(f"{MODELS[m]}\npredicted inside the book's range: {inside[m]:.0%}", fontsize=9)
        fig.suptitle(f"Textbook {name} texts ({len(p)}): SM book against predicted level (counts of texts)", fontsize=11, x=0.02, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        fig.savefig(OUT / f"confusion_{name}.png", dpi=110)
        plt.close(fig)
        print(name, "done")


if __name__ == "__main__":
    main()
