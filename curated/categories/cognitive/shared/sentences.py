"""Sentence splitting for the text-only cognitive signals: a break after . ! ? … followed by whitespace, and at line breaks.
Abbreviations (esim., jne.) split too often; the parser-based signals use the parser's own sentences instead."""
import re

_BREAK = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    return [s for s in _BREAK.split(text.strip()) if s.strip()]
