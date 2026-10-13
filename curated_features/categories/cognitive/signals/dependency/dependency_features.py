"""DependencyFeatures: sentence structure from the dependency parse of the Turku parser (curated_features/categories/cognitive/shared/parser_client.py).

Per text, over the parser's sentences:
  cognitive_dep_mean_tree_depth       mean over sentences of the depth of the dependency tree (the deepest chain to the root)
  cognitive_dep_max_tree_depth        the deepest tree in the text
  cognitive_dep_mean_distance         mean dependency distance |position - head position| (working-memory load, Gibson 1998)
  cognitive_dep_max_distance          the longest dependency in the text
  cognitive_dep_clauses_per_sentence  finite verbs per sentence (one finite verb ~ one clause)
  cognitive_dep_subordinate_per_sentence  subordinate clauses per sentence (ccomp, csubj, advcl, acl and acl:relcl dependents)
  cognitive_dep_mean_distinct_pos     mean number of different part-of-speech tags in a sentence (Revita's average_num_pos)
"""
import numpy as np
import pandas as pd

from curated_features.utils.base import TextAnalysis
from curated_features.categories.cognitive.shared.cognitive_base import CognitiveFeatureConstruct

SUBORDINATE = {"ccomp", "csubj", "advcl", "acl"}


def tree_depth(sentence: list[dict]) -> int:
    head = {t["id"]: t["head"] for t in sentence}
    depth = 0
    for t in sentence:
        steps, node = 0, t["id"]
        while node != 0 and steps <= len(sentence):  # the step limit guards against a cyclic parse
            node, steps = head.get(node, 0), steps + 1
        depth = max(depth, steps)
    return depth


class DependencyFeatures(CognitiveFeatureConstruct):
    feature_names = ["cognitive_dep_mean_tree_depth", "cognitive_dep_max_tree_depth", "cognitive_dep_mean_distance",
                     "cognitive_dep_max_distance", "cognitive_dep_clauses_per_sentence", "cognitive_dep_subordinate_per_sentence",
                     "cognitive_dep_mean_distinct_pos"]

    def build(self, analysis: TextAnalysis) -> pd.DataFrame:
        rows = []
        for sentences in analysis.parse:
            if not sentences:
                rows.append([0.0] * len(self.feature_names))
                continue
            depths = [tree_depth(s) for s in sentences]
            dists = [abs(t["id"] - t["head"]) for s in sentences for t in s if t["head"] != 0]
            finite = sum("VerbForm=Fin" in t["feats"] for s in sentences for t in s)
            subordinate = sum(t["deprel"].split(":")[0] in SUBORDINATE for s in sentences for t in s)
            rows.append([np.mean(depths), max(depths), np.mean(dists) if dists else 0.0, max(dists, default=0),
                         finite / len(sentences), subordinate / len(sentences), np.mean([len({t["upos"] for t in s}) for s in sentences])])
        return pd.DataFrame(rows, index=analysis.df.index, columns=self.feature_names)
