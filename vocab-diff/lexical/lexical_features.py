"""LexicalFeatures: the word-form signal of a text (signal 2 of the vocab category). Needs only Voikko and the lemma list.

  lexical diversity     n_unique_lemmas, ttr_lemma_200 (distinct lemmas among the first 200 / 200)
  word form             avg_word_length, long_word_ratio (10 or more characters)
  compounding           compound_ratio, avg_compound_parts, n_compound_tokens (compounds = readings with 2 or more stems)
  derivation            deriv_llinen_ratio, deriv_ton_ratio (Voikko suffix markers),
                        deriv_minen_ratio, deriv_sti_ratio (HEURISTICS: Voikko treats -minen / -sti as inflection)
Content words = nouns, adjectives, verbs, adverbs; names, abbreviations and unrecognised words are not content words.
Definitions: docs/features.md. The reading of an ambiguous word is the Voikko candidate whose lemma has the highest
lemma-list frequency (context-free).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vocab-diff" / "shared"))
from base import FeatureConstruct, TextAnalysis  # noqa: E402
from text_common import load_lemma_list, pick_reading  # noqa: E402

CONTENT_CLASSES = {"nimisana", "laatusana", "teonsana", "seikkasana", "nimisana_laatusana"}
LONG_WORD = 10
TTR_WINDOW = 200
MINEN_ENDINGS = ("minen", "misen", "mista", "mistä", "missa", "missä", "misessa", "misessä", "misesta", "misestä",
                 "miseen", "misella", "misellä", "miselta", "miseltä", "miselle", "misena", "miseksi", "misetta", "misettä",
                 "misten", "misia", "misiä", "misissa", "misissä", "misista", "misistä", "misiin", "misilla", "misillä")
FEATURES = ["n_unique_lemmas", "ttr_lemma_200", "avg_word_length", "long_word_ratio", "compound_ratio",
            "avg_compound_parts", "n_compound_tokens", "deriv_llinen_ratio", "deriv_ton_ratio",
            "deriv_minen_ratio", "deriv_sti_ratio"]


class LexicalFeatures(FeatureConstruct):
    category = "vocab"
    signal = "lexical"
    feature_names = FEATURES

    def __init__(self):
        _, self.lemma_freq = load_lemma_list("freq")

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        info = {tok: self._token_info(tok, status, readings) for tok, (status, readings) in analysis.voikko.items()}
        rows = [self._text_row(toks, info) for toks in analysis.tokens]
        return pd.DataFrame(rows, index=analysis.df.index, columns=self.feature_names)

    def _token_info(self, tok, status, readings):
        """(lemma, reading or None) of a token; names and unrecognised words have no reading."""
        if status in ("name", "abbrev"):
            return readings[0][0].lower(), None
        if status != "ok":
            return tok.lower(), None
        reading, _ = pick_reading(readings, self.lemma_freq)
        return reading[0].lower(), reading

    def _text_row(self, tokens, info):
        lemmas, content = [], []
        for tok in tokens:
            lemma, reading = info[tok]
            lemmas.append(lemma)
            if reading is not None and reading[1] in CONTENT_CLASSES:
                content.append((tok.lower(), reading))
        n_content = len(content)
        window = lemmas[:TTR_WINDOW]
        compounds = [r for _, r in content if len(r[2]) >= 2]
        ratio = lambda k: k / n_content if n_content else 0.0
        llinen = sum(any(s.endswith(">+nen") and s.startswith("lli") for s in r[3]) for _, r in content)
        ton = sum(any(s.endswith(">+ton") for s in r[3]) for _, r in content)
        minen = sum(r[1] == "teonsana" and tok.endswith(MINEN_ENDINGS) for tok, r in content)
        sti = sum(r[1] == "laatusana" and tok.endswith("sti") and r[0].lower() != tok and not r[0].endswith("sti") for tok, r in content)
        return {
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
        }
