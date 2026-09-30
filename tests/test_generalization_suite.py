import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluate_generalization_suite import CASES, PHYSICS_CASES, candidates, generation_is_correct


class GeneralizationSuiteTests(unittest.TestCase):
    def test_physics_candidate_uses_each_prompts_own_names(self):
        for case_id, prompt, _middle, target, base, known, numerator in PHYSICS_CASES:
            with self.subTest(case_id=case_id):
                self.assertIn(target.casefold(), prompt.casefold())
                self.assertIn(base.casefold(), prompt.casefold())
                self.assertEqual(numerator - known, -2)
                completion = candidates(target, base, known, numerator)["-2"]
                self.assertIn(f"{target} is proportional to {base}^-2", completion)
                self.assertTrue(generation_is_correct(
                    prompt + completion, prompt, target, base, -2
                ))

    def test_open_generation_requires_uncontradicted_final_answer(self):
        prompt = "Find N as a power of z.\nReasoning: "
        self.assertTrue(generation_is_correct(
            prompt + "1 - (-1) = 2. Answer: N is proportional to z^2.",
            prompt, "N", "z", 2
        ))
        for continuation in (
            "N is proportional to z^2. Answer: N is proportional to z^3.",
            "N is proportional to z^1. Answer: N is proportional to z^2.",
            "Answer: Q is proportional to z^2.",
            "Answer: N is proportional to z^2.5.",
            "Answer: N is proportional to z^2. Also Q is proportional to z^4.",
        ):
            with self.subTest(continuation=continuation):
                self.assertFalse(generation_is_correct(
                    prompt + continuation, prompt, "N", "z", 2
                ))

    def test_archived_generations_match_corrected_report_counts(self):
        root = Path(__file__).resolve().parents[1]
        expected = {
            "v5_two_premise": (0, 0),
            "v6_diverse": (2, 0),
            "v7_reasoning_stage_500": (1, 0),
        }
        for run, counts in expected.items():
            with self.subTest(run=run):
                report = json.loads((root / "runs" / run / "generalization_suite.json").read_text())
                actual = []
                for key, cases in (("abstract_cases", CASES), ("physics_cases", PHYSICS_CASES)):
                    correct = 0
                    for row, case in zip(report[key], cases, strict=True):
                        case_id, prompt, _middle, target, base, known, numerator = case
                        self.assertEqual((row["id"], row["prompt"]), (case_id, prompt))
                        correct += generation_is_correct(
                            row["generation"], prompt, target, base, numerator - known
                        )
                    actual.append(correct)
                self.assertEqual(tuple(actual), counts)


if __name__ == "__main__":
    unittest.main()
