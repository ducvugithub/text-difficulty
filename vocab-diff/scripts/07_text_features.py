"""Step 7: recompute OOV / vocab-bag coverage for train/valid/test with the STEM bags and the LEMMA bags, and report how
much of each split is unknown (overlap check). Uses VocabDiffFeatureConstruct (vocab-diff/vocab_construct.py).

Stem level: a word's bag is the bag of its rarest known stem. Lemma level: a word's bag is the bag of its own lemma.
A word whose stems were all removed in step 5 as English-looking counts as `borrowed` (not OOV); a word Voikko does not
recognise, or that is not in the list, is OOV. Names and abbreviations are skipped. Bag 1 = most frequent.
Every table is shown for all rows and for Finnish-native-only rows (origine = Real).

Output: outputs/vocab_features_{bag_method}_{split}.csv, reports/07_text_features.md
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from base import ROOT, TextAnalysis  # noqa: E402
from builder import TextDiffFeaturesConstruct  # noqa: E402
from common import ensure_dirs, write_report  # noqa: E402
from text_common import BAG_METHODS, SPLIT_FILES, load_split  # noqa: E402

OUT_DIR = ROOT / "outputs"
LEVELS = ("stem", "lemma")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bag-method", default="uniform_cumfreq_bin", choices=BAG_METHODS)
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(exist_ok=True)

    construct = TextDiffFeaturesConstruct(configs={"vocab": {"bag_method": args.bag_method}}).constructs["vocab"]
    bag_cols = construct.bag_columns
    keep = ["borrowed_coverage"] + [c for lv in LEVELS for c in (f"{lv}_OOV_coverage", *bag_cols[lv], f"mean_log_{lv}_freq")]

    lines = ["# 07 text features / OOV check",
             f"- bag method {args.bag_method}; stem bags: {len(construct.bags['stem']):,} stems, {construct.n_bags['stem']} bags; "
             f"lemma bags: {len(construct.bags['lemma']):,} lemmas, {construct.n_bags['lemma']} bags; {len(construct.borrowed):,} English-looking stems were removed in step 5",
             "- every table is shown for two subsets: `all` rows, and `finnish-native-only` (`origine` = Real; the Russian-origin rows are translations)",
             "",
             "- `per-text-avg-oov`: each text's OOV rate (unknown words / counted words), averaged over texts: every text counts equally.",
             "- `all-text-pool-oov`: all unknown words in the split / all counted words: every word counts equally.",
             "- stem level: a word's bag is the bag of its rarest known stem; lemma level: the bag of its own lemma. `borrowed` = all its stems are English-looking (removed in step 5); it is not OOV.",
             "- The last five columns are shares of ALL words in the split and add up to 100%. OOV = the two OOV columns together, divided by all words except the skipped names/abbreviations.",
             "", "| level | split | subset | texts | words | per-text-avg-oov (old) | per-text-avg-oov (new) | all-text-pool-oov (new) | in bag | borrowed (English-looking) | OOV: Voikko-unknown | OOV: recognised, not in list | skipped (name/abbrev) |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    label_lines = []

    for split in SPLIT_FILES:
        df = load_split(split)
        feats, tally = construct.build_with_tallies(TextAnalysis(df))
        out = feats[keep].copy()
        out.insert(0, "label", df["label"])
        out.to_csv(OUT_DIR / f"vocab_features_{args.bag_method}_{split}.csv", index_label="row")

        native = (df["origine"] == "Real").to_numpy()
        for subset, mask in (("all", native | ~native), ("finnish-native-only", native)):
            if subset != "all" and mask.all():
                continue  # identical to `all`
            tl, ft, dfm = tally[mask], feats[mask], df[mask]
            counted = tl["all"].sum() - tl["skipped"].sum()
            for lv in LEVELS:
                pct = lambda k: f"{100 * tl[k].sum() / tl['all'].sum():.1f}%"
                unk = tl[f"{lv}_unrecognised"].sum() + tl[f"{lv}_unlisted"].sum()
                lines.append(f"| {lv} | {split} | {subset} | {len(dfm):,} | {tl['all'].sum():,} | {100 * dfm['OOV_coverage'].mean():.1f}% | {100 * ft[f'{lv}_OOV_coverage'].mean():.1f}% "
                             f"| {100 * unk / counted:.1f}% | {pct(f'{lv}_in_bag')} | {pct('borrowed')} | {pct(f'{lv}_unrecognised')} | {pct(f'{lv}_unlisted')} | {pct('skipped')} |")
                n_b = construct.n_bags[lv]
                label_lines += ["", f"### {lv} bags, {split}, {subset}", "",
                                "| label | texts | per-text-avg-oov | borrowed | " + " | ".join(f"bag {b}" for b in range(1, n_b + 1)) + " |",
                                "|---|---:|---:|---:|" + "---:|" * n_b]
                g = ft.assign(label=df.loc[mask, "label"])
                by = g.groupby("label")[[f"{lv}_OOV_coverage", "borrowed_coverage", *bag_cols[lv]]].mean()
                n_texts = g.groupby("label").size()
                for k, r in by.iterrows():
                    label_lines.append(f"| {k} | {n_texts[k]:,} | {100 * r[f'{lv}_OOV_coverage']:.1f}% | {100 * r['borrowed_coverage']:.1f}% | " + " | ".join(f"{100 * r[c]:.1f}%" for c in bag_cols[lv]) + " |")
    write_report("07_text_features.md", lines + ["", "## By label (average share of words per bag; bag 1 = most frequent, highest bag = rarest)"] + label_lines)


if __name__ == "__main__":
    main()
