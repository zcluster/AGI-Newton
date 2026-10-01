import json
import hashlib
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
from summarise_subtraction_weight import numeric_correct
from audit_arithmetic_exposure import batch_shares, audit
from unittest.mock import patch
from build_balanced_math import balanced
from summarise_balanced_math import validation_errors
from build_arithmetic_transfer import build as build_transfer
from build_math_calibration import build as build_math
from summarise_arithmetic_transfer import summarise as summarise_transfer


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
    def test_transfer_summary_scores_generations_and_checks_hashes(self):
        train, _ = build_math()
        probes = build_transfer(train)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = json.dumps(probes)
            digest = hashlib.sha256(content.encode()).hexdigest()
            (root / 'probes.json').write_text(content)
            (root / 'manifest.json').write_text(json.dumps({'probes_sha256': digest}))
            for arm, checkpoint in [('answer_only', '2565030214e3860c16b693523bed43ef4934eee7a5e28194a212dc5a016865ef'),
                                    ('balanced', 'a270638321e841743f5a1a089d52f3ba7ec0776106cd272f430942a196827faa')]:
                (root / f'{arm}.json').write_text(json.dumps({
                    'checkpoint_sha256': checkpoint, 'source_sha256': digest, 'prepend_bos': False,
                    'probes': [{**p, 'generation': p['prompt'] + f"{p['expected']}."} for p in probes]}))
            result = summarise_transfer(root)
            self.assertEqual(result['balanced']['seen_new_wording']['exact'], 48)
            self.assertEqual(result['balanced']['seen_new_wording']['by_wording']['new_verbal']['exact'], 24)
            self.assertEqual(result['balanced']['seen_new_wording']['by_wording']['new_symbolic']['cases'], 24)
            self.assertEqual(result['answer_only']['unseen_operands_new_answer']['both_wordings_correct'], 24)
            (root / 'manifest.json').write_text(json.dumps({'probes_sha256': 'wrong'}))
            with self.assertRaises(AssertionError):
                summarise_transfer(root)

    def test_transfer_probes_separate_wording_operands_and_answers(self):
        train, _ = build_math()
        probes = build_transfer(train)
        answers = {r['numerator'] - r['known'] for r in train if r['family'] == 'math_subtraction'}
        self.assertEqual(probes, build_transfer(train))
        for p in probes:
            self.assertEqual(p['expected'], p['a'] - p['b'])
            if p['group'] != 'seen_operands':
                self.assertGreater(max(abs(p['a']), abs(p['b'])), 8)
                self.assertEqual(p['expected'] in answers, p['group'] == 'unseen_operands_known_answer')

    def test_validation_error_diagnostic_keeps_format_failures_visible(self):
        base = {'group': 'validation', 'prompt': 'A: ', 'a': 1, 'b': 3, 'expected': -2}
        rows = [{**base, 'generation': 'A: ' + answer} for answer in ('-2.', '-1.', '-3.', 'unknown')]
        result = validation_errors(rows)
        self.assertEqual(result['cases'], 4)
        self.assertEqual(result['parseable_integer_answers'], 3)
        self.assertEqual(result['exact'], 1)
        self.assertEqual(result['off_by_one'], 2)
        self.assertAlmostEqual(result['mean_absolute_error_on_parseable'], 2/3)

    def test_exposure_record_mask_matches_actual_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = {'source': 'procedural', 'family': 'math_subtraction', 'prompt': 'Q\nA: ', 'text': 'Q\nA: 1.'}
            ids, weights = encode_record(row, CharacterTokenizer(), True, answer_only=True)
            tokens, targets, records, report = [root / name for name in ('t.bin', 'w.bin', 'r.jsonl', 'report.json')]
            np.asarray(ids * 2, dtype=np.uint16).tofile(tokens)
            np.asarray(weights * 2, dtype=np.uint8).tofile(targets)
            records.write_text(json.dumps(row) + '\n' + json.dumps({**row, 'family': 'math_elimination'}) + '\n')
            report.write_text(json.dumps({'vocab_size': 256, 'args': {
                'seed': 1686, 'context': 6, 'width': 8, 'heads': 2, 'layers': 1,
                'train': str(tokens), 'validation': str(tokens), 'loss_weights': str(targets),
                'tokenizer': 'mock', 'batch_size': 2, 'steps': 2}}))
            with patch('audit_arithmetic_exposure.spm.SentencePieceProcessor', return_value=CharacterTokenizer()):
                result = audit(report, records)
                self.assertEqual(result['record_tokens_by_family']['math_subtraction'], len(ids))
                self.assertEqual(result['arithmetic_target_positions'], sum(weights))
                self.assertEqual(result['global_static_arithmetic_mass_plain'], .5)
                self.assertAlmostEqual(result['global_static_arithmetic_mass_weight128'], 128/129)
                np.asarray([0] * (2 * len(weights)), dtype=np.uint8).tofile(targets)
                with self.assertRaises(AssertionError):
                    audit(report, records)

    def test_balancing_only_duplicates_training_records(self):
        row = {'split': 'train', 'family': 'math_subtraction', 'prompt': 'Q', 'text': 'Q A',
               'numerator': 2, 'known': 1}
        validation = [{**row, 'split': 'validation', 'prompt': 'V', 'text': 'V A'}]
        self.assertEqual(balanced([row], validation), [row] * 128)
        self.assertEqual(balanced([{**row, 'family': 'math_elimination'}], validation),
                         [{**row, 'family': 'math_elimination'}])
        for invalid in ({**row, 'numerator': 1, 'known': 3}, {**row, 'numerator': 3, 'known': 1},
                        {**row, 'prompt': 'V'}):
            with self.assertRaises(AssertionError):
                balanced([invalid], validation)

    def test_weight_multiplier_cannot_create_missing_batch_exposure(self):
        weights = torch.tensor([0., 1., 1.])
        plain, scaled = batch_shares(weights, torch.tensor([False, True, False]))
        self.assertEqual(plain, 0.5)
        self.assertAlmostEqual(scaled, 128/129)
        self.assertEqual(batch_shares(weights, torch.zeros(3, dtype=torch.bool)), (0., 0.))
        with self.assertRaises(ValueError):
            batch_shares(torch.zeros(3), torch.zeros(3, dtype=torch.bool))

    def test_numeric_subtraction_grader_rejects_wrong_or_explanatory_suffix(self):
        fixture = {"prompt": "Answer: ", "expected": -2}
        for answer in ("-2.", "-2", " -2. "):
            self.assertTrue(numeric_correct({**fixture, "generation": "Answer: " + answer}))
        for answer in ("-1.", "-2.5", "x^-2.", "1 - 3 = -2.", "-2. Then 0."):
            self.assertFalse(numeric_correct({**fixture, "generation": "Answer: " + answer}))

    def test_subtraction_scaling_changes_only_its_answer_weights(self):
        row = {"source": "procedural", "family": "math_subtraction",
               "text": "Question: What is 2 minus 1?\nAnswer: 1."}
        ids, plain = encode_record(row, CharacterTokenizer(), True, answer_only=True)
        weighted_ids, scaled = encode_record(row, CharacterTokenizer(), True, answer_only=True, subtraction_weight=128)
        self.assertEqual(ids, weighted_ids)
        self.assertEqual(scaled, [w * 128 for w in plain])
        self.assertEqual(scaled[0], 0)
        self.assertEqual(scaled[-1], 128)
        self.assertEqual(encode_record({**row, "family": "math_elimination"}, CharacterTokenizer(), True,
                                     answer_only=True, subtraction_weight=128), (ids, plain))
        for bad in (0, 256):
            with self.assertRaises(ValueError):
                encode_record(row, CharacterTokenizer(), True, answer_only=True, subtraction_weight=bad)
        with self.assertRaises(ValueError):
            encode_record(row, CharacterTokenizer(), True, subtraction_weight=128)

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
