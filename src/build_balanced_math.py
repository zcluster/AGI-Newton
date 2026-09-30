#!/usr/bin/env python3
"""Resample existing training records only; no new mathematical content."""
import hashlib
import json
import random
from collections import Counter
from pathlib import Path


def balanced(train, validation):
    assert train and validation
    assert all(r['split'] == 'train' for r in train)
    assert all(r['split'] == 'validation' for r in validation)
    assert not {r['prompt'] for r in train} & {r['prompt'] for r in validation}
    assert all((r['numerator'], r['known']) != (1, 3) for r in train)
    assert all((r['numerator'], r['known']) != (3, 1) for r in train if r['family'] == 'math_subtraction')
    rows = [r for r in train for _ in range(128 if r['family'] == 'math_subtraction' else 1)]
    random.Random(1686).shuffle(rows)
    expected = {r['text']: 128 if r['family'] == 'math_subtraction' else 1 for r in train}
    assert Counter(r['text'] for r in rows) == expected
    return rows


if __name__ == '__main__':
    root = Path('data/math_calibration')
    train, validation = [[json.loads(line) for line in (root / f'{split}.jsonl').read_text().splitlines()]
                         for split in ('train', 'validation')]
    rows = balanced(train, validation)
    content = ''.join(json.dumps(row) + '\n' for row in rows)
    (root / 'balanced_train.jsonl').write_text(content)
    result = {'provenance': 'Modern synthetic capability control, not historical-only discovery',
              'shuffle_seed': 1686, 'arithmetic_record_multiplicity': 128,
              'records': len(rows), 'family_counts': dict(Counter(r['family'] for r in rows)),
              'original_train_sha256': hashlib.sha256((root / 'train.jsonl').read_bytes()).hexdigest(),
              'unchanged_validation_sha256': hashlib.sha256((root / 'validation.jsonl').read_bytes()).hexdigest(),
              'balanced_train_sha256': hashlib.sha256(content.encode()).hexdigest()}
    (root / 'balanced_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
