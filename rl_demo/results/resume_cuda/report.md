# Discovery demo result

Engineering demo only; finite quadratic grammar; no historical or frontier discovery claim.

Device: cuda; parameters: 69,065; elapsed: 0.7s.

| Evaluation | Model extrapolation NMSE | Random | Enumeration |
|---|---:|---:|---:|
| id | 1.37036 | 3.77150 | 0.00000 |
| heldout | 1.74031 | 5.41007 | 0.00000 |
| ood | 17.74082 | 6.50811 | 5.13706 |

Lower NMSE is better. OOD sine worlds are outside the generator grammar.
RL improvement is an experimental outcome, not a smoke-test pass condition.

Checks: `{"accelerator_backward": true, "finite_training": true, "weights_changed": true, "checkpoint_reload_equal": true, "frozen_evaluation": true}`
