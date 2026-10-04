"""Step 7: recompute OOV_coverage / vocab_bag_k_coverage for train/valid/test with the cleaned list, and
report how much of each split is out-of-vocabulary (overlap check).

Tokens -> Voikko lemma (context-free: the listed candidate with the highest frequency) -> bag.
Token classes: in a bag | OOV = not recognised by Voikko, or not in the list.
Proper names / abbreviations are dropped from the denominator by default (--names oov counts them as OOV instead).

Output: text-diff/feature-curated-based/outputs/vocab_features_{bag_method}_{split}.csv, reports/07_text_features.md
"""
import argparse
from collections import Counter

import pandas as pd

from common import ROOT, ensure_dirs, write_report
from text_common import (BAG_METHODS, SPLIT_FILES, analyse_tokens, assign_bags, best_lemma, load_lemma_list,
                         load_split, token_counts)

OUT_DIR = ROOT / "text-diff" / "feature-curated-based" / "outputs"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--freq-column", default="freq", choices=["freq", "rarest_stem_freq"])
    ap.add_argument("--bag-method", default="uniform_cumfreq_bin", choices=BAG_METHODS)
    ap.add_argument("--names", default="skip", choices=["skip", "oov"])
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lemmas, freq = load_lemma_list(args.freq_column)
    bags = assign_bags(lemmas, freq, args.bag_method)
    n_bags = max(bags.values())
    frames = {s: load_split(s) for s in SPLIT_FILES}
    counts = {s: token_counts(f["text"]) for s, f in frames.items()}
    analysis = analyse_tokens({t for cs in counts.values() for c in cs for t in c})

    lines = ["# 07 text features / OOV check",
             f"- frequency column {args.freq_column}, bag method {args.bag_method} ({len(bags):,} binned lemmas, {n_bags} bags, {len(lemmas):,} in full list), names: {args.names}",
             "",
             "- `per-text-avg-oov`: each text's OOV rate (unknown words / counted words), averaged over texts: every text counts equally.",
             "- `all-text-pool-oov`: all unknown words in the split / all counted words: every word counts equally.",
             "- The last four columns are shares of ALL words in the split and add up to 100%. OOV = the two OOV columns together, divided by all words except the skipped names/abbreviations.",
             "", "| split | texts | words | per-text-avg-oov (old) | per-text-avg-oov (new) | all-text-pool-oov (new) | in bag | OOV: Voikko-unknown | OOV: recognised, not in list | skipped (name/abbrev) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    label_lines = []

    for split, df in frames.items():
        rows, totals = [], Counter()
        for cnt in counts[split]:
            t = Counter()
            for tok, n in cnt.items():
                status, cands = analysis[tok]
                if status in ("name", "abbrev"):
                    t["skipped" if args.names == "skip" else "oov_name"] += n
                    continue
                lemma = best_lemma(cands, freq) if status == "ok" else None
                if lemma is None:
                    t["unrecognised" if status == "unrecognised" else "unlisted"] += n
                else:
                    t[f"bag{bags[lemma]}"] += n
            total = sum(cnt.values())
            denom = total - t["skipped"]
            oov = t["unrecognised"] + t["unlisted"] + t["oov_name"]
            row = {"n_word_tokens": denom, "OOV_coverage": oov / denom if denom else 0.0}
            row.update({f"vocab_bag_{b}_coverage": (t[f"bag{b}"] / denom if denom else 0.0) for b in range(1, n_bags + 1)})
            row.update({f"frac_{k}": (t[k] / denom if denom else 0.0) for k in ("unrecognised", "unlisted")})
            rows.append(row)
            totals.update(t)
            totals["all"] += total
            totals["oov_words"] += oov
            totals["counted_words"] += denom
        out = pd.DataFrame(rows, index=df.index)
        if "label" in df:
            out.insert(0, "label", df["label"])
        out.to_csv(OUT_DIR / f"vocab_features_{args.bag_method}_{split}.csv", index_label="row")

        all_tok = totals["all"]
        in_bag = sum(totals[f"bag{b}"] for b in range(1, n_bags + 1))
        pct = lambda k: f"{100 * totals[k] / all_tok:.1f}%"
        lines.append(f"| {split} | {len(df):,} | {all_tok:,} | {100 * df['OOV_coverage'].mean():.1f}% | {100 * out['OOV_coverage'].mean():.1f}% "
                     f"| {100 * totals['oov_words'] / totals['counted_words']:.1f}% | {100 * in_bag / all_tok:.1f}% | {pct('unrecognised')} | {pct('unlisted')} | {pct('skipped')} |")
        if "label" in out:
            bag_cols = [f"vocab_bag_{b}_coverage" for b in range(1, n_bags + 1)]
            by = out.groupby("label")[["OOV_coverage", *bag_cols]].mean()
            n_texts = out.groupby("label").size()
            label_lines += ["", f"### {split}", "",
                            "| label | texts | per-text-avg-oov | " + " | ".join(f"bag {b}" for b in range(1, n_bags + 1)) + " |",
                            "|---|---:|---:|" + "---:|" * n_bags]
            for k, r in by.iterrows():
                label_lines.append(f"| {k} | {n_texts[k]:,} | {100 * r['OOV_coverage']:.1f}% | " + " | ".join(f"{100 * r[c]:.1f}%" for c in bag_cols) + " |")
    write_report("07_text_features.md", lines + ["", "## By label (average share of words per bag; bag 1 = rarest, bag 10 = most frequent)"] + label_lines)


if __name__ == "__main__":
    main()
