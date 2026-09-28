#!/usr/bin/env python3
"""Encode JSONL text into a compact token stream for random-init training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import sentencepiece as spm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--data", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    if tokenizer.vocab_size() > np.iinfo(np.uint16).max:
        raise SystemExit("Vocabulary does not fit uint16")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    documents = 0
    tokens = 0
    with args.output.open("wb") as output:
        for path in args.data:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    ids = [tokenizer.bos_id()]
                    ids.extend(tokenizer.encode(json.loads(line)["text"], out_type=int))
                    ids.append(tokenizer.eos_id())
                    encoded = np.asarray(ids, dtype=np.uint16)
                    encoded.tofile(output)
                    tokens += len(encoded)
                    documents += 1
    audit = {
        "tokenizer": str(args.tokenizer),
        "data": [str(path) for path in args.data],
        "output": str(args.output),
        "documents": documents,
        "tokens": tokens,
        "bytes": args.output.stat().st_size,
        "dtype": "uint16",
    }
    args.output.with_suffix(args.output.suffix + ".json").write_text(
        json.dumps(audit, indent=2) + "\n"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
