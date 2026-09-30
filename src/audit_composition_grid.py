#!/usr/bin/env python3
"""Audit answer coverage and one-input counterfactuals in a saved grid report."""

import argparse
import itertools
import json
import random
import re
from collections import defaultdict
from pathlib import Path


def stated_power(row):
    if not row["generation"].startswith(row["prompt"]):
        return None
    continuation = row["generation"][len(row["prompt"]):]
    relation = re.compile(
        rf"\b{re.escape(row['target'])}\s*(?:is proportional to|∝)\s*"
        rf"{re.escape(row['base'])}\s*\^\s*(-?\d+)(?!\d|\.\d|/|\s+divided\s+by)", re.I
    )
    powers = {int(match.group(1)) for match in relation.finditer(continuation)}
    return next(iter(powers)) if len(powers) == 1 else None


def audit(rows, permutations=0):
    groups = defaultdict(list)
    strata = defaultdict(list)
    for row in rows:
        template, middle, known, numerator = row["id"].split("_")
        groups[(template, middle, "known", known)].append(row)
        groups[(template, middle, "numerator", numerator)].append(row)
        strata[(template, middle)].append(row)
    pairs = [pair for group in groups.values() for pair in itertools.combinations(group, 2)]
    powers = {row["id"]: stated_power(row) for row in rows}
    def pair_score(assigned):
        observed = [(a, b) for a, b in pairs
                    if assigned[a["id"]] is not None and assigned[b["id"]] is not None]
        correct = sum(assigned[b["id"]] - assigned[a["id"]] ==
                      b["expected"] - a["expected"] for a, b in observed)
        return len(observed), correct

    observed, correct = pair_score(powers)
    result = {
        "cases": len(rows),
        "answer_correct": sum(row["answer_correct"] for row in rows),
        "unique_relation_coverage": sum(power is not None for power in powers.values()),
        "eligible_one_input_pairs": len(pairs),
        "observed_one_input_pairs": observed,
        "counterfactual_consistent_pairs": correct,
    }
    if permutations:
        rng = random.Random(1686)
        rates = []
        for _ in range(permutations):
            shuffled = {}
            for group in strata.values():
                values = [powers[row["id"]] for row in group]
                rng.shuffle(values)
                shuffled.update((row["id"], value) for row, value in zip(group, values))
            count, hits = pair_score(shuffled)
            rates.append(hits / count if count else 0)
        rates.sort()
        actual = correct / observed if observed else 0
        result["permutation_null"] = {
            "draws": permutations,
            "mean_rate": sum(rates) / permutations,
            "interval_95": [rates[int(0.025 * permutations)], rates[int(0.975 * permutations)]],
            "upper_tail_p": (1 + sum(rate >= actual for rate in rates)) / (permutations + 1),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    rows = report["cases"]
    result = {"source": str(args.report), "all": audit(rows, permutations=1000)}
    result["by_template"] = {
        template: audit([row for row in rows if row["id"].startswith(template + "_")],
                        permutations=1000)
        for template in ("t0", "t1")
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
