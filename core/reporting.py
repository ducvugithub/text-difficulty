"""Small helpers shared by the report writers of the curated and the BERT way."""
import numpy as np


def table(text: str, heading: str):
    """Rows (lists of cells) of the first markdown table after the line `heading`, without the header row."""
    lines = text.split("\n")
    i = next(k for k, line in enumerate(lines) if line.strip() == heading)
    rows, started = [], False
    for line in lines[i + 1:]:
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not set(cells[0]) <= {"-", ":"}:
                rows.append(cells)
        elif started:
            break
    return rows[1:]


def steps(mae) -> str:
    """An average miss in label steps (one step is 0.5)."""
    return f"{float(mae) / 0.5:.2f}"


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def md_table(header, rows):
    """A markdown table from a header list and a list of row lists."""
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]


def confusion_md(y, pred):
    """A confusion matrix as row percentages: rows = true label, columns = the prediction rounded to the nearest half step."""
    from core.evaluate import CLASSES, confusion_counts

    true, counts = confusion_counts(y, pred)
    out = ["| true label \\ predicted | " + " | ".join(f"{c:g}" for c in CLASSES) + " |", "|---|" + "---:|" * len(CLASSES)]
    for t, row in zip(true, counts):
        n = int(row.sum())
        cells = []
        for c, v in zip(CLASSES, row):
            share = "<1%" if 0 < 100 * v / n < 0.5 else f"{100 * v / n:.0f}%"
            cells.append("" if v == 0 else (f"**{share}**" if c == t else share))
        out.append(f"| {t:g} (n={n}) | " + " | ".join(cells) + " |")
    return out
