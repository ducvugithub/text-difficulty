"""TopicLevelFeatures: share of a text's Revita syllabus-topic occurrences at each CEFR level (syllabus/fin_syllabus.json). The sublevel is dropped (A1.3 -> A1)."""
from categories.grammar.shared.level_features import LevelFeatures


class TopicLevelFeatures(LevelFeatures):
    kind = "topic"
