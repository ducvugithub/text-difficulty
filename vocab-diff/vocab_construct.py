"""VocabDiffFeatureConstruct: word-level difficulty features of a text.

Two sets of frequency-bin features, built side by side so they can be compared. Bin type and number of bins are set
per level: VocabDiffFeatureConstruct(lemma_bin_method="log10_freq_bin", stem_bin_method="uniform_cumfreq_bin",
lemma_n_bins=10, stem_n_bins=10); bin types: uniform_rank_bin, uniform_cumfreq_bin, log10_freq_bin (see step 6).
Bins: 1 = most frequent ... highest = rarest.
  lemma level  each word is placed by the count of its own LEMMA
  stem level   each word is split into its STEMS (työ + paikka) and every stem is placed by its own stem count;
               a word with two stems is two units, a word Voikko does not recognise is one unit
Per level, shares are over the counted units (names and abbreviations are skipped):
  {level}_OOV_coverage        unknown: a word Voikko does not recognise, or a lemma / stem that is not in the list
  {level}_borrowed_coverage   English-looking: lemma / stems removed in step 5 (not OOV)
  {level}_bag_{k}_coverage    in bin k
  mean_log_{level}_freq       mean log10 count of the units in a bin
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

    def __init__(self, lemma_bin_method: str = "log10_freq_bin", stem_bin_method: str = "uniform_cumfreq_bin",
                 lemma_n_bins: int = 10, stem_n_bins: int = 10):
        """Bin type and number of bins are set per level. n_bins is the maximum: log10_freq_bin gives one bin per
        decade (9 for this data) and merges the rarest decades into the last bin when n_bins is smaller."""
        self.bin_methods = {"lemma": lemma_bin_method, "stem": stem_bin_method}
        self.n_bins = {"lemma": lemma_n_bins, "stem": stem_n_bins}
        lemmas_desc, self.freq = {}, {}
        lemmas_desc["lemma"], self.freq["lemma"] = load_lemma_list("freq")
        lemmas_desc["stem"], self.freq["stem"] = load_stem_list()
        self.bags = {lv: assign_bags(lemmas_desc[lv], self.freq[lv], self.bin_methods[lv], self.n_bins[lv]) for lv in LEVELS}
        self.n_bags = {lv: max(self.bags[lv].values()) for lv in LEVELS}
        self.bag_columns = {lv: [f"{lv}_bag_{b}_coverage" for b in range(1, self.n_bags[lv] + 1)] for lv in LEVELS}
        self.borrowed = load_borrowed_stems()
        self.feature_names = [name for lv in ("stem", "lemma") for name in
                              (f"{lv}_OOV_coverage", f"{lv}_borrowed_coverage", *self.bag_columns[lv], f"mean_log_{lv}_freq")] + TEXT_FEATURES

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
        """What one token contributes: its lemma, reading, one lemma-level unit and its stem-level units.
        A unit is (kind, bin, log10 count); kind is bag / borrowed / unlisted / unrecognised / skipped."""
        info = {"lemma": tok.lower(), "reading": None, "lemma_unit": ("unrecognised", 0, 0.0), "stem_units": [("unrecognised", 0, 0.0)]}
        if status in ("name", "abbrev"):
            info.update(lemma=readings[0][0].lower(), lemma_unit=("skipped", 0, 0.0), stem_units=[])
            return info
        if status != "ok":
            return info
        listed = best_lemma([r[0].lower() for r in readings], self.freq["lemma"])
        reading = next((r for r in readings if r[0].lower() == listed), readings[0])
        stems = [s.replace("=", "") for s in reading[2]]
        stems = [s for s in stems if s and not s[:1].isupper()] or [reading[0].lower()]
        info.update(lemma=reading[0].lower(), reading=reading)
        units = []
        for s in stems:
            if s in self.bags["stem"]:
                units.append(("bag", self.bags["stem"][s], math.log10(self.freq["stem"][s])))
            else:
                units.append(("borrowed" if s in self.borrowed else "unlisted", 0, 0.0))
        info["stem_units"] = units
        if listed is not None:
            info["lemma_unit"] = ("bag", self.bags["lemma"][listed], math.log10(self.freq["lemma"][listed]))
        else:  # not in the lemma list: removed as English-looking, or unknown
            all_borrowed = all(kind == "borrowed" for kind, _, _ in units)
            info["lemma_unit"] = ("borrowed" if all_borrowed else "unlisted", 0, 0.0)
        return info

    def _text_row(self, tokens, info):
        lemmas, content = [], []
        tally = {lv: Counter() for lv in LEVELS}
        bag_counts = {lv: np.zeros(self.n_bags[lv] + 1) for lv in LEVELS}
        logfs = {lv: [] for lv in LEVELS}
        for tok in tokens:
            t = info[tok]
            lemmas.append(t["lemma"])
            for lv, units in (("stem", t["stem_units"]), ("lemma", [t["lemma_unit"]])):
                for kind, bag, logf in units:
                    tally[lv][kind] += 1
                    if kind == "bag":
                        bag_counts[lv][bag] += 1
                        logfs[lv].append(logf)
            if t["reading"] is not None and t["reading"][1] in CONTENT_CLASSES:
                content.append((tok.lower(), t["reading"]))

        n_content = len(content)
        window = lemmas[:TTR_WINDOW]
        compounds = [r for _, r in content if len(r[2]) >= 2]
        ratio = lambda k: k / n_content if n_content else 0.0
        llinen = sum(any(s.endswith(">+nen") and s.startswith("lli") for s in r[3]) for _, r in content)
        ton = sum(any(s.endswith(">+ton") for s in r[3]) for _, r in content)
        minen = sum(r[1] == "teonsana" and tok.endswith(MINEN_ENDINGS) for tok, r in content)
        sti = sum(r[1] == "laatusana" and tok.endswith("sti") and r[0].lower() != tok and not r[0].endswith("sti") for tok, r in content)
        row = {}
        for lv in LEVELS:
            counted = sum(v for k, v in tally[lv].items() if k != "skipped")
            share = lambda k: k / counted if counted else 0.0
            row[f"{lv}_OOV_coverage"] = share(tally[lv]["unrecognised"] + tally[lv]["unlisted"])
            row[f"{lv}_borrowed_coverage"] = share(tally[lv]["borrowed"])
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
        tally_row = {"words": len(tokens), "skipped": tally["lemma"]["skipped"]}
        for lv in LEVELS:
            tally_row.update({f"{lv}_{k}": tally[lv][k] for k in ("unrecognised", "unlisted", "borrowed", "bag")})
        return row, tally_row
