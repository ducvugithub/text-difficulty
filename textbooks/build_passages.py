"""The reading texts of the Suomen mestari textbooks (books 1-4) with book, chapter, page and an estimated difficulty, from the per-page text files in data/textbooks/<book>/p0001.txt ... (Tesseract OCR for the scanned books 1, 2 and 4, the PDF's own text layer for book 3).

Which pages hold a text is chosen by hand in SEGMENTS (book, chapter, first page, last page, kind, needs_review); this script cuts the texts out.
Book level is what the book states itself: SM1 A1, SM2 A2.1, SM3 A2.2, SM4 B1 (the foreword says it can take learners towards B2).
The estimated label is a guess, not a measurement: the book's label range, spread over the chapters. Change LABEL_RANGE to try another mapping.
The texts are copyrighted: the output stays in data/textbooks/ (git-ignored).

    python textbooks/build_passages.py        writes data/textbooks/passages.csv (all passages), paragraph_texts.csv / dialogue_texts.csv / other_texts.csv (the same split by type) and page_index.csv (every page: which text it belongs to, if any)
"""
import csv
import re
import subprocess
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "textbooks"
SM3_PDF = Path(__file__).resolve().parents[2] / "textbooks" / "SM textbooks" / "Suomen-Mestari-3.pdf"  # the only book with a text layer; books 1, 2 and 4 are scans (OCR, see the docstring)
BOOK_LEVEL = {"sm1": "A1", "sm2": "A2.1", "sm3": "A2.2", "sm4": "B1"}
MIN_WORDS = 60
HEADER_WORDS = {"Lähettäjä", "Vastaanottaja", "Aihe", "Otsikko", "Kysymys", "Vastaus", "Huom", "Esimerkki", "Päivämäärä", "Liitteet", "Kopio"}
SPEAKER = re.compile(r"(?:^|\s)([A-ZÅÄÖ][a-zåäö]{2,12}):(?=\s|$)")
LABEL_RANGE = {"sm1": (1.0, 1.5), "sm2": (1.5, 2.0), "sm3": (2.5, 3.0), "sm4": (3.0, 4.0)}  # learner-guide level range of each book (uusikielemme.fi) on our scale (1 = A1, 2 = A2, 3 = B1, 4 = B2); label at chapter 1 and at chapter 8 (chapter 9 of SM1 = the end)
CHAPTERS = {"sm1": 9, "sm2": 8, "sm3": 8, "sm4": 8}

# (book, chapter, first page, last page, kind, needs_review): kind = main text | dialogue | reading | article | letter | list | mixed
# `prose` keeps only the paragraph part of a text (before the first speaker line, "Pedro:"); a text is `usable` when it is not a dialogue / list / mixed item and has >= MIN_WORDS prose words.
SEGMENTS = [
    ("sm1", 2, 21, 21, "main text", 0), ("sm1", 2, 23, 23, "main text", 0), ("sm1", 2, 25, 25, "dialogue", 0),
    ("sm1", 3, 43, 43, "letter", 0), ("sm1", 3, 48, 48, "dialogue", 0),
    ("sm1", 4, 63, 64, "main text", 0), ("sm1", 4, 68, 68, "dialogue", 0),
    ("sm1", 5, 83, 84, "main text", 0), ("sm1", 5, 89, 89, "dialogue", 0),
    ("sm1", 6, 107, 107, "main text", 0), ("sm1", 6, 108, 108, "main text", 0), ("sm1", 6, 112, 112, "dialogue", 0),
    ("sm1", 7, 137, 138, "main text", 0), ("sm1", 7, 141, 141, "dialogue", 0),
    ("sm1", 8, 163, 164, "main text", 0), ("sm1", 8, 171, 171, "dialogue", 0),
    ("sm1", 9, 193, 194, "main text", 0), ("sm1", 9, 199, 199, "dialogue", 0),
    ("sm2", 1, 12, 13, "dialogue", 0), ("sm2", 2, 49, 50, "main text", 0), ("sm2", 3, 81, 84, "main text", 0),
    ("sm2", 4, 121, 122, "dialogue", 0), ("sm2", 5, 149, 150, "main text", 0), ("sm2", 6, 177, 178, "main text", 0),
    ("sm2", 7, 211, 212, "article", 0), ("sm2", 8, 247, 249, "main text", 0),
    ("sm3", 1, 11, 11, "main text", 0), ("sm3", 1, 13, 13, "main text", 0), ("sm3", 1, 20, 20, "reading", 0),
    ("sm3", 2, 47, 48, "article", 1), ("sm3", 2, 50, 50, "main text", 0), ("sm3", 2, 59, 59, "reading", 0),
    ("sm3", 3, 85, 85, "dialogue", 0), ("sm3", 3, 86, 86, "reading", 0),
    ("sm3", 4, 119, 119, "letter", 0), ("sm3", 4, 120, 120, "letter", 0), ("sm3", 4, 128, 128, "reading", 0),
    ("sm3", 5, 149, 150, "main text", 0), ("sm3", 5, 159, 159, "reading", 0),
    ("sm3", 6, 181, 181, "dialogue", 0), ("sm3", 6, 184, 184, "dialogue", 0), ("sm3", 6, 190, 191, "reading", 0),
    ("sm3", 7, 221, 222, "main text", 0), ("sm3", 7, 228, 228, "reading", 0),
    ("sm3", 8, 255, 256, "dialogue", 1), ("sm3", 8, 264, 264, "reading", 0),
    ("sm4", 1, 11, 11, "dialogue", 0), ("sm4", 1, 13, 13, "article", 1), ("sm4", 1, 14, 14, "letter", 1), ("sm4", 1, 16, 16, "list", 1),
    ("sm4", 2, 48, 49, "dialogue", 1), ("sm4", 2, 53, 53, "main text", 1),
    ("sm4", 3, 88, 89, "main text", 1), ("sm4", 3, 91, 91, "article", 1), ("sm4", 3, 93, 94, "article", 1),
    ("sm4", 4, 129, 130, "main text", 1), ("sm4", 4, 132, 133, "article", 1),
    ("sm4", 5, 170, 170, "dialogue", 1), ("sm4", 5, 172, 173, "article", 1), ("sm4", 5, 201, 202, "article", 1),
    ("sm4", 6, 207, 207, "dialogue", 1), ("sm4", 6, 209, 210, "reading", 1),
    ("sm4", 7, 246, 248, "article", 1),
    ("sm4", 8, 279, 283, "mixed", 1),
]


def decode(s):
    """The text layer of book 3 holds UTF-8 bytes as literal octal escapes (\\303\\244 = ä)."""
    return re.sub(r"(?:\\[0-7]{3})+", lambda m: bytes(int(x, 8) for x in re.findall(r"\\([0-7]{3})", m.group())).decode("utf-8", "replace"), s)


def ensure_sm3_pages():
    """Book 3 has a text layer, so no OCR: write its pages as sm3/p0001.txt ... like the OCR pages of the other books (from pdftotext -raw, pages split at the form feed)."""
    folder = DATA / "sm3"
    if (folder / "p0001.txt").exists():
        return
    folder.mkdir(parents=True, exist_ok=True)
    raw = subprocess.run(["pdftotext", "-raw", str(SM3_PDF), "-"], capture_output=True, text=True, check=True).stdout
    for n, text in enumerate(raw.split("\f")[:-1], 1):  # the last piece is empty (nothing after the final form feed)
        (folder / f"p{n:04d}.txt").write_text(decode(text), encoding="utf-8")


def page_texts(book):
    """{page number: text} of a book, from its per-page files (OCR for books 1, 2 and 4, the text layer for book 3)."""
    if book == "sm3":
        ensure_sm3_pages()
    return {int(f.stem[1:]): f.read_text(encoding="utf-8", errors="ignore") for f in sorted((DATA / book).glob("p*.txt"))}


def clean(text):
    lines = []
    for line in text.split("\n"):
        line = line.strip().replace("\t", " ")
        if re.match(r"^(Kappale\s*\d?|Q|[0-9]{1,3})$", line) or len(re.findall(r"[A-Za-zÅÄÖåäö]", line)) < 3:
            continue  # chapter header, margin symbol, page number, OCR noise
        line = re.sub(r"^(5|10|15|20|25|30|35|40|45|50|55|60)\s+(?=[A-ZÅÄÖa-zåäö\"“–-])", "", line)  # the line counter in the margin
        lines.append(line)
    return re.sub(r"(\w)-\n(\w)", r"\1\2", "\n".join(lines))


def prose_part(text):
    """The text before the first speaker line (all of it if there is none)."""
    for m in SPEAKER.finditer(text):
        if m.group(1) not in HEADER_WORDS:
            return text[:m.start()].strip()
    return text


def split_files(rows):
    """paragraph_texts (usable, the prose part), dialogue_texts (dialogues and the dialogue part of main texts), other_texts (lists, mixed items, too short)."""
    keep = ["id", "book", "book_level", "chapter", "pages", "kind", "title", "estimated_label", "n_words", "needs_review", "text"]
    para, dia, other = [], [], []
    for r in rows:
        prose = r["prose"] if r["usable"] else ""
        rest = r["text"][len(r["prose"]):].strip() if r["kind"] not in ("list", "mixed") else ""
        if r["usable"]:
            para.append({**r, "n_words": r["prose_words"], "text": prose})
        if len(rest.split()) >= 30:
            dia.append({**r, "id": r["id"] + "-dialogue", "kind": "dialogue", "n_words": len(rest.split()), "text": rest})
        if r["kind"] in ("list", "mixed") or (not r["usable"] and len(rest.split()) < 30):
            other.append(r)
    for name, items in (("paragraph_texts", para), ("dialogue_texts", dia), ("other_texts", other)):
        with open(DATA / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keep)
            w.writeheader()
            w.writerows([{k: x[k] for k in keep} for x in items])
        print(f"{name}.csv: {len(items)} texts, {sum(int(x['n_words']) for x in items)} words")


def label(book, chapter):
    lo, hi = LABEL_RANGE[book]
    return round(lo + (hi - lo) * (chapter - 1) / (CHAPTERS[book] - 1), 2)


def main():
    pages = {b: page_texts(b) for b in BOOK_LEVEL}
    rows = []
    for book, chapter, first, last, kind, review in SEGMENTS:
        text = "\n".join(clean(pages[book][p]) for p in range(first, last + 1))
        lines = text.split("\n")
        title = lines[0] if lines and len(lines[0]) < 60 and "." not in lines[0] and not lines[0].endswith(":") else ""
        prose = prose_part(text) if kind not in ("dialogue", "list", "mixed") else ""
        rows.append({"id": f"{book}-ch{chapter}-p{first}", "book": book, "book_level": BOOK_LEVEL[book], "chapter": chapter, "pages": f"{first}-{last}" if last > first else str(first),
                     "kind": kind, "title": title, "estimated_label": label(book, chapter), "n_words": len(text.split()), "needs_review": review,
                     "prose_words": len(prose.split()), "usable": int(len(prose.split()) >= MIN_WORDS), "prose": prose, "text": text})
    with open(DATA / "passages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    owner = {(r["book"], p): r for r in rows for p in range(int(r["pages"].split("-")[0]), int(r["pages"].split("-")[-1]) + 1)}
    with open(DATA / "page_index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["book", "page", "file", "passage_id", "kind", "first_line"])
        for book in BOOK_LEVEL:
            for n, t in sorted(pages[book].items()):
                o = owner.get((book, n))
                first = next((l for l in clean(t).split("\n")), "")[:70]
                w.writerow([book, n, f"{book}/p{n:04d}.txt", o["id"] if o else "", o["kind"] if o else "", first])
    split_files(rows)
    print(len(rows), "passages ->", DATA / "passages.csv")
    for b in BOOK_LEVEL:
        r = [x for x in rows if x["book"] == b]
        u = [x for x in r if x["usable"]]
        print(f"{b} ({BOOK_LEVEL[b]}): {len(r)} passages, of which {len(u)} usable paragraph texts ({sum(x['prose_words'] for x in u)} words), {sum(x['needs_review'] for x in u)} of them to review")


if __name__ == "__main__":
    main()
