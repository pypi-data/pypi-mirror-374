import argparse, os, sys
import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel

TEXT_CANDIDATES = ["func", "code", "functionSource", "source", "text"]
LABEL_CANDIDATES = ["target", "label", "y", "class", "category"]

def pick_col(df, wanted, candidates):
    if wanted and wanted in df.columns: return wanted
    for c in candidates:
        if c in df.columns: return c
    raise ValueError(f"None of the expected columns found: {candidates}")

def load_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".json", ".jsonl"):
        # try both normal and lines JSON
        try:
            return pd.read_json(path)
        except Exception:
            return pd.read_json(path, lines=True)
    raise ValueError("Supported inputs: .csv, .json, .jsonl")

def device_from_arg(arg: str):
    arg = (arg or "cpu").lower()
    if arg == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if arg == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

def encode(texts, tokenizer, model, device, batch_size=16, max_len=512):
    vecs = []
    model.eval()
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), batch_size), desc="Encoding"):
            batch = texts[i:i+batch_size]
            enc = tokenizer(
                batch, padding=True, truncation=True, max_length=max_len,
                return_tensors="pt"
            )
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc).last_hidden_state[:, 0, :]  # CLS token
            vecs.append(out.detach().cpu())
    X = torch.cat(vecs, dim=0).numpy().astype("float32")
    return X

def main():
    ap = argparse.ArgumentParser(description="Make cached features (.npz) from code text using CodeBERT.")
    ap.add_argument("--input", required=True, help="CSV/JSON file with code and labels")
    ap.add_argument("--text-col", default=None, help="Column name for code text (auto-detect if omitted)")
    ap.add_argument("--label-col", default=None, help="Column name for labels (auto-detect if omitted)")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"], help="Where to run embeddings")
    ap.add_argument("--model", default="microsoft/codebert-base", help="HF model name")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=512)
    ap.add_argument("--out", default="features_cpu.npz", help="Output .npz path")
    args = ap.parse_args()

    df = load_table(args.input)
    text_col = pick_col(df, args.text_col, TEXT_CANDIDATES)
    label_col = pick_col(df, args.label_col, LABEL_CANDIDATES)

    # drop na
    df = df[[text_col, label_col]].dropna()
    texts = df[text_col].astype(str).tolist()
    y = df[label_col].to_numpy()

    device = device_from_arg(args.device)
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModel.from_pretrained(args.model).to(device)

    X = encode(texts, tokenizer, model, device, batch_size=args.batch_size, max_len=args.max_len)
    np.savez(args.out, X=X, y=y)
    print(f"Saved {args.out} with X.shape={X.shape}, y.shape={y.shape}")

if __name__ == "__main__":
    main()
