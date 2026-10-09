"""Step 3: collapse surface forms to lemmas.

Per surface form: drop proper-name / abbreviation readings when a common-word reading exists; forms with only
name (or only abbreviation) readings are dropped; forms Voikko does not recognise (typos, English, junk) are dropped.
Lemmas are lowercase: readings of one form that differ only by case are one lemma, counted once, and forms of the same
lemma add up (names are dropped first, so a capitalised leftover such as Pirkanmaa just becomes pirkanmaa).
Ambiguous forms (e.g. 'sinä' = se/sinä) count in full for every distinct lemma (so lemma totals can exceed the corpus size).
Per lemma `freq` = all its inflected forms added up.

Input : cleaned/02_analysis.tsv
Output: cleaned/03_lemmas.tsv  (lemma, class, stems, n_forms, freq)
        cleaned/03_unrecognised.tsv (top 50k, for review), reports/03_merge_lemmas.md
"""
import os
from collections import defaultdict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))  # common.py, text_common.py

from common import CLEANED, decode_readings, ensure_dirs, select_readings, write_report

ENGLISH_DICT = "/usr/share/dict/words"
TOP_UNRECOGNISED = 50_000


def load_english():
    if not os.path.exists(ENGLISH_DICT):
        return set()
    with open(ENGLISH_DICT, encoding="utf-8", errors="replace") as fh:
        return {w.strip().lower() for w in fh if len(w.strip()) >= 3}


def main():
    ensure_dirs()
    english = load_english()
    # lemma -> [class, stems, n_forms, freq]
    lemmas = {}
    dropped = defaultdict(lambda: [0, 0, []])  # status -> [rows, tokens, examples]
    unrec_written = 0
    english_rows = english_tokens = 0
    kept_rows = kept_tokens = 0

    with open(CLEANED / "02_analysis.tsv", encoding="utf-8") as src, open(
        CLEANED / "03_unrecognised.tsv", "w", encoding="utf-8"
    ) as unrec:
        for line in src:
            count_s, word, field = line.rstrip("\n").split("\t")
            count = int(count_s)
            status, readings = select_readings(decode_readings(field))
            if status != "ok":
                d = dropped[status]
                d[0] += 1
                d[1] += count
                if len(d[2]) < 15:
                    d[2].append(f"{word} ({count})")
                if status == "unrecognised":
                    is_en = word.lower() in english
                    english_rows += is_en
                    english_tokens += count * is_en
                    if unrec_written < TOP_UNRECOGNISED:
                        unrec.write(f"{count}\t{word}\t{'en' if is_en else ''}\n")
                        unrec_written += 1
                continue

            kept_rows += 1
            kept_tokens += count
            distinct = {}  # lowercase lemma -> (class, stems, reading was already lowercase)
            for base, cls, stems in readings:
                key = base.lower()  # readings that differ only by case (lappeenranta / Lappeenranta) are one lemma, counted once
                if key not in distinct or (base == key and not distinct[key][2]):
                    distinct[key] = (cls, stems, base == key)
            for base, (cls, stems, _) in distinct.items():  # full count for every distinct lemma
                rec = lemmas.get(base)
                if rec is None:
                    lemmas[base] = [cls, stems, 1, count]
                else:
                    rec[2] += 1
                    rec[3] += count

    out_path = CLEANED / "03_lemmas.tsv"
    with open(out_path, "w", encoding="utf-8") as dst:
        for lemma, (cls, stems, n_forms, freq) in sorted(lemmas.items(), key=lambda kv: -kv[1][3]):
            dst.write(f"{lemma}\t{cls}\t{'+'.join(stems)}\t{n_forms}\t{freq}\n")

    lines = [
        "# 03 merge lemmas",
        f"- surface forms kept: {kept_rows:,} (total count {kept_tokens:,}) -> {len(lemmas):,} lemmas ({out_path.name})",
        "- ambiguous forms count in full for every distinct lemma",
        "",
        "Columns of 03_lemmas.tsv: `lemma` dictionary form; `class` Voikko word class; `stems` stems it is built from "
        "(`+`-joined); `n_forms` inflected forms merged into the lemma; `freq` all those forms' counts added up.",
        "",
        "| dropped | rows | total count | most frequent examples |",
        "|---|---:|---:|---|",
    ]
    for status, (rows, tokens, examples) in sorted(dropped.items(), key=lambda kv: -kv[1][1]):
        lines.append(f"| {status} | {rows:,} | {tokens:,} | {', '.join(examples)} |")
    if english:
        lines += [
            "",
            "## English check on unrecognised forms",
            f"- unrecognised forms found in {ENGLISH_DICT} (len>=3): {english_rows:,} rows, total count {english_tokens:,}",
            "- English words are already removed by Voikko recognition; recognised English-looking lemmas (sauna, radio...) "
            "are real Finnish loanwords and are deliberately kept.",
            "- review 03_unrecognised.tsv (column 3 = 'en' if in the English dictionary) for Finnish words Voikko misses.",
        ]
    write_report("03_merge_lemmas.md", lines)


if __name__ == "__main__":
    main()
