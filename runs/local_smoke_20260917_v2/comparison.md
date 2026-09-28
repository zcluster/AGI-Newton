# Pre-Newton random-init quick stab

This is an engineering and signal-detection run, not a claim that Newton's law was rediscovered.
Both arms start from the same seed and architecture. The only treatment is adding the isolated
Boulliau/Hooke precursor corpus to the second arm.

| Arm | Parameters | Training bytes | Tokens seen | Final validation loss | Training time |
|---|---:|---:|---:|---:|---:|
| Strict | 124,736 | 100,000 | 768 | 40.5047 | 0.0 min |
| + precursors | 124,736 | 100,000 | 768 | 40.5047 | 0.0 min |

Lower mean NLL is preferred. The key diagnostic is whether precursor exposure selectively lowers
the inverse-square completion relative to the other laws.

| Probe | Strict winner | +precursor winner | Strict inverse-square NLL | +precursor inverse-square NLL | Change |
|---|---|---|---:|---:|---:|
| modern_direct | inverse_cube | inverse_cube | 41.6072 | 41.6072 | +0.0000 |
| period_style | inverse_cube | inverse_cube | 41.9029 | 41.9029 | +0.0000 |
| law_notation | constant | constant | 51.1551 | 51.1551 | +0.0000 |

Mean inverse-square NLL change after precursor exposure: **+0.0000**.
A negative value is the expected direction, but replication across seeds and a larger corpus are required.

## Free generations

### Strict

```text
Question: How does the attractive power between the Earth and Moon vary with their distance? Answer: It varies as      
```

### With precursors

```text
Question: How does the attractive power between the Earth and Moon vary with their distance? Answer: It varies as      
```

## Interpretation rule

- If neither arm prefers inverse-square, record a clean negative result: the present corpus/model is insufficient.
- If only the precursor arm prefers it, the harness detects historical leakage but not rediscovery.
- If the strict arm prefers it reproducibly across seeds and adversarial paraphrases, scale before making a stronger claim.
