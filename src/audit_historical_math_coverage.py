#!/usr/bin/env python3
"""Count V11 source-role coverage; bibliographic roles are not passage labels."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import sentencepiece as spm

from tokenize_corpus import encode_record


def audit(data, tokenizer_path, token_audit, token_stream):
    tokenizer = spm.SentencePieceProcessor(model_file=str(tokenizer_path))
    sources = {}
    stream_hash = hashlib.sha256()
    for line in data.read_text().splitlines():
        row = json.loads(line)
        source = sources.setdefault(row['source_id'], {
            key: row[key] for key in ('title', 'language', 'role')
        } | {'chunks': 0, 'tokens': 0, 'characters': 0})
        assert all(source[key] == row[key] for key in ('title', 'language', 'role'))
        ids, _ = encode_record(row, tokenizer, False)
        # Match the existing uint16 little-endian historical stream on this host.
        for token in ids:
            stream_hash.update(token.to_bytes(2, 'little'))
        source['chunks'] += 1
        source['tokens'] += len(ids)
        source['characters'] += len(row['text'])
    total = sum(row['tokens'] for row in sources.values())
    expected = json.loads(token_audit.read_text())
    assert total == expected['tokens'], (total, expected['tokens'])
    assert sum(row['chunks'] for row in sources.values()) == expected['documents']
    actual_hash = hashlib.sha256(token_stream.read_bytes()).hexdigest()
    assert stream_hash.hexdigest() == actual_hash, 'Reconstructed tokens differ from the training stream'
    roles = defaultdict(int)
    languages = defaultdict(int)
    for row in sources.values():
        roles[row['role']] += row['tokens']
        languages[row['language']] += row['tokens']
    assert sum(roles.values()) == sum(languages.values()) == total
    return {
        'data_sha256': hashlib.sha256(data.read_bytes()).hexdigest(),
        'tokenizer_sha256': hashlib.sha256(tokenizer_path.read_bytes()).hexdigest(),
        'reconstructed_stream_sha256': stream_hash.hexdigest(),
        'tokens': total, 'role_tokens': dict(roles),
        'language_tokens': dict(languages), 'sources': sources,
        'scope': 'V11 scientific training stream only; EEBO bootstrap not subject-classified',
        'limitation': 'Whole-source metadata roles; not counts of usable mathematical passages or expert-approved content',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data/real_pilot_v11/train.jsonl'))
    parser.add_argument('--tokenizer', type=Path, default=Path('data/tokenizer_v11/pre1687_bpe.model'))
    parser.add_argument('--token-audit', type=Path, default=Path('data/real_pilot_v11/train.bin.json'))
    parser.add_argument('--token-stream', type=Path, default=Path('data/real_pilot_v11/train.bin'))
    parser.add_argument('--output', type=Path, default=Path('audit/historical_math_coverage.json'))
    args = parser.parse_args()
    result = audit(args.data, args.tokenizer, args.token_audit, args.token_stream)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'sources'}, indent=2))
