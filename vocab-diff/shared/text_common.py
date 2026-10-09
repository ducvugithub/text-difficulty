"""Helpers shared by the text-level scripts (07, 08). Needs pandas (see requirements.txt)."""
import math
import sys
from functools import lru_cache
from collections import Counter
from pathlib import Path

import pandas as pd

from common import CLEANED, NAME_CLASSES, WORD_RE, decode_readings, run_voikko, select_readings

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dataset import SPLIT_FILES, load_split  # noqa: E402,F401  (re-exported for the scripts)

LIST_COLS = ["rank", "lemma", "class", "n_stems", "n_forms", "freq"]
N_BAGS = 10
MAX_TOKEN_LEN = 45  # same cut-off as 01_normalize
CHUNK = 50_000


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


def analyse_tokens_full(tokens):
    """token -> (status, readings) with readings (base, cls, stems, suffixes).
    status 'ok' keeps only the common-word readings; names/abbreviations keep all their readings;
    unrecognised tokens have none."""
    todo = sorted(t for t in tokens if len(t) <= MAX_TOKEN_LEN)
    result = {t: ("unrecognised", []) for t in tokens if len(t) > MAX_TOKEN_LEN}
    for i in range(0, len(todo), CHUNK):
        part = todo[i : i + CHUNK]
        for tok, field in zip(part, run_voikko(part)):
            readings = decode_readings(field, full=True)
            status, kept = select_readings(readings)
            result[tok] = (status, kept if status == "ok" else readings)
    return result


@lru_cache(maxsize=None)
def load_stem_list():
    """Final stem list as (ordered stems, stem -> full count), highest count first."""
    df = pd.read_csv(CLEANED / "05_stem_freq.tsv", sep="\t", usecols=["stem", "freq"], keep_default_na=False)
    return df["stem"].tolist(), dict(zip(df["stem"], df["freq"]))


@lru_cache(maxsize=None)
def load_borrowed_stems():
    """Stems tagged English-looking in step 5 (removed from the stem list)."""
    df = pd.read_csv(CLEANED / "05_stem_borrowing.tsv", sep="\t", usecols=["stem", "borrowed"], keep_default_na=False)
    return set(df.loc[df["borrowed"] == 1, "stem"])


@lru_cache(maxsize=None)
def load_lemma_list(variant):
    """Final list as (ordered lemmas, lemma -> freq of `variant`), highest frequency first."""
    df = pd.read_csv(CLEANED / "05_lemma_freq.tsv", sep="\t", usecols=["lemma", variant], keep_default_na=False)
    df = df.sort_values(variant, ascending=False, kind="stable")
    return df["lemma"].tolist(), dict(zip(df["lemma"], df[variant]))


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


def pick_reading(readings, lemma_freq):
    """(reading, listed lemma or None) of an analysed word: the reading whose lemma has the highest list frequency
    (context-free); `listed` is None when no candidate lemma is in the list, and the first reading is used."""
    listed = best_lemma([r[0].lower() for r in readings], lemma_freq)
    return next((r for r in readings if r[0].lower() == listed), readings[0]), listed


def best_lemma(candidates, freq):
    """Context-free disambiguation: the candidate with the highest list frequency, or None if none is listed."""
    listed = [c for c in candidates if c in freq]
    return max(listed, key=freq.__getitem__) if listed else None
