# SignalRoom real-data feasibility result

Decision: **PROMOTE_AVERAGE_EFFECT_ONLY**

This is a capacity-constrained re-engagement benchmark on a real randomized
retail email experiment. It is not evidence of SaaS churn reduction or client
revenue.

## Frozen contract

- Data: Hillstrom GitHub mirror at `c44ae9aea5923533ffdaf34522e4937afd813c9e` (`0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`)
- Contrast: Mens E-Mail versus No E-Mail
- Outcome: two-week `visit`
- Rows: 42,613 total; 34,090 train; 8,523 holdout
- Policy: positive predicted uplift, up to 20% capacity
- Split: joint treatment/outcome 80/20 holdout, seed 42

## Experiment health

- Arm counts: {'control': 21306, 'mens_email': 21307}
- Sample-ratio check: p=0.9961 (PASS)
- Maximum absolute covariate SMD: 0.0164
  (PASS at 0.10)

## Held-out result

All brackets are percentile-bootstrap 95% intervals.

| Metric | Result |
| --- | ---: |
| Average treatment effect | 0.0767 [0.0634, 0.0920] |
| Normalized Qini | 0.0144 [-0.0166, 0.0457] |
| Top-capacity realized uplift | 0.1167 [0.0733, 0.1512] |
| IPW policy gain vs random at equal capacity | 0.0060 [-0.0019, 0.0128] |
| Learned policy value | 0.1274 |
| Random capacity policy value | 0.1214 |

Underlying outcome-model diagnostics:

| Arm | ROC AUC | Brier score | Outcome rate |
| --- | ---: | ---: | ---: |
| Control | 0.6394 | 0.0931 | 0.1061 |
| Mens email | 0.6314 | 0.1444 | 0.1828 |

## Pre-registered gate

- Qini lower bound > 0: **False**
- Top-capacity uplift > overall ATE: **True**
- Policy-gain lower bound > 0: **False**

Targeting supported: **False**. Average effect
supported: **True**.

If targeting is rejected, the correct operational result is to retain the
experiment-level effect and not claim that the available features improve who
should receive the intervention.

## Limitations

- Public historical benchmark; the holdout is a reproducibility check, not an
  untouched scientific discovery.
- No timestamps, so temporal generalization and drift are untested.
- Visit is a short-horizon re-engagement outcome, not retention or revenue.
- Unsubscribe, complaint, long-term churn, and other harm outcomes are absent.
- The benchmark uses one email creative and a fixed 20% maximum capacity.

Reproduce with:

```bash
pip install -c requirements-benchmark.txt -e ".[dev]"
python -m signalroom.real_benchmark --bootstrap 500
```
