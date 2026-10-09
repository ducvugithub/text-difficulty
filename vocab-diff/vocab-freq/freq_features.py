"""FreqBinFeatures: the frequency-bin signal of a text (signal 1 of the vocab category).

Two sets of features, built side by side so they can be compared. Bin type and number of bins are set per level:
FreqBinFeatures(lemma_bin_method="log10_freq_bin", stem_bin_method="uniform_cumfreq_bin", lemma_n_bins=10, stem_n_bins=10);
bin types: uniform_rank_bin, uniform_cumfreq_bin, log10_freq_bin (see step 6). Bins: 1 = most frequent ... highest = rarest.
  lemma level  each word is placed by the count of its own LEMMA
  stem level   each word is split into its STEMS (työ + paikka) and every stem is placed by its own stem count;
               a word with two stems is two units, a word Voikko does not recognise is one unit
Per level, shares are over the counted units (names and abbreviations are skipped):
  {level}_OOV_coverage        unknown: a word Voikko does not recognise, or a lemma / stem that is not in the list
  {level}_borrowed_coverage   English-looking: lemma / stems removed in step 5 (not OOV)
  {level}_bag_{k}_coverage    in bin k
  mean_log_{level}_freq       mean log10 count of the units in a bin
The reading of an ambiguous word is the Voikko candidate whose lemma has the highest lemma-list frequency (context-free).
"""
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vocab-diff" / "shared"))
from base import TextAnalysis  # noqa: E402
from text_common import assign_bags, load_borrowed_stems, load_lemma_list, load_stem_list  # noqa: E402
from vocab_base import VocabFeatureConstruct  # noqa: E402

LEVELS = ("stem", "lemma")


class FreqBinFeatures(VocabFeatureConstruct):
    signal = "freq"

    def __init__(self, lemma_bin_method: str = "log10_freq_bin", stem_bin_method: str = "uniform_cumfreq_bin",
                 lemma_n_bins: int = 10, stem_n_bins: int = 10):
        """n_bins is the maximum: log10_freq_bin gives one bin per decade (9 for this data) and merges the rarest decades
        into the last bin when n_bins is smaller."""
        super().__init__()
        self.bin_methods = {"lemma": lemma_bin_method, "stem": stem_bin_method}
        self.n_bins = {"lemma": lemma_n_bins, "stem": stem_n_bins}
        items_desc, self.freq = {}, {}
        items_desc["lemma"], self.freq["lemma"] = load_lemma_list("freq")
        items_desc["stem"], self.freq["stem"] = load_stem_list()
        self.bags = {lv: assign_bags(items_desc[lv], self.freq[lv], self.bin_methods[lv], self.n_bins[lv]) for lv in LEVELS}
        self.n_bags = {lv: max(self.bags[lv].values()) for lv in LEVELS}
        self.bag_columns = {lv: [f"{lv}_bag_{b}_coverage" for b in range(1, self.n_bags[lv] + 1)] for lv in LEVELS}
        self.borrowed = load_borrowed_stems()
        self.feature_names = [name for lv in LEVELS for name in
                              (f"{lv}_OOV_coverage", f"{lv}_borrowed_coverage", *self.bag_columns[lv], f"mean_log_{lv}_freq")]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        return self.build_with_tallies(analysis)[0]

    def build_with_tallies(self, analysis: TextAnalysis):
        """(features, tallies): tallies has the unit counts per text, per level (unrecognised, unlisted, borrowed, bag)."""
        info = {tok: self._token_info(self.read_word(tok, status, readings)) for tok, (status, readings) in analysis.voikko.items()}
        rows, tallies = [], []
        for toks in analysis.tokens:
            row, tally = self._text_row(toks, info)
            rows.append(row)
            tallies.append(tally)
        return (pd.DataFrame(rows, index=analysis.df.index, columns=self.feature_names),
                pd.DataFrame(tallies, index=analysis.df.index))

    def _token_info(self, word):
        """One lemma-level unit and the stem-level units of a word. A unit is (kind, bin, log10 count);
        kind is bag / borrowed / unlisted / unrecognised / skipped."""
        if word.kind == "skipped":
            return {"lemma_unit": ("skipped", 0, 0.0), "stem_units": []}
        if word.kind == "unrecognised":
            return {"lemma_unit": ("unrecognised", 0, 0.0), "stem_units": [("unrecognised", 0, 0.0)]}
        reading, listed = word.reading, word.listed
        stems = [s.replace("=", "") for s in reading[2]]
        stems = [s for s in stems if s and not s[:1].isupper()] or [reading[0].lower()]
        units = []
        for s in stems:
            if s in self.bags["stem"]:
                units.append(("bag", self.bags["stem"][s], math.log10(self.freq["stem"][s])))
            else:
                units.append(("borrowed" if s in self.borrowed else "unlisted", 0, 0.0))
        if listed is not None:
            lemma_unit = ("bag", self.bags["lemma"][listed], math.log10(self.freq["lemma"][listed]))
        else:  # not in the lemma list: removed as English-looking, or unknown
            lemma_unit = ("borrowed" if all(k == "borrowed" for k, _, _ in units) else "unlisted", 0, 0.0)
        return {"lemma_unit": lemma_unit, "stem_units": units}

    def _text_row(self, tokens, info):
        tally = {lv: Counter() for lv in LEVELS}
        bag_counts = {lv: np.zeros(self.n_bags[lv] + 1) for lv in LEVELS}
        logfs = {lv: [] for lv in LEVELS}
        for tok in tokens:
            t = info[tok]
            for lv, units in (("stem", t["stem_units"]), ("lemma", [t["lemma_unit"]])):
                for kind, bag, logf in units:
                    tally[lv][kind] += 1
                    if kind == "bag":
                        bag_counts[lv][bag] += 1
                        logfs[lv].append(logf)
        row = {}
        for lv in LEVELS:
            counted = sum(v for k, v in tally[lv].items() if k != "skipped")
            share = lambda k: k / counted if counted else 0.0
            row[f"{lv}_OOV_coverage"] = share(tally[lv]["unrecognised"] + tally[lv]["unlisted"])
            row[f"{lv}_borrowed_coverage"] = share(tally[lv]["borrowed"])
            row.update({f"{lv}_bag_{b}_coverage": share(bag_counts[lv][b]) for b in range(1, self.n_bags[lv] + 1)})
            row[f"mean_log_{lv}_freq"] = float(np.mean(logfs[lv])) if logfs[lv] else 0.0
        tally_row = {"words": len(tokens), "skipped": tally["lemma"]["skipped"]}
        for lv in LEVELS:
            tally_row.update({f"{lv}_{k}": tally[lv][k] for k in ("unrecognised", "unlisted", "borrowed", "bag")})
        return row, tally_row
