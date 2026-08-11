# Expertise notes

## When real randomized data supports an intervention but not necessarily targeting

### Client trigger

- Job wording or deliverable that makes this relevant: churn prevention,
  campaign targeting, uplift modeling, treatment/control evaluation, or a
  capacity-constrained intervention queue.
- How often it appeared in the measured corpus or proposal log: predictive ML
  represented 127 of 4,908 measured requirement tags (2.6%); this is a bounded
  credibility gap rather than a general portfolio expansion.
- Existing project/component that can be reused: SignalRoom's T-learner and
  capacity policy; the real-data evaluation components selected in
  `docs/REAL_DATA_ADMISSION.md`.

### Failure symptom or unanswered choice

Synthetic data can prove that the software runs, but it cannot establish that
customer features contain enough real treatment-effect signal to justify an
individual targeting policy.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Broad treatment | The randomized experiment may show a positive average email effect | Ignores a real capacity constraint and may contact low/negative-effect customers |
| Random 20% policy | Honest capacity-matched baseline that needs no model | Leaves any learnable heterogeneity unused |
| T-learner top 20% | Uses treated/control outcome models to rank incremental response | Can overfit weak heterogeneity and look useful without beating the capacity-matched baseline |

### Controlled comparison

- Representative cases or fixtures: pinned 64,000-row Hillstrom GitHub mirror;
  42,613-row Mens-email versus no-email randomized contrast.
- Frozen development/held-out split, when relevant: deterministic joint
  treatment/outcome 80/20 split, seed 42.
- Metrics and decision thresholds chosen before the run: ATE with 95%
  bootstrap interval; normalized Qini with lower bound greater than zero;
  top-20% uplift above ATE; 20%-capacity IPW value gain over random with lower
  bound greater than zero.
- Runtime, hardware, model/provider version, cost assumptions, and date:
  local Windows CPU; Python/sklearn versions captured in the output; no model
  provider or token cost; run date captured by the command.
- What is deliberately outside the comparison: SaaS churn, temporal drift,
  conversion/spend optimization, long-run harms, UI/API changes, and model
  shopping.

### Result

The checksum-pinned run used 42,613 customers, with 34,090 training rows and
8,523 held-out rows. Randomization health passed: the binary-arm SRM check was
`p=0.9961`, and maximum absolute covariate SMD was `0.0164` against the `0.10`
limit.

- Average two-week visit effect: `+0.0767`, bootstrap 95% interval
  `[0.0634, 0.0920]`.
- Top-20% realized uplift: `0.1167`, interval `[0.0733, 0.1512]`.
- Normalized Qini: `0.0144`, interval `[-0.0166, 0.0457]`.
- Learned 20%-capacity policy value: `0.1274`; random equal-capacity policy:
  `0.1214`.
- IPW policy-value gain: `+0.0060`, interval `[-0.0019, 0.0128]`.

The average intervention effect passed. Individual targeting failed two of
three pre-registered gates because both Qini and policy-gain intervals crossed
zero. No model, feature, arm, split, or threshold was changed after the run.

The local Qini (`0.0144495`) and uplift-at-20% (`0.1167296`) were independently
cross-checked against `scikit-uplift==0.5.1` (`0.0144346` and `0.1165697`). The
minor differences are consistent with implementation-specific curve/tie
conventions and do not change either decision gate.

### Decision rule

Promote learned targeting only when it beats a random policy at the same
capacity with a positive bootstrap lower bound and passes the two ranking
gates. This run therefore retains the experiment-level email effect and
rejects individualized targeting for the available features. At a fixed 20%
capacity, use an explicit non-model allocation rule and keep a randomized
control until richer pre-treatment features can be tested under the same gate.

### Delivery control

Require an explicit randomized control arm, pre-treatment feature allowlist,
checksum-pinned input, held-out policy evaluation, and a capacity-matched
baseline before a learned intervention queue is described as beneficial.

### Reuse boundary

- Reusable without client data: loader contract, leakage checks, joint split,
  Qini/uplift-at-k, IPW capacity evaluation, bootstrap report, and promotion
  rule.
- Requires client data, credentials, environment, or acceptance criteria:
  treatment definition, action cost/capacity, outcome horizon, harm
  guardrails, and a representative randomized experiment.
- Unsupported claim that must not appear in a proposal: that SignalRoom's
  synthetic SaaS lift or this retail email benchmark proves production churn
  reduction or client revenue.

### Proposal-safe insight

I built a checksum-pinned evaluation path around a real randomized email
experiment and separated average intervention lift from targeting value. The
experiment showed a clear average visit increase, but the model's equal-budget
advantage crossed zero, so the deployment gate correctly rejected a stronger
personalized-targeting claim.

### Central index disposition

- **Map to existing card:** `Require targeting to beat an equal-capacity
  baseline, not merely show average lift`.
- Reason: this note is the empirical SignalRoom evidence behind that exact
  buyer-facing delivery control; creating another card would duplicate the
  retrieval trigger.

### Evidence

- Code: `signalroom/real_data.py`, `signalroom/real_metrics.py`, and
  `signalroom/real_benchmark.py`.
- Tests: real-data, metric, promotion, report, existing API, and policy suites;
  15 passing with 91% aggregate coverage in the local verification run.
- Raw comparison artifacts: `artifacts/real_data/benchmark.json` and
  `artifacts/real_data/benchmark.md`.
- Human review, if used: none.
- Reproduction commands: `pip install -c requirements-benchmark.txt -e
  ".[dev]"`, then `python -m signalroom.real_benchmark --bootstrap 500`.

### Interview follow-up

- Likely technical question: Why is ordinary response prediction not enough?
- Short answer: it ranks likely visitors, including people who would visit
  without email; uplift ranking estimates the difference between treated and
  untreated potential outcomes and must be evaluated against randomized
  treatment assignments.
- Deeper evidence to open if challenged: the pinned contract, held-out Qini,
  top-capacity uplift, and IPW policy-value comparison.

## Match uplift evaluation to the deployed decision rule

### Client trigger

- Job wording or deliverable that makes this relevant: uplift modelling,
  campaign targeting, next-best action, retention offers, Qini/AUUC
  optimization, treatment-effect ranking, or policy-value evaluation.
- How often it appeared in the measured corpus or proposal log: it refines the
  predictive-ML opportunity cluster already measured for SignalRoom; no new
  frequency claim is made from the dossier.
- Existing project/component that can be reused: SignalRoom's held-out Qini,
  uplift-at-capacity, IPW policy-value, capacity policy and promotion gate.

### Failure symptom or unanswered choice

A model can rank customers well by one uplift curve while placing the
zero-benefit threshold incorrectly or losing value under the actual capacity
and cost rule. Selecting it on Qini alone answers a different question from
the client's decision.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Select by Qini/AUUC | Common and easy to compare across uplift scores | High variance, tie/convention sensitivity, and no calibrated threshold guarantee |
| Select by effect error | Directly assesses CATE accuracy when truth is known | PEHE is unavailable on ordinary real randomized data |
| Select by held-out policy value/regret | Matches the frozen action rule, budget and utility | Needs outer isolation, assignment probabilities, nuisance controls and uncertainty |
| Use a panel and route by objective | Makes disagreements visible and avoids a universal winner | More reporting and a predeclared decision hierarchy |

### Controlled comparison

- Representative cases or fixtures: current Hillstrom result; corrected Criteo
  later; Jobs/policy-risk and known-effect synthetic/semi-synthetic cases.
- Frozen development/held-out split, when relevant: nested development folds
  inside a never-touched outer test; calibration and policy selection remain
  inside development.
- Metrics and decision thresholds chosen before the run: ATE, PEHE where
  observable, Qini/AUUC/uplift@k, RATE/TOC, effect calibration, IPW/SNIPS/DR
  value, regret and equal-capacity baselines with intervals.
- Runtime, hardware, model/provider version, cost assumptions, and date: must
  be frozen in the S2/S4/S5 manifest; no comparison run occurred in this
  dossier.
- What is deliberately outside the comparison: a universal leaderboard,
  test-set tuning, fitted-model transfer between unrelated public datasets,
  and a no-harm claim without an adverse outcome.

### Result

The research comparison found established evidence that ranking, calibrated
effect and policy value are distinct objectives. Recent UpliftBench evidence
is especially direct but remains provisional because it was submitted on
2026-08-02 and is under review. Published metric work also disagrees about the
best correction to conventional Qini-style evaluation. Therefore no new
metric was promoted and no candidate result was inferred.

### Decision rule

Name the deployment rule first. Use ranking metrics for prioritization,
calibration for score-level thresholds, and outer-held-out policy value/regret
for the exact cost/capacity policy. When metrics disagree, select for the named
decision and report the disagreement; do not average it away.

### Delivery control

Require a frozen estimand, metric implementations/tie conventions, outer-test
isolation, equal-capacity baselines, utility/capacity assumptions, paired
uncertainty and raw per-seed results before calling a targeting policy better.

### Reuse boundary

- Reusable without client data: benchmark manifest, metric/policy result
  schema, outer-split controls, toy metric fixtures and decision hierarchy.
- Requires client data, credentials, environment, or acceptance criteria:
  outcome horizon, treatment probabilities, action cost, customer value,
  capacity and acceptable uncertainty.
- Unsupported claim that must not appear in a proposal: that a high public
  Qini score establishes client ROI or a reliable benefit threshold.

### Proposal-safe insight

I separate uplift ranking from the decision it is meant to support: ranking
curves show prioritization, calibration supports score thresholds, and the
frozen policy must still beat an equal-capacity baseline on held-out value.

### Central index disposition

- **Add new card:** `Match uplift evaluation to the deployed decision rule`.
- Reason: Qini/AUUC and policy-evaluation wording are direct buyer retrieval
  triggers not covered by the existing equal-capacity card alone.

### Evidence

- Code: existing `signalroom/real_metrics.py`, `signalroom/real_benchmark.py`
  and `signalroom/policy.py`; no dossier source change.
- Tests: existing metric/policy/benchmark tests; constrained baseline is 15
  passing.
- Raw comparison artifacts: `TECHNIQUE_TAXONOMY.md`,
  `EVIDENCE_MATRIX.csv`, `BENCHMARK_DESIGN.md` and `RESEARCH_DECISION.md`.
- Human review, if used: none.
- Reproduction commands: no new experiment; later S0 is the exact next
  controlled action.

### Interview follow-up

- Likely technical question: Why not just optimize Qini?
- Short answer: Qini evaluates an ordering, while a real policy acts at a
  threshold under capacity and costs; the ordering can look good while its
  score level or held-out value is wrong.
- Deeper evidence to open if challenged: the metric-contestation rows and the
  S4/S5 outer-held-out protocol.

## Inspect overlap before trusting personalized effects

### Client trigger

- Job wording or deliverable that makes this relevant: observational uplift,
  propensity scores, causal ML, heterogeneous treatment effects, treatment
  imbalance, biased targeting logs, or personalized policy.
- How often it appeared in the measured corpus or proposal log: it supports the
  same bounded causal/predictive portfolio gap; no independent count is claimed.
- Existing project/component that can be reused: SignalRoom's randomized-arm
  health checks and proposed S3 propensity/overlap stress protocol.

### Failure symptom or unanswered choice

The model assigns large positive or negative effects in covariate regions where
one treatment arm has little or no support. Flexible learners can turn
extrapolation or unstable inverse weights into confident-looking targeting.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Trust randomized assignment globally | Hillstrom assignment is randomized and balanced | Marginal balance can hide subgroup scarcity; future logs may be observational |
| Clip or trim propensities | Stabilizes extreme weights and DR pseudo-outcomes | Changes the target population and introduces a tuning choice |
| Use orthogonal/DR learners | Reduces nuisance sensitivity under assumptions | Does not solve absent overlap or both nuisance models being wrong |
| Restrict/hold unsupported cases | Preserves defensible action in supported regions | Reduces coverage and requires a fallback policy |

### Controlled comparison

- Representative cases or fixtures: Hillstrom/Criteo propensity diagnostics and
  synthetic 50/50, 85/15 and weak-overlap regimes with known effects.
- Frozen development/held-out split, when relevant: propensity models,
  clipping/trimming and candidate selection use development folds only.
- Metrics and decision thresholds chosen before the run: propensity tails and
  calibration, overlap effective sample size, pseudo-outcome distribution,
  PEHE/regret where known, ranking/policy value and coverage of supported cases.
- Runtime, hardware, model/provider version, cost assumptions, and date: later
  S3 manifest; no overlap experiment ran in this dossier.
- What is deliberately outside the comparison: claiming unconfoundedness from
  a good propensity model or using a sensitivity tool as proof of identification.

### Result

The external evidence establishes overlap as an identification and variance
boundary. GRF, EconML, DoubleML and OAR supply diagnostics or candidate logic;
none makes unsupported covariate regions trustworthy. Hillstrom has healthy
randomized marginal assignment, but this does not close subgroup or future
observational support.

### Decision rule

Inspect treatment support before estimating personalized effects. Where
support is inadequate, narrow the population, collect randomized data, choose
a broad/random fallback, or hold the action. Trimming/clipping is reported as a
target-population change, not a silent numerical fix.

### Delivery control

Require treatment-propensity distributions, effective sample sizes, fold-safe
nuisance fitting, clipping/trimming sensitivity, supported-population coverage
and an explicit unsupported-case route.

### Reuse boundary

- Reusable without client data: diagnostic schema, stress DGPs, propensity and
  overlap fixture contracts, failure routing.
- Requires client data, credentials, environment, or acceptance criteria:
  actual assignment mechanism, causal feature set, target population and
  acceptable coverage.
- Unsupported claim that must not appear in a proposal: that doubly robust
  estimation removes the need for overlap or measured-confounding assumptions.

### Proposal-safe insight

I treat overlap as a deployment boundary: orthogonal or doubly robust learners
can reduce nuisance-model sensitivity, but they do not justify personalized
actions in treatment regions the data barely observed.

### Central index disposition

- **Add new card:** `Check treatment overlap before personalizing an
  intervention`.
- Reason: propensity/observational-causal job wording creates a distinct buyer
  retrieval trigger and delivery control.

### Evidence

- Code: current experiment-health checks plus the frozen S3 design; no new
  estimator implementation.
- Tests: current constrained baseline 15 passing.
- Raw comparison artifacts: taxonomy overlap section, matrix rows SR011,
  SR012, SR016, SR017, SR020, SR037 and SR038, and S3 benchmark design.
- Human review, if used: none.
- Reproduction commands: none for the research decision; S0 must pass before
  later S3 admission.

### Interview follow-up

- Likely technical question: Isn't randomization enough for overlap?
- Short answer: it gives known assignment and strong marginal support in this
  trial, but fine subgroups can still be sparse and observational deployment
  logs can be very different; I inspect both support and policy coverage.
- Deeper evidence to open if challenged: the S3 known-propensity versus
  estimated-propensity stress grid.

## Calibrate treatment-effect scores before thresholding action

### Client trigger

- Job wording or deliverable that makes this relevant: persuadable/sleeping-dog
  segmentation, positive-uplift threshold, next-best action, expected value, or
  per-customer treatment-effect score.
- How often it appeared in the measured corpus or proposal log: technical
  refinement of the same SignalRoom opportunity; it is not assigned a separate
  frequency.
- Existing project/component that can be reused: SignalRoom's score-to-value
  policy and proposed cross-fitted calibration layer.

### Failure symptom or unanswered choice

The score orders customers reasonably but its zero point and magnitudes are
wrong, so `uplift > 0` or expected-value thresholds select the wrong coverage
even when a ranking curve appears acceptable.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Use raw CATE score | Simple and preserves estimator output | Score level may be biased or compressed |
| Use rank-only top-k | Avoids trusting magnitude | Cannot express benefit sign or value/cost break-even |
| Calibrate out of fold | Aligns score bins/levels with observed treatment-effect structure | Consumes calibration data and can overfit without isolation |
| Use conservative/held action | Avoids acting near uncertain zero | Lower automatic coverage |

### Controlled comparison

- Representative cases or fixtures: synthetic known CATE, Hillstrom and
  corrected Criteo under S3/S4.
- Frozen development/held-out split, when relevant: cross-fitted calibration
  is learned on development predictions only; test remains untouched.
- Metrics and decision thresholds chosen before the run: calibration curves,
  calibration error/BLP, sign error on oracle data, policy value/regret at
  frozen thresholds and coverage.
- Runtime, hardware, model/provider version, cost assumptions, and date: later
  manifest; no calibration run occurred.
- What is deliberately outside the comparison: per-person counterfactual
  certainty and post-hoc test calibration.

### Result

Published and implemented causal calibration work establishes a reusable
cross-fitted route. It does not establish that calibration will improve
SignalRoom; that remains an S3/S4 question. The dossier therefore admits the
layer but makes no performance claim.

### Decision rule

Use raw scores for ranking only when ranking is the deployment rule. Before a
sign or economic threshold, measure cross-fitted effect calibration and compare
the exact held-out policy. If calibration is unstable, use rank/capacity or
hold the uncertain region instead of presenting the score as causal magnitude.

### Delivery control

Require fold lineage, calibration plots/tests, predeclared bins/smoother,
uncalibrated comparison, outer-held-out policy value and explicit uncertainty
near the action boundary.

### Reuse boundary

- Reusable without client data: calibration adapter contract and toy fixtures.
- Requires client data, credentials, environment, or acceptance criteria:
  representative randomized/logged outcomes, decision threshold and utility.
- Unsupported claim that must not appear in a proposal: that a model's raw
  CATE value is an individually observed or automatically calibrated effect.

### Proposal-safe insight

I do not turn an uplift ranking score directly into “treat if positive.” I
measure treatment-effect calibration out of fold and then verify the exact
threshold policy on an untouched holdout.

### Central index disposition

- **Do not add a separate card.** Map as technical support for `Match uplift
  evaluation to the deployed decision rule`.
- Reason: calibration is a critical control but not a distinct buyer retrieval
  trigger from threshold/policy-alignment work.

### Evidence

- Code: proposed adapter to
  `Larsvanderlaan/causalCalibration@fdaad7b823ce0acb8040d11f1c342510e2e4b627`;
  no code copied or run.
- Tests: later parity fixtures required; current baseline remains 15 passing.
- Raw comparison artifacts: matrix row SR030 and S3/S4 benchmark design.
- Human review, if used: none.
- Reproduction commands: none yet; blocked behind S0 and S1.

### Interview follow-up

- Likely technical question: Can a model have good Qini and bad calibration?
- Short answer: yes; ranking depends on order, while calibration depends on
  score level, so the zero or value threshold can be wrong despite a useful
  ordering.
- Deeper evidence to open if challenged: causal-isotonic reference and the
  frozen calibration-versus-policy protocol.

## Treat harm as a separate policy constraint

### Client trigger

- Job wording or deliverable that makes this relevant: sleeping dogs,
  unsubscribe/complaint prevention, responsible targeting, adverse outcomes,
  safe policy, customer fatigue, or no-harm personalization.
- How often it appeared in the measured corpus or proposal log: no defensible
  measured frequency is assigned; this is a credibility boundary for any
  intervention proposal.
- Existing project/component that can be reused: SignalRoom's positive-uplift/
  positive-value filtering and explicit policy hold/rejection logic.

### Failure symptom or unanswered choice

A campaign improves visits or value on average while increasing a separate
adverse outcome for some customers or groups. Treating negative predicted
benefit as the only form of harm hides that tradeoff.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Optimize average utility only | Direct business objective | Can hide adverse outcomes or vulnerable subgroups |
| Treat negative CATE as harm | Simple one-score rule | Confuses lack of benefit with a distinct adverse event |
| Add a measured harm constraint | Matches the safety question | Needs separate outcome, assumptions and enough support |
| Abstain where harm is unidentified | Preserves a conservative boundary | Reduces coverage and may require more experiment data |

### Controlled comparison

- Representative cases or fixtures: only a future experiment with separately
  recorded unsubscribe, complaint, fatigue or defensible long-run harm.
- Frozen development/held-out split, when relevant: benefit/harm models,
  thresholds and constraints selected before the outer test.
- Metrics and decision thresholds chosen before the run: benefit policy value,
  harm rate/value, conservative bound, group worst case, coverage and regret.
- Runtime, hardware, model/provider version, cost assumptions, and date: not
  applicable until the S7 entry gate passes.
- What is deliberately outside the comparison: inferring no harm from a
  positive average visit effect or from an absent harm column.

### Result

No SignalRoom harm comparison is possible. Hillstrom has no unsubscribe,
complaint or long-run adverse outcome. The literature establishes that harm is
distinct from average utility and that conservative policies require explicit
outcomes/identification bounds. The correct current result is `UNAVAILABLE`.

### Decision rule

Never claim no harm without a separately defined and observed adverse outcome
or a defensible bound. If the entry data are absent, disclose the gap and keep
the safe-policy profile closed.

### Delivery control

Require a harm definition/horizon, collection mechanism, missingness audit,
minimum support, conservative acceptance bound, group/worst-case report and an
abstain/fallback action.

### Reuse boundary

- Reusable without client data: harm-aware result schema, entry gate and
  abstention routing.
- Requires client data, credentials, environment, or acceptance criteria:
  adverse outcome, causal assumptions, harm cost/bound and risk tolerance.
- Unsupported claim that must not appear in a proposal: that Hillstrom or
  SignalRoom proves outreach does not annoy or harm customers.

### Proposal-safe insight

I treat harm as a separate measured outcome, not as the negative side of an
uplift score. When unsubscribe or complaint data are absent, I report that the
safety question is unavailable rather than implying a no-harm result.

### Central index disposition

- **Add new card:** `Treat intervention harm as a separate measured outcome`.
- Reason: safety, unsubscribe and customer-fatigue wording create a distinct
  buyer concern and a strong credibility control.

### Evidence

- Code: current policy filtering only; no no-harm estimator exists or is
  claimed.
- Tests: current baseline 15 passing; no harm test can be valid without data.
- Raw comparison artifacts: matrix rows SR035/SR036 and conditional S7 design.
- Human review, if used: none.
- Reproduction commands: none; S7 is blocked by missing harm data.

### Interview follow-up

- Likely technical question: Aren't “sleeping dogs” already the harm group?
- Short answer: negative benefit on the selected business outcome is not the
  same as an adverse outcome such as unsubscribe; identifying individual
  principal strata also needs assumptions the observed RCT does not close.
- Deeper evidence to open if challenged: the no-harm and partial-identification
  source rows plus S7 entry gate.

## Validate targeting conclusions under campaign and population shift

### Client trigger

- Job wording or deliverable that makes this relevant: campaign transfer,
  model monitoring, temporal validation, multi-market rollout, domain shift,
  client-specific uplift, or retraining policy.
- How often it appeared in the measured corpus or proposal log: no separate
  frequency is claimed; this is a deployment boundary for every public-data
  portfolio result.
- Existing project/component that can be reused: SignalRoom's artifact
  provenance, drift concepts, frozen public benchmark and proposed S6 contract.

### Failure symptom or unanswered choice

A targeting conclusion derived from one randomized campaign is reused for a
new channel, population, time window or outcome even though assignment,
covariates, response and costs changed.

### Competing options

| Option | Why it is plausible | Main cost or failure risk |
| --- | --- | --- |
| Transfer the fitted model | Fastest deployment | Feature meaning and response surfaces may not match |
| Refit but reuse the old winner | Preserves familiar stack | Estimator/objective ranking may change by regime |
| Revalidate conclusion and policy | Tests support, calibration and value on target data | Requires target experiment/holdout and delays promotion |
| Use broad/random fallback | Safe when personalized value is unsupported | Gives up potential heterogeneity |

### Controlled comparison

- Representative cases or fixtures: Hillstrom versus corrected Criteo for
  conclusion stability only; comparable client campaigns/time windows for
  actual transport evidence.
- Frozen development/held-out split, when relevant: target-period/campaign
  holdout remains untouched; any adaptation uses earlier data.
- Metrics and decision thresholds chosen before the run: feature/assignment/
  outcome shift, overlap, calibration, metric/rank stability, held-out policy
  value and worst campaign/time group.
- Runtime, hardware, model/provider version, cost assumptions, and date: later
  S6 manifest; no shift experiment ran.
- What is deliberately outside the comparison: treating anonymized Criteo
  features as Hillstrom/customer features or calling cross-dataset rank
  agreement causal transport.

### Result

Transportability literature and cross-campaign marketing evidence establish
that internal validity does not imply target-population validity. SignalRoom's
public data have no valid time split, so the client transfer question remains
unknown and must be tested on target data.

### Decision rule

Reuse the workflow and acceptance gate, not the fitted public model or its
effect claim. Recheck support, calibration and policy value in every target
campaign/population; fall back to broad/random action until personalized value
passes.

### Delivery control

Require target-population definition, comparable outcome horizon, data and
model provenance, assignment/overlap audit, temporal or campaign holdout,
worst-group report and an explicit retraining/fallback rule.

### Reuse boundary

- Reusable without client data: manifests, adapters, validation metrics and
  promotion/fallback logic.
- Requires client data, credentials, environment, or acceptance criteria:
  target experiment, feature semantics, action economics and deployment horizon.
- Unsupported claim that must not appear in a proposal: that Hillstrom email
  lift or public Criteo results prove client churn or campaign value.

### Proposal-safe insight

I reuse the evaluation workflow across campaigns, not the public benchmark's
fitted model or effect claim. Personalized targeting is re-promoted only after
support, calibration and equal-budget value hold on the target campaign.

### Central index disposition

- **Add new card:** `Revalidate targeting under campaign and population
  shift`.
- Reason: transfer, monitoring and multi-market job language is a distinct
  retrieval trigger with a defensible delivery boundary.

### Evidence

- Code: current provenance/drift surfaces and proposed S6 design; no transfer
  implementation.
- Tests: current constrained baseline 15 passing.
- Raw comparison artifacts: matrix rows SR021, SR022, SR039 and SR040 and S6.
- Human review, if used: none.
- Reproduction commands: none; target data and later checkpoint required.

### Interview follow-up

- Likely technical question: Why compare Hillstrom and Criteo if models cannot
  transfer?
- Short answer: they can test whether conclusions and estimator/objective
  rankings are regime-sensitive under a shared harness; actual policy transfer
  still needs comparable target data and validation.
- Deeper evidence to open if challenged: the corrected-Criteo boundary and S6
  transport protocol.
