import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tokenize_corpus import encode_record
from train_bpe_gpt import TokenStream


class CharacterTokenizer:
    def bos_id(self):
        return 1

    def eos_id(self):
        return 2

    def encode(self, text, out_type=int, return_type=None):
        if return_type == "offset_mapping":
            return {"ids": [ord(char) for char in text],
                    "offsets": [(i, i+1) for i in range(len(text))]}
        return [ord(char) for char in text]


class WeightedTrainingTests(unittest.TestCase):
    def test_answer_only_preserves_input_and_masks_prompt(self):
        prompt = "A square is assigned to x.\nQuestion: Which power?\nAnswer: "
        row = {"source": "procedural", "prompt": prompt, "text": prompt + "square of x."}
        plain, _ = encode_record(row, CharacterTokenizer(), True)
        ids, weights = encode_record(row, CharacterTokenizer(), True, answer_only=True)
        self.assertEqual(ids, plain)
        self.assertEqual(weights[:1+len(prompt)], [0] * (1+len(prompt)))
        self.assertEqual(weights[1+len(prompt):], [1] * (len(row["text"])-len(prompt)+1))
        del row["prompt"]
        with self.assertRaises(ValueError):
            encode_record(row, CharacterTokenizer(), True, answer_only=True)
        copy_prompt = "Question: Copy x.\nAnswer: "
        copy_row = {"source": "procedural", "text": copy_prompt + "x."}
        self.assertEqual(
            encode_record(copy_row, CharacterTokenizer(), True, answer_only=True),
            encode_record({**copy_row, "prompt": copy_prompt}, CharacterTokenizer(), True, answer_only=True))
        with self.assertRaises(ValueError):
            encode_record({**row, "source": "historical"}, CharacterTokenizer(), True, answer_only=True)
        with self.assertRaises(ValueError):
            encode_record({**row, "prompt": "wrong"}, CharacterTokenizer(), True, answer_only=True)
        with self.assertRaises(ValueError):
            encode_record({"source": "procedural", "text": "Question: x?\nReasoning: x.\nAnswer: x."},
                          CharacterTokenizer(), True, answer_only=True)

    def test_identical_questions_cannot_cross_validation_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, train, validation = (root / name for name in ("all.jsonl", "train.jsonl", "validation.jsonl"))
            texts = [f"Question: {index}?\nAnswer: {index}." for index in range(200)]
            source.write_text("".join(json.dumps({"text": text}) + "\n" for text in texts * 2))
            subprocess.run([
                sys.executable, str(Path(__file__).resolve().parents[1] / "src" / "split_curriculum.py"),
                "--input", str(source), "--train", str(train), "--validation", str(validation)
            ], check=True, capture_output=True)
            with train.open() as train_file, validation.open() as validation_file:
                train_texts = {json.loads(line)["text"] for line in train_file}
                validation_texts = {json.loads(line)["text"] for line in validation_file}
            self.assertTrue(train_texts and validation_texts)
            self.assertFalse(train_texts & validation_texts)
            self.assertEqual(len(train_texts | validation_texts), 200)

    def test_only_procedural_continuation_is_upweighted(self):
        tokenizer = CharacterTokenizer()
        row = {"source": "procedural", "text": "Question: x?\nAnswer: y."}
        ids, weights = encode_record(row, tokenizer, weighted=True)
        boundary = 1 + len("Question: x?\n")
        self.assertEqual(len(ids), len(weights))
        self.assertEqual(weights[:boundary], [1] * boundary)
        self.assertEqual(weights[boundary:-1], [4] * len("Answer: y."))
        self.assertEqual(weights[-1], 1)
        _, historical_weights = encode_record(
            {"source": "historical", "text": row["text"]}, tokenizer, weighted=True
        )
        self.assertEqual(set(historical_weights), {1})

    def test_final_exponent_receives_distinct_weight(self):
        row = {"source": "procedural", "family": "diverse_elimination",
               "text": "Question: A^2 follows x^3. B follows x^1/A^2.\n"
                       "Reasoning: 1 - (3) = -2.\nAnswer: B is proportional to x^-2."}
        ids, weights = encode_record(row, CharacterTokenizer(), True, True)
        final = row["text"].rfind("-2")
        self.assertEqual(len(ids), len(weights))
        self.assertEqual(weights[1 + final:1 + final + 2], [16, 16])
        self.assertEqual(weights[1 + final - 1], 4)

    def test_sampled_weights_follow_next_token_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            tokens = Path(directory) / "tokens.bin"
            weights = Path(directory) / "weights.bin"
            np.arange(40, dtype=np.uint16).tofile(tokens)
            np.asarray([1] * 20 + [4] * 20, dtype=np.uint8).tofile(weights)
            x, y, sampled = TokenStream(tokens, weights).batch(8, 6, torch.device("cpu"))
            self.assertTrue(torch.equal(y, x + 1))
            self.assertTrue(torch.equal(sampled, torch.where(y < 20, 1.0, 4.0)))
            weights.write_bytes(b"\x01")
            with self.assertRaises(ValueError):
                TokenStream(tokens, weights)


if __name__ == "__main__":
    unittest.main()
