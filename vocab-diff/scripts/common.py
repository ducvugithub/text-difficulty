"""Shared helpers for the vocab-freq cleaning pipeline (stdlib only)."""
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CLEANED = ROOT / "vocab-diff" / "vocab-freq" / "cleaned"
REPORTS = ROOT / "vocab-diff" / "vocab-freq" / "reports"
RAW_VOCAB = DATA / "finnish_vocab.txt"

# One or more letter runs joined by single hyphens: "talo", "EU-maa"
WORD_RE = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")

# Voikko CLASS values
NAME_CLASSES = {"nimi", "etunimi", "sukunimi", "paikannimi"}
ABBREV_CLASSES = {"lyhenne"}

_ANALYSIS_LINE = re.compile(r"^A\((.*)\):(\d+):([A-Z_]+)=(.*)$")
_WORDBASE = re.compile(r"\+([^()]*)\(([^()]*)\)")


def ensure_dirs():
    CLEANED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)


def write_report(name, lines):
    ensure_dirs()
    path = REPORTS / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"report -> {path}")


def parse_counted_line(line):
    """'  123 word' -> (123, 'word'), or None if malformed."""
    parts = line.split(None, 1)
    if len(parts) != 2 or not parts[0].isdigit():
        return None
    return int(parts[0]), parts[1].strip()


def _stems(wordbases):
    """Real stems of a Voikko WORDBASES string; derivational suffixes "(+us)" and hyphens are skipped."""
    return [lemma for _, lemma in _WORDBASE.findall(wordbases) if lemma and not lemma.startswith("+") and lemma != "-"]


def _suffixes(wordbases):
    """Derivational suffixes of a WORDBASES string as 'surface>lemma' (e.g. 'lli+nen>+nen', 'ton>+ton')."""
    return [f"{surface}>{lemma}" for surface, lemma in _WORDBASE.findall(wordbases) if lemma.startswith("+")]


def run_voikko(words):
    """Analyse words with `voikkospell -m`.

    Returns one string per word: '-' if Voikko does not recognise it, else readings joined by ';',
    each reading 'baseform|class|stem1+stem2|suffix1,suffix2' (deduplicated, Voikko order; the 4th field is new,
    older files have 3 fields and decode_readings accepts both).

    LC_ALL must be a UTF-8 locale: under the default C locale Voikko silently rejects every word with ä/ö.
    """
    env = dict(os.environ, LC_ALL="en_US.UTF-8")
    out = subprocess.run(
        ["voikkospell", "-m"],
        input="\n".join(words) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=True,
    ).stdout

    results = []
    readings = {}  # reading index -> [baseform, class, wordbases] for the current word
    expected = iter(words)

    def flush():
        if current_word is None:
            return
        if not readings:
            results.append("-")
            return
        seen = []
        for base, cls, wb in readings.values():
            enc = f"{base}|{cls}|{'+'.join(_stems(wb))}|{','.join(_suffixes(wb))}"
            if enc not in seen:
                seen.append(enc)
        results.append(";".join(seen))

    current_word = None
    for line in out.splitlines():
        if line.startswith(("C: ", "W: ")):
            flush()
            readings = {}
            current_word = line[3:]
            want = next(expected)
            if current_word != want:
                raise RuntimeError(f"voikkospell output out of sync: got {current_word!r}, expected {want!r}")
        elif line.startswith("E:"):
            raise RuntimeError(f"voikkospell error line {line!r}; normalisation should have removed this word")
        else:
            m = _ANALYSIS_LINE.match(line)
            if m:
                _, idx, key, val = m.groups()
                r = readings.setdefault(idx, ["", "", ""])
                if key == "BASEFORM":
                    r[0] = val
                elif key == "CLASS":
                    r[1] = val
                elif key == "WORDBASES":
                    r[2] = val
    flush()
    if len(results) != len(words):
        raise RuntimeError(f"voikkospell returned {len(results)} results for {len(words)} words")
    return results


def decode_readings(field, full=False):
    """'a|cls|s1+s2|sfx;b|cls||' -> [(base, cls, [stems])]; '-' -> [].
    With full=True each reading also carries its derivational suffixes: (base, cls, [stems], ['surface>lemma'])."""
    if field == "-":
        return []
    readings = []
    for enc in field.split(";"):
        parts = enc.split("|")
        base, cls, stems = parts[0], parts[1], parts[2]
        reading = (base, cls, stems.split("+") if stems else [])
        if full:
            suffixes = parts[3] if len(parts) > 3 and parts[3] else ""
            reading += (suffixes.split(",") if suffixes else [],)
        readings.append(reading)
    return readings


def select_readings(readings):
    """Drop proper-name and abbreviation readings when a common-word reading exists.

    Returns (status, readings): status is 'ok', 'name' (only name readings), 'abbrev' (only abbreviations)
    or 'unrecognised' (no readings).
    """
    if not readings:
        return "unrecognised", []
    common = [r for r in readings if r[1] not in NAME_CLASSES]
    if not common:
        return "name", []
    non_abbrev = [r for r in common if r[1] not in ABBREV_CLASSES]
    if not non_abbrev:
        return "abbrev", []
    return "ok", non_abbrev
