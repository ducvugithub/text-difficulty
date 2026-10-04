"""English translations and etymology for stems from the Wiktionary Finnish dump (kaikki.org), cached in a tsv.

The dump is one JSON entry per line (4.6 GB, CC BY-SA). It is streamed once and only the entries of our stems are kept,
so the cache is small. The fetch is a ONE-TIME step (~20 min): `ensure_translations` reads the cache and only downloads
when the cache is missing or refetch=True.

Cache: cleaned/05_translations.tsv  (stem, english, etymology)
  english    single-word English glosses of the stem, joined by '|' (inflected / alternative forms skipped)
  etymology  borrowing / derivation tags, e.g. 'bor:sv der:la' (see english_borrowing.etymology_tags)
"""
import json
import re
import urllib.request

from common import CLEANED
from english_borrowing import english_candidates, etymology_tags

DUMP_URL = "https://kaikki.org/dictionary/Finnish/kaikki.org-dictionary-Finnish.jsonl"
CACHE = CLEANED / "05_translations.tsv"
_WORD = re.compile(rb'"word": "((?:[^"\\]|\\.)*)"')


def fetch(stems, dump=None, limit_mb=0):
    """Stream the dump and return {stem: (english list, etymology tags)} for the given stems."""
    found, read = {}, 0
    with (open(dump, "rb") if dump else urllib.request.urlopen(DUMP_URL, timeout=120)) as fh:
        for line in fh:
            read += len(line)
            if limit_mb and read > limit_mb * 1_000_000:
                break
            m = _WORD.search(line)
            if not m or m.group(1).decode("utf-8") not in stems:
                continue
            word = m.group(1).decode("utf-8")
            entry = json.loads(line)
            english, tags = found.get(word, ([], ""))
            english += [c for c in english_candidates(entry) if c not in english]
            found[word] = (english, tags or etymology_tags(entry))
            if len(found) % 5000 == 0:
                print(f"\r{read / 1e9:.2f} GB read, {len(found):,} stems found", end="", flush=True)
    print()
    return found


def ensure_translations(stems, refetch=False, dump=None, limit_mb=0):
    """Load the cache, downloading it first if it is missing (or refetch). Returns ({stem: (english, etymology)}, n stems not in the cache)."""
    if refetch or not CACHE.exists():
        found = fetch(stems, dump, limit_mb)
        with open(CACHE, "w", encoding="utf-8") as dst:
            dst.write("stem\tenglish\tetymology\n")
            for stem in sorted(found):
                english, tags = found[stem]
                dst.write(f"{stem}\t{'|'.join(english)}\t{tags}\n")
    rows = {}
    with open(CACHE, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            stem, english, etymology = line.rstrip("\n").split("\t")
            rows[stem] = (english.split("|") if english else [], etymology)
    return rows, len(stems - rows.keys())
