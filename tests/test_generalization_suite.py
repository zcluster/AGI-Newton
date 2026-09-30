import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluate_generalization_suite import PHYSICS_CASES, candidates, generation_is_correct


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
                    prompt + completion, prompt, base, known, numerator, -2
                ))


if __name__ == "__main__":
    unittest.main()
