"""Vocabulary bins of the Suomen mestari paragraph texts against the real-Finnish train and test texts of the same level.

One markdown file per binning method in reports/textbook_evaluation/vocab_eda/ (lemma and stem bins use the same method):
  decades_bin_eda.md     one bin per factor of 10 in frequency
  equal_freq_eda.md      every bin holds 10% of all occurrences
  equal_count_eda.md     every bin holds the same number of distinct words
Each has images/<name>_sm_only.png (the four SM books) and images/<name>_levels.png (each SM book against the train and test texts of the corresponding level;
our training labels start at A2 = 1.5 to 2, so SM1 has no A1 reference) in the images folder. A line is the mean share of the words of a text in each bin
(bin 1 = most frequent).

    python textbooks/vocab_bins_eda.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core.dataset import load_split, native_mask  # noqa: E402
from curated_features.utils import registry  # noqa: E402
from curated_features.utils.feature_store import feature_table  # noqa: E402
from score_textbooks import DATA, ROOT, Blocks  # noqa: E402

OUT = ROOT / "reports" / "textbook_evaluation" / "vocab_eda"
METHODS = {  # folder -> (bin method, readable name)
    "decades_bin_eda": ("log10_freq_bin", "decades (one bin per factor of 10 in frequency)"),
    "equal_freq_eda": ("uniform_cumfreq_bin", "equal frequency (every bin holds 10% of all occurrences)"),
    "equal_count_eda": ("uniform_rank_bin", "equal count (every bin holds the same number of distinct words)"),
}
LEVELS = {"A2 (1.5-2)": (1.5, 2.0), "B1 (3-3.5)": (3.0, 3.5), "B2 (4)": (4.0, 4.0)}
PAIRS = [("sm1", "A2 (1.5-2)"), ("sm2", "A2 (1.5-2)"), ("sm3", "A2 (1.5-2)"), ("sm3", "B1 (3-3.5)"), ("sm4", "B1 (3-3.5)"), ("sm4", "B2 (4)")]
SM_COLORS = {"sm1": "tab:blue", "sm2": "tab:cyan", "sm3": "tab:orange", "sm4": "tab:red"}


def bin_columns(frame, level):
    cols = [c for c in frame.columns if c.startswith(f"{level}_bag_") and c.endswith("_coverage")]
    return sorted(cols, key=lambda c: int(c.split("_")[2]))


def draw(ax, x, values, color, label):
    ax.plot(x, values.mean(axis=0), color=color, linewidth=1.0, alpha=0.65, marker="o", markersize=2, label=label)


def main():
    warnings.filterwarnings("ignore")
    tr, te = load_split("train"), load_split("test")
    rows = native_mask(tr)
    keep_te = np.flatnonzero(native_mask(te))
    y_tr, y_te = tr["label"].to_numpy()[rows], te["label"].to_numpy()[keep_te]
    books = pd.read_csv(DATA / "paragraph_texts.csv")
    blocks = Blocks(books["text"].astype(str), books["id"].tolist(), tr, rows)
    book = books["book"].to_numpy()
    counts = "; ".join(f"{n}: train {int(((y_tr >= lo) & (y_tr <= hi)).sum())}, test {int(((y_te >= lo) & (y_te <= hi)).sum())}" for n, (lo, hi) in LEVELS.items())

    for folder, (method, readable) in METHODS.items():
        (OUT / "images").mkdir(parents=True, exist_ok=True)
        settings = {"lemma_bin_method": method, "stem_bin_method": method}
        spec = {"signals": [("vocab", "freq", settings)]}
        train = feature_table("train", spec)[0].iloc[np.flatnonzero(rows)].reset_index(drop=True)
        test = feature_table("test", spec)[0].iloc[keep_te].reset_index(drop=True)
        sm = registry.make("vocab", "freq", **settings).build(blocks.analysis).reset_index(drop=True)
        short = readable.split(" (")[0]
        units = [("lemma", f"Lemma bins, {short}"), ("stem", f"Stem bins, {short}")]

        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for ax, (unit, title) in zip(axes, units):
            cols = bin_columns(train, unit)
            x = np.arange(1, len(cols) + 1)
            for b, color in SM_COLORS.items():
                draw(ax, x, sm[cols][book == b].to_numpy(), color, b.upper())
            ax.set_xticks(x)
            ax.set_xlabel("bin (1 = most frequent words)")
            ax.set_ylabel("mean share of the words of a text")
            ax.set_title(title, fontsize=10, loc="left")
            ax.legend(fontsize=7, frameon=False)
        fig.tight_layout()
        fig.savefig(OUT / "images" / f"{folder}_sm_only.png", dpi=120)
        plt.close(fig)

        fig, axes = plt.subplots(len(PAIRS), 2, figsize=(10, 2.3 * len(PAIRS)), squeeze=False)
        for i, (b, level) in enumerate(PAIRS):
            lo, hi = LEVELS[level]
            for j, (unit, title) in enumerate(units):
                cols = bin_columns(train, unit)
                x = np.arange(1, len(cols) + 1)
                ax = axes[i, j]
                draw(ax, x, train[cols][(y_tr >= lo) & (y_tr <= hi)].to_numpy(), "0.35", f"train {level}")
                draw(ax, x, test[cols][(y_te >= lo) & (y_te <= hi)].to_numpy(), "tab:orange", f"test {level}")
                draw(ax, x, sm[cols][book == b].to_numpy(), "tab:blue", b.upper())
                ax.set_xticks(x)
                ax.tick_params(labelsize=7)
                ax.set_title(f"{unit.capitalize()} bins: {b.upper()} vs {level}", fontsize=8, loc="left")
                ax.legend(fontsize=6, loc="upper right", frameon=False)
        fig.tight_layout()
        fig.savefig(OUT / "images" / f"{folder}_levels.png", dpi=110)
        plt.close(fig)

        md = [f"# Vocabulary bins of the SM books: {readable}", "",
              "Mean share of a text's words in each frequency bin (bin 1 = most frequent); lemma and stem bins use the same method.", "",
              "## SM books only", "", f"![SM books only](images/{folder}_sm_only.png)", "",
              "## Each SM book against the train and test texts of the corresponding level", "",
              "Six comparisons from the three training levels that the books can match (our labels start at A2, so SM1 has no A1 reference; C1 and C2 have no SM counterpart). "
              f"Real-Finnish texts per level, {counts}; SM paragraph texts: " + ", ".join(f"{b.upper()} {int((book == b).sum())}" for b in SM_COLORS) + ".", "",
              f"![levels](images/{folder}_levels.png)", ""]
        (OUT / f"{folder}.md").write_text("\n".join(md))
        print(folder, "done", flush=True)


if __name__ == "__main__":
    main()
