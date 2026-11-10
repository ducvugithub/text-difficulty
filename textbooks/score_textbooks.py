"""Score the textbook texts, the paragraph texts and the dialogue texts separately (data/textbooks/paragraph_texts.csv, dialogue_texts.csv).

Every model is gradient boosting trained on the real-Finnish training rows and applied to the textbook texts. The groups, in order:
  BERT          frozen layer 5; LoRA and full fine-tuning (only when their saved weights exist, see bert_based/run_finetune.py --save-model)
  length        sentence length, the 4 surface measures
  grammar       concept coverage / CEFR levels / rarity, syllabus topic coverage / levels / rarity
  vocabulary    frequency bins, lexical features, rank bands, bins + lexical
  combinations  vocabulary + grammar, and + length
  constant      the mean of the estimated labels
The grammar counts of the textbook texts come from Revita's own pipeline (textbooks/revita_concepts_remote.py, run on the staging server; stored in
data/textbooks/revita_concepts.json), while the training rows carry the concept columns of an older Revita run.
The labels of the books are estimates (build_passages.py): the answer is the estimated label rounded to the nearest half step, the prediction is rounded the same way.

    python textbooks/score_textbooks.py        prints the results per set, writes reports/textbook_evaluation/TEXTBOOK_RESULTS.md (numbers only) and data/textbooks/predictions_<set>.csv
In the dialogue texts the speaker labels ("Pedro:") are removed before scoring, so the names do not count as words.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bert_based import embeddings  # noqa: E402
from build_passages import HEADER_WORDS, SPEAKER  # noqa: E402
from core.dataset import load_split, native_mask, surface_features  # noqa: E402
from curated_features.categories.grammar.shared import grammar_items  # noqa: E402
from curated_features.modeling.rank_bands import BANDS, SPECIAL, RankBander, cached_shares  # noqa: E402
from curated_features.utils import registry  # noqa: E402
from curated_features.utils.base import TextAnalysis  # noqa: E402
from curated_features.utils.feature_store import feature_table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "textbooks"
BOOK_INDEX = {"sm1": 1, "sm2": 2, "sm3": 3, "sm4": 4}
R = 5  # the label range (labels 1 to 6); the percents divide by it
RANK_COLS = BANDS + SPECIAL + ["mean_log_rank"]
SIGNALS = {  # block name -> the registered signals (train: precomputed columns; textbooks: computed)
    "sent": [("cognitive", "sentence_length")], "freq": [("vocab", "freq")], "freq_eq": [("vocab", "freq", {"lemma_bin_method": "uniform_cumfreq_bin"})], "freq_dec": [("vocab", "freq", {"stem_bin_method": "log10_freq_bin"})], "lexical": [("vocab", "lexical")],
    "g_cov": [("grammar", "coverage_concepts")], "g_lev": [("grammar", "manual_concepts_levels")], "g_rar": [("grammar", "rarity_concepts")],
    "t_cov": [("grammar", "coverage_topics")], "t_lev": [("grammar", "manual_topics_levels")], "t_rar": [("grammar", "rarity_topics")],
}
FREQ_SPLIT = {"freq_lemma": ("freq", "lemma"), "freq_stem": ("freq", "stem"), "freq_stem_dec": ("freq_dec", "stem"), "freq_lemma_eq": ("freq_eq", "lemma")}  # the lemma-level / stem-level columns of the frequency block
GRAMMAR_KIND = {"g_cov": "concept", "g_lev": "concept", "g_rar": "concept", "t_cov": "topic", "t_lev": "topic", "t_rar": "topic"}
# (group, name, blocks)
MODELS = [
    ("length", "sentence length (4)", ["sent"]),
    ("length", "surface measures (4)", ["surface"]),
    ("length", "sentence length + surface", ["sent", "surface"]),
    ("grammar", "concept individual share (268)", ["g_cov"]),
    ("grammar", "concept manual CEFR level share (8)", ["g_lev"]),
    ("grammar", "concept rarity bin share (9)", ["g_rar"]),
    ("grammar", "topic individual share (133)", ["t_cov"]),
    ("grammar", "topic manual CEFR level share (4)", ["t_lev"]),
    ("grammar", "topic rarity bin share (8)", ["t_rar"]),
    ("grammar", "concept individual share + manual CEFR level share + rarity", ["g_cov", "g_lev", "g_rar"]),
    ("vocabulary", "lemma frequency bins, decades (12)", ["freq_lemma"]),
    ("vocabulary", "lemma frequency bins, equal-share (13)", ["freq_lemma_eq"]),
    ("vocabulary", "stem frequency bins, equal-share (13)", ["freq_stem"]),
    ("vocabulary", "stem frequency bins, decades (12)", ["freq_stem_dec"]),
    ("vocabulary", "lemma decades + stem equal-share (25)", ["freq"]),
    ("vocabulary", "lemma decades + stem decades (24)", ["freq_dec"]),
    ("vocabulary", "lemma equal-share + stem equal-share (26)", ["freq_eq"]),
    ("vocabulary", "lexical features, word form (11)", ["lexical"]),
    ("vocabulary", "lemma decades + stem equal-share + lexical features, word form (36)", ["freq", "lexical"]),
    ("combination", "vocabulary (bins + lexical) + concept individual share", ["freq", "lexical", "g_cov"]),
    ("combination", "vocabulary (bins + lexical) + concept manual CEFR level share + rarity", ["freq", "lexical", "g_lev", "g_rar"]),
    ("combination + length", "vocabulary + concept individual share + sentence length", ["freq", "lexical", "g_cov", "sent"]),
    ("combination + length", "vocabulary + concept individual share + surface", ["freq", "lexical", "g_cov", "surface"]),
    ("combination + length", "vocabulary + concept individual share + sentence length + surface", ["freq", "lexical", "g_cov", "sent", "surface"]),
]
FINETUNED = {"bert-base-finnish-cased-v1 LoRA + linear head (0.3M trained)": ROOT / "outputs" / "finetuned" / "lora_train_native", "bert-base-finnish-cased-v1 full + linear head (124.5M trained)": ROOT / "outputs" / "finetuned" / "full_train_native"}


def gbm():
    return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)


def strip_speakers(text):
    return SPEAKER.sub(lambda m: " " if m.group(1) not in HEADER_WORDS else m.group(0), text)


class Blocks:
    """The feature blocks of the training rows and of one set of textbook texts, each computed once."""

    def __init__(self, texts, ids, train_df, rows):
        self.texts, self.ids, self.rows = texts, ids, rows
        self.frame = pd.DataFrame({"text": texts.to_numpy()})
        self.analysis = TextAnalysis(self.frame)
        self.train_native = train_df[rows]
        self.revita = json.loads((DATA / "revita_concepts.json").read_text())
        self.train_cache, self.new_cache, self._ranks = {}, {}, None

    def train(self, name):
        if name in FREQ_SPLIT:
            base, level = FREQ_SPLIT[name]
            X = self.train(base)
            return X[[c for c in X.columns if level in c]]
        if name not in self.train_cache:
            if name == "surface":
                X = feature_table("train", {"surface": True})[0]
            elif name == "rank":
                return cached_shares("train_native", self.train_native)[RANK_COLS]
            else:
                X = feature_table("train", {"signals": SIGNALS[name]})[0]
            self.train_cache[name] = X.iloc[np.flatnonzero(self.rows)]
        return self.train_cache[name]

    def new(self, name):
        if name in FREQ_SPLIT:
            base, level = FREQ_SPLIT[name]
            X = self.new(base)
            return X[[c for c in X.columns if level in c]]
        if name not in self.new_cache:
            if name == "surface":
                X = surface_features(self.frame)
            elif name == "rank":
                if self._ranks is None:
                    self._ranks = RankBander().analyse(self.frame)[0]
                X = self._ranks[RANK_COLS]
            elif name in GRAMMAR_KIND:
                kind = GRAMMAR_KIND[name]
                counts = pd.DataFrame([self.revita[i]["concepts" if kind == "concept" else "topics"] for i in self.ids]).reindex(columns=grammar_items.ids(kind), fill_value=0).fillna(0.0)
                (category, signal), = SIGNALS[name]
                sig = registry.make(category, signal)
                sig.counts = lambda analysis, _c=counts: _c  # Revita's own counts instead of the precomputed columns
                X = sig.build(self.analysis)
            else:
                X = pd.concat([registry.make(c, s, **(rest[0] if rest else {})).build(self.analysis) for c, s, *rest in SIGNALS[name]], axis=1)
            self.new_cache[name] = X.reset_index(drop=True)
        return self.new_cache[name]


def accuracy(p, gold):
    off = np.abs(np.round(p * 2) / 2 - gold)
    return float((off == 0).mean()), float((off <= 0.5).mean()), float((off <= 1.0).mean())


def fmt(v):
    return f"{v:.3f} ({100 * v / R:.1f}%)"


def bert_frozen(texts, y, rows):
    import torch
    from transformers import AutoModel, AutoTokenizer
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(embeddings.DEFAULT_MODEL)
    bert = AutoModel.from_pretrained(embeddings.DEFAULT_MODEL, output_hidden_states=True).eval().to(device)
    E_new = embeddings.embed(texts.tolist(), tok, bert, device)[:, 5, :]
    E_tr = embeddings.load(embeddings.DEFAULT_MODEL, "train")[:, 5, :][rows]
    return gbm().fit(E_tr, y).predict(E_new)


def finetuned(folder, texts):
    """Predictions of a saved fine-tuned model (bert_based/run_finetune.py --save-model) for the texts."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from bert_based.run_finetune import predict
    meta = json.loads((folder / "meta.json").read_text())
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(meta["base_model"])
    if meta["variant"] == "lora":
        from peft import PeftModel
        model = PeftModel.from_pretrained(AutoModelForSequenceClassification.from_pretrained(meta["base_model"], num_labels=1), folder)
    else:
        model = AutoModelForSequenceClassification.from_pretrained(folder)
    return predict(model.to(device), tok, texts.tolist(), device, meta["mean"], meta["std"], meta["window"])


def score(csv_name, title, strip, tr, rows, y, report):
    books = pd.read_csv(DATA / csv_name)
    texts = books["text"].astype(str)
    if strip:
        texts = texts.map(strip_speakers)
    blocks = Blocks(texts, books["id"].tolist(), tr, rows)
    est, book = books["estimated_label"].to_numpy(), books["book"].map(BOOK_INDEX).to_numpy()
    gold = np.round(est * 2) / 2
    results = [("BERT", "bert-base-finnish-cased-v1 frozen, layer 5 + gradient boosting", bert_frozen(texts, y, rows))]
    for name, path in FINETUNED.items():
        results.append(("BERT", name, finetuned(path, texts) if (path / "meta.json").exists() else None))
    for group, name, parts in MODELS:
        X_tr = pd.concat([blocks.train(b) for b in parts], axis=1)
        X_new = pd.concat([blocks.new(b) for b in parts], axis=1).reindex(columns=X_tr.columns, fill_value=0.0)
        results.append((group, name, gbm().fit(X_tr, y).predict(X_new)))
    results.append(("constant", "constant guess (the mean estimate)", np.full(len(est), float(est.mean()))))
    head = ["model", "exactly right", "within 0.5", "within 1.0", "MAE (%)", "MSE (%)", "corr"]
    lines = [f"\n### {title}: {len(books)} texts (" + ", ".join(f"{b} {int((books['book'] == b).sum())}" for b in BOOK_INDEX) + ")", "",
             "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out, last = books[["id", "book", "chapter", "pages", "kind", "estimated_label"]].copy(), None
    for group, name, p in results:
        if group != last:
            lines.append(f"| **{group}** | | | | | | |")
            last = group
        if p is None:
            lines.append(f"| {name} | not available yet | | | | | |")
            continue
        ex, w1, w2 = accuracy(p, gold)
        err = p - est
        corr = float(np.corrcoef(p, est)[0, 1]) if p.std() > 0 else float("nan")
        lines.append(f"| {name} | {ex:.0%} | {w1:.0%} | {w2:.0%} | {fmt(np.abs(err).mean())} | {100 * (err ** 2).mean() / R ** 2:.1f}% | {corr:.2f} |")
        out[name] = np.round(p, 3)
    lines += ["", "answer = the estimated label rounded to the nearest half step; prediction rounded the same way. MAE, MSE (as a share of the squared label range) and corr are against the unrounded estimated label."]
    out.to_csv(DATA / f"predictions_{csv_name.replace('_texts.csv', '')}.csv", index=False)
    report.extend(lines)
    print("\n".join(lines), flush=True)


def main():
    warnings.filterwarnings("ignore")
    tr = load_split("train")
    rows = native_mask(tr)
    y = tr["label"].to_numpy()[rows]
    report = ["# Textbook texts scored by the models", "",
              "Generated by `textbooks/score_textbooks.py`.", "",
              "BERT rows use TurkuNLP/bert-base-finnish-cased-v1 (124.5M parameters); the other models are gradient boosting trained on the real-Finnish rows. The estimated label of a text is its book's CEFR range (our labels: 1 = A1, 2 = A2, 3 = B1, 4 = B2) spread evenly over the chapters.", "",
              "| book | learner guide range ([uusikielemme.fi](https://uusikielemme.fi/language-levels/textbooks/suomen-mestari-series-finnish-study-books)) | CEFR estimated range (label) |",
              "|---|---|---|",
              "| SM1 | zero to A1.3 | 1.0 to 1.5 |",
              "| SM2 | A1.3 to A2.1 | 1.5 to 2.0 |",
              "| SM3 | A2.2 to B1.1 | 2.5 to 3.0 |",
              "| SM4 | B1.1 to B2 | 3.0 to 4.0 |", "",
              "What some row names mean:", "",
              "| row | what it uses |",
              "|---|---|",
              "| sentence length (4) | number of sentences, mean sentence length in words, longest sentence, standard deviation of sentence length |",
              "| surface measures (4) | number of words, number of characters, mean word length in characters, mean sentence length in words |",
              "",
              "Frequency bins of the two levels (bin 1 = most frequent). Lemma bins are decades (one bin per factor of 10 in times seen); stem bins are equal share (each bin holds 10% of all stem occurrences):", "",
              "| bin | stem count | stem freq (times seen) | lemma count | lemma freq (times seen) |",
              "|---|---|---|---|---|",
              "| 1 | 3 | 54.7M to 175M | 2 | 100M to 999M |",
              "| 2 | 14 | 16.2M to 52.2M | 25 | 10M to 99M |",
              "| 3 | 29 | 7.87M to 15.0M | 401 | 1M to 9.99M |",
              "| 4 | 54 | 4.85M to 7.42M | 2,502 | 100k to 999k |",
              "| 5 | 89 | 2.83M to 4.83M | 11,012 | 10k to 99k |",
              "| 6 | 144 | 1.85M to 2.82M | 46,629 | 1k to 9.99k |",
              "| 7 | 219 | 1.15M to 1.84M | 176,769 | 100 to 999 |",
              "| 8 | 394 | 581k to 1.14M | 768,222 | 10 to 99 |",
              "| 9 | 929 | 196k to 581k | 5,277,621 | 1 to 9 |",
              "| 10 | 18,829 | 1 to 195k | none | none |", "",
              "A third option, equal count (not scored), gives every bin the same number of distinct words."]
    score("paragraph_texts.csv", "Paragraph texts", False, tr, rows, y, report)
    score("dialogue_texts.csv", "Dialogue texts (speaker labels removed)", True, tr, rows, y, report)
    out = ROOT / "reports" / "textbook_evaluation" / "TEXTBOOK_RESULTS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\nreport -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
