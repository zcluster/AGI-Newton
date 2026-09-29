"""Small, auditable equation-generation pipeline; no pretrained model downloads."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

GRID = torch.linspace(-2, 2, 9)
GRAMMAR = torch.tensor(list(itertools.product(range(9), repeat=3)))
# A split over equation identities, not observation rows. This is a finite toy DSL.
HELD_OUT = torch.tensor([
    int(hashlib.sha256(bytes(row)).hexdigest()[:8], 16) % 5 == 0
    for row in GRAMMAR.tolist()
])
TRAIN_IDS = GRAMMAR[~HELD_OUT]
TEST_IDS = GRAMMAR[HELD_OUT]


def predict(ids, x):
    coefficients = GRID.to(x.device)[ids]
    a, b, c = coefficients.unbind(-1)
    return a[:, None] + b[:, None] * x + c[:, None] * x.square()


def worlds(count, seed, split):
    """Generate on CPU; use a saved tensor file for exact cross-platform inputs."""
    g = torch.Generator().manual_seed(seed)
    pool = TEST_IDS if split == "heldout" else TRAIN_IDS
    ids = pool[torch.randint(len(pool), (count,), generator=g)]
    x = torch.linspace(-1, 1, 8).repeat(count, 1)
    x = x + 0.015 * torch.randn(x.shape, generator=g)
    test_x = torch.linspace(1.25, 2, 16).repeat(count, 1)
    if split == "ood":
        amplitude = 1 + torch.rand(count, 1, generator=g)
        frequency = 2 + torch.rand(count, 1, generator=g)
        y = amplitude * torch.sin(frequency * x)
        test_y = amplitude * torch.sin(frequency * test_x)
    else:
        y, test_y = predict(ids, x), predict(ids, test_x)
    return {"observed": torch.stack((x, y), -1), "test_x": test_x,
            "test_y": test_y}


class TheoryTransformer(nn.Module):
    """Numeric observation prefix + causal output of three coefficient tokens."""
    def __init__(self):
        super().__init__()
        self.observation = nn.Linear(2, 64)
        self.token = nn.Embedding(10, 64)  # 9 coefficients + BOS
        self.position = nn.Parameter(torch.randn(1, 11, 64) * 0.02)
        layer = nn.TransformerEncoderLayer(
            64, 4, dim_feedforward=128, dropout=0, batch_first=True,
            norm_first=True, activation="gelu")
        self.blocks = nn.TransformerEncoder(layer, 2, enable_nested_tensor=False)
        self.head = nn.Linear(64, 9)

    def forward(self, observations, prefix):
        obs = self.observation(observations / 4)
        tokens = self.token(prefix)
        hidden = torch.cat((obs, tokens), 1)
        size = hidden.shape[1]
        # Observation prefix is bidirectional; generated tokens cannot see future tokens.
        mask = torch.ones(size, size, device=hidden.device, dtype=torch.bool).triu(1)
        mask[:8, :8] = False
        hidden = self.blocks(hidden + self.position[:, :size], mask=mask)
        return self.head(hidden[:, 8:])

    def generate(self, observations, stochastic=False):
        prefix = torch.full((len(observations), 1), 9, device=observations.device,
                            dtype=torch.long)
        log_prob, entropy, selected = [], [], []
        for _ in range(3):
            logits = self(observations, prefix)[:, -1]
            distribution = torch.distributions.Categorical(logits=logits)
            action = distribution.sample() if stochastic else logits.argmax(-1)
            log_prob.append(distribution.log_prob(action))
            entropy.append(distribution.entropy())
            selected.append(action)
            prefix = torch.cat((prefix, action[:, None]), 1)
        return (torch.stack(selected, 1), torch.stack(log_prob, 1).sum(1),
                torch.stack(entropy, 1).mean(1))


def error(ids, observations):
    x, y = observations.unbind(-1)
    mse = (predict(ids, x) - y).square().mean(1)
    return mse / (y.square().mean(1) + 1)


@torch.no_grad()
def enumerate_best(observations):
    """Strong symbolic baseline and optional SFT teacher: uses observations only."""
    candidates = GRAMMAR.to(observations.device)
    scores = []
    for obs in observations.split(32):
        x, y = obs.unbind(-1)
        coeff = GRID.to(obs.device)[candidates]
        prediction = (coeff[None, :, 0, None] + coeff[None, :, 1, None] * x[:, None]
                      + coeff[None, :, 2, None] * x[:, None].square())
        scores.append(candidates[(prediction - y[:, None]).square().mean(-1).argmin(1)])
    return torch.cat(scores)


def objective(ids, observations):
    # Reward queries only the training observation set, never extrapolation test points.
    complexity = (ids != 4).float().mean(1)
    return torch.exp(-4 * error(ids, observations)) - 0.01 * complexity


def choose_device(name):
    if name == "auto":
        name = "cuda" if torch.cuda.is_available() else (
            "mps" if torch.backends.mps.is_available() else "cpu")
    if name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; refusing silent CPU fallback")
    if name == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS requested but unavailable; use --device cpu explicitly")
    return torch.device(name)


def digest(state):
    h = hashlib.sha256()
    for key, value in sorted(state.items()):
        h.update(key.encode())
        h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def save_checkpoint(path, model, optimizer, step, stage):
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    torch.save({"model": state, "optimizer": optimizer.state_dict(), "step": step,
                "stage": stage, "architecture": "numeric-prefix-transformer-v1",
                "weights_sha256": digest(state)}, path)


@torch.no_grad()
def evaluate(model, episodes, device):
    result, examples = {}, []
    for split, batch in episodes.items():
        obs = batch["observed"].to(device)
        ids = torch.cat([model.generate(part)[0].cpu() for part in obs.split(64)])
        fit = error(ids, batch["observed"])
        mse = (predict(ids, batch["test_x"]) - batch["test_y"]).square().mean(1)
        scale = batch["test_y"].square().mean(1) + 1
        result[split] = {"observation_nmse": fit.mean().item(),
                         "extrapolation_nmse": (mse / scale).mean().item(),
                         "exact_observation_fit_rate": (fit < 1e-6).float().mean().item()}
        examples.append({"split": split, "coefficients": GRID[ids[0]].tolist(),
                         "x": batch["test_x"][0].tolist(),
                         "predicted": predict(ids[:1], batch["test_x"][:1])[0].tolist(),
                         "actual": batch["test_y"][0].tolist()})
    return result, examples


@torch.no_grad()
def archive(model, observed, device):
    """Per-world non-dominated candidates; no hidden test data admitted."""
    obs = observed[:1].to(device).repeat(64, 1, 1)
    ids = model.generate(obs, stochastic=True)[0]
    # unique_dim is unavailable on PyTorch 2.8 MPS. Archive housekeeping is tiny.
    ids = torch.unique(torch.cat((ids, enumerate_best(obs[:1]))).cpu(), dim=0).to(device)
    errors = error(ids, obs[:1].expand(len(ids), -1, -1))
    complexity = (ids != 4).sum(1)
    records = []
    for i in range(len(ids)):
        dominates = ((errors <= errors[i]) & (complexity <= complexity[i]) &
                     ((errors < errors[i]) | (complexity < complexity[i])))
        if not dominates.any():
            records.append({"coefficients": GRID[ids[i].cpu()].tolist(),
                            "observation_nmse": errors[i].item(),
                            "nonzero_terms": complexity[i].item()})
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--device", choices=["auto", "cpu", "mps", "cuda"], default="auto")
    p.add_argument("--out", type=Path, default=Path("runs/local"))
    p.add_argument("--sft-steps", type=int, default=150)
    p.add_argument("--rl-steps", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--eval-worlds", type=int, default=64)
    p.add_argument("--seed", type=int, default=20260911)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--evaluation-worlds", type=Path,
                   help="Reuse materialized test tensors for cross-device comparison")
    p.add_argument("--eval-only", action="store_true")
    args = p.parse_args()
    if min(args.sft_steps, args.rl_steps) < 0 or min(args.batch_size, args.eval_worlds) < 1:
        p.error("steps must be nonnegative; batch size and eval worlds must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "report.json").exists():
        p.error("output already contains a report; choose a fresh --out directory")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(4)
    device = choose_device(args.device)
    model = TheoryTransformer().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    if args.checkpoint:
        ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
        if ckpt["architecture"] != "numeric-prefix-transformer-v1":
            raise ValueError("checkpoint architecture mismatch")
        if digest(ckpt["model"]) != ckpt["weights_sha256"]:
            raise ValueError("checkpoint weights hash mismatch")
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        # Explicitly relocate Adam tensors for cross-device resume.
        for state in optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor) and k != "step":
                    state[k] = v.to(device)
    environment = {"python": platform.python_version(), "torch": torch.__version__,
                   "cuda_build": torch.version.cuda, "device": str(device),
                   "platform": platform.platform(),
                   "parameters": sum(v.numel() for v in model.parameters()),
                   "precision": "float32", "seed": args.seed}
    if device.type == "cuda":
        environment.update(gpu=torch.cuda.get_device_name(),
                           capability=list(torch.cuda.get_device_capability()))
    print(json.dumps(environment), flush=True)
    initial_hash = digest(model.state_dict())
    # Tensor-level accelerator check, including backward, not just CUDA visibility.
    t = torch.randn(128, 128, device=device, requires_grad=True)
    t.square().mean().backward()
    assert torch.isfinite(t.grad).all()
    history, started = [], time.time()
    if not args.eval_only:
        for stage, steps in [("sft", args.sft_steps), ("rl", args.rl_steps)]:
            stage_initial = digest(model.state_dict())
            for step in range(steps):
                seed = args.seed + step + (100000 if stage == "rl" else 0)
                observations = worlds(args.batch_size, seed, "train")["observed"].to(device)
                model.train()
                if stage == "sft":
                    teacher = enumerate_best(observations)
                    bos = torch.full((len(teacher), 1), 9, device=device, dtype=torch.long)
                    logits = model(observations, torch.cat((bos, teacher[:, :-1]), 1))
                    loss = F.cross_entropy(logits.reshape(-1, 9), teacher.reshape(-1))
                    reward_value = None
                else:
                    ids, log_prob, entropy = model.generate(observations, stochastic=True)
                    with torch.no_grad():
                        reward = objective(ids, observations)
                        greedy = model.generate(observations)[0]
                        advantage = reward - objective(greedy, observations)
                    loss = -(advantage * log_prob).mean() - 0.005 * entropy.mean()
                    reward_value = reward.mean().item()
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite training loss")
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                norm = nn.utils.clip_grad_norm_(model.parameters(), 1)
                if not torch.isfinite(norm):
                    raise RuntimeError("nonfinite gradient")
                optimizer.step()
                row = {"stage": stage, "step": step + 1, "loss": loss.item(),
                       "reward": reward_value}
                history.append(row)
                if step == 0 or (step + 1) % 25 == 0:
                    print(json.dumps(row), flush=True)
            if steps:
                assert digest(model.state_dict()) != stage_initial
                save_checkpoint(args.out / f"{stage}.pt", model, optimizer, steps, stage)
        save_checkpoint(args.out / "final.pt", model, optimizer, len(history), "final")
    model.eval()
    # Test worlds are instantiated only after all optimization has finished.
    if args.evaluation_worlds:
        episodes = torch.load(args.evaluation_worlds, map_location="cpu", weights_only=True)
        if set(episodes) != {"id", "heldout", "ood"}:
            raise ValueError("evaluation file must contain id/heldout/ood")
        if any(len(batch["observed"]) != args.eval_worlds for batch in episodes.values()):
            raise ValueError("--eval-worlds must match the saved evaluation tensor count")
    else:
        episodes = {split: worlds(args.eval_worlds, 900000 + i, split)
                    for i, split in enumerate(["id", "heldout", "ood"])}
    torch.save(episodes, args.out / "evaluation_worlds.pt")
    before_eval = digest(model.state_dict())
    final_scores, examples = evaluate(model, episodes, device)
    assert digest(model.state_dict()) == before_eval
    baselines = {}
    for name in ["random", "enumeration"]:
        baselines[name] = {}
        g = torch.Generator().manual_seed(773)
        for split, batch in episodes.items():
            ids = (torch.randint(9, (args.eval_worlds, 3), generator=g) if name == "random"
                   else enumerate_best(batch["observed"]))
            nmse = ((predict(ids, batch["test_x"]) - batch["test_y"]).square().mean(1)
                    / (batch["test_y"].square().mean(1) + 1))
            baselines[name][split] = {"extrapolation_nmse": nmse.mean().item()}
    ablations = {}
    # Compare SFT-only with final RL using the identical materialized evaluation tensors.
    if (args.out / "sft.pt").exists():
        control = TheoryTransformer().to(device)
        control.load_state_dict(torch.load(args.out / "sft.pt", map_location="cpu",
                                          weights_only=True)["model"])
        control.eval()
        ablations["sft_only"] = evaluate(control, episodes, device)[0]
    if not args.checkpoint:
        torch.manual_seed(args.seed)
        control = TheoryTransformer().to(device).eval()
        ablations["untrained"] = evaluate(control, episodes, device)[0]
    reload_equal = None
    if (args.out / "final.pt").exists():
        loaded = TheoryTransformer().to(device).eval()
        loaded.load_state_dict(torch.load(args.out / "final.pt", map_location="cpu",
                                         weights_only=True)["model"])
        obs = episodes["heldout"]["observed"][:8].to(device)
        with torch.no_grad():
            reload_equal = torch.equal(model.generate(obs)[0], loaded.generate(obs)[0])
        assert reload_equal
    pareto = archive(model, episodes["heldout"]["observed"], device)
    report = {"environment": environment, "elapsed_seconds": time.time() - started,
              "config": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
              "checks": {"accelerator_backward": True, "finite_training": True,
                         "weights_changed": before_eval != initial_hash,
                         "checkpoint_reload_equal": reload_equal, "frozen_evaluation": True},
              "model": final_scores, "baselines": baselines, "ablations": ablations,
              "history": history, "examples": examples, "pareto_archive": pareto,
              "weights_sha256": before_eval,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "evaluation_sha256": digest({f"{s}/{k}": v for s, b in episodes.items()
                                           for k, v in b.items()}),
              "claim": "Engineering demo only; finite quadratic grammar; no historical or frontier discovery claim."}
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Discovery demo result", "", report["claim"], "",
             f"Device: {device}; parameters: {environment['parameters']:,}; elapsed: {report['elapsed_seconds']:.1f}s.",
             "", "| Evaluation | Model extrapolation NMSE | Random | Enumeration |",
             "|---|---:|---:|---:|"]
    for split, values in final_scores.items():
        lines.append(f"| {split} | {values['extrapolation_nmse']:.5f} | "
                     f"{baselines['random'][split]['extrapolation_nmse']:.5f} | "
                     f"{baselines['enumeration'][split]['extrapolation_nmse']:.5f} |")
    lines += ["", "Lower NMSE is better. OOD sine worlds are outside the generator grammar.",
              "RL improvement is an experimental outcome, not a smoke-test pass condition.",
              "", "Checks: `" + json.dumps(report["checks"]) + "`"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"report": str(args.out / "report.md"), "checks": report["checks"],
                      "scores": final_scores}), flush=True)


if __name__ == "__main__":
    main()
