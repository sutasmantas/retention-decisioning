# SignalRoom controlled benchmark design

Date: 2026-08-05

## Evidence-reuse result

External evidence closes that risk, average response, heterogeneous effect
ranking, calibrated effect and realized policy value are different targets. It
also closes that S/T/X/R/DR, causal forests and direct uplift methods are real
families; no family is a universal winner; Qini alone is not a sufficient
deployment gate; overlap, cross-fitting, calibration and outer-held-out policy
evaluation matter; and a safety claim requires a measured harm outcome.

External evidence does **not** close which estimator or metric panel is stable
on SignalRoom's exact data, utility, capacity and environment. Those unknowns
justify the later queue below. This dossier runs none of it.

## Shared protocol

Every later run must freeze a machine-readable manifest before execution.

| Field | Frozen requirement |
| --- | --- |
| Question | one estimand, failure mode or policy choice; never “best uplift model” |
| Baselines | difference in means, current T-learner, treat-none, treat-all, random and equal-capacity rules where feasible |
| Candidate | package/repository/release/commit, estimator, base learners, hyperparameters, propensity handling, folds and seed |
| Data | owner/version/content digest, unit, treatment/control, outcome horizon, feature allowlist, missingness, treatment ratio and leakage audit |
| Split | outer test isolated before tuning; development folds for nuisance/estimator/calibration/policy selection; group/time split where applicable |
| Estimand | ATE/CATE/prioritization/policy value, target population and assumptions |
| Utility | outcome value, action cost, variable cost if present, capacity, harm and fallback rule |
| Metrics | exact implementation/version, orientation, normalization, ties, uncertainty method and undefined-case behavior |
| Repetition | at least five outer seeds/splits for screening; ten where candidate intervals or rankings overlap; raw per-run results retained |
| Resources | install and download time, median/p95 runtime, peak RSS, artifact/data bytes, failures and named hardware |
| Result | aggregate and per-regime values with intervals, metric disagreements, failed runs and artifact hashes |
| Decision | control, core, specialised, dominated, unsupported or inconclusive; include routing and claim boundary |

No candidate may use the outer test to choose base learners, hyperparameters,
trimming, calibration, score orientation, threshold, capacity, or policy. A
published package default is still a frozen modelling decision and must be
recorded.

### Default screen budget

- use the repository's constrained numerical stack for S0; use an isolated
  Python 3.12 lock/container for the pinned UpliftBench seam;
- maximum 25 GB combined downloaded data/cache and 20 GB artifacts for the
  first screen; corrected Criteo runs are staged at named row counts before any
  full-scale authorization;
- maximum 8 CPU-hours per non-neural candidate/regime and 16 CPU-hours for a
  first forest screen; neural/GPU candidates require a separate checkpoint;
- stop an estimator after two reproducible correctness or resource failures,
  retaining the failure evidence;
- no client data, remote service, deployment or application runtime change is
  implied by a benchmark pass.

## Frozen workload plan

1. **Current SignalRoom software control:** preserve commit, source and artifact
   hashes; synthetic seed-42 outputs; API/test behavior; and the frozen
   Hillstrom JSON/Markdown evidence.
2. **Hillstrom randomized email contrast:** checksum-pinned Mens email versus
   control, two-week visit, the existing joint treatment/outcome split and a
   newly frozen nested-CV comparison on training data. It tests randomized
   targeting and policy evaluation, not churn or transport.
3. **Corrected Criteo uplift:** owner-corrected 13,979,592-row version only,
   exact hash, visit and conversion outcomes reported separately. Screen a
   deterministic capped sample before a full-scale run; never describe the
   sample leaderboard as the 14M-row result.
4. **Oracle/semi-synthetic:** IHDP, ACIC and controlled DGPs with known CATE or
   policy risk. Vary prognostic complexity, treatment-effect complexity,
   assignment ratio, overlap, outcome sparsity, imbalance, heterogeneity and
   misspecification.
5. **Policy-risk workload:** a Jobs/policy-risk case where direct policy
   selection and ranking selection can be compared by known regret.
6. **Transport workload:** comparable campaign or time-window pairs only when
   available. Hillstrom-to-Criteo compares conclusion/ranking stability under a
   shared benchmark contract; it does not transfer a fitted model or feature
   meaning.

## Required metric panel

| Layer | Measures | Gate interpretation |
| --- | --- | --- |
| Health | arm/outcome counts, SRM, covariate balance, missingness, propensity histogram, overlap ESS | failure invalidates downstream interpretation |
| ATE | difference in means, covariate-adjusted/DR ATE, CI and ATE error on oracle data | broad intervention only |
| Effect accuracy | PEHE and subgroup error on known-effect workloads | unavailable on ordinary real RCTs |
| Ranking | Qini, AUUC, uplift@5/10/20/30/50%, RATE/TOC; experimental pROCini/balanced metric only after parity | report intervals and disagreement; no single universal gate |
| Calibration | binned effect calibration, calibration error, BLP/calibration test and sign-threshold reliability | required before score-level action |
| Policy | IPW, SNIPS, DR value, treat-none/all/random/equal-capacity baselines and regret | exact frozen policy and capacity only |
| Robustness | per-DGP worst group, seed/split interval, propensity clipping/trimming sensitivity, failed fits | profile routing rather than pooled winner |
| Safety | adverse outcome value/rate and conservative bound | `UNAVAILABLE`, not zero, when harm outcome is absent |
| Resources | install/start, fit and predict time, peak RSS, serialized size and failure count | named environment only |

Bootstrap or repeated-split intervals must resample at the independent unit.
Outcome adjustment is compared on development data as a variance-reduction
layer; it cannot repair a ranking/policy objective mismatch. Metric code must
pass orientation, tie, all-treated/all-control, constant-score, empty-capacity,
and known-toy fixtures.

## S0 — baseline, environment and artifact reconciliation

- **Hypothesis:** the existing SignalRoom software and Hillstrom evidence can be
  frozen as a trustworthy control before any estimator comparison.
- **Baseline:** commit `ecbf00988053de5347d2a47ac245057a64e156a2`, current
  package, tests and committed Hillstrom artifacts.
- **Candidates/data:** none; no download. Use only present repository files and
  cached/local test inputs.
- **Checks:** source/artifact hashes, constraints, Python/package versions,
  exact train/holdout row counts, split lineage, feature allowlist, current
  Qini/uplift/IPW conventions, all 15 tests, lint, JavaScript syntax and Docker
  Compose validation.
- **Known environment finding:** an uncontrolled pandas 3.0.5 run makes
  `_balance_table()` misclassify the string-like categorical
  `history_segment` and one real-benchmark test fails. Under the repository's
  frozen `pandas==2.2.3`, `numpy==2.2.4`, `scikit-learn==1.8.0` and
  `scipy==1.16.3` constraints, all 15 tests pass. This must be recorded as a
  compatibility boundary, not hidden by switching environments.
- **Budget:** 30 CPU minutes; no network or data/model download.
- **Decision:** `PASS` only if the constrained environment and artifacts
  reconcile and the uncontrolled failure is explicitly bounded. Repair the
  oracle before S1 if any value or lineage differs.

This is the exact first later controlled action. The dossier stops before it.

## S1 — benchmark-harness and metric compatibility

- **Hypothesis:** the pinned UpliftBench harness can consume a SignalRoom frame,
  isolate the outer test and reproduce shared metric fixtures without changing
  product runtime.
- **Baseline:** current T-learner result contract and SignalRoom metric toy
  fixtures.
- **Candidate:** `binshuangli/uplift-bench@604cf7c` in an isolated Python 3.12
  lock/container using its documented adapter seam.
- **Data:** a tiny generated fixture and the already-present Hillstrom schema;
  no full benchmark or new data download.
- **Checks:** one successful adapter result; malformed schema, unsupported
  outcome and estimator failure paths; fold lineage; Qini/AUUC orientation and
  ties; normalized result/provenance schema.
- **Budget:** 60 CPU minutes and 2 GB temporary artifacts.
- **Decision:** pass only if the adapter does not expose outer-test labels to
  selection, current metric differences are explained, and failure states are
  explicit. Otherwise retain the repository as protocol evidence and select a
  narrower maintained harness.

## S2 — estimator-family and workload bakeoff

- **Hypothesis:** no one estimator dominates across treatment balance,
  heterogeneity, outcome sparsity and objective; a small routed profile is more
  defensible than replacing the T-learner with the mean winner.
- **Baselines:** ATE/risk controls and current logistic T-learner.
- **Candidates:** matched-base S/T/X; R and DR with cross-fitting; EconML
  `CausalForestDML`; one CausalML uplift tree/forest; a transformed/direct
  method if the harness supplies it.
- **Data:** Hillstrom, corrected Criteo at named sample tiers, IHDP/ACIC,
  Jobs/policy-risk and frozen synthetic DGP grid.
- **Fair comparison:** identical base-learner classes and tuning budgets where
  reductions allow; native forest/direct criteria declared; five outer seeds,
  ten when rankings overlap.
- **Metrics:** full health/effect/ranking/calibration/policy/resource panel.
- **Decision:** retain a candidate only for a non-dominated regime with stable
  intervals and an explicit routing rule. Do not select from pooled mean rank.
- **Routing:** balanced transparent small-data may keep T/S; imbalance can
  admit X; robust nuisance conditions can admit R/DR; nonlinear heterogeneity
  can admit forest/direct uplift only if it earns its cost.

## S3 — nuisance, calibration and overlap stress

- **Hypothesis:** nuisance quality and overlap controls explain more policy
  instability than estimator labels in at least some regimes.
- **Candidates:** retained S2 profiles with known versus estimated propensity;
  simple versus flexible outcome/propensity models; uncalibrated versus
  cross-fitted causal isotonic calibration.
- **Data:** randomized 50/50 and 85/15 assignments, controlled weak-overlap
  bands, sparse outcomes, misspecified nuisance functions and Hillstrom/Criteo
  diagnostics.
- **Metrics:** propensity calibration and tails, overlap ESS, CATE/ranking/
  policy panel, pseudo-outcome distribution, trimming/clipping sensitivity and
  calibration error.
- **Candidate reserve:** OAR enters only if ordinary regularized/trimmed
  candidates fail a predeclared weak-overlap region.
- **Decision:** no personalized policy where support is insufficient. Route to
  broad/random action, narrower population, more experiment data or explicit
  `HOLD` rather than extrapolating.

## S4 — metric variance, objective alignment and repeated evaluation

- **Hypothesis:** candidate order changes across effect accuracy, ranking and
  deployed policy value, and outcome adjustment reduces uncertainty without
  resolving that objective mismatch.
- **Candidates:** all non-dominated S2/S3 profiles; raw and published
  outcome-adjusted metric variants.
- **Metrics:** Qini/AUUC/uplift@k, RATE/TOC, PEHE/ATE error where oracle truth
  exists, calibration and policy value/regret. pROCini and balanced ranking
  enter only after official/reproducible code passes fixtures.
- **Repetition:** nested outer repetitions with paired intervals and rank
  stability; retain every seed and undefined metric.
- **Decision:** select for the deployment rule, not for a universal metric. A
  candidate with high Qini but worse calibrated threshold policy cannot drive
  that policy.

## S5 — cost, value, capacity and policy evaluation

- **Hypothesis:** capacity and economic assumptions reverse at least some
  estimator/policy rankings, so a single 20% IPW value is insufficient.
- **Baselines:** treat-none, treat-all when feasible, random and fixed
  non-model allocation at equal capacity, current thresholded value policy.
- **Candidates:** frozen score threshold, top-capacity, calibrated sign/value
  threshold and shallow DR policy tree only after simple policies pass.
- **Grid:** capacities 5/10/20/30/50%; fixed and variable action costs; customer
  value scales; pessimistic/base/optimistic cost assumptions.
- **Evaluation:** outer-held-out IPW, SNIPS and DR value with intervals; policy
  regret on oracle data; selection/evaluation split; exact utility recorded.
- **Decision:** retain the simplest non-dominated policy. A learned policy must
  beat the feasible equal-capacity baseline with a positive paired lower bound
  in its claimed region.

## S6 — campaign/population shift

- **Hypothesis:** estimator and policy conclusions do not automatically
  transport between campaigns, populations or outcome horizons.
- **Data:** Hillstrom and corrected Criteo under a shared abstract result
  contract; later comparable client campaigns or time windows with named
  covariate/outcome changes.
- **Checks:** feature/assignment/outcome shift, overlap in target population,
  calibration and policy-value degradation, candidate rank stability, and
  worst campaign/time group.
- **Decision:** use public cross-dataset evidence only to test conclusion
  stability. Never transfer Hillstrom's fitted model, anonymized Criteo feature
  interpretation, or claimed effect to a client population.

## S7 — no-harm/safe policy, conditional only

- **Entry gate:** a separately measured adverse outcome such as unsubscribe,
  complaint, harmful engagement, or defensible long-run detriment; a frozen
  harm cost/bound; and sufficient arm support.
- **Hypothesis:** utility-maximizing and no-harm policies choose different
  actions for some units/groups.
- **Evaluation:** benefit, adverse outcome, conservative harm bound, review/
  abstention, group/worst-case results and policy value under the constraint.
- **Decision:** no harm claim is possible without the entry data. For
  Hillstrom, record `UNAVAILABLE`; do not infer safety from a positive visit
  effect or absence of a recorded complaint column.

## Exact next controlled action

The first later action is **S0 only**. Freeze and reconcile the current
SignalRoom repository, environment, artifacts, split, metrics and 15 tests at
`ecbf009`. No estimator, data or model is downloaded and no benchmark is run.
S1 is blocked until S0 is `PASS` and a later execution checkpoint explicitly
authorizes the isolated Python 3.12 harness work.

## Current baseline verification only

The following checks were run for this dossier; they are not an experiment:

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
node --check app.js
docker compose config -q
```

Observed on 2026-08-05 under the frozen numerical constraints: Ruff passed, 15
tests passed in 2.83 seconds, JavaScript syntax passed, and Compose config
validated. An uncontrolled global pandas 3.0.5 run produced the compatibility
failure described in S0; the repository constrains pandas below 3.
