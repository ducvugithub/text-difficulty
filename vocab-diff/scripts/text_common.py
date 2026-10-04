"""Helpers shared by the text-level scripts (07, 08). Needs pandas (see requirements.txt)."""
import math
from collections import Counter

import pandas as pd

from common import CLEANED, DATA, NAME_CLASSES, WORD_RE, decode_readings, run_voikko, select_readings

SPLIT_FILES = {"train": "Fi_train.csv", "valid": "Fi_valid.csv", "test": "Fi_test.csv"}
LIST_COLS = ["rank", "lemma", "class", "n_stems", "n_forms", "freq", "rarest_stem_freq"]
N_BAGS = 10
MAX_TOKEN_LEN = 45  # same cut-off as 01_normalize
CHUNK = 50_000


def load_split(split):
    return pd.read_csv(DATA / f"Source_ Finnish Difficulty texts with features - {SPLIT_FILES[split]}")


def token_counts(texts):
    """One Counter of word tokens per text."""
    return [Counter(WORD_RE.findall(str(t))) for t in texts]


def analyse_tokens(tokens):
    """token -> (status, [candidate lemmas]); overlong tokens count as unrecognised."""
    todo = sorted(t for t in tokens if len(t) <= MAX_TOKEN_LEN)
    result = {t: ("unrecognised", []) for t in tokens if len(t) > MAX_TOKEN_LEN}
    for i in range(0, len(todo), CHUNK):
        part = todo[i : i + CHUNK]
        for tok, field in zip(part, run_voikko(part)):
            status, readings = select_readings(decode_readings(field))
            result[tok] = (status, list(dict.fromkeys(base for base, _, _ in readings)))
    return result


def load_lemma_list(variant):
    """Final list as (ordered lemmas, lemma -> freq of `variant`), highest frequency first."""
    df = pd.read_csv(CLEANED / "lemma_freq.tsv", sep="\t", usecols=["lemma", variant], keep_default_na=False)
    df = df.sort_values(variant, ascending=False, kind="stable")
    return df["lemma"].tolist(), dict(zip(df["lemma"], df[variant]))


BAG_METHODS = ("uniform_rank_bin", "uniform_cumfreq_bin", "log10_freq_bin")

BAG_METHOD_DOCS = {
    "uniform_rank_bin": "Every bag has the same NUMBER of lemmas. Lemmas are ordered by frequency and cut into 10 equal "
    "groups (original Revita definition, but over the whole list).",
    "uniform_cumfreq_bin": "Every bag covers the same share of the TOTAL freq count (10% each). Lemmas are ordered from most "
    "to least frequent with a running total of freq; a new bag starts each time the running total passes another 10% of the "
    "grand total. The top bags hold few lemmas, the bottom bag holds millions.",
    "log10_freq_bin": "One bag per factor of 10 in frequency: bag = floor(log10(freq)) + 1 (freq 1-9 -> bag 1, 10-99 -> bag 2, "
    "...). The data spans ~10^0 to 10^8, so 9 bags are used.",
}


def assign_bags(lemmas_desc, freq, method, n_bags=N_BAGS):
    """lemma -> bag, 1 = rarest ... highest = most frequent. `lemmas_desc` is ordered by `freq` descending."""
    if method == "uniform_rank_bin":
        ascending = lemmas_desc[::-1]
        size = max(len(ascending) // n_bags, 1)  # remainder goes into the top bag (the original code emitted a stray bag 11)
        return {lemma: min(i // size + 1, n_bags) for i, lemma in enumerate(ascending)}
    if method == "uniform_cumfreq_bin":
        total = sum(freq[lemma] for lemma in lemmas_desc)
        bags, before = {}, 0
        for lemma in lemmas_desc:
            bags[lemma] = n_bags - min(int(before / total * n_bags), n_bags - 1)
            before += freq[lemma]
        return bags
    if method == "log10_freq_bin":
        return {lemma: min(int(math.log10(freq[lemma])) + 1, n_bags) for lemma in lemmas_desc}
    raise ValueError(f"unknown bag method {method!r}")


def best_lemma(candidates, freq):
    """Context-free disambiguation: the candidate with the highest list frequency, or None if none is listed."""
    listed = [c for c in candidates if c in freq]
    return max(listed, key=freq.__getitem__) if listed else None
