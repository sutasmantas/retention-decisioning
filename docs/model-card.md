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

## Promotion gates for real use

1. Refit on consented, versioned business data.
2. Backtest on a future time window.
3. Validate probability calibration and segment performance.
4. Run a randomized intervention experiment.
5. Confirm intervention costs and capacity with operations.
6. Add outcome logging and retraining/rollback controls.

