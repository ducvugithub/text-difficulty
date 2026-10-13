"""Build and cache the features of registered signals (curated_features/utils/registry.py) for train / valid / test.

    python curated_features/scripts/build_features.py                                  every default signal of every category, all splits
    python curated_features/scripts/build_features.py --signals vocab.freq grammar.rarity_concepts --splits test
    python curated_features/scripts/build_features.py --sets vocab_coverage_cognitive  the signals a feature set is made of
    python curated_features/scripts/build_features.py --parser                         also the signals that need the parser server (cognitive.dependency)
    python curated_features/scripts/build_features.py --refresh                        rebuild even if cached (after changing a signal's code)
    python curated_features/scripts/build_features.py --list                           what is registered

Features are cached in outputs/features/ by curated_features/utils/feature_store.py; the experiments (curated_features/modeling/run_experiment.py) read them from there.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from curated_features.modeling.feature_sets import FEATURE_SETS  # noqa: E402
from curated_features.utils import registry  # noqa: E402
from core.dataset import SPLIT_FILES  # noqa: E402
from curated_features.utils.feature_store import signal_features  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--signals", nargs="*", metavar="category.signal")
    ap.add_argument("--sets", nargs="*", metavar="feature_set")
    ap.add_argument("--splits", nargs="*", default=list(SPLIT_FILES), choices=list(SPLIT_FILES))
    ap.add_argument("--parser", action="store_true", help="include signals that need the parser server")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for category, signals in registry.SIGNALS.items():
            for name in signals:
                flags = [("default" if name in registry.DEFAULTS[category] else ""), ("needs parser" if (category, name) in registry.NEEDS_PARSER else "")]
                print(f"{category}.{name:26s} {' '.join(f for f in flags if f)}")
        print("\nfeature sets:", ", ".join(FEATURE_SETS))
        return

    jobs = []  # (category, signal, settings)
    if args.sets:
        for name in args.sets:
            jobs += [(c, s, *(rest[:1] or [None])) for c, s, *rest in FEATURE_SETS[name].get("signals", [])]
    if args.signals:
        jobs += [(*key.split(".", 1), None) for key in args.signals]
    if not jobs:
        jobs = [(c, s, None) for c, names in registry.DEFAULTS.items() for s in names]
        if args.parser:
            jobs += [(c, s, None) for c, s in sorted(registry.NEEDS_PARSER)]
    for category, signal, settings in dict.fromkeys((c, s, tuple(sorted((st or {}).items()))) for c, s, st in jobs):
        for split in args.splits:
            signal_features(split, category, signal, dict(settings) or None, args.refresh)


if __name__ == "__main__":
    main()
