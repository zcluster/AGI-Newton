#!/usr/bin/env python3
"""CPU RNG replay of mathematical sampling, not a recorded gradient audit."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from train_bpe_gpt import GPT, TokenStream


def batch_shares(weights, arithmetic):
    denominator = weights.sum()
    if denominator <= 0:
        raise ValueError('No supervised targets')
    plain = weights[arithmetic].sum() / denominator
    scaled = weights.clone()
    scaled[arithmetic] *= 128
    return float(plain), float(scaled[arithmetic].sum() / scaled.sum())


def audit(report_path):
    report = json.loads(report_path.read_text())
    args = report['args']
    torch.set_num_threads(2)
    torch.manual_seed(args['seed'])
    # Reproduce CPU initialization RNG consumption, including overwritten weights.
    model = GPT(report['vocab_size'], args['context'], args['width'], args['heads'], args['layers'])
    del model
    train = TokenStream(Path(args['train']), Path(args['loss_weights']))
    validation = TokenStream(Path(args['validation']))
    for _ in range(16):
        validation.batch(args['batch_size'], args['context'], torch.device('cpu'))
    weighted = np.asarray(train.weights)
    assert set(np.unique(weighted)) == {0, 1, 128}
    arithmetic = torch.from_numpy(weighted == 128)
    plain_weights = train.weights.clone()
    plain_weights[arithmetic] = 1
    assert int(arithmetic.sum()) == 1394
    exposures = np.zeros(len(weighted), dtype=np.int64)
    plain_shares, scaled_shares, batches_with_arithmetic = [], [], 0
    starts_hash = hashlib.sha256()
    offsets = torch.arange(1, args['context'] + 1)
    for _ in range(args['steps']):
        starts = torch.randint(0, len(train.tokens) - args['context'] - 1, (args['batch_size'],))
        starts_hash.update(starts.numpy().astype('<i8').tobytes())
        indices = starts[:, None] + offsets
        mask = arithmetic[indices]
        batches_with_arithmetic += int(mask.any())
        plain, scaled = batch_shares(plain_weights[indices], mask)
        plain_shares.append(plain)
        scaled_shares.append(scaled)
        hit_indices = indices[mask].numpy()
        np.add.at(exposures, hit_indices, 1)
    counts = exposures[arithmetic.numpy()]
    assert len(counts) == 1394
    return {
        'scope': 'CPU RNG reconstruction on the training host/runtime; no original sampled-index log exists',
        'limitation': 'Loss-coefficient mass is not gradient contribution; no forward or optimizer steps replayed',
        'torch_version': torch.__version__, 'seed': args['seed'],
        'steps': args['steps'], 'batch_size': args['batch_size'], 'context': args['context'],
        'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
        'weights_sha256': hashlib.sha256(Path(args['loss_weights']).read_bytes()).hexdigest(),
        'sampled_starts_sha256': starts_hash.hexdigest(),
        'arithmetic_target_positions': len(counts),
        'arithmetic_target_exposures': int(counts.sum()),
        'positions_never_sampled': int((counts == 0).sum()),
        'exposure_min_median_max': [int(counts.min()), float(np.median(counts)), int(counts.max())],
        'batches_with_arithmetic': batches_with_arithmetic,
        'batches_without_arithmetic': args['steps'] - batches_with_arithmetic,
        'mean_batch_arithmetic_loss_mass_plain': float(np.mean(plain_shares)),
        'mean_batch_arithmetic_loss_mass_weight128': float(np.mean(scaled_shares)),
        'global_static_arithmetic_mass_plain': float(plain_weights[arithmetic].sum() / plain_weights.sum()),
        'global_static_arithmetic_mass_weight128': float(train.weights[arithmetic].sum() / train.weights.sum()),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path('runs/hpc_math_subtraction128_seed1686/report.json'))
    parser.add_argument('--output', type=Path, default=Path('audit/arithmetic_exposure.json'))
    args = parser.parse_args()
    result = audit(args.report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
