"""RarityFeatures: how rare the grammar of a text is, from how often each item occurs in Revita's Finnish stories (the
reference). The grammar counterpart of the vocab frequency bins: an item plays the role of a word.

Each occurrence is placed in a bin by the reference count of its item (bin 1 = most common ... highest = rarest; the bin
types of curated/utils/binning.py). Per text, shares are over all counted occurrences:
  grammar_{kind}_rarity_bag_{k}   share of occurrences in bin k
  grammar_{kind}_rarity_unseen    share of items that never occur in the reference (the grammar OOV)
  grammar_{kind}_mean_idf       mean log10(N / stories containing the item), over the seen items; N = the most widespread item's story count
"""
import numpy as np
import pandas as pd

from curated.utils.base import TextAnalysis
from curated.utils.binning import BAG_METHODS, assign_bags
from curated.categories.grammar.shared import grammar_items
from curated.categories.grammar.shared.grammar_base import GrammarFeatureConstruct


class RarityFeatures(GrammarFeatureConstruct):
    def __init__(self, source: str = "columns", bin_method: str = "log10_freq_bin", n_bins: int = 7):
        super().__init__(source)
        if bin_method not in BAG_METHODS:
            raise ValueError(f"bin_method must be one of {BAG_METHODS}")
        ref = grammar_items.reference(self.kind)
        self.bag = pd.Series(assign_bags(list(ref.index), ref["count"].to_dict(), bin_method, n_bins))
        self.idf = np.log10(ref["n_stories"].max() / ref["n_stories"])
        self.bag_columns = [f"grammar_{self.kind}_rarity_bag_{k}" for k in range(1, int(self.bag.max()) + 1)]
        self.feature_names = [*self.bag_columns, f"grammar_{self.kind}_rarity_unseen", f"grammar_{self.kind}_mean_idf"]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        counts = self.counts(analysis)
        shares = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        bags = shares.columns.map(self.bag)  # NaN: the item is not in the reference
        by_bag = shares.T.groupby(bags).sum().T.reindex(columns=range(1, len(self.bag_columns) + 1), fill_value=0.0)
        out = pd.DataFrame(by_bag.to_numpy(), index=shares.index, columns=self.bag_columns)
        seen = shares.loc[:, ~bags.isna()]
        out[f"grammar_{self.kind}_rarity_unseen"] = shares.sum(axis=1) - seen.sum(axis=1)
        idf = self.idf.reindex(seen.columns)
        out[f"grammar_{self.kind}_mean_idf"] = (seen @ idf).div(seen.sum(axis=1).replace(0, np.nan)).fillna(0.0)
        return out
