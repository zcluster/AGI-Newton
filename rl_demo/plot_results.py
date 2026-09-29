"""Render actual report data; plotting is optional and never part of GPU training."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

p = argparse.ArgumentParser()
p.add_argument("report", type=Path)
args = p.parse_args()
data = json.loads(args.report.read_text())
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), layout="constrained")
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.18)
sft = [r for r in data["history"] if r["stage"] == "sft"]
rl = [r for r in data["history"] if r["stage"] == "rl"]
axes[0].plot([r["step"] for r in sft], [r["loss"] for r in sft], color="#126e82")
axes[0].set(title="Supervised warm-start", xlabel="SFT updates", ylabel="Token cross-entropy")
axes[1].plot([r["step"] for r in rl], [r["reward"] for r in rl], color="#ce741c")
axes[1].set(title="Actual RL training rewards", xlabel="RL updates", ylabel="Mean observation reward")
methods = {"Random": data["baselines"]["random"]}
if "sft_only" in data["ablations"]:
    methods["SFT only"] = data["ablations"]["sft_only"]
methods["SFT + RL"] = data["model"]
methods["Enumeration"] = data["baselines"]["enumeration"]
x = np.arange(3)
width = 0.19
colors = ["#aab4bf", "#68a6b3", "#126e82", "#ce741c"]
for i, (name, results) in enumerate(methods.items()):
    y = [max(results[s]["extrapolation_nmse"], 1e-6) for s in ["id", "heldout", "ood"]]
    axes[2].bar(x + (i - (len(methods) - 1) / 2) * width, y, width,
                label=name, color=colors[i])
axes[2].set(xticks=x, xticklabels=["ID", "Held-out\ncoefficients", "OOD sine"],
            yscale="log", ylabel="Extrapolation NMSE (lower is better)",
            title="Identical test worlds; log scale")
axes[2].legend(fontsize=8, frameon=True, facecolor="white", framealpha=0.95,
               edgecolor="#dddddd", loc="lower left")
fig.suptitle(f"DiscoverAI engineering demo | {data['environment']['device']} | "
             f"{data['environment']['parameters']:,} parameters", fontsize=14)
fig.text(0.5, -0.055, "Single seed, small evaluation set. Enumeration floor = 1e-6. "
         "This is not evidence of open-ended scientific discovery.", ha="center", fontsize=9)
for suffix in ("png", "pdf"):
    fig.savefig(args.report.with_name(f"results.{suffix}"), dpi=180, bbox_inches="tight")
print(args.report.with_name("results.png"))
