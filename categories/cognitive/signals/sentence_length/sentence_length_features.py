"""SentenceLengthFeatures: sentence length in words, from a plain sentence split (no parser needed).

cognitive_sent_n_sentences, cognitive_sent_mean_len, cognitive_sent_max_len, cognitive_sent_std_len
"""
import numpy as np
import pandas as pd

from utils.base import TextAnalysis
from categories.cognitive.shared.cognitive_base import CognitiveFeatureConstruct
from categories.vocab.shared.common import WORD_RE


class SentenceLengthFeatures(CognitiveFeatureConstruct):
    feature_names = ["cognitive_sent_n_sentences", "cognitive_sent_mean_len", "cognitive_sent_max_len", "cognitive_sent_std_len"]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        rows = []
        for sentences in analysis.sentences:
            lengths = np.array([len(WORD_RE.findall(s)) for s in sentences] or [0], float)
            rows.append([len(sentences), lengths.mean(), lengths.max(), lengths.std()])
        return pd.DataFrame(rows, index=analysis.df.index, columns=self.feature_names)
