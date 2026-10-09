"""Step 5: drop English-looking (borrowed) stems and lemmas, then rank the final stem and lemma lists.

Stem tagging: a stem is English-looking when
  - its edit score to the closest English translation of its FIRST meaning is at most MAX_NORM (35) of the longer word's
    length (english_borrowing.py: normal edits cost 1, the STANDARD modifications Finnish applies when it borrows a word cost 0.2), or
  - its Wiktionary etymology says it was borrowed from English (bor:en). The audit then shows the English source word
    (kämppä <- camp), with the score against that word, not against an unrelated translation,
  unless the etymology says it is inherited from Proto-Finnic / Uralic (muu, moni, nimi, sama look English but are native).
  Stems under 3 characters, stems without a Wiktionary entry or English gloss, and capitalised stems (names) are not judged.
Lemma rule (--lemma-rule): a lemma is dropped when all of its stems are tagged (default), when any is, or never.
The English translations come from a one-time Wiktionary fetch cached in cleaned/05_translations.tsv (wiktionary.py).

Input : cleaned/04_lemmas_stem.tsv, cleaned/04_stems.tsv, cleaned/03_lemmas.tsv, cleaned/05_translations.tsv (fetched if missing)
Output: cleaned/05_lemma_freq.tsv  (rank, lemma, class, n_stems, n_forms, freq)       final lemma list
        cleaned/05_stem_freq.tsv   (rank, stem, freq, standalone_freq, n_lemmas, n_compounds)            final stem list
        cleaned/05_stem_borrowing.tsv (stem, freq, english, english_from, edit_score, norm, borrowed, reason, etymology)  audit of every stem that has an English gloss or is tagged, tagged ones first (by freq)
        reports/05_rank_and_filter.md
--keep-borrowed writes the same lists without removing anything (for comparison).
"""
import argparse

from common import CLEANED, ensure_dirs, write_report
from english_borrowing import MAX_NORM, MIN_LENGTH, edit_score, looks_english, norm_score
from wiktionary import ensure_translations

LEMMA_COLS = ["lemma", "class", "n_stems", "n_forms", "freq"]
# team sheet: Finnish, English, the sheet's edit score and norm
SHEET_BORROWED = [("banana", "banana", 0, 0.0), ("presidentti", "president", 0.4, 3.6), ("vitamiini", "vitamin", 0.4, 4.4),
                  ("fysiikka", "physics", 0.4, 5.0), ("koreografia", "choreography", 0.6, 5.5), ("psykologia", "psychology", 0.4, 4.0),
                  ("konferenssi", "conference", 0.6, 5.5), ("meloni", "melon", 0.2, 3.3), ("tee", "tea", 1, 33.3), ("bussi", "bus", 0.4, 8.0),
                  ("kahvi", "coffee", 3.4, 68.0), ("matematiikka", "mathematics", 0.4, 3.3), ("strategia", "strategy", 0.2, 2.2),
                  ("demokratia", "democracy", 1.4, 14.0), ("sohva", "sofa", 0.2, 4.0), ("innovaatio", "innovation", 1.2, 12.0),
                  ("metalli", "metal", 2, 28.6), ("linkki", "link", 0.4, 6.7), ("flunssa", "flu", 4, 57.1),
                  ("flunssa", "influenza", 3.2, 35.6), ("moottori", "motor", 0.6, 7.5), ("motivoida", "motivate", 3.2, 35.6),
                  ("rekisteröidä", "register", 0.4, 3.3), ("tsekata", "check", 1.6, 22.9)]
SHEET_NATIVE = [("tatti", "bolete", 6, 120.0), ("käsi", "hand", 4, 100.0), ("haluta", "want", 5, 83.3), ("mennä", "go", 5, 100.0),
                ("tutkimus", "research", 8, 100.0), ("jalka", "leg", 4, 80.0), ("haaste", "challenge", 7, 77.8),
                ("neuvosto", "council", 7, 87.5), ("siellä", "there", 5, 83.3), ("tieto", "data", 3.2, 64.0), ("sivu", "side", 2, 50.0)]
SHEET_VERBS = {"rekisteröidä", "motivoida", "tsekata"}  # sheet pairs whose English side is a verb: the verb-ending rules apply
# inherited from Proto-Finnic, Proto-Finno-Permic, Proto-Uralic, Proto-Finno-Ugric
NATIVE_ETYMOLOGY = {"inh:urj-fin-pro", "inh:urj-fpr-pro", "inh:urj-pro", "inh:fiu-pro"}


def tag_stems(translations):
    """stem -> dict(english, edit_score, norm, etymology, borrowed, reason) for stems with a Wiktionary entry."""
    tags = {}
    for stem, (english, etymology, en_source) in translations.items():
        close, match = looks_english(stem, english)
        native = bool(NATIVE_ETYMOLOGY & set(etymology.split()))
        bor_en = any(t in ("bor:en", "lbor:en") for t in etymology.split())
        hit = close or bor_en
        english_from = "translation"
        if not close and bor_en and en_source:  # tagged by the etymology: show and score the English word it came from
            match, english_from = (en_source, edit_score(en_source, stem), norm_score(en_source, stem)), "etymology"
        tags[stem] = {
            "english": match[0] if match else "", "edit_score": match[1] if match else "", "norm": match[2] if match else "",
            "english_from": english_from, "etymology": etymology, "borrowed": int(hit and not native),
            "reason": "native etymology" if hit and native else "edit score" if close else ("bor:en" if bor_en else ""),
        }
    return tags


def stems_of(lemma, stem_field):
    return [s.replace("=", "") for s in stem_field.split("+")] if stem_field else [lemma]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lemma-rule", default="all", choices=["all", "any", "none"])
    ap.add_argument("--min-freq", type=float, default=0, help="drop lemmas below this freq (default 0 = keep all)")
    ap.add_argument("--keep-borrowed", action="store_true", help="rank only, remove nothing")
    ap.add_argument("--refetch", action="store_true", help="download the Wiktionary translations again")
    args = ap.parse_args()
    ensure_dirs()

    # lemma stems from 03 (lemma, class, stems, n_forms, freq); lowercase stems are the vocabulary stems
    lemma_stems = {}
    with open(CLEANED / "03_lemmas.tsv", encoding="utf-8") as fh:
        for line in fh:
            lemma, _, stem_field, *_ = line.split("\t", 3)
            lemma_stems[lemma] = stems_of(lemma, stem_field)
    stems = {s for ss in lemma_stems.values() for s in ss if not s[:1].isupper()}
    translations, n_uncached = ensure_translations(stems, refetch=args.refetch)
    translations = {s: v for s, v in translations.items() if s in stems}

    tags = tag_stems(translations)
    borrowed = set() if args.keep_borrowed else {s for s, t in tags.items() if t["borrowed"]}

    with open(CLEANED / "04_stems.tsv", encoding="utf-8") as fh:
        next(fh)
        stem_rows = [line.rstrip("\n").split("\t") for line in fh]
    stem_freq = {r[0]: int(r[1]) for r in stem_rows}
    with open(CLEANED / "05_stem_borrowing.tsv", "w", encoding="utf-8") as fh:  # stems with an English translation
        fh.write("stem\tfreq\tenglish\tenglish_from\tedit_score\tnorm\tborrowed\treason\tetymology\n")
        for stem, t in sorted(((s, t) for s, t in tags.items() if t["english"] or t["borrowed"]), key=lambda x: (-x[1]["borrowed"], -stem_freq.get(x[0], 0))):
            fh.write(f"{stem}\t{stem_freq.get(stem, '')}\t{t['english']}\t{t['english_from']}\t{t['edit_score'] if t['edit_score'] == '' else format(t['edit_score'], '.2f')}\t{t['norm'] if t['norm'] == '' else format(t['norm'], '.1f')}\t{t['borrowed']}\t{t['reason']}\t{t['etymology']}\n")

    agg = {"all": all, "any": any}.get(args.lemma_rule)
    drop_lemmas = {l for l, ss in lemma_stems.items() if agg and borrowed and agg(s in borrowed for s in ss)}

    # final lemma list
    with open(CLEANED / "04_lemmas_stem.tsv", encoding="utf-8") as fh:
        rows = [line.rstrip("\n").split("\t") for line in fh]
    key = LEMMA_COLS.index("freq")
    total_freq = sum(int(r[4]) for r in rows)
    removed = [r for r in rows if r[0] in drop_lemmas]
    kept = sorted((r for r in rows if r[0] not in drop_lemmas and float(r[key]) >= args.min_freq), key=lambda r: -float(r[key]))
    with open(CLEANED / "05_lemma_freq.tsv", "w", encoding="utf-8") as dst:
        dst.write("rank\t" + "\t".join(LEMMA_COLS) + "\n")
        for rank, row in enumerate(kept, 1):
            dst.write(f"{rank}\t" + "\t".join(row) + "\n")

    # final stem list
    stem_kept = sorted((r for r in stem_rows if r[0] not in borrowed), key=lambda r: -int(r[1]))
    with open(CLEANED / "05_stem_freq.tsv", "w", encoding="utf-8") as dst:
        dst.write("rank\tstem\tfreq\tstandalone_freq\tn_lemmas\tn_compounds\n")
        for rank, row in enumerate(stem_kept, 1):
            dst.write(f"{rank}\t" + "\t".join(row) + "\n")

    n_gloss = sum(1 for t in tags.values() if t["english"] and t["english_from"] == "translation")
    n_tagged = sum(t["borrowed"] for t in tags.values())
    n_by_score = sum(1 for t in tags.values() if t["reason"] == "edit score")
    n_by_etymology = sum(1 for t in tags.values() if t["reason"] == "bor:en")
    n_spared = sum(1 for t in tags.values() if t["reason"] == "native etymology")
    n_minfreq = len(rows) - len(removed) - len(kept)
    border = sorted(((t["norm"], s, t) for s, t in tags.items() if t["norm"] != "" and 25 <= t["norm"] <= 50), key=lambda x: x[0])
    step = max(len(border) // 60, 1)
    lines = [
        "# 05 rank and filter",
        f"- English-looking rule: edit score / longer word length x 100 <= {MAX_NORM:g} (stems of {MIN_LENGTH}+ characters), or the etymology says `bor:en`; not tagged when the etymology says inherited from Proto-Finnic / Uralic"
        + ("; --keep-borrowed: nothing removed" if args.keep_borrowed else ""),
        "",
        "Stems:",
        "",
        "| step | stems |",
        "|---|---:|",
        f"| all lowercase stems | {len(stems):,} |",
        f"| found in the dictionary (Wiktionary) | {len(tags):,} ({n_uncached:,} not found: cannot be judged, they stay) |",
        f"| with an English translation | {n_gloss:,} (the others cannot be judged, they stay) |",
        f"| tagged as English-looking | {n_tagged:,} ({n_by_score:,} by edit score, {n_by_etymology:,} only by etymology `bor:en`) |",
        f"| not tagged because the etymology says native | {n_spared:,} |",
        f"| **in the final list** (`05_stem_freq.tsv`) | **{len(stem_kept):,}** |",
        "",
        "Lemmas (a lemma is removed when all of its stems are tagged):",
        "",
        "| step | lemmas |",
        "|---|---:|",
        f"| before | {len(rows):,} |",
        f"| removed as English-looking | {len(removed):,} ({100 * sum(int(r[4]) for r in removed) / total_freq:.2f}% of all lemma counts) |",
        f"| removed by --min-freq {args.min_freq:g} | {n_minfreq:,} |",
        f"| **in the final list** (`05_lemma_freq.tsv`, sorted by freq) | **{len(kept):,}** |",
        "",
        "Columns of `05_lemma_freq.tsv`:",
        "- `rank`: position (1 = most frequent)",
        "- `lemma`",
        "- `class`: Voikko word class",
        "- `n_stems`: number of stems",
        "- `n_forms`: forms merged into the lemma",
        "- `freq`: all forms added up",
        "",
        "Columns of `05_stem_freq.tsv`:",
        "- `rank`: position by `freq`",
        "- `stem`",
        "- `freq`: full count (the `freq` of every lemma containing the stem, added up)",
        "- `standalone_freq`: the lemma frequency of the stem as its own word (empty if it never occurs alone)",
        "- `n_lemmas`: lemmas containing it",
        "- `n_compounds`: compounds containing it",
        "",
        "Columns of `05_stem_borrowing.tsv` (stems with an English gloss, plus tagged ones; tagged stems first, most frequent first):",
        "- `stem`",
        "- `freq`: full count of the stem",
        "- `english`: closest English translation of the stem's first meaning",
        "- `edit_score`: weighted edit distance",
        "- `norm`: edit score / longer word length x 100",
        "- `borrowed`: 1 = tagged",
        "- `english_from`: `translation` (first meaning) or `etymology` (the English word the stem was borrowed from, for stems tagged only by `bor:en`)",
        "- `reason`: `edit score`; `bor:en` (the etymology says borrowed from English); `native etymology` (a rule fired, but the stem is inherited from Proto-Finnic, so not tagged)",
        "- `etymology`: Wiktionary tags (`bor:sv` borrowed from Swedish, `der:la` derived from Latin, `inh:urj-fin-pro` inherited from Proto-Finnic)",
        "",
        f"## Calibration: the team sheet pairs (tagged when norm <= {MAX_NORM:g})",
        "| Finnish | English | sheet edit score | our edit score | sheet norm | our norm | tagged |", "|---|---|---:|---:|---:|---:|---|",
    ]
    for group in (SHEET_BORROWED, SHEET_NATIVE):
        for f, e, se, sn in group:
            verb = f in SHEET_VERBS
            n = norm_score(e, f, verb)
            lines.append(f"| {f} | {e} | {se:g} | {edit_score(e, f, verb):.1f} | {sn:g} | {n:.1f} | {'yes' if n <= MAX_NORM else 'no'} |")
    lines += ["", "## Most frequent removed lemmas", "", ", ".join(f"{r[0]} ({int(r[4]):,})" for r in sorted(removed, key=lambda r: -int(r[4]))[:40])]
    lines += ["", "## Close to the threshold (norm 25 to 50; check by eye)", "", "| stem | english | norm | tagged |", "|---|---|---:|---|"]
    lines += [f"| {s} | {t['english']} | {n:.1f} | {'yes' if t['borrowed'] else 'no'} |" for n, s, t in border[::step]]
    write_report("05_rank_and_filter.md", lines)


if __name__ == "__main__":
    main()
