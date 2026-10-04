"""VocabDiffFeatureConstruct: word-level difficulty features of a text.

Two sets of frequency-bag features, built side by side so they can be compared:
  stem level   a word's bag is the bag of its rarest known STEM (työ, paikka, ostaa): a compound is as hard as its hardest part
  lemma level  a word's bag is the bag of its own LEMMA
Bags: 1 = most frequent ... highest = rarest. Per level:
  {stem|lemma}_OOV_coverage     share of counted words that are unknown: not recognised by Voikko, or recognised but not in the list
  {stem|lemma}_bag_{k}_coverage share of counted words in bag k
  mean_log_{stem|lemma}_freq    mean log10 count of the word's rarest known stem / of the word's lemma (words in the list only)
Shared: borrowed_coverage = share of words whose stems are all English-looking (removed in step 5); they are not OOV.
Shares are over the counted words: names and abbreviations are skipped.
Other features (definitions in docs/features.md):
  lexical diversity     n_unique_lemmas, ttr_lemma_200
  word form             avg_word_length, long_word_ratio
  compounding           compound_ratio, avg_compound_parts, n_compound_tokens
  derivation            deriv_llinen_ratio, deriv_ton_ratio (Voikko suffix markers),
                        deriv_minen_ratio, deriv_sti_ratio (HEURISTICS: Voikko treats -minen / -sti as inflection)
Content words = nouns, adjectives, verbs, adverbs; names, abbreviations and unrecognised words are not content words.
The reading of an ambiguous word is the Voikko candidate whose lemma has the highest lemma-list frequency (context-free).
"""
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from base import FeatureConstruct, TextAnalysis  # noqa: E402
from text_common import assign_bags, best_lemma, load_borrowed_stems, load_lemma_list, load_stem_list  # noqa: E402

CONTENT_CLASSES = {"nimisana", "laatusana", "teonsana", "seikkasana", "nimisana_laatusana"}
LONG_WORD = 10
TTR_WINDOW = 200
MINEN_ENDINGS = ("minen", "misen", "mista", "mistä", "missa", "missä", "misessa", "misessä", "misesta", "misestä",
                 "miseen", "misella", "misellä", "miselta", "miseltä", "miselle", "misena", "miseksi", "misetta", "misettä",
                 "misten", "misia", "misiä", "misissa", "misissä", "misista", "misistä", "misiin", "misilla", "misillä")
TEXT_FEATURES = ["n_unique_lemmas", "ttr_lemma_200", "avg_word_length", "long_word_ratio", "compound_ratio",
                 "avg_compound_parts", "n_compound_tokens", "deriv_llinen_ratio", "deriv_ton_ratio",
                 "deriv_minen_ratio", "deriv_sti_ratio"]
LEVELS = ("stem", "lemma")


class VocabDiffFeatureConstruct(FeatureConstruct):
    category = "vocab"

    def __init__(self, bag_method: str = "uniform_cumfreq_bin"):
        self.bag_method = bag_method
        lemmas_desc, self.freq = {}, {}
        lemmas_desc["lemma"], self.freq["lemma"] = load_lemma_list("freq")
        lemmas_desc["stem"], self.freq["stem"] = load_stem_list()
        self.bags = {lv: assign_bags(lemmas_desc[lv], self.freq[lv], bag_method) for lv in LEVELS}
        self.n_bags = {lv: max(self.bags[lv].values()) for lv in LEVELS}
        self.bag_columns = {lv: [f"{lv}_bag_{b}_coverage" for b in range(1, self.n_bags[lv] + 1)] for lv in LEVELS}
        self.borrowed = load_borrowed_stems()
        self.feature_names = ["borrowed_coverage",
                              "stem_OOV_coverage", *self.bag_columns["stem"], "mean_log_stem_freq",
                              "lemma_OOV_coverage", *self.bag_columns["lemma"], "mean_log_lemma_freq", *TEXT_FEATURES]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        return self.build_with_tallies(analysis)[0]

    def build_with_tallies(self, analysis: TextAnalysis):
        """(features, tallies): tallies has the word counts per text, per level (all, skipped, borrowed, unrecognised, unlisted, in_bag)."""
        info = {tok: self._token_info(tok, status, readings) for tok, (status, readings) in analysis.voikko.items()}
        rows, tallies = [], []
        for toks in analysis.tokens:
            row, tally = self._text_row(toks, info)
            rows.append(row)
            tallies.append(tally)
        return (pd.DataFrame(rows, index=analysis.df.index, columns=self.feature_names),
                pd.DataFrame(tallies, index=analysis.df.index))

    def _token_info(self, tok, status, readings):
        """Everything one token contributes: its lemma, reading, and how it counts at the stem and lemma level."""
        info = {"lemma": tok.lower(), "reading": None,
                "stem": ("unrecognised", 0, 0.0), "lemma_level": ("unrecognised", 0, 0.0)}
        if status in ("name", "abbrev"):
            info.update(lemma=readings[0][0].lower(), stem=("skipped", 0, 0.0), lemma_level=("skipped", 0, 0.0))
            return info
        if status != "ok":
            return info
        listed = best_lemma([r[0].lower() for r in readings], self.freq["lemma"])
        reading = next((r for r in readings if r[0].lower() == listed), readings[0])
        stems = [s.replace("=", "") for s in reading[2]]
        stems = [s for s in stems if s and not s[:1].isupper()] or [reading[0].lower()]
        known = [s for s in stems if s in self.bags["stem"]]
        info.update(lemma=reading[0].lower(), reading=reading)
        if known:
            info["stem"] = ("bag", max(self.bags["stem"][s] for s in known), math.log10(min(self.freq["stem"][s] for s in known)))
        else:
            info["stem"] = ("borrowed" if any(s in self.borrowed for s in stems) else "unlisted", 0, 0.0)
        if listed is not None:
            info["lemma_level"] = ("bag", self.bags["lemma"][listed], math.log10(self.freq["lemma"][listed]))
        else:  # not in the lemma list: removed as English-looking, or unknown
            info["lemma_level"] = ("borrowed" if info["stem"][0] == "borrowed" else "unlisted", 0, 0.0)
        return info

    def _text_row(self, tokens, info):
        lemmas, content = [], []
        tally = {lv: Counter() for lv in LEVELS}
        bag_counts = {lv: np.zeros(self.n_bags[lv] + 1) for lv in LEVELS}
        logfs = {lv: [] for lv in LEVELS}
        for tok in tokens:
            t = info[tok]
            lemmas.append(t["lemma"])
            for lv, key in (("stem", "stem"), ("lemma", "lemma_level")):
                kind, bag, logf = t[key]
                tally[lv][kind] += 1
                if kind == "bag":
                    bag_counts[lv][bag] += 1
                    logfs[lv].append(logf)
            if t["reading"] is not None and t["reading"][1] in CONTENT_CLASSES:
                content.append((tok.lower(), t["reading"]))

        counted = len(tokens) - tally["stem"]["skipped"]
        n_content = len(content)
        window = lemmas[:TTR_WINDOW]
        compounds = [r for _, r in content if len(r[2]) >= 2]
        ratio = lambda k: k / n_content if n_content else 0.0
        share = lambda k: k / counted if counted else 0.0
        llinen = sum(any(s.endswith(">+nen") and s.startswith("lli") for s in r[3]) for _, r in content)
        ton = sum(any(s.endswith(">+ton") for s in r[3]) for _, r in content)
        minen = sum(r[1] == "teonsana" and tok.endswith(MINEN_ENDINGS) for tok, r in content)
        sti = sum(r[1] == "laatusana" and tok.endswith("sti") and r[0].lower() != tok and not r[0].endswith("sti") for tok, r in content)
        row = {"borrowed_coverage": share(tally["stem"]["borrowed"])}
        for lv in LEVELS:
            row[f"{lv}_OOV_coverage"] = share(tally[lv]["unrecognised"] + tally[lv]["unlisted"])
            row.update({f"{lv}_bag_{b}_coverage": share(bag_counts[lv][b]) for b in range(1, self.n_bags[lv] + 1)})
            row[f"mean_log_{lv}_freq"] = float(np.mean(logfs[lv])) if logfs[lv] else 0.0
        row.update({
            "n_unique_lemmas": len(set(lemmas)),
            "ttr_lemma_200": len(set(window)) / len(window) if window else 0.0,
            "avg_word_length": float(np.mean([len(t) for t in tokens])) if tokens else 0.0,
            "long_word_ratio": sum(len(t) >= LONG_WORD for t in tokens) / len(tokens) if tokens else 0.0,
            "compound_ratio": ratio(len(compounds)),
            "avg_compound_parts": float(np.mean([len(r[2]) for r in compounds])) if compounds else 0.0,
            "n_compound_tokens": len(compounds),
            "deriv_llinen_ratio": ratio(llinen),
            "deriv_ton_ratio": ratio(ton),
            "deriv_minen_ratio": ratio(minen),
            "deriv_sti_ratio": ratio(sti),
        })
        tally_row = {"all": len(tokens), "skipped": tally["stem"]["skipped"], "borrowed": tally["stem"]["borrowed"]}
        for lv in LEVELS:
            tally_row.update({f"{lv}_unrecognised": tally[lv]["unrecognised"], f"{lv}_unlisted": tally[lv]["unlisted"], f"{lv}_in_bag": tally[lv]["bag"]})
        return row, tally_row
