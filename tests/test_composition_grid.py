import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluate_composition_grid import cases, equation_and_answer_correct


class CompositionGridTests(unittest.TestCase):
    def test_balanced_grid_and_sealed_pair(self):
        rows = list(cases())
        self.assertEqual(len(rows), 204)
        self.assertEqual(len({row["prompt"] for row in rows}), 204)
        self.assertEqual(sum(row["sealed_pair"] for row in rows), 6)
        self.assertTrue(all(row["expected"] == row["numerator"] - row["known"] for row in rows))
        self.assertTrue(all(row["expected"] == -2 for row in rows if row["sealed_pair"]))

    def test_trace_check_rejects_wrong_arithmetic_answer_or_quotient(self):
        case = next(row for row in cases() if row["sealed_pair"])
        prompt = case["prompt"]
        self.assertTrue(equation_and_answer_correct(
            prompt + "1 - (3) = -2. Answer: N is proportional to z^-2.", case
        ))
        self.assertFalse(equation_and_answer_correct(
            prompt + "1 - (3) = -1. Answer: N is proportional to z^-2.", case
        ))
        self.assertFalse(equation_and_answer_correct(
            prompt + "1 - (3) = -2. Answer: N is proportional to z^-1.", case
        ))
        self.assertFalse(equation_and_answer_correct(
            prompt + "z^1/z^2; 1 - (3) = -2. Answer: N is proportional to z^-2.", case
        ))

    def test_prompts_do_not_occur_in_training_corpus(self):
        corpus = ROOT / "data" / "reasoning" / "admissible_reasoning_v6.jsonl"
        text = corpus.read_text(encoding="utf-8")
        self.assertNotIn("carries the same dependence", text)
        self.assertNotIn("Two measurements:", text)


if __name__ == "__main__":
    unittest.main()
