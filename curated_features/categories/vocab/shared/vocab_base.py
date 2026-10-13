"""VocabFeatureConstruct: the parent of the vocab signals (frequency bins, lexical features, ...).

It fixes the category ("vocab"), gives every signal a name, and holds what all vocab signals need first: the lemma and
the reading of each analysed word. A signal subclasses it and implements build().
"""
from collections import namedtuple

from curated_features.utils.base import FeatureConstruct
from curated_features.categories.vocab.shared.text_common import load_lemma_list, pick_reading

# kind: "skipped" (name / abbreviation), "unrecognised" (Voikko does not know the word) or "ok"
# lemma: lowercase lemma; reading: (base, class, stems, suffixes) or None; listed: the lemma if it is in the lemma list, else None
Word = namedtuple("Word", "kind lemma reading listed")


class VocabFeatureConstruct(FeatureConstruct):
    category = "vocab"
    signal = ""  # name of the signal, set by the subclass

    def __init__(self):
        _, self.lemma_freq = load_lemma_list("freq")

    def read_word(self, tok, status, readings) -> Word:
        """Lemma and reading of one analysed word (context-free: the candidate with the highest lemma-list frequency)."""
        if status in ("name", "abbrev"):
            return Word("skipped", readings[0][0].lower(), None, None)
        if status != "ok":
            return Word("unrecognised", tok.lower(), None, None)
        reading, listed = pick_reading(readings, self.lemma_freq)
        return Word("ok", reading[0].lower(), reading, listed)
