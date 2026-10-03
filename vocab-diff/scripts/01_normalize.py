"""Step 1: drop tokens that cannot be words (numbers, symbols, URLs, fragments, absurdly long).

Input : data/finnish_vocab.txt          ('count word' per line, raw surface forms)
Output: cleaned/01_normalized.tsv       ('count<TAB>word'), reports/01_normalize.md
"""
import argparse
from collections import defaultdict

from common import CLEANED, RAW_VOCAB, WORD_RE, ensure_dirs, parse_counted_line, write_report

MAX_LEN = 45  # longest legitimate Finnish compounds are ~40 chars; beyond this it is junk


def reject_reason(word, min_count_ok):
    if not min_count_ok:
        return "below_min_count"
    if any(c.isdigit() for c in word):
        return "contains_digit"
    if not any(c.isalpha() for c in word):
        return "punctuation_only"
    if len(word) > MAX_LEN:
        return "too_long"
    if WORD_RE.fullmatch(word):
        return None
    if word.startswith("-") or word.endswith("-"):
        return "edge_hyphen_fragment"
    return "other_symbols"  # URLs, e-mail, apostrophes, colon/dot forms, underscores...


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-count", type=int, default=1, help="drop surface forms rarer than this (default 1 = keep all)")
    args = ap.parse_args()

    ensure_dirs()
    out_path = CLEANED / "01_normalized.tsv"
    stats = defaultdict(lambda: [0, 0, []])  # reason -> [rows, tokens, examples]
    rows_in = tokens_in = rows_out = tokens_out = malformed = 0

    with open(RAW_VOCAB, encoding="utf-8", errors="replace") as src, open(out_path, "w", encoding="utf-8") as dst:
        for line in src:
            parsed = parse_counted_line(line)
            if parsed is None:
                malformed += 1
                continue
            count, word = parsed
            rows_in += 1
            tokens_in += count
            reason = reject_reason(word, count >= args.min_count)
            if reason is None:
                dst.write(f"{count}\t{word}\n")
                rows_out += 1
                tokens_out += count
            else:
                s = stats[reason]
                s[0] += 1
                s[1] += count
                if len(s[2]) < 15:  # input is sorted by count desc, so these are the most frequent offenders
                    s[2].append(f"{word} ({count})")

    lines = [
        "# 01 normalize",
        f"- rows in: {rows_in:,} ({tokens_in:,} tokens), malformed lines skipped: {malformed:,}",
        f"- rows out: {rows_out:,} ({tokens_out:,} tokens) -> {out_path.name}",
        f"- min-count: {args.min_count}",
        "",
        "| reason | rows | tokens | most frequent examples |",
        "|---|---:|---:|---|",
    ]
    for reason, (rows, tokens, examples) in sorted(stats.items(), key=lambda kv: -kv[1][0]):
        lines.append(f"| {reason} | {rows:,} | {tokens:,} | {', '.join(examples)} |")
    write_report("01_normalize.md", lines)


if __name__ == "__main__":
    main()
