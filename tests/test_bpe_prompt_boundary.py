"""Run with project dependencies: python tests/test_bpe_prompt_boundary.py."""
import sys
from pathlib import Path
import sentencepiece as spm
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from train_bpe_gpt import generate, score
from tokenize_corpus import encode_record


class FixedModel:
    context = 512

    def __init__(self, tokenizer, next_id):
        self.vocab = tokenizer.vocab_size()
        self.next_id = next_id
        self.inputs = []

    def eval(self):
        return self

    def __call__(self, tokens):
        self.inputs.append(tokens.tolist()[0])
        logits = torch.zeros((*tokens.shape, self.vocab))
        logits[:, :, self.next_id] = 100
        return logits


def check():
    path = Path(__file__).resolve().parents[1] / "data/tokenizer_v11/pre1687_bpe.model"
    tokenizer = spm.SentencePieceProcessor(model_file=str(path))
    prompt = "Question: Which power?\nAnswer: "
    normalized = tokenizer.encode(prompt.rstrip(" \t"))
    assert tokenizer.encode(prompt) != normalized
    answer_ids = tokenizer.encode("square of the lengths.")
    assert tokenizer.encode(prompt + "square of the lengths.") == normalized + answer_ids
    model = FixedModel(tokenizer, answer_ids[0])
    result = generate(model, tokenizer, prompt, torch.device("cpu"), "fp32", length=1, temperature=0)
    assert model.inputs[0] == normalized
    assert result.startswith(prompt) and len(result) > len(prompt)
    score(model, tokenizer, prompt, "square of the lengths.", torch.device("cpu"), "fp32")
    assert model.inputs[-1] == (normalized + answer_ids)[:-1]
    model.next_id = tokenizer.eos_id()
    assert generate(model, tokenizer, prompt, torch.device("cpu"), "fp32", temperature=0) == prompt
    row = {"source": "procedural", "family": "symbolic",
           "text": "Question: A ∝ x^3; B ∝ x^1.\nAnswer: B/A ∝ x^-2."}
    plain, _ = encode_record(row, tokenizer, False)
    weighted, weights = encode_record(row, tokenizer, True, True)
    assert plain == weighted and len(plain) == len(weights)
    assert 16 in weights
    encoded = tokenizer.encode(row["text"], return_type="offset_mapping")
    final = row["text"].rfind("-2")
    assert all(weights[i+1] == 16 for i, (begin, end) in enumerate(encoded["offsets"])
               if begin < final+2 and end > final)
    print("Prompt boundary, scoring alignment, exact prefix and EOS checks passed")


if __name__ == "__main__":
    check()
