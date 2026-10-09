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
    ("iikka$", "ics$", 0.0),                           # matematiikka / mathematics
]
# Finnish verb endings (inspiroida / to inspire, tsekata / to check). Applied ONLY when the English translation is a verb
# ("to ..."): the -ta of the noun rotta (rat) is not a verb ending.
VERB_RULES = [("oida$", "$", 0.2), ("öidä$", "$", 0.2), ("ta$", "$", 0.2), ("tä$", "$", 0.2)]
DOUBLING_COST = 0.2        # a doubled Finnish letter against a single English one: tt / t, ss / s, kk / k, ii / i

MIN_LENGTH = 3             # shorter Finnish stems are never judged by the edit score
MAX_NORM = 35.0            # at or below this norm a stem counts as English-looking (threshold from the team sheet)

_PAREN = re.compile(r"\([^)]*\)")
_WORD = re.compile(r"[a-z]+(?:-[a-z]+)*")


def _gloss_words(gloss):
    """Single-word translations in one gloss. A verb keeps its "to" ("to register"), so the verb-ending rules can be limited to verbs."""
    words = []
    for part in re.split(r"[,;/]", _PAREN.sub("", gloss)):
        part = part.strip().lower()
        verb = part.startswith("to ")
        part = re.sub(r"^(to|a|an|the)\s+", "", part)
        if _WORD.fullmatch(part):
            words.append(("to " if verb else "") + part)
    return words


def english_candidates(entry):
    """Single-word English translations from a kaikki.org Wiktionary entry (skips inflected / alternative forms)."""
    out = []
    for sense in entry.get("senses", []):
        if "form_of" in sense or "alt_of" in sense:
            continue
        for gloss in sense.get("glosses", []):
            if gloss.lower().startswith(("inflection of", "synonym of", "alternative")):
                continue
            out += [w for w in _gloss_words(gloss) if w not in out]
    return out


def first_sense_candidates(entry):
    """Single-word English translations of the FIRST meaning of an entry (the first sense that is not an inflected /
    alternative form and has a single-word gloss). Later meanings are ignored: puku (suit) also has an antelope sense
    whose translation is "puku", and kissa (cat) a slang sense "chick"."""
    for sense in entry.get("senses", []):
        if "form_of" in sense or "alt_of" in sense:
            continue
        words = []
        for gloss in sense.get("glosses", []):
            if gloss.lower().startswith(("inflection of", "synonym of", "alternative")):
                continue
            words += [w for w in _gloss_words(gloss) if w not in words]
        if words:
            return words
    return []


def english_source(entry):
    """The English source word of a `bor:en` / `lbor:en` etymology (biisi <- piece, kämppä <- camp), or ''."""
    for t in entry.get("etymology_templates", []):
        args = t.get("args", {})
        if t.get("name") in ("bor", "lbor") and args.get("2") == "en" and args.get("3"):
            return args["3"].lower()
    return ""


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
_RULES_VERB = _parse(RULES + VERB_RULES)


def edit_score(english, finnish, verb=False):
    """Weighted edit distance from an English word to a Finnish one (lower = more alike). verb=True also allows the verb-ending rules."""
    rules = _RULES_VERB if verb else _RULES
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
            for fp, f_end, ep, e_end, cost in rules:
                if e.startswith(ep, i) and f.startswith(fp, j) and (not e_end or i + len(ep) == n) and (not f_end or j + len(fp) == m):
                    relax(i + len(ep), j + len(fp), cost)
    return d[n][m]


def norm_score(english, finnish, verb=False):
    """Edit score as a percentage of the longer word's length."""
    return 100 * edit_score(english, finnish, verb) / max(len(english), len(finnish))


def best_match(finnish, candidates):
    """(english, edit score, norm) of the closest candidate, or None. A candidate "to register" is a verb: the Finnish
    verb-ending rules apply to it, and only to it."""
    scored = []
    for c in candidates:
        verb = c.startswith("to ")
        word = c[3:] if verb else c
        scored.append((c, edit_score(word, finnish, verb), norm_score(word, finnish, verb)))
    return min(scored, key=lambda t: t[2]) if scored else None


MIN_ENGLISH_ZIPF = 2.8   # a translation identical to the stem must be at least this common in English (wordfreq Zipf scale)


def real_translations(finnish, candidates):
    """Drop a translation that is the stem itself unless it is a real, current English word: Wiktionary names untranslatable
    Finnish things by their own name (pulla = the Finnish bun), which is not a translation. radio, video, internet and
    euro stay (Zipf 4-5); pulla (1.5), kerma (1.8) and raita (1.9) go."""
    from wordfreq import zipf_frequency

    f = finnish.lower()
    return [c for c in candidates if (c[3:] if c.startswith("to ") else c) != f or zipf_frequency(f, "en") >= MIN_ENGLISH_ZIPF]


def looks_english(finnish, candidates):
    match = best_match(finnish, real_translations(finnish, candidates)) if len(finnish) >= MIN_LENGTH else None
    return match is not None and match[2] <= MAX_NORM, match
