#!/usr/bin/env python3
"""Post-hoc reading diagnostic, not a historical discovery benchmark."""
import argparse
import hashlib
import json
from pathlib import Path


def cases(root):
    path = root / "raw/streete_astronomia_carolina_1661.txt"
    text = path.read_text()
    start = text.index("For Example, The Period of the Revolution of the Earth")
    end = text.index("Mars, or by artificiall numbers,", start)
    excerpt = text[start:end] + "Mars, or by artificiall numbers,"
    records = []
    for name, passage, target in [
        ("original_ocr", excerpt, "square"),
        ("modern_paraphrase", "The squares of the periods are as the cubes of the distances.", "square"),
        ("counterfactual_paraphrase", "The cubes of the periods are as the squares of the distances.", "cube"),
    ]:
        for form in ("question", "continuation"):
            suffix = ("\nQuestion: What power of the periods is compared?\nAnswer: "
                      if form == "question" else "\nThe passage compares the ")
            records.append({"id": name + "_" + form, "prompt": passage + suffix,
                            "target": target, "candidates": {
                                power: power + " of the periods." for power in ("square", "cube")}})
    for first, second, target in [(1, 3, "-2"), (3, 1, "2")]:
        records.append({"id": f"arithmetic_{first}_{second}",
                        "prompt": f"Question: What is {first} minus {second}?\nAnswer: ",
                        "target": target, "candidates": {n: n + "." for n in ("-2", "0", "2")}})
    assert len(records) == 8 and len({r["id"] for r in records}) == 8
    assert "ſquare" in excerpt and "Cube" in excerpt
    return records, hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--tokenizer", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    probes, source_hash = cases(Path(__file__).resolve().parents[1])
    if args.self_check:
        assert probes[2]["target"] != probes[4]["target"]
        print("8 diagnostic cases and source extraction checked")
        return
    if not all((args.checkpoint, args.tokenizer, args.output)):
        parser.error("checkpoint, tokenizer and output are required")
    import sentencepiece as spm
    import torch
    from train_bpe_gpt import GPT, generate, score
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved = checkpoint["args"]
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    device = torch.device("cuda")
    model = GPT(tokenizer.vocab_size(), int(saved["context"]), int(saved["width"]),
                int(saved["heads"]), int(saved["layers"])).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    for probe in probes:
        prompt = probe["prompt"]
        # Never silently crop the source or candidates in this diagnostic.
        assert max(len(tokenizer.encode(prompt + answer)) for answer in probe["candidates"].values()) < model.context
        probe["prompt_tokens"] = len(tokenizer.encode(prompt))
        probe["scores"] = {key: score(model, tokenizer, prompt, answer, device, "bf16")
                           for key, answer in probe["candidates"].items()}
        probe["winner"] = min(probe["scores"], key=lambda key: probe["scores"][key]["mean_nll"])
        probe["generation"] = generate(model, tokenizer, prompt, device, "bf16",
                                       length=60, temperature=0, minimum_length=0)
    report = {"checkpoint": str(args.checkpoint), "label": saved["label"],
              "source_sha256": source_hash, "probes": probes,
              "limitation": "Single-checkpoint post-hoc diagnostic; ranking is not free-generation success or discovery."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "rank_correct": sum(p["winner"] == p["target"] for p in probes)}))


if __name__ == "__main__":
    main()
