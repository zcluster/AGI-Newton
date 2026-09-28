#!/usr/bin/env python3
"""Train and test a random-init byte GPT on sealed historical text.

This is intentionally a small, auditable experiment. It uses neither a
pretrained tokenizer nor pretrained weights, so a clean negative result is a
valid outcome; fluent output is not assumed.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from contextlib import nullcontext
from pathlib import Path

import torch
from torch import nn


VOCAB_SIZE = 257  # 256 byte values plus a document separator.

LAW_PROBES = [
    {
        "id": "kepler_huygens_derivation",
        "prompt": (
            "Kepler's observations give that the square of an orbital period is as the cube of its mean distance. "
            "For circular motion, the turning tendency is as the distance divided by the square of the period. "
            "Combining only these two relations, the turning tendency varies with distance as "
        ),
        "candidates": {
            "constant": "a constant.",
            "inverse": "the reciprocal of the distance.",
            "inverse_square": "the reciprocal square of the distance.",
            "inverse_cube": "the reciprocal cube of the distance.",
        },
    },
    {
        "id": "modern_direct",
        "prompt": "Question: How does the attractive power between the Earth and Moon vary with their distance? Answer: It varies as ",
        "candidates": {
            "constant": "a constant independent of distance.",
            "inverse": "the reciprocal of the distance.",
            "inverse_square": "the reciprocal square of the distance.",
            "inverse_cube": "the reciprocal cube of the distance.",
        },
    },
    {
        "id": "period_style",
        "prompt": "The attractive virtue betwixt the Earth and the Moon, as their distance increaseth, is diminished in the proportion of ",
        "candidates": {
            "constant": "no power of the distance.",
            "inverse": "the distance simply.",
            "inverse_square": "the duplicate ratio of the distance.",
            "inverse_cube": "the triplicate ratio of the distance.",
        },
    },
    {
        "id": "law_notation",
        "prompt": "Let r be the distance between the Earth and Moon. The attractive power F is most nearly proportional to ",
        "candidates": {
            "constant": "1.",
            "inverse": "1/r.",
            "inverse_square": "1/r^2.",
            "inverse_cube": "1/r^3.",
        },
    },
]


class TinyGPT(nn.Module):
    def __init__(self, context: int, width: int, heads: int, layers: int):
        super().__init__()
        self.context = context
        self.token = nn.Embedding(VOCAB_SIZE, width)
        self.position = nn.Embedding(context, width)
        block = nn.TransformerEncoderLayer(
            width,
            heads,
            dim_feedforward=4 * width,
            dropout=0.0,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.blocks = nn.TransformerEncoder(block, layers, norm=nn.LayerNorm(width))
        self.output = nn.Linear(width, VOCAB_SIZE, bias=False)
        self.output.weight = self.token.weight

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        length = tokens.shape[1]
        positions = torch.arange(length, device=tokens.device)
        hidden = self.token(tokens) + self.position(positions)
        causal = torch.triu(
            torch.ones(length, length, dtype=torch.bool, device=tokens.device), diagonal=1
        )
        return self.output(self.blocks(hidden, mask=causal))


def read_bytes(paths: list[Path], maximum: int) -> torch.Tensor:
    data: list[int] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                data.extend(json.loads(line)["text"].encode("utf-8", errors="replace"))
                data.append(256)
                if maximum and len(data) >= maximum:
                    break
        if maximum and len(data) >= maximum:
            break
    if maximum:
        del data[maximum:]
    return torch.tensor(data, dtype=torch.long)


def batches(data: torch.Tensor, batch_size: int, context: int, device: torch.device):
    starts = torch.randint(0, len(data) - context - 1, (batch_size,))
    x = torch.stack([data[start : start + context] for start in starts]).to(device)
    y = torch.stack([data[start + 1 : start + context + 1] for start in starts]).to(device)
    return x, y


def autocast_context(device: torch.device, precision: str):
    if device.type != "cuda" or precision == "fp32":
        return nullcontext()
    dtype = torch.bfloat16 if precision == "bf16" else torch.float16
    return torch.autocast(device_type="cuda", dtype=dtype)


@torch.no_grad()
def evaluate(model, data, batch_size, context, device, precision, rounds=8) -> float:
    model.eval()
    losses = []
    for _ in range(rounds):
        x, y = batches(data, batch_size, context, device)
        with autocast_context(device, precision):
            loss = nn.functional.cross_entropy(
                model(x).reshape(-1, VOCAB_SIZE), y.reshape(-1)
            )
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


@torch.no_grad()
def score_completion(model, prompt, completion, device, precision):
    prompt_bytes = list(prompt.encode("utf-8", errors="replace"))
    completion_bytes = list(completion.encode("utf-8", errors="replace"))
    combined = prompt_bytes + completion_bytes
    if len(combined) > model.context:
        removed = len(combined) - model.context
        combined = combined[removed:]
        prompt_length = max(1, len(prompt_bytes) - removed)
    else:
        prompt_length = len(prompt_bytes)
    if prompt_length < 1 or prompt_length >= len(combined):
        raise ValueError("Prompt/candidate cannot be scored at this context length")
    tokens = torch.tensor(combined, dtype=torch.long, device=device).unsqueeze(0)
    with autocast_context(device, precision):
        logits = model(tokens[:, :-1])[0]
        targets = tokens[0, 1:]
        first = prompt_length - 1
        losses = nn.functional.cross_entropy(
            logits[first:], targets[first:], reduction="none"
        )
    return {
        "mean_nll": losses.float().mean().item(),
        "sum_nll": losses.float().sum().item(),
        "bytes": len(completion_bytes),
    }


@torch.no_grad()
def run_law_probes(model, device, precision):
    model.eval()
    results = []
    votes: dict[str, int] = {}
    for probe in LAW_PROBES:
        scores = {
            name: score_completion(model, probe["prompt"], completion, device, precision)
            for name, completion in probe["candidates"].items()
        }
        winner = min(scores, key=lambda name: scores[name]["mean_nll"])
        votes[winner] = votes.get(winner, 0) + 1
        results.append(
            {"id": probe["id"], "prompt": probe["prompt"], "winner": winner, "scores": scores}
        )
    model.train()
    return {"probes": results, "votes": votes}


@torch.no_grad()
def generate(model, prompt, device, precision, length=240, temperature=0.8):
    model.eval()
    tokens = list(prompt.encode("utf-8", errors="replace"))
    for _ in range(length):
        window = torch.tensor(
            tokens[-model.context :], dtype=torch.long, device=device
        ).unsqueeze(0)
        with autocast_context(device, precision):
            logits = model(window)[0, -1].float() / temperature
        logits[256] = -float("inf")
        tokens.append(torch.multinomial(torch.softmax(logits, dim=-1), 1).item())
    model.train()
    return bytes(value for value in tokens if value < 256).decode("utf-8", errors="replace")


def choose_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def choose_precision(requested: str, device: torch.device) -> str:
    if requested != "auto":
        return requested
    if device.type == "cuda" and torch.cuda.is_bf16_supported():
        return "bf16"
    return "fp32"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, nargs="+", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument(
        "--precision", choices=["auto", "fp32", "bf16", "fp16"], default="auto"
    )
    parser.add_argument("--max-bytes", type=int, default=0, help="0 uses all input text")
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--context", type=int, default=256)
    parser.add_argument("--width", type=int, default=384)
    parser.add_argument("--heads", type=int, default=6)
    parser.add_argument("--layers", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--generation-length", type=int, default=160)
    parser.add_argument("--seed", type=int, default=1686)
    parser.add_argument("--label", default="unnamed")
    args = parser.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = choose_device(args.device)
    precision = choose_precision(args.precision, device)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)
        torch.backends.cuda.matmul.allow_tf32 = True
    corpus = read_bytes(args.data, args.max_bytes)
    if len(corpus) < 2 * args.context + 2:
        raise SystemExit("Corpus is too small for the requested context length")
    split = int(0.95 * len(corpus))
    train, validation = corpus[:split], corpus[split:]

    model = TinyGPT(args.context, args.width, args.heads, args.layers).to(device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    optimizer_kwargs = {"lr": args.learning_rate}
    if device.type == "cuda":
        optimizer_kwargs["fused"] = True
    optimizer = torch.optim.AdamW(model.parameters(), **optimizer_kwargs)
    scaler = torch.amp.GradScaler(
        "cuda", enabled=(device.type == "cuda" and precision == "fp16")
    )
    initial = evaluate(model, validation, args.batch_size, args.context, device, precision)
    losses = []
    started = time.time()
    for step in range(1, args.steps + 1):
        x, y = batches(train, args.batch_size, args.context, device)
        with autocast_context(device, precision):
            loss = nn.functional.cross_entropy(
                model(x).reshape(-1, VOCAB_SIZE), y.reshape(-1)
            )
        optimizer.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        losses.append(loss.item())
        if step == 1 or step % 100 == 0 or step == args.steps:
            print(
                f"step={step} train_loss={loss.item():.4f} "
                f"elapsed_s={time.time() - started:.1f}",
                flush=True,
            )
    duration = time.time() - started
    final = evaluate(model, validation, args.batch_size, args.context, device, precision)
    probes = run_law_probes(model, device, precision)
    generations = {
        probe["id"]: generate(
            model,
            probe["prompt"],
            device,
            precision,
            length=args.generation_length,
        )
        for probe in LAW_PROBES
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    saved_args = {
        key: [str(item) for item in value]
        if isinstance(value, list)
        else str(value)
        if isinstance(value, Path)
        else value
        for key, value in vars(args).items()
    }
    torch.save({"model": model.state_dict(), "args": saved_args}, args.output_dir / "model.pt")
    report = {
        "purpose": "real quick-stab random-init language-model experiment; not yet a rediscovery claim",
        "label": args.label,
        "data": [str(path) for path in args.data],
        "device": str(device),
        "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        "precision": precision,
        "parameters": parameter_count,
        "bytes": len(corpus),
        "steps": args.steps,
        "tokens_seen": args.steps * args.batch_size * args.context,
        "training_seconds": duration,
        "initial_validation_loss": initial,
        "final_validation_loss": final,
        "initial_perplexity": math.exp(initial),
        "final_perplexity": math.exp(final),
        "last_train_loss": losses[-1],
        "law_evaluation": probes,
        "free_generation": generations[LAW_PROBES[0]["id"]],
        "free_generations": generations,
        "limitations": [
            "byte tokenizer and small model",
            f"training mixture contains {len(corpus)/1_000_000:.1f} MB of byte-level text",
            "candidate ranking is diagnostic and is not equivalent to an open-ended derivation",
            "machine-reviewed pilot editions are not yet publication-grade human-audited data",
        ],
    }
    (args.output_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
