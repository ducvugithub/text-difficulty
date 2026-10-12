"""PrecomputedParseFeatures: the three syntax columns already in the data CSVs, computed by Revita's difficulty pipeline
(difficulty_api/inference_for_diff_regression.py get_sent_feat): average tree depth, average number of different POS tags per
sentence and average sentence length (tokens per parsed sentence). Only for the splits; no parser is run."""
import pandas as pd

from utils.base import TextAnalysis
from categories.cognitive.shared.cognitive_base import CognitiveFeatureConstruct

COLUMNS = {"average_tree_depth": "cognitive_parse_tree_depth", "average_num_pos": "cognitive_parse_distinct_pos",
           "average_sentence_length": "cognitive_parse_sentence_length"}


class PrecomputedParseFeatures(CognitiveFeatureConstruct):
    feature_names = list(COLUMNS.values())

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        return analysis.df[list(COLUMNS)].rename(columns=COLUMNS)
