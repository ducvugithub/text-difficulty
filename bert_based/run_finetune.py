"""BERT with a regression head, fine-tuned: the whole model is trained to predict the difficulty label.

A BERT model with a linear regression head (one output, mean squared error on the standardised label). Training examples are the windows of at most 510 word-pieces of
every training text, each with its text's label; a text is predicted as the average of its windows' predictions. The epoch is chosen on the real-Finnish valid texts, so the
test set is never used to choose anything. Graded on the same 865 real-Finnish test texts as the curated experiments.

    python bert_based/run_finetune.py --train train_native            real-Finnish train texts (2,332)
    python bert_based/run_finetune.py --train train_all               all train texts (8,293)
    python bert_based/run_finetune.py --train train_native --limit 64 --epochs 1      a quick trial (nothing is saved)

Each run writes bert_based/reports/runs/finetune_<train>.json; the report bert_based/reports/BERT_FINETUNE.md is rebuilt from all runs that exist.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root
from bert_based.embeddings import DEFAULT_MODEL, WINDOW  # noqa: E402
from core import predictions  # noqa: E402
from core.dataset import TRAIN_SETS, load_split, native_mask, train_mask  # noqa: E402
from core.evaluate import bootstrap_mae, ci, metrics  # noqa: E402
from core.reporting import confusion_md, pct, steps, table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "bert_based" / "reports" / "runs"
REPORT = ROOT / "bert_based" / "reports" / "BERT_FINETUNE.md"
CURATED_RUNS = ROOT / "curated_features" / "modeling" / "reports" / "runs"
CURATED_CONTEXT = [("vocab_grammar_coverage_cognitive", "best curated set: vocab + grammar_coverage + cognitive (new)"),
                   ("original_all", "curated reference: all (old)"), ("surface", "curated reference: surface (new)")]


def windows_of(tokenizer, texts, window=WINDOW):
    ids = tokenizer(list(texts), add_special_tokens=False, truncation=False)["input_ids"]
    return [(i, seq[s:s + window]) for i, seq in enumerate(ids) for s in range(0, max(len(seq), 1), window)]


def collate(tokenizer, batch):
    import torch

    width = max(len(w) for _, w in batch) + 2
    input_ids = torch.full((len(batch), width), tokenizer.pad_token_id, dtype=torch.long)
    attention = torch.zeros((len(batch), width), dtype=torch.long)
    for k, (_, w) in enumerate(batch):
        row = [tokenizer.cls_token_id] + w + [tokenizer.sep_token_id]
        input_ids[k, :len(row)] = torch.tensor(row)
        attention[k, :len(row)] = 1
    return input_ids, attention


def predict(model, tokenizer, texts, device, mean, std, window=WINDOW, batch_size=16):
    """One prediction per text: the average over its windows, back on the label scale."""
    import torch

    model.eval()
    wins = sorted(windows_of(tokenizer, texts, window), key=lambda w: len(w[1]))
    total, count = np.zeros(len(texts)), np.zeros(len(texts))
    with torch.no_grad():
        for b in range(0, len(wins), batch_size):
            batch = wins[b:b + batch_size]
            ids, att = collate(tokenizer, batch)
            out = model(input_ids=ids.to(device), attention_mask=att.to(device)).logits.squeeze(-1).float().cpu().numpy()
            for k, (i, _) in enumerate(batch):
                total[i] += out[k]
                count[i] += 1
    return total / np.maximum(count, 1) * std + mean


def run(args):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=1).to(device)

    train_df, valid_df, test_df = load_split("train"), load_split("valid"), load_split("test")
    train_df = train_df[train_mask(train_df, args.train)]
    train_df = train_df.iloc[:args.limit] if args.limit else train_df
    valid_df = valid_df[native_mask(valid_df)]
    mean, std = float(train_df["label"].mean()), float(train_df["label"].std())
    texts, labels = train_df["text"].astype(str).tolist(), train_df["label"].to_numpy()
    wins = windows_of(tokenizer, texts, args.window)
    target = {i: (labels[i] - mean) / std for i in range(len(texts))}
    steps_per_epoch = int(np.ceil(len(wins) / (args.batch_size * args.accum)))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, int(0.1 * steps_per_epoch * args.epochs), steps_per_epoch * args.epochs)
    print(f"{args.train}: {len(texts)} texts -> {len(wins)} windows, {steps_per_epoch} steps per epoch, device {device}", flush=True)

    history, best, start = [], None, time.time()
    valid_texts, valid_y = valid_df["text"].astype(str).tolist(), valid_df["label"].to_numpy()
    test_texts, test_y = test_df["text"].astype(str).tolist(), test_df["label"].to_numpy()
    for epoch in range(1, args.epochs + 1):
        model.train()
        order = rng.permutation(len(wins))
        running = 0.0
        optimizer.zero_grad()
        for n, s in enumerate(range(0, len(order), args.batch_size), 1):
            batch = [wins[j] for j in order[s:s + args.batch_size]]
            ids, att = collate(tokenizer, batch)
            y = torch.tensor([target[i] for i, _ in batch], dtype=torch.float32, device=device)
            loss = torch.nn.functional.mse_loss(model(input_ids=ids.to(device), attention_mask=att.to(device)).logits.squeeze(-1).float(), y)
            (loss / args.accum).backward()  # gradients of `accum` small batches add up to one larger batch
            running += float(loss) / args.accum
            if n % args.accum == 0 or s + args.batch_size >= len(order):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
        valid_pred = predict(model, tokenizer, valid_texts, device, mean, std, args.window)
        valid_mae = float(np.abs(valid_pred - valid_y).mean())
        history.append({"epoch": epoch, "train_loss": running / steps_per_epoch, "valid_mae": valid_mae})
        print(f"epoch {epoch}: train loss {running / steps_per_epoch:.3f}, valid (real Finnish) MAE {valid_mae:.3f}, {time.time() - start:.0f}s", flush=True)
        if best is None or valid_mae < best[0]:  # keep the predictions of the epoch that is best on valid
            best = (valid_mae, epoch, predict(model, tokenizer, test_texts, device, mean, std, args.window))
    _, best_epoch, test_pred = best
    result = {"model": args.model, "train": args.train, "epochs": args.epochs, "lr": args.lr, "batch_size": args.batch_size * args.accum, "window": args.window, "history": history, "best_epoch": best_epoch,
              "windows": len(wins), "seconds": time.time() - start, "test": {k: v for k, v in metrics(test_y, test_pred).items() if k != "per_label"},
              "test_ci": ci(bootstrap_mae(test_y, test_pred)), "test_pred": [float(x) for x in test_pred]}
    print(f"best epoch {best_epoch}: test MAE {result['test']['mae']:.3f}", flush=True)
    if not args.limit:
        RUNS.mkdir(parents=True, exist_ok=True)
        (RUNS / f"finetune_{args.train}.json").write_text(json.dumps(result), encoding="utf-8")
        predictions.save("bert", "finetune", "regression_head", args.train, test_y, test_pred)
        write_report()


def curated_context(train):
    path = CURATED_RUNS / f"{train}_main.md"
    if not path.exists():
        return []
    rows = {r[0]: r for r in table(path.read_text(encoding="utf-8"), "## test: gradient boosting")}
    return [(label, rows[k]) for k, label in CURATED_CONTEXT if k in rows]


def write_report():
    runs = {t: json.loads((RUNS / f"finetune_{t}.json").read_text(encoding="utf-8")) for t in TRAIN_SETS if (RUNS / f"finetune_{t}.json").exists()}
    if not runs:
        return
    y_test = load_split("test")["label"].to_numpy()
    first = next(iter(runs.values()))
    L = ["# BERT with a regression head, fine-tuned", "",
         f"Generated by `bert_based/run_finetune.py`. Model: `{first['model']}`, the whole model is trained.", "", "## Summary", ""]
    for t, r in runs.items():
        L.append(f"- Trained on {TRAIN_SETS[t]}: average miss **{r['test']['mae']:.3f}** [{r['test_ci'][0]:.3f}, {r['test_ci'][1]:.3f}] on the test set (epoch {r['best_epoch']} of {r['epochs']}, "
                 f"chosen on the real-Finnish valid texts).")
    L += ["", "## How to read the numbers", "",
          "- **Average miss (MAE)**: average distance between predicted and true label; smaller is better. One label step is 0.5.",
          "- **Exactly right / within one step**: the prediction, rounded to the nearest half step, equals the label / is off by at most 0.5.",
          "- **95% interval**: from resampling the 865 test texts; overlapping intervals may be noise.", "",
          "## Setup", "",
          f"- BERT with one linear output (regression), trained with mean squared error on the label standardised by the training mean and spread, AdamW, learning rate {first['lr']:g}, "
          f"effective batch size {first['batch_size']}, {first['epochs']} epochs, linear warm-up and decay.",
          f"- Training examples are the windows of at most {first.get('window', WINDOW)} word-pieces of every training text; a text is predicted as the average over its windows.",
          "- The epoch is chosen on the real-Finnish valid texts (263), so the test set is never used to choose anything.",
          "- Test set: the same 865 real-Finnish texts as in the curated results, so the numbers are comparable with `curated_features/modeling/reports/RESULTS.md`.", "",
          "## Results", ""]
    for t, r in runs.items():
        L += [f"### Trained on {TRAIN_SETS[t]}", "", "| model | average miss (MAE) [95% interval] | in label steps | exactly right | within one step |", "|---|---|---:|---:|---:|",
              f"| **BERT, fine-tuned** | {r['test']['mae']:.3f} [{r['test_ci'][0]:.3f}, {r['test_ci'][1]:.3f}] | {steps(r['test']['mae'])} | {pct(r['test']['accuracy'])} | {pct(r['test']['accuracy_1step'])} |"]
        for label, c in curated_context(t):
            L.append(f"| *{label}* | {c[3]} {c[4]} | {steps(c[3])} | {c[5]} | {c[6]} |")
        L += ["", "Per epoch (valid MAE on the real-Finnish valid texts):", "", "| epoch | train loss | valid MAE |", "|---:|---:|---:|"]
        L += [f"| {h['epoch']}{' (chosen)' if h['epoch'] == r['best_epoch'] else ''} | {h['train_loss']:.3f} | {h['valid_mae']:.3f} |" for h in r["history"]]
        L += [f"", f"Training took {r['seconds'] / 60:.0f} minutes.", ""]
    if "train_native" in runs:
        L += ["### Confusion matrix (trained on real-Finnish rows)", "",
              "Each row is the true label, each column the predicted label (rounded to the nearest half step). A row adds up to 100%; the **bold** cell is the share predicted exactly right.", ""]
        L += confusion_md(y_test, np.array(runs["train_native"]["test_pred"]))
    L += ["", "## Reproduce", "", "```", "python bert_based/run_finetune.py --train train_native", "python bert_based/run_finetune.py --train train_all", "```", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L), encoding="utf-8")
    print("report ->", REPORT)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--train", default="train_native", choices=list(TRAIN_SETS))
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch-size", type=int, default=8, help="windows per step on the device (memory); the effective batch is batch-size x accum")
    ap.add_argument("--accum", type=int, default=2, help="steps whose gradients are added before one update")
    ap.add_argument("--window", type=int, default=WINDOW, help="word-pieces per window (shorter = less memory)")
    ap.add_argument("--limit", type=int, help="only the first N training texts, and nothing is saved (a quick trial)")
    run(ap.parse_args())
