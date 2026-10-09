"""Step 2: morphological analysis with Voikko (surface form -> lemma readings + compound stems).

Input : cleaned/01_normalized.tsv
Output: cleaned/02_analysis.tsv   ('count<TAB>word<TAB>readings'; readings '-' = not recognised)
Parallel: one voikkospell process per chunk.
"""
import argparse
from itertools import islice
from multiprocessing import Pool

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))  # common.py, text_common.py

from common import CLEANED, ensure_dirs, run_voikko, write_report

CHUNK = 50_000


def analyse_chunk(lines):
    parsed = [line.rstrip("\n").split("\t") for line in lines]
    readings = run_voikko([word for _, word in parsed])
    return [f"{count}\t{word}\t{r}\n" for (count, word), r in zip(parsed, readings)]


def chunks(fh):
    while True:
        chunk = list(islice(fh, CHUNK))
        if not chunk:
            return
        yield chunk


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    ensure_dirs()
    src_path, dst_path = CLEANED / "01_normalized.tsv", CLEANED / "02_analysis.tsv"
    done = 0
    with open(src_path, encoding="utf-8") as src, open(dst_path, "w", encoding="utf-8") as dst, Pool(args.workers) as pool:
        gen = chunks(src)
        while True:
            batch = list(islice(gen, args.workers * 4))  # bounded, so the whole file is never held in memory
            if not batch:
                break
            for out in pool.map(analyse_chunk, batch):
                dst.writelines(out)
                done += len(out)
            print(f"\r{done:,} words analysed", end="", flush=True)
    print()
    write_report("02_analyze.md", ["# 02 analyze", f"- words analysed: {done:,} -> {dst_path.name}"])


if __name__ == "__main__":
    main()
