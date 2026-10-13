"""Frozen BERT embeddings: one vector per text and per layer, cached on disk.

Each text is cut into windows of at most 510 word-pieces (+ [CLS] and [SEP] = 512), every window goes through BERT, and for every layer the hidden
states of the real word-pieces are averaged over the whole text (a token-weighted average of the windows: every word-piece counts once).
Layer 0 is the embedding layer, layers 1..12 are the transformer layers. Nothing is trained here.

    python bert_based/embeddings.py                              all splits, TurkuNLP/bert-base-finnish-cased-v1
    python bert_based/embeddings.py --model <hf name> --splits test --limit 40       a quick trial

Cache: outputs/embeddings/<model>/<split>.npy, float16, shape (texts, layers + 1, hidden). Work is saved every CHUNK texts, so an interrupted
run resumes where it stopped; a cache is reused only if the texts, the model and the window size are the same.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root
from core.dataset import SPLIT_FILES, load_split  # noqa: E402

DEFAULT_MODEL = "TurkuNLP/bert-base-finnish-cased-v1"
WINDOW = 510   # word-pieces per window, without [CLS] and [SEP]
CHUNK = 200    # texts per saved chunk
ROOT = Path(__file__).resolve().parents[1]


def cache_dir(model_name: str) -> Path:
    return ROOT / "outputs" / "embeddings" / model_name.replace("/", "__")


def load(model_name: str, split: str) -> np.ndarray:
    """The cached embeddings of a split as float32 (texts, layers + 1, hidden); run this module first to create them."""
    path = cache_dir(model_name) / f"{split}.npy"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing: run  python bert_based/embeddings.py --model {model_name} --splits {split}")
    return np.load(path).astype(np.float32)


def _fingerprint(texts, model_name):
    h = hashlib.sha1(f"{model_name}|{WINDOW}|".encode())
    for t in texts:
        h.update(t.encode("utf-8"))
    return h.hexdigest()


def embed(texts, tokenizer, model, device, batch_size=16):
    """(texts, layers + 1, hidden) float32: the token-averaged hidden states of every layer."""
    import torch

    n_layers, hidden = model.config.num_hidden_layers + 1, model.config.hidden_size
    ids = tokenizer(list(texts), add_special_tokens=False, truncation=False)["input_ids"]
    windows = [(i, seq[s:s + WINDOW]) for i, seq in enumerate(ids) for s in range(0, max(len(seq), 1), WINDOW)]
    windows.sort(key=lambda w: len(w[1]))  # similar lengths together: less padding
    total = np.zeros((len(texts), n_layers, hidden), dtype=np.float64)
    count = np.zeros(len(texts), dtype=np.float64)
    cls, sep, pad = tokenizer.cls_token_id, tokenizer.sep_token_id, tokenizer.pad_token_id
    for b in range(0, len(windows), batch_size):
        batch = windows[b:b + batch_size]
        width = max(len(w) for _, w in batch) + 2
        input_ids = torch.full((len(batch), width), pad, dtype=torch.long)
        attention = torch.zeros((len(batch), width), dtype=torch.long)
        real = torch.zeros((len(batch), width), dtype=torch.float32)  # 1 on the real word-pieces, 0 on [CLS], [SEP] and padding
        for k, (_, w) in enumerate(batch):
            row = [cls] + w + [sep]
            input_ids[k, :len(row)] = torch.tensor(row)
            attention[k, :len(row)] = 1
            real[k, 1:1 + len(w)] = 1
        with torch.no_grad():
            states = model(input_ids=input_ids.to(device), attention_mask=attention.to(device)).hidden_states
        real = real.to(device)
        stacked = torch.stack(states, dim=1)                      # (batch, layers + 1, width, hidden)
        sums = (stacked * real[:, None, :, None]).sum(dim=2).float().cpu().numpy()   # (batch, layers + 1, hidden)
        for k, (i, w) in enumerate(batch):
            total[i] += sums[k]
            count[i] += len(w)
    return (total / np.maximum(count, 1)[:, None, None]).astype(np.float32)


def run(model_name, splits, limit=None, batch_size=16):
    import torch
    from transformers import AutoModel, AutoTokenizer

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_hidden_states=True).eval().to(device)
    out_dir = cache_dir(model_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    for split in splits:
        texts = load_split(split)["text"].astype(str).tolist()[:limit]
        final, meta = out_dir / f"{split}.npy", out_dir / f"{split}.meta.json"
        fp = _fingerprint(texts, model_name)
        if limit is None and final.exists() and meta.exists() and json.loads(meta.read_text()).get("fingerprint") == fp:
            print(f"{split}: cached", flush=True)
            continue
        parts, start = [], time.time()
        for c, s in enumerate(range(0, len(texts), CHUNK)):
            part = out_dir / f"{split}.part{c:03d}.{fp[:8]}.npy"
            if not part.exists():
                np.save(part, embed(texts[s:s + CHUNK], tokenizer, model, device, batch_size).astype(np.float16))
            parts.append(part)
            done = min(s + CHUNK, len(texts))
            print(f"{split}: {done}/{len(texts)} texts, {time.time() - start:.0f}s", flush=True)
        arr = np.concatenate([np.load(p) for p in parts])
        target = out_dir / (f"{split}.trial.npy" if limit else f"{split}.npy")
        np.save(target, arr)
        if limit is None:
            meta.write_text(json.dumps({"fingerprint": fp, "model": model_name, "window": WINDOW, "shape": list(arr.shape)}))
        for p in parts:
            p.unlink()
        print(f"{split}: saved {target.name} {arr.shape}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--splits", nargs="*", default=list(SPLIT_FILES), choices=list(SPLIT_FILES))
    ap.add_argument("--limit", type=int, help="only the first N texts of each split (a trial; saved as <split>.trial.npy)")
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()
    run(args.model, args.splits, args.limit, args.batch_size)
