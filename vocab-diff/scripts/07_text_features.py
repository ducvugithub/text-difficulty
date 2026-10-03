"""Step 7: recompute OOV_coverage / vocab_bag_k_coverage for train/valid/test with the cleaned list, and
report how much of each split is out-of-vocabulary (overlap check).

Tokens -> Voikko lemma (context-free: the listed candidate with the highest frequency) -> bag.
Token classes: in a bag | OOV = not recognised by Voikko, or listed but beyond --top-n, or not in the list.
Proper names / abbreviations are dropped from the denominator by default (--names oov counts them as OOV instead).

Output: text-diff/feature-curated-based/outputs/vocab_features_{split}.csv, reports/07_text_features.md
"""
import argparse
from collections import Counter

import pandas as pd

from common import ROOT, ensure_dirs, write_report
from text_common import N_BAGS, SPLIT_FILES, analyse_tokens, assign_bags, best_lemma, load_lemma_list, load_split, token_counts

OUT_DIR = ROOT / "text-diff" / "feature-curated-based" / "outputs"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default="rarest_stem_freq", choices=["freq", "rarest_stem_freq"])
    ap.add_argument("--top-n", type=int, default=20_000)
    ap.add_argument("--names", default="skip", choices=["skip", "oov"])
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lemmas, freq = load_lemma_list(args.variant)
    bags = assign_bags(lemmas, args.top_n)
    frames = {s: load_split(s) for s in SPLIT_FILES}
    counts = {s: token_counts(f["text"]) for s, f in frames.items()}
    analysis = analyse_tokens({t for cs in counts.values() for c in cs for t in c})

    lines = ["# 07 text features / OOV check",
             f"- variant {args.variant}, top-n {args.top_n or 'all'} ({len(bags):,} binned lemmas, {len(lemmas):,} in full list), names: {args.names}",
             "", "| split | texts | tokens | OOV old | OOV new | in bag | unrecognised | listed beyond top-n | name/abbrev (skipped) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    type_lines = ["", "## Type-level overlap (unique lemmas / unrecognised forms)", "",
                  "| split | recognised lemma types | in full list | in bags | unrecognised form types |", "|---|---:|---:|---:|---:|"]
    label_lines = []

    for split, df in frames.items():
        rows, totals, lemma_types, unrec_types = [], Counter(), set(), set()
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
                    if status == "unrecognised":
                        unrec_types.add(tok)
                    else:
                        lemma_types.update(cands[:1])
                elif lemma in bags:
                    t[f"bag{bags[lemma]}"] += n
                    lemma_types.add(lemma)
                else:
                    t["beyond_top_n"] += n
                    lemma_types.add(lemma)
            total = sum(cnt.values())
            denom = total - t["skipped"]
            oov = t["unrecognised"] + t["unlisted"] + t["beyond_top_n"] + t["oov_name"]
            row = {"n_word_tokens": denom, "OOV_coverage": oov / denom if denom else 0.0}
            row.update({f"vocab_bag_{b}_coverage": (t[f"bag{b}"] / denom if denom else 0.0) for b in range(1, N_BAGS + 1)})
            row.update({f"frac_{k}": (t[k] / denom if denom else 0.0) for k in ("unrecognised", "unlisted", "beyond_top_n")})
            rows.append(row)
            totals.update(t)
            totals["all"] += total
        out = pd.DataFrame(rows, index=df.index)
        if "label" in df:
            out.insert(0, "label", df["label"])
        out.to_csv(OUT_DIR / f"vocab_features_{split}.csv", index_label="row")

        all_tok = totals["all"]
        in_bag = sum(totals[f"bag{b}"] for b in range(1, N_BAGS + 1))
        pct = lambda k: f"{100 * totals[k] / all_tok:.1f}%"
        lines.append(f"| {split} | {len(df):,} | {all_tok:,} | {df['OOV_coverage'].mean():.3f} | {out['OOV_coverage'].mean():.3f} "
                     f"| {100 * in_bag / all_tok:.1f}% | {pct('unrecognised')} | {pct('beyond_top_n')} | {pct('skipped')} |")
        in_list = sum(1 for l in lemma_types if l in freq)
        type_lines.append(f"| {split} | {len(lemma_types):,} | {in_list:,} | {sum(1 for l in lemma_types if l in bags):,} | {len(unrec_types):,} |")
        if "label" in out:
            by = out.groupby("label")["OOV_coverage"].agg(["count", "mean"])
            label_lines += [f"", f"### {split}: mean OOV_coverage by label", "", "| label | texts | OOV new |", "|---|---:|---:|"]
            label_lines += [f"| {k} | {int(r['count'])} | {r['mean']:.3f} |" for k, r in by.iterrows()]
    write_report("07_text_features.md", lines + type_lines + ["", "## By label"] + label_lines)


if __name__ == "__main__":
    main()
