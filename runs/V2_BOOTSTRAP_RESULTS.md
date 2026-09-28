# Pre-Newton random-init quick stab

This is an engineering and signal-detection run, not a claim that Newton's law was rediscovered.
Both arms start from the same seed and architecture. The only treatment is adding the isolated
Boulliau/Hooke precursor corpus to the second arm.

| Arm | Parameters | Training bytes | Tokens seen | Final validation loss | Training time |
|---|---:|---:|---:|---:|---:|
| Strict | 25,482,752 | 223,091,724 | 245,760,000 | 1.5473 | 10.7 min |
| + precursors | 25,482,752 | 233,563,236 | 245,760,000 | 2.2843 | 9.4 min |

Lower mean NLL is preferred. The key diagnostic is whether precursor exposure selectively lowers
the inverse-square completion relative to the other laws.

| Probe | Strict winner | +precursor winner | Strict target margin | +precursor target margin | Treatment effect |
|---|---|---|---:|---:|---:|
| kepler_huygens_derivation | inverse_square | inverse_square | -0.0119 | -0.0699 | -0.0580 |
| modern_direct | constant | inverse | +0.0288 | +0.2539 | +0.2251 |
| period_style | constant | inverse_square | +0.3476 | -0.0937 | -0.4413 |
| law_notation | constant | inverse | +1.4479 | +0.6758 | -0.7721 |

Target margin is inverse-square mean NLL minus the best non-target NLL; negative means inverse-square wins.
Mean treatment effect on that margin: **-0.2616**.
A negative treatment effect is the expected direction. Mixed signs across probes are a failed sensitivity check,
not evidence for or against physical rediscovery.

## Free generations

### Strict

```text
Kepler's observations give that the square of an orbital period is as the cube of its mean distance. For circular motion, the turning tendency is as the distance divided by the square of the period. Combining only these two relations, the turning tendency varies with distance as the ruine of
 sinne which being said before. Nam observis & seculatur ejusciri. Where the great diseases about is sene, the triannor of God, the lesser co equitie to the heart of the several benefit t
```

### With precursors

```text
Kepler's observations give that the square of an orbital period is as the cube of its mean distance. For circular motion, the turning tendency is as the distance divided by the square of the period. Combining only these two relations, the turning tendency varies with distance as the reciprocal cube of Bishops, which is the cube of Bishops; and the excubition of Aristotle, and the cubes of Bishops only on the cube of Bishops, and one of Bishops of Bishops, and the others of Bi
```

## Interpretation rule

- If neither arm prefers inverse-square, record a clean negative result: the present corpus/model is insufficient.
- If only the precursor arm prefers it, the harness detects historical leakage but not rediscovery.
- If the strict arm prefers it reproducibly across seeds and adversarial paraphrases, scale before making a stronger claim.
