"""Helpers shared by the text-level scripts (07, 08). Needs pandas (see requirements.txt)."""
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


def assign_bags(lemmas_desc, top_n, n_bags=N_BAGS):
    """Same definition as the original Revita features: equal-count bins over the frequency-ascending list,
    bag 1 = rarest ... bag n_bags = most frequent. (The original code could emit a stray bag 11 for the
    remainder; here the remainder goes into the top bag.)"""
    kept = lemmas_desc[:top_n] if top_n else lemmas_desc
    ascending = kept[::-1]
    size = max(len(ascending) // n_bags, 1)
    return {lemma: min(i // size + 1, n_bags) for i, lemma in enumerate(ascending)}


def best_lemma(candidates, freq):
    """Context-free disambiguation: the candidate with the highest list frequency, or None if none is listed."""
    listed = [c for c in candidates if c in freq]
    return max(listed, key=freq.__getitem__) if listed else None
