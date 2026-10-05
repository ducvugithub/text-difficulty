"""Step 7: recompute OOV / vocab-bag coverage for train/valid/test with the STEM bags and the LEMMA bags, and report how
much of each split is unknown (overlap check). Uses VocabDiffFeatureConstruct (vocab-diff/vocab_construct.py).

Stem level: a word is split into its stems and every stem is placed by its own count. Lemma level: a word is placed by its lemma.
A word whose stems were all removed in step 5 as English-looking counts as `borrowed` (not OOV); a word Voikko does not
recognise, or that is not in the list, is OOV. Names and abbreviations are skipped. Bag 1 = most frequent.
Every table is shown for all rows and for Finnish-native-only rows (origine = Real).

Output: outputs/vocab_features_{split}.csv, reports/07_text_features.md
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
    ap.add_argument("--lemma-bin-method", default="log10_freq_bin", choices=BAG_METHODS)
    ap.add_argument("--stem-bin-method", default="uniform_cumfreq_bin", choices=BAG_METHODS)
    ap.add_argument("--lemma-n-bins", type=int, default=10)
    ap.add_argument("--stem-n-bins", type=int, default=10)
    args = ap.parse_args()
    ensure_dirs()
    OUT_DIR.mkdir(exist_ok=True)

    construct = TextDiffFeaturesConstruct(configs={"vocab": {"lemma_bin_method": args.lemma_bin_method, "stem_bin_method": args.stem_bin_method, "lemma_n_bins": args.lemma_n_bins, "stem_n_bins": args.stem_n_bins}}).constructs["vocab"]
    bag_cols = construct.bag_columns
    keep = [c for lv in LEVELS for c in (f"{lv}_OOV_coverage", f"{lv}_borrowed_coverage", *bag_cols[lv], f"mean_log_{lv}_freq")]

    lines = ["# 07 text features / OOV check",
             f"- bin method: lemma `{args.lemma_bin_method}` ({args.lemma_n_bins} bins), stem `{args.stem_bin_method}` ({args.stem_n_bins} bins); "
             f"stem bins: {len(construct.bags['stem']):,} stems, {construct.n_bags['stem']} bins; lemma bins: {len(construct.bags['lemma']):,} lemmas, {construct.n_bags['lemma']} bins; "
             f"{len(construct.borrowed):,} English-looking stems were removed in step 5",
             "- every table is shown for two subsets: `all` rows, and `finnish-native-only` (`origine` = Real; the Russian-origin rows are translations)",
             "",
             "- lemma level: a unit is a word, placed by its lemma. Stem level: a word is split into its stems and every stem is a unit (työpaikka = työ + paikka = 2 units); a word Voikko does not recognise is 1 unit",
             "- `borrowed` = lemma / stems removed in step 5 as English-looking; not OOV. OOV = a word Voikko does not recognise, or a lemma / stem not in the list",
             "- `per-text-avg-oov`: each text's OOV share of units, averaged over texts (every text counts equally). `all-text-pool-oov`: all unknown units / all units (every unit counts equally)",
             "- Names and abbreviations are skipped; `skipped` is their share of all words. The four shares before it add up to 100% of the units",
             "", "| level | split | subset | texts | words | units | per-text-avg-oov (old) | per-text-avg-oov (new) | all-text-pool-oov (new) | in bin | borrowed | OOV: Voikko-unknown | OOV: not in list | skipped (% of words) |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    label_lines = []

    for split in SPLIT_FILES:
        df = load_split(split)
        feats, tally = construct.build_with_tallies(TextAnalysis(df))
        out = feats[keep].copy()
        out.insert(0, "label", df["label"])
        out.to_csv(OUT_DIR / f"vocab_features_{split}.csv", index_label="row")

        native = (df["origine"] == "Real").to_numpy()
        for subset, mask in (("all", native | ~native), ("finnish-native-only", native)):
            if subset != "all" and mask.all():
                continue  # identical to `all`
            tl, ft, dfm = tally[mask], feats[mask], df[mask]
            for lv in LEVELS:
                units = sum(tl[f"{lv}_{k}"].sum() for k in ("unrecognised", "unlisted", "borrowed", "bag"))
                pct = lambda k: f"{100 * tl[f'{lv}_{k}'].sum() / units:.1f}%"
                unk = tl[f"{lv}_unrecognised"].sum() + tl[f"{lv}_unlisted"].sum()
                lines.append(f"| {lv} | {split} | {subset} | {len(dfm):,} | {tl['words'].sum():,} | {units:,} | {100 * dfm['OOV_coverage'].mean():.1f}% | {100 * ft[f'{lv}_OOV_coverage'].mean():.1f}% "
                             f"| {100 * unk / units:.1f}% | {pct('bag')} | {pct('borrowed')} | {pct('unrecognised')} | {pct('unlisted')} | {100 * tl['skipped'].sum() / tl['words'].sum():.1f}% |")
                n_b = construct.n_bags[lv]
                label_lines += ["", f"### {lv} bins, {split}, {subset}", "",
                                "| label | texts | per-text-avg-oov | borrowed | " + " | ".join(f"bin {b}" for b in range(1, n_b + 1)) + " |",
                                "|---|---:|---:|---:|" + "---:|" * n_b]
                g = ft.assign(label=df.loc[mask, "label"])
                by = g.groupby("label")[[f"{lv}_OOV_coverage", f"{lv}_borrowed_coverage", *bag_cols[lv]]].mean()
                n_texts = g.groupby("label").size()
                for k, r in by.iterrows():
                    label_lines.append(f"| {k} | {n_texts[k]:,} | {100 * r[f'{lv}_OOV_coverage']:.1f}% | {100 * r[f'{lv}_borrowed_coverage']:.1f}% | " + " | ".join(f"{100 * r[c]:.1f}%" for c in bag_cols[lv]) + " |")
    write_report("07_text_features.md", lines + ["", "## By label (average share of units per bin; bin 1 = most frequent, highest bin = rarest)"] + label_lines)


if __name__ == "__main__":
    main()
