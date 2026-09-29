"""Checks for scientific data boundaries and the autoregressive implementation."""
import unittest
import torch
from run_demo import (GRID, TRAIN_IDS, TEST_IDS, TheoryTransformer, enumerate_best,
                      error, worlds)


class DemoTests(unittest.TestCase):
    def test_equation_split_disjoint(self):
        train = set(map(tuple, TRAIN_IDS.tolist()))
        test = set(map(tuple, TEST_IDS.tolist()))
        self.assertFalse(train & test)
        self.assertEqual(len(train | test), 729)

    def test_enumeration_uses_observations_and_recovers(self):
        for split in ("train", "heldout"):
            batch = worlds(12, 42, split)
            ids = enumerate_best(batch["observed"])
            self.assertLess(error(ids, batch["observed"]).max().item(), 1e-7)

    def test_test_worlds_repeat_exactly(self):
        a, b = worlds(10, 900000, "heldout"), worlds(10, 900000, "heldout")
        for key in a:
            self.assertTrue(torch.equal(a[key], b[key]))
        self.assertTrue((a["test_x"] > a["observed"][:, :, 0].max()).all())

    def test_causal_mask(self):
        torch.manual_seed(0)
        model = TheoryTransformer().eval()
        obs = worlds(2, 9, "train")["observed"]
        # Changing last prefix token must not affect preceding logits.
        a = torch.tensor([[9, 0, 1], [9, 2, 3]])
        b = a.clone()
        b[:, -1] = 8
        with torch.no_grad():
            self.assertTrue(torch.allclose(model(obs, a)[:, :2], model(obs, b)[:, :2]))

    def test_ood_cannot_be_exactly_represented(self):
        batch = worlds(12, 900002, "ood")
        ids = enumerate_best(batch["observed"])
        self.assertGreater(error(ids, batch["observed"]).min().item(), 1e-6)


if __name__ == "__main__":
    torch.set_num_threads(2)
    unittest.main()
