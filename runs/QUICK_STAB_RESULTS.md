# Pre-Newton random-init quick stab

This is an engineering and signal-detection run, not a claim that Newton's law was rediscovered.
Both arms start from the same seed and architecture. The only treatment is adding the isolated
Boulliau/Hooke precursor corpus to the second arm.

| Arm | Parameters | Training bytes | Tokens seen | Final validation loss | Training time |
|---|---:|---:|---:|---:|---:|
| Strict | 10,844,544 | 13,619,596 | 12,288,000 | 2.5105 | 0.8 min |
| + precursors | 10,844,544 | 14,928,535 | 12,288,000 | 2.9974 | 0.9 min |

Lower mean NLL is preferred. The key diagnostic is whether precursor exposure selectively lowers
the inverse-square completion relative to the other laws.

| Probe | Strict winner | +precursor winner | Strict target margin | +precursor target margin | Treatment effect |
|---|---|---|---:|---:|---:|
| modern_direct | inverse | inverse_square | +0.0578 | -0.0381 | -0.0959 |
| period_style | inverse_square | inverse_cube | -0.0423 | +0.0045 | +0.0467 |
| law_notation | constant | constant | +1.4336 | +1.6888 | +0.2552 |

Target margin is inverse-square mean NLL minus the best non-target NLL; negative means inverse-square wins.
Mean treatment effect on that margin: **+0.0687**.
A negative treatment effect is the expected direction. Mixed signs across probes are a failed sensitivity check,
not evidence for or against physical rediscovery.

## Free generations

### Strict

```text
Question: How does the attractive power between the Earth and Moon vary with their distance? Answer: It varies as th 
re H the
lle e E the the Eall ine e the _ fofo B ththe the C por le the tiy towhis pofo tham twe wo l
be sthe bene the the to of cath bomof ole whe co e a t
```

### With precursors

```text
Question: How does the attractive power between the Earth and Moon vary with their distance? Answer: It varies as pald Aistoure sedesesthem bereallayesee te Anthicove apthithafqueatuale whe 
iy, oufiser, oue, m twestome
be stiatinge, osothe hator, atick, te ollinat co elath
```

## Interpretation rule

- If neither arm prefers inverse-square, record a clean negative result: the present corpus/model is insufficient.
- If only the precursor arm prefers it, the harness detects historical leakage but not rediscovery.
- If the strict arm prefers it reproducibly across seeds and adversarial paraphrases, scale before making a stronger claim.
