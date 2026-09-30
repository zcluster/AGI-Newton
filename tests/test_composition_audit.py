import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_composition_grid import audit, stated_power


class CompositionAuditTests(unittest.TestCase):
    def test_one_input_change_requires_matching_answer_change(self):
        rows = []
        for numerator, answer in ((0, -3), (1, -2), (2, -2)):
            prompt = "Find N.\nAnswer: "
            rows.append({"id": f"t0_M_3_{numerator}", "prompt": prompt,
                         "generation": prompt + f"N is proportional to z^{answer}.",
                         "target": "N", "base": "z", "expected": numerator - 3,
                         "answer_correct": answer == numerator - 3})
        result = audit(rows, permutations=20)
        self.assertEqual(result["eligible_one_input_pairs"], 3)
        self.assertEqual(result["observed_one_input_pairs"], 3)
        self.assertEqual(result["counterfactual_consistent_pairs"], 1)
        self.assertEqual(result["answer_correct"], 2)
        self.assertEqual(result["permutation_null"]["draws"], 20)
        self.assertIsNone(stated_power({**rows[0], "generation": rows[0]["generation"]
                                       + " N is proportional to z^0."}))
        self.assertIsNone(stated_power({**rows[0], "generation": "N is proportional to z^-3."}))


if __name__ == "__main__":
    unittest.main()
