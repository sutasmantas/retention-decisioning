# Model card

## Intended use

Prioritize SaaS customer-success outreach by combining churn risk, estimated
intervention benefit, account value and team capacity.

## Models

- Churn: logistic regression after numeric standardization and segment
  one-hot encoding.
- Treatment effect: a T-learner consisting of separate treated and control
  logistic outcome models.

## Default evaluation

Deterministic seed `42`, 2,400 generated accounts, stratified 75/25 split.

| Metric | Result |
|---|---:|
| Holdout accounts | 600 |
| Churn prevalence | 0.272 |
| ROC-AUC | 0.763 |
| PR-AUC | 0.573 |
| Brier score | 0.162 |
| Synthetic uplift RMSE | 0.084 |

The holdout is also reported by segment and five probability bands through
`GET /api/monitoring`.

## Real randomized-data feasibility result

The separate, non-UI Hillstrom benchmark evaluates Mens-email versus no-email
on the two-week website-visit outcome. It does not relabel the retail dataset
as SaaS churn data or replace the product model.

The frozen 80/20 joint-stratified run produced an average visit lift of
`0.0767` with a bootstrap 95% interval of `[0.0634, 0.0920]`. The learned
20%-capacity policy's estimated gain over random allocation was `0.0060`, but
its interval `[-0.0019, 0.0128]` crossed zero; normalized Qini also crossed
zero. The pre-registered decision is therefore `PROMOTE_AVERAGE_EFFECT_ONLY`:
the real experiment supports the intervention on average, but these features
do not support a claim that learned targeting improves allocation.

See the [admission and reuse record](REAL_DATA_ADMISSION.md) and the committed
[benchmark report](../artifacts/real_data/benchmark.md).

## Decision-policy comparator

The product reports a risk-only baseline alongside the value-aware policy. The
baseline uses the same risk threshold and capacity, but ranks by churn
probability and does not remove negative-uplift or negative-value accounts.
This comparison quantifies the modeled economic difference between the two
queue-construction rules on the same scored population.

It does not prove realized business lift. That requires prospective outcome
measurement under a randomized intervention.

## Inputs

Segment, MRR, seat change, weekly active ratio, priority-ticket count, days to
renewal, feature adoption, tenure, NPS and support-resolution time.

## Limitations

- Synthetic data does not reproduce an actual customer population.
- Random holdout performance is not a substitute for temporal validation.
- T-learner uplift is only causally interpretable because treatment is
  randomized by the synthetic generator.
- Input-based reason codes summarize risky values; they are not exact model
  contribution or causal explanations.
- Expected protected MRR is a model estimate, not realized revenue.
- The historical Hillstrom visit result does not establish long-term
  retention, revenue, temporal generalization, or production targeting lift.

## Promotion gates for real use

1. Refit on consented, versioned business data.
2. Backtest on a future time window.
3. Validate probability calibration and segment performance.
4. Run a randomized intervention experiment.
5. Confirm intervention costs and capacity with operations.
6. Add outcome logging and retraining/rollback controls.
