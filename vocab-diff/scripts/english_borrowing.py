"""Helpers for spotting Finnish words that look like English ones: gloss parsing and an edit score.

edit score = weighted edit distance from the English word to the Finnish one: a normal edit (insert, delete, substitute)
costs 1, the STANDARD modifications Finnish applies when it borrows a word cost 0.2 (or 0), see RULES.
norm = edit score / max(Finnish length, English length) * 100. A stem is English-looking at norm <= MAX_NORM.
The rule table and threshold come from the team sheet; tune them here.
"""
import re

COST_NORMAL = 1.0
COST_STANDARD = 0.2
# (Finnish part, English part, cost); '$' anchors the part at the end of the word. Anything not listed costs COST_NORMAL.
RULES = [
    ("i$", "$", 0.2),                                  # Finnish final -i: bussi / bus, vitamiini / vitamin
    ("i$", "e$", 0.2),                                 # final e -> i: conference / konferenssi (inferred from the sheet's 0.6)
    ("k", "c", 0.2), ("f", "ph", 0.2), ("k", "ch", 0.2), ("k", "g", 0.2), ("d", "t", 0.2), ("t", "th", 0.2),
    ("ss", "c", 0.2), ("s", "c", 0.2), ("s", "ch", 0.2), ("ss", "ch", 0.2), ("ts", "ch", 0.2),
    ("ts", "z", 0.2), ("ss", "z", 0.2), ("hv", "f", 0.2),
    ("ia$", "y$", 0.2), ("iä$", "y$", 0.2),            # strategia / strategy
    ("oida$", "$", 0.2), ("öidä$", "$", 0.2),          # verb endings: inspiroida / inspire
    ("ta$", "$", 0.2), ("tä$", "$", 0.2),
    ("iikka$", "ics$", 0.0),                           # matematiikka / mathematics
]
DOUBLING_COST = 0.2        # a doubled Finnish letter against a single English one: tt / t, ss / s, kk / k, ii / i

MIN_LENGTH = 3             # shorter Finnish stems are never judged by the edit score
MAX_NORM = 35.0            # at or below this norm a stem counts as English-looking (threshold from the team sheet)

_PAREN = re.compile(r"\([^)]*\)")
_WORD = re.compile(r"[a-z]+(?:-[a-z]+)*")


def english_candidates(entry):
    """Single-word English translations from a kaikki.org Wiktionary entry (skips inflected / alternative forms)."""
    out = []
    for sense in entry.get("senses", []):
        if "form_of" in sense or "alt_of" in sense:
            continue
        for gloss in sense.get("glosses", []):
            if gloss.lower().startswith(("inflection of", "synonym of", "alternative")):
                continue
            for part in re.split(r"[,;/]", _PAREN.sub("", gloss)):
                part = re.sub(r"^(to|a|an|the)\s+", "", part.strip().lower())
                if _WORD.fullmatch(part) and part not in out:
                    out.append(part)
    return out


def etymology_tags(entry, limit=6):
    """Compact etymology evidence, e.g. 'bor:sv der:la'. Borrowing / derivation templates only."""
    tags = []
    for t in entry.get("etymology_templates", []):
        name, args = t.get("name"), t.get("args", {})
        if name in ("bor", "lbor", "der", "inh", "slbor", "obor"):
            tag = f"{name}:{args.get('2', '')}"
        elif name == "cog":
            tag = f"cog:{args.get('1', '')}"
        else:
            continue
        if tag not in tags:
            tags.append(tag)
    return " ".join(tags[:limit])


def _parse(rules):
    out = []
    for f, e, cost in rules:
        out.append((f.rstrip("$"), f.endswith("$"), e.rstrip("$"), e.endswith("$"), cost))
    return out


_RULES = _parse(RULES)


def edit_score(english, finnish):
    """Weighted edit distance from an English word to a Finnish one (lower = more alike)."""
    e, f = english.lower(), finnish.lower()
    n, m = len(e), len(f)
    INF = float("inf")
    d = [[INF] * (m + 1) for _ in range(n + 1)]
    d[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            cur = d[i][j]
            if cur == INF:
                continue
            def relax(ni, nj, cost):
                if cur + cost < d[ni][nj]:
                    d[ni][nj] = cur + cost
            if i < n and j < m:
                relax(i + 1, j + 1, 0.0 if e[i] == f[j] else COST_NORMAL)
            if i < n:
                relax(i + 1, j, COST_NORMAL)
            if j < m:
                relax(i, j + 1, COST_NORMAL)
            if i < n and j + 1 < m and f[j] == f[j + 1] and e[i] == f[j]:
                relax(i + 1, j + 2, DOUBLING_COST)
            for fp, f_end, ep, e_end, cost in _RULES:
                if e.startswith(ep, i) and f.startswith(fp, j) and (not e_end or i + len(ep) == n) and (not f_end or j + len(fp) == m):
                    relax(i + len(ep), j + len(fp), cost)
    return d[n][m]


def norm_score(english, finnish):
    """Edit score as a percentage of the longer word's length."""
    return 100 * edit_score(english, finnish) / max(len(english), len(finnish))


def best_match(finnish, candidates):
    """(english, edit score, norm) of the closest candidate, or None."""
    scored = [(c, edit_score(c, finnish), norm_score(c, finnish)) for c in candidates]
    return min(scored, key=lambda t: t[2]) if scored else None


def looks_english(finnish, candidates):
    match = best_match(finnish, candidates) if len(finnish) >= MIN_LENGTH else None
    return match is not None and match[2] <= MAX_NORM, match
