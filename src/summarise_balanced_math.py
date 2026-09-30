#!/usr/bin/env python3
"""Matched-budget resampling comparison; arithmetic is not discovery."""
import json
from pathlib import Path

from summarise_subtraction_weight import numeric_correct


def main():
    root = Path(__file__).resolve().parents[1] / 'audit'
    baseline = json.loads((root / 'subtraction_weight128/baseline/subtraction_grid.json').read_text())
    new = json.loads((root / 'balanced_math/subtraction_grid.json').read_text())
    old_report = json.loads((root / 'math_calibration/answer_only/report.json').read_text())
    report = json.loads((root / 'balanced_math/report.json').read_text())
    for key in ('parameters', 'vocab_size', 'steps', 'tokens_seen', 'resumed_from'):
        assert old_report[key] == report[key]
    for key in ('seed', 'context', 'width', 'heads', 'layers', 'learning_rate', 'warmup_steps', 'batch_size', 'precision'):
        assert old_report['args'][key] == report['args'][key]
    assert len(baseline['probes']) == len(new['probes']) == 578
    for old, new_row in zip(baseline['probes'], new['probes']):
        for key in ('id', 'prompt', 'group', 'expected', 'candidates'):
            assert old[key] == new_row[key]
    groups = {}
    for group in ('train', 'validation', 'sealed_newton', 'sealed_reverse'):
        groups[group] = {'cases': sum(p['group'] == group for p in new['probes'])}
        for label, data in [('baseline', baseline), ('balanced', new)]:
            groups[group][label] = sum(numeric_correct(p) for p in data['probes'] if p['group'] == group)
    assert [r['cases'] for r in groups.values()] == [544, 30, 2, 2]
    result = {'matched_settings_verified': True, 'groups': groups,
              'train_gate_passed': groups['train']['balanced'] / 544 >= .9,
              'validation_gate_passed': groups['validation']['balanced'] / 30 >= .8,
              'limitation': 'One seed, modern synthetic capability arm; not historical scientific discovery'}
    (root / 'balanced_math/summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
