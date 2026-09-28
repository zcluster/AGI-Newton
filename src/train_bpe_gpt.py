#!/usr/bin/env python3
"""Train a random-init GPT with a tokenizer learned only from sealed text."""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import sentencepiece as spm
import torch
from torch import nn
from torch.nn import functional as F

try:
    from train_random_init_smoke import LAW_PROBES
except ModuleNotFoundError:  # Supports importing as src.train_bpe_gpt in tests.
    from src.train_random_init_smoke import LAW_PROBES


class Attention(nn.Module):
    def __init__(self, width: int, heads: int):
        super().__init__()
        self.heads = heads
        self.head_width = width // heads
        self.qkv = nn.Linear(width, 3 * width, bias=False)
        self.projection = nn.Linear(width, width, bias=False)

    def forward(self, x):
        batch, length, width = x.shape
        qkv = self.qkv(x).view(batch, length, 3, self.heads, self.head_width)
        q, k, v = qkv.unbind(dim=2)
        q, k, v = (value.transpose(1, 2) for value in (q, k, v))
        attended = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.projection(attended.transpose(1, 2).contiguous().view(batch, length, width))


class Block(nn.Module):
    def __init__(self, width: int, heads: int):
        super().__init__()
        self.attention_norm = nn.LayerNorm(width)
        self.attention = Attention(width, heads)
        self.mlp_norm = nn.LayerNorm(width)
        self.mlp = nn.Sequential(
            nn.Linear(width, 4 * width, bias=False),
            nn.GELU(),
            nn.Linear(4 * width, width, bias=False),
        )

    def forward(self, x):
        x = x + self.attention(self.attention_norm(x))
        return x + self.mlp(self.mlp_norm(x))


class GPT(nn.Module):
    def __init__(self, vocab: int, context: int, width: int, heads: int, layers: int):
        super().__init__()
        self.context = context
        self.token = nn.Embedding(vocab, width)
        self.position = nn.Embedding(context, width)
        self.blocks = nn.ModuleList(Block(width, heads) for _ in range(layers))
        self.norm = nn.LayerNorm(width)
        self.output = nn.Linear(width, vocab, bias=False)
        self.output.weight = self.token.weight
        self.apply(self._initialize)

    @staticmethod
    def _initialize(module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, tokens):
        positions = torch.arange(tokens.shape[1], device=tokens.device)
        x = self.token(tokens) + self.position(positions)
        for block in self.blocks:
            x = block(x)
        return self.output(self.norm(x))


def precision_context(device, precision):
    if device.type != "cuda" or precision == "fp32":
        return nullcontext()
    dtype = torch.bfloat16 if precision == "bf16" else torch.float16
    return torch.autocast("cuda", dtype=dtype)


class TokenStream:
    def __init__(self, path: Path):
        self.array = np.memmap(path, dtype=np.uint16, mode="r")
        # PyTorch cannot advanced-index UInt16 tensors on CPU.  Keep the file
        # compact, but make one Int32 RAM copy for random batch sampling.
        self.tokens = torch.from_numpy(self.array.astype(np.int32))

    def batch(self, batch_size, context, device):
        starts = torch.randint(0, len(self.tokens) - context - 1, (batch_size,))
        offsets = torch.arange(context + 1)
        sequences = self.tokens[starts[:, None] + offsets].long().to(device)
        return sequences[:, :-1], sequences[:, 1:]


@torch.no_grad()
def validation_loss(model, stream, batch_size, context, device, precision, rounds=16):
    model.eval()
    values = []
    for _ in range(rounds):
        x, y = stream.batch(batch_size, context, device)
        with precision_context(device, precision):
            values.append(F.cross_entropy(model(x).flatten(0, 1), y.flatten()).item())
    model.train()
    return sum(values) / len(values)


@torch.no_grad()
def score(model, tokenizer, prompt, completion, device, precision):
    prompt_ids = tokenizer.encode(prompt, out_type=int)
    completion_ids = tokenizer.encode(completion, out_type=int)
    combined = (prompt_ids + completion_ids)[-model.context :]
    prompt_length = min(len(prompt_ids), len(combined) - len(completion_ids))
    tokens = torch.tensor(combined, device=device).unsqueeze(0)
    with precision_context(device, precision):
        logits = model(tokens[:, :-1])[0]
        losses = F.cross_entropy(
            logits[prompt_length - 1 :], tokens[0, prompt_length:], reduction="none"
        )
    return {"mean_nll": losses.float().mean().item(), "tokens": len(completion_ids)}


@torch.no_grad()
def evaluate_laws(model, tokenizer, device, precision):
    model.eval()
    results = []
    for probe in LAW_PROBES:
        scores = {
            name: score(model, tokenizer, probe["prompt"], candidate, device, precision)
            for name, candidate in probe["candidates"].items()
        }
        results.append({
            "id": probe["id"],
            "winner": min(scores, key=lambda key: scores[key]["mean_nll"]),
            "scores": scores,
        })
    return results


@torch.no_grad()
def generate(
    model, tokenizer, prompt, device, precision, length=100, temperature=0.8, minimum_length=0
):
    model.eval()
    tokens = tokenizer.encode(prompt, out_type=int)
    prompt_length = len(tokens)
    forbidden = {tokenizer.pad_id(), tokenizer.bos_id(), tokenizer.unk_id()}
    for _ in range(length):
        window = torch.tensor(tokens[-model.context :], device=device).unsqueeze(0)
        with precision_context(device, precision):
            logits = model(window)[0, -1].float()
        for token_id in forbidden:
            if token_id >= 0:
                logits[token_id] = -float("inf")
        if temperature > 0:
            next_id = torch.multinomial(torch.softmax(logits / temperature, dim=-1), 1).item()
        else:
            next_id = torch.argmax(logits).item()
        if next_id == tokenizer.eos_id() and len(tokens) - prompt_length >= minimum_length:
            break
        if next_id == tokenizer.eos_id():
            logits[next_id] = -float("inf")
            if temperature > 0:
                next_id = torch.multinomial(torch.softmax(logits / temperature, dim=-1), 1).item()
            else:
                next_id = torch.argmax(logits).item()
        tokens.append(next_id)
    return tokenizer.decode(tokens)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--context", type=int, default=512)
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--heads", type=int, default=12)
    parser.add_argument("--layers", type=int, default=12)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--warmup-steps", type=int, default=500)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--precision", choices=["fp32", "bf16", "fp16"], default="bf16")
    parser.add_argument("--seed", type=int, default=1686)
    parser.add_argument("--label", default="unnamed")
    parser.add_argument("--log-every", type=int, default=100)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)
        torch.backends.cuda.matmul.allow_tf32 = True
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    train = TokenStream(args.train)
    validation = TokenStream(args.validation)
    model = GPT(tokenizer.vocab_size(), args.context, args.width, args.heads, args.layers).to(device)
    if args.resume:
        resumed = torch.load(args.resume, map_location="cpu", weights_only=False)
        model.load_state_dict(resumed["model"])
    parameters = sum(parameter.numel() for parameter in model.parameters())
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, fused=device.type == "cuda")
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda" and args.precision == "fp16")
    initial = validation_loss(model, validation, args.batch_size, args.context, device, args.precision)
    started = time.time()
    last_loss = None
    for step in range(1, args.steps + 1):
        x, y = train.batch(args.batch_size, args.context, device)
        with precision_context(device, args.precision):
            loss = F.cross_entropy(model(x).flatten(0, 1), y.flatten())
        optimizer.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scale = min(1.0, step / args.warmup_steps)
        for group in optimizer.param_groups:
            group["lr"] = args.learning_rate * scale
        scaler.step(optimizer)
        scaler.update()
        last_loss = loss.item()
        if step == 1 or step % args.log_every == 0 or step == args.steps:
            allocated = torch.cuda.max_memory_allocated() / 1e9 if device.type == "cuda" else 0
            print(f"step={step} loss={last_loss:.4f} elapsed_s={time.time()-started:.1f} max_GB={allocated:.2f}", flush=True)

    final = validation_loss(model, validation, args.batch_size, args.context, device, args.precision)
    laws = evaluate_laws(model, tokenizer, device, args.precision)
    generations = {
        probe["id"]: generate(model, tokenizer, probe["prompt"], device, args.precision)
        for probe in LAW_PROBES
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    saved_args = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()}
    torch.save({"model": model.state_dict(), "args": saved_args}, args.output_dir / "model.pt")
    report = {
        "label": args.label,
        "parameters": parameters,
        "vocab_size": tokenizer.vocab_size(),
        "train_tokens": len(train.tokens),
        "validation_tokens": len(validation.tokens),
        "tokens_seen": args.steps * args.batch_size * args.context,
        "steps": args.steps,
        "training_seconds": time.time() - started,
        "initial_validation_loss": initial,
        "final_validation_loss": final,
        "final_validation_perplexity": math.exp(final),
        "last_train_loss": last_loss,
        "resumed_from": str(args.resume) if args.resume else None,
        "law_evaluation": laws,
        "free_generations": generations,
        "args": saved_args,
    }
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
