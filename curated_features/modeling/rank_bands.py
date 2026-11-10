"""How common are the words of a text, in rank bands a teacher can read: the most common 100 words, 101-500, ... over 20,000.

The rank of a lemma is its place in the lemma frequency list (the same list as the frequency bins), counted from the most common word.
The word rarity is log10(rank): about 2 for the 100th word, 3 for the 1,000th, 4 for the 10,000th, 5 for the 100,000th.
Each word of a text falls in one band; words Voikko does not know or that are not in the list are "unknown", English-looking ones "borrowed", names are skipped.
Used by the explanation prototype; results are cached in outputs/explanation_prototype/.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from curated_features.categories.vocab.shared.text_common import assign_bags, load_lemma_list, load_stem_list
from curated_features.categories.vocab.signals.vocab_freq.freq_features import FreqBinFeatures
from curated_features.utils.base import TextAnalysis

EDGES = [100, 500, 1000, 2000, 5000, 10000, 20000]
BANDS = ["top 100", "101-500", "501-1,000", "1,001-2,000", "2,001-5,000", "5,001-10,000", "10,001-20,000", "over 20,000"]
SPECIAL = ["unknown", "borrowed"]
CACHE = Path(__file__).resolve().parents[2] / "outputs" / "explanation_prototype"


class RankBander:
    def __init__(self):
        self.fb = FreqBinFeatures()
        self.neg_counts = -np.sort(np.fromiter(self.fb.freq["lemma"].values(), dtype=np.int64))[::-1]  # ascending, for searchsorted
        self.neg_stem = -np.sort(np.fromiter(self.fb.freq["stem"].values(), dtype=np.int64))[::-1]

    def token_class(self, tok, status, readings):
        """(band or "unknown" / "borrowed", log10 rank or None); None for names and abbreviations."""
        word = self.fb.read_word(tok, status, readings)
        if word.kind == "skipped":
            return None
        if word.kind == "unrecognised":
            return "unknown", None
        kind = self.fb._token_info(word)["lemma_unit"][0]
        if kind == "bag":
            rank = int(np.searchsorted(self.neg_counts, -self.fb.freq["lemma"][word.listed], side="left")) + 1
            return BANDS[int(np.searchsorted(EDGES, rank, side="left"))], float(np.log10(rank))
        return ("borrowed" if kind == "borrowed" else "unknown"), None

    def stem_classes(self, tok, status, readings):
        """The band of every stem unit of a word (a compound word has several); names and abbreviations give none."""
        word = self.fb.read_word(tok, status, readings)
        if word.kind == "skipped":
            return []
        if word.kind == "unrecognised":
            return ["unknown"]
        out = []
        for kind, _, logf in self.fb._token_info(word)["stem_units"]:
            if kind == "bag":
                rank = int(np.searchsorted(self.neg_stem, -int(round(10 ** logf)), side="left")) + 1
                out.append(BANDS[int(np.searchsorted(EDGES, rank, side="left"))])
            else:
                out.append("borrowed" if kind == "borrowed" else "unknown")
        return out

    def analyse(self, df):
        """(shares per text and the mean word rarity as a DataFrame, token -> (band, log10 rank) per text)"""
        an = TextAnalysis(df)
        cls = {tok: self.token_class(tok, *an.voikko[tok]) for toks in an.tokens for tok in toks}
        stem_cls = {tok: self.stem_classes(tok, *an.voikko[tok]) for toks in an.tokens for tok in toks}
        rows, per_text = [], []
        for toks in an.tokens:
            pairs = [cls[t] for t in toks if cls[t] is not None]
            classes = [b for b, _ in pairs]
            n = max(len(classes), 1)
            logs = [lr for _, lr in pairs if lr is not None]
            stems = [b for t in toks for b in stem_cls[t]]
            ns = max(len(stems), 1)
            rows.append({**{b: classes.count(b) / n for b in BANDS + SPECIAL}, **{"stem::" + b: stems.count(b) / ns for b in BANDS + SPECIAL},
                         "mean_log_rank": float(np.mean(logs)) if logs else 0.0})
            per_text.append({t: cls[t] for t in toks})
        return pd.DataFrame(rows, index=df.index), per_text


def cached_shares(name, df):
    """Rank-band shares of the texts of `df`, computed once and kept in outputs/explanation_prototype/rank_bands_<name>.csv."""
    path = CACHE / f"rank_bands_{name}.csv"
    if path.exists():
        return pd.read_csv(path, index_col=0).set_axis(df.index)
    CACHE.mkdir(parents=True, exist_ok=True)
    shares, _ = RankBander().analyse(df)
    shares.to_csv(path)
    return shares


METHODS = {"log10_freq_bin": "decade", "uniform_cumfreq_bin": "equalshare", "uniform_rank_bin": "equalcount"}


def cached_method(name, df, method):
    """Lemma and stem shares per bin for one of the pipeline's binning methods (10 bins), cached in outputs/explanation_prototype/bins_<method>_<name>.csv."""
    path = CACHE / f"bins_{METHODS[method]}_{name}.csv"
    if path.exists():
        return pd.read_csv(path, index_col=0).set_axis(df.index)
    CACHE.mkdir(parents=True, exist_ok=True)
    X = FreqBinFeatures(lemma_bin_method=method, stem_bin_method=method, lemma_n_bins=10, stem_n_bins=10).build(TextAnalysis(df))
    X = X[[c for c in X.columns if not c.startswith("mean_log")]]
    X.to_csv(path)
    return X


def bin_tables():
    """For every method and unit: the bins with their word ranks, corpus counts, number of different words and share of running text (list of dict rows)."""
    out = {}
    for unit, loader in (("lemma", lambda: load_lemma_list("freq")), ("stem", load_stem_list)):
        items, freq = loader()
        counts = np.array([freq[i] for i in items], dtype=np.int64)
        order = np.argsort(-counts, kind="stable")
        items, counts = [items[i] for i in order], counts[order]
        total = counts.sum()
        assignments = {m: np.array([bags[i] for i in items]) for m in METHODS for bags in [assign_bags(items, freq, m, 10)]}
        assignments["rank bands"] = np.searchsorted(EDGES, np.arange(1, len(items) + 1), side="left") + 1
        for m, b in assignments.items():
            rows = []
            for k in sorted(set(b.tolist())):
                sel = np.flatnonzero(b == k)
                rows.append({"bin": int(k), "ranks": (int(sel.min()) + 1, int(sel.max()) + 1), "counts": (int(counts[sel].min()), int(counts[sel].max())), "words": len(sel),
                             "share": 100 * float(counts[sel].sum()) / float(total)})
            out[(m, unit)] = rows
        del items, counts
    return out
