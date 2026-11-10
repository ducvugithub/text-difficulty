"""Grammar concepts of the Suomen mestari paragraph texts against the real-Finnish train and test texts of the same level.

One markdown file per feature set in reports/textbook_evaluation/grammar_eda/, each with images/<name>_sm_only.png and images/<name>_levels.png
(each SM book against the train and test texts of the corresponding level; our training labels start at A2 = 1.5 to 2, so SM1 has no A1 reference):
  concept_level_share_eda.md        the 8 manual CEFR level shares (lines, like the vocabulary bins)
  concept_rarity_eda.md             the 7 rarity bins and the unseen share (lines)
  concept_individual_share_eda.md   the mean share of each of the 268 concepts, one line per group over the concepts (one line per group over the concepts)

    python textbooks/grammar_eda.py
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
from curated_features.utils.feature_store import feature_table  # noqa: E402
from score_textbooks import DATA, ROOT, SIGNALS, Blocks  # noqa: E402
from vocab_bins_eda import LEVELS, PAIRS, SM_COLORS  # noqa: E402

OUT = ROOT / "reports" / "textbook_evaluation" / "grammar_eda"
LEVEL_ORDER = ["A1", "A1_A2", "A1_B1", "A2", "A2_B1", "B1", "B1_B2", "B2"]


def draw(ax, x, values, color, label):
    ax.plot(x, values.mean(axis=0), color=color, linewidth=1.0, alpha=0.65, marker="o", markersize=2, label=label)


def line_figures(name, title, cols, ticks, train, test, sm, y_tr, y_te, book, md_extra):
    x = np.arange(len(cols))
    fig, ax = plt.subplots(figsize=(7, 4))
    for b, color in SM_COLORS.items():
        draw(ax, x, sm[cols][book == b].to_numpy(), color, b.upper())
    ax.set_xticks(x, ticks, fontsize=7)
    ax.set_ylabel("mean share")
    ax.set_title(title, fontsize=10, loc="left")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "images" / f"{name}_sm_only.png", dpi=120)
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(10, 7), squeeze=False)
    for ax, (b, level) in zip(axes.ravel(), PAIRS):
        lo, hi = LEVELS[level]
        draw(ax, x, train[cols][(y_tr >= lo) & (y_tr <= hi)].to_numpy(), "0.35", f"train {level}")
        draw(ax, x, test[cols][(y_te >= lo) & (y_te <= hi)].to_numpy(), "tab:orange", f"test {level}")
        draw(ax, x, sm[cols][book == b].to_numpy(), "tab:blue", b.upper())
        ax.set_xticks(x, ticks, fontsize=6)
        ax.set_title(f"{b.upper()} vs {level}", fontsize=8, loc="left")
        ax.legend(fontsize=6, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "images" / f"{name}_levels.png", dpi=110)
    plt.close(fig)


def concept_lines(ax, x, series, title):
    for values, color, label in series:
        ax.plot(x, values, color=color, linewidth=0.8, alpha=0.7, label=label)
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.set_xlabel("concepts, from the most to the least common in the train texts", fontsize=7)
    ax.set_ylabel("mean share of a text", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.set_title(title, fontsize=8, loc="left")
    ax.legend(fontsize=6, frameon=False, loc="upper right")


def scatter_figures(name, cols, train, test, sm, y_tr, y_te, book):
    """One line per group over all concepts, ordered by the mean share in the train texts."""
    mean = lambda X, mask: X[cols][mask].to_numpy().mean(axis=0)
    order = np.argsort(-train[cols].to_numpy().mean(axis=0))
    x = np.arange(len(cols))
    fig, ax = plt.subplots(figsize=(10, 4))
    concept_lines(ax, x, [(mean(sm, book == b)[order], color, b.upper()) for b, color in SM_COLORS.items()], "SM books only")
    fig.tight_layout()
    fig.savefig(OUT / "images" / f"{name}_sm_only.png", dpi=120)
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(12, 9), squeeze=False)
    for ax, (b, level) in zip(axes.ravel(), PAIRS):
        lo, hi = LEVELS[level]
        tmask, emask = (y_tr >= lo) & (y_tr <= hi), (y_te >= lo) & (y_te <= hi)
        concept_lines(ax, x, [(mean(train, tmask)[order], "0.35", f"train {level}"), (mean(test, emask)[order], "tab:orange", f"test {level}"),
                              (mean(sm, book == b)[order], "tab:blue", b.upper())], f"{b.upper()} vs {level}")
    fig.tight_layout()
    fig.savefig(OUT / "images" / f"{name}_levels.png", dpi=110)
    plt.close(fig)


def write_md(name, title, intro):
    md = [f"# {title}", "", intro, "",
          "## SM books only", "", f"![SM books only](images/{name}_sm_only.png)", "",
          "## Each SM book against the train and test texts of the corresponding level", "",
          "Six comparisons from the three training levels that the books can match (our labels start at A2, so SM1 has no A1 reference; C1 and C2 have no SM counterpart).", "",
          f"![levels](images/{name}_levels.png)", ""]
    return md


def main():
    warnings.filterwarnings("ignore")
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    tr, te = load_split("train"), load_split("test")
    rows = native_mask(tr)
    keep_te = np.flatnonzero(native_mask(te))
    y_tr, y_te = tr["label"].to_numpy()[rows], te["label"].to_numpy()[keep_te]
    books = pd.read_csv(DATA / "paragraph_texts.csv")
    blocks = Blocks(books["text"].astype(str), books["id"].tolist(), tr, rows)
    book = books["book"].to_numpy()

    def tables(block):
        train = feature_table("train", {"signals": SIGNALS[block]})[0].iloc[np.flatnonzero(rows)].reset_index(drop=True)
        test = feature_table("test", {"signals": SIGNALS[block]})[0].iloc[keep_te].reset_index(drop=True)
        return train, test, blocks.new(block)

    # concept level share
    train, test, sm = tables("g_lev")
    cols = [f"grammar_concept_level_{c}" for c in LEVEL_ORDER]
    cols = [c for c in cols if np.ptp(np.concatenate([train[c], test[c], sm[c]])) > 0]
    line_figures("concept_level_share_eda", "Concept share by manual CEFR level", cols, [c.replace("grammar_concept_level_", "").replace("_", "-") for c in cols], train, test, sm, y_tr, y_te, book, None)
    (OUT / "concept_level_share_eda.md").write_text("\n".join(write_md("concept_level_share_eda", "Grammar concepts by manual CEFR level: the SM books",
        "Mean share of the levelled concept occurrences of a text at each manual CEFR level (Revita's levels; concepts without a level are not counted).")))

    # concept rarity bins
    train, test, sm = tables("g_rar")
    cols = [f"grammar_concept_rarity_bag_{k}" for k in range(1, 8)] + ["grammar_concept_rarity_unseen"]
    line_figures("concept_rarity_eda", "Concept rarity bins", cols, [*map(str, range(1, 8)), "unseen"], train, test, sm, y_tr, y_te, book, None)
    (OUT / "concept_rarity_eda.md").write_text("\n".join(write_md("concept_rarity_eda", "Grammar concept rarity: the SM books",
        "Mean share of a text's concept occurrences in each rarity bin (bin 1 = most common in Revita's 10,221 stories, bin 7 = rarest) and the share of concepts never seen there. The mean IDF is left out because it is on another scale.")))

    # individual concepts
    train, test, sm = tables("g_cov")
    cols = [c for c in train.columns if c.startswith("grammar_concept_cov_")]
    scatter_figures("concept_individual_share_eda", cols, train, test, sm, y_tr, y_te, book)
    md = write_md("concept_individual_share_eda", "Grammar concepts: mean share of each of the 268 concepts, SM books",
                  f"The {len(cols)} concepts on the x axis, ordered from the most to the least common in the train texts (the same order in every plot); the y axis is the mean share of a text's concept occurrences "
                  "(log-like scale, so that the rare concepts are visible). If the lines of two groups lie on top of each other, the two groups use the grammar alike.")
    (OUT / "concept_individual_share_eda.md").write_text("\n".join(md))


if __name__ == "__main__":
    main()
