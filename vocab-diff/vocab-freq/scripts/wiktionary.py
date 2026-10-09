"""English translations and etymology for stems from the Wiktionary Finnish dump (kaikki.org).

The dump is one JSON entry per line (4.6 GB, CC BY-SA). It is streamed ONCE (~20 min) and the entries of our stems are
saved in a slim local file, so changing the matching rules later never needs the download again:
  cleaned/05_wiktionary_entries.jsonl  one slim entry per line: word, senses (glosses, form_of / alt_of flags), etymology templates
The translation table is built from that file (seconds):
  cleaned/05_translations.tsv  (stem, english, english_all, etymology, en_source)
    english      single-word English translations of the FIRST meaning of the stem, joined by '|' (used for the edit score)
    english_all  single-word translations of all meanings (for reference only)
    etymology    borrowing / derivation tags, e.g. 'bor:sv der:la' (see english_borrowing.etymology_tags)
    en_source    the English source word when the etymology says borrowed from English (biisi <- piece), else empty
`ensure_translations` downloads only when the entries file is missing (or refetch=True).
"""
import json
import re
import urllib.request

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))  # common.py, text_common.py

from common import CLEANED
from english_borrowing import english_candidates, english_source, etymology_tags, first_sense_candidates

DUMP_URL = "https://kaikki.org/dictionary/Finnish/kaikki.org-dictionary-Finnish.jsonl"
ENTRIES = CLEANED / "05_wiktionary_entries.jsonl"
CACHE = CLEANED / "05_translations.tsv"
_WORD = re.compile(rb'"word": "((?:[^"\\]|\\.)*)"')


def _slim(entry):
    """Keep only what the matching needs."""
    senses = []
    for s in entry.get("senses", []):
        if "glosses" not in s:
            continue
        slim = {"glosses": s["glosses"]}
        for flag in ("form_of", "alt_of"):
            if flag in s:
                slim[flag] = True
        senses.append(slim)
    templates = [{"name": t.get("name"), "args": {k: v for k, v in t.get("args", {}).items() if k in ("1", "2", "3")}}
                 for t in entry.get("etymology_templates", []) if t.get("name") in ("bor", "lbor", "der", "inh", "slbor", "obor", "cog")]
    return {"word": entry["word"], "senses": senses, "etymology_templates": templates}


def fetch_entries(stems, dump=None, limit_mb=0):
    """Stream the dump and write the slim entries of the given stems to ENTRIES."""
    n, read = 0, 0
    with (open(dump, "rb") if dump else urllib.request.urlopen(DUMP_URL, timeout=120)) as fh, open(ENTRIES, "w", encoding="utf-8") as out:
        for line in fh:
            read += len(line)
            if limit_mb and read > limit_mb * 1_000_000:
                break
            m = _WORD.search(line)
            if not m or m.group(1).decode("utf-8") not in stems:
                continue
            out.write(json.dumps(_slim(json.loads(line)), ensure_ascii=False) + "\n")
            n += 1
            if n % 5000 == 0:
                print(f"\r{read / 1e9:.2f} GB read, {n:,} entries saved", end="", flush=True)
    print()


def build_translations():
    """Read the saved entries and write the translation table."""
    # stem -> [first-meaning english, all-meanings english, etymology tags, en_source, fallback tags, fallback en_source]
    # The etymology comes from the SAME entry as the first meaning (kerma has a cream entry and a physics-unit entry);
    # a stem with no usable first meaning falls back to its first entry's etymology.
    found = {}
    with open(ENTRIES, encoding="utf-8") as fh:
        for line in fh:
            entry = json.loads(line)
            rec = found.setdefault(entry["word"], [[], [], "", "", etymology_tags(entry), english_source(entry)])
            if not rec[0]:
                candidates = first_sense_candidates(entry)
                if candidates:
                    rec[0], rec[2], rec[3] = candidates, etymology_tags(entry), english_source(entry)
            rec[1] += [c for c in english_candidates(entry) if c not in rec[1]]
    found = {w: (r[0], r[1], r[2] if r[0] else r[4], r[3] if r[0] else r[5]) for w, r in found.items()}
    with open(CACHE, "w", encoding="utf-8") as dst:
        dst.write("stem\tenglish\tenglish_all\tetymology\ten_source\n")
        for stem in sorted(found):
            first, allm, tags, src = found[stem]
            dst.write(f"{stem}\t{'|'.join(first)}\t{'|'.join(allm)}\t{tags}\t{src}\n")


def ensure_translations(stems, refetch=False, dump=None, limit_mb=0):
    """Returns ({stem: (first-meaning english, etymology, en_source)}, n stems without an entry). Downloads the dump
    only when the entries file is missing (or refetch); the translation table is always rebuilt from the entries."""
    if refetch or not ENTRIES.exists():
        fetch_entries(stems, dump, limit_mb)
    build_translations()
    rows = {}
    with open(CACHE, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            stem, english, _, etymology, en_source = line.rstrip("\n").split("\t")
            rows[stem] = (english.split("|") if english else [], etymology, en_source)
    return rows, len(stems - rows.keys())
