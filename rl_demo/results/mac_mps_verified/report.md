# Discovery demo result

Engineering demo only; finite quadratic grammar; no historical or frontier discovery claim.

Device: mps; parameters: 69,065; elapsed: 30.4s.

| Evaluation | Model extrapolation NMSE | Random | Enumeration |
|---|---:|---:|---:|
| id | 0.93544 | 3.77150 | 0.00000 |
| heldout | 0.69538 | 5.41007 | 0.00000 |
| ood | 7.61367 | 6.50811 | 5.13706 |

Lower NMSE is better. OOD sine worlds are outside the generator grammar.
RL improvement is an experimental outcome, not a smoke-test pass condition.

Checks: `{"accelerator_backward": true, "finite_training": true, "weights_changed": true, "checkpoint_reload_equal": true, "frozen_evaluation": true}`
