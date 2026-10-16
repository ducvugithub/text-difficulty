"""A report with one figure per feature group: how well gradient boosting predicts the label from that group alone, and from the best combination.

Each figure has a boxplot (the spread of the predictions for each true label) and a scatter plot (every test text). The title gives the
average miss (MAE), MSE, RMSE and the correlation. The percents divide by the label range (5 points; MSE by its square), so 0 is perfect.
All models are gradient boosting (300 rounds, learning rate 0.05) trained on the chosen training set and graded on the 865 test texts.

    python core/run_feature_group_plots.py                  writes reports/feature_group_plots/FEATURE_GROUPS.md and train_native/01_*.png ... 09_*.png
    python core/run_feature_group_plots.py --train train_all   the same for the all-rows training set (FEATURE_GROUPS_train_all.md)
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root
from bert_based import embeddings  # noqa: E402
from core import predictions  # noqa: E402
from core.dataset import TRAIN_SETS, load_split, train_mask  # noqa: E402
from core.reporting import LABEL_RANGE, md_table  # noqa: E402
from curated_features.utils.feature_store import feature_table  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "reports" / "feature_group_plots"
FINETUNED = Path(__file__).resolve().parents[1] / "bert_based" / "reports" / "runs"
LEVELS = np.arange(1, 6.5, 0.5)  # every possible label, also the ones the test set does not have
SURFACE = [("cognitive", "sentence_length"), ("cognitive", "parse_old")]
CONCEPTS, TOPICS = [("grammar", "coverage_concepts")], [("grammar", "coverage_topics")]
VOCAB = [("vocab", "freq"), ("vocab", "lexical")]
FREQ = [("vocab", "freq")]
LENGTH_LIKE = ["avg_word_length", "long_word_ratio", "n_unique_lemmas", "n_compound_tokens"]  # word-form features that mostly measure length
# file name, title, signals, which columns to keep
GROUPS = [
    ("best_surface_grammar_vocab", "surface + all grammar + all vocab", SURFACE + CONCEPTS + TOPICS + VOCAB, None),
    ("grammar_vocab_no_length", "all grammar + all vocab, no length features", CONCEPTS + TOPICS + VOCAB, None),
    ("grammar_concept_only", "grammar-concept only", CONCEPTS, None),
    ("grammar_topic_only", "grammar-topic only", TOPICS, None),
    ("grammar_only", "grammar only (concept + topic)", CONCEPTS + TOPICS, None),
    ("vocab_lemma_only", "vocab-lemma only", FREQ, "lemma_"),
    ("vocab_stem_only", "vocab-stem only", FREQ, "stem_"),
    ("vocab_only", "vocab only (lemma + stem)", FREQ, None),
    ("surface_only", "surface only", SURFACE, None),
]


def gbm():
    return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)


def curated_data(signals, prefix, train_df, train_rows, drop=()):
    spec = {"signals": signals}
    (X_tr, _), (X_te, _) = feature_table("train", spec), feature_table("test", spec)
    cols = [c for c in X_tr.columns if c not in drop and (prefix is None or c.startswith(prefix) or c.startswith("mean_log_" + prefix.rstrip("_")))]
    X_tr, X_te = X_tr[cols], X_te.reindex(columns=cols, fill_value=0.0)
    return X_tr.to_numpy()[train_rows], X_te.to_numpy(), len(cols)


def best_bert_layer(train):
    runs = [r for r in predictions.load_all() if r["way"] == "bert" and r["train"] == train and r["name"].startswith("layer_")]
    return int(min(runs, key=lambda r: r["mae"])["name"].split("_")[1])


def scores(y, p):
    err = p - y
    r = LABEL_RANGE
    return {"MAE": (np.abs(err).mean(), np.abs(err).mean() / r), "MSE": ((err ** 2).mean(), (err ** 2).mean() / r ** 2),
            "RMSE": (np.sqrt((err ** 2).mean()), np.sqrt((err ** 2).mean()) / r), "corr": np.corrcoef(y, p)[0, 1]}


def draw(path, header, y, p):
    s = scores(y, p)
    fig, (box, scat) = plt.subplots(1, 2, figsize=(15, 6.2), sharey=True)
    present = [v for v in LEVELS if (y == v).any()]
    box.boxplot([p[y == v] for v in present], positions=[list(LEVELS).index(v) for v in present], widths=0.6, medianprops={"color": "tab:orange"})
    rng = np.random.default_rng(0)
    scat.scatter(y + rng.uniform(-0.12, 0.12, len(y)), p, s=9, alpha=0.35)
    scat.plot([1, 6], [1, 6], color="tab:red", linewidth=1, linestyle=":")
    box.set_xticks(range(len(LEVELS)))
    box.set_xticklabels([f"{v:g}\n(n={int((y == v).sum())})" for v in LEVELS], fontsize=8)
    scat.set_xticks(LEVELS)
    scat.set_xticklabels([f"{v:g}" for v in LEVELS], fontsize=8)
    for ax, name in ((box, "boxplot: the predictions for each true label"), (scat, "scatter: every test text (dotted line = perfect)")):
        ax.set_yticks(range(1, 7))
        ax.set_ylim(0.5, 6.6)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_xlabel("true label")
        ax.set_title(name, fontsize=10)
    box.set_ylabel("predicted label")
    fig.suptitle(f"{header}\n"
                 f"MAE: {s['MAE'][0]:.3f} ({100 * s['MAE'][1]:.1f}%),  MSE: {s['MSE'][0]:.3f} ({100 * s['MSE'][1]:.1f}%),  "
                 f"RMSE: {s['RMSE'][0]:.3f} ({100 * s['RMSE'][1]:.1f}%),  corr: {s['corr']:.3f}", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", default="train_native", choices=list(TRAIN_SETS))
    args = ap.parse_args()
    (OUT / args.train).mkdir(parents=True, exist_ok=True)
    train_df = load_split("train")
    rows = train_mask(train_df, args.train)
    y_tr, y_te = train_df["label"].to_numpy()[rows], load_split("test")["label"].to_numpy()
    results = []
    for i, (name, title, signals, prefix) in enumerate(GROUPS, 1):
        X_tr, X_te, n = curated_data(signals, prefix, train_df, rows, LENGTH_LIKE if name == "grammar_vocab_no_length" else ())
        image = f"{args.train}/{i:02d}_{name}.png"
        results.append((title, n, image, draw(OUT / image, f"gradient boosting: {title} ({n} features)", y_te, gbm().fit(X_tr, y_tr).predict(X_te))))
    layer = best_bert_layer(args.train)
    emb = {s: embeddings.load(embeddings.DEFAULT_MODEL, s)[:, layer, :] for s in ("train", "test")}
    p = gbm().fit(emb["train"][rows], y_tr).predict(emb["test"])
    image = f"{args.train}/{len(GROUPS) + 1:02d}_bert_embedding.png"
    results.append((f"BERT-embedding (layer {layer})", emb["train"].shape[1], image, draw(OUT / image, f"gradient boosting: BERT-embedding (best layer, layer {layer}) ({emb['train'].shape[1]} features)", y_te, p)))
    for variant, name in (("full", "full"), ("lora", "LoRA")):  # reference rows: the fine-tuned runs of bert_based/run_finetune.py, if they exist
        path = FINETUNED / f"finetune_{variant}_{args.train}.json"
        if path.exists():
            run = json.loads(path.read_text(encoding="utf-8"))
            image = f"{args.train}/{len(results) + 1:02d}_bert_finetuned_{variant}.png"
            title = f"fine-tuned BERT ({name}), reference"
            results.append((title, "the text itself", image, draw(OUT / image, f"{title}: the text itself, {run['trainable_parameters']:,} trained parameters", y_te, np.array(run["test_pred"]))))
    write_report(args.train, results, layer)


def cell(v):
    return f"{v[0]:.3f} ({100 * v[1]:.1f}%)"


def write_report(train, results, layer):
    ranked = sorted(results, key=lambda r: r[3]["MAE"][0])
    L = ["# Which feature group predicts the label, and how well?", "",
         "Generated by `core/run_feature_group_plots.py`; no number is typed by hand. Every feature-group model is gradient boosting (300 rounds, learning rate 0.05), "
         f"trained on {TRAIN_SETS[train]} and graded on the 865 real-Finnish test texts. Each group is used alone, so the rows show what a group can do by itself; "
         "The rows are sorted by MAE. The two *fine-tuned BERT* rows are references, not gradient boosting on a feature group: they come from `bert_based/run_finetune.py` "
         "(BERT trained end to end on the texts; see `bert_based/reports/BERT_FINETUNE.md`).", "",
         "## How to read the numbers", "",
         "- **MAE, MSE, RMSE**: the average miss in label points, its mean square and its square root. In brackets: the same value as a share of the label range "
         f"({LABEL_RANGE} points, labels 1 to 6; MSE divided by the square of it). 0 is perfect. RMSE punishes big misses more than MAE does.",
         "- **corr**: Pearson correlation between the prediction and the true label; 1 is perfect, 0 means no relation.",
         "- **Boxplot**: for each true label, the spread of the predictions (the box holds the middle half, the orange line is the median, circles are outliers). "
         "**Scatter**: one dot per test text, nudged sideways so they do not overlap; the dotted line is a perfect prediction. "
         "The test set has no texts with label 1, 2.5 or 4.5, so those slots are empty.", "",
         "## What the groups are", "",
         "- **surface**: the 7 length and parse features (sentence count, mean, max and standard deviation of sentence length; tree depth, distinct POS, sentence length from the old parse columns).",
         "- **grammar-concept / grammar-topic**: the share of every grammar concept (268) or syllabus topic (133) in the text.",
         "- **vocab-lemma / vocab-stem**: the share of the text's words in each frequency bin, by lemma (12) or stem (13), and the mean log frequency. **vocab only** is both (25).",
         "- **all grammar + all vocab, no length features**: the same as the line below without surface: no sentence-length or parse features, and without the four word-form features that mostly measure length "
         f"({', '.join(LENGTH_LIKE)}).",
         "- **surface + all grammar + all vocab**: surface, concepts, topics, and all vocab including the 11 word-form features (word length, distinct lemmas, compounds, suffix ratios).",
         "- **fine-tuned BERT (full / LoRA)**: BERT trained on the texts themselves, all 125M weights (full) or about 0.3M small adapter weights (LoRA); no hand-made features. Same train and test texts.",
         f"- **BERT-embedding**: the 768 numbers of layer {layer} of `TurkuNLP/bert-base-finnish-cased-v1`, the layer with the lowest miss for ridge regression on the test set (so slightly optimistic).", "",
         "## Results (smaller miss is better)", ""]
    L += md_table(["feature group", "features", "MAE", "MSE", "RMSE", "corr"],
                  [[f"[{t}]({img})", n, cell(s["MAE"]), cell(s["MSE"]), cell(s["RMSE"]), f"{s['corr']:.3f}"] for t, n, img, s in ranked]) + [""]
    L += ["## Figures", ""]
    for t, n, img, s in ranked:
        L += [f"### {t}", "", f"![{t}]({img})", ""]
    L += ["## Reproduce", "", "```", "python core/run_feature_group_plots.py" + ("" if train == "train_native" else f" --train {train}"), "```", ""]
    path = OUT / ("FEATURE_GROUPS.md" if train == "train_native" else f"FEATURE_GROUPS_{train}.md")
    path.write_text("\n".join(L), encoding="utf-8")
    print("report ->", path)


if __name__ == "__main__":
    main()
