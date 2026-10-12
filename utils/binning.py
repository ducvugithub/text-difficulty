"""Frequency bins shared by the vocab and grammar frequency signals.

Items (lemmas, stems, grammar concepts, ...) ordered by frequency are cut into bins; bin 1 = most frequent, the highest
bin = rarest. Three ways to cut, see BAG_METHOD_DOCS.
"""
import math

N_BAGS = 10

BAG_METHODS = ("uniform_rank_bin", "uniform_cumfreq_bin", "log10_freq_bin")

BAG_METHOD_DOCS = {
    "uniform_rank_bin": "Every bag has the same NUMBER of lemmas. Lemmas are ordered by frequency and cut into 10 equal "
    "groups (the original Revita definition).",
    "uniform_cumfreq_bin": "Every bag covers the same share of the TOTAL freq count (10% each). Lemmas are ordered from most "
    "to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the "
    "grand total. The first bags hold few lemmas, the last bag holds most of them.",
    "log10_freq_bin": "One bag per factor of 10 in frequency, from the most frequent decade (bag 1) down to the rarest "
    "(bag = highest decade - floor(log10(freq)) + 1). The data spans ~10^0 to 10^8, so 9 bags are used.",
}


def assign_bags(items_desc, freq, method, n_bags=N_BAGS):
    """item -> bag, 1 = most frequent ... highest number = rarest. `items_desc` is ordered by `freq` descending."""
    if method == "uniform_rank_bin":
        size = max(len(items_desc) // n_bags, 1)  # the remainder goes into the last (rarest) bag
        return {item: min(i // size + 1, n_bags) for i, item in enumerate(items_desc)}
    if method == "uniform_cumfreq_bin":
        total = sum(freq[item] for item in items_desc)
        bags, before = {}, 0
        for item in items_desc:
            bags[item] = min(int(before / total * n_bags) + 1, n_bags)
            before += freq[item]
        return bags
    if method == "log10_freq_bin":
        top = max(int(math.log10(freq[item])) for item in items_desc)
        return {item: min(top - int(math.log10(freq[item])) + 1, n_bags) for item in items_desc}
    raise ValueError(f"unknown bag method {method!r}")
