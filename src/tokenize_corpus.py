#!/usr/bin/env python3
"""Encode JSONL text into a compact token stream for random-init training."""

from __future__ import annotations

import argparse
import json
import re
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import sentencepiece as spm


def encode_record(row, tokenizer, weighted, focus_final_exponent=False):
    text = row["text"]
    if weighted and row.get("source") == "procedural":
        question, separator, continuation = text.partition("\n")
        if not separator or not continuation:
            raise ValueError("procedural record must contain a question and continuation")
        prompt_ids = tokenizer.encode(question + separator, out_type=int)
        parts = [(continuation, 4)]
        if focus_final_exponent and row.get("family") in {
            "symbolic", "elimination", "diverse_elimination"
        }:
            match = re.search(r"(-?\d+)(?=\.$)", continuation)
            if not match:
                raise ValueError("reasoning record lacks a final integer exponent")
            parts = [(continuation[:match.start()], 4), (match.group(1), 16),
                     (continuation[match.end():], 4)]
        ids = [tokenizer.bos_id(), *prompt_ids]
        weights = [1] * len(ids)
        for part, weight in parts:
            encoded = tokenizer.encode(part, out_type=int)
            ids.extend(encoded)
            weights.extend([weight] * len(encoded))
        ids.append(tokenizer.eos_id())
        weights.append(1)
    else:
        ids = [tokenizer.bos_id(), *tokenizer.encode(text, out_type=int), tokenizer.eos_id()]
        weights = [1] * len(ids)
    return ids, weights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--data", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--loss-weights-output", type=Path,
                        help="Optional uint8 token weights: procedural continuations receive weight 4")
    parser.add_argument("--focus-final-exponent", action="store_true",
                        help="Give final reasoning-example exponent tokens weight 16")
    args = parser.parse_args()
    if args.focus_final_exponent and not args.loss_weights_output:
        parser.error("--focus-final-exponent requires --loss-weights-output")
    if args.loss_weights_output and args.loss_weights_output.resolve() == args.output.resolve():
        parser.error("loss weights and token output must be distinct files")
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    if tokenizer.vocab_size() > np.iinfo(np.uint16).max:
        raise SystemExit("Vocabulary does not fit uint16")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.loss_weights_output:
        args.loss_weights_output.parent.mkdir(parents=True, exist_ok=True)
    documents = 0
    tokens = 0
    weight_file = args.loss_weights_output.open("wb") if args.loss_weights_output else nullcontext()
    with args.output.open("wb") as output, weight_file as weights_output:
        for path in args.data:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    ids, weights = encode_record(json.loads(line), tokenizer,
                                                 bool(weights_output), args.focus_final_exponent)
                    encoded = np.asarray(ids, dtype=np.uint16)
                    encoded.tofile(output)
                    if weights_output:
                        np.asarray(weights, dtype=np.uint8).tofile(weights_output)
                    tokens += len(encoded)
                    documents += 1
    if args.loss_weights_output:
        assert args.loss_weights_output.stat().st_size == tokens
    audit = {
        "tokenizer": str(args.tokenizer),
        "data": [str(path) for path in args.data],
        "output": str(args.output),
        "documents": documents,
        "tokens": tokens,
        "bytes": args.output.stat().st_size,
        "dtype": "uint16",
        "loss_weights_output": str(args.loss_weights_output) if args.loss_weights_output else None,
        "focus_final_exponent": args.focus_final_exponent,
    }
    args.output.with_suffix(args.output.suffix + ".json").write_text(
        json.dumps(audit, indent=2) + "\n"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
