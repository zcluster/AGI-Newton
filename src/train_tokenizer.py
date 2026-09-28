#!/usr/bin/env python3
"""Train a tokenizer from the sealed corpus; no pretrained vocabulary is used."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sentencepiece as spm


def sentences(paths: list[Path], maximum_characters: int = 4000):
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                text = json.loads(line)["text"]
                for start in range(0, len(text), maximum_characters):
                    part = text[start : start + maximum_characters].strip()
                    if part:
                        yield part


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, nargs="+", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--vocab-size", type=int, default=8000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.output_dir / "pre1687_bpe"
    spm.SentencePieceTrainer.train(
        sentence_iterator=sentences(args.data),
        model_prefix=str(prefix),
        vocab_size=args.vocab_size,
        model_type="bpe",
        character_coverage=1.0,
        normalization_rule_name="identity",
        remove_extra_whitespaces=False,
        byte_fallback=True,
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
        hard_vocab_limit=True,
        train_extremely_large_corpus=True,
    )
    processor = spm.SentencePieceProcessor(model_file=str(prefix) + ".model")
    summary = {
        "training_data": [str(path) for path in args.data],
        "vocab_size": processor.vocab_size(),
        "model": str(prefix) + ".model",
        "pretrained_vocabulary": False,
        "normalization": "identity",
    }
    (args.output_dir / "tokenizer_audit.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
