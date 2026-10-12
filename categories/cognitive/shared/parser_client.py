"""Client of the Turku dependency-parser server that Revita uses (reachable from the Revita hosts, e.g. through an SSH
tunnel:  ssh -N -L 7689:hpz440-2.cs.helsinki.fi:7689 revita_staging ).

The server takes JSON {"text": ...} and returns {"conll": ...}, CoNLL-U with the sentences it found. PARSER_URL sets the
address (default http://localhost:7689/model). Parses are cached on disk by text hash, so a text is parsed once.
"""
import hashlib
import json
import os
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PARSER_URL = os.environ.get("PARSER_URL", "http://localhost:7689/model")
CACHE = Path(__file__).resolve().parents[1] / "outputs" / "parse_cache.jsonl"
_lock = threading.Lock()


def _post(text: str, retries: int = 3) -> str:
    request = urllib.request.Request(PARSER_URL, data=json.dumps({"text": text}).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            return json.loads(urllib.request.urlopen(request, timeout=300).read())["conll"]
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def read_conllu(conll: str) -> list[list[dict]]:
    """CoNLL-U -> sentences, each a list of tokens {id, form, upos, feats, head, deprel}; multiword and empty nodes are skipped."""
    sentences = []
    for block in conll.strip().split("\n\n"):
        tokens = []
        for line in block.split("\n"):
            c = line.split("\t")
            if len(c) < 8 or not c[0].isdigit():
                continue
            tokens.append({"id": int(c[0]), "form": c[1], "upos": c[3], "feats": c[5], "head": int(c[6]), "deprel": c[7]})
        if tokens:
            sentences.append(tokens)
    return sentences


def parse_texts(texts: list[str], workers: int = 1) -> list[list[list[dict]]]:
    """Per text, its parsed sentences (see read_conllu). Only texts missing from the cache are sent to the server, one request at a time
    (the server resets the connection when several arrive at once; raise `workers` only if it copes)."""
    cache = {}
    if CACHE.exists():
        with open(CACHE, encoding="utf-8") as f:
            cache = dict(json.loads(line) for line in f)
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
    todo = {k: t for k, t in zip(keys, texts) if k not in cache}
    if todo:
        CACHE.parent.mkdir(exist_ok=True)

        def work(item):
            k, t = item
            conll = _post(t)
            with _lock, open(CACHE, "a", encoding="utf-8") as f:
                f.write(json.dumps([k, conll]) + "\n")
            cache[k] = conll

        with ThreadPoolExecutor(workers) as pool:
            list(pool.map(work, todo.items()))
    return [read_conllu(cache[k]) for k in keys]
